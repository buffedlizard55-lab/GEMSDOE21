"""Strict GeoTIFF validation and atomic writing. Invalid predictions FAIL, never silently clip."""

from __future__ import annotations

from pathlib import Path
import tempfile
import zipfile

import numpy as np
import rasterio

from .io import sha256


def template_footprint(template):
    """Reject malformed references; equality to a broken template is not compliance.

    Shape/origin come from the supplied template. Universal published constraints
    (single float32 band, EPSG:32611, north-up 100m grid, nonempty footprint) also apply.
    A validated grid is not authenticated organizer provenance.
    """
    checks = {
        "template_single_float32_band": template.count == 1 and template.dtypes == ("float32",),
        "template_epsg32611": template.crs is not None and template.crs.to_epsg() == 32611,
        "template_north_up_100m": bool(
            np.isfinite(list(template.transform)).all()
            and template.transform.a == 100
            and template.transform.e == -100
            and template.transform.b == 0
            and template.transform.d == 0
        ),
    }
    if template.count < 1 or template.dtypes[0] not in ("float32", "float64"):
        raise ValueError("Template must contain a real floating-point footprint band")
    footprint = np.isfinite(template.read(1)) & (template.read_masks(1) > 0)
    checks["template_nonempty_footprint"] = bool(footprint.any())
    if not all(checks.values()):
        raise ValueError(f"Invalid submission template: {checks}")
    return footprint, checks


def validate(path: Path, template_path: Path, expected_sha: str | None = None) -> dict:
    path, template_path = Path(path), Path(template_path)
    with rasterio.open(template_path) as t, rasterio.open(path) as s:
        footprint, template_checks = template_footprint(t)
        checks = {
            **template_checks,
            "single_band": s.count == 1,
            "float32": s.dtypes == ("float32",),
            "crs_exact": s.crs == t.crs,
            "shape_exact": s.shape == t.shape,
            "geotransform_exact": s.transform == t.transform,
        }
        if not checks["shape_exact"] or not checks["single_band"] or not checks["float32"]:
            return {"passed": False, "checks": checks, "sha256": sha256(path)}
        a = s.read(1)
        vals = a[footprint]
        mask = s.read_masks(1) > 0
        checks["no_masked_footprint_pixels"] = bool(mask[footprint].all())
        checks["footprint_finite"] = bool(np.isfinite(vals).all())
        checks["footprint_range_0_1"] = bool(
            np.isfinite(vals).all() and (vals >= 0).all() and (vals <= 1).all()
        )
        checks["outside_null_or_nan"] = bool((~mask[~footprint] | np.isnan(a[~footprint])).all())
        finite = a[np.isfinite(a)]
        checks["all_finite_values_in_range"] = bool(((finite >= 0) & (finite <= 1)).all())
        checks["no_infinity_anywhere"] = not bool(np.isinf(a).any())
        h = sha256(path)
        if expected_sha:
            checks["expected_sha256"] = h == expected_sha
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "sha256": h,
            "bytes": path.stat().st_size,
            "shape": list(s.shape),
            "crs": str(s.crs),
            "transform": list(s.transform)[:6],
            "footprint_pixels": int(footprint.sum()),
            "outside_pixels": int((~footprint).sum()),
            "footprint_nan_inf": int((~np.isfinite(vals)).sum()),
            "footprint_out_of_range": int(((vals < 0) | (vals > 1)).sum()),
            "footprint_min": float(np.min(vals)) if np.isfinite(vals).all() else None,
            "footprint_max": float(np.max(vals)) if np.isfinite(vals).all() else None,
            "raw_all_pixels_finite": bool(np.isfinite(a).all()),
            "positive_footprint_pixels": int((vals > 0).sum()),
            "validator_scope": "local official-format checks; not platform acceptance or score verification",
        }


def validate_bundle(path: Path, template_path: Path, expected_sha: str | None = None) -> dict:
    """Validate a TIFF or a safe ZIP with exactly one TIFF; SHA refers to contained TIFF."""
    path = Path(path)
    if path.suffix.lower() != ".zip":
        return validate(path, template_path, expected_sha)
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) != 1:
            raise ValueError("Submission ZIP must contain exactly one GeoTIFF and nothing else")
        entry = entries[0]
        if (
            entry.is_dir()
            or Path(entry.filename).name != entry.filename
            or any(character in entry.filename for character in ("\\", ":", "\x00", "\r", "\n"))
            or Path(entry.filename).suffix.lower() not in (".tif", ".tiff")
            or entry.flag_bits & 1
            or entry.file_size > 300_000_000
            or (entry.external_attr >> 16) & 0o170000 not in (0, 0o100000)
        ):
            raise ValueError("Unsafe or oversized submission ZIP entry")
        if archive.testzip() is not None:
            raise ValueError("Submission ZIP CRC failed")
        with tempfile.TemporaryDirectory(prefix="gems-validate-zip-") as temp:
            tif = Path(temp) / "submission.tif"
            tif.write_bytes(archive.read(entry.filename))
            report = validate(tif, template_path, expected_sha)
            return {
                **report,
                "container_sha256": sha256(path),
                "container_bytes": path.stat().st_size,
                "zip_member": entry.filename,
                "zip_exactly_one_tiff_crc_verified": True,
            }


def write(pred: np.ndarray, template_path: Path, dest: Path, outside="nan") -> Path:
    if outside not in ("nan", "masked-zero"):
        raise ValueError("Outside must be nan or masked-zero")
    dest, template_path = Path(dest), Path(template_path)
    if dest.resolve() == template_path.resolve():
        raise ValueError("Refuse to overwrite the reference template")
    raw = np.asarray(pred)
    if raw.dtype.kind not in "fiub":
        raise ValueError("Predictions must be real numeric confidence values, not complex or encoded text")
    with rasterio.open(template_path) as t:
        footprint, _ = template_footprint(t)
        if raw.shape != t.shape:
            raise ValueError("Prediction shape differs from template")
        vals = raw[footprint]
        if not np.isfinite(vals).all() or (vals < 0).any() or (vals > 1).any():
            raise ValueError("Predicted values must be finite and in range [0, 1]")
        p = np.where(footprint, raw, np.nan if outside == "nan" else 0).astype(np.float32)
        profile = t.profile.copy()
        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            compress="deflate",
            predictor=3,
            nodata=np.nan if outside == "nan" else None,
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Unique same-directory staging avoids concurrent writers sharing a .partial path.
    with tempfile.NamedTemporaryFile(dir=dest.parent, prefix=".gems-tiff-", suffix=".tif", delete=False) as f:
        tmp = Path(f.name)
    try:
        with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
            with rasterio.open(tmp, "w", **profile) as s:
                s.write(p, 1)
                if outside == "masked-zero":
                    s.write_mask(footprint.astype(np.uint8) * 255)
        result = validate(tmp, template_path)
        if not result["passed"]:
            raise ValueError(f"Emitted file failed checks: {result['checks']}")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest


def zip_single(path: Path, dest: Path | None = None) -> Path:
    path = Path(path)
    dest = Path(dest) if dest else path.with_suffix(".zip")
    if path.suffix.lower() != ".tif" or dest.suffix.lower() != ".zip" or path.resolve() == dest.resolve():
        raise ValueError("Need distinct .tif input and .zip output paths")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, prefix=".gems-zip-", suffix=".zip", delete=False) as f:
        tmp = Path(f.name)
    try:
        info = zipfile.ZipInfo(path.name, date_time=(2026, 9, 30, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        with zipfile.ZipFile(tmp, "w") as z:
            z.writestr(info, path.read_bytes())
        with zipfile.ZipFile(tmp) as z:
            if (
                z.namelist() != [path.name]
                or z.testzip() is not None
                or z.read(path.name) != path.read_bytes()
            ):
                raise ValueError("ZIP does not contain exactly the validated GeoTIFF")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest

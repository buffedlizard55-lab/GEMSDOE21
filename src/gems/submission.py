"""Strict GeoTIFF validation and atomic writing. Invalid predictions FAIL, never silently clip."""

from __future__ import annotations

from pathlib import Path
import zipfile

import numpy as np
import rasterio

from .io import sha256


def validate(path: Path, template_path: Path, expected_sha: str | None = None) -> dict:
    path, template_path = Path(path), Path(template_path)
    with rasterio.open(template_path) as t, rasterio.open(path) as s:
        ta = t.read(1)
        footprint = np.isfinite(ta) & (t.read_masks(1) > 0)
        checks = {
            "single_band": s.count == 1,
            "float32": s.dtypes == ("float32",),
            "crs_exact": s.crs == t.crs,
            "shape_exact": s.shape == t.shape,
            "geotransform_exact": s.transform == t.transform,
        }
        if not checks["shape_exact"] or s.count < 1:
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


def write(pred: np.ndarray, template_path: Path, dest: Path, outside="nan") -> Path:
    if outside not in ("nan", "masked-zero"):
        raise ValueError("Outside must be nan or masked-zero")
    dest = Path(dest)
    with rasterio.open(template_path) as t:
        footprint = np.isfinite(t.read(1)) & (t.read_masks(1) > 0)
        if np.shape(pred) != t.shape:
            raise ValueError("Prediction shape differs from template")
        vals = np.asarray(pred)[footprint]
        if not np.isfinite(vals).all() or (vals < 0).any() or (vals > 1).any():
            raise ValueError("Predicted values must be finite and in range [0, 1]")
        p = np.where(footprint, pred, np.nan if outside == "nan" else 0).astype(np.float32)
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
    tmp = dest.with_name(dest.name + ".partial.tif")
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
    tmp = dest.with_name(dest.name + ".partial")
    info = zipfile.ZipInfo(path.name, date_time=(2026, 9, 30, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    with zipfile.ZipFile(tmp, "w") as z:
        z.writestr(info, path.read_bytes())
    with zipfile.ZipFile(tmp) as z:
        if z.namelist() != [path.name] or z.testzip() is not None or z.read(path.name) != path.read_bytes():
            raise ValueError("ZIP does not contain exactly the validated GeoTIFF")
    tmp.replace(dest)
    return dest

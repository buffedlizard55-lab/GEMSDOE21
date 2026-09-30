"""Verify every grid/hash, flag template/metadata irregularities, prepare label-free vectors."""

from __future__ import annotations

import gc
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.features import coorientation, dequantize, local_residual  # noqa: E402
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from download_data import CORE_HASHES  # noqa: E402


def main():
    data = data_dir()
    vec = data / "prepared"
    vec.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_utc": utc_now(),
        "rasters": {},
        "features": {},
        "model_inputs_catalogue_derived": False,
        "transport_not_official_auth": True,
    }
    with rasterio.open(data / "sample_submission.tif") as t:
        template = t.read(1)
        footprint = np.isfinite(template) & (t.read_masks(1) > 0)
        grid = {"shape": list(t.shape), "crs": str(t.crs), "transform": list(t.transform)[:6]}
        shape, crs, transform = t.shape, t.crs, t.transform
    for file, want in CORE_HASHES.items():
        path = data / file
        if sha256(path) != want:
            raise ValueError(f"{file} SHA mismatch")
        with rasterio.open(path) as s:
            if s.shape != shape or s.crs != crs or s.transform != transform:
                raise ValueError(f"{file} grid mismatch")
            report["rasters"][file] = {
                "sha256": want,
                "bytes": path.stat().st_size,
                "grid": grid,
                "bands": s.count,
                "dtypes": list(s.dtypes),
            }
    with rasterio.open(data / "labels.tif") as s:
        catalogue = (s.read(1) > 0) & footprint
    report.update(
        footprint_pixels=int(footprint.sum()),
        outside_pixels=int((~footprint).sum()),
        known_pixels=int(catalogue.sum()),
        template_positive_pixels=int((template[footprint] > 0).sum()),
        template_positive_mask_equals_catalogue=bool(np.array_equal((template > 0) & footprint, catalogue)),
    )
    np.save(vec / "footprint.npy", footprint)
    # Scorer-only catalogue: not a feature vector; per-fold visibility is enforced by holdout.py.
    np.save(vec / "catalogue.npy", catalogue)
    fp_idx = np.flatnonzero(footprint)
    base_cols, extra_cols = [], []

    def save(name, values, extra=False):
        a = np.asarray(values, dtype=np.float32)
        a = a.ravel()[fp_idx] if a.shape == shape else a
        if a.shape != (len(fp_idx),) or not np.isfinite(a).all():
            raise ValueError(f"Bad vector {name}: {a.shape}")
        p = vec / f"{name}.npy"
        np.save(p, a)
        report["features"][name] = {"sha256": sha256(p), "shape": list(a.shape), "catalogue_derived": False}
        (extra_cols if extra else base_cols).append(name)

    def band(n):
        with rasterio.open(data / "training_features.tif") as s:
            a = s.read(n)
            ok = np.isfinite(a) & (a > -1e20) & (s.read_masks(n) > 0) & footprint
            report.setdefault("invalid_feature_pixels", {})[str(n)] = int((footprint & ~ok).sum())
        return np.where(ok, a, 0).astype(np.float32), ok

    mag, mok = band(2)
    grav, gok = band(13)
    print("Building registered co-orientation signature (no labels)...", flush=True)
    magnitude, extra, supported = coorientation(mag, grav, mok & gok)
    for k, v in magnitude.items():
        save(k, v)
    for k, v in extra.items():
        save(k, v, extra=True)
    save("rtp_local15", local_residual(mag, mok))
    save("grav_local15", local_residual(grav, gok))
    del mag, grav, magnitude, extra
    for n, name in [(12, "det_elev_local15"), (17, "conductivity_local15")]:
        a, ok = band(n)
        save(name, local_residual(a, ok))
    a, _ = band(19)
    save("det_elev_slope", a)
    del a
    gc.collect()
    meta = json.loads((data / "external/lidar_scarp_features.json").read_text())
    with rasterio.open(data / "external/lidar_scarp_features_u8.tif") as s:
        if s.shape != shape or s.crs != crs or s.transform != transform:
            raise ValueError("Lidar grid mismatch")
        names = list(s.descriptions)
        lid = {name: dequantize(s.read(i + 1), meta["quantisation"][name]) for i, name in enumerate(names)}
    lidok = (lid["valid"] > 0.5) & footprint
    report["lidar_coverage_fraction"] = float(lidok.sum() / footprint.sum())
    for name in ["ex_max", "step_max", "coh100", "relief"]:
        save("lidar_" + name, lid[name])
    save("lidar_valid", lidok)
    save("lidar_dipole", np.sqrt(np.maximum(lid["lapneg_max"] * lid["lappos_max"], 0)))
    save(
        "lidar_tect_fluvial",
        (np.maximum(lid["downface_max"], 1.35 * lid["upface_max"]) * (0.3 + lid["coh100"]))
        / (lid["cross_max"] + 0.08),
    )
    save("lidar_antislope", lid["upface_max"] * (0.25 + lid["coh100"]) / (lid["cross_max"] + 0.10))
    save("lidar_piedmont", lid["step_max"] / np.sqrt(lid["relief"] + 9))
    del lid
    gc.collect()
    manifest = json.loads((data / "dem10/manifest.json").read_text())
    for name in manifest["channels"]:
        p = data / "dem10" / f"{name}.f32.npy"
        if sha256(p) != manifest["channel_stats"][name]["sha256"]:
            raise ValueError(f"DEM channel hash mismatch: {name}")
        v = np.load(p, mmap_mode="r")
        save(name, v)
    # Require actual gradient support, not just an interpolated class probability.
    np.save(vec / "physical_support.npy", supported.ravel()[fp_idx])
    report.update(
        base_columns=base_cols,
        candidate_extra_columns=extra_cols,
        physical_supported_pixels=int(supported.sum()),
        model_forbidden_inputs=[
            "fault distance",
            "external fault lines",
            "trained context fields",
            "GDR full-catalogue orphan flags",
            "template positive values",
        ],
        notes=[
            "template is used for grid and finite/mask footprint only; positive values are not features",
            "100m aggregate terrain features cannot reconstruct raw 1m drainage offsets",
            "band 6 tc tag is ambiguous; not used for a tilt interpretation or this model",
            "invalid source sentinels are missing data, not zero-absence targets",
        ],
    )
    write_json(vec / "manifest.json", report)
    write_json(ROOT / "evidence/data-verification.json", report)
    print(
        f"Prepared {len(base_cols)} control and {len(extra_cols)} candidate channels; "
        f"footprint={report['footprint_pixels']:,}, known={report['known_pixels']:,}",
        flush=True,
    )


if __name__ == "__main__":
    main()

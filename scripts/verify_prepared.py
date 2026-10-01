"""Independent post-run source/mask/hash guard, with no retraining or result alteration."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, write_json, utc_now  # noqa: E402
from download_data import CORE_HASHES  # noqa: E402


def verify():
    data = data_dir()
    prepared = data / "prepared"
    manifest = json.loads((prepared / "manifest.json").read_text())
    for file, digest in CORE_HASHES.items():
        if sha256(data / file) != digest:
            raise ValueError(f"Core input changed: {file}")
    with rasterio.open(data / "sample_submission.tif") as t, rasterio.open(data / "labels.tif") as s:
        fp = np.isfinite(t.read(1)) & (t.read_masks(1) > 0)
        cat = (s.read(1) > 0) & fp
    if not np.array_equal(fp, np.load(prepared / "footprint.npy")):
        raise ValueError("Prepared footprint differs from independent template read")
    if not np.array_equal(cat, np.load(prepared / "catalogue.npy")):
        raise ValueError("Prepared catalogue differs from independent labels read")
    for name, spec in manifest["features"].items():
        if sha256(prepared / f"{name}.npy") != spec["sha256"]:
            raise ValueError(f"Prepared feature changed: {name}")
    registered = ROOT / "research/preregistration-h21.md"
    from gems.locks import verify_file

    verify_file(ROOT, "research/preregistration-h21.md")
    first = ROOT / "evidence/h21-1-results.json"
    if first.exists():
        result = json.loads(first.read_text())
        verify_file(ROOT, "evidence/h21-1-results.json")
        frozen_bytes = verify_file(ROOT, "evidence/data-verification.json")
        import hashlib

        if hashlib.sha256(frozen_bytes).hexdigest() != result["source_manifest_sha256"]:
            raise ValueError("First-result preparation manifest binding is inconsistent")
        frozen = json.loads(frozen_bytes)

        def semantic(obj):
            return {k: v for k, v in obj.items() if k != "generated_utc"}

        if semantic(frozen) != semantic(manifest):
            raise ValueError("Prepared scientific inputs/metadata differ from the frozen first run")
        if sha256(registered) != result["registration_sha256"]:
            raise ValueError("Result belongs to a different registration")
        if {n: v["sha256"] for n, v in manifest["features"].items()} != result["feature_sha256"]:
            raise ValueError("Result features differ from current preparation")
    support = np.load(prepared / "physical_support.npy")
    if (
        support.shape != (int(fp.sum()),)
        or support.dtype != bool
        or int(support.sum()) != manifest["physical_supported_pixels"]
    ):
        raise ValueError("Prepared physical support shape/type/count changed")
    prior_audit = ROOT / "evidence/prepared-lineage-audit.json"
    if prior_audit.exists():
        prior = json.loads(prior_audit.read_text())
        if prior["physical_support_sha256"] != sha256(prepared / "physical_support.npy"):
            raise ValueError("Physical support differs from preserved independent audit")
    report = {
        "generated_utc": utc_now(),
        "passed": True,
        "core_hashes": CORE_HASHES,
        "catalogue_sha256": sha256(prepared / "catalogue.npy"),
        "footprint_sha256": sha256(prepared / "footprint.npy"),
        "physical_support_sha256": sha256(prepared / "physical_support.npy"),
        "independent_catalogue_and_footprint_equal": True,
        "features_verified": len(manifest["features"]),
        "first_result_sha256": sha256(first) if first.exists() else None,
        "first_result_modified": False,
        "scope": "Data/hash/mask audit only, no holdout re-test or geological success claim",
    }
    return report


def main():
    report = verify()
    write_json(ROOT / "evidence/prepared-lineage-audit.json", report)
    print("Independent prepared-input/first-result lineage: passed")


if __name__ == "__main__":
    main()

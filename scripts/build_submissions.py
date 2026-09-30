"""Publish a byte-identical H19-4 reference, not a fabricated new improvement.

New research outputs remain ignored unless the locked scientific AND current-best gates pass.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from gems.submission import validate, write, zip_single  # noqa: E402
from download_data import H19_NAME, H19_SHA  # noqa: E402


def main():
    data = data_dir()
    src = data / "historical" / H19_NAME
    template = data / "sample_submission.tif"
    source_checks = validate(src, template, H19_SHA)
    if not source_checks["passed"]:
        raise ValueError(f"Historical file fails preflight: {source_checks['checks']}")
    with rasterio.open(src) as s, rasterio.open(template) as t, rasterio.open(data / "labels.tif") as lab:
        pred = s.read(1)
        footprint = np.isfinite(t.read(1)) & (t.read_masks(1) > 0)
        known = (lab.read(1) > 0) & footprint
    cid = hashlib.sha256((pred[footprint & ~known] > 0.5).astype(np.uint8).tobytes()).hexdigest()[:8]
    if cid != "691e4dfa":
        raise ValueError("Historical scored-pixel identity changed")
    downloads = ROOT / "docs/downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    name = f"gems21-h19-4-reference-20260930-{cid}.tif"
    primary = downloads / name
    # Preserve ALL bytes, not just apparent value equality, and change the transport name only.
    shutil.copyfile(src, primary)
    fallback = write(pred, template, downloads / name.replace(".tif", "-masked-zero.tif"), "masked-zero")
    zipfile = zip_single(primary)
    docdata = ROOT / "docs/data"
    docdata.mkdir(parents=True, exist_ok=True)
    mask_template = write(np.zeros(footprint.shape, np.float32), template, docdata / "template-mask.tif")
    files = []
    for role, path in [("primary", primary), ("zip", zipfile), ("masked-zero fallback", fallback)]:
        entry = {
            "role": role,
            "name": path.name,
            "href": "downloads/" + path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        if path.suffix == ".tif":
            entry["preflight"] = validate(path, mask_template)
            if not entry["preflight"]["passed"]:
                raise ValueError("Published file failed independent re-read")
        files.append(entry)
    with rasterio.open(fallback) as f:
        twin = f.read(1)
        equal = np.array_equal(twin[footprint], pred[footprint])
    if not equal or sha256(primary) != H19_SHA:
        raise ValueError("Historical prediction changed while publishing")
    report = {
        "generated_utc": utc_now(),
        "role": "historical reference; NOT a novel hypothesis or new score",
        "content_id": cid,
        "source_repository": "buffedlizard55-lab/19GEMSDOE",
        "source_commit": "a3aca62fdb2be428f4245e22570cbc54082b2c15",
        "source_filename": H19_NAME,
        "source_sha256": H19_SHA,
        "byte_identical_to_h19_4": True,
        "score": 0.1894,
        "score_status": "USER-REPORTED file association; visible account best independently agrees",
        "note": "GEMS21 | H19-4 historical reference | id 691e4dfa | same predictions, not a new experiment",
        "files": files,
        "template_mask_sha256": sha256(mask_template),
        "prediction_inside_footprint_equal_across_variants": equal,
        "known_pixels_predicted": int((pred[known] > 0).sum()),
        "new_submission_recommended": False,
        "warning": "Do not spend a slot re-uploading an existing scored field. A filename change cannot improve DTI.",
        "fallback_caveat": "All raw values finite [0,1]; outside marked null using internal GDAL mask. Platform acceptance untested.",
    }
    write_json(ROOT / "evidence/submission-validation.json", report)
    write_json(docdata / "submissions.json", report)
    print(
        f"Published {name}; SHA={H19_SHA}; footprint positives={source_checks['positive_footprint_pixels']:,}"
    )


if __name__ == "__main__":
    main()

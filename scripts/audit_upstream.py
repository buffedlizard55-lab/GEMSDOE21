"""Pinned-source line audit and scored-pixel comparison; NOT a holdout of pretrained fields."""

from __future__ import annotations

import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from download_data import G19, H19_NAME, H19_SHA, fetch  # noqa: E402

G16 = ("buffedlizard55-lab/16GEMSDOE", "962587af0d16a50d45e32a80a3c90436435cb9d8")
H16_NAME = "gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif"
H16_SHA = "055309694ed499ca3d87e76b3f5e81c292aef6e39c418d33ff5a817aa1309bea"


def main():
    data = data_dir()
    upstream = data / "audit/19GEMSDOE"
    paths = [
        "src/gems/hypotheses.py",
        "src/gems/holdout.py",
        "src/gems/metric.py",
        "scripts/run_spatial_holdout_and_build.py",
        "scripts/evaluate_h19_and_build_submissions.py",
        "README.md",
    ]
    content = {}
    hashes = {}
    for path in paths:
        local = upstream / path
        fetch(G19, path, local)
        content[path] = local.read_text()
        hashes[path] = sha256(local)
    findings = []

    def finding(id, path, text, interpretation, status="VERIFIED CODE"):
        lines = content[path].splitlines()
        n = next(i + 1 for i, line in enumerate(lines) if text in line)
        findings.append(
            {
                "id": id,
                "status": status,
                "file": path,
                "line": n,
                "excerpt": lines[n - 1].strip(),
                "finding": interpretation,
                "source": f"https://github.com/{G19[0]}/blob/{G19[1]}/{path}#L{n}",
            }
        )

    finding(
        "A01",
        paths[0],
        "0.57 * L3_open + 0.35 * L4_anti",
        "L3 and L4 scarp experts total 92% of lidar-regime blend, not four equal lines.",
    )
    finding(
        "A02",
        paths[0],
        "0.506 * L3_open + 0.35 * L4_anti",
        "Scarp experts total 85.6% of gap-regime blend before quantile/gate.",
    )
    finding(
        "A03",
        paths[0],
        "0.95 * p_scarp_anti_16",
        "The arm called L4 is a scarp/terrain-geophysics expert, not an independent pure geopotential measurement.",
    )
    finding(
        "A04",
        paths[0],
        "np.clip(second_best / 0.18, 0.35, 1.0)",
        "Gate attenuates to 35%; it does not completely discard all single-layer matches.",
    )
    finding(
        "A05",
        paths[3],
        "y_tr = np.r_[np.ones",
        "Uncatalogued samples are assigned binary-negative targets, not nnPU risk.",
    )
    finding(
        "A06",
        paths[3],
        "near_cat_2d = binary_dilation(labels",
        "Negative-sampling collar derives from the full catalogue, including held-out labels.",
    )
    finding(
        "A07",
        paths[1],
        "mask_predictions: bool = False",
        "Sparse scoring default can retain TP credit from known masked predictions.",
    )
    finding(
        "A08",
        paths[4],
        "oof_probs_h19_arms.npz",
        "H19 exporter requires a prediction cache absent from the pinned repository tree.",
    )
    tree = subprocess.check_output(["gh", "api", f"repos/{G19[0]}/git/trees/{G19[1]}?recursive=1"], text=True)
    import json

    tree = json.loads(tree)
    tracked = [t["path"] for t in tree["tree"] if t["type"] == "blob"]
    # Search ALL committed Python, not only selected filenames, before saying no generator exists.
    hits = []
    for path in tracked:
        if not path.endswith(".py"):
            continue
        if path not in content:
            local = upstream / path
            fetch(G19, path, local)
            content[path] = local.read_text()
        for n, line in enumerate(content[path].splitlines(), 1):
            if "oof_probs_h19_arms" in line:
                hits.append({"file": path, "line": n, "text": line.strip()})
    fetch(G16, "docs/downloads/" + H16_NAME, data / "historical/h16-1.tif", H16_SHA)
    with rasterio.open(data / "sample_submission.tif") as s:
        fp = np.isfinite(s.read(1))
    with rasterio.open(data / "labels.tif") as s:
        known = (s.read(1) > 0) & fp
    with rasterio.open(data / "historical/h16-1.tif") as s:
        p16 = s.read(1)
    with rasterio.open(data / "historical" / H19_NAME) as s:
        p19 = s.read(1)
    if sha256(data / "historical" / H19_NAME) != H19_SHA:
        raise ValueError("H19 reference identity mismatch")
    domain = fp & ~known
    a, b = p16[domain] > 0.5, p19[domain] > 0.5
    overlap = {
        "h16_scored_positive_pixels": int(a.sum()),
        "h19_scored_positive_pixels": int(b.sum()),
        "intersection": int((a & b).sum()),
        "union": int((a | b).sum()),
        "jaccard": float((a & b).sum() / (a | b).sum()),
        "added_pixels": int((b & ~a).sum()),
        "removed_pixels": int((a & ~b).sum()),
        "h19_known_pixel_positives": int((p19[known] > 0).sum()),
        "h19_scored_content_id": hashlib.sha256(b.astype(np.uint8).tobytes()).hexdigest()[:8],
    }
    # Thermal CSV audit: rows are records, not unique wells/springs. Full-catalogue distance is forbidden.
    rows = list(csv.DictReader((data / "external/gdr_wellspring_in_footprint.csv").open()))
    unique_locations = {(r["row"], r["col"]) for r in rows}
    csv_audit = {
        "records": len(rows),
        "unique_100m_cells": len(unique_locations),
        "contains_full_catalogue_distance": "dist_known_fault_px" in rows[0],
        "contains_well_depth": any("depth" in k.lower() for k in rows[0]),
        "model_used_this_csv": False,
        "warning": "Joined chemistry/sample rows are not independent site counts. A hot observation does not prove a local unmapped fault.",
    }
    report = {
        "generated_utc": utc_now(),
        "source_repository": G19[0],
        "source_commit": G19[1],
        "tracked_python_files_inspected": len([p for p in tracked if p.endswith(".py")]),
        "source_sha256": hashes,
        "line_findings": findings,
        "h19_cache_references": hits,
        "h19_cache_tracked": any("oof_probs_h19_arms" in p for p in tracked),
        "historical_mask_comparison": overlap,
        "thermal_csv_audit": csv_audit,
        "score_difference_user_reported": 0.1894 - 0.1855,
        "causal_attribution": "UNIDENTIFIED: different predictions, no controlled component ablation on hidden labels",
        "not_a_holdout_evaluation": True,
    }
    write_json(ROOT / "evidence/upstream-audit.json", report)
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=["id", "status", "file", "line", "excerpt", "finding", "source"]
    )
    writer.writeheader()
    writer.writerows(findings)
    (ROOT / "evidence/upstream-line-audit.csv").write_text(output.getvalue())
    print(json.dumps(overlap, indent=2))
    print(json.dumps(csv_audit, indent=2))


if __name__ == "__main__":
    main()

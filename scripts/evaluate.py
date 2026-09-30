"""Run ONLY the locked H21-1 comparison. No leaderboard contact or parameter sweep."""

from __future__ import annotations

import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.holdout import WholeSegmentHoldout  # noqa: E402
from gems.inference import emit  # noqa: E402
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from gems.metric import dti  # noqa: E402
from gems.pu import NNPULogistic  # noqa: E402
from gems.statistics import promotion, sign_flip  # noqa: E402


def main():
    t0 = time.monotonic()
    data = data_dir()
    vec = data / "prepared"
    manifest = json.loads((vec / "manifest.json").read_text())
    for name, spec in manifest["features"].items():
        if sha256(vec / f"{name}.npy") != spec["sha256"]:
            raise ValueError(f"Prepared feature changed: {name}")
    registration = ROOT / "research/preregistration-h21.md"
    locked = subprocess.check_output(["git", "show", "2dfc5de:research/preregistration-h21.md"], cwd=ROOT)
    if locked != registration.read_bytes():
        raise ValueError("Registration changed after its pre-results commit")
    fp = np.load(vec / "footprint.npy")
    cat = np.load(vec / "catalogue.npy")
    idx = np.flatnonzero(fp)
    supported = np.zeros(fp.shape, dtype=bool)
    supported.ravel()[idx] = np.load(vec / "physical_support.npy")
    holdout = WholeSegmentHoldout(fp, cat)
    features = {name: np.load(vec / f"{name}.npy", mmap_mode="r") for name in manifest["features"]}
    base_cols = manifest["base_columns"]
    extra_cols = manifest["candidate_extra_columns"]
    feature_sets = {"C21-PU": base_cols, "H21-1": base_cols + extra_cols}
    report = {
        "experiment_id": "H21-1-fixed-v1",
        "generated_utc": utc_now(),
        "registration_commit": "2dfc5de",
        "registration_sha256": sha256(registration),
        "metric": {"alpha": 0.2, "beta": 0.8, "radius_pixels": 3, "catalogue_mask": "pixel-exact all terms"},
        "scope": "known whole-segment hide/recover with incomplete-reference sensitivity; NOT hidden test score",
        "source_manifest_sha256": sha256(vec / "manifest.json"),
        "feature_sha256": {n: spec["sha256"] for n, spec in manifest["features"].items()},
        "label_free_features": True,
        "confirmed_negative_targets": 0,
        "weekly_slots_spent": 0,
        "budget_fraction": 0.025,
        "family_size": 4,
        "folds": [],
        "blocks": [],
        "current_best_comparator": {
            "id": "H19-4",
            "reproducible_on_this_protocol": False,
            "reason": "Missing upstream H19 arm generation; old PU/masking/segment protocol differs.",
        },
    }
    # Non-overlapping fixed 4x4 blocks, within outer geographic rectangle. Empty-truth blocks are
    # retained in fold FP summaries; paired block test excludes only blocks with no reference truth.
    ycuts = np.linspace(0, fp.shape[0], 5, dtype=int)
    xcuts = np.linspace(0, fp.shape[1], 5, dtype=int)
    pooled = {name: np.zeros(fp.shape, dtype=bool) for name in feature_sets}
    all_converged = True
    for i in range(4):
        fold = holdout.fold(i)
        audit = holdout.audit(fold)
        if not audit["passes"]:
            raise RuntimeError("Holdout leaks a whole segment")
        allowed = fold.train_domain.ravel()[idx]
        visible = fold.visible_catalogue.ravel()[idx]
        rng = np.random.default_rng(210930 + i)
        p_all, u_all = np.flatnonzero(allowed & visible), np.flatnonzero(allowed)
        pidx = rng.choice(p_all, min(30000, len(p_all)), replace=False)
        uidx = rng.choice(u_all, min(100000, len(u_all)), replace=False)
        test_idx = np.flatnonzero(fold.region.ravel()[idx])
        detail = {
            "id": i,
            "name": fold.name,
            "audit": audit,
            "models": {},
            "positive_sample_count": len(pidx),
            "unlabeled_sample_count": len(uidx),
            "unlabeled_sample_contains_known_positives": int(visible[uidx].sum()),
        }
        print(
            f"Fold {fold.name}: {len(pidx)} P, {len(uidx)} U; {audit['withheld_whole_components']} whole hidden segments",
            flush=True,
        )
        for name, cols in feature_sets.items():
            xp = np.column_stack([features[c][pidx] for c in cols])
            xu = np.column_stack([features[c][uidx] for c in cols])
            model = NNPULogistic().fit(xp, xu)
            all_converged &= model.fit_report["success"]
            score = np.zeros(fp.shape, dtype=np.float32)
            for offset in range(0, len(test_idx), 100000):
                sel = test_idx[offset : offset + 100000]
                x = np.column_stack([features[c][sel] for c in cols])
                score.ravel()[idx[sel]] = model.predict(x)
            pred = emit(score, fold.region, fold.visible_catalogue, supported)
            pooled[name] |= pred
            dense = dti(pred, fold.dense_truth, valid=fold.region, known=cat & ~fold.hidden)
            sparse = dti(pred, fold.sparse_truth, valid=fold.region, known=fold.sparse_known)
            detail["models"][name] = {
                "fit": model.fit_report,
                "dense": dense,
                "sparse": sparse,
                "columns": cols,
            }
            print(
                f"  {name}: dense={dense['dti']:.6f}, sparse={sparse['dti']:.6f}; "
                f"TP={dense['TP_w']:.1f}, FP={dense['FP_w']:.1f}, FN={dense['FN_w']:.1f}; "
                f"converged={model.fit_report['success']}",
                flush=True,
            )
            del xp, xu, x, score, pred, model
        report["folds"].append(detail)
    for yi in range(4):
        for xi in range(4):
            sl = (slice(ycuts[yi], ycuts[yi + 1]), slice(xcuts[xi], xcuts[xi + 1]))
            truth = cat[sl]
            valid = fp[sl]
            if not (truth & valid).any():
                continue
            record = {"id": f"B{yi}{xi}", "models": {}}
            for name in feature_sets:
                record["models"][name] = dti(pooled[name][sl], truth, valid)
            report["blocks"].append(record)
    report["summary"] = {}
    for name in feature_sets:
        dense = [f["models"][name]["dense"] for f in report["folds"]]
        sparse = [f["models"][name]["sparse"] for f in report["folds"]]
        totals = {k: sum(x[k] for x in dense) for k in ("TP_w", "FP_w", "FN_w", "alpha_FP", "beta_FN")}
        report["summary"][name] = {
            "dense": [x["dti"] for x in dense],
            "sparse": [x["dti"] for x in sparse],
            "mean_dense_dti": float(np.mean([x["dti"] for x in dense])),
            "mean_sparse_dti": float(np.mean([x["dti"] for x in sparse])),
            "recovery": totals["TP_w"] / sum(x["n_truth"] for x in dense),
            **totals,
        }
    deltas = [b["models"]["H21-1"]["dti"] - b["models"]["C21-PU"]["dti"] for b in report["blocks"]]
    report["block_test"] = sign_flip(deltas)
    dense_deltas = np.array(report["summary"]["H21-1"]["dense"]) - report["summary"]["C21-PU"]["dense"]
    report["quadrant_sign_flip_diagnostic"] = sign_flip(dense_deltas)
    report["gate"] = promotion(
        report["summary"]["C21-PU"],
        report["summary"]["H21-1"],
        report["block_test"],
        all_converged,
        current_best_reproducible=False,
    )
    c, h = report["summary"]["C21-PU"], report["summary"]["H21-1"]
    report["prediction_check"] = {
        "registered_dense_dti_delta": 0.008,
        "observed_dense_dti_delta": h["mean_dense_dti"] - c["mean_dense_dti"],
        "registered_recovery_delta": 0.015,
        "observed_recovery_delta": h["recovery"] - c["recovery"],
        "registered_fp_relative_change": -0.03,
        "observed_fp_relative_change": h["FP_w"] / c["FP_w"] - 1,
        "registered_sparse_dti_delta": 0.004,
        "observed_sparse_dti_delta": h["mean_sparse_dti"] - c["mean_sparse_dti"],
        "beat_registered_dense_prediction": bool(h["mean_dense_dti"] - c["mean_dense_dti"] >= 0.008),
    }
    report["disposition"] = (
        "REJECTED" if not report["gate"]["control_pass"] else "CONTROL PASS; SUBMISSION BLOCKED"
    )
    report["elapsed_seconds"] = round(time.monotonic() - t0, 2)
    research = data / "research"
    research.mkdir(exist_ok=True)
    # Experimental masks stay ignored, cannot be mistaken for a released recommendation.
    for name, pred in pooled.items():
        np.savez_compressed(research / f"{name}-oof-mask.npz", pred=pred)
    write_json(ROOT / "evidence/h21-1-results.json", report)
    print(
        f"{report['disposition']}; submission eligible={report['gate']['submission_eligible']}; "
        f"elapsed {report['elapsed_seconds']}s",
        flush=True,
    )


if __name__ == "__main__":
    main()

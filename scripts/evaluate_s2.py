"""ONE prospective exploratory H21-5 test; never an untouched-confirmation/leaderboard score.

No hyperparameter/budget sweep. Whole official NUM-linked groups purged from every model
input; unlabeled stays unlabeled. Current-best and fresh-confirmation gates fail closed.
"""

from __future__ import annotations

import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")

import gc
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.emission_guard import strict_emit  # noqa: E402
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from gems.locks import verify_file  # noqa: E402
from gems.metric import dti  # noqa: E402
from gems.partitioned_metric import aggregate, partitions  # noqa: E402
from gems.pu import NNPULogistic  # noqa: E402
from gems.statistics import sign_flip  # noqa: E402
from gems.system_holdout import SystemHoldout  # noqa: E402
from prepare_s2 import prepare  # noqa: E402


def gate(control, candidate, block_test, all_converged):
    dense = np.asarray(candidate["dense"]) - control["dense"]
    sparse = np.asarray(candidate["sparse"]) - control["sparse"]
    dense_gain, sparse_gain = float(dense.mean()), float(sparse.mean())
    recovery_gain = candidate["recovery"] - control["recovery"]
    fp_change = candidate["FP_w"] / control["FP_w"] - 1 if control["FP_w"] > 0 else None
    forecast = {
        "dense_gain_at_least_forecast_0_006": dense_gain >= 0.006,
        "sparse_gain_at_least_forecast_0_002": sparse_gain >= 0.002,
        "recovery_gain_at_least_forecast_0_008": recovery_gain >= 0.008,
        "fp_change_at_most_forecast_minus_2pct": fp_change is not None and fp_change <= -0.02,
    }
    quality = {
        "at_least_three_dense_fold_wins": int((dense > 0).sum()) >= 3,
        "no_fold_loss_below_minus_0_01": min(dense.min(), sparse.min()) >= -0.01,
        "eight_candidate_corrected_p_under_0_05": block_test["p_bonferroni"] < 0.05,
        "all_fits_converged": bool(all_converged),
    }
    return {
        "delta_dense": dense_gain,
        "delta_sparse": sparse_gain,
        "delta_recovery": float(recovery_gain),
        "fp_relative_change": None if fp_change is None else float(fp_change),
        "forecast_rules": {k: bool(v) for k, v in forecast.items()},
        "quality_rules": {k: bool(v) for k, v in quality.items()},
        "forecast_pass": all(forecast.values()),
        "exploratory_control_pass": bool(all(forecast.values()) and all(quality.values())),
        "current_best_reproducible": False,
        "fresh_confirmation": False,
        "submission_eligible": False,
        "blocking_reason": "H19 clean generator unavailable; evaluation geography observed previously. Diagnostics cannot establish confirmation or leaderboard improvement.",
    }


def main():
    output = ROOT / "evidence/h21-5-results.json"
    masks = data_dir() / "research/H21-5-first-masks"
    if output.exists() or masks.exists():
        raise ValueError("Refusing to overwrite or retest a preserved H21-5 first outcome/mask directory")
    verify_file(ROOT, "research/preregistration-h21-s2.md")
    verify_file(ROOT, "evidence/h21-1-results.json")
    t0 = time.monotonic()
    prepared = prepare()
    data = data_dir()
    base, extra = data / "prepared", data / "prepared-s2"
    original = json.loads((base / "manifest.json").read_text())
    fp, cat, groups = [
        np.load(path) for path in [base / "footprint.npy", base / "catalogue.npy", extra / "groups.npy"]
    ]
    idx = np.flatnonzero(fp)
    geometry = {int(k): v for k, v in json.loads((extra / "group-geometry.json").read_text()).items()}
    with rasterio.open(data / "sample_submission.tif") as t:
        holdout = SystemHoldout(fp, cat, groups, geometry, t.transform)
    strength = np.zeros(fp.shape, dtype=np.float32)
    strength.ravel()[idx] = np.load(extra / "physical_strength.npy")
    base_cols, extra_cols = original["base_columns"], prepared["candidate_columns"]
    sets = {"C21-S2-PU": base_cols, "H21-5": base_cols + extra_cols}
    features = {n: np.load(base / f"{n}.npy", mmap_mode="r") for n in base_cols}
    features.update({n: np.load(extra / f"{n}.npy", mmap_mode="r") for n in extra_cols})
    code_paths = sorted((ROOT / "src/gems").glob("*.py")) + [
        ROOT / "scripts/evaluate_s2.py",
        ROOT / "scripts/prepare_s2.py",
    ]
    report = {
        "experiment_id": "H21-5-signed-step-system-holdout-exploratory-v1",
        "generated_utc": utc_now(),
        "registration_commit": "452c21c",
        "registration_sha256": sha256(ROOT / "research/preregistration-h21-s2.md"),
        "implementation_before_results_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "code_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in code_paths},
        "runner": {"actions_run_id": os.environ.get("GITHUB_RUN_ID"), "cpu_threads": 2},
        "metric": {
            "alpha": 0.2,
            "beta": 0.8,
            "radius_pixels": 3,
            "known_mask": "pixel-exact before all distances and terms",
        },
        "scope": "Prospective exploratory whole-system hide/recover on previously observed geography; NOT fresh confirmation or a hidden score",
        "fresh_evaluation": False,
        "first_h21_1_preserved_sha256": sha256(ROOT / "evidence/h21-1-results.json"),
        "source_preparation_sha256": sha256(extra / "manifest.json"),
        "input_and_output_sha256": prepared["output_sha256"],
        "official_vector_sha256": prepared["official_vector_sha256"],
        "grouping_audit": prepared["grouping_audit"],
        "feature_audit": prepared["feature_audit"],
        "confirmed_negative_targets": 0,
        "label_free_predictors": True,
        "budget_fraction": 0.025,
        "family_size": 8,
        "weekly_slots_spent": 0,
        "folds": [],
        "blocks": [],
        "current_best_comparator": {
            "id": "H19-4",
            "reproducible": False,
            "reason": "No generator in audited main or original PR head; cannot use historical map as OOF comparator",
        },
    }
    ycuts, xcuts = np.linspace(0, fp.shape[0], 5, dtype=int), np.linspace(0, fp.shape[1], 5, dtype=int)
    owners = np.zeros(fp.shape, dtype=np.int8)
    for yi in range(4):
        for xi in range(4):
            owners[ycuts[yi] : ycuts[yi + 1], xcuts[xi] : xcuts[xi + 1]] = yi * 4 + xi
    block_parts = {name: [[] for _ in range(16)] for name in sets}
    all_converged = True
    masks.mkdir(parents=True)
    for i in range(4):
        fold = holdout.fold(i)
        audit = holdout.audit(fold)
        if not audit["passes"]:
            raise ValueError("Whole-system/geometry-buffer holdout leaks")
        allowed = fold.train_domain.ravel()[idx]
        visible = fold.visible_catalogue.ravel()[idx]
        rng = np.random.default_rng(210930 + i)
        pa, ua = np.flatnonzero(allowed & visible), np.flatnonzero(allowed)
        pidx = rng.choice(pa, min(30000, len(pa)), replace=False)
        uidx = rng.choice(ua, min(100000, len(ua)), replace=False)
        test = np.flatnonzero(fold.region.ravel()[idx])
        detail = {
            "id": i,
            "name": fold.name,
            "audit": audit,
            "models": {},
            "positive_sample_count": len(pidx),
            "unlabeled_sample_count": len(uidx),
            "unlabeled_sample_includes_known_positives": int(visible[uidx].sum()),
            "positive_indices_sha256": hashlib.sha256(pidx.tobytes()).hexdigest(),
            "unlabeled_indices_sha256": hashlib.sha256(uidx.tobytes()).hexdigest(),
        }
        print(
            f"Fold {fold.name}: {len(pidx)} P / {len(uidx)} U, {len(fold.hidden_component_ids)} whole groups hidden",
            flush=True,
        )
        for name, columns in sets.items():
            xp = np.column_stack([features[c][pidx] for c in columns])
            xu = np.column_stack([features[c][uidx] for c in columns])
            model = NNPULogistic(max_iter=1000).fit(xp, xu)
            all_converged &= model.fit_report["success"]
            score = np.zeros(fp.shape, dtype=np.float32)
            for begin in range(0, len(test), 100000):
                selected = test[begin : begin + 100000]
                x = np.column_stack([features[c][selected] for c in columns])
                score.ravel()[idx[selected]] = model.predict(x)
            pred = strict_emit(score, fold.region, fold.visible_catalogue, strength)
            known = cat & ~fold.hidden
            dense = dti(pred, fold.dense_truth, fold.region, known)
            sparse = dti(pred, fold.sparse_truth, fold.region, fold.sparse_known)
            parts = partitions(pred, fold.dense_truth, fold.region, known, owners)
            partition_total = aggregate(parts)
            for k in ("TP_w", "FP_w", "FN_w", "dti", "emitted_pixels"):
                if not np.isclose(partition_total[k], dense[k], atol=1e-8, rtol=1e-12):
                    raise ValueError("Owned-block kernel context does not conserve the official fold metric")
            for block, part in enumerate(parts):
                block_parts[name][block].append(part)
            path = masks / f"{fold.name}-{name}.npz"
            np.savez_compressed(path, pred=pred)
            detail["models"][name] = {
                "fit": model.fit_report,
                "dense": dense,
                "sparse": sparse,
                "columns": columns,
                "prediction_cache_sha256": sha256(path),
                "emission": "strict NMS, positive physical strength, no budget padding",
            }
            print(
                f"  {name}: dense={dense['dti']:.6f}; sparse={sparse['dti']:.6f}; TP={dense['TP_w']:.1f}, FP={dense['FP_w']:.1f}, FN={dense['FN_w']:.1f}; converged={model.fit_report['success']}",
                flush=True,
            )
            del xp, xu, score, pred, model, x
            gc.collect()
        report["folds"].append(detail)
        del fold
        gc.collect()
    for block in range(16):
        report["blocks"].append(
            {
                "id": f"B{block // 4}{block % 4}",
                "models": {name: aggregate(block_parts[name][block]) for name in sets},
                "context": "full originating-fold kernels retained across block borders; fold masks never blended",
            }
        )
    report["summary"] = {}
    for name in sets:
        dense = [f["models"][name]["dense"] for f in report["folds"]]
        sparse = [f["models"][name]["sparse"] for f in report["folds"]]
        total = aggregate(dense)
        report["summary"][name] = {
            "dense": [r["dti"] for r in dense],
            "sparse": [r["dti"] for r in sparse],
            "mean_dense_dti": float(np.mean([r["dti"] for r in dense])),
            "mean_sparse_dti": float(np.mean([r["dti"] for r in sparse])),
            "pooled_component_dti": total["dti"],
            **{k: v for k, v in total.items() if k != "dti"},
        }
    deltas = [
        b["models"]["H21-5"]["dti"] - b["models"]["C21-S2-PU"]["dti"]
        for b in report["blocks"]
        if b["models"]["H21-5"]["n_truth"] > 0
    ]
    report["block_test"] = sign_flip(deltas, family_size=8)
    report["block_test"]["inferential_status"] = (
        "exploratory diagnostic; previously observed geography and spatial dependence"
    )
    control, candidate = report["summary"]["C21-S2-PU"], report["summary"]["H21-5"]
    report["quadrant_sign_flip_diagnostic"] = sign_flip(
        np.asarray(candidate["dense"]) - control["dense"], family_size=8
    )
    report["gate"] = gate(control, candidate, report["block_test"], all_converged)
    report["disposition"] = (
        "EXPLORATORY FORECAST PASS; PROMOTION BLOCKED"
        if report["gate"]["exploratory_control_pass"]
        else "REJECTED FOR PROMOTION"
    )
    report["elapsed_seconds"] = round(time.monotonic() - t0, 2)
    write_json(output, report)
    print(f"{report['disposition']}; no weekly slot or new competition artifact", flush=True)


if __name__ == "__main__":
    main()

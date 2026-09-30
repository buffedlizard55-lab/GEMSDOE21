"""Registered paired spatial-block sign-flip test, with conservative family correction."""

from __future__ import annotations

import numpy as np


def sign_flip(deltas, family_size=4):
    d = np.asarray(deltas, dtype=float)
    if d.ndim != 1 or not np.isfinite(d).all() or not 1 <= len(d) <= 20 or family_size < 1:
        raise ValueError("Need 1..20 finite block deltas and a positive family size")
    n = len(d)
    signs = ((np.arange(1 << n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    observed = float(d.mean())
    null = (signs @ d) / n
    # Enumerate the complete randomization distribution, including the observed configuration.
    p = float(np.mean(null >= observed - 1e-12))
    return {
        "n_blocks": n,
        "mean_delta": observed,
        "p_one_sided": p,
        "family_size": family_size,
        "p_bonferroni": min(1.0, family_size * p),
        "assumption": "paired block sign exchangeability; adjacent blocks may remain correlated",
    }


def promotion(control, candidate, block_test, fits_converged, current_best_reproducible=False):
    dense_delta = np.mean(candidate["dense"]) - np.mean(control["dense"])
    sparse_delta = np.mean(candidate["sparse"]) - np.mean(control["sparse"])
    rules = {
        "dense_gain_at_least_0_003": bool(dense_delta >= 0.003),
        "sparse_gain_positive": bool(sparse_delta > 0),
        "dense_fold_wins_at_least_3": bool(sum(np.array(candidate["dense"]) > control["dense"]) >= 3),
        "no_fold_loss_over_0_01": bool(
            min(
                np.min(np.array(candidate["dense"]) - control["dense"]),
                np.min(np.array(candidate["sparse"]) - control["sparse"]),
            )
            >= -0.01
        ),
        "recovery_does_not_drop": bool(candidate["recovery"] >= control["recovery"]),
        "family_corrected_p_under_0_05": bool(block_test["p_bonferroni"] < 0.05),
        "fits_converged": bool(fits_converged),
    }
    return {
        "control_pass": all(rules.values()),
        "control_rules": rules,
        "current_best_reproducible": bool(current_best_reproducible),
        "submission_eligible": bool(all(rules.values()) and current_best_reproducible),
        "delta_dense": float(dense_delta),
        "delta_sparse": float(sparse_delta),
        "reason": "Cannot claim improvement over H19-4 without its leakage-safe reproducible comparator.",
    }

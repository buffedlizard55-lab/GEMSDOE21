"""Owned-pixel metric partitions with FULL same-fold kernel context.

Unlike scoring cropped blocks independently, a neighbour across a block boundary can
supply true-positive credit. Catalogue and fold masks are applied before distances.
This implementation is binary-only, matching H21-5's registered emission protocol.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

from .metric import ALPHA, BETA, EPS, RADIUS


def from_components(tp, fp, fn, n_truth, emitted_pixels, mass):
    denominator = tp + ALPHA * fp + BETA * fn + EPS
    return {
        "TP_w": float(tp),
        "FP_w": float(fp),
        "FN_w": float(fn),
        "alpha_FP": float(ALPHA * fp),
        "beta_FN": float(BETA * fn),
        "dti": float(tp / denominator),
        "denominator": float(denominator),
        "n_truth": int(n_truth),
        "emitted_pixels": int(emitted_pixels),
        "mass": float(mass),
        "recovery": float(tp / n_truth) if n_truth else 0.0,
        "fp_interpretation": "unverified prediction mass against incomplete reference; not proved negatives",
    }


def partitions(pred, truth, valid, known, owners, n_parts=16):
    pred, truth, valid, known, owners = map(np.asarray, (pred, truth, valid, known, owners))
    if pred.ndim != 2 or any(a.shape != pred.shape for a in (truth, valid, known, owners)):
        raise ValueError("All partition arrays must be matched 2D arrays")
    domain = valid.astype(bool) & ~known.astype(bool)
    values = pred[domain]
    if not np.isfinite(values).all() or not np.isin(values, [0, 1]).all():
        raise ValueError("Partitioned H21-5 metric requires finite binary predictions")
    if not np.isfinite(truth[domain]).all():
        raise ValueError("Truth must be finite in domain")
    if (
        n_parts < 1
        or not np.issubdtype(owners.dtype, np.integer)
        or (owners[domain] < 0).any()
        or (owners[domain] >= n_parts).any()
    ):
        raise ValueError("Every evaluated pixel needs one valid integer partition owner")
    p = (pred > 0) & domain
    g = (truth > 0) & domain
    op, og = owners[p], owners[g]
    n_truth = np.bincount(og, minlength=n_parts)
    emitted = np.bincount(op, minlength=n_parts)
    tp = np.zeros(n_parts, dtype=np.float64)
    fp = emitted.astype(np.float64)
    if p.any() and g.any():
        dp = distance_transform_edt(~p)
        credit = np.maximum(1 - dp[g] / RADIUS, 0)
        tp = np.bincount(og, weights=credit, minlength=n_parts)
        del dp
        dg = distance_transform_edt(~g)
        fp = np.bincount(op, weights=np.minimum(dg[p] / RADIUS, 1), minlength=n_parts)
    fn = n_truth - tp
    return [from_components(tp[i], fp[i], fn[i], n_truth[i], emitted[i], emitted[i]) for i in range(n_parts)]


def aggregate(metrics):
    keys = ("TP_w", "FP_w", "FN_w", "n_truth", "emitted_pixels", "mass")
    totals = {k: sum(m[k] for m in metrics) for k in keys}
    return from_components(
        totals["TP_w"],
        totals["FP_w"],
        totals["FN_w"],
        totals["n_truth"],
        totals["emitted_pixels"],
        totals["mass"],
    )

"""Official distance-weighted Tversky index; exact catalogue exclusion in ALL terms.

https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4

FP_w is the official penalty against an incomplete reference. It is NOT evidence
that those pixels are geologically negative. Never use it as a negative-label target.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA, BETA, RADIUS, EPS = 0.2, 0.8, 3.0, 1e-7


def offsets(radius: float = RADIUS):
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("Radius must be finite and positive")
    n = int(np.ceil(radius))
    return [
        (dy, dx, 1 - np.hypot(dy, dx) / radius)
        for dy in range(-n, n + 1)
        for dx in range(-n, n + 1)
        if np.hypot(dy, dx) < radius
    ]


def dti(pred, truth, valid=None, known=None) -> dict:
    """Exact probabilistic max-kernel TP, distance-to-new-truth FP and complementary FN.

    Outside/known pixels are removed BEFORE either distance or max calculation.
    No buffered catalogue exemption and no credit for a near-miss to a wrong label.
    """
    pred, truth = np.asarray(pred), np.asarray(truth)
    if pred.ndim != 2 or pred.shape != truth.shape:
        raise ValueError("Expected same-shaped 2D prediction and truth")
    domain = np.ones(pred.shape, dtype=bool) if valid is None else np.asarray(valid, dtype=bool).copy()
    if domain.shape != pred.shape:
        raise ValueError("Valid shape differs")
    if known is not None:
        known = np.asarray(known, dtype=bool)
        if known.shape != pred.shape:
            raise ValueError("Known shape differs")
        domain &= ~known
    active = pred[domain]
    if not np.isfinite(active).all() or (active < 0).any() or (active > 1).any():
        raise ValueError("Predicted values must be finite and in range [0, 1] on evaluated pixels")
    if not np.isfinite(truth[domain]).all():
        raise ValueError("Truth must be finite in domain")
    p = np.where(domain, pred, 0).astype(np.float32)
    g = (truth > 0) & domain
    n_truth = int(g.sum())
    pp = p > 0
    if not g.any():
        tp, fp, fn = 0.0, float(p.sum(dtype=np.float64)), 0.0
    elif not pp.any():
        tp, fp, fn = 0.0, 0.0, float(n_truth)
    else:
        # Binary predictions admit an exact EDT optimization. No thresholded soft approximation.
        if np.all((p == 0) | (p == 1)):
            dp = distance_transform_edt(~pp)
            tp = float(np.maximum(1 - dp[g] / RADIUS, 0).sum(dtype=np.float64))
            del dp
        else:
            yy, xx = np.nonzero(g)
            credit = np.zeros(len(yy), dtype=np.float64)
            for dy, dx, k in offsets():
                y, x = yy + dy, xx + dx
                ok = (y >= 0) & (x >= 0) & (y < p.shape[0]) & (x < p.shape[1])
                credit[ok] = np.maximum(credit[ok], p[y[ok], x[ok]] * k)
            tp = float(credit.sum())
        dg = distance_transform_edt(~g)
        fp = float(np.sum(p[pp] * np.minimum(dg[pp] / RADIUS, 1), dtype=np.float64))
        fn = float(n_truth - tp)
    denom = tp + ALPHA * fp + BETA * fn + EPS
    return {
        "TP_w": tp,
        "FP_w": fp,
        "FN_w": fn,
        "alpha_FP": ALPHA * fp,
        "beta_FN": BETA * fn,
        "dti": tp / denom,
        "denominator": denom,
        "recovery": tp / n_truth if n_truth else 0.0,
        "weighted_precision_proxy": tp / (tp + fp) if tp + fp else 0.0,
        "n_truth": n_truth,
        "emitted_pixels": int(pp.sum()),
        "mass": float(p.sum(dtype=np.float64)),
        "fp_interpretation": "unverified prediction mass against incomplete reference; not proved negatives",
    }

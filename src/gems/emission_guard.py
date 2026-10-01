"""Post-result correctness repair, NOT activated in H21-1's preserved experiment.

The first emitter prioritizes ridge pixels and can fill with non-ridges. This corrected
helper implements a strict NMS subset AND explicit positive physical-signal strength.
S2 used this in its registered exploratory attempt, without rescuing H21-1. A subsequent
one-pixel round-versus-floor budget issue was repaired for FUTURE protocols only; no
rescoring of either preserved result is performed to manufacture an improvement.
"""

from __future__ import annotations

import numpy as np

from .inference import ridge_nms


def strict_emit(score, domain, known, physical_strength, budget=0.025):
    domain = np.asarray(domain, dtype=bool)
    strength = np.asarray(physical_strength)
    score = np.asarray(score)
    known = np.asarray(known, dtype=bool)
    if domain.ndim != 2 or any(a.shape != domain.shape for a in (score, known, strength)):
        raise ValueError("All emission arrays must be 2D and match the domain shape")
    values = score[domain]
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError("Scores must be finite and in range [0, 1] throughout the domain")
    if not 0 <= budget <= 1:
        raise ValueError("Budget must lie in [0,1]")
    if not np.isfinite(strength[domain]).all() or (strength[domain] < 0).any():
        raise ValueError("Physical signal strength must be finite and nonnegative")
    eligible = domain & ~known & (strength > 0) & np.isfinite(score) & (score > 0)
    ridge = ridge_nms(score, eligible) & eligible
    idx = np.flatnonzero(ridge)
    # A literal MAXIMUM must round down; round() can exceed it by one pixel.
    # First S2 used round; its locked result/masks are NOT regenerated with this fix.
    k = min(int(np.floor(budget * domain.sum())), len(idx))
    out = np.zeros(domain.shape, dtype=bool)
    if k:
        # Deterministic exact order; no fabricated padding from non-ridge or zero-signal cells.
        order = np.lexsort((idx, -score.ravel()[idx]))
        out.ravel()[idx[order[:k]]] = True
    return out

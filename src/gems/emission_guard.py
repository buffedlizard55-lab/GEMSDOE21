"""Post-result correctness repair, NOT activated in H21-1's preserved experiment.

The first emitter prioritizes ridge pixels and can fill with non-ridges. This corrected
helper implements a strict NMS subset AND explicit positive physical-signal strength.
Its use in a model needs a separately registered fresh validation protocol; no rescoring
of the observed shared holdout is performed to manufacture an improvement.
"""

from __future__ import annotations

import numpy as np

from .inference import ridge_nms


def strict_emit(score, domain, known, physical_strength, budget=0.025):
    domain = np.asarray(domain, dtype=bool)
    strength = np.asarray(physical_strength)
    score = np.asarray(score)
    known = np.asarray(known, dtype=bool)
    if any(a.shape != domain.shape for a in (score, known, strength)):
        raise ValueError("All emission arrays must match the domain shape")
    if not 0 <= budget <= 1:
        raise ValueError("Budget must lie in [0,1]")
    if not np.isfinite(strength[domain]).all() or (strength[domain] < 0).any():
        raise ValueError("Physical signal strength must be finite and nonnegative")
    eligible = domain & ~known & (strength > 0) & np.isfinite(score) & (score > 0)
    ridge = ridge_nms(score, eligible) & eligible
    idx = np.flatnonzero(ridge)
    k = min(int(round(budget * domain.sum())), len(idx))
    out = np.zeros(domain.shape, dtype=bool)
    if k:
        # Deterministic exact order; no fabricated padding from non-ridge or zero-signal cells.
        order = np.lexsort((idx, -score.ravel()[idx]))
        out.ravel()[idx[order[:k]]] = True
    return out

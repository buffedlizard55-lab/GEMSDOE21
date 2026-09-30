"""Fixed Hessian ridge emission, with deterministic ties and no unsupported budget padding."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


def ridge_nms(score, valid, sigma=1.0):
    s = np.where(valid, score, 0).astype(np.float32)
    ss = gaussian_filter(s, sigma=sigma)
    gy, gx = np.gradient(ss)
    hyy, hyx = np.gradient(gy)
    hxy, hxx = np.gradient(gx)
    hxy = 0.5 * (hxy + hyx)
    eigen = 0.5 * (hxx + hyy) - np.sqrt(0.25 * (hxx - hyy) ** 2 + hxy**2)
    vx, vy = hxy, eigen - hxx
    small = np.abs(vx) + np.abs(vy) < 1e-12
    vx, vy = np.where(small, 1.0, vx), np.where(small, 0.0, vy)
    direction = np.round(np.mod(np.degrees(np.arctan2(vy, vx)), 180) / 45).astype(int) % 4
    p = np.pad(ss, 1, mode="edge")
    h, w = ss.shape
    center = p[1 : 1 + h, 1 : 1 + w]
    keep = np.zeros(s.shape, dtype=bool)
    for q, (dy, dx) in enumerate([(0, 1), (1, 1), (1, 0), (1, -1)]):
        a = p[1 + dy : 1 + dy + h, 1 + dx : 1 + dx + w]
        b = p[1 - dy : 1 - dy + h, 1 - dx : 1 - dx + w]
        keep |= (direction == q) & (center >= a) & (center >= b) & ((center > a) | (center > b))
    return keep & (eigen < -1e-7) & valid & (s > 0)


def emit(score, domain, known=None, evidence=None, budget=0.025):
    if not 0 <= budget <= 1:
        raise ValueError("Budget must be in [0,1]")
    domain = np.asarray(domain, dtype=bool)
    if np.shape(score) != domain.shape:
        raise ValueError("Score/domain shape mismatch")
    eligible = domain.copy()
    if known is not None:
        eligible &= ~known
    if evidence is not None:
        eligible &= evidence
    eligible &= np.isfinite(score) & (score > 0)
    k = min(int(round(budget * domain.sum())), int(eligible.sum()))
    out = np.zeros(domain.shape, dtype=bool)
    if k == 0:
        return out
    ridge = ridge_nms(score, eligible)
    boosted = np.where(ridge, score + 1.0, score * 0.5)
    idx = np.flatnonzero(eligible)
    values = boosted.ravel()[idx]
    cutoff = np.partition(values, len(values) - k)[len(values) - k]
    higher = idx[values > cutoff]
    tied = idx[values == cutoff][: k - len(higher)]
    out.ravel()[np.r_[higher, tied]] = True
    return out

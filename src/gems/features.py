"""Label-free physical transforms. NO catalogue geometry or full-catalogue prediction input."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter


def axial_agreement(gy1, gx1, gy2, gx2):
    """Squared cosine: invariant to sign reversal; undefined zero-amplitude directions -> 0."""
    dot = gy1 * gy2 + gx1 * gx2
    energy = (gy1 * gy1 + gx1 * gx1) * (gy2 * gy2 + gx2 * gx2)
    out = np.zeros(np.shape(dot), dtype=np.float32)
    np.divide(dot * dot, energy, out=out, where=energy > 1e-20)
    return np.clip(out, 0, 1)


def supported_gradient(field, valid, sigma):
    """Normalized Gaussian smoothing with >=99% support, then gradient at 100m cells.

    Support additionally guards one gradient-neighbour pixel to avoid finite difference
    artifacts at missing-data boundaries. No extrapolated zero edge is evidence.
    """
    valid = np.asarray(valid, dtype=bool)
    support = gaussian_filter(valid.astype(np.float32), sigma, truncate=4)
    filtered = gaussian_filter(np.where(valid, field, 0).astype(np.float32), sigma, truncate=4)
    smooth = np.divide(filtered, support, out=np.zeros_like(filtered), where=support > 1e-8)
    gy, gx = np.gradient(smooth, 100.0)
    supported = support >= 0.99
    for axis in (0, 1):
        supported &= np.roll(support >= 0.99, 1, axis) & np.roll(support >= 0.99, -1, axis)
    supported[[0, -1], :] = False
    supported[:, [0, -1]] = False
    return gy.astype(np.float32), gx.astype(np.float32), supported


def coorientation(magnetic, gravity, valid):
    m1y, m1x, ok1 = supported_gradient(magnetic, valid, 1)
    g1y, g1x, okg1 = supported_gradient(gravity, valid, 1)
    m3y, m3x, ok3 = supported_gradient(magnetic, valid, 3)
    g3y, g3x, okg3 = supported_gradient(gravity, valid, 3)
    valid = valid & ok1 & okg1 & ok3 & okg3
    persistence = np.sqrt(axial_agreement(m1y, m1x, m3y, m3x) * axial_agreement(g1y, g1x, g3y, g3x))
    magnitudes = {
        "mag_gradient_100m": np.hypot(m1y, m1x),
        "grav_gradient_100m": np.hypot(g1y, g1x),
        "mag_gradient_300m": np.hypot(m3y, m3x),
        "grav_gradient_300m": np.hypot(g3y, g3x),
    }
    j1 = (
        axial_agreement(m1y, m1x, g1y, g1x)
        * persistence
        * np.sqrt(np.log1p(magnitudes["mag_gradient_100m"]) * np.log1p(magnitudes["grav_gradient_100m"]))
    )
    j3 = (
        axial_agreement(m3y, m3x, g3y, g3x)
        * persistence
        * np.sqrt(np.log1p(magnitudes["mag_gradient_300m"]) * np.log1p(magnitudes["grav_gradient_300m"]))
    )
    extra = {
        "joint_orientation_100m": j1,
        "joint_orientation_300m": j3,
        "joint_orientation_multiscale": np.sqrt(j1 * j3),
    }
    return (
        {k: np.where(valid, v, 0).astype(np.float32) for k, v in magnitudes.items()},
        {k: np.where(valid, v, 0).astype(np.float32) for k, v in extra.items()},
        valid,
    )


def local_residual(field, valid, size=15):
    support = uniform_filter(valid.astype(np.float32), size=size)
    total = uniform_filter(np.where(valid, field, 0).astype(np.float32), size=size)
    mean = np.divide(total, support, out=np.zeros_like(total), where=support > 0)
    return np.where(valid & (support >= 0.99), field - mean, 0).astype(np.float32)


def dequantize(q, spec):
    maximum, mode = spec
    u = np.clip((q.astype(np.float32) - 1) / 254, 0, 1)
    if mode not in ("sqrt", "linear"):
        raise ValueError(f"Unknown quantisation mode {mode}")
    return np.where(q > 0, (u * u if mode == "sqrt" else u) * maximum, 0).astype(np.float32)

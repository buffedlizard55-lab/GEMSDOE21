"""H21-5 label-free signed cross-normal step topology; registration 452c21c.

A physical-property contact is not necessarily a fault. These are testable signatures,
not a forward-model inversion, a geological label or calibrated fault probabilities.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates, minimum_filter


def step_strength(field, valid, sigma: float, chunk_rows=128):
    """Concentrated monotone profile × opposing curvature balance × gradient amplitude.

    Unit normals come from this field only. Complete profile/support checks are required;
    missing-data/array boundaries cannot create a step. Chunking limits coordinate RAM.
    """
    field = np.asarray(field, dtype=np.float32)
    valid = np.asarray(valid, dtype=bool)
    if field.ndim != 2 or field.shape != valid.shape or min(field.shape) < 5:
        raise ValueError("Need matched 2D field/valid arrays with dimensions >=5")
    if sigma not in (1, 3) or chunk_rows < 1:
        raise ValueError("Only preregistered sigma 1 or 3 and positive chunk rows are allowed")
    if not np.isfinite(field[valid]).all():
        raise ValueError("Field must be finite on its valid support")
    support = gaussian_filter(valid.astype(np.float32), sigma, truncate=4)
    smooth = gaussian_filter(np.where(valid, field, 0), sigma, truncate=4)
    np.divide(smooth, support, out=smooth, where=support > 1e-8)
    smooth[support <= 1e-8] = 0
    # Hessian finite differences need TWO neighbouring cells; no wrap-around support.
    safe = minimum_filter((support >= 0.99).astype(np.uint8), size=5, mode="constant", cval=0).astype(
        np.float32
    )
    del support
    gy, gx = np.gradient(smooth, 100.0)
    hyy, hyx = np.gradient(gy, 100.0)
    hxy, hxx = np.gradient(gx, 100.0)
    hxy += hyx
    hxy *= 0.5
    del hyx
    amplitude = np.hypot(gy, gx)
    ny = np.divide(gy, amplitude, out=np.zeros_like(gy), where=amplitude > 1e-12)
    nx = np.divide(gx, amplitude, out=np.zeros_like(gx), where=amplitude > 1e-12)
    del gy, gx
    out = np.zeros(field.shape, dtype=np.float32)
    eligible = np.zeros(field.shape, dtype=bool)
    width = field.shape[1]
    for begin in range(0, field.shape[0], chunk_rows):
        end = min(begin + chunk_rows, field.shape[0])
        sl = np.s_[begin:end, :]
        yy, xx = np.meshgrid(
            np.arange(begin, end, dtype=np.float32), np.arange(width, dtype=np.float32), indexing="ij"
        )
        uy, ux = ny[sl], nx[sl]
        okay = (safe[sl] > 0) & (amplitude[sl] > 1e-12)

        def sample(array, offset):
            coords = np.array([yy + offset * uy, xx + offset * ux])
            return map_coordinates(array, coords, order=1, mode="constant", cval=0, prefilter=False)

        points = {}
        for offset in (-3 * sigma, -sigma, 0, sigma, 3 * sigma):
            okay &= sample(safe, offset) >= 1 - 1e-6
            points[offset] = sample(smooth, offset)
        left = points[-sigma] - points[-3 * sigma]
        middle = points[sigma] - points[-sigma]
        right = points[3 * sigma] - points[sigma]
        # All intervals have length 2*sigma. Reject opposing increments and diffuse ramps.
        monotone = (middle * left >= 0) & (middle * right >= 0) & (np.abs(middle) > 1e-8)
        concentration = np.clip(
            (np.abs(middle) - np.maximum(np.abs(left), np.abs(right))) / (np.abs(middle) + 1e-12), 0, 1
        )
        curvature = []
        for offset in (-sigma, sigma):
            curvature.append(
                sample(hyy, offset) * uy * uy
                + 2 * sample(hxy, offset) * ux * uy
                + sample(hxx, offset) * ux * ux
            )
        cl, cr = curvature
        opposite = (cl * cr < 0) & (middle * cl > 0) & (middle * cr < 0)
        balance = 2 * np.minimum(np.abs(cl), np.abs(cr)) / (np.abs(cl) + np.abs(cr) + 1e-12)
        strength = np.log1p(amplitude[sl]) * concentration * balance
        eligible[sl] = okay
        out[sl] = np.where(okay & monotone & opposite, strength, 0)
    if not np.isfinite(out).all() or (out < 0).any():
        raise ValueError("Signed step transform emitted invalid strength")
    return out, eligible


def signed_step_features(field, valid, prefix):
    one, supported_one = step_strength(field, valid, 1)
    three, supported_three = step_strength(field, valid, 3)
    joint_support = supported_one & supported_three
    return {
        f"{prefix}_step100": one,
        f"{prefix}_step300": three,
        f"{prefix}_step_persistent": np.where(joint_support, np.sqrt(one * three), 0).astype(np.float32),
    }, joint_support

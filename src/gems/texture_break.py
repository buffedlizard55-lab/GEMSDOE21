"""H21-9 fixed magnetic texture-break prototype; SYNTHETIC-ONLY in Session 3.

The physical hypothesis is burial-depth contrast, not confirmed geothermal discharge.
Depositional/volcanic contacts, boulders and survey seams can produce the same pattern.
No catalogue, model fit, scorer or submission exporter is used by this module.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import convolve, gaussian_filter, map_coordinates


SUPPORT_MIN = 0.99


def _smooth(field, valid, sigma):
    support = gaussian_filter(valid.astype(np.float64), sigma, mode="constant", cval=0, truncate=4)
    total = gaussian_filter(np.where(valid, field, 0), sigma, mode="constant", cval=0, truncate=4)
    smooth = np.divide(total, support, out=np.zeros_like(total), where=support > 1e-12)
    return smooth, support >= SUPPORT_MIN


def _sample(array, valid, y, x):
    coordinates = np.array([y, x])
    value = map_coordinates(array, coordinates, order=1, mode="constant", cval=0, prefilter=False)
    support = map_coordinates(
        valid.astype(np.float64), coordinates, order=1, mode="constant", cval=0, prefilter=False
    )
    return value, support >= 1 - 1e-12


def _contrast(texture, valid, y, x, ny, nx, offset):
    left, lok = _sample(texture, valid, y - offset * ny, x - offset * nx)
    right, rok = _sample(texture, valid, y + offset * ny, x + offset * nx)
    total = left + right
    contrast = np.divide(right - left, total, out=np.zeros_like(total), where=total > 1e-12)
    return contrast, 0.5 * total, lok & rok


def texture_break(magnetic, valid):
    """One strength, signed contrast and support mask. Not a probability or a model.

    Fixed 1/3px Gaussian high pass, 5x5 RMS, ±2/±5px normal contrast and ±5px
    along-strike repeatability. Constant padding cannot reflect evidence into gaps.
    The caller must respect support; zeros outside it are missing, NOT negative labels.
    """
    raw = np.asarray(magnetic)
    mask = np.asarray(valid)
    if (
        raw.ndim != 2
        or min(raw.shape) < 2
        or mask.shape != raw.shape
        or raw.dtype.kind not in "fiu"
        or mask.dtype.kind != "b"
    ):
        raise ValueError("Need same-shaped 2D real numeric field and boolean support, both dimensions >=2")
    field = raw.astype(np.float64)
    mask = mask & np.isfinite(field) & (np.abs(field) < 1e20)
    # An arbitrary fixed valid datum removes cancellation under constant offsets.
    # It is not a fitted scaler, catalogue input or field-outcome threshold.
    datum = field.ravel()[np.flatnonzero(mask)[0]] if mask.any() else 0.0
    field = field - datum
    fine, ok1 = _smooth(field, mask, 1)
    coarse, ok3 = _smooth(field, mask, 3)
    hp_valid = mask & ok1 & ok3
    highpass = np.where(hp_valid, fine - coarse, 0)
    roundoff = 64 * np.finfo(np.float64).eps * (np.abs(fine) + np.abs(coarse))
    highpass = np.where(np.abs(highpass) <= roundoff, 0, highpass)
    # Direct local sums avoid a rolling accumulator carrying border cancellation
    # into a zero-energy interior (a synthetic ramp must not become a contact).
    box = np.full((5, 5), 1.0 / 25.0)
    rms_support = convolve(hp_valid.astype(np.float64), box, mode="constant", cval=0)
    energy = convolve(highpass * highpass, box, mode="constant", cval=0)
    texture = np.sqrt(
        np.maximum(np.divide(energy, rms_support, where=rms_support > 1e-12, out=np.zeros_like(energy)), 0)
    )
    rms_valid = hp_valid & (rms_support >= SUPPORT_MIN)
    smooth_texture, edge_valid = _smooth(texture, rms_valid, 1)
    gy, gx = np.gradient(smooth_texture)
    centre_valid = edge_valid & rms_valid
    for axis in (0, 1):
        centre_valid &= np.roll(edge_valid, 1, axis) & np.roll(edge_valid, -1, axis)
    centre_valid[[0, -1], :] = False
    centre_valid[:, [0, -1]] = False
    amplitude = np.hypot(gy, gx)
    direction = amplitude > 1e-12
    ny = np.divide(gy, amplitude, out=np.zeros_like(gy), where=direction)
    nx = np.divide(gx, amplitude, out=np.zeros_like(gx), where=direction)
    y, x = np.indices(field.shape, dtype=np.float64)
    near, mean_near, near_ok = _contrast(texture, rms_valid, y, x, ny, nx, 2)
    far, mean_far, far_ok = _contrast(texture, rms_valid, y, x, ny, nx, 5)
    consistent = near * far > 0
    central = np.minimum(np.abs(near), np.abs(far))
    flank_strengths = []
    support = centre_valid & direction & near_ok & far_ok
    for side in (-1, 1):
        fy, fx = y + side * 5 * nx, x - side * 5 * ny
        flank, _, flank_ok = _contrast(texture, rms_valid, fy, fx, ny, nx, 2)
        flank_strengths.append(np.where(flank * near > 0, np.abs(flank), 0))
        support &= flank_ok
    agreement = np.minimum(flank_strengths[0], flank_strengths[1])
    agreement = np.clip(
        np.divide(agreement, np.abs(near), out=np.zeros_like(near), where=np.abs(near) > 1e-12), 0, 1
    )
    strength = central * agreement * np.log1p(0.5 * (mean_near + mean_far))
    strength = np.where(support & consistent, strength, 0)
    contrast = np.where(support & consistent, near, 0)
    if not np.isfinite(strength).all() or not np.isfinite(contrast).all():
        raise ValueError("Nonfinite texture transform; do not replace it with evidence")
    return strength.astype(np.float32), contrast.astype(np.float32), support

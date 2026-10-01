"""Synthetic invariants only. Passing tests are NOT geological evidence or DTI gains."""

import numpy as np
import pytest

from gems.texture_break import texture_break


def toy():
    y, x = np.indices((161, 161))
    # Texture differs across a vertical boundary; no model/real fault labels.
    field = np.sin(2 * np.pi * y / 5) * np.where(x < 80, 1.0, 0.12)
    return field, np.ones(field.shape, bool)


def test_constant_and_linear_ramp_have_no_interior_strength():
    y, x = np.indices((101, 101))
    for field in (np.ones(x.shape), 2.0 * x + 3.0 * y):
        s, c, ok = texture_break(field, np.ones(x.shape, bool))
        assert not s[25:-25, 25:-25].any()
        assert not c[25:-25, 25:-25].any()
        assert not ok[0].any() and not ok[-1].any()


def test_uniform_roughness_is_not_a_texture_boundary():
    y, _ = np.indices((101, 101))
    s, _, _ = texture_break(np.sin(2 * np.pi * y / 5), np.ones(y.shape, bool))
    assert not s[25:-25, 25:-25].any()


def test_toy_texture_boundary_sign_offset_transpose_invariants():
    field, mask = toy()
    strength, contrast, ok = texture_break(field, mask)
    assert strength[40:120, 75:85].max() > 0.02
    assert strength[40:120, 20:40].max() == 0
    assert np.isfinite(strength).all() and (strength >= 0).all()
    assert (np.abs(contrast) <= 1).all()
    for changed in (-field, field + 300):
        other, _, other_ok = texture_break(changed, mask)
        assert np.allclose(strength, other, atol=2e-7)
        # Directions of zero-amplitude floating point noise cannot become evidence.
        assert np.allclose(strength[ok & other_ok], other[ok & other_ok], atol=2e-7)
    rotated, _, _ = texture_break(field.T, mask.T)
    assert np.allclose(strength, rotated.T, atol=2e-7)


def test_missing_or_sentinel_strip_is_not_a_contact():
    field, mask = toy()
    for missing in (np.nan, np.inf, -3.4028235e38):
        changed = field.copy()
        changed[:, 73:88] = missing
        s, _, ok = texture_break(changed, mask)
        assert not s[30:-30, 65:96].any()
        assert not ok[30:-30, 65:96].any()
    mask[:, 73:88] = False
    s, _, ok = texture_break(field, mask)
    assert not s[30:-30, 65:96].any() and not ok[30:-30, 65:96].any()


def test_all_missing_never_fills_with_reflected_evidence():
    s, c, ok = texture_break(np.ones((40, 40)), np.zeros((40, 40), bool))
    assert not s.any() and not c.any() and not ok.any()


@pytest.mark.parametrize(
    "field,mask",
    [
        (np.ones((1, 40)), np.ones((1, 40), bool)),
        (np.ones((4, 4)), np.ones((5, 5), bool)),
        (np.ones((4, 4), complex), np.ones((4, 4), bool)),
        (np.full((4, 4), "1"), np.ones((4, 4), bool)),
        (np.ones((4, 4)), np.ones((4, 4), int)),
    ],
)
def test_invalid_inputs_fail_closed(field, mask):
    with pytest.raises(ValueError):
        texture_break(field, mask)

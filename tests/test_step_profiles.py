import numpy as np
import pytest

from gems.step_profiles import signed_step_features, step_strength


def test_step_sign_reversal_and_axis_rotation_invariants():
    x = np.indices((81, 81))[1]
    field = (x >= 40).astype(np.float32) * 100
    valid = np.ones_like(field, dtype=bool)
    a, _ = step_strength(field, valid, 1)
    b, _ = step_strength(-field, valid, 1)
    c, _ = step_strength(field.T, valid.T, 1)
    assert a[40, 39:41].max() > 0
    assert np.allclose(a, b, atol=2e-7)
    assert np.allclose(a, c.T, atol=2e-7)
    extra, _ = signed_step_features(field, valid, "gravity")
    assert len(extra) == 3 and extra["gravity_step_persistent"][40, 39:41].max() > 0


def test_constant_and_linear_ramp_not_concentrated_steps():
    x = np.indices((81, 81))[1].astype(np.float32)
    for field in (np.ones_like(x), x):
        for sigma in (1, 3):
            strength, _ = step_strength(field, np.ones_like(field, bool), sigma)
            assert np.allclose(strength[15:-15, 15:-15], 0, atol=1e-8)


def test_missing_data_cannot_create_supported_step():
    x = np.indices((81, 81))[1]
    field = (x >= 40).astype(np.float32)
    valid = np.ones_like(field, dtype=bool)
    valid[:, 39:42] = False
    field[~valid] = np.nan
    extra, support = signed_step_features(field, valid, "magnetic")
    assert not support[40, 40]
    assert all(np.isfinite(a).all() and a[40, 40] == 0 for a in extra.values())


def test_constant_array_boundaries_never_create_step():
    a = np.ones((45, 50), dtype=np.float32) * 7
    strength, supported = step_strength(a, np.ones_like(a, bool), 3)
    assert not strength.any()
    assert not supported[0].any() and not supported[:, -1].any()


def test_chunking_does_not_change_the_transform():
    y, x = np.indices((75, 80))
    a = (x > 35 + 0.25 * y).astype(np.float32)
    valid = np.ones_like(a, dtype=bool)
    one, ok1 = step_strength(a, valid, 1, chunk_rows=8)
    two, ok2 = step_strength(a, valid, 1, chunk_rows=73)
    assert np.array_equal(one, two) and np.array_equal(ok1, ok2)


@pytest.mark.parametrize("sigma", [0, 2, np.nan])
def test_unregistered_scale_rejected(sigma):
    with pytest.raises(ValueError):
        step_strength(np.ones((20, 20)), np.ones((20, 20), bool), sigma)

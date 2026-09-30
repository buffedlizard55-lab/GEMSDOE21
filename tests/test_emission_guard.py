import numpy as np
import pytest

from gems.emission_guard import strict_emit
from gems.inference import emit, ridge_nms


def test_zero_physical_evidence_never_emits_prior_bias():
    domain = np.ones((48, 48), bool)
    score = np.full(domain.shape, 0.03)
    assert not strict_emit(score, domain, ~domain, np.zeros(domain.shape)).any()


def test_constant_score_is_not_a_structural_ridge():
    domain = np.ones((48, 48), bool)
    score = np.full(domain.shape, 0.03)
    strength = np.ones(domain.shape)
    assert not strict_emit(score, domain, ~domain, strength).any()
    # Explicitly expose the pre-result soft-NMS behavior; do not conceal the deviation.
    assert emit(score, domain, evidence=domain).any()


def test_strict_nms_never_pads_nonridge_cells_to_budget():
    domain = np.ones((48, 48), bool)
    y, x = np.indices(domain.shape)
    score = np.exp(-((x - 24) ** 2) / 2).astype(np.float32)
    strength = np.ones(domain.shape)
    known = np.zeros(domain.shape, bool)
    known[20:25, 24] = True
    out = strict_emit(score, domain, known, strength, budget=0.5)
    assert out.any() and not (out & known).any()
    eligible = domain & ~known & (strength > 0) & (score > 0)
    assert not (out & ~ridge_nms(score, eligible)).any()
    assert out.sum() < round(0.5 * domain.sum())


@pytest.mark.parametrize("bad", [np.nan, np.inf, -1])
def test_signal_strength_invalid_values_rejected(bad):
    domain = np.ones((16, 16), bool)
    strength = np.ones(domain.shape)
    strength[4, 4] = bad
    with pytest.raises(ValueError):
        strict_emit(np.ones(domain.shape), domain, ~domain, strength)

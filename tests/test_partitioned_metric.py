import numpy as np
import pytest

from gems.metric import dti
from gems.partitioned_metric import aggregate, partitions


def test_owned_block_totals_equal_whole_fold_metric():
    rng = np.random.default_rng(54)
    pred = rng.random((27, 25)) < 0.12
    truth = rng.random(pred.shape) < 0.08
    valid = rng.random(pred.shape) > 0.1
    known = rng.random(pred.shape) < 0.05
    owners = np.indices(pred.shape)[1] // 7
    part = partitions(pred, truth, valid, known, owners, n_parts=4)
    total = aggregate(part)
    expected = dti(pred, truth, valid, known)
    for key in ("TP_w", "FP_w", "FN_w", "alpha_FP", "beta_FN", "dti", "n_truth", "mass"):
        assert total[key] == pytest.approx(expected[key], abs=1e-9)


def test_cross_block_neighbour_credit_is_retained():
    p = np.zeros((12, 12), bool)
    g = p.copy()
    p[6, 5], g[6, 6] = True, True
    owners = (np.indices(p.shape)[1] >= 6).astype(int)
    parts = partitions(p, g, np.ones_like(p), np.zeros_like(p), owners, n_parts=2)
    assert parts[1]["TP_w"] == pytest.approx(2 / 3)
    assert parts[0]["FP_w"] == pytest.approx(1 / 3)
    assert aggregate(parts)["dti"] == pytest.approx(dti(p, g)["dti"])


def test_known_prediction_removed_before_cross_block_credit():
    p = np.zeros((12, 12), bool)
    g = p.copy()
    p[6, 5], g[6, 6] = True, True
    known = p.copy()
    owners = (np.indices(p.shape)[1] >= 6).astype(int)
    parts = partitions(p, g, np.ones_like(p), known, owners, n_parts=2)
    assert parts[1]["TP_w"] == 0 and parts[1]["FN_w"] == 1


def test_nonbinary_or_unowned_evaluation_rejected():
    p = np.ones((10, 10)) * 0.5
    with pytest.raises(ValueError):
        partitions(p, p, p > 0, p < 0, np.zeros_like(p, int))
    p[:] = 1
    with pytest.raises(ValueError):
        partitions(p, p, p > 0, p < 0, np.full_like(p, -1, int))

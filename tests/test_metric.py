import numpy as np
import pytest

from gems.metric import dti, offsets


def brute(p, g, domain, known):
    domain = domain & ~known
    p = np.where(domain, p, 0)
    gt = np.argwhere((g > 0) & domain)
    tp = 0.0
    for y, x in gt:
        tp += max(
            [
                p[y + dy, x + dx] * k
                for dy, dx, k in offsets()
                if 0 <= y + dy < p.shape[0] and 0 <= x + dx < p.shape[1]
            ]
            or [0]
        )
    fp = 0.0
    for y, x in np.argwhere(p > 0):
        k = max([max(0, 1 - np.hypot(y - gy, x - gx) / 3) for gy, gx in gt] or [0])
        fp += p[y, x] * (1 - k)
    fn = len(gt) - tp
    return tp, fp, fn


@pytest.mark.parametrize("binary", [True, False])
def test_exact_against_independent_brute(binary):
    rng = np.random.default_rng(17)
    for _ in range(20):
        p = (rng.random((11, 13)) > 0.8).astype(float) if binary else rng.random((11, 13))
        g = rng.random((11, 13)) > 0.93
        domain, known = rng.random(g.shape) > 0.1, rng.random(g.shape) > 0.9
        expected = brute(p, g, domain, known)
        result = dti(p, g, domain, known)
        assert [result[k] for k in ["TP_w", "FP_w", "FN_w"]] == pytest.approx(expected, abs=1e-6)


def test_masked_prediction_cannot_earn_recovery():
    p, g, known = np.zeros((9, 9)), np.zeros((9, 9)), np.zeros((9, 9), bool)
    p[4, 3] = 1
    known[4, 3] = True
    g[4, 4] = 1
    r = dti(p, g, known=known)
    assert r["TP_w"] == 0 and r["FP_w"] == 0 and r["FN_w"] == 1


def test_near_wrong_known_label_is_full_penalty():
    p, g, known = np.zeros((20, 20)), np.zeros((20, 20)), np.zeros((20, 20), bool)
    p[3, 4] = 1
    known[3, 3] = True
    g[15, 15] = 1
    r = dti(p, g, known=known)
    assert r["TP_w"] == 0 and r["FP_w"] == 1


def test_known_truth_does_not_create_credit_for_wrong_label():
    p, g, known = np.zeros((20, 20)), np.zeros((20, 20)), np.zeros((20, 20), bool)
    g[3, 3] = 1
    known[3, 3] = True
    g[15, 15] = 1
    p[3, 4] = 1
    assert dti(p, g, known=known)["FP_w"] == 1


def test_three_pixel_support_and_soft_max_not_sum():
    g = np.zeros((11, 11))
    g[5, 5] = 1
    p = np.zeros_like(g)
    p[5, 6] = 0.6
    p[5, 4] = 0.8
    assert dti(p, g)["TP_w"] == pytest.approx(0.8 * 2 / 3, abs=1e-7)
    p = np.zeros_like(g)
    p[5, 8] = 1
    assert dti(p, g)["TP_w"] == 0


@pytest.mark.parametrize("bad", [-1e-6, 1.00001, np.nan, np.inf, -3.4028235e38])
def test_invalid_prediction_rejected(bad):
    p = np.zeros((4, 4))
    p[1, 1] = bad
    with pytest.raises(ValueError):
        dti(p, np.ones((4, 4)))


def test_empty_truth_and_empty_prediction():
    assert dti(np.zeros((5, 5)), np.ones((5, 5)))["FN_w"] == 25
    assert dti(np.ones((5, 5)), np.zeros((5, 5)))["FP_w"] == 25
    assert dti(np.zeros((5, 5)), np.zeros((5, 5)))["dti"] == 0


def test_official_worked_example():
    value = 3 / (3 + 0.2 * 1.89 + 0.8 * 2)
    assert round(value, 2) == 0.60

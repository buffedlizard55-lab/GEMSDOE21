import numpy as np
import pytest
from scipy.optimize import check_grad

from gems.features import axial_agreement, coorientation
from gems.holdout import WholeSegmentHoldout, farther_than
from gems.inference import emit
from gems.pu import risk_and_grad, NNPULogistic
from gems.statistics import sign_flip, promotion


def test_whole_cross_boundary_segment_is_purged_everywhere():
    fp = np.ones((40, 40), bool)
    cat = np.zeros_like(fp)
    cat[10, 4:34] = True
    cat[30, 3:8] = True
    h = WholeSegmentHoldout(fp, cat, buffer_px=2)
    f = h.fold(0)
    assert f.hidden[10, 33] and not f.visible_catalogue[10, 33]
    assert not f.train_domain[11, 33]
    assert h.audit(f)["withheld_pixels_outside_quadrant"] > 0
    assert h.audit(f)["passes"]
    assert f.visible_catalogue[30, 3]
    assert not (f.hidden & f.visible_catalogue).any()


def test_buffers_are_euclidean_not_manhattan():
    mask = np.zeros((20, 20), bool)
    mask[10, 10] = True
    safe = farther_than(mask, 3)
    assert not safe[12, 12] and safe[13, 13]
    assert farther_than(np.zeros((5, 5), bool), 15).all()


def test_sparse_selection_uses_full_component_ids():
    fp = np.ones((50, 50), bool)
    cat = np.zeros_like(fp)
    for y in range(3, 21, 4):
        cat[y, 3:45] = True
    h = WholeSegmentHoldout(fp, cat, buffer_px=1)
    f = h.fold(0)
    ids = np.unique(h.components[f.sparse_truth])
    for cid in ids[ids > 0]:
        assert not (f.sparse_known & (h.components == cid)).any()
    assert np.array_equal(f.sparse_truth, h.fold(0).sparse_truth)


def test_nnpu_analytic_gradient_and_clamp():
    rng = np.random.default_rng(4)
    xp, xu = rng.normal(size=(20, 5)), rng.normal(size=(30, 5))
    for w in [np.zeros(5), np.array([2.0, -1.0, 0.1, 0.2, 0.5])]:
        err = check_grad(lambda v: risk_and_grad(v, xp, xu)[0], lambda v: risk_and_grad(v, xp, xu)[1], w)
        assert err < 1e-6
    # A nearly-saturated positive-only sample can make the uncorrected negative term negative.
    xp = np.array([[1.0, 20.0], [1.0, 21.0]])
    xu = np.array([[1.0, -20.0], [1.0, -21.0]])
    w = np.array([0.0, 1.0])
    assert check_grad(lambda v: risk_and_grad(v, xp, xu)[0], lambda v: risk_and_grad(v, xp, xu)[1], w) < 1e-6
    assert risk_and_grad(w, xp, xu)[0] >= 0


def test_pu_contains_no_confirmed_negative_targets():
    rng = np.random.default_rng(9)
    model = NNPULogistic().fit(rng.normal(1, 0.3, (40, 3)), rng.normal(0, 1, (300, 3)))
    assert model.fit_report["confirmed_negative_targets"] == 0
    p = model.predict(rng.normal(size=(10, 3)))
    assert np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all()
    with pytest.raises(ValueError):
        model.fit(np.empty((0, 3)), np.ones((2, 3)))


def test_axial_agreement_zero_and_orthogonal():
    a = np.ones((2, 2))
    z = np.zeros_like(a)
    assert np.all(axial_agreement(a, z, -a, z) == 1)
    assert np.all(axial_agreement(a, z, z, a) == 0)
    assert np.all(axial_agreement(z, z, z, z) == 0)


def test_parallel_step_signature_and_missing_data_support():
    x = np.indices((50, 50))[1]
    step = (x > 25).astype(np.float32)
    valid = np.ones_like(step, bool)
    _, joint, ok = coorientation(step, 2 * step, valid)
    assert joint["joint_orientation_multiscale"][25, 25] > 0
    valid[:, 21:30] = False
    _, joint, ok = coorientation(step, step, valid)
    assert not ok[25, 25] and joint["joint_orientation_multiscale"][25, 25] == 0


def test_zero_evidence_never_fills_budget():
    score = np.zeros((20, 20))
    domain = np.ones_like(score, bool)
    assert not emit(score, domain, budget=0.25).any()
    assert not emit(np.ones_like(score), domain, evidence=np.zeros_like(domain), budget=0.25).any()
    known = domain.copy()
    known[3, 3] = False
    out = emit(np.ones_like(score), domain, known, budget=0.25)
    assert out.sum() == 1 and out[3, 3]


def test_signflip_multiplicity_and_best_comparator_blocker():
    r = sign_flip(np.ones(16))
    assert r["p_one_sided"] == 1 / 65536 and r["p_bonferroni"] == 4 / 65536
    assert sign_flip(np.ones(4))["p_bonferroni"] == 0.25
    c = {"dense": [0.1] * 4, "sparse": [0.03] * 4, "recovery": 0.1}
    h = {"dense": [0.11] * 4, "sparse": [0.04] * 4, "recovery": 0.11}
    result = promotion(c, h, r, True)
    assert result["control_pass"] and not result["submission_eligible"]
    result = promotion(c, h, r, False, True)
    assert not result["submission_eligible"]

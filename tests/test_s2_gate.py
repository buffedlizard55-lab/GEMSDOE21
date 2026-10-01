import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

from gems.emission_guard import strict_emit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("evaluate_s2", ROOT / "scripts/evaluate_s2.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_even_perfect_exploratory_gain_cannot_enable_a_submission():
    c = {"dense": [0.1] * 4, "sparse": [0.03] * 4, "recovery": 0.1, "FP_w": 100}
    h = {"dense": [0.12] * 4, "sparse": [0.04] * 4, "recovery": 0.12, "FP_w": 90}
    r = module.gate(c, h, {"p_bonferroni": 0.001}, True)
    assert r["forecast_pass"] and r["exploratory_control_pass"]
    assert not r["fresh_confirmation"] and not r["current_best_reproducible"]
    assert not r["submission_eligible"]
    assert not module.gate(c, h, {"p_bonferroni": 0.001}, False)["exploratory_control_pass"]


@pytest.mark.parametrize("bad", [np.nan, np.inf, -0.1, 1.1])
def test_strict_emitter_rejects_invalid_scores_not_silent_filtering(bad):
    p = np.ones((30, 30)) * 0.2
    p[10, 10] = bad
    with pytest.raises(ValueError, match="Scores"):
        strict_emit(p, np.ones_like(p, bool), np.zeros_like(p, bool), np.ones_like(p))

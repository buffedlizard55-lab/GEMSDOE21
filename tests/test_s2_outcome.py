"""Post-outcome invariant/receipt tests; never any new candidate fit or score."""

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from gems.emission_guard import strict_emit
from gems.io import sha256
from gems.locks import verify_file

ROOT = Path(__file__).resolve().parents[1]


def test_literal_maximum_budget_rounds_down_not_up():
    domain = np.ones((5, 7), bool)
    _, x = np.indices(domain.shape)
    score = np.exp(-((x - 3) ** 2) / 2).astype(np.float32)
    # 35 * .025 = .875; old round produced one, exceeding the literal maximum.
    pred = strict_emit(score, domain, ~domain, np.ones(domain.shape))
    assert pred.sum() == 0


def test_h21_5_exact_recovered_asset_and_original_remain_locked():
    verify_file(ROOT, "evidence/h21-5-results.json")
    verify_file(ROOT, "evidence/h21-1-results.json")
    receipt = json.loads((ROOT / "evidence/h21-5-recovery-receipt.json").read_text())
    asset = next(x for x in receipt["assets"] if x["name"] == "h21-5-results.json")
    assert asset["digest"] == "sha256:" + sha256(ROOT / "evidence/h21-5-results.json")
    assert asset["size"] == (ROOT / "evidence/h21-5-results.json").stat().st_size


def test_h21_5_cannot_be_retested_or_overwritten():
    path = ROOT / "evidence/h21-5-results.json"
    before = path.read_bytes()
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_s2.py")], capture_output=True, text=True
    )
    assert out.returncode != 0 and "Refusing to overwrite or retest" in out.stderr
    assert path.read_bytes() == before


def test_knowledge_joins_and_first_outcome_summation_consistency():
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_knowledge import check

    assert check()["passed"]

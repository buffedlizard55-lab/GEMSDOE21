"""Read-only consistency check for claim/source/provenance joins, not universal fact certification."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256  # noqa: E402
from gems.locks import verify_file, verify_prompt  # noqa: E402
from gems.metric import ALPHA, BETA, RADIUS  # noqa: E402


def load(path):
    return json.loads((ROOT / path).read_text())


def check():
    sources = load("registry/sources.json")["sources"]
    ids = {s["id"] for s in sources}
    assert len(ids) == len(sources)
    claims = load("registry/knowledge-s2.json")["claims"] + load("registry/knowledge-s3.json")["claims"]
    assert len({c["id"] for c in claims}) == len(claims)
    for row in claims:
        assert row["kind"] and row["claim"] and row["boundary"]
        assert set(row["source_ids"]) <= ids and row["source_ids"]
        if row["evidence"]:
            assert (ROOT / row["evidence"]).is_file(), row["evidence"]
    verify_prompt(ROOT / "README.md")
    for name in (
        "research/preregistration-h21.md",
        "research/preregistration-h21-s2.md",
        "evidence/h21-1-results.json",
        "evidence/data-verification.json",
    ):
        verify_file(ROOT, name)
    assert ALPHA == 0.2 and BETA == 0.8 and RADIUS == 3
    registration = load("registry/hypotheses-s2.json")
    assert registration["registration_sha256"] == sha256(ROOT / registration["registration"])
    assert registration["cumulative_correction_family_size"] == 8
    assert len(registration["candidates"]) == 4
    assert registration["candidates"][0]["expected_dense_delta"] == 0.006
    baseline = load("evidence/baseline-recovery-s2.json")
    assert (
        not baseline["reproducible_H19_current_best"]
        and not baseline["main_and_original_PR_python_differences"]
    )
    probe = load("evidence/h21-s2-input-only-probe.json")
    assert probe["model_fits"] == 0 and probe["scores_observed"] == 0
    expected_discarded = {
        "/features/" + s + "/sha256"
        for s in ("joint_orientation_100m", "joint_orientation_300m", "joint_orientation_multiscale")
    }
    assert {d["path"] for d in probe["manifest_differences"]} == expected_discarded
    first = load("evidence/data-verification.json")
    assert len(first["base_columns"]) == 31
    for name in first["base_columns"]:
        assert probe["feature_descriptions"][name]["sha256"] == first["features"][name]["sha256"]
    receipt = load("evidence/official-inputs-s2.json")
    vector = receipt["sources"]["fault_vectors"]
    assert probe["actual_official_zip_sha256"] == vector["sha256"]
    primary = load("evidence/submission-validation.json")
    assert primary["byte_identical_to_h19_4"] and not primary["new_submission_recommended"]
    assert np.isclose(0.1894 - 0.1855, 0.0039)
    outcome = ROOT / "evidence/h21-5-results.json"
    if outcome.exists():
        result = json.loads(outcome.read_text())
        assert result["official_vector_sha256"] == vector["sha256"]
        assert result["base_feature_sha256"] == {
            n: first["features"][n]["sha256"] for n in first["base_columns"]
        }
        assert result["family_size"] == 8 and result["confirmed_negative_targets"] == 0
        assert not result["gate"]["submission_eligible"] and not result["gate"]["fresh_confirmation"]
        assert result["metric"] == {
            "alpha": 0.2,
            "beta": 0.8,
            "radius_pixels": 3,
            "known_mask": "pixel-exact before all distances and terms",
        }
        for key in ("TP_w", "FP_w", "FN_w", "alpha_FP", "beta_FN"):
            for name in ("C21-S2-PU", "H21-5"):
                total = sum(f["models"][name]["dense"][key] for f in result["folds"])
                assert np.isclose(total, result["summary"][name][key]), key
    verify_file(ROOT, "research/preregistration-h21-s3.md")
    s3 = load("registry/hypotheses-s3.json")
    assert s3["registration_sha256"] == sha256(ROOT / s3["registration"])
    assert s3["cumulative_planned_correction_family_size"] == 12
    assert len(s3["candidates"]) == 4 and s3["historical_scored_attempts"] == 2
    assert s3["candidates"][0]["expected_dense_delta"] == 0.005
    assert all(c["observed_dense_delta"] is None and not c["submission_eligible"] for c in s3["candidates"])
    assert all(set(c["source_ids"]) <= ids for c in s3["candidates"])
    readiness = load("evidence/research-readiness-s3.json")
    assert readiness["dimensions"]["phase"] == "INPUT_ONLY"
    assert not readiness["dimensions"]["field_fit_permission"]["authorized"]
    assert not readiness["dimensions"]["new_submission_eligibility"]["eligible"]
    assert not readiness["dimensions"]["competition_acceptance"]["verified"]
    assert readiness["cumulative_planned_family_size"] == 12
    for key in (
        "field_maps_computed_s3",
        "field_model_fits_s3",
        "geological_scores_observed_s3",
        "weekly_slots_spent_s3",
    ):
        assert readiness[key] == 0
    for path, digest in readiness["input_evidence_bindings"].items():
        assert sha256(ROOT / path) == digest, path
    print(
        f"Knowledge consistency passed: {len(claims)} typed claims, {len(sources)} sources; no universal/hidden-score certification"
    )
    return {"claims": len(claims), "sources": len(sources), "passed": True}


if __name__ == "__main__":
    check()

import copy
from pathlib import Path
import sys

import pytest

from gems.readiness import assess_s3_readiness, authorize_s3_activity

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_readiness_inputs_s3 import vector_schema  # noqa: E402


def test_forged_ready_booleans_or_scores_cannot_unlock_s3_field_fit():
    receipt = {"ready": True, "field_fit_allowed": True, "dense_gain": 1.0, "sources": {}}
    baseline = {"clean_current_best_refittable": True}
    delivery = {"files": [], "byte_identical_to_h19_4": False}
    result = assess_s3_readiness(copy.deepcopy(receipt), baseline, delivery)
    assert result["phase"] == "INPUT_ONLY"
    assert not result["field_fit_permission"]["authorized"]
    assert not result["scientific_readiness"]["ready"]
    assert not result["new_submission_eligibility"]["eligible"]
    assert not result["competition_acceptance"]["verified"]


@pytest.mark.parametrize("activity", ["field-fit", "geological-score", "new-submission", "upload", ""])
def test_field_activities_fail_closed(activity):
    with pytest.raises(PermissionError, match="INPUT/PROTOTYPE ONLY"):
        authorize_s3_activity(activity, ROOT)


@pytest.mark.parametrize("activity", ["source-metadata", "synthetic-prototype", "historical-delivery"])
def test_only_registered_nonfield_activities_allowed(activity):
    assert authorize_s3_activity(activity, ROOT)["authorized"]


def test_source_with_missing_archive_or_schema_is_not_verified():
    result = assess_s3_readiness({"sources": {"missing": {}}}, {}, {"files": []})
    assert not result["input_transport"]["missing"]["full_bytes_with_sha_recorded"]
    assert not result["input_transport"]["missing"]["crc_and_member_safety_checked"]
    assert not result["input_transport"]["missing"]["numeric_or_vector_schema_recorded"]
    assert not result["historical_delivery"]["locally_format_verified"]


def test_empty_official_layer_does_not_invent_bounds(monkeypatch):
    class Empty:
        crs = "EPSG:4269"
        schema = {"geometry": "LineString", "properties": {"NUM": "str"}}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def __len__(self):
            return 0

        @property
        def bounds(self):
            raise AssertionError("No extent for an empty table")

    monkeypatch.setattr("fetch_readiness_inputs_s3.fiona.listlayers", lambda _: ["empty"])
    monkeypatch.setattr("fetch_readiness_inputs_s3.fiona.open", lambda *args, **kwargs: Empty())
    records = vector_schema(Path("metadata-only.shp"), reserve=True)
    assert records[0]["features"] == 0 and records[0]["bounds"] is None
    assert "features_with_envelope_intersecting_reserved_box" not in records[0]


@pytest.mark.parametrize("script", ["check_s3_prototype.py", "build_readiness_s3.py"])
def test_new_commands_reject_field_data_or_fit_options(script):
    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--fit", "field.tif"], capture_output=True, text=True
    )
    assert result.returncode == 2 and "unrecognized arguments" in result.stderr
    assert not result.stdout


def test_s3_registration_is_committed_before_new_implementation():
    import hashlib
    import subprocess

    registration = "689160f54af40f8b5a65dc660da5e9b64465a1f0"
    implementation = "bcbdee358913f825b9eabd286be5dda21936529f"
    content = subprocess.check_output(
        ["git", "show", registration + ":research/preregistration-h21-s3.md"], cwd=ROOT
    )
    assert (
        hashlib.sha256(content).hexdigest()
        == "7353bfbdabe48637bdd549722cbefaa70da1bb5ca62f4c1ee80332c23e9145a8"
    )
    assert (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", registration, implementation], cwd=ROOT
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "cat-file", "-e", registration + ":src/gems/texture_break.py"],
            cwd=ROOT,
            capture_output=True,
        ).returncode
        != 0
    )
    assert (
        subprocess.run(
            ["git", "cat-file", "-e", implementation + ":src/gems/texture_break.py"], cwd=ROOT
        ).returncode
        == 0
    )

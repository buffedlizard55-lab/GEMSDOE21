"""Build bound, fail-closed S3 readiness evidence. No model evaluation or scientific TIFF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256, utc_now, write_json  # noqa: E402
from gems.locks import verify_file, verify_prompt  # noqa: E402
from gems.readiness import assess_s3_readiness, authorize_s3_activity  # noqa: E402
from gems.submission import validate_bundle  # noqa: E402


def load(path):
    return json.loads((ROOT / path).read_text())


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()  # metadata only; never accept fit/score flags
    authorize_s3_activity("historical-delivery", ROOT)
    verify_prompt(ROOT / "README.md")
    for file in ("evidence/h21-1-results.json", "evidence/h21-5-results.json"):
        verify_file(ROOT, file)
    binding = load("evidence/input-recovery-s3.json")
    source_path = ROOT / "evidence/official-inputs-s3.json"
    if sha256(source_path) != binding["decoded_receipt_sha256"]:
        raise ValueError("Official input receipt differs from recovered content hash")
    source = load("evidence/official-inputs-s3.json")
    if source["registration_sha256"] != sha256(ROOT / "research/preregistration-h21-s3.md"):
        raise ValueError("Input receipt does not bind the locked S3 registration")
    for key in (
        "field_model_fits",
        "geological_scores_observed",
        "drivendata_requests",
        "competition_uploads",
    ):
        if source.get(key) != 0:
            raise ValueError("Source collection exceeds authorized input-only scope")
    if binding.get("official_archive_assets_matched") is not True:
        raise ValueError("Public full-byte source assets not bound to recovered source hashes")
    prototype = load("evidence/prototype-s3.json")
    if not prototype.get("passed") or prototype["prototype_sha256"] != sha256(
        ROOT / "src/gems/texture_break.py"
    ):
        raise ValueError("Synthetic prototype receipt is stale/failed")
    baseline = load("evidence/baseline-history-s3.json")
    delivery = load("evidence/submission-validation.json")
    manifest = load("docs/data/submissions.json")
    if (
        delivery != manifest
        or delivery.get("source_sha256") != "89109a3bd2cd3b12e7a0f388113c519843acfc9c4f46825affefc3e63dd99b22"
    ):
        raise ValueError("Historical delivery identity changed")
    for file in manifest["files"]:
        # CLI hashes refer to container; contained TIFF gets an independent full preflight.
        path = ROOT / "docs" / file["href"]
        if (
            sha256(path) != file["sha256"]
            or not validate_bundle(path, ROOT / "docs/data/template-mask.tif")["passed"]
        ):
            raise ValueError("Actual local delivery bytes/grid/range failed")
    report = {
        "kind": "S3-research-readiness-NOT-a-scientific-result",
        "generated_utc": utc_now(),
        "registration": "research/preregistration-h21-s3.md",
        "registration_sha256": sha256(ROOT / "research/preregistration-h21-s3.md"),
        "registration_commit": "689160f54af40f8b5a65dc660da5e9b64465a1f0",
        "cumulative_planned_family_size": 12,
        "historical_scored_attempts": 2,
        "field_maps_computed_s3": 0,
        "field_model_fits_s3": 0,
        "geological_scores_observed_s3": 0,
        "new_scientific_tiffs_s3": 0,
        "weekly_slots_spent_s3": 0,
        "dimensions": assess_s3_readiness(source, baseline, delivery),
        "reserved_box_wgs84": source["reserved_box_wgs84"],
        "reserved_box_outside_competition_rectangle": source["reserved_box_outside_competition_rectangle"],
        "label_outcomes_viewed_in_reserved_box": False,
        "input_evidence_bindings": {
            path: sha256(ROOT / path)
            for path in (
                "evidence/official-inputs-s3.json",
                "evidence/input-recovery-s3.json",
                "evidence/baseline-history-s3.json",
                "evidence/prototype-s3.json",
                "evidence/submission-validation.json",
                "docs/data/template-mask.tif",
            )
        },
        "count_scope": "New S3 candidate field maps/fits/geological DTI only; historical delivery byte/pixel audits and identical overview rendering are excluded",
        "scope": "Transport/schema/coverage, synthetic invariants and historical byte-format delivery. No fresh geological evidence, new DTI gain, prize promise or competition acceptance.",
    }
    write_json(ROOT / "evidence/research-readiness-s3.json", report)
    print("S3 readiness: inputs audited; scientific readiness, field fit and new submission remain BLOCKED")


if __name__ == "__main__":
    main()

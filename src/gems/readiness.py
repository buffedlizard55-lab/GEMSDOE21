"""S3 fail-closed phase policy: successful input acquisition is NOT permission to fit.

This is an auditable workflow guard, not a security boundary against arbitrary Python.
There is no S3 field evaluator/exporter. Future scientific permission requires a new
separately reviewed and locked prospective fit/split/control protocol, not edited flags.
"""

from __future__ import annotations

ALLOWED_S3_ACTIVITIES = frozenset({"source-metadata", "synthetic-prototype", "historical-delivery"})


def authorize_s3_activity(activity, root):
    from .locks import verify_file

    verify_file(root, "research/preregistration-h21-s3.md")
    if activity not in ALLOWED_S3_ACTIVITIES:
        raise PermissionError(
            "S3 is INPUT/PROTOTYPE ONLY; field fits, scores, new TIFFs and uploads are not authorized"
        )
    return {"phase": "INPUT_ONLY", "activity": activity, "authorized": True}


def assess_s3_readiness(receipt, baseline, delivery):
    """Keep five independent dimensions. No caller boolean/score can unlock field fits."""
    transport = {}
    for name, source in receipt.get("sources", {}).items():
        archive = source.get("archive", {})
        file = source.get("transport", {})
        transport[name] = {
            "status": source.get("status", "MISSING"),
            "full_bytes_with_sha_recorded": bool(
                file.get("bytes", 0) > 0 and len(file.get("sha256", "")) == 64
            ),
            "crc_and_member_safety_checked": archive.get("crc_verified") is True,
            "numeric_or_vector_schema_recorded": bool(source.get("rasters") or source.get("schemas")),
        }
    blockers = {
        "original_H19_arm_producer_and_clean_same_split_refit": baseline.get("clean_current_best_refittable")
        is not True,
        "complete_compatible_external_predictors": True,
        "separately_locked_prospective_fit_split_control_protocol": True,
        "unobserved_whole_system_label_provenance_and_cross_domain_links": True,
        "native_acquisition_texture_resolution_and_raster_units": True,
    }
    return {
        "phase": "INPUT_ONLY",
        "input_transport": transport,
        "scientific_readiness": {
            "ready": False,
            "blocking_requirements": [name for name, failed in blockers.items() if failed],
            "caveat": "40/100m output cells and new publication dates do not establish effective resolution or fresh labels",
        },
        "field_fit_permission": {
            "authorized": False,
            "reason": "Immutable S3 registration permits input and synthetic prototype only; no S3 field scorer/exporter exists",
        },
        "new_submission_eligibility": {
            "eligible": False,
            "reason": "No new geological outcome, corrected promotion result, clean current-best win or fresh confirmation",
        },
        "historical_delivery": {
            "locally_format_verified": delivery.get("byte_identical_to_h19_4") is True
            and {f.get("role") for f in delivery.get("files", [])}
            == {"primary", "zip", "masked-zero fallback"}
            and len(delivery.get("files", [])) == 3
            and all(
                f.get("preflight", {}).get("passed", False)
                for f in delivery.get("files", [])
                if f["role"] != "zip"
            ),
            "new_scientific_model": False,
            "new_submission_recommended": False,
            "note": delivery.get("note"),
        },
        "competition_acceptance": {
            "verified": False,
            "status": "UNTESTED ON COMPETITION PLATFORM",
            "scope": "Local or live-site format/byte checks are not a platform acceptance/score receipt",
        },
    }

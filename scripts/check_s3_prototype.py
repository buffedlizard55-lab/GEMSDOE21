"""Run only deterministic synthetic H21-9 invariants. NOT a geological test/forecast win."""

import argparse
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256, utc_now, write_json  # noqa: E402
from gems.readiness import authorize_s3_activity  # noqa: E402
from gems.texture_break import texture_break  # noqa: E402


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()  # no field-data/fit/score options
    policy = authorize_s3_activity("synthetic-prototype", ROOT)
    y, x = np.indices((161, 161))
    mask = np.ones(y.shape, bool)
    toy = np.sin(2 * np.pi * y / 5) * np.where(x < 80, 1.0, 0.12)
    strength, _, _ = texture_break(toy, mask)
    offset, _, _ = texture_break(toy + 300, mask)
    reversed_sign, _, _ = texture_break(-toy, mask)
    transposed, _, _ = texture_break(toy.T, mask.T)
    constant, _, _ = texture_break(np.ones(y.shape), mask)
    ramp, _, _ = texture_break(2.0 * x + 3.0 * y, mask)
    uniform, _, _ = texture_break(np.sin(2 * np.pi * y / 5), mask)
    missing = toy.copy()
    missing[:, 73:88] = np.nan
    gap, _, support = texture_break(missing, mask)
    checks = {
        "constant_interior_zero": not constant[25:-25, 25:-25].any(),
        "linear_ramp_interior_zero": not ramp[25:-25, 25:-25].any(),
        "uniform_roughness_interior_zero": not uniform[25:-25, 25:-25].any(),
        "toy_side_contrast_detected": strength[40:120, 75:85].max() > 0.02,
        "offset_invariant": np.allclose(strength, offset, atol=2e-7),
        "sign_invariant": np.allclose(strength, reversed_sign, atol=2e-7),
        "transpose_invariant": np.allclose(strength, transposed.T, atol=2e-7),
        "missing_strip_not_a_contact": not gap[30:-30, 65:96].any() and not support[30:-30, 65:96].any(),
        "all_outputs_finite": np.isfinite(strength).all(),
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    report = {
        "generated_utc": utc_now(),
        "kind": "S3-H21-9-SYNTHETIC-ONLY",
        "phase_policy": policy,
        "registration_sha256": sha256(ROOT / "research/preregistration-h21-s3.md"),
        "prototype_sha256": sha256(ROOT / "src/gems/texture_break.py"),
        "checks": {k: bool(v) for k, v in checks.items()},
        "passed": True,
        "field_maps_computed": 0,
        "field_model_fits": 0,
        "geological_scores_observed": 0,
        "new_submission_tiffs": 0,
        "scope": "Numerical/support invariants only. Strength is neither a calibrated probability nor evidence of faults, hydrothermal flow or a DTI gain.",
        "initial_synthetic_failures_retained_in_notes": "research/implementation-notes-s3.md",
    }
    write_json(ROOT / "evidence/prototype-s3.json", report)
    print("H21-9 synthetic invariants passed; 0 field maps/fits/geological scores; no promotion")


if __name__ == "__main__":
    main()

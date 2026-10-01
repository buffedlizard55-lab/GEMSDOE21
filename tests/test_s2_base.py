"""A platform-only discarded H21-1 byte difference must never unlock a consumed input."""

import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_prepared import preparation_semantics, UNUSED_H21_1_COLUMNS  # noqa: E402


def test_s2_ignores_only_three_discarded_hashes_but_legacy_guard_is_strict():
    first = json.loads((ROOT / "evidence/data-verification.json").read_text())
    changed = copy.deepcopy(first)
    for name in UNUSED_H21_1_COLUMNS:
        changed["features"][name]["sha256"] = "0" * 64
    assert preparation_semantics(first) != preparation_semantics(changed)
    assert preparation_semantics(first, True) == preparation_semantics(changed, True)
    assert len(first["base_columns"]) == 31
    assert not set(first["base_columns"]) & set(UNUSED_H21_1_COLUMNS)


def test_s2_used_hashes_source_metadata_support_and_shape_remain_strict():
    first = json.loads((ROOT / "evidence/data-verification.json").read_text())
    for column in first["base_columns"]:
        changed = copy.deepcopy(first)
        changed["features"][column]["sha256"] = "0" * 64
        assert preparation_semantics(first, True) != preparation_semantics(changed, True)
    for key, value in (
        ("physical_supported_pixels", 0),
        ("model_inputs_catalogue_derived", True),
        ("known_pixels", 0),
    ):
        changed = copy.deepcopy(first)
        changed[key] = value
        assert preparation_semantics(first, True) != preparation_semantics(changed, True)
    changed = copy.deepcopy(first)
    changed["features"][UNUSED_H21_1_COLUMNS[0]]["shape"] = [1]
    assert preparation_semantics(first, True) != preparation_semantics(changed, True)

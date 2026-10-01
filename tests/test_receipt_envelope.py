import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_readiness_receipt import decode, encode  # noqa: E402


def test_lossless_deterministic_json_envelope_round_trip():
    content = json.dumps({"scope": "input only", "schemas": ["repeated layer metadata"] * 10000}).encode()
    envelope = encode(content)
    assert decode(envelope) == content and encode(content) == envelope


def test_receipt_tampering_and_truncation_fail_closed():
    envelope = encode(b'{"model_fits":0}')
    for changed in (
        dict(envelope, sha256="0" * 64),
        dict(envelope, uncompressed_bytes=10),
        dict(envelope, payload=envelope["payload"][:-4]),
        dict(envelope, uncompressed_bytes=4_000_001),
    ):
        with pytest.raises(ValueError):
            decode(changed)


def test_empty_or_oversized_receipts_not_silently_truncated():
    for content in (b"", b"x" * 4_000_001):
        with pytest.raises(ValueError):
            encode(content)

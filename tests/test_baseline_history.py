import hashlib
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_baseline_history as audit  # noqa: E402


def test_literal_search_never_confuses_reader_with_writer():
    text = 'a = np.load("oof_probs_h19_arms.npz")\nnp.savez("oof_probs_h19_arms.npz", x=x)'
    hits = audit.scan_text(text, "script.py", "a" * 40)
    assert [h["kind"] for h in hits] == ["literal reader", "possible literal writer"]
    assert (
        audit.scan_text("H19_1_PowerLaw_TipStepover", "evidence.json", "a" * 40)[0]["kind"]
        == "arm-symbol mention"
    )


def test_git_object_hash_includes_header():
    content = b"reproducible source"
    assert audit.git_blob_sha(content) == hashlib.sha1(b"blob 19\0" + content).hexdigest()


def test_inventory_pages_all_rows_and_rejects_incomplete_total(monkeypatch):
    def api(route):
        if route.endswith("&page=1"):
            return {"total_count": 101, "items": list(range(100))}
        return {"total_count": 101, "items": [100]}

    monkeypatch.setattr(audit, "api", api)
    assert audit.pages("inventory", "items") == list(range(101))
    monkeypatch.setattr(audit, "api", lambda _: {"total_count": 3, "items": [1]})
    with pytest.raises(ValueError, match="incomplete"):
        audit.pages("inventory", "items")

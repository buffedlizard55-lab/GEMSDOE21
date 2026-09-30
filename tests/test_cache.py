import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from download_data import fetch  # noqa: E402


def test_unverified_metadata_cache_always_refetched_at_pin(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMS_DATA_DIR", str(tmp_path))
    dest = tmp_path / "metadata.json"
    dest.write_bytes(b"wrong-old-version")
    calls = []

    def run(cmd, stdout, stderr, timeout):
        calls.append(cmd)
        stdout.write(b'{"pinned":true}')
        return subprocess.CompletedProcess(cmd, 0, stderr=b"")

    monkeypatch.setattr(subprocess, "run", run)
    result = fetch(("owner/repo", "immutable-commit"), "metadata.json", dest)
    assert dest.read_bytes() == b'{"pinned":true}' and len(calls) == 1
    assert "immutable-commit" in calls[0][2] and result["status"] == "fetched-verified"


def test_hash_pinned_large_cache_reused_only_on_expected_digest(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMS_DATA_DIR", str(tmp_path))
    dest = tmp_path / "large.tif"
    dest.write_bytes(b"known-pinned-bytes")
    want = hashlib.sha256(dest.read_bytes()).hexdigest()

    def forbidden(*args, **kwargs):
        raise AssertionError("Matching pinned cache should not refetch")

    monkeypatch.setattr(subprocess, "run", forbidden)
    assert fetch(("owner/repo", "commit"), "large.tif", dest, want)["status"] == "cached-verified"

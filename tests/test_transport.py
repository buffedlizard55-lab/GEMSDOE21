import hashlib
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from download_data import G19, fetch  # noqa: E402
from publish_s2_execution import redact  # noqa: E402


def test_public_raw_fallback_has_exact_pin_no_credentials_and_same_hash(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMS_DATA_DIR", str(tmp_path))
    content = b"exact pinned bytes"
    want = hashlib.sha256(content).hexdigest()
    calls = []

    def failed_gh(cmd, stdout, stderr, timeout):
        stdout.write(b"not the intended bytes")
        return subprocess.CompletedProcess(cmd, 1, stderr=b"API route failure")

    class Response:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def raise_for_status(self):
            pass

        def iter_content(self, size):
            yield content

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(subprocess, "run", failed_gh)
    monkeypatch.setattr("requests.get", get)
    path = tmp_path / "input.bin"
    result = fetch(G19, "public-input.bin", path, want)
    assert path.read_bytes() == content and result["sha256"] == want
    assert G19[1] in calls[0][0] and "/main/" not in calls[0][0]
    assert not calls[0][1]["allow_redirects"] and "headers" not in calls[0][1]


def test_fallback_hash_mismatch_never_installs_a_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMS_DATA_DIR", str(tmp_path))
    monkeypatch.setattr("time.sleep", lambda _: None)

    def failed_gh(cmd, stdout, stderr, timeout):
        return subprocess.CompletedProcess(cmd, 1, stderr=b"fail")

    class Response:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def raise_for_status(self):
            pass

        def iter_content(self, size):
            yield b"wrong data"

    monkeypatch.setattr(subprocess, "run", failed_gh)
    monkeypatch.setattr("requests.get", lambda *a, **k: Response())
    path = tmp_path / "input.bin"
    with pytest.raises(RuntimeError):
        fetch(G19, "public-input.bin", path, "0" * 64)
    assert not path.exists() and not path.with_name("input.bin.partial").exists()


def test_execution_receipt_redacts_signed_queries_and_tokens():
    text = "failed https://example.gov/x?sig=secret&jwt=secret ghp_sensitive01234 github_pat_sensitive01234"
    clean = redact(text)
    assert "secret" not in clean and "sensitive" not in clean
    assert "https://example.gov/x" in clean

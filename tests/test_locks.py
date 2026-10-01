from pathlib import Path
import subprocess

import pytest

from gems.locks import LOCKED_FILES, verify_file, verify_prompt

ROOT = Path(__file__).resolve().parents[1]


def test_content_locks_do_not_need_git_history(tmp_path):
    # A source archive / shallow export has no .git, but protection is still mandatory.
    for name in LOCKED_FILES:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / name).read_bytes())
        assert verify_file(tmp_path, name) == (ROOT / name).read_bytes()
    p = tmp_path / "README.md"
    p.write_text((ROOT / "README.md").read_text())
    assert verify_prompt(p)


def test_changed_research_or_prompt_fails_closed(tmp_path):
    p = tmp_path / "research/preregistration-h21-s2.md"
    p.parent.mkdir()
    p.write_text("modified registration")
    with pytest.raises(ValueError, match="Immutable"):
        verify_file(tmp_path, "research/preregistration-h21-s2.md")
    p = tmp_path / "README.md"
    p.write_text("```text\nmodified brief\n```")
    with pytest.raises(ValueError, match="prompt changed"):
        verify_prompt(p)


def test_new_registration_is_already_committed_before_results():
    probe = subprocess.run(["git", "cat-file", "-e", "452c21c^{commit}"], cwd=ROOT, capture_output=True)
    if probe.returncode:
        pytest.skip("Historical commit unavailable; independent immutable content locks still run")
    content = subprocess.check_output(["git", "show", "452c21c:research/preregistration-h21-s2.md"], cwd=ROOT)
    assert content == verify_file(ROOT, "research/preregistration-h21-s2.md")

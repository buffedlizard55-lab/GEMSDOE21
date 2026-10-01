"""Preserve hosted setup/runtime diagnostics when archive/log endpoints are inaccessible.

A pre-score infrastructure failure is not a geological negative result. Query strings
and token-like material are redacted before publication. Never changes a first outcome.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256, utc_now, write_json  # noqa: E402


def redact(text):
    text = re.sub(r"(https?://[^\s?\"'<>]+)\?[^\s\"'<>]+", r"\1?<redacted-query>", text)
    return re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b", "<redacted-token>", text)


def main():
    log = ROOT / ".cache/s2-setup.log"
    result = ROOT / "evidence/h21-5-results.json"
    report = {
        "generated_utc": utc_now(),
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "code_commit": os.environ.get("GITHUB_SHA"),
        "job_status": os.environ.get("S2_JOB_STATUS"),
        "scientific_result_present": result.exists(),
        "first_result_sha256": sha256(result) if result.exists() else None,
        "setup_tail_redacted": redact(log.read_text(errors="replace")[-16000:])
        if log.exists()
        else "No setup log; inspect Actions job steps",
        "scope": "Infrastructure diagnostic, not a score or an additional hypothesis test",
        "drivendata_requests": 0,
    }
    path = ROOT / ".cache/s2-execution-status.json"
    write_json(path, report)
    repo = os.environ["GITHUB_REPOSITORY"]
    tag = "h21-5-execution-status"
    exists = (
        subprocess.run(["gh", "release", "view", tag, "--repo", repo], capture_output=True).returncode == 0
    )
    command = [
        "gh",
        "release",
        "edit" if exists else "create",
        tag,
        "--repo",
        repo,
        "--notes-file",
        str(path),
    ]
    if not exists:
        command += [
            "--target",
            os.environ["GITHUB_SHA"],
            "--prerelease",
            "--title",
            "H21-5 hosted setup/runtime status — not a geological result",
        ]
    subprocess.run(command, check=True)
    print("Preserved redacted setup status without changing any scientific outcome")


if __name__ == "__main__":
    main()

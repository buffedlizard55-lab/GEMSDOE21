import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_delivery_only_never_calls_any_prepare_fit_inference_or_score(monkeypatch):
    spec = importlib.util.spec_from_file_location("delivery_runner", ROOT / "scripts/run_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []

    def run(command, **kwargs):
        calls.append(Path(command[1]).name)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--delivery-only"])
    module.main()
    assert calls == [
        "download_data.py",
        "audit_upstream.py",
        "audit_group.py",
        "build_submissions.py",
        "check_knowledge.py",
        "build_site.py",
        "check_site.py",
    ]
    assert not any("prepare" in s or "evaluate" in s for s in calls)


def test_delivery_only_cannot_be_misused_for_a_replication():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_pipeline.py"), "--delivery-only", "--replicate"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 2 and "cannot request a scientific replication" in out.stderr

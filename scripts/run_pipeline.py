"""Autonomous pinned data → preparation → locked CPU experiment → audited reference → site.

Rejected hypotheses stay research-only. --replicate repeats the SAME registered parameters,
writing an ignored timestamped report, never replacing the first outcome or selecting variants.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replicate",
        action="store_true",
        help="Repeat fixed experiment into ignored data/research/; no tuning",
    )
    parser.add_argument(
        "--refresh-sources", action="store_true", help="Refresh permitted health probes, not leaderboard"
    )
    parser.add_argument(
        "--delivery-only",
        action="store_true",
        help="Rebuild historical audited delivery/site without preparing, fitting or scoring any model",
    )
    args = parser.parse_args()
    if args.delivery_only and args.replicate:
        parser.error("--delivery-only cannot request a scientific replication")
    env = dict(os.environ, OPENBLAS_NUM_THREADS="2", OMP_NUM_THREADS="2")

    def run(script, *extra):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), *map(str, extra)], cwd=ROOT, env=env, check=True
        )

    run("download_data.py")
    if not args.delivery_only:
        if not (data_dir() / "prepared/manifest.json").exists():
            run("prepare_data.py")
        run("verify_prepared.py")
        if not (ROOT / "evidence/h21-1-results.json").exists():
            run("evaluate.py")
        elif args.replicate:
            out = (
                data_dir() / f"research/H21-1-replication-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.json"
            )
            run("evaluate.py", "--replication-output", out)
        else:
            print(
                "Preserving/using first registered result; --replicate performs the fixed train/inference/validation again.",
                flush=True,
            )
    else:
        print(
            "Delivery-only: no feature preparation, training, inference, replication or new score", flush=True
        )
    run("audit_upstream.py")
    run("audit_group.py")
    run("build_submissions.py")
    if (ROOT / "research/preregistration-h21-s3.md").exists():
        # Delivery never reruns even the toy transform. Read its preserved bound receipt.
        run("build_readiness_s3.py")  # source bindings, byte/format checks and blocked scientific gates
    if args.refresh_sources or not (ROOT / "docs/data/source-health.json").exists():
        run("refresh_sources.py")
    run("check_knowledge.py")
    run("build_site.py")
    run("check_site.py")
    print(
        "Pipeline complete. First outcomes preserved; published historical reference is NOT a new scientific submission.",
        flush=True,
    )


if __name__ == "__main__":
    main()

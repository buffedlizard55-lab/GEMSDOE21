"""Audit the obtainable current H19 source, original PR head and artifact inventory.

This does NOT evaluate pretrained maps against their training labels, invent a generator,
assume private artifacts do not exist, or claim that code weights caused a hidden score.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256, utc_now, write_json  # noqa: E402

REPO = "buffedlizard55-lab/19GEMSDOE"
MAIN_PIN = "a3aca62fdb2be428f4245e22570cbc54082b2c15"
PR_HEAD = "1a8624961dc4de630ab239321832611fcb3fbd71"


def api(route):
    return json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/{route}"], text=True))


def main():
    head = api("commits/main")["sha"]
    main_tree, pr_tree = api(f"git/trees/{MAIN_PIN}?recursive=1"), api(f"git/trees/{PR_HEAD}?recursive=1")
    if main_tree.get("truncated") or pr_tree.get("truncated"):
        raise ValueError("Cannot claim complete Python inspection on a truncated GitHub tree")

    def python_files(tree):
        return {
            x["path"]: x["sha"] for x in tree["tree"] if x["type"] == "blob" and x["path"].endswith(".py")
        }

    paths, original_paths = python_files(main_tree), python_files(pr_tree)
    differences = sorted(p for p in set(paths) | set(original_paths) if paths.get(p) != original_paths.get(p))
    cache = ROOT / ".cache/audit/19GEMSDOE"
    hashes, hits = {}, []
    for path in paths:
        p = cache / path
        # Re-read immutable GitHub contents, never trust a mutable local source cache.
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(
            subprocess.check_output(
                [
                    "gh",
                    "api",
                    f"repos/{REPO}/contents/{path}?ref={MAIN_PIN}",
                    "-H",
                    "Accept: application/vnd.github.raw",
                ]
            )
        )
        text = p.read_text()
        ast.parse(text)  # Valid Python is required for a source audit, not execution.
        hashes[path] = sha256(p)
        for n, line in enumerate(text.splitlines(), 1):
            if "oof_probs_h19_arms" in line:
                hits.append(
                    {
                        "file": path,
                        "line": n,
                        "excerpt": line.strip(),
                        "url": f"https://github.com/{REPO}/blob/{MAIN_PIN}/{path}#L{n}",
                    }
                )
    artifacts = api("actions/artifacts?per_page=100")
    if artifacts["total_count"] > 100:
        raise ValueError("Artifact inventory needs pagination before claiming coverage")
    report = {
        "generated_utc": utc_now(),
        "repository": REPO,
        "current_main": head,
        "pinned_main": MAIN_PIN,
        "original_PR_head": PR_HEAD,
        "current_main_equals_audited_pin": head == MAIN_PIN,
        "main_and_original_PR_python_differences": differences,
        "python_files_inspected": len(paths),
        "source_sha256": hashes,
        "cache_filename_references": hits,
        "tracked_cache_present": any("oof_probs_h19_arms" in t["path"] for t in main_tree["tree"]),
        "listed_actions_artifacts": [
            {k: a[k] for k in ("id", "name", "expired", "size_in_bytes")} for a in artifacts["artifacts"]
        ],
        "reproducible_H19_current_best": False,
        "disposition": "BLOCKED: obtainable source has the cache reader, not its original generator",
        "scope": "Audited pinned public Python, original PR-head comparison and listed artifacts only; private/untracked/expired data may exist but are not available here",
        "score_causality": "UNIDENTIFIED; source mechanics and changed pixels do not prove which change caused .1894",
        "code_novelty_anchors": [
            {
                "candidate": "H21-5",
                "prior": "H19 compute_strike_worm_feature integrates magnitude along/flanking lines; H21-1 axial_agreement compares field directions; neither computes the new signed normal-curvature step contract",
                "paths": ["scripts/run_spatial_holdout_and_build.py", "src/gems/hypotheses.py"],
                "claim_scope": "relative to inspected source, not worldwide or private-group novelty",
            },
            {
                "candidate": "H21-6",
                "prior": "H19 k_th_anom is a local ratio residual; proposed directional cross-scarp compositional jumps remain unimplemented",
            },
            {
                "candidate": "H21-7",
                "prior": "H19 clay-conduit/demagnetization features use local amplitude products, not the proposed signed edge sidedness",
            },
            {
                "candidate": "H21-8",
                "prior": "H19 uses seismic_ieq_log and strain summary rasters, not ComCat uncertainty/depth/time-plane geometry",
            },
        ],
    }
    write_json(ROOT / "evidence/baseline-recovery-s2.json", report)
    print(
        f"Inspected {len(paths)} Python files; {len(hits)} cache readers; clean H19 comparator remains BLOCKED"
    )


if __name__ == "__main__":
    main()

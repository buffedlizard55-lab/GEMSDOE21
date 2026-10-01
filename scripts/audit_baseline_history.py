"""Read-only, full reachable-history H19 producer search. No model execution or scoring.

GitHub indexes and content-addressed blobs are accessed via gh. Static searches cannot
prove that private/untracked/dynamically named generators do not exist. A serialized
full-catalogue prediction, a cache or an upstream score is not a clean refittable model.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import utc_now, write_json  # noqa: E402

REPOSITORY = "buffedlizard55-lab/19GEMSDOE"
TEXT_SUFFIXES = {".py", ".sh", ".yml", ".yaml", ".js", ".mjs", ".md", ".json", ".toml", ".txt"}
CACHE_NAME = "oof_probs_h19_arms"
ARM_RE = re.compile(r"H19_[123]_(?:PowerLaw|Backward|Openness)")
WRITE_RE = re.compile(r"savez|save\(|write\(|tofile|dump\(|open\([^\n]*[\"'](?:w|a)")


def api(route):
    return json.loads(
        subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/{route}"], text=True, timeout=90)
    )


def pages(route, key=None):
    """Do not silently treat the first 100 rows as a complete inventory."""
    result = []
    for page in range(1, 101):
        sep = "&" if "?" in route else "?"
        body = api(f"{route}{sep}per_page=100&page={page}")
        rows = body[key] if key else body
        if not isinstance(rows, list):
            raise ValueError("Expected a paginated list")
        result.extend(rows)
        if len(rows) < 100:
            if key and "total_count" in body and len(result) != body["total_count"]:
                raise ValueError("Inventory changed or pagination is incomplete")
            return result
    raise ValueError("Pagination cap reached; no complete-coverage claim permitted")


def git_blob_sha(content):
    return hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()


def scan_text(text, path, commit):
    """Literal and arm-symbol evidence, not a semantic proof of generator absence."""
    hits = []
    for line, excerpt in enumerate(text.splitlines(), 1):
        literal, arm = CACHE_NAME in excerpt, bool(ARM_RE.search(excerpt))
        if literal or arm:
            is_code = Path(path).suffix in {".py", ".sh", ".yml", ".yaml", ".js", ".mjs"}
            kind = (
                "possible literal writer"
                if literal and is_code and WRITE_RE.search(excerpt)
                else "literal reader"
                if literal and is_code and ("load(" in excerpt or "np.load" in excerpt)
                else "literal mention"
                if literal
                else "arm-symbol mention"
            )
            hits.append(
                {
                    "path": path,
                    "commit": commit,
                    "line": line,
                    "kind": kind,
                    "excerpt": excerpt.strip()[:1000],
                    "url": f"https://github.com/{REPOSITORY}/blob/{commit}/{path}#L{line}",
                }
            )
    return hits


def audit():
    branches = pages("branches")
    commits = {}
    for branch in branches:
        for commit in pages(f"commits?sha={quote(branch['commit']['sha'], safe='')}"):
            commits[commit["sha"]] = commit
    missing_parents = sorted({p["sha"] for c in commits.values() for p in c["parents"]} - set(commits))
    if missing_parents:
        raise ValueError("Reachable-history inventory lacks parents; cannot claim full coverage")
    inventory, blob_refs, tracked_caches = {}, {}, []
    for commit in sorted(commits):
        tree = api(f"git/trees/{commit}?recursive=1")
        if tree.get("truncated"):
            raise ValueError("Truncated tree; producer recovery audit must stop")
        entries = [e for e in tree["tree"] if e["type"] == "blob"]
        inventory[commit] = {
            "message": commits[commit]["commit"]["message"].splitlines()[0],
            "parents": [p["sha"] for p in commits[commit]["parents"]],
            "tracked_files": len(entries),
            "inspected_text_paths": [],
        }
        for entry in entries:
            path = entry["path"]
            if CACHE_NAME in path:
                tracked_caches.append({"commit": commit, "path": path, "git_blob_sha": entry["sha"]})
            if Path(path).suffix in TEXT_SUFFIXES or path in {".gitignore", "AGENTS.md"}:
                if entry.get("mode") not in {"100644", "100755"}:
                    raise ValueError(f"Unsupported text mode: {path}")
                if entry.get("size", 0) > 4_000_000:
                    raise ValueError(f"Text blob exceeds audit cap: {path}")
                inventory[commit]["inspected_text_paths"].append(path)
                blob_refs.setdefault(entry["sha"], []).append((commit, path))
    blobs, findings = [], []
    for sha, refs in sorted(blob_refs.items()):
        raw = api(f"git/blobs/{sha}")
        if raw["encoding"] != "base64" or raw["size"] > 4_000_000:
            raise ValueError("Unexpected blob encoding/size")
        content = base64.b64decode(raw["content"], validate=False)
        if len(content) != raw["size"] or git_blob_sha(content) != sha:
            raise ValueError("Git blob content-address mismatch")
        text = content.decode("utf-8")
        refs = sorted(refs)
        blobs.append(
            {
                "git_blob_sha": sha,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "references": [{"commit": c, "path": p} for c, p in refs],
            }
        )
        for commit, path in refs:
            findings.extend(scan_text(text, path, commit))
    pulls = pages("pulls?state=all")
    pr_records = []
    for pr in pulls:
        comments = pages(f"issues/{pr['number']}/comments")
        reviews = pages(f"pulls/{pr['number']}/comments")
        bodies = [pr.get("body") or ""] + [c.get("body") or "" for c in comments + reviews]
        pr_records.append(
            {
                "number": pr["number"],
                "url": pr["html_url"],
                "head": pr["head"]["sha"],
                "body_sha256": hashlib.sha256(bodies[0].encode()).hexdigest(),
                "public_comment_count": len(comments),
                "public_review_comment_count": len(reviews),
                "cache_literal_mentions": sum(CACHE_NAME in body for body in bodies),
                "limit": "PR descriptions are claims, not an original trainer or execution receipt",
            }
        )
    releases = pages("releases")
    artifacts = pages("actions/artifacts", "artifacts")
    writer_hits = [h for h in findings if h["kind"] == "possible literal writer"]
    return {
        "generated_utc": utc_now(),
        "repository": REPOSITORY,
        "branches": [{"name": b["name"], "sha": b["commit"]["sha"]} for b in branches],
        "reachable_commit_count": len(commits),
        "history_inventory": inventory,
        "all_reachable_parents_present": not missing_parents,
        "unique_text_blobs_inspected": len(blobs),
        "text_blob_hashes": blobs,
        "tracked_target_cache": tracked_caches,
        "source_findings": findings,
        "literal_writer_hits": writer_hits,
        "pull_request_inventory": pr_records,
        "release_inventory": [
            {
                "tag": r["tag_name"],
                "url": r["html_url"],
                "assets": [{k: a.get(k) for k in ("name", "size", "digest")} for a in r["assets"]],
            }
            for r in releases
        ],
        "artifact_inventory": [
            {k: a.get(k) for k in ("id", "name", "size_in_bytes", "expired")} for a in artifacts
        ],
        "original_producer_recovered": False,
        "clean_current_best_refittable": False,
        "status": "REQUIRES REVIEW" if writer_hits or tracked_caches else "BLOCKED",
        "blockers": [
            "No audited original H19 arm producer with reproducible execution lineage is recovered",
            "Legacy negative targets/full-catalogue collar and sparse scoring assumptions are not the clean protocol",
            "No independently refitted same-split current-best comparator exists",
        ],
        "scope": "All public-branch-reachable recognized .py/.sh/.yml/.yaml/.js/.mjs/.md/.json/.toml/.txt and .gitignore blobs, plus paginated PR/comments/releases/artifact indexes at this dated read; literal/arm-symbol static search, NOT a proof no dynamically named, other-extension, private, untracked or expired generator exists",
        "field_model_fits": 0,
        "geological_scores_observed": 0,
        "causal_hidden_score_attribution": "UNIDENTIFIED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/baseline-history-s3.json")
    args = parser.parse_args()
    report = audit()
    write_json(args.output, report)
    print(
        f"Inspected {report['reachable_commit_count']} reachable commits / "
        f"{report['unique_text_blobs_inspected']} text blobs; clean H19 refit {report['status']}"
    )


if __name__ == "__main__":
    main()

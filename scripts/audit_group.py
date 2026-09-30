"""Verify inherited historical artifact identities; no scores are queried or recomputed.

The user's reported scores remain reported. Hash/pixel equality is independently checked.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from download_data import fetch, G19, H19_NAME  # noqa: E402


def api(endpoint):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def main():
    prior = data_dir() / "audit/19GEMSDOE/registry/submissions.json"
    fetch(G19, "registry/submissions.json", prior)
    entries = json.loads(prior.read_text())["entries"]
    # Prompt corrections/additions, NOT newly observed public/private score receipts.
    for e in entries:
        if e["id"] == "GEMSDOE10-H25":
            e["lb_score"] = 0.1280
        e["score_provenance"] = "USER-REPORTED; not an independently authenticated file-score receipt"
        e["artifact_association"] = "Pinned upstream registry attribution; source file bytes checked here"
    trees = {}
    heads = {}

    def tree(repo):
        if repo not in trees:
            heads[repo] = api(f"repos/buffedlizard55-lab/{repo}/commits/main")["sha"]
            obj = api(f"repos/buffedlizard55-lab/{repo}/git/trees/{heads[repo]}?recursive=1")
            if obj.get("truncated"):
                raise ValueError("Truncated Git tree cannot establish completeness")
            trees[repo] = {x["path"]: x for x in obj["tree"] if x["type"] == "blob"}
        return trees[repo]

    def add(id, repo, token, score, site, label):
        matches = [
            (p, v) for p, v in tree(repo).items() if token in p and p.endswith(".tif") and "download" in p
        ]
        nan_matches = [(p, v) for p, v in matches if p.endswith("-nan.tif")]
        if len(nan_matches) == 1:
            matches = nan_matches
        if len(matches) != 1:
            entries.append(
                {
                    "id": id,
                    "github_repo": repo,
                    "label": label,
                    "lb_score": score,
                    "site_url": site,
                    "status": "artifact unresolved",
                    "matching_artifacts": [p for p, v in matches],
                }
            )
            return
        path, blob = matches[0]
        entries.append(
            {
                "id": id,
                "github_repo": repo,
                "label": label,
                "lb_score": score,
                "site_url": site,
                "repo_path": path,
                "git_blob_sha1": blob["sha"],
                "bytes": blob["size"],
                "score_provenance": "USER-REPORTED / not authenticated",
            }
        )

    add(
        "17GEMSDOE-F",
        "17GEMSDOE",
        "F-ensemble-2pct",
        0.0187,
        "https://buffedlizard55-lab.github.io/17GEMSDOE/",
        "F ensemble 2%",
    )
    add(
        "18GEMSDOE",
        "18GEMSDOE",
        "",
        0.0297,
        "https://buffedlizard55-lab.github.io/18GEMSDOE/",
        "Unknown exact file: prompt gives project score only",
    )
    add(
        "19GEMSDOE-H19-4",
        "19GEMSDOE",
        H19_NAME,
        0.1894,
        "https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html",
        "H19-4 corroborated blend",
    )
    add(
        "19GEMSDOE-H19-5",
        "19GEMSDOE",
        "gems19-h19-5",
        None,
        "https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html",
        "H19-5 budget variant (no reported score)",
    )
    add(
        "16GEMSDOE-H18-3a",
        "16GEMSDOE",
        "h18-3a",
        None,
        "https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html",
        "H18-3a complexity prior",
    )
    add(
        "16GEMSDOE-H18-4",
        "16GEMSDOE",
        "h18-4",
        None,
        "https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html",
        "H18-4 mapped faults (not a PU holdout)",
    )
    with rasterio.open(data_dir() / "sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1)) & (s.read_masks(1) > 0)
        grid = (s.shape, s.crs, s.transform)
    with rasterio.open(data_dir() / "labels.tif") as s:
        known = (s.read(1) > 0) & footprint
    domain = footprint & ~known
    verified = []
    for e in entries:
        if not e.get("git_blob_sha1"):
            continue
        repo, blob = e["github_repo"], e["git_blob_sha1"]
        path = data_dir() / f"audit/group/{repo}/{blob}.tif"
        try:
            if not path.exists():
                obj = api(f"repos/buffedlizard55-lab/{repo}/git/blobs/{blob}")
                if obj.get("encoding") != "base64":
                    raise ValueError("Unknown Git blob encoding")
                raw = base64.b64decode(obj["content"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            raw = path.read_bytes()
            digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
            if digest != blob:
                raise ValueError("Git blob content identity failed")
            current = tree(repo).get(e["repo_path"], {})
            e["snapshot_head"] = heads[repo]
            e["file_link"] = (
                f"https://github.com/buffedlizard55-lab/{repo}/blob/{heads[repo]}/{e['repo_path']}"
            )
            e["current_path_matches_inherited_blob"] = current.get("sha") == blob
            with rasterio.open(path) as s:
                p = s.read(1)
                matches = (s.shape, s.crs, s.transform) == grid
                e["byte_identity_verified"] = True
                e["sha256"] = sha256(path)
                e["grid_matches"] = matches
                if matches:
                    vals = p[footprint]
                    inside_valid = bool(np.isfinite(vals).all() and ((vals >= 0) & (vals <= 1)).all())
                    e["footprint_range_verified"] = inside_valid
                    e["scored_positive_pixels_gt_05"] = int((p[domain] > 0.5).sum())
                    e["known_pixel_positives_gt_05"] = int((p[known] > 0.5).sum())
                    e["binary_scored_id"] = hashlib.sha256(
                        (p[domain] > 0.5).astype(np.uint8).tobytes()
                    ).hexdigest()[:8]
                    if inside_valid:
                        # Exact scored confidence equality, NOT only binary-mask similarity.
                        e["soft_scored_sha256"] = hashlib.sha256(
                            np.asarray(p[domain], dtype="<f4").tobytes()
                        ).hexdigest()
            verified.append(e["id"])
        except (subprocess.CalledProcessError, ValueError, OSError, rasterio.errors.RasterioError) as err:
            e["verification_error"] = str(err)[:250]
        print(
            f"{e['id']}: {e.get('binary_scored_id', 'not verified')}; score={e.get('lb_score')}", flush=True
        )
    for n in range(20, 28):
        entries.append(
            {
                "id": f"GEMSDOE{n}",
                "github_repo": "20GEMSDOE" if n == 20 else "GEMSDOE21" if n == 21 else None,
                "label": "H19 historical reference (not novel)" if n == 21 else "No score reported",
                "lb_score": None,
                "score_provenance": "PROMPT BLANK, not zero",
                "status": "no new competition result",
            }
        )
    groups = {}
    for e in entries:
        if e.get("soft_scored_sha256"):
            groups.setdefault(e["soft_scored_sha256"], []).append(e["id"])
    duplicates = [ids for ids in groups.values() if len(ids) > 1]
    report = {
        "generated_utc": utc_now(),
        "scores_source": "Full user prompt stored verbatim in README; no automated DrivenData calls",
        "inherited_file_map_source": f"{G19[0]}@{G19[1]}:registry/submissions.json",
        "entries": entries,
        "verified_artifact_ids": verified,
        "exact_soft_scored_duplicates": duplicates,
        "warning": "No inference of causal mechanism from historical live scores; no full-catalogue file was evaluated as OOF. Artifact-name associations without receipts remain provisional.",
    }
    write_json(ROOT / "registry/group-results.json", report)
    print("Exact scored-field duplicate groups:", duplicates)


if __name__ == "__main__":
    main()

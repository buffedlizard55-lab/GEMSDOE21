"""Verify OUR live Pages content/downloads; no competition website is contacted."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256  # noqa: E402
from validate_submission import check  # noqa: E402

BASE = "https://buffedlizard55-lab.github.io/GEMSDOE21/"


def fetch(url, dest, expected):
    # Redirects cannot turn an owned-site health check into DrivenData monitoring/SSRF.
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "buffedlizard55-lab.github.io"
        or not parsed.path.startswith("/GEMSDOE21/")
    ):
        raise ValueError("Only our owned project Pages origin is permitted")
    with requests.get(
        url,
        timeout=(8, 30),
        allow_redirects=False,
        stream=True,
        headers={"Cache-Control": "no-cache", "User-Agent": "GEMSDOE21-owned-live-download-check"},
    ) as response:
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError("Live verification requires a direct HTTP 200, not redirects")
        dest.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        digest = hashlib.sha256()
        with dest.open("wb") as out:
            for chunk in response.iter_content(1 << 16):
                n += len(chunk)
                if n > expected.stat().st_size:
                    raise ValueError("Live file exceeds expected byte length")
                out.write(chunk)
                digest.update(chunk)
        actual = digest.hexdigest()
        if n != expected.stat().st_size or actual != sha256(expected):
            raise ValueError(f"Served content mismatch: {url}")
        return {
            "url": url,
            "http_status": 200,
            "bytes": n,
            "sha256": actual,
            "expected_bytes_equal": True,
            "content_type": response.headers.get("content-type"),
        }


def main():
    out = ROOT / ".cache/live-artifacts"
    docs = ROOT / "docs"
    manifest = json.loads((docs / "data/submissions.json").read_text())
    routes = {"": ROOT / "index.html"}
    for path in [
        "index.html",
        "executive-summary.html",
        "research.html",
        "sources.html",
        "readiness.html",
        "assets/site.css",
        "assets/site.js",
        "data/submissions.json",
        "data/template-mask.tif",
        "data/h21-5-results.json",
        "data/h21-5-protocol-review.json",
        "data/hypotheses-s2.json",
        "data/knowledge-s2.json",
        "data/sources.json",
        "data/hypotheses-s3.json",
        "data/knowledge-s3.json",
        "data/research-readiness-s3.json",
        "data/official-inputs-s3.json",
        "data/input-recovery-s3.json",
        "data/prototype-s3.json",
        "data/baseline-history-s3.json",
        "data/preregistration-h21-s3.md",
        "data/implementation-notes-s3.md",
        "data/request-audit-s3.md",
    ]:
        routes["docs/" + path] = docs / path
    for spec in manifest["files"]:
        routes["docs/" + spec["href"]] = docs / spec["href"]
    records = []
    for path, expected in routes.items():
        dest = out / (path or "root-index.html")
        record = fetch(urljoin(BASE, path), dest, expected)
        records.append(record)
        print(f"Verified served bytes: {path or '/'}", flush=True)
    for spec in manifest["files"]:
        dest = out / "docs" / spec["href"]
        result = check(dest, out / "docs/data/template-mask.tif", spec["sha256"])
        if not result["passed"]:
            raise ValueError("Actual live download failed numeric/grid/container preflight")
        records.append({"file": spec["name"], "live_preflight": result})
    report = {
        "kind": "owned-pages-live-download-verification",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "passed": True,
        "site": BASE,
        "records": records,
        "main_commit_at_check": os.environ.get("LIVE_MAIN_COMMIT"),
        "verification_code_commit": os.environ.get("GITHUB_SHA"),
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "drivendata_requests": 0,
        "platform_submission": False,
        "score_verified": False,
        "scope": "Our actually served Pages content, hashes and downloaded GeoTIFF/ZIP format. NOT competition acceptance or score.",
    }
    Path("live-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print("LIVE Pages + three full-byte downloads/format checks: PASSED")


if __name__ == "__main__":
    main()

"""Refresh permitted public-data/GitHub health, NEVER DrivenData or an upload.

These transport probes do not validate geology, data licensing or footprint coverage.
The scheduled workflow publishes the JSON as a fixed GitHub release's body; no bot pushes main.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
PERMITTED_EXACT = {
    "docs.nlr.gov",
    "gdr.openei.org",
    "hydro.nationalmap.gov",
    "mrdata.usgs.gov",
    "www.usgs.gov",
    "www.osti.gov",
    "prd-tnm.s3.amazonaws.com",
    "www.sciencebase.gov",
    "sciencebase.gov",
    "doi.org",
    "ngmdb.usgs.gov",
    "downloadsb.usgs.gov",
    "data.usgs.gov",
    "earthquake.usgs.gov",
}


def permitted(url):
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname in PERMITTED_EXACT
        and not parsed.username
        and not parsed.password
        and parsed.port in (None, 443)
    )


def probe(source):
    url = source["monitor_url"]
    base = {
        "id": source["id"],
        "title": source["title"],
        "url": url,
        "scope": "transport/metadata health only; NOT usable-data or geological validation",
    }
    try:
        with requests.Session() as session:
            session.headers["User-Agent"] = (
                "GEMSDOE21-public-source-audit (+https://github.com/buffedlizard55-lab/GEMSDOE21)"
            )
            for _ in range(7):
                if not permitted(url):
                    raise ValueError("Non-permitted host/URL blocked BEFORE requesting it")
                response = session.get(
                    url,
                    headers={"Range": "bytes=0-65535"},
                    timeout=(6, 12),
                    allow_redirects=False,
                    stream=True,
                )
                if response.status_code in (301, 302, 303, 307, 308):
                    next_url = urljoin(url, response.headers.get("Location", ""))
                    response.close()
                    if next_url == url:
                        raise ValueError("Redirect loop")
                    url = next_url
                    continue
                with response:
                    head = b""
                    for chunk in response.iter_content(4096):
                        head += chunk
                        if len(head) >= 65536:
                            head = head[:65536]
                            break
                    text = head.decode("utf-8", errors="replace").lower()
                    is_error_page = any(
                        s in text for s in ("<title>404", "<title>page not found", "<title>access denied")
                    )
                    is_pdf = head.startswith(b"%PDF-")
                    is_zip = head.startswith(b"PK\x03\x04")
                    is_tif = head[:4] in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+")
                    json_checks = {}
                    if "json" in response.headers.get("content-type", ""):
                        try:
                            obj = json.loads(head)
                            json_checks = {"json_parsed": True, "api_error": "error" in obj}
                            if isinstance(obj, dict) and "extent" in obj:
                                json_checks["advertised_extent"] = obj["extent"]
                            if isinstance(obj, dict) and "layers" in obj:
                                json_checks["flowline_layers"] = [
                                    x for x in obj["layers"] if "flowline" in x.get("name", "").lower()
                                ]
                        except (ValueError, TypeError):
                            json_checks = {
                                "json_parsed": False,
                                "note": "Response may exceed 64KiB probe cap",
                            }
                    okay = (
                        response.status_code in (200, 206)
                        and len(head) > 0
                        and not is_error_page
                        and not json_checks.get("api_error", False)
                    )
                    return {
                        **base,
                        "final_url": url,
                        "http_status": response.status_code,
                        "status": "reachable" if okay else "http/error response",
                        "sampled_bytes": len(head),
                        "content_type": response.headers.get("content-type"),
                        "advertised_content_length": response.headers.get("content-length"),
                        "last_modified": response.headers.get("last-modified"),
                        "magic": "PDF"
                        if is_pdf
                        else "ZIP/XLSX"
                        if is_zip
                        else "TIFF"
                        if is_tif
                        else "text/other",
                        **json_checks,
                    }
            raise ValueError("Too many redirects")
    except (requests.RequestException, ValueError) as e:
        return {
            **base,
            "status": "unreachable from this runner",
            "error": str(e)[:350],
            "not_evidence_of_global_unavailability": True,
        }


def github_health(repo):
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/buffedlizard55-lab/{repo}/commits/main"],
            capture_output=True,
            text=True,
            timeout=25,
        )
        if result.returncode:
            return {"repository": repo, "status": "not readable", "error": result.stderr[-250:]}
        obj = json.loads(result.stdout)
        return {
            "repository": repo,
            "status": "reachable",
            "head": obj["sha"],
            "committed_utc": obj["commit"]["committer"]["date"],
            "url": obj["html_url"],
            "message": obj["commit"]["message"].splitlines()[0],
        }
    except (OSError, subprocess.TimeoutExpired, KeyError, ValueError) as e:
        return {"repository": repo, "status": "not readable", "error": str(e)[:250]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/data/source-health.json")
    args = parser.parse_args()
    sources = json.loads((ROOT / "registry/sources.json").read_text())["sources"]
    targets = [s for s in sources if s.get("monitor_url")]
    if not all(permitted(s["monitor_url"]) for s in targets):
        raise ValueError("Registry contains a forbidden monitor target")
    repos = [
        "GEMSDOE",
        "GEMSDOE2",
        "GEMSDOE3",
        "GEMSDOE4",
        "5GEMSDOE",
        "6GEMSDOE",
        "7GEMSDOE",
        "8GEMSDOE",
        "GEMSDOE9",
        "GEMSDOE10",
        "11GEMSDOE",
        "12GEMSDOE",
        "13GEMSDOE",
        "14GEMSDOE",
        "15GEMSDOE",
        "16GEMSDOE",
        "17GEMSDOE",
        "18GEMSDOE",
        "19GEMSDOE",
        "20GEMSDOE",
        "GEMSDOE21",
    ]
    with ThreadPoolExecutor(max_workers=5) as pool:
        data_health = list(pool.map(probe, targets))
        repo_health = list(pool.map(github_health, repos))
    report = {
        "kind": "permitted-source-health-only",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "drivendata_requests": 0,
        "competition_uploads": 0,
        "sources": data_health,
        "repositories": repo_health,
        "warning": "Health probes verify response headers/sample bytes ONLY; not full-file hashes, coverage, licenses, science or scores.",
        "leaderboard": "Dated static snapshot; never automatically fetched.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Checked {len(targets)} permitted data endpoints and {len(repos)} repositories; 0 DrivenData requests"
    )


if __name__ == "__main__":
    main()

"""Retrieve free official validation vectors and a LIMITED ComCat schema probe.

No DrivenData access. Full archives remain ignored/Actions artifacts, never committed.
Every redirect is checked BEFORE requesting it; TLS verification is never disabled.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path
import sys
import zipfile

import rasterio
from rasterio.warp import transform_bounds
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256, utc_now, write_json  # noqa: E402
from refresh_sources import permitted  # noqa: E402

VECTOR_URL = "https://gdr.openei.org/files/1391/qfaults_ingenious_nad83conus117_2023-06-27.zip"
VECTOR_SHA = "c7b091c9ac8bca140ad89ee6bb2bd63dd3ac12e3013acbfd8373d11c9faee59d"


def retrieve(url: str, dest: Path, maximum_bytes: int, expected_sha: str | None = None) -> dict:
    from urllib.parse import urljoin

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".partial")
    try:
        with requests.Session() as session:
            session.headers["User-Agent"] = "GEMSDOE21-official-research-inputs"
            for _ in range(5):
                if not permitted(url):
                    raise ValueError("Non-permitted research URL blocked BEFORE request")
                response = session.get(url, stream=True, timeout=(10, 90), allow_redirects=False)
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers.get("Location", ""))
                    response.close()
                    continue
                with response:
                    response.raise_for_status()
                    if response.status_code != 200:
                        raise ValueError("Expected a complete HTTP 200 input")
                    n = 0
                    with tmp.open("wb") as out:
                        for chunk in response.iter_content(1 << 16):
                            n += len(chunk)
                            if n > maximum_bytes:
                                raise ValueError("Official input exceeded size cap")
                            out.write(chunk)
                if n == 0 or (expected_sha is not None and sha256(tmp) != expected_sha):
                    raise ValueError("Official input is empty or differs from pinned SHA256")
                actual = sha256(tmp)
                tmp.replace(dest)
                return {"url": url, "bytes": n, "sha256": actual, "http_status": 200}
            raise ValueError("Too many official-source redirects")
    finally:
        tmp.unlink(missing_ok=True)


def validate_vector_archive(path: Path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if z.testzip() is not None:
            raise ValueError("Official vector archive CRC failure")
        if any(
            Path(n).is_absolute() or ".." in Path(n).parts or "\\" in n or n.startswith("/") for n in names
        ):
            raise ValueError("Unsafe vector archive member")
        if not any(n.endswith(".shp") for n in names):
            raise ValueError("No shapefile in official vector archive")
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/official-s2")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if not out.is_relative_to(ROOT / "data") and not out.is_relative_to(ROOT / ".cache"):
        raise ValueError("External data must stay in ignored data/ or .cache/")
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_utc": utc_now(),
        "code_commit": os.environ.get("GITHUB_SHA"),
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "drivendata_requests": 0,
        "sources": {},
        "scope": "Official transport and schema checks; NOT model validation or a complete ComCat catalogue",
    }
    try:
        p = out / "qfaults-v2.zip"
        item = retrieve(VECTOR_URL, p, 10_000_000, VECTOR_SHA)
        item["archive_members"] = validate_vector_archive(p)
        item["license"] = "CC BY 4.0; attribution INGENIOUS DOI 10.15121/1881483"
        report["sources"]["fault_vectors"] = {"status": "VERIFIED TRANSPORT", **item}
    except (requests.RequestException, ValueError, zipfile.BadZipFile) as exc:
        report["sources"]["fault_vectors"] = {"status": "BLOCKED", "error": str(exc)[:500]}
    with rasterio.open(ROOT / "docs/data/template-mask.tif") as t:
        bbox = transform_bounds(t.crs, "EPSG:4326", *t.bounds, densify_pts=21)
    params = {
        "format": "csv",
        "starttime": "2000-01-01",
        "endtime": "2026-09-29T23:59:59",
        "minlatitude": bbox[1],
        "maxlatitude": bbox[3],
        "minlongitude": bbox[0],
        "maxlongitude": bbox[2],
        "eventtype": "earthquake",
        "minmagnitude": 2,
        "orderby": "time-asc",
        "limit": 100,
    }
    url = (
        requests.Request("GET", "https://earthquake.usgs.gov/fdsnws/event/1/query", params=params)
        .prepare()
        .url
    )
    try:
        p = out / "comcat-schema-probe.csv"
        item = retrieve(url, p, 2_000_000)
        reader = csv.DictReader(io.StringIO(p.read_text()))
        rows = list(reader)
        required = {"id", "time", "latitude", "longitude", "depth", "type", "depthError", "horizontalError"}
        if not rows or not required.issubset(reader.fieldnames or []):
            raise ValueError("ComCat schema missing required origin/type/uncertainty fields or events")
        item.update(
            rows=len(rows),
            fields=reader.fieldnames,
            query=params,
            missing_depth_error=sum(not r["depthError"].strip() for r in rows),
            missing_horizontal_error=sum(not r["horizontalError"].strip() for r in rows),
            footprint_scope="outer reference-grid rectangle, NOT clipped to irregular study footprint",
            complete_catalogue=False,
            candidate_viable=False,
            limitation="First 100 magnitude>=2 events only; completeness/coverage and uncertainty audit still required",
        )
        report["sources"]["comcat"] = {"status": "LIMITED SCHEMA PROBE OBTAINABLE", **item}
    except (requests.RequestException, ValueError) as exc:
        report["sources"]["comcat"] = {"status": "BLOCKED", "url": url, "error": str(exc)[:500]}
    write_json(out / "receipt.json", report)
    print(json.dumps(report, indent=2))
    if report["sources"]["fault_vectors"]["status"] != "VERIFIED TRANSPORT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

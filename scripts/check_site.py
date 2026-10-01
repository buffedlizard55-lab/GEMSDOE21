"""Fail-closed static links/bytes/grid audit and optional real Chromium end-to-end tests."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256  # noqa: E402
from validate_submission import check  # noqa: E402


def static_checks():
    docs = ROOT / "docs"
    manifest = json.loads((docs / "data/submissions.json").read_text())
    template = docs / "data/template-mask.tif"
    if sha256(template) != manifest["template_mask_sha256"]:
        raise AssertionError("Published footprint template hash changed")
    for spec in manifest["files"]:
        path = docs / spec["href"]
        assert path.resolve().is_relative_to(docs.resolve())
        assert path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"]
        assert check(path, template, spec["sha256"])["passed"]
    assert manifest["byte_identical_to_h19_4"] and not manifest["new_submission_recommended"]
    result = json.loads((docs / "data/h21-1-results.json").read_text())
    assert result["disposition"] == "REJECTED" and not result["gate"]["submission_eligible"]
    assert sha256(ROOT / "evidence/h21-1-results.json") == sha256(docs / "data/h21-1-results.json")
    from gems.locks import verify_file, verify_prompt

    locked = verify_file(ROOT, "research/preregistration-h21.md")
    verify_file(ROOT, "research/preregistration-h21-s2.md")
    verify_file(ROOT, "research/preregistration-h21-s3.md")
    verify_file(ROOT, "evidence/h21-1-results.json")
    readiness = json.loads((docs / "data/research-readiness-s3.json").read_text())
    assert not readiness["dimensions"]["field_fit_permission"]["authorized"]
    assert not readiness["dimensions"]["new_submission_eligibility"]["eligible"]
    assert readiness["field_model_fits_s3"] == readiness["geological_scores_observed_s3"] == 0
    for path in (
        "research-readiness-s3.json",
        "official-inputs-s3.json",
        "prototype-s3.json",
        "input-recovery-s3.json",
        "baseline-history-s3.json",
    ):
        assert sha256(ROOT / "evidence" / path) == sha256(docs / "data" / path)
    assert (docs / "readiness.html").is_file()
    assert hashlib.sha256(locked).hexdigest() == result["registration_sha256"]
    verify_prompt(ROOT / "README.md")
    pages = list(docs.glob("*.html")) + [ROOT / "index.html"]
    links_checked = 0
    for page in pages:
        soup = BeautifulSoup(page.read_text(), "html.parser")
        assert soup.html.get("lang") == "en" and soup.select_one("main#main")
        base = soup.find("base")
        directory = page.parent / (base.get("href", "") if base else "")
        for element, attr in [(n, "href") for n in soup.select("a[href],link[href]")] + [
            (n, "src") for n in soup.select("img[src],script[src]")
        ]:
            url = urlparse(element[attr])
            assert url.scheme not in ("javascript", "data"), "Unsafe link"
            if url.scheme or url.netloc:
                assert url.scheme in ("https", "mailto")
                continue
            target = (
                (directory / unquote(url.path)).resolve()
                if url.path
                else (directory / "index.html").resolve()
                if base
                else page.resolve()
            )
            assert target.is_relative_to(ROOT) and target.is_file(), (
                f"Broken local link {page.name}: {element[attr]}"
            )
            if url.fragment and target.suffix == ".html":
                other = BeautifulSoup(target.read_text(), "html.parser")
                assert other.find(id=unquote(url.fragment)), f"Missing anchor: {element[attr]}"
            links_checked += 1
        first = soup.select_one("a[data-verified-download]")
        if page.name in ("index.html", "executive-summary.html"):
            assert first and first.get("download") == manifest["files"][0]["name"]
            assert soup.select_one("#submission-note").get("value") == manifest["note"]
        embedded = json.loads(soup.select_one("#submission-manifest").text)
        assert embedded == manifest
    for asset in (ROOT / "site/assets").iterdir():
        assert sha256(asset) == sha256(docs / "assets" / asset.name), f"Stale compiled asset: {asset.name}"
    assert (ROOT / ".nojekyll").exists() and (docs / ".nojekyll").exists()
    assert BeautifulSoup((ROOT / "index.html").read_text(), "html.parser").find("base")["href"] == "docs/"
    if shutil.which("node"):
        subprocess.run(["node", "--check", str(ROOT / "site/assets/site.js")], check=True)
    print(
        f"Static audit passed: {len(pages)} pages; {links_checked} local links; {len(manifest['files'])} validated downloads; original prompt unchanged"
    )
    return {
        "passed": True,
        "pages": len(pages),
        "local_links": links_checked,
        "downloads": len(manifest["files"]),
        "prompt_unchanged": True,
    }


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def browser_checks():
    from playwright.sync_api import sync_playwright, expect

    out = ROOT / ".cache/site-checks"
    stage = out / "public"
    stage.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "docs", stage / "docs", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "index.html", stage / "index.html")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(stage)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []
    completed = []
    try:
        with sync_playwright() as p:
            launch = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
            executable = os.environ.get("CHROMIUM_EXECUTABLE")
            # Sandbox fallback from a pinned npm Chromium package when Microsoft's CDN is inaccessible.
            vendor_lib = ROOT / ".cache/browser/al2023/lib"
            if not executable and Path("/tmp/chromium").exists() and vendor_lib.exists():
                executable = "/tmp/chromium"
            if executable:
                launch["executable_path"] = executable
                launch["args"] += ["--single-process", "--no-zygote", "--disable-gpu"]
                launch["env"] = {
                    **os.environ,
                    "LD_LIBRARY_PATH": str(vendor_lib) + ":" + os.environ.get("LD_LIBRARY_PATH", ""),
                }
            browser = p.chromium.launch(**launch)
            context = browser.new_context(
                accept_downloads=True,
                viewport={"width": 1440, "height": 1000},
                permissions=["clipboard-read", "clipboard-write"],
            )
            feed = json.loads((ROOT / "docs/data/source-health.json").read_text())
            context.route(
                "https://api.github.com/**",
                lambda route: route.fulfill(
                    status=200, content_type="application/json", body=json.dumps({"body": json.dumps(feed)})
                ),
            )
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            base = f"http://127.0.0.1:{server.server_port}"
            for name in [
                "index.html",
                "executive-summary.html",
                "research.html",
                "readiness.html",
                "sources.html",
            ]:
                page.goto(f"{base}/docs/{name}", wait_until="networkidle")
                expect(page.locator("h1")).to_be_visible()
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth+1"), (
                    f"Desktop overflow: {name}"
                )
                completed.append("desktop: " + name)
            expect(page.locator("#health-table tbody tr")).to_have_count(len(feed["sources"]))
            page.locator("[data-filter]").fill("thermal")
            assert page.locator("#source-table tbody tr:visible").count() < len(
                json.loads((ROOT / "registry/sources.json").read_text())["sources"]
            )
            completed.append("source feed rendering + ledger search")
            page.goto(f"{base}/docs/index.html", wait_until="networkidle")
            page.screenshot(path=str(out / "desktop.png"), full_page=True)
            manifest = json.loads((ROOT / "docs/data/submissions.json").read_text())
            main = manifest["files"][0]
            with page.expect_download() as info:
                page.locator(f"[data-verified-download='{main['name']}']").click()
            download = info.value
            assert download.suggested_filename == main["name"]
            dest = out / main["name"]
            download.save_as(dest)
            assert (
                sha256(dest) == main["sha256"] and check(dest, ROOT / "docs/data/template-mask.tif")["passed"]
            )
            expect(page.locator("[data-download-status]")).to_contain_text("SHA-256 verified")
            page.locator("[data-copy]").click()
            expect(page.locator(".copy-status")).to_contain_text("Note copied")
            assert page.evaluate("navigator.clipboard.readText()") == manifest["note"]
            completed.append("real SHA-verified download + Python preflight + clipboard")
            page.goto(f"{base}/docs/executive-summary.html", wait_until="networkidle")
            page.locator("#local-file").set_input_files(str(dest))
            expect(page.locator("#file-check-result")).to_contain_text("Recognized primary")
            bad = bytearray(dest.read_bytes())
            bad[0] ^= 1
            page.locator("#local-file").set_input_files(
                {"name": "corrupt.tif", "mimeType": "image/tiff", "buffer": bytes(bad)}
            )
            expect(page.locator("#file-check-result")).to_contain_text("SHA-256 does not match")
            page.locator("#local-file").set_input_files(
                {"name": "unknown.tif", "mimeType": "image/tiff", "buffer": b"broken"}
            )
            expect(page.locator("#file-check-result")).to_contain_text("NOT checked here")
            completed.append("local file recognizes known bytes; rejects corrupt/unknown")
            page.goto(f"{base}/docs/index.html", wait_until="networkidle")
            downloads = []
            page.on("download", lambda d: downloads.append(d.suggested_filename))
            pattern = "**/downloads/" + main["name"]
            page.route(
                pattern, lambda route: route.fulfill(status=200, content_type="image/tiff", body=b"truncated")
            )
            page.locator(f"[data-verified-download='{main['name']}']").click()
            expect(page.locator("[data-download-status]")).to_contain_text("Byte length mismatch")
            assert not downloads, "Truncated bytes must never be downloaded/padded"
            page.unroute(pattern)
            page.route(pattern, lambda route: route.fulfill(status=503, body="unavailable"))
            page.locator(f"[data-verified-download='{main['name']}']").click()
            expect(page.locator("[data-download-status]")).to_contain_text("HTTP 503")
            assert not downloads
            page.unroute(pattern)
            completed.append("fail-closed truncated/HTTP-error downloads")
            for name in [
                "index.html",
                "executive-summary.html",
                "research.html",
                "readiness.html",
                "sources.html",
            ]:
                page.set_viewport_size({"width": 390, "height": 844})
                page.goto(f"{base}/docs/{name}", wait_until="networkidle")
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth+1"), (
                    f"Mobile overflow: {name}"
                )
                expect(page.locator("h1")).to_be_visible()
                completed.append("mobile: " + name)
            page.goto(f"{base}/docs/index.html", wait_until="networkidle")
            page.screenshot(path=str(out / "mobile.png"), full_page=True)
            page.goto(base + "/", wait_until="networkidle")
            expect(page.locator("a[data-verified-download]").first).to_be_visible()
            assert page.locator("img").first.evaluate("img => img.complete && img.naturalWidth > 0")
            completed.append("legacy Pages root/base assets")
            context.close()
            browser.close()
            # Single-process sandbox Chromium exits when its sole incognito context closes.
            # A fresh browser also isolates the no-JS fallback from all previous route overrides.
            browser = p.chromium.launch(**launch)
            nojs = browser.new_context(java_script_enabled=False, accept_downloads=True)
            plain = nojs.new_page()
            plain.goto(base + "/docs/index.html")
            with plain.expect_download() as info:
                plain.locator(f"[data-verified-download='{main['name']}']").click()
            assert info.value.suggested_filename == main["name"]
            completed.append("no-JavaScript direct download fallback")
            nojs.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert not errors, f"Browser JavaScript errors: {errors}"
    print(f"Real Chromium audit passed: {len(completed)} scenarios; 0 JavaScript errors")
    return {"passed": True, "scenarios": completed, "javascript_errors": errors, "browser": "Chromium"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "static": static_checks(),
    }
    if args.browser:
        report["browser"] = browser_checks()
    out = ROOT / ".cache/site-checks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

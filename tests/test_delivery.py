"""Post-result infrastructure tests, not additional candidate model selection."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems.submission import write

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_submission import check  # noqa: E402
from refresh_sources import permitted, probe  # noqa: E402


@pytest.fixture
def small_template(tmp_path):
    p = tmp_path / "template.tif"
    a = np.zeros((16, 16), np.float32)
    a[0] = np.nan
    with rasterio.open(
        p,
        "w",
        driver="GTiff",
        count=1,
        width=16,
        height=16,
        dtype="float32",
        nodata=np.nan,
        crs="EPSG:32611",
        transform=from_origin(243350, 4508550, 100, 100),
    ) as s:
        s.write(a, 1)
    return p


@pytest.mark.parametrize(
    "host",
    [
        "www.drivendata.org",
        "community.drivendata.org",
        "localhost",
        "127.0.0.1",
        "gdr.openei.org.evil.invalid",
    ],
)
def test_monitor_never_allows_competition_or_untrusted_hosts(host):
    assert not permitted("https://" + host + "/anything")


@pytest.mark.parametrize(
    "url", ["http://gdr.openei.org/", "https://user:pw@gdr.openei.org/", "https://gdr.openei.org:8443/"]
)
def test_monitor_rejects_cleartext_credentials_and_custom_ports(url):
    assert not permitted(url)


def test_forbidden_redirect_blocked_before_request(monkeypatch):
    called = []

    class Response:
        status_code = 302
        headers = {"Location": "https://www.drivendata.org/competitions/306/"}

        def close(self):
            pass

    def get(self, url, **kwargs):
        called.append(url)
        return Response()

    monkeypatch.setattr("requests.Session.get", get)
    out = probe({"id": "test", "title": "test", "monitor_url": "https://gdr.openei.org/"})
    assert called == ["https://gdr.openei.org/"]
    assert "blocked BEFORE" in out["error"]


@pytest.mark.parametrize("member", ["../bad.tif", "nested/bad.tif", "bad\\name.tif", "report.html"])
def test_zip_unsafe_member_rejected(small_template, tmp_path, member):
    zpath = tmp_path / "bad.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr(member, b"bad")
    with pytest.raises(ValueError):
        check(zpath, small_template)


def test_zip_extra_files_rejected(small_template, tmp_path):
    zpath = tmp_path / "bad.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("one.tif", b"bad")
        z.writestr("__MACOSX/junk", b"bad")
    with pytest.raises(ValueError):
        check(zpath, small_template)


def test_expected_hash_fail_closed(small_template, tmp_path):
    p = write(np.zeros((16, 16)), small_template, tmp_path / "a.tif")
    assert not check(p, small_template, "0" * 64)["passed"]


def test_cli_malformed_file_is_failure_not_clipped(tmp_path, small_template):
    p = tmp_path / "bad.tif"
    p.write_bytes(b"truncated")
    out = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_submission.py"),
            str(p),
            "--template",
            str(small_template),
        ],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 1
    assert '"passed": false' in out.stdout


def test_first_result_is_not_overwritten():
    path = ROOT / "evidence/h21-1-results.json"
    if not path.exists():
        pytest.skip("Registered first result not yet generated")
    first = path.read_bytes()
    out = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate.py")], capture_output=True, text=True)
    assert out.returncode != 0 and "Refusing to overwrite" in out.stderr
    assert path.read_bytes() == first


def test_locked_original_prompt_and_site_published_outputs():
    spec = importlib.util.spec_from_file_location("check_site", ROOT / "scripts/check_site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.static_checks()["passed"]

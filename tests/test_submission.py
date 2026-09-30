from pathlib import Path
import zipfile

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems.submission import write, validate, zip_single


@pytest.fixture
def template(tmp_path):
    path = tmp_path / "template.tif"
    a = np.zeros((32, 40), np.float32)
    a[:2, :] = np.nan
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=32,
        width=40,
        count=1,
        dtype="float32",
        crs="EPSG:32611",
        transform=from_origin(243350, 4508550, 100, 100),
        nodata=np.nan,
    ) as s:
        s.write(a, 1)
    return path


@pytest.mark.parametrize("outside", ["nan", "masked-zero"])
def test_strict_writer_grid_range_and_outside_null(template, tmp_path, outside):
    p = np.full((32, 40), 0.5, np.float32)
    path = write(p, template, tmp_path / f"gems21-{outside}.tif", outside)
    r = validate(path, template)
    assert r["passed"] and r["footprint_out_of_range"] == 0 and r["footprint_nan_inf"] == 0
    assert r["raw_all_pixels_finite"] == (outside == "masked-zero")
    zpath = zip_single(path)
    with zipfile.ZipFile(zpath) as z:
        assert z.namelist() == [path.name]
        assert z.read(path.name) == path.read_bytes()
    assert zip_single(path).read_bytes() == zpath.read_bytes()


@pytest.mark.parametrize("bad", [-3.4028235e38, -1e-6, 1.00001, np.nan, np.inf])
def test_writer_rejects_not_silently_clips(template, tmp_path, bad):
    p = np.zeros((32, 40))
    p[4, 4] = bad
    with pytest.raises(ValueError):
        write(p, template, tmp_path / "bad.tif")
    assert not (tmp_path / "bad.tif").exists()


def test_wrong_grid_detected(template, tmp_path):
    path = write(np.zeros((32, 40)), template, tmp_path / "wrong.tif")
    with rasterio.open(path, "r+") as s:
        s.transform = from_origin(243351, 4508550, 100, 100)
    assert not validate(path, template)["passed"]


def test_published_downloads_hash_and_format_when_built():
    import json

    root = Path(__file__).resolve().parents[1]
    manifest = root / "docs/data/submissions.json"
    if not manifest.exists():
        pytest.skip("Published files not yet built")
    m = json.loads(manifest.read_text())
    template = root / "docs/data/template-mask.tif"
    for f in m["files"]:
        path = root / "docs" / f["href"]
        if path.suffix == ".tif":
            assert validate(path, template, f["sha256"])["passed"]
        else:
            with zipfile.ZipFile(path) as z:
                assert len(z.namelist()) == 1 and z.namelist()[0].endswith(".tif")

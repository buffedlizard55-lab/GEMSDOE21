"""Additional range/grid/container regressions; no geological scoring."""

from pathlib import Path
import zipfile

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine, from_origin

from gems.io import sha256
from gems.submission import validate, validate_bundle, write, zip_single


def reference(tmp_path, *, empty=False, crs="EPSG:32611", dtype="float32", transform=None):
    path = tmp_path / "reference.tif"
    values = np.full((16, 20), np.nan if empty else 0, dtype=dtype)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        count=1,
        height=16,
        width=20,
        dtype=dtype,
        crs=crs,
        transform=transform or from_origin(243350, 4508550, 100, 100),
        nodata=np.nan,
    ) as dst:
        dst.write(values, 1)
    return path


@pytest.mark.parametrize("bad", [np.nextafter(1.0, 2.0), np.nextafter(0.0, -1.0), np.nan, np.inf, -np.inf])
def test_invalid_float64_never_rounds_into_compliance_or_overwrites(tmp_path, bad):
    template = reference(tmp_path)
    target = write(np.zeros((16, 20)), template, tmp_path / "existing.tif")
    before = sha256(target)
    pred = np.zeros((16, 20), np.float64)
    pred[4, 4] = bad
    with pytest.raises(ValueError):
        write(pred, template, target)
    assert sha256(target) == before
    assert not list(tmp_path.glob(".gems-tiff-*"))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"empty": True},
        {"crs": None},
        {"crs": "EPSG:4326"},
        {"dtype": "float64"},
        {"transform": from_origin(243350, 4508550, 50, 50)},
        {"transform": Affine(100, 1, 243350, 0, -100, 4508550)},
    ],
)
def test_matching_a_bad_template_is_not_compliance(tmp_path, kwargs):
    template = reference(tmp_path, **kwargs)
    with pytest.raises(ValueError, match="Invalid submission template"):
        write(np.zeros((16, 20)), template, tmp_path / "file.tif")


def test_template_and_tiff_cannot_be_overwritten_by_outputs(tmp_path):
    template = reference(tmp_path)
    before = sha256(template)
    with pytest.raises(ValueError, match="reference template"):
        write(np.zeros((16, 20)), template, template)
    with pytest.raises(ValueError):
        zip_single(template, template)
    assert sha256(template) == before


def test_complex_and_string_predictions_are_not_coerced(tmp_path):
    template = reference(tmp_path)
    for pred in (np.zeros((16, 20), complex), np.full((16, 20), "0")):
        with pytest.raises(ValueError, match="real numeric"):
            write(pred, template, tmp_path / "file.tif")


def test_safe_bundle_checks_the_actual_contained_tiff(tmp_path):
    template = reference(tmp_path)
    tif = write(np.full((16, 20), 0.4), template, tmp_path / "file.tif")
    archive = zip_single(tif)
    report = validate_bundle(archive, template, sha256(tif))
    assert report["passed"] and report["zip_exactly_one_tiff_crc_verified"]
    assert report["container_sha256"] == sha256(archive)
    assert not validate_bundle(archive, template, "0" * 64)["passed"]
    with rasterio.open(tif, "r+") as dst:
        values = dst.read(1)
        values[5, 5] = np.inf
        dst.write(values, 1)
    assert not validate_bundle(zip_single(tif), template)["passed"]


@pytest.mark.parametrize(
    "name,symlink",
    [
        ("../escape.tif", False),
        ("nested/a.tif", False),
        ("file.tif", True),
        ("C:escape.tif", False),
        ("line\nbreak.tif", False),
    ],
)
def test_unsafe_zip_is_never_extracted(tmp_path, name, symlink):
    template = reference(tmp_path)
    archive = tmp_path / "unsafe.zip"
    info = zipfile.ZipInfo(name)
    if symlink:
        info.external_attr = 0o120777 << 16
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(info, b"not a confidence raster")
    with pytest.raises(ValueError, match="Unsafe"):
        validate_bundle(archive, template)
    assert not (tmp_path / "escape.tif").exists()


def test_wrong_complex_tiff_dtype_fails_without_range_type_error(tmp_path):
    template = reference(tmp_path)
    path = tmp_path / "complex.tif"
    with rasterio.open(template) as src:
        profile = src.profile.copy()
        profile.update(dtype="complex64", nodata=None)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(np.zeros((16, 20), np.complex64), 1)
    assert not validate(path, template)["passed"]


def test_zip_with_extra_file_and_unknown_output_scheme_rejected(tmp_path):
    template = reference(tmp_path)
    tif = write(np.zeros((16, 20)), template, tmp_path / "file.tif")
    with pytest.raises(ValueError):
        zip_single(tif, Path(tmp_path / "file.txt"))
    archive = zip_single(tif)
    with zipfile.ZipFile(archive, "a") as z:
        z.writestr("readme.txt", "extra")
    with pytest.raises(ValueError, match="exactly one"):
        validate_bundle(archive, template)

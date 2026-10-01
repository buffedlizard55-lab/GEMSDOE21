from pathlib import Path
import zipfile

import pytest

from gems.archives import safe_members, unpack


@pytest.mark.parametrize("name", ["../outside", "/root/a", "C:/secret", "x\\y", "x/../y", "x\ny", "x\x00y"])
def test_unsafe_member_names_fail_before_extraction(name):
    with pytest.raises(ValueError):
        safe_members([{"name": name, "bytes": 1, "special": False}])


def test_archive_limits_special_files_and_case_collisions():
    for members in [
        [{"name": "x", "bytes": 10, "special": True}],
        [{"name": "x", "bytes": 900_000_001, "special": False}],
        [{"name": "X", "bytes": 1, "special": False}, {"name": "x", "bytes": 1, "special": False}],
    ]:
        with pytest.raises(ValueError):
            safe_members(members)


def test_real_safe_zip_crc_and_no_overwrite(tmp_path):
    archive = tmp_path / "safe.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("nested/data.txt", b"verified data")
    dest = tmp_path / "extracted"
    report = unpack(archive, dest)
    assert report["crc_verified"] and report["uncompressed_bytes"] == 13
    assert (dest / "nested/data.txt").read_bytes() == b"verified data"
    with pytest.raises(ValueError, match="nonempty"):
        unpack(archive, dest)


def test_zip_symlink_is_not_extracted(tmp_path):
    archive = tmp_path / "unsafe.zip"
    info = zipfile.ZipInfo("escape")
    info.external_attr = 0o120777 << 16
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(info, "../elsewhere")
    with pytest.raises(ValueError, match="Unsafe"):
        unpack(archive, tmp_path / "extracted")
    assert not (tmp_path / "extracted/escape").exists()


def test_real_safe_7z_crc_and_metadata(tmp_path):
    py7zr = pytest.importorskip("py7zr")
    original = tmp_path / "hello.txt"
    original.write_text("source bytes")
    archive = tmp_path / "safe.7z"
    with py7zr.SevenZipFile(archive, "w") as z:
        z.write(original, "nested/hello.txt")
    dest = tmp_path / "extracted"
    report = unpack(archive, dest)
    assert report["crc_verified"] and report["uncompressed_bytes"] == 12
    assert (dest / "nested/hello.txt").read_text() == "source bytes"


def test_invalid_archive_suffix(tmp_path):
    with pytest.raises(ValueError, match="Expected official"):
        unpack(Path("file.tar"), tmp_path / "extracted")

"""Fail-closed local GeoTIFF/one-GeoTIFF ZIP validation; NEVER clip values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import zipfile
from rasterio.errors import RasterioError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256  # noqa: E402
from gems.submission import validate  # noqa: E402


def check(path: Path, template: Path, expected_sha: str | None = None):
    if expected_sha and sha256(path) != expected_sha:
        return {"passed": False, "error": "Input SHA256 does not match expected bytes"}
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            members = z.infolist()
            if len(members) != 1:
                raise ValueError("ZIP must contain exactly one GeoTIFF and nothing else")
            entry = members[0]
            name = entry.filename
            if Path(name).name != name or "\\" in name or not name.lower().endswith(".tif"):
                raise ValueError("ZIP member must be a safe root-level .tif filename")
            if entry.file_size > 256 * 1024 * 1024 or entry.flag_bits & 1:
                raise ValueError("Encrypted/over-256MiB ZIP member is unsupported")
            # Validate CRC while reading; never extract to a caller-controlled path.
            with tempfile.TemporaryDirectory(prefix="gems21-preflight-") as tmp:
                tif = Path(tmp) / "prediction.tif"
                tif.write_bytes(z.read(entry))
                result = validate(tif, template)
            result.update({"archive_sha256": sha256(path), "zip_member": name, "zip_single_member": True})
            return result
    if path.suffix.lower() != ".tif":
        raise ValueError("Expected .tif or one-GeoTIFF .zip, not a report or image")
    return validate(path, template, expected_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--template", type=Path, default=ROOT / "docs/data/template-mask.tif")
    parser.add_argument("--expected-sha")
    args = parser.parse_args()
    try:
        result = check(args.file, args.template, args.expected_sha)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, RasterioError) as e:
        result = {"passed": False, "error": str(e)}
    print(json.dumps(result, indent=2, allow_nan=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

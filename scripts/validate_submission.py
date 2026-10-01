"""Fail-closed local GeoTIFF/one-GeoTIFF ZIP validation; NEVER clip values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile
from rasterio.errors import RasterioError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import sha256  # noqa: E402
from gems.submission import validate_bundle  # noqa: E402


def check(path: Path, template: Path, expected_sha: str | None = None):
    path, template = Path(path), Path(template)
    if path.suffix.lower() not in (".tif", ".zip"):
        raise ValueError("Expected .tif or one-GeoTIFF .zip, not a report or image")
    # CLI SHA authenticates the input container bytes, not organizer provenance.
    if expected_sha and sha256(path) != expected_sha:
        return {"passed": False, "error": "Input SHA256 does not match expected bytes"}
    result = validate_bundle(path, template, expected_sha if path.suffix.lower() != ".zip" else None)
    if path.suffix.lower() == ".zip":
        result.update({"archive_sha256": sha256(path), "zip_single_member": True})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--template", type=Path, default=ROOT / "docs/data/template-mask.tif")
    parser.add_argument("--expected-sha", help="Expected SHA256 of the input TIFF or ZIP container")
    args = parser.parse_args()
    try:
        result = check(args.file, args.template, args.expected_sha)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, RasterioError) as e:
        result = {"passed": False, "error": str(e)}
    print(json.dumps(result, indent=2, allow_nan=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

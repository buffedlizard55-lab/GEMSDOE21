"""Input-only official acquisition for S3. NEVER fit, infer, score or upload to DrivenData.

Obtainability is established by full downloaded bytes and schema, not landing pages.
The prospective box was locked BEFORE fault outcomes. Label geometry stays split/scorer
metadata; no fault map is rendered and no candidate is evaluated in this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

import fiona
import numpy as np
import rasterio
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform_bounds

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.archives import unpack  # noqa: E402
from gems.io import sha256, utc_now, write_json  # noqa: E402
from gems.locks import verify_file  # noqa: E402
from fetch_research_inputs import retrieve  # noqa: E402
from publish_s2_execution import redact  # noqa: E402

BOX = (-115.8, 38.8, -114.8, 39.8)
MAG_ITEM = "https://www.sciencebase.gov/catalog/item/68c9d87fd4be0274ff4be93e?format=json"
MAG_GRID_URL = "https://www.sciencebase.gov/catalog/file/get/68c9d87fd4be0274ff4be93e?f=__disk__80%2Fd5%2F2e%2F80d52ec9a27baa4946af580fa1c173c7bb91e0ab"
MAG_XML_URL = "https://www.sciencebase.gov/catalog/file/get/68c9d87fd4be0274ff4be93e?f=__disk__cd%2F31%2F7c%2Fcd317ce112240b9de9e643533b7267e10c00184a"
GRID_MD5 = "b5faee39106a9421579cb97fa799cce8"
XML_MD5 = "b61572ccf8f506ace056588c0fc15771"
QFAULT_URL = "https://earthquake.usgs.gov/static/lfs/nshm/qfaults/Qfaults_GIS.zip"
PALEO_URL = "https://gdr.openei.org/files/1391/paleo_geothermal_regional.zip"
ATLAS_URL = (
    "https://www.conservation.ca.gov/cgs/documents/publications/geologic-data-maps/GDM_009-SNESA-Data.zip"
)


def official_file(url, path, cap, expected_md5=None, expected_bytes=None):
    item = retrieve(url, path, cap)
    digest = hashlib.md5(path.read_bytes()).hexdigest()
    if (expected_md5 and digest != expected_md5) or (expected_bytes and item["bytes"] != expected_bytes):
        path.unlink(missing_ok=True)
        raise ValueError("Official metadata MD5/byte size mismatch; input rejected")
    return {
        **item,
        "md5": digest,
        "official_metadata_md5_matched": bool(expected_md5 and digest == expected_md5),
        "official_metadata_bytes_matched": bool(expected_bytes and item["bytes"] == expected_bytes),
    }


def numeric_raster_schema(path):
    """Metadata plus actual nodata/support counts in the locked box. No model outcome."""
    with rasterio.open(path) as src:
        numeric = (
            src.count == 1
            and src.dtypes[0] in ("float32", "float64")
            and src.crs is not None
            and all(c.name not in ("red", "green", "blue", "palette") for c in src.colorinterp)
        )
        record = {
            "name": path.name,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "count": src.count,
            "dtypes": list(src.dtypes),
            "color_interpretation": [c.name for c in src.colorinterp],
            "crs": str(src.crs),
            "shape": list(src.shape),
            "resolution": list(src.res),
            "bounds": list(src.bounds),
            "nodata": float(src.nodata) if src.nodata is not None and np.isfinite(src.nodata) else None,
            "units": list(src.units),
            "descriptions": list(src.descriptions),
            "numeric_single_band_not_color_image": numeric,
            "scope": "Input support/metadata only; numeric values are not visualized or evaluated against faults",
        }
        if numeric:
            box = transform_bounds("EPSG:4326", src.crs, *BOX, densify_pts=41)
            window = from_bounds(*box, transform=src.transform).round_offsets().round_lengths()
            window = window.intersection(Window(0, 0, src.width, src.height))
            support_count = total = 0
            # Chunk the reserved-region support audit; never load every grid at once.
            for start in range(int(window.row_off), int(window.row_off + window.height), 256):
                piece = Window(
                    window.col_off, start, window.width, min(256, window.row_off + window.height - start)
                )
                values = src.read(1, window=piece, masked=True)
                supported = (
                    ~np.ma.getmaskarray(values) & np.isfinite(values.data) & (np.abs(values.data) < 1e20)
                )
                support_count += int(supported.sum())
                total += supported.size
            record.update(
                reserved_box_outer_window_cells=total,
                reserved_box_supported_cells=support_count,
                reserved_box_support_fraction=support_count / total if total else 0,
                support_count_not_prediction_vs_label=True,
                reserved_box_bounds_wgs84=list(BOX),
                support_scope="Envelope transformed to source grid; not polygon-exact coverage or independent acquisition resolution",
            )
        return record


def vector_schema(path, reserve=False):
    records = []
    for layer in fiona.listlayers(str(path)):
        with fiona.open(path, layer=layer) as src:
            feature_count = len(src)
            geometry = src.schema["geometry"]
            bounds = None
            bounds_error = None
            if feature_count and geometry not in (None, "None"):
                try:
                    bounds = list(src.bounds)
                except Exception as exc:
                    # Empty/attribute-only layers or drivers without extent metadata
                    # must not erase independently verified transport/other schemas.
                    bounds_error = f"{type(exc).__name__}: {exc}"
            rec = {
                "layer": layer,
                "features": feature_count,
                "crs": str(src.crs),
                "geometry": geometry,
                "fields": dict(src.schema["properties"]),
                "bounds": bounds,
                "bounds_error": bounds_error,
                "role": "source schema / future split/scorer metadata, NOT predictor or new confirmed truth",
            }
            if (
                reserve
                and src.crs
                and feature_count
                and geometry not in (None, "None")
                and bounds is not None
            ):
                bbox = transform_bounds("EPSG:4326", src.crs, *BOX, densify_pts=41)
                # Fiona bbox is an envelope intersection, NOT an exact geometry count.
                rec["features_with_envelope_intersecting_reserved_box"] = sum(
                    1 for _ in src.filter(bbox=bbox)
                )
                rec["reserved_box_bounds_wgs84"] = list(BOX)
                rec["labels_used_in_model_or_score"] = False
            records.append(rec)
    return records


def acquire_magnetics(out):
    # Re-read official metadata and bind exactly the selected resource, no silent substitution.
    metadata_path = out / "eastern-magnetic-item.json"
    metadata_transport = official_file(MAG_ITEM, metadata_path, 200_000)
    metadata = json.loads(metadata_path.read_text())
    grid = next(f for f in metadata["files"] if f["name"] == "magnetic_grids.7z")
    if grid["checksum"] != {"value": GRID_MD5, "type": "MD5"} or grid["size"] != 210_814_683:
        raise ValueError("Pinned official grid metadata changed; requires a separate amendment")
    item = official_file(MAG_GRID_URL, out / "magnetic_grids.7z", 220_000_000, GRID_MD5, 210_814_683)
    xml = official_file(MAG_XML_URL, out / "metadata_magnetics.xml", 100_000, XML_MD5, 25_110)
    tree = ET.parse(out / "metadata_magnetics.xml")
    unit_context = [
        {"tag": e.tag, "text": (e.text or "").strip()}
        for e in tree.iter()
        if e.text
        and any(
            term in e.text.lower()
            for term in ("nanotesla", "nano tesla", "reduced to", "rtp", "100 m", "50 m")
        )
    ]
    with tempfile.TemporaryDirectory(prefix="magnetic-schema-", dir=out) as temp:
        directory = Path(temp)
        archive = unpack(out / "magnetic_grids.7z", directory)
        rasters = [
            numeric_raster_schema(p)
            for p in sorted(directory.rglob("*"))
            if p.suffix.lower() in (".tif", ".tiff")
        ]
    if not rasters:
        raise ValueError("Selected numeric magnetic archive contains no GeoTIFFs")
    return {
        "status": "VERIFIED FULL TRANSPORT AND INPUT SCHEMA",
        "doi": "https://doi.org/10.5066/P13VSMZ3",
        "license": "CC0 1.0 as stated by USGS parent release",
        "transport": item,
        "official_item_transport": metadata_transport,
        "metadata_xml_transport": xml,
        "metadata_unit_context": unit_context,
        "archive": archive,
        "rasters": rasters,
        "candidate_validation_viable": False,
        "limitations": [
            "Support window is only input coverage, not hide-and-recover evaluation",
            "200m flight lines / nominal 100m clearance differ from western GeoDAWN Area 2",
            "No matching full 31-channel control, original H19 arms or locked fresh-fit protocol available",
            "Units/processing/source compatibility and whole-system cross-domain links need review before transfer",
        ],
    }


def acquire_vector(url, name, out, reserve=False):
    item = official_file(url, out / name, 60_000_000)
    with tempfile.TemporaryDirectory(prefix="vector-schema-", dir=out) as temp:
        directory = Path(temp)
        archive = unpack(out / name, directory)
        paths = sorted(directory.rglob("*.shp")) + sorted(directory.rglob("*.gdb"))
        schemas = [s for p in paths for s in vector_schema(p, reserve)]
    if not schemas:
        raise ValueError("Official archive has no supported vector schema")
    return {
        "status": "VERIFIED FULL TRANSPORT AND INPUT SCHEMA",
        "transport": item,
        "archive": archive,
        "schemas": schemas,
        "new_label_freshness_established": False,
        "model_input": False,
        "caveat": "A new download/publication date is not evidence of independent new labels; source lineage, mapping scale and rights require review",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".cache/official-s3")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if not out.is_relative_to((ROOT / ".cache").resolve()):
        raise ValueError("Official S3 raw data must remain in ignored .cache/")
    out.mkdir(parents=True, exist_ok=True)
    registration = verify_file(ROOT, "research/preregistration-h21-s3.md")
    with rasterio.open(ROOT / "docs/data/template-mask.tif") as template:
        competition_box = transform_bounds(template.crs, "EPSG:4326", *template.bounds, densify_pts=41)
    disjoint = (
        BOX[0] > competition_box[2]
        or BOX[2] < competition_box[0]
        or BOX[1] > competition_box[3]
        or BOX[3] < competition_box[1]
    )
    if not disjoint:
        raise ValueError("Preregistered external box overlaps the competition outer rectangle")
    report = {
        "kind": "S3-input-only-official-obtainability",
        "generated_utc": utc_now(),
        "code_commit": os.environ.get("GITHUB_SHA"),
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "registration_sha256": hashlib.sha256(registration).hexdigest(),
        "reserved_box_wgs84": list(BOX),
        "competition_outer_bounds_wgs84": list(competition_box),
        "reserved_box_outside_competition_rectangle": disjoint,
        "field_model_fits": 0,
        "geological_scores_observed": 0,
        "drivendata_requests": 0,
        "competition_uploads": 0,
        "sources": {},
        "scope": "Official full-byte transport/schema/coverage metadata only. NOT scientific validation, new fault discovery or eligible submission.",
    }
    jobs = {
        "eastern_magnetics": lambda: acquire_magnetics(out),
        "national_qfaults": lambda: acquire_vector(QFAULT_URL, "Qfaults_GIS.zip", out, True),
        "paleo_geothermal": lambda: acquire_vector(PALEO_URL, "paleo_geothermal_regional.zip", out),
        "sierra_atlas": lambda: acquire_vector(ATLAS_URL, "GDM_009-SNESA-Data.zip", out),
    }
    for name, job in jobs.items():
        try:
            report["sources"][name] = job()
        except Exception as exc:
            # Evidence collection must retain independent source failures; NEVER fallback
            # to a different file, swallow the error as success or attempt a model fit.
            report["sources"][name] = {
                "status": "BLOCKED / REQUIRES REVIEW",
                "error_type": type(exc).__name__,
                "error": redact(str(exc))[:600],
                "not_evidence_of_global_unavailability": True,
            }
        print(f"{name}: {report['sources'][name]['status']}", flush=True)
        write_json(out / "receipt.json", report)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

"""Prepare the ONE locked H21-5 signature and original-vector validation metadata.

Large arrays/geometry stay ignored. Never revise original H21-1 preparation or outcome.
"""

from __future__ import annotations

import gc
import json
from pathlib import Path
import sys
import zipfile

import fiona
import numpy as np
import rasterio
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402
from gems.locks import verify_file  # noqa: E402
from gems.step_profiles import signed_step_features  # noqa: E402
from gems.system_holdout import geometry_window, link_systems  # noqa: E402
from fetch_research_inputs import VECTOR_SHA  # noqa: E402
from verify_prepared import verify  # noqa: E402


def prepare():
    verify_file(ROOT, "research/preregistration-h21-s2.md")
    base_verification = verify(s2_base_only=True)
    if base_verification["features_verified"] != 31:
        raise ValueError("S2 requires the original exact 31 consumed columns")
    data = data_dir()
    source = data / "official-s2/qfaults-v2.zip"
    if not source.is_file() or sha256(source) != VECTOR_SHA:
        raise ValueError("Exact official vector bytes required; no centroid/component-only fallback")
    out = data / "prepared-s2"
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for file, digest in manifest["output_sha256"].items():
            if sha256(out / file) != digest:
                raise ValueError(f"S2 prepared cache changed: {file}")
        if manifest["transform_code_sha256"] != sha256(ROOT / "src/gems/step_profiles.py"):
            raise ValueError("Signed-step transform changed; never silently reuse its cache")
        if manifest["grouping_code_sha256"] != sha256(ROOT / "src/gems/system_holdout.py"):
            raise ValueError("Grouping code changed; never silently reuse its cache")
        return manifest
    out.mkdir(parents=True, exist_ok=True)
    base = data / "prepared"
    fp = np.load(base / "footprint.npy")
    cat = np.load(base / "catalogue.npy")
    idx = np.flatnonzero(fp)
    manifest = {
        "generated_utc": utc_now(),
        "registration_commit": "452c21c",
        "registration_sha256": sha256(ROOT / "research/preregistration-h21-s2.md"),
        "transform_code_sha256": sha256(ROOT / "src/gems/step_profiles.py"),
        "grouping_code_sha256": sha256(ROOT / "src/gems/system_holdout.py"),
        "official_vector_sha256": VECTOR_SHA,
        "predictor_catalogue_usage": False,
        "base_input_verification": base_verification,
        "candidate_columns": [],
        "feature_audit": {},
        "output_sha256": {},
    }
    with rasterio.open(data / "training_features.tif") as s:
        for n, prefix in [(13, "gravity"), (2, "magnetic")]:
            field = s.read(n)
            valid = fp & np.isfinite(field) & (field > -1e20) & (s.read_masks(n) > 0)
            extra, supported = signed_step_features(field, valid, prefix)
            for name, values in extra.items():
                a = values.ravel()[idx]
                path = out / f"{name}.npy"
                np.save(path, a)
                manifest["candidate_columns"].append(name)
                manifest["output_sha256"][path.name] = sha256(path)
                manifest["feature_audit"][name] = {
                    "nonzero_pixels": int((a > 0).sum()),
                    "maximum": float(a.max()),
                    "source_band": n,
                    "source_description": s.descriptions[n - 1],
                    "invalid_source_pixels": int((fp & ~valid).sum()),
                    "catalogue_derived": False,
                }
                del a, values
            del field, valid, extra, supported
            gc.collect()
    strength = np.maximum.reduce(
        [
            np.load(base / f"{name}.npy")
            for name in [
                "mag_gradient_100m",
                "mag_gradient_300m",
                "grav_gradient_100m",
                "grav_gradient_300m",
            ]
        ]
    )
    strength[~np.load(base / "physical_support.npy")] = 0
    np.save(out / "physical_strength.npy", strength)
    manifest["output_sha256"]["physical_strength.npy"] = sha256(out / "physical_strength.npy")
    del strength
    with rasterio.open(data / "sample_submission.tif") as t:
        transform, crs = t.transform, t.crs
    uri = "zip://" + str(source)
    layers = fiona.listlayers(uri)
    if len(layers) != 1:
        raise ValueError("Official fault archive must have the audited single vector layer")
    records = []
    with fiona.open(uri, layer=layers[0]) as vectors:
        if not {"NUM", "NAME"}.issubset(vectors.schema["properties"]):
            raise ValueError("Official fault ID/name schema differs")
        manifest["official_vector_schema"] = vectors.schema
        manifest["official_vector_crs"] = vectors.crs_wkt
        manifest["official_vector_rows"] = len(vectors)
        for row in vectors:
            if row.geometry is None or row.geometry.type not in ("LineString", "MultiLineString"):
                raise ValueError("Null/non-line fault geometry must be reviewed, not silently discarded")
            geometry = transform_geom(vectors.crs_wkt, crs, dict(row.geometry))
            if geometry_window(geometry, fp.shape, transform, margin=16) is not None:
                records.append(
                    {"system": row.properties["NUM"], "name": row.properties["NAME"], "geometry": geometry}
                )
    groups, geometry, audit = link_systems(cat, records, transform)
    np.save(out / "groups.npy", groups)
    write_json(out / "group-geometry.json", geometry)
    for name in ["groups.npy", "group-geometry.json"]:
        manifest["output_sha256"][name] = sha256(out / name)
    manifest["grouping_audit"] = audit
    with zipfile.ZipFile(source) as z:
        text = next(n for n in z.namelist() if n.lower().endswith(".txt"))
        definitions = z.read(text).decode("utf-8", errors="replace")
        manifest["official_field_definitions"] = definitions
    # Physical transform audit precedes model scores; proxy/NUM ambiguities remain explicit.
    write_json(manifest_path, manifest)
    print(
        f"Prepared six signed-step channels and {audit['whole_groups']} conservative vector-linked groups; "
        f"unlinked proxies={audit['unlinked_proxy_components']}",
        flush=True,
    )
    return manifest


if __name__ == "__main__":
    prepare()

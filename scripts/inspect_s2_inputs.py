"""One INPUT-ONLY hosted diagnostic. NEVER fits a model, scores a label or selects a variant."""

from __future__ import annotations

from pathlib import Path
import platform
import sys
import zipfile

import fiona
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, read_json, sha256, utc_now, write_json  # noqa: E402
from prepare_data import main as prepare_original  # noqa: E402


def differences(before, after, prefix=""):
    if isinstance(before, dict) and isinstance(after, dict):
        return [
            row for key in sorted(set(before) | set(after))
            for row in differences(before.get(key), after.get(key), prefix + "/" + key)
            if key != "generated_utc"
        ]
    return [] if before == after else [{"path":prefix,"first":before,"hosted":after}]


def main():
    data = data_dir()
    error = None
    try:
        prepare_original()
    except ValueError as exc:
        if str(exc) != "Preparation differs from first audit; register a separate protocol":
            raise
        error = str(exc)
    current = read_json(data / "prepared/manifest.json")
    first = read_json(ROOT / "evidence/data-verification.json")
    diff = differences(first,current)
    report = {
        "generated_utc":utc_now(),"kind":"INPUT-ONLY diagnostic; ZERO model fits/scores",
        "original_prepare_error":error,"model_fits":0,"scores_observed":0,"drivendata_requests":0,
        "environment":{"python":platform.python_version(),"platform":platform.platform(),"numpy":np.__version__,"scipy":scipy.__version__,"rasterio_fiona_gdal":fiona.__gdal_version__},
        "manifest_differences":diff,
        "current_preparation_sha256":sha256(data / "prepared/manifest.json"),
        "feature_descriptions":{},
        "frozen_original_preserved":sha256(ROOT / "evidence/data-verification.json"),
    }
    for name in current["base_columns"] + current["candidate_extra_columns"]:
        a = np.load(data / "prepared" / f"{name}.npy",mmap_mode="r")
        report["feature_descriptions"][name] = {
            "minimum":float(np.min(a)),"maximum":float(np.max(a)),"mean":float(np.mean(a,dtype=np.float64)),
            "sha256":sha256(data / "prepared" / f"{name}.npy"),"count":len(a),"finite":bool(np.isfinite(a).all()),
        }
    source=data / "official-s2/qfaults-v2.zip"
    uri="zip://" + str(source)
    layers=fiona.listlayers(uri)
    report["actual_official_zip_layers"]=layers
    report["actual_official_zip_sha256"]=sha256(source)
    with fiona.open(uri,layer=layers[0]) as vectors:
        report["actual_official_schema"]=vectors.schema
        report["actual_official_crs_wkt"]=vectors.crs_wkt
        report["actual_official_rows"]=len(vectors)
        geometry_types={};missing_nums=0;names={}
        for row in vectors:
            kind = row.geometry.type if row.geometry is not None else "NULL"
            geometry_types[kind]=geometry_types.get(kind,0)+1
            num,name=row.properties.get("NUM"),row.properties.get("NAME")
            missing_nums += int(num is None or not str(num).strip())
            if num is not None: names.setdefault(str(num),set()).add(str(name))
        report["actual_geometry_types"]=geometry_types
        report["missing_NUM_rows"]=missing_nums
        report["distinct_nonmissing_NUM"]=len(names)
        report["NUM_name_conflicts"]=sum(len(x)>1 for x in names.values())
    with zipfile.ZipFile(source) as z:
        report["actual_field_definitions"]= {n:z.read(n).decode("utf-8",errors="replace") for n in z.namelist() if n.lower().endswith(".txt")}
    out=ROOT / ".cache/s2-input-only-probe.json"
    write_json(out,report)
    print(f"INPUT-ONLY probe: {len(diff)} manifest differences, zero models, zero scores",flush=True)


if __name__ == "__main__":
    main()

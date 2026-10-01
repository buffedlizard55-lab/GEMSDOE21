"""Hash-pinned, resumable GitHub transport for user-supplied rasters and official derivatives.

No DrivenData requests. A mirror hash verifies transport, NOT organizer provenance.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, sha256, utc_now, write_json  # noqa: E402

BRIDGE = ("buffedlizard55-lab/GEMSDOE", "c0c06ac82178f26b94fce3397036ef8f12a2f3a0")
G7 = ("buffedlizard55-lab/7GEMSDOE", "9d8b5d55b674629f7b0e0e486269917c0fa2dade")
DEM = ("buffedlizard55-lab/GEMSDOE10", "91d6566ecc86141eca9e81c259057678930e596f")
G19 = ("buffedlizard55-lab/19GEMSDOE", "a3aca62fdb2be428f4245e22570cbc54082b2c15")
CORE_HASHES = {
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
    "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
}
G7_FILES = [
    (
        "external/dem/lidar_scarp_features_u8.tif",
        "external/lidar_scarp_features_u8.tif",
        "d580bb8bdcdb941e32fefb8b38044bc5bf04e199bf2e83498c3576e6fc465568",
    ),
    ("external/dem/lidar_scarp_features.json", "external/lidar_scarp_features.json", None),
    (
        "external/geodawn_rad/geodawn_rad_u8.tif",
        "external/geodawn_rad_u8.tif",
        "c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682",
    ),
    ("external/geodawn_rad/geodawn_rad.json", "external/geodawn_rad.json", None),
    (
        "external/geodawn_extensions/geodawn_extensions_u8.tif",
        "external/geodawn_extensions_u8.tif",
        "a35a9c6d2a14786f4dab85481ee59769213072f5dab5b2535ea82ae4d9bb7d9b",
    ),
    ("external/geodawn_extensions/geodawn_extensions.json", "external/geodawn_extensions.json", None),
]
H19_NAME = "gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif"
H19_SHA = "89109a3bd2cd3b12e7a0f388113c519843acfc9c4f46825affefc3e63dd99b22"


def fetch(source: tuple[str, str], remote: str, dest: Path, expected: str | None = None) -> dict:
    repo, ref = source
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Never trust an unversioned local metadata cache when no expected content digest exists.
    # Those small files are refetched at the immutable commit; large hash-pinned rasters can resume.
    cached = expected is not None and dest.is_file() and sha256(dest) == expected
    if not cached:
        tmp = dest.with_name(dest.name + ".partial")
        last_error = ""
        for attempt in range(3):
            with tmp.open("wb") as out:
                result = subprocess.run(
                    [
                        "gh",
                        "api",
                        f"repos/{repo}/contents/{remote}?ref={ref}",
                        "-H",
                        "Accept: application/vnd.github.raw",
                    ],
                    stdout=out,
                    stderr=subprocess.PIPE,
                    timeout=300,
                )
            if result.returncode == 0 and (expected is None or sha256(tmp) == expected):
                tmp.replace(dest)
                break
            last_error = (
                result.stderr.decode(errors="replace")[-500:]
                + f"; received_bytes={tmp.stat().st_size}; received_sha256={sha256(tmp)}"
            )
            # Public, immutable RAW fallback uses no token. Some hosted runners cannot
            # retrieve large raw contents through gh's API route. Identical pinned hash
            # is still required; changing transport never changes scientific inputs.
            if source in (BRIDGE, G7, DEM, G19):
                import requests

                try:
                    with requests.get(
                        f"https://raw.githubusercontent.com/{repo}/{ref}/{remote}",
                        timeout=(10, 90),
                        stream=True,
                        allow_redirects=False,
                    ) as response:
                        response.raise_for_status()
                        if response.status_code != 200:
                            raise ValueError("Public mirror fallback must be a direct HTTP 200")
                        n = 0
                        with tmp.open("wb") as out:
                            for chunk in response.iter_content(1 << 16):
                                n += len(chunk)
                                if n > 128 * (1 << 20):
                                    raise ValueError("Public mirror part exceeds size cap")
                                out.write(chunk)
                    if n > 0 and (expected is None or sha256(tmp) == expected):
                        tmp.replace(dest)
                        break
                    last_error += "; public RAW bytes differ from pinned hash"
                except (requests.RequestException, ValueError) as exc:
                    last_error += f"; public RAW fallback: {str(exc)[:200]}"
            tmp.unlink(missing_ok=True)
            time.sleep(attempt + 1)
        else:
            raise RuntimeError(f"Failed/hash mismatch: {repo}/{remote}; {last_error}")
    actual = sha256(dest)
    if expected is not None and actual != expected:
        raise ValueError(f"SHA mismatch: {dest}")
    return {
        "path": str(dest.relative_to(data_dir())),
        "source_repository": repo,
        "source_commit": ref,
        "source_path": remote,
        "sha256": actual,
        "bytes": dest.stat().st_size,
        "status": "cached-verified" if cached else "fetched-verified",
        "verification_scope": "pinned mirror transport; not an authenticated organizer download",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-only", action="store_true")
    args = parser.parse_args()
    if "GEMS_DATA_DIR" not in os.environ and not (ROOT / "data").exists():
        backing = ROOT / ".cache" / "data"
        backing.mkdir(parents=True, exist_ok=True)
        (ROOT / "data").symlink_to(".cache/data", target_is_directory=True)
    out = data_dir()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    manifest_path = out / "bridge-manifest.json"
    records.append(fetch(BRIDGE, "data/bridge/manifest.json", manifest_path))
    manifest = json.loads(manifest_path.read_text())
    for spec in manifest["files"]:
        dest = out / spec["canonical"]
        want = CORE_HASHES[spec["canonical"]]
        if spec["sha256"] != want:
            raise ValueError("Mirror manifest changed pinned core hash")
        if spec.get("parts"):
            if not dest.exists() or sha256(dest) != want:
                parts = []
                for part in spec["parts"]:
                    p = out / "parts" / part["name"]
                    records.append(fetch(BRIDGE, "data/bridge/" + part["name"], p, part["sha256"]))
                    parts.append(p)
                tmp = dest.with_suffix(".tif.partial")
                with tmp.open("wb") as stream:
                    for part in parts:
                        with part.open("rb") as src:
                            for chunk in iter(lambda: src.read(1 << 20), b""):
                                stream.write(chunk)
                if sha256(tmp) != want:
                    tmp.unlink(missing_ok=True)
                    raise ValueError("Reassembled features SHA mismatch")
                tmp.replace(dest)
                for p in parts:
                    p.unlink()
            records.append(
                {
                    "path": spec["canonical"],
                    "sha256": sha256(dest),
                    "bytes": dest.stat().st_size,
                    "status": "reassembled-verified",
                    "source_repository": BRIDGE[0],
                    "source_commit": BRIDGE[1],
                    "verification_scope": "user-provided transport mirror, not independently official",
                }
            )
        else:
            records.append(fetch(BRIDGE, "data/bridge/" + spec["name"], dest, want))
        print(f"Verified {spec['canonical']}", flush=True)
    if not args.core_only:
        for remote, local, h in G7_FILES:
            records.append(fetch(G7, remote, out / local, h))
            print(f"Verified {local}", flush=True)
        dem_manifest_path = out / "dem10" / "manifest.json"
        records.append(fetch(DEM, "manifest.json", dem_manifest_path))
        dem_manifest = json.loads(dem_manifest_path.read_text())
        if dem_manifest["template_sha256"] != CORE_HASHES["sample_submission.tif"]:
            raise ValueError("DEM vectors use a different template")
        for ch in dem_manifest["channels"]:
            h = dem_manifest["channel_stats"][ch]["sha256"]
            records.append(fetch(DEM, f"{ch}.f32.npy", out / "dem10" / f"{ch}.f32.npy", h))
            print(f"Verified {ch}", flush=True)
        records.append(fetch(G19, f"docs/downloads/{H19_NAME}", out / "historical" / H19_NAME, H19_SHA))
        for name in [
            "gdr_wellspring_in_footprint.csv",
            "external_verification.json",
            "dem1m_tile_audit.json",
            "dem1m_high_prior_openness_lrm.npz",
        ]:
            records.append(fetch(G19, "evidence/ci/" + name, out / "external" / name))
    report = {
        "generated_utc": utc_now(),
        "no_drivendata_access": True,
        "provenance_warning": "Mirrors validate supplied bytes, not organizer-origin authenticity.",
        "files": records,
    }
    write_json(ROOT / "evidence" / "download-verification.json", report)
    print(f"Data ready at {out}. Run python scripts/prepare_data.py", flush=True)


if __name__ == "__main__":
    main()

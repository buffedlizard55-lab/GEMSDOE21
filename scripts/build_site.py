"""Build a download-first, static Pages site from evidence; no invented model score."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
import numpy as np
from PIL import Image
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir  # noqa: E402


def load(path):
    return json.loads((ROOT / path).read_text())


def overview(dest):
    from download_data import H19_NAME

    with rasterio.open(data_dir() / "sample_submission.tif") as s:
        fp = np.isfinite(s.read(1))
    with rasterio.open(data_dir() / "labels.tif") as s:
        known = (s.read(1) > 0) & fp
    with rasterio.open(data_dir() / "historical" / H19_NAME) as s:
        pred = (s.read(1) > 0.5) & fp & ~known
    step = 8
    height, width = (int(np.ceil(n / step)) for n in fp.shape)

    def pool(a):
        padded = np.pad(a, ((0, height * step - a.shape[0]), (0, width * step - a.shape[1])))
        return padded.reshape(height, step, width, step).max(axis=(1, 3))

    rgb = np.full((height, width, 3), [234, 236, 227], dtype=np.uint8)
    rgb[pool(fp)] = [218, 224, 210]
    rgb[pool(known)] = [139, 149, 142]
    rgb[pool(pred)] = [26, 120, 92]
    Image.fromarray(rgb).save(dest)


def main():
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "data").mkdir(exist_ok=True)
    sub = load("evidence/submission-validation.json")
    if not sub["byte_identical_to_h19_4"] or sub["new_submission_recommended"]:
        raise ValueError("This release must remain an honest historical reference")
    result = load("evidence/h21-1-results.json")
    if result["disposition"] != "REJECTED" or result["gate"]["submission_eligible"]:
        raise ValueError("Site language is only valid for the recorded rejected experiment")
    context = {
        "sub": sub,
        "primary": next(f for f in sub["files"] if f["role"] == "primary"),
        "submission_json": json.dumps(sub).replace("<", "\\u003c"),
        "result": result,
        "control": result["summary"]["C21-PU"],
        "candidate": result["summary"]["H21-1"],
        "upstream": load("evidence/upstream-audit.json"),
        "hypotheses": load("registry/hypotheses.json")["candidates"],
        "sources": load("registry/sources.json")["sources"],
        "flags": load("registry/irregularities.json")["flags"],
        "groups": load("registry/group-results.json"),
    }
    context["group_entries"] = sorted(
        context["groups"]["entries"],
        key=lambda e: -(e.get("lb_score") if e.get("lb_score") is not None else -1),
    )
    env = Environment(
        loader=FileSystemLoader(ROOT / "site/templates"),
        autoescape=select_autoescape(),
        undefined=StrictUndefined,
    )
    pages = [
        ("index.html", "index.html", "home", "Download & evidence"),
        ("guide.html", "executive-summary.html", "guide", "Executive submission guide"),
        ("research.html", "research.html", "research", "Registered research"),
        ("sources.html", "sources.html", "sources", "Official source ledger"),
    ]
    for template, dest, page, title in pages:
        html = env.get_template(template).render(**context, page=page, title=title)
        (docs / dest).write_text(html)
        if page == "home":
            # Existing Pages is main / (legacy). This real root entry avoids admin-permission dependency.
            # All assets, files and subpages resolve under docs/; no JS redirect or empty landing page.
            root_html = html.replace(
                '<meta charset="utf-8">', '<meta charset="utf-8">\n  <base href="docs/">', 1
            )
            (ROOT / "index.html").write_text(root_html)
    shutil.copytree(ROOT / "site/assets", docs / "assets", dirs_exist_ok=True)
    overview(docs / "assets/historical-map.png")
    for parent, files in {
        "registry": [
            "sources.json",
            "group-results.json",
            "hypotheses.json",
            "decisions.json",
            "irregularities.json",
            "leaderboard-snapshot.json",
        ],
        "evidence": [
            "h21-1-results.json",
            "data-verification.json",
            "download-verification.json",
            "submission-validation.json",
            "upstream-audit.json",
            "upstream-line-audit.csv",
            "prepared-lineage-audit.json",
            "review-passes.json",
            "request-audit.json",
            "fixed-replication.json",
            "delivery-status.json",
        ],
    }.items():
        for file in files:
            src = ROOT / parent / file
            if not src.exists():
                raise ValueError(f"Missing evidence: {parent}/{file}")
            shutil.copyfile(src, docs / "data" / file)
    for path in (ROOT / ".nojekyll", docs / ".nojekyll"):
        path.touch()
    print("Built 4 static pages + legacy root entry; historical reference only")


if __name__ == "__main__":
    main()

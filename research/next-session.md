# Next session — read the full README brief first

## Outcome to preserve

* Preregistration `2dfc5de`, first implementation `fc809c8`, first-result SHA256 `ee3a52c471720dd5d6692a9fb849d21979111de2c3ecf57d6130f8dab66c6c67`.
* H21-1 **rejected for promotion**: dense ΔDTI −.00140662, sparse ΔDTI −.00104483, recovery −.00172146, FP mass +.03264%; 0/4 dense wins; corrected p=1.0. NW/NE hit fixed 150 iterations. See `research/h21-1-outcome.md` and the unchanged first JSON. No post-result tuning, no weekly slots used.
* Primary download is exact historical H19-4 bytes, renamed `gems21-h19-4-reference-20260930-691e4dfa.tif`, SHA256 `89109a3bd2cd3b12e7a0f388113c519843acfc9c4f46825affefc3e63dd99b22`. It is **not a new model**; do not re-upload a field already scored. Masked-zero/internal-mask fallback and deterministic one-TIFF ZIP have identical footprint predictions; fallback server acceptance is untested.

## Do first, before another hypothesis

1. Recover original H19 arm-generation source/provenance, not merely the full-catalogue cache. Audit all training/calibration/input lineage and refit per fold with whole hidden segments/buffers and corrected exact masking. The pinned H19 snapshot lacks a generator; no .1894-to-local-score substitution.
2. Address post-result emission review F19: the first emitter rank-boosts ridges but fills non-ridges. The separate corrected `strict_emit` helper requires positive physical strength and strict NMS, but has **no model/holdout result**. Register its use on fresh data; never silently swap it into a claimed first-result replication.
3. Strengthen the raster-connected component proxy with original geological vector fault IDs. Registration hides complete raster components, including parts across geographic boundaries; disconnected pieces of one geological system are not independently identified by a binary raster. Purge original trace IDs from all catalogue-derived inputs.
4. Establish separate development and fresh evaluation regions/IDs. The current shared holdout has been observed. Preregister a convergence-safe optimizer protocol using development-only diagnostics before attempting any new inferential test. A repeated fixed run is replication, not a chance to select new parameters.
5. Audit catalogue mapping propensity and class-prior assumptions; .03/SCAR are not verified fault prevalence or calibrated probability. Do not assign unknown pixels negative labels.

## Registered deferred candidates and required data

* **H21-2**: obtain a specific official NHDPlus HR/3DHP flowline product intersecting the actual footprint and raw 3DEP terrain; verify bytes/hash/license/extent. HU codes in the original plan were conditional guesses and must be resolved from official spatial metadata, not assumed. Retired NHD ≠ current hydrologic truth. Reconstruct paired drainage offsets across label-free breaklines.
* **H21-3**: prefer 2026 GeMS SGMC DOI 10.5066/P1A3DQZK; if using legacy NV/CA maps record exact version/scale and uncertainty. Use unit polygons as competing explanation, never full-catalogue fault lines or confident-negative contacts.
* **H21-4**: investigate the USGS P9BZPVUC residual well-point release, GDR1390 conductivity/quality, GDR1391 depth/temperature metadata. Deduplicate site/measurement keys; keep assumed/unmeasured/blank distinct. Current thermal CSV has 27,092 records but only 12,570 distinct 100m cells, no well depth, and prohibited full-catalogue distance columns. No claim that a hot well implies a nearby permeable unknown fault.
* None of these three has a holdout result this session. Check the permitted source feed, then actually download/schema/footprint-validate inputs before calling them viable.

## Reproduce without overwriting history

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
# gh already uses the configured connection; never request/store credentials.
.venv/bin/python scripts/run_pipeline.py
# Same registration/parameters, report goes only to ignored data/research/:
.venv/bin/python scripts/run_pipeline.py --replicate
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_site.py --browser
```

`data/` resolves to ignored `.cache/data/` by default. Large inputs (~419MB feature TIFF plus derivatives/DEM vectors) and OOF masks stay out of Git. Two CPU cores, ~3.8GiB RAM, no GPU/swap; use sequential band processing/chunked inference. First prep and fixed eight fits completed without observed OOM; peak RAM was not measured. This is a CPU nnPU pipeline, not the organizer GPU U-Net.

For local browser checks use Playwright Chromium (`python -m playwright install --with-deps chromium`). Microsoft's CDN was blocked by sandbox TLS policy here; a pinned `@sparticuz/chromium@140.0.0` npm package with its AL2023 shared libraries was used for real Chromium tests. Cache/binary paths are regenerable and not Git artifacts. The exact sandbox fallback used:

```bash
mkdir -p .cache/browser
npm install --prefix .cache/browser --ignore-scripts --no-audit --no-fund @sparticuz/chromium@140.0.0
node -e 'require("./.cache/browser/node_modules/@sparticuz/chromium").executablePath().then(console.log)'
mkdir -p .cache/browser/al2023
node -e 'const fs=require("fs"),z=require("zlib");fs.writeFileSync(".cache/browser/al2023.tar",z.brotliDecompressSync(fs.readFileSync(".cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br")))'
tar -xf .cache/browser/al2023.tar -C .cache/browser/al2023
# check_site detects /tmp/chromium and the packaged libraries automatically.
.venv/bin/python scripts/check_site.py --browser
```

## Publishing, refresh and limitations

* Static site is generated into `docs/`; a real root `index.html` with `<base href="docs/">` preserves existing legacy Pages `main /` configuration without an administrative change. Root and docs `.nojekyll` keep assets/filenames intact. Browser-verified downloads fail closed on byte-length/SHA mismatch; arbitrary TIFFs require Python preflight.
* Daily permitted-source workflow writes JSON into fixed GitHub release `source-feed`, not a bot commit to main. Browser fetches public GitHub release metadata (no secret), with saved snapshot/staleness fallback. Probes check headers/sample bytes, not full external-file validity. Direct sandbox HTTP to USGS/GDR failed despite successful research-reader access; do not label those sources globally unavailable.
* DrivenData Terms prohibit automated monitoring. No authorized API/session, credentials, auto-download or submission was used. Leaderboard is the dated 2026-09-30 snapshot (.3168 leader), not a constantly current feed. An organizer-authorized API would be needed to change that scope, not credentials in chat.
* Download transport hashes do not authenticate organizer provenance; the supplied sample's positive mask equals labels despite its official all-absence description. It supplies grid/footprint only, never positive values to models.
* Strict format validation fixes the new files' numeric/container compliance; the user's exact old file is absent, so the historical range-error cause remains undiagnosed. The finite-zero/null-mask alternative may help a naive reader, but no official acceptance was tested.
* Hidden labels/selection/coverage, prize eligibility, final account allowance and AI-disclosure certification remain unavailable or entrant responsibilities. Fault candidates are not confirmed vents or economic reservoirs.
* PR/merge/deployment/remote CI receipts are recorded in `evidence/delivery-status.json` after verification. Do not equate a planned URL, pushed commit or local test with a successful deployment.

Keep “Maximize P(Win)” and “Own the Outcome” focal: recover the comparison bottleneck, design one distinguishable mechanism, audit alternate explanations, preserve losses, and only then consider a scarce slot.

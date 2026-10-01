# Next session — read the entire README and original brief first

## Current completed state

* H21-1 original rejection unchanged: registration2dfc5de; implementationfc809c8; first SHA **ee3a52c471720dd5d6692a9fb849d21979111de2c3ecf57d6130f8dab66c6c67**. Dense−.00140662, sparse−.00104483, 0/4 wins, two unconverged folds and original soft-NMS deviation. Do not rescue or silently replace it.
* **H21-5 REJECTED FOR PROMOTION**: registration452c21c, implementation48f17c7; sole scientific run [36801939888](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36801939888) at **69fdde6**. Dense+.0000416632 vs+.006 forecast; sparse−.0002134493 vs+.002; recovery+.0000329115 vs+.008; FP+.0089694745% vs−2%; 2/4 dense wins, adjustedp1. Eight fits converged (101–194 iterations, fixed1000 cap/ftol1e−8). Previously observed geography, not fresh confirmation; clean H19 comparison absent.
* Exact first JSON:65,266B, SHA **8979d1b93ba33bfb5fd0712198bc5953b97850baac42572b56a1d384a764e75d**; [release](https://github.com/buffedlizard55-lab/GEMSDOE21/releases/tag/h21-5-first-result) asset digest and byte length match recovered body. The39,344,795B cache archive contains prepared-S2 geometry/features and eight prediction masks, stored outside Git. Use its digest12bbfa3bb18b444e91f82eba6564a5892b275a65e22c8c5c3655a3711d0481b5. Do not rerun to recover unavailable local caches.
* Both results/registrations/full brief/frozen original preparation have history-independent SHA locks. `evaluate_s2.py` refuses existing result/mask paths. Hosted guard refuses a second invocation if result release or published model-start status exists; later blocked jobs cannot erase that status.
* Primary TIFF remains exact historical H19-4: `docs/downloads/gems21-h19-4-reference-20260930-691e4dfa.tif`, SHA **89109a3bd2cd3b12e7a0f388113c519843acfc9c4f46825affefc3e63dd99b22**. Unique note and download-first guide stay prominent. No new qualified artifact or slot; do not re-upload an already scored field.

## Publication resumed — PR #4 pending checks/merge/deployment

GitHub connection is restored. Saved commits through d375c77 were pushed successfully, and [PR #4](https://github.com/buffedlizard55-lab/GEMSDOE21/pull/4) is open. Await checks and merge into main without deleting the session branch. Native Pages completion triggers the owned live verifier, including the scientific JSON/knowledge evidence plus full TIFF/ZIP bytes. Actual new Pages publication/served-byte verification remains pending. Earlier authentication/push failures and historical successful delivery are preserved in `evidence/delivery-status.json`; do not reclassify them as scientific failures or rerun a model for publication.

## Priority 1: comparison and fresh-data bottleneck

1. Recover **original H19 arm-generation source/provenance**, not just its full-catalogue map/cache. Audited public maina3aca62/original PR1a86249 have identical34 Python files; current public branches point to those two commits. Cache reader is obtainable; producer is not. Public shell/workflow also do not reference that cache. This is scoped evidence, not proof no private/untracked generator exists. Old negative targets/full-catalogue collars/sparse defaults cannot be a clean comparator. No .1894-to-local-score substitution.
2. Acquire **genuinely unobserved labels or independent geography** with verified predictors before another confirmatory model. All available in-footprint quadrants were scored in both sessions. NUM grouping, new seeds, repartitioning or greater optimizer caps do not create untouched confirmation. Document external coverage, domain shift and prospective selection before outcomes; no live leaderboard probing.
3. Inspect conditioning/forward-physics using **training/development-only** diagnostics. Three gravity step maxima(.00177,.00808,.00242) are below the nnPU scaling floor.01; that is an unproved explanation for weak influence, not permission to rescale/retest this holdout. Future experiments should persist coefficients/scalers/training diagnostics, currently not saved. No fit to reconstruct them here.
4. Register one new falsifiable mechanism/confounder/effect forecast and **cumulative** multiplicity before implementation. The family is already8 planned hypotheses,2 scored attempts. Compare with both clean control and clean current best; require fresh confirmation before a weekly slot/final full-grid model.

## Original geometry strengthening completed, with honest caveats

Official INGENIOUS v2 ZIP **c7b091c9ac8bca140ad89ee6bb2bd63dd3ac12e3013acbfd8373d11c9faee59d**,6,131,182B, actually retrieved/hash/CRC/Fiona-inspected on hosted runs. NUMstr:6 / NAMEstr:80; NAD83 Albers central meridian−117 WKT. Actual mixed line/multiline geometry accepted, not hardcoded EPSG5070 or centroid approximation.

Within the reference rectangle:3199 raster components →149 conservative NUM/trace groups,154 named IDs link,60988/60988 labels within one-cell matching tolerance,60958 exact overlap. Zero unlinked components, **two unnamed trace-ID groups**,87 rectangle-intersecting records missing NUM, four linked NUM/name conflicts. Whole-archive missingness3508/22956 and39 conflicts is a different population. Full hidden vectors/labels get15px Euclidean training purges everywhere; four actual audits have zero visibility/partial-group/buffer leaks. Vectors/IDs are split metadata only; one-cell matching never changes the exact scoring mask.

**Post-result integer-budget caveat:** SW first pair emits35716/1428627(2.50002275%), one above a literal2.5% maximum due `round()`. Both arms used it; other folds/overall mass are below2.5%. First scores/masks stay locked. Future helper now floors quota with a regression test; use source69fdde6 for first computation, not later helper. No corrected model score was produced. See `evidence/h21-5-protocol-review.json` and `research/h21-5-outcome.md`.

## Deferred input-dependent ideas

* H21-6: independently percentile-quantized uint8 GeoDAWN K/Th/U/TC ranks do not recover physical log ratios; per-channel units/scales/mosaic boundaries must be resolved. `evidence/radiometric-units-s2.json`. No score.
* H21-7: conductivity-sidedness plausible, but cold saline sediments, clay and coarse MT footprint compete. Verify units/resolution and avoid calling conductive-base depth basement or conductivity permeability. No score.
* H21-8: USGS ComCat **100-event historical schema probe succeeded**, not a complete dataset.54 missing horizontal errors,0 missing depth errors; rectangular earliest time-ascending magnitude≥2 query, not irregular-footprint clipped. Need complete frozen-window paging/completeness/type/uncertainty audit and nonunique100m surface projection review. No event-plane model/score.
* Original H21-2/3: exact official NHDPlusHR/3DHP/3DEP and GeMS/SGMC polygons/coverage remain conditional. Do not use full fault lines as predictor or lithologic contacts as confirmed negatives. H21-4 remains blocked by depth/quality/site matching; thermal CSV27092 rows/12570 distinct100m cells has full-catalogue distances and no well depth. Not a model input.

## Rebuild delivery without any scientific test

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/run_pipeline.py --delivery-only
.venv/bin/python scripts/check_knowledge.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_site.py --browser
```

`--delivery-only` never prepares/refits/scores a model; it rebuilds the exact historical files/site. Original full H21-1 replication remains strict and can reject a different platform’s three unused candidate hashes. Do not force those locks. **S2 does not consume those fields:** prefit runs36799921631/36800344273 and input-only run36801268774 isolated exactly three unused SHA differences; all31 consumed base hashes and other metadata match. `prepare_s2_base.py` ignores only their unused SHA fields, never any consumed source/mask/support/value/shape. Separate dated amendments preserve the failure/repair before the first score.

Data/caches live in ignored `data/` (default `.cache/data/`). Direct sandbox GDR TLS, Azure artifacts/logs, release-assets download and uploads.github.com cache upload failed. **Do not repeat those routes** or infer global unavailability. Hosted retrieval/evaluation/publication succeeded; release body/digest metadata is readable locally. Empty release `prepared-h21-original` has no uploaded cache and is explicitly unavailable. Do not call it usable.

Browser dependency: Playwright Chromium. If Microsoft CDN fails, pinned fallback:
```bash
npm install --prefix .cache/browser --ignore-scripts --no-audit --no-fund @sparticuz/chromium@140.0.0
node -e 'require("./.cache/browser/node_modules/@sparticuz/chromium").executablePath().then(console.log)'
mkdir -p .cache/browser/al2023
node -e 'const fs=require("fs"),z=require("zlib");fs.writeFileSync(".cache/browser/al2023.tar",z.brotliDecompressSync(fs.readFileSync(".cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br")))'
tar -xf .cache/browser/al2023.tar -C .cache/browser/al2023
.venv/bin/python scripts/check_site.py --browser
```

## Publication, access and remaining limits

Source/knowledge registries:28 sources,17 typed claims,25 flags,37 historical group rows; no private score/file receipt or universal factual certification. Leaderboard is dated **2026-10-01**(.3168 leader), not a poll. Daily feed checks15 permitted official-data endpoints and21 GitHub heads only; metadata health ≠ usable data/science. No automated DrivenData access/login/upload or credentials requested.

Static docs/root entry respects existing Pages `main /` via `<base href="docs/">`; binary downloads are full-byte/format validated. `evidence/review-passes.json` holds actual three-pass checks; `evidence/delivery-status.json` records PR/merge/deployment receipts. Check latest releases `source-feed` and `delivery-verification` for dated current status. Local screenshots/builds are not proof of live deployment; hosted verifier must fetch served HTML/evidence/TIFF/ZIP and preflight actual bytes.

Unknown original range-error bytes/cause; fallback server acceptance and authentic organizer template provenance remain unverified. Template positive mask equals labels despite described all-absence sample; grid/finite footprint only is used. Hidden expert selection, mapping propensity/SCAR/prior, independence/domain shift, prize eligibility, final allowance and AI disclosure remain limits or entrant obligations. Predictions are fault candidates, not confirmed vents/reservoirs. Keep **Maximize P(Win)** and **Own the Outcome** focal: recover the bottleneck, retain every failed forecast, and only then spend a scarce slot.

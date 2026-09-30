# GEMSDOE21 — audited fault-discovery research & submission hub

**Read this entire README, including the full original user prompt below, at the start of every session.**

## Download the submission TIFF first

**[Download the locally format-verified historical H19-4 TIFF](https://buffedlizard55-lab.github.io/GEMSDOE21/docs/downloads/gems21-h19-4-reference-20260930-691e4dfa.tif)** · [Executive upload guide](https://buffedlizard55-lab.github.io/GEMSDOE21/docs/executive-summary.html) · [Research & evidence hub](https://buffedlizard55-lab.github.io/GEMSDOE21/)

`gems21-h19-4-reference-20260930-691e4dfa.tif` is **byte-identical to H19-4**, the file the user associates with **0.1894**. It is not a newly validated model. **Do not spend a slot re-uploading the same predictions.** The file has 1 float32 band, 3730×3292 shape, EPSG:32611, exact 100m reference geotransform, [0,1] finite values, zero NaN/Inf inside the footprint, and NaN outside. [Local format/hash evidence](evidence/submission-validation.json) is not an official acceptance receipt.

Short note: `GEMS21 | H19-4 historical reference | id 691e4dfa | same predictions, not a new experiment`

The site offers SHA-verified browser downloads, a deterministic one-TIFF ZIP and an **all-finite / internal-null-mask fallback** with identical footprint predictions. Fallback platform acceptance is untested. Exact cause of the user's old range-error file is unknown; the new files are strictly preflighted rather than silently clipped. The final live Pages/build receipt is recorded separately; a planned URL alone is not deployment evidence.

## Own the Outcome · Maximize P(Win)

**Maximize P(Win):** build a reproducible geological research program, not a leaderboard-probing machine. Name the mechanism and non-fault confounders, register forecasts before scores, hide whole known segments with purges, use positive–unlabeled risk and the exact official metric, and retain negative results. No score or prize guarantee.

**Own the Outcome:** complete authorized data placement, CPU training/inference, validation, reference delivery and a usable site; execute three real review passes; flag defects and genuine access limits. Protect submission budget. One research program/account; no multi-account evasion. Keep source/knowledge/decision registries reusable for expert review.

## What actually ran

* Initial checkout had an 11-byte README and **no** pipeline, site, tests or previous-session next-step notes. The prompt's inherited “GPU pipeline ready; only data placement missing” did not describe this checkout.
* Preregistration committed/pushed **`2dfc5de` before implementation/results**. First implementation/test commit **`fc809c8` before results**. Four hypotheses were ranked, not selected by the live leaderboard.
* Pinned transport downloaded and verified core rasters, physical derivatives and 13 DEM channels. Direct authenticated organizer provenance is not verified. The supplied template positive mask equals the known catalogue despite the official all-absence description; only its grid/finite footprint is used.
* Preparation produced 31 label-free control + 3 candidate channels; 5,167,373 footprint pixels, 60,988 known pixels. Global whole 8-connected components are hidden with 1.5km Euclidean training purges. This is a segment proxy, not verified original geological fault IDs.
* First CPU nnPU experiment: **H21-1 REJECTED for promotion**. Mean dense DTI **0.199205→0.197798 (−.00140662)**; sparse-reference **0.075496→0.074451 (−.00104483)**. Recovery fell; FP mass rose .03264%; 0/4 dense wins; family-corrected p=1.0. NW/NE both hit the fixed optimizer cap.
* Second-pass review found the original emitter **soft-prioritizes NMS, rather than restricting to ridges**, and its evidence mask is data support rather than an explicit positive-amplitude guard. Therefore those numbers are a failed implementation attempt, not a fully compliant confirmatory strict-NMS test. A separate corrected helper is unit-tested but **not** activated/retested on this observed holdout. [Protocol review](research/protocol-review.md).
* Independent re-preparation reproduced all feature hashes. Fixed-parameter replication of the **original** implementation reproduced exact summaries/gates/block test/prediction masks, without changing the first result. [Replication evidence](evidence/fixed-replication.json). No tuning or weekly slots used.
* Local checks: **57 tests passed**, static hash/grid/link audit passed, real Chromium desktop/mobile/file/clipboard/failure/no-JS checks passed. Three-pass details and original-request coverage: [review record](evidence/review-passes.json), [request audit](evidence/request-audit.json).

First outcome and expert-review rationale: [research/h21-1-outcome.md](research/h21-1-outcome.md), [raw JSON](evidence/h21-1-results.json). The primary outcome SHA is `ee3a52c471720dd5d6692a9fb849d21979111de2c3ecf57d6130f8dab66c6c67`. Never overwrite it to rescue a forecast.

## H19-4 audit: what changed, what is not established

H19-4 is scarp-dominant: L3+L4 have 92% of lidar-regime and 85.6% of gap-regime pre-gate weight. L4 is not a pure independent geophysics measurement. The second-best gate attenuates to 35%, not hard rejection. H19 vs H16 has **20,153 added / 20,313 removed** scored selected pixels and **71.92% Jaccard**. This documents a changed map, **not causal attribution** of the reported +.0039 hidden-score difference.

The pinned H19 exporter requires an untracked OOF arm cache; an all-committed-Python search found readers but no generator. Old sampling assigns unknown pixels negative targets and derives a collar from the full catalogue; sparse masking defaults differ. **Current-best clean comparison is blocked.** A historical full-catalogue map or .1894 score cannot substitute. [Source-line audit](evidence/upstream-line-audit.csv) · [computed audit](evidence/upstream-audit.json).

[Group registry](registry/group-results.json) preserves the prompt's reported scores and blanks, separately audits 29 artifact identities, and exposes exact scored-confidence duplicates (GEMSDOE/5/8/17-A; 12 NaN/all-finite). Filename suffixes alone are not proof of equality. GEMSDOE14's referenced artifact has the wrong origin; its reported score is not an authenticated file receipt.

## Locked ranked research plan

[Immutable registration](research/preregistration-h21.md) — mechanisms, confounders, transforms, fixed parameters and four-member correction:

| Rank | Hypothesis | Expected local ΔDTI, not hidden-score forecast | Cost / disposition |
|---|---|---:|---|
| 1 | H21-1 co-oriented, scale-persistent gravity/RTP edges | +.008 dense / +.004 sparse | Low–medium; first attempt rejected; emission review above |
| 2 | H21-2 repeated drainage offsets across label-free scarps | +.005 | High; exact official hydrography/terrain retrieval and coverage required |
| 3 | H21-3 unit-interior versus lithologic-contact context | +.004 | Medium; exact GeMS/SGMC polygon version/extent required |
| 4 | H21-4 depth/conduction-corrected thermal residual | +.003 | Medium–high; missing depth/quality matching blocks viability |

External-dependent ideas remain **conditional/untested**, not viable just because a landing page exists. Source registry names the specific free official USGS/GDR resources and their limitations. Thermal CSV has 27,092 records but only 12,570 distinct 100m cells; it lacks well depth and contains prohibited full-catalogue distances. It was not a model input. No thermal anomaly alone proves a new fault or a reservoir.

## Exact scoring and qualified sources

`DTI = TP_w / (TP_w + .2 FP_w + .8 FN_w + epsilon)` uses the maximum probability×300m triangular kernel, not convolution. Remove known pixels from predictions **and truth before all terms**, pixel-exactly, with no scoring buffer or wrong-label credit. Unlabelled is not confirmed negative; official FP mass is the penalty against an incomplete reference, not geological proof of absence.

* [Official task/math/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
* [Staff exact known mask](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4)
* [Staff undisclosed new-label selection](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7)
* [Official rules, reproducibility, AI-use disclosure](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
* [22 qualified source records](registry/sources.json) · [19 irregularities](registry/irregularities.json) · [all rejected/deferred decisions](registry/decisions.json)

Inspected public snapshot on **2026-09-30**: DARD .3168, smrtdoog5 .1894, extradr19 .1855. [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). Account best does not identify a file; prompt file-score associations remain **USER-REPORTED**. .3049 from the brief is older. This snapshot is **not a live feed**.

[Terms](https://www.drivendata.org/termsofuse/) prohibit automatic website monitoring; no authorized DrivenData API/session is established. No code polls/signs into/uploads to DrivenData. A daily permitted-source workflow instead refreshes USGS/DOE transport health and GitHub heads, publishing JSON in fixed release `source-feed` without bot pushes to main. The site reads public release metadata, dates/stale-marks it and falls back safely to a saved snapshot. Probes establish response/sample-byte health, **not** full-file coverage/licensing/geological validity. Direct sandbox TLS to official data hosts failed despite research-reader access; do not call that global unavailability.

## Reproduce end to end

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/run_pipeline.py
# Repeat SAME registered original implementation, never replace first outcome:
.venv/bin/python scripts/run_pipeline.py --replicate
.venv/bin/python scripts/validate_submission.py path/to/prediction.tif
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_site.py --browser
```

The wrapper downloads pinned authorized GitHub transport, prepares if needed, verifies independent lineage, preserves or explicitly replicates the locked experiment, audits upstream/group artifacts, emits compliant historical files and builds/checks the site. Large data/OOF masks live in ignored `data/` (default `.cache/data/` symlink). Two CPU cores/~3.8GiB RAM/no GPU: sequential preparation and chunked inference completed; peak RAM was not measured. No organizer GPU U-Net is claimed trained.

Browser setup: `.venv/bin/python -m playwright install --with-deps chromium`. This sandbox's Microsoft CDN TLS was blocked; real Chromium tests used pinned `@sparticuz/chromium@140.0.0` with its packaged libraries. See the handoff for regenerable setup. The static site works without a browser dependency or JavaScript; arbitrary TIFF validation remains Python fail-closed.

## Limitations and next-session priority

**No new validated score improvement or top-prize guarantee.** Recover/audit H19 arm generation, get original vector fault IDs, and lock fresh development/test/convergence/strict-emission protocols before another candidate. Establish exact external-byte/schema/coverage provenance; retain this failed forecast and all confounders for Phase 2. No reused shared-holdout tuning.

Final submission/eligibility/slot availability and AI-disclosure certification require the entrant's own authorized account; no credentials are requested. The all-finite fallback's server acceptance and the old range-error cause are not verified. Hidden labels/selection/coverage and private score are unavailable. Competition targets fault candidates, not confirmed vents or drillable reservoirs.

[Next-session handoff](research/next-session.md) · [PR/merge/deployment receipt](evidence/delivery-status.json). The final remote receipt must be verified after merge; local tests or a planned URL are not proof of deployment.

## Full original user prompt (verbatim session brief)

<details>
<summary>Read the entire request before every session. This is a specification and historical/user-reported information, not independent evidence.</summary>

```text
Review the repo. 

There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.

Research and Discovery Standard (read first, every session): Treat this as a research program, not a leaderboard-probing exercise — the two produce different behavior even at the same submission budget. Before writing any code, state a specific, falsifiable geological hypothesis: name the physical mechanism a signature should indicate, name at least one non-fault process that produces the same pattern, and write down the predicted direction and rough size of the score change before testing it. Validate exclusively on a hide-and-recover holdout that withholds whole known fault segments (with a buffer) from every input the model sees and mirrors the organizer-confirmed scoring behavior exactly — pixel-exact masking of known faults, no credit for a near-miss against the wrong label. Because the competition's entire premise is that the training catalogue is incomplete, treat every unlabeled pixel as unlabeled, not confirmed-negative, and train and score accordingly, rather than optimizing against the false assumption that "absent from the training raster" means "no fault." Decompose the actual metric — a 0.2/0.8-weighted precision–recall trade, from the official definition — and test each candidate against that decomposition, not against how convincing the map looks. Once several hypotheses are running against the same holdout, pre-register each one's predicted effect before looking and correct for testing multiple candidates at once; the improvement that survives is the one that beat a documented prediction, not the best of an uncorrected batch. Log every rejected hypothesis and why — a negative result narrows the next one and is worth writing down for Phase 2's expert reviewers, who read the reasoning behind a flagged fault, not just the pixel mask. All of this runs inside our one repo, on our one account, against our own holdout: a score bought by testing more variants against the live leaderboard instead of a real holdout isn't a result, it's the same uncorrected-comparisons error this whole standard exists to catch.

Here are the results from our groups submissions, separated by ....:

GEMSDOE1

[https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html)

GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/6GEMSDOE/](https://buffedlizard55-lab.github.io/6GEMSDOE/)

6GEMSDOE SCORE: 0.0286

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1193

1 · SUBMIT FIRST

f347b70daa

Pindrop nodes

....

GEMSDOE2

[https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html)

GEMSDOE2 SCORE: 0.1560

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.0830

2 · SUBMIT SECOND37f9d5b855

Pindrop catalogue-gap target SECOND SYSTEM

....

[https://buffedlizard55-lab.github.io/GEMSDOE4/](https://buffedlizard55-lab.github.io/GEMSDOE4/)

GEMSDOE 4 SCORE: 0.0343

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1152

3 · CONTROL · UPLOAD LAST

4e03fc9705

Pindrop dense ridge control

....

[https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)

5GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/7GEMSDOE/](https://buffedlizard55-lab.github.io/7GEMSDOE/)

7GEMSDOE SCORE: 0.1461

....

[https://buffedlizard55-lab.github.io/8GEMSDOE/](https://buffedlizard55-lab.github.io/8GEMSDOE/)

8GEMSDOESCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html)

9GEMSDOE SCORE: 0.0107

....

[https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html)

11GEMSDOE SCORE: 0.0202

....

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62_allfinite

SDCF9

....

[https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html)

15GEMSDOE SCORE: 0.0782

gems-tso1-20260929T005627Z-conj_alteration_mag

smashi34

....

[https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html)

14GEMSDOE SCORE: 0.0020

smrtdoog5

....

[https://buffedlizard55-lab.github.io/GEMSDOE10/](https://buffedlizard55-lab.github.io/GEMSDOE10/)

10GEMSDOE SCORE:

h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461

h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921

H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280

h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 

wbg1

....

[https://buffedlizard55-lab.github.io/13GEMSDOE/](https://buffedlizard55-lab.github.io/13GEMSDOE/)

13GEMSDOE SCORE:

....

[https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html)

16GEMSDOE SCORE:

h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855

h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 

h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 

extradr19

....

[https://buffedlizard55-lab.github.io/17GEMSDOE/](https://buffedlizard55-lab.github.io/17GEMSDOE/)

17GEMSDOE SCORE:0.0187

17GEMSDOE_F-ensemble-2pct_20260930T050626Z

....

[https://buffedlizard55-lab.github.io/18GEMSDOE/](https://buffedlizard55-lab.github.io/18GEMSDOE/)

18GEMSDOE SCORE: 0.0297

....

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 

....

20GEMSDOE SCORE:

....

21GEMSDOE SCORE:

....

22GEMSDOE SCORE:

....

23GEMSDOE SCORE:

....

24GEMSDOE SCORE:

....

25GEMSDOE SCORE:

....

26GEMSDOE SCORE:

....

27GEMSDOE SCORE:

....

HIGHEST SCORE SO FAR IS THE FOLLOWING

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to study the highest score we have achieved so far which is 19GEMSDOE.

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.1855?  

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to quickly look at the results and our results.

We have a good understanding of how our hypothesis, methodology, calculations, analysis are done so we should be able to figure out a way to score higher on the leaderboard using previous results and scoring that we have across the sites listed above.  We need to come up with distinct and unique strategies to score higher in this competition leaderboard.  We need to start doing heavy and deep research into the part of the project that matters the most, which is the scientific discovery of geothermal vents.  We should store all of our information and knowledge that we can gather from official verified sources.  This will serve as a starting point for other projects as well.  We need to think outside the box but still be grounded in proper scientific research, we are ultimately aiming for a top prize that many others are competing for.  So it's important to be contrarian but be smart about it.  We need to find sources of data that others are over looking or areas of the project when it comes to geothermal vents.  We need to do deep research and critical thinking and come up with new hypothesis to test.

Use these sites as a starting point for understanding how our group has generated submissions in the past.  

GEMSDOE1

[https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html)

GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/6GEMSDOE/](https://buffedlizard55-lab.github.io/6GEMSDOE/)

6GEMSDOE SCORE: 0.0286

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1193

1 · SUBMIT FIRST

f347b70daa

Pindrop nodes

....

GEMSDOE2

[https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html)

GEMSDOE2 SCORE: 0.1560

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.0830

2 · SUBMIT SECOND37f9d5b855

Pindrop catalogue-gap target SECOND SYSTEM

....

[https://buffedlizard55-lab.github.io/GEMSDOE4/](https://buffedlizard55-lab.github.io/GEMSDOE4/)

GEMSDOE 4 SCORE: 0.0343

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1152

3 · CONTROL · UPLOAD LAST

4e03fc9705

Pindrop dense ridge control

....

[https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)

5GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/7GEMSDOE/](https://buffedlizard55-lab.github.io/7GEMSDOE/)

7GEMSDOE SCORE: 0.1461

....

[https://buffedlizard55-lab.github.io/8GEMSDOE/](https://buffedlizard55-lab.github.io/8GEMSDOE/)

8GEMSDOESCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html)

9GEMSDOE SCORE: 0.0107

....

[https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html)

11GEMSDOE SCORE: 0.0202

....

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62_allfinite

SDCF9

....

[https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html)

15GEMSDOE SCORE: 0.0782

gems-tso1-20260929T005627Z-conj_alteration_mag

smashi34

....

[https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html)

14GEMSDOE SCORE: 0.0020

smrtdoog5

....

[https://buffedlizard55-lab.github.io/GEMSDOE10/](https://buffedlizard55-lab.github.io/GEMSDOE10/)

10GEMSDOE SCORE:

h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461

h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921

H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280

h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 

wbg1

....

[https://buffedlizard55-lab.github.io/13GEMSDOE/](https://buffedlizard55-lab.github.io/13GEMSDOE/)

13GEMSDOE SCORE:

....

[https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html)

16GEMSDOE SCORE:

h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855

h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 

h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 

extradr19

....

[https://buffedlizard55-lab.github.io/17GEMSDOE/](https://buffedlizard55-lab.github.io/17GEMSDOE/)

17GEMSDOE SCORE:0.0187

17GEMSDOE_F-ensemble-2pct_20260930T050626Z

....

[https://buffedlizard55-lab.github.io/18GEMSDOE/](https://buffedlizard55-lab.github.io/18GEMSDOE/)

18GEMSDOE SCORE: 0.0297

....

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 

....

20GEMSDOE SCORE:

....

21GEMSDOE SCORE:

....

22GEMSDOE SCORE:

....

23GEMSDOE SCORE:

....

24GEMSDOE SCORE:

....

25GEMSDOE SCORE:

....

26GEMSDOE SCORE:

....

27GEMSDOE SCORE:

....

HIGHEST SCORE SO FAR IS THE FOLLOWING

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to study the highest score we have achieved so far which is 19GEMSDOE.

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.1855?  

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

0.3049	is the highest score right now so we need to design a new strategy, research, testing, analyzing, and generating submission system than the current website.  It should be unique, take unique approaches to generating a submission that can score higher than .3049.  

Put this prompt into the repo readme and read it everytime we work on the project as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use.  It should solve the problem of having to manually check everything ourselves and having an up to date current feed.

Review the repo. 

The following is taken from the Arena AI team and I think it makes a good point on building a successful project, so let's keep the Core Values and Own the Outcome as a focal point when building, developing, researching, suggesting upgrades, and implementing the work.

Our Core Values

Maximize P(Win)

“Maximize the Probability of Winning”: our decision making framework. In every decision, we weigh tradeoffs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside our emotions and make tough decisions in order to maximize P(Win). “Maximize P(Win)” frees us from constraints and clarifies that we must put Arena first.

Own the Outcome

We own results end to end — not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

We need to focus on being able to generate a submission into the competition.  

The site should be able to generate a TIF file that is required for submission.  It should be as easy as download to click a File to submit into the competition.  This needs to be in the executive summary or the very beginning of the site.  it should be obvious when you visit the site.

I tried to submit the document that i downloaded from the site but it returned this error on the submission form:

"Predicted values must be in range [0, 1]"

Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Here is the submission page when i click submit file

New submission

File to submitNo file chosen

You can submit a single-band GeoTIFF (.tif) file, or a .zip file containing a single GeoTIFF, with your predictions. It must match the submission format's CRS, shape, and geotransform. You may wish to review the competition rules first.

Note (optional)

A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Create a executive summary subpage that explains exactly how to make a submission into the contest.

Work on the next steps from the previous sessions first.

The goal of this project is to place top of the leaderboard in this competition.  The following is the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

We need to create a project that can compete and place top of the leaderboard.  We need to understand the problem, collect all the data and organize it into a clean easily auditable table with official verified links for manual verification.  

This is the guidelines we need to follow.[https://www.drivendata.org/competitions/306/competition-doe-gems/](https://www.drivendata.org/competitions/306/competition-doe-gems/)

Get familiar with the problem through the overview and problem description,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). You might also want to reference additional resources available on the about page,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/).

Download the data from the data,[https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), tab.  

Create and train your own model. This reference solution,[https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) implements a simple approach.

Use your model to generate predictions that match the submission format.

Tell me what are you limitations and what you need access to during this project.  We will need to find free publicly available sources and data from official and verified sources if we are to use 3rd party or external data.  

this pdf outlines how submissions must be entered into the competition.  

[https://docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

You must be able to do your own research, deep research, scientific literature research and organize the knowledge so that we can critically think through the problem and generate a solution through scientific and free publicly available information.  this must be done autonomously and must be constantly reviewed and improved upon.  Provide suggestions and improvements and implement them.

❌ No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (verified redirect to login)

See below for links from the above site.  See attached files for links from the above site.

[https://gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391)

Download competition data from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (requires login) to data/

See links below for competition data:

[https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&amp;st=wz4kofki&amp;dl=0](https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&st=wz4kofki&dl=0)

[https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&amp;st=8junzdyw&amp;dl=0](https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&st=8junzdyw&dl=0)

[https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&amp;st=rnino7ya&amp;dl=0](https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&st=rnino7ya&dl=0)

[https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&amp;st=zj1lag1r&amp;dl=0](https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&st=zj1lag1r&dl=0)

[https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&amp;st=srhhir10&amp;dl=0](https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&st=srhhir10&dl=0)

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Site creation

Create a github page for this repo that has clean ui, user friendly, simple and easy to use.  It should be organized and clean.  

It should include all relevant information in an easy to read format with official verified links as sources for review.  Work line by line verify everything no hallucinations.

**The single remaining blocker to training is data placement**: run `bash scripts/download_competition_data.sh` on any unrestricted machine into `data/`, then `python scripts/prepare_data.py` — after that the full train→inference→validate pipeline is ready to run (GPU needed for training; metric/losses/validation all verified working here on CPU).

you need to complete the above task by yourself.  Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Run this task through multiple passes.

Pass 1: Implement the task completely and verify the result.

Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases. Fix everything you find.

Pass 3: Re-check the entire implementation against the original request. Improve accuracy, reliability, completeness, and code quality. Fix any remaining issues.

Do not stop after the first pass. Each pass must build on the previous one. Before finishing, verify that the final result fully satisfies the original request.  Work line by line verify everything no hallucinations.

Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project.  It should be worked on in this next session or the next session.  Work line by line verify everything no hallucinations.
```

</details>

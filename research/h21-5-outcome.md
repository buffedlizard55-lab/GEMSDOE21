# H21-5 first outcome — rejected for promotion

2026-10-01. Registration [452c21c](https://github.com/buffedlizard55-lab/GEMSDOE21/commit/452c21c) preceded implementation [48f17c7](https://github.com/buffedlizard55-lab/GEMSDOE21/commit/48f17c7). The sole scientific run [36801939888](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36801939888) used **69fdde6** after two **prefit** setup failures and an input-only diagnostic. No optimizer/feature/budget variant was selected from scores; no weekly slot was spent.

First result: `evidence/h21-5-results.json`, **65,266 bytes**, SHA256 **8979d1b93ba33bfb5fd0712198bc5953b97850baac42572b56a1d384a764e75d**. Canonically recovered GitHub release-body bytes match the uploaded asset’s size and SHA256 exactly. [Immutable first-result release](https://github.com/buffedlizard55-lab/GEMSDOE21/releases/tag/h21-5-first-result) also retains the ignored 39,344,795-byte scientific cache/mask archive. Binary archive access from the sandbox is blocked, not global source unavailability. See `evidence/h21-5-recovery-receipt.json`.

## Forecast versus observation

| Quantity | Preregistered forecast | First observation | Verdict |
|---|---:|---:|---|
| Mean dense DTI | +.006 | .1947428073 → .1947844706, Δ **+.0000416632** | Miss |
| Mean sparse-reference DTI | +.002 | .0965993835 → .0963859342, Δ **−.0002134493** | Wrong direction |
| Pooled weighted recovery | +.008 | Δ **+.0000329115** | Miss |
| FP mass, relative | −2% | **+.0089694745%** | Wrong direction |
| Dense fold wins | ≥3/4 | **2/4** | Fail |
| Eight-family adjusted block p | <.05 | **1.0**, raw .71923828125, 11 truth-containing blocks | Fail; exploratory only |
| Fit convergence | All | **8/8**, 101–194 iterations, fixed cap1000/ftol1e−8 | Pass |
| Clean current-best / fresh confirmation | Required | **False / false** | Blocks promotion independently |

The four-quadrant raw diagnostic p=.375. Mean block Δ is −.0003059768; mean quadrant Δ is +.0000416632. These summaries weight different units and are not contradictory. Adjacent blocks are correlated and the geography was observed in H21-1; neither p-value is fresh confirmation. No absolute cross-session score comparison or .1894-to-local-score substitution is valid.

## Actual official metric decomposition, dense totals

| Term | C21-S2-PU | H21-5 | Change |
|---|---:|---:|---:|
| TP_w | 14235.852684 | 14237.859888 | +2.007204 |
| FP_w | 115575.529423 | 115585.895941 | +10.366518 |
| FN_w | 46752.147316 | 46750.140112 | −2.007204 |
| .2 FP_w | 23115.105885 | 23117.179188 | +2.073304 |
| .8 FN_w | 37401.717853 | 37400.112090 | −1.605763 |

Both arms emit 129,184 pixels. The tiny gain is not useful forecast-beating recovery. FP remains unverified mass against an incomplete reference, not confirmed geological absence. The same predictions were used for both reference scenarios. Exact known pixels were removed before all distances/terms; no wrong-known-label proximity credit. All 16 owned blocks retain full originating-fold kernel context, and their components conserve fold totals.

## Input and whole-group audit

* Raw core/source hashes, all **31 consumed** original control hashes, mask and support hashes verified before scoring. Candidate adds exactly six registered label-free step channels. Class-prior .03/SCAR remain assumptions; no confirmed-negative targets or holdout calibration.
* The official source ZIP was actually hash/CRC/schema inspected, not inferred obtainable from a landing page. Its actual NUM field definitions include fault/fold sections. 3,199 raster components became **149 conservative groups**; 154 named NUM values link to catalogue, with unions for shared components.
* All 60,988 catalogue pixels link within one cell; 60,958 have exact vector overlap. One-cell linkage is **not** a scoring mask or exemption.
* **Zero unlinked component proxies** does not mean zero identity uncertainty: two linked groups use explicitly unnamed source-trace IDs; 87 rectangle-intersecting records have missing NUM, and four linked NUMs have name conflicts. Whole-archive missingness is different: 3,508/22,956 rows, 39 conflicts. Do not conflate these populations.
* Whole hidden groups and full source geometry receive 15px Euclidean training purges everywhere, including disconnected/out-of-quadrant parts. Four actual fold audits show zero hidden label visibility, partially visible groups or training pixels inside hidden geometry buffers.
* The original 34-channel preparation guard is preserved. Input-only run36801268774 isolated exactly three discarded H21-1 hashes; they are not read by either S2 model. The actual 31 consumed hashes were not relaxed or replaced. See the separate pre-score amendments and genuine prefit failure.

## Pass-2 caveat and repair — do not rewrite the first outcome

The registered wording specifies a literal **maximum** 2.5% budget, but the first helper used integer `round()`. SW emits35,716 pixels in1,428,627 domain cells (**2.50002275%**), one above floor35,715, in **both** arms. Other folds and overall mass are below2.5%. This is a minor protocol deviation, not fully literal-budget compliance. The forecasts already fail and no promotion is allowed.

`evidence/h21-5-protocol-review.json` preserves this independent post-result audit. The helper now uses `floor()` for **future registered experiments only**, with a synthetic regression test. **No new fit, score, first-result replacement or mask regeneration** was performed. To inspect first masks, use the release and code snapshot69fdde6, not the later helper. H21-1’s original rejection also remains unchanged.

## Expert-review interpretation and next step

The physical density/magnetic juxtaposition mechanism remains plausible; this particular signed-profile/model combination did **not** establish additional useful recovery. Contacts, intrusion boundaries, basin margins and seams remain non-fault explanations. Small improvement cannot be attributed to a true missing fault or predicted hidden score.

Source maxima for all three gravity channels are below the nnPU robust scaling floor .01. This may attenuate their influence, but it is an **unproved conditioning explanation**, not a post-hoc causal diagnosis or permission to rescale on the same holdout. Coefficients/scalers were not persisted; future registered experiments should save them. No rerun to recover them is authorized here.

Prioritize original H19 producer/provenance and genuinely unobserved labels/geography. Do not rename or repartition the already scored footprint as fresh confirmation. Only development-only conditioning/physical forward checks may motivate a new preregistration. Keep H21-6/7/8 untested; the limited ComCat and quantized radiometric products do not make them fully viable. Primary TIFF remains byte-identical historical H19-4; **do not re-upload it** or publish H21-5 as an improved competition entry.

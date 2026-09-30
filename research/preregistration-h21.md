# H21 registration — locked before implementation and results

Registered: 2026-09-30 UTC. Starting commit: ad4b3b9bd55b90c40bdb8959fbb1f2391387503c.
Registration is immutable after the first evaluation. Protocol corrections must be separate, dated amendments with a new experiment identifier; never silently replace a result.

## Findings established by reading, not by a new experiment

This repository initially has only README.md (`# GEMSDOE21`). The source snapshot of 19GEMSDOE is main @ a3aca62fdb2be428f4245e22570cbc54082b2c15. Its exported H19-4 field is available, but its H19 out-of-fold cache is not committed and no script in that snapshot generates `oof_probs_h19_arms.npz`. Its training code uses binary-negative targets on sampled uncatalogued pixels, and its sparse scoring default does not remove masked catalogue predictions before distance calculation. Those scores cannot be assumed comparable to a corrected holdout. We will not validate its fixed submission against faults that trained it.

The account-best public leaderboard snapshot (research read on 2026-09-30) has DARD .3168, smrtdoog5 .1894 and extradr19 .1855. Account-best scores do not identify files. The H19-4-to-.1894 association is USER-REPORTED. No leaderboard result will be used to tune a parameter or select a variant.

## Ranked hypotheses (four-member family, FWER .05)

### 1. H21-1: cross-field co-orientation with scale persistence (top candidate)

* Mechanism: fault displacement juxtaposes blocks with differing density and magnetic properties. Buried/low-relief continuations may leave coincident, parallel gradient normals in isostatic gravity and RTP magnetics even where regional surface mapping missed a trace.
* Layers: competition `rtp` (band 2) and `iso_grav_anom` (band 13), with existing 1m 3DEP scarp summaries, 10m 3DEP one-sided/curvature summaries, detrended elevation, and conductivity as the clean control features. No fault distance, known-map coordinate or held-out label input.
* New signature: at Gaussian sigma=1 and 3 competition pixels, normalized gradients with axial agreement A=(grad_m dot grad_g)^2/(|grad_m|^2 |grad_g|^2). Combine A with within-field cross-scale axial persistence and log1p gradient amplitudes. Minimum valid smoothing support=.99. Add the sigma=1 and sigma=3 joint features and their geometric mean; never treat a direction with zero amplitude as agreement.
* Difference: upstream H16/H19 combines gradient magnitudes and maximum multi-azimuth worms, including sqrt(mag_worm*grav_worm); it does not compute this cross-field axial-direction agreement or cross-scale persistence. Novel relative to inspected code, not a claim of worldwide novelty.
* Non-fault explanations: lithologic/intrusive contacts, lava-flow boundaries, and interpolation/survey seams can align gravity and magnetic gradients. Correlated geological layers are not four statistically independent measurements. This is evidence for testing, not proof of a fault.
* Prediction BEFORE testing: mean dense hide/recover DTI +.008 (plausible .003–.015); weighted recovery +.015 absolute; unverified FP mass -3% relative at identical 2.5% emission budget. Sparse-reference DTI expected +.004 (plausible .001–.008). None are predictions of hidden leaderboard score.
* Cost: low–medium, CPU-only, no new external data beyond already published derivatives. Test exactly ONE fixed implementation, not a sweep.

### 2. H21-2: repeated drainage-offset geometry

* Layers: raw USGS 3DEP 1m/10m terrain and USGS NHDPlus HR flowlines (HU4 1604/1605 as appropriate to footprint, confirm extent before processing).
* Signature: project at least three channel crossings onto a terrain breakline and test consistency of lateral offset sign/size upstream versus downstream; distinguish throughgoing offset from a ridge along a single channel. Do not use catalogue traces to propose a held-out breakline.
* Missing faults: small intrabasin strike-slip strands may offset drainage without producing tall range-front scarps.
* Difference: upstream tectonic/fluvial amplitude ratios do not reconstruct and pair drainage networks.
* Confounders: fan avulsion, stream capture, agricultural ditches, inaccurate hydrography. NHD retirement means historical coverage is not a live hydrologic truth.
* Prediction: +.005 DTI (.001–.012), recovery +.010; FP mass roughly unchanged. High cost. Not tested this session.
* Specific free official source: USGS https://www.usgs.gov/national-hydrography/access-national-hydrography-products and staged NHDPlusHR VPU/current products at https://prd-tnm.s3.amazonaws.com/. Viability CONDITIONAL on logged successful product availability/extent checks, not merely a landing page.

### 3. H21-3: lithology-conditioned contact discrimination

* Layers: same potential fields/terrain plus SGMC/GeMS Nevada and California unit POLYGONS, not fault lines. Official DOI https://doi.org/10.5066/P1A3DQZK (2026 release preferred); legacy state files https://mrdata.usgs.gov/geology/state/.
* Signature: field edges that cut the interior of a unit and cohere with a scarp versus edges following a unit boundary. Use contextual features, not a hard exclusion or a negative label. Spatial uncertainty matters: coarse maps cannot locate 100m faults precisely.
* Missing faults: weak breaks inside broad alluvial units may be overlooked by regional catalogues; pure lithologic boundaries explain some non-fault edges.
* Difference: upstream SGMC work rasterizes fault lines; this uses unit identity/contact geometry as an alternative explanation.
* Confounders: mapped contacts can be faulted, unit polygons can be wrong or too coarse, and unmapped lithologic contacts may cross units.
* Prediction: +.004 DTI (.000–.010); recovery no worse than -.003, FP mass -5%. Medium cost. Not tested this session. Viability CONDITIONAL on actual version/file retrieval and metadata review.

### 4. H21-4: depth-corrected advective thermal residual

* Layers: INGENIOUS GDR1391 well/spring temperature, silica/cation geothermometers, WELL DEPTH and measurement metadata, with USGS conductive heat flow https://doi.org/10.5066/P9BZPVUC and thermal conductivity GDR1390.
* Signature: residual T_observed - (T_surface + q_conductive*depth/k), requiring compatible measurement depth, units, equilibrium flags and corroborating structure. Do not infer an exact upflow trace from a point anomaly.
* Missing faults: residual anomalies could support blind fluid pathways under cover, whereas deep hot wells alone need not indicate local advection.
* Difference: upstream H19 thresholds absolute temperature/geothermometry and smooths anomaly points; it does not correct for drilling depth/background conduction.
* Confounders: lateral aquifer transport, pumped/nonequilibrium wells, shallow solar heating, mixing and uncertain thermal conductivity.
* Prediction: +.003 DTI (-.002–.009); FP mass -4%. Medium–high cost. BLOCKED until depth/measurement metadata are obtainable for enough wells. Current exported CSV omits depth. Not viable merely because the GDR page exists; record retrieval and schema first.

## Fixed validation protocol for H21-1

1. Use template-derived finite footprint, exact input hashes, and full-raster 8-connected catalogue components as whole known segments. Determine geographic quadrants from footprint medians. A component intersecting a held-out quadrant is withheld IN ITS ENTIRETY, including pixels outside that quadrant. No random pixels, no clipped components.
2. Train only outside the held-out quadrant plus 15-pixel (1.5km) Euclidean buffer; also purge a 15-pixel buffer around EVERY withheld component outside that quadrant. Model-facing catalogue retains no withheld component or buffer pixels. All external catalogue-distance/maps, trained context fields, and full-catalogue fault-derived features are forbidden. Exogenous physical layers remain available — hiding the geological signal itself would make recovery impossible.
3. One magnitude-only clean control C21-PU and one C21-PU + H21-1 model. Both are explicitly NEW positive–unlabeled reconstructions, not reproductions of H19-4. Refit from scratch in each fold. Use non-negative PU logistic risk: pi=.03, fixed; R=pi E_P log(1+exp(-f))+max(0,E_U log(1+exp(f))-pi E_P log(1+exp(f)))+L2. U is sampled from the entire allowed training footprint (including unknown positives), never assigned confirmed-negative labels. SCAR/constant-prior assumptions are limitations, not geological facts.
4. Training sample cap: 30,000 labelled positives and 100,000 unlabeled pixels/fold; seed 210930+fold; robust feature transform arcsinh then scale from allowed TRAINING U only; standardized squares add fixed nonlinear capacity. L2=.001; optimizer L-BFGS-B, maximum 150 iterations, no holdout early stopping. Nonconvergence blocks promotion. Same sample indices for both models. No hyperparameter/budget/prior sweep this session.
5. Fixed prediction emission: sigma=1 Hessian across-strike NMS, take top 2.5% per fold (deterministic index tie-break). Exclude model-visible known pixels BEFORE budget selection. Scores are confidence rankings, not calibrated geology probabilities. Apply only score >= 0 and a nonzero evidence guard; never fill the budget from entirely unsupported cells.
6. Dense reference: all whole hidden segments in held-out quadrant. Sparse reference: deterministic 20% of whole-component IDs (seed 4242+fold); keep same predictions; other catalogue components are scorer-only known/neutral. This is an INCOMPLETE-REFERENCE sensitivity test, not a claimed sparse training scenario. No sparse truth is passed to the model. Known raster pixels are removed from predictions and truth BEFORE kernels/distances. Radius 3px, alpha=.2, beta=.8, no catalogue buffer in scoring. Report exact TP_w, FP_w, FN_w, recovery, .2FP and .8FN. Official FP mass is epistemically unverified, not a count of proved non-faults.
7. Compare matched predictions in 16 fixed non-overlapping geographic sub-blocks (4x4 extent). Paired sign-flip test of mean block DTI improvement, 65,536 sign patterns if all 16 blocks are usable. Family-wise Bonferroni p_adj=min(1,4*p), fixed family=4 including deferred hypotheses. Spatial block test is an approximation; adjacent blocks may still correlate. Macro quadrant scores remain primary summaries. With only four independent quadrant units, significance power is intrinsically limited; explicitly report a four-fold sign-flip diagnostic too.
8. Scientific control pass: dense mean gain >=.003, positive sparse mean gain, at least 3/4 dense fold wins, no fold drops >.01, multiplicity-adjusted block p<.05, and no loss in weighted recovery overall. Compare results to the numeric prediction, including misses.
9. Submission gate ALSO requires a reproducible leakage-safe current-best H19 comparator evaluated on the exact same split. That comparator is CURRENTLY BLOCKED by missing H19 arm-generation code/cache and by invalid prior assumptions. Even a control pass will not justify a new competition recommendation. Never invent a current-best holdout score or substitute its .1894 public score for a local benchmark.
10. No live submission, no repeated candidate tuning after looking. Log negative/blocked outcomes and expert-review rationale. Publish a byte/hash-verified historical H19-4 download clearly marked NOT a novel experiment. It is already user-reported at .1894, and renaming it cannot improve its score.

## Official source anchors

* Task, metric, template rules: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
* Exact catalogue mask / no wrong-label credit: https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4
* Expert label sources/coverage deliberately undisclosed: https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7
* Joint geophysical interpretation and ambiguity: USGS-authored https://www.osti.gov/servlets/purl/1724108; corroborated blind-system examples https://doi.org/10.2172/1724080
* nnPU method (primary research, NOT a government data source): https://arxiv.org/abs/1703.00593
* Rules/AI disclosure: https://docs.nlr.gov/docs/fy26osti/96647.pdf
* No automated DrivenData feed/upload: https://www.drivendata.org/termsofuse/

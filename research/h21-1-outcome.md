# H21-1 — first registered result, rejected for promotion

Registration was committed/pushed as `2dfc5de` before implementation and any outcomes; the implementation/tests were committed/pushed as `fc809c8` before this run. Do not amend the locked protocol to turn this result into a success.

**Disposition: REJECTED for promotion. No competition submission or leaderboard probe.** Executed CPU experiment took 99.41s. First-result evidence: [h21-1-results.json](../evidence/h21-1-results.json). This is raster-connected whole-known-segment hide/recover, **not** a hidden leaderboard score or geological proof that co-oriented gradients never indicate a fault.

## Prediction versus observation

| Registered quantity | Forecast | First observed result |
|---|---:|---:|
| Mean dense DTI change | +0.008 | **−0.00140662** |
| Mean sparse-reference DTI change | +0.004 | **−0.00104483** |
| Weighted recovery change | +0.015 absolute | **−0.00172146** |
| Unverified FP mass change | −3% relative | **+0.03264%** |

| Fold | Control dense | H21-1 dense | Control sparse | H21-1 sparse | Fits converged? |
|---|---:|---:|---:|---:|---|
| NW | 0.211764 | 0.209373 | 0.091660 | 0.087215 | No, both hit 150 iterations |
| NE | 0.222271 | 0.221767 | 0.056759 | 0.057683 | No, both hit 150 iterations |
| SW | 0.141339 | 0.139573 | 0.064175 | 0.062828 | Yes |
| SE | 0.221445 | 0.220478 | 0.089389 | 0.090078 | Yes |
| **Mean** | **0.199205** | **0.197798** | **0.075496** | **0.074451** | **2/4** |

## Actual DTI decomposition

Dense summed components across the four non-overlapping evaluation quadrants:

| Quantity | C21-PU control | H21-1 | Change |
|---|---:|---:|---:|
| TP_w | 14,543.24 | 14,438.25 | −104.99 |
| FP_w (unverified mass) | 115,366.38 | 115,404.04 | +37.65 |
| FN_w | 46,444.76 | 46,549.75 | +104.99 |
| 0.2 × FP_w | 23,073.28 | 23,080.81 | +7.53 |
| 0.8 × FN_w | 37,155.81 | 37,239.80 | +83.99 |

Thus the predicted recovery gain/FP reduction did not materialize under the fixed implementation. Mean-fold DTI is not DTI computed from summed components: report the aggregation explicitly. FP is the official incomplete-reference penalty, **not a set of confirmed geological non-faults**.

## Gate and limitations

* Dense wins: **0/4**. Dense gain threshold, positive sparse gain, recovery guard, corrected significance and convergence guard all fail.
* **11 of 16 fixed geographic blocks** have usable evaluation truth. Exact one-sided paired sign flips: p=0.98876953; four-member Bonferroni p=**1.0**. Four-quadrant diagnostic p=1.0. Adjacent blocks may correlate; do not claim 16 independent tests or significance.
* Both models hit the preregistered 150-iteration cap in NW/NE. This weakens scientific interpretation even beyond the negative scores. Increasing the cap now to select a better shared-holdout outcome is prohibited. A new optimizer/convergence protocol must be registered on different development/validation data.
* All fold lineage checks found zero hidden component pixels supplied to model-facing labels, zero partly visible raster components, and Euclidean 1.5km purges. Raster components are a proxy for known segments, not verified named geological fault-system IDs.
* Positive–unlabeled logistic fits use a fixed .03 prior and SCAR assumption. Mapping bias, prior misspecification and finite model capacity remain untested.
* The current-best H19 OOF generator is missing. A frozen historical map trained on the full catalogue and its reported .1894 live score are **not** clean comparators. Even a control improvement would not be enough to promote.

## Expert-review rationale and next test

The rationale is physically plausible density/magnetization juxtaposition; lithologic boundaries and survey seams can produce the same alignment. This session provides a falsified **score forecast under one fixed experiment**, not causal discrimination of those mechanisms. Retain the transform and this negative result as research evidence; do not add it to a competition entry. Recover a clean comparator, obtain vector fault IDs, and preregister a convergence-safe protocol and fresh test before evaluating a different candidate. H21-2/3/4 remain untested; no post-result transform/budget sweep.

## Post-result implementation review (not a retest)

The pre-result emitter `src/gems/inference.py@fc809c8` gives NMS pixels a rank boost but fills the remaining 2.5% budget with non-ridge positive scores. The support mask is valid source-data support, not an explicit positive-amplitude guard; a constant prior can emit pixels in a toy flat field. This is weaker than preregistration point 5. Therefore the first scores are an **audited failed implementation attempt**, not a fully compliant confirmatory test of strict-NMS geometry. Neither the saved JSON nor the original emitter was rewritten. A separate corrected `strict_emit` helper is unit-tested but **not activated or rescored** on this observed holdout. Its use needs a separately preregistered fresh test. This adds another reason not to promote; it does not rescue or improve the recorded result.

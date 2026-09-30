# Post-result protocol review — preserve, do not rescue

This review is separate from the immutable preregistration and first outcome. The original executed scientific code is available at `fc809c8`; first JSON remains SHA256 `ee3a52c471720dd5d6692a9fb849d21979111de2c3ecf57d6130f8dab66c6c67`.

## F19: emitter contract is weaker than point 5

`emit()` boosts Hessian NMS ranks by 1 but does not restrict selection to the NMS subset. It can fill a budget using other positive model scores. `physical_support.npy` is valid physical-data smoothing support, not an explicit positive structural-amplitude field; a positive prior is not itself fault evidence. Unit tests added in the second pass expose this in a toy constant field, without another model outcome.

**Repair:** separate `gems.emission_guard.strict_emit()` rejects invalid physical-strength values, requires positive physical strength, and selects only actual NMS ridges with deterministic ties, never padding to budget. It is unit-tested but **NOT used to rescore the current observed holdout or create a new competition file**. Existing `emit()` is retained for faithful first-experiment replication. If strict emission is selected next session, register a new experiment identifier, development-only convergence procedure and fresh evaluation data before any scores.

**Interpretation:** local DTI math/whole-component label purges remain independently tested. The original geometry/emission attempt nevertheless is not a fully compliant confirmatory test of strict-NMS point 5. Its forecasts missed, two fits did not converge, and the best comparator was missing regardless. Rejection must stand. Do not claim that a corrected guard yields better DTI without a future valid test.

## Other scope limits retained

* Whole raster components are the documented segment proxy, not original named physical-fault IDs. Source vectors are needed to group disconnected pieces of the same geological trace/system.
* Paired 11 usable sub-blocks are spatially adjacent. Bonferroni arithmetic does not establish exchangeability/independence or statistical power.
* PU prior/SCAR assumptions are fixed, not measured/calibrated. Official incomplete-reference FP penalty remains actual DTI, not a catalogue-absence target.
* Global physical fields are exogenous inputs; all hidden catalogue geometry, buffers and catalogue-derived predictors/sampling are excluded. Template-positive values never enter features.
* Replication is fixed-parameter verification, not tuning. First outcomes/data audit cannot be overwritten. Replication reports/masks remain ignored.

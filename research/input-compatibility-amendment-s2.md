# Pre-score input-compatibility repair — 2026-10-01

**Zero model fits or candidate scores preceded this repair.** Registration `452c21c` and every scientific parameter/forecast remain unchanged. No H21-1 retest or rescue is authorized.

## Observed failure and isolated diagnostic

* Run [36799921631](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36799921631) failed during physical-input restoration; later steps were skipped. Its full logs could not be fetched from the sandbox.
* Run [36800344273](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36800344273) restored all pinned raw bytes but `prepare_data.py` refused a preparation differing from the original complete 34-channel audit. Missing explicit bash pipefail allowed the failure to appear as a successful tee step. `prepare_s2.py` then stopped at the same strict full-input guard, BEFORE features/groups/fits/scores. Preserve the genuine redacted execution receipt in `evidence/h21-s2-prefit-failure.json`; do not interpret failure as a geological result.
* Input-only run [36801268774](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36801268774) performed **no model fit or score**. Its published [probe](https://github.com/buffedlizard55-lab/GEMSDOE21/releases/tag/h21-s2-input-only-probe), copied to `evidence/h21-s2-input-only-probe.json`, identified **exactly three differing manifest fields**: the byte hashes of `joint_orientation_100m`, `joint_orientation_300m` and `joint_orientation_multiscale`. These belong solely to the discarded H21-1 candidate and are used in **NEITHER S2 arm**.
* All **31 consumed base feature hashes** match the original frozen audit; all other manifest metadata match, including source hashes, shape/grid, feature/support counts and label/footprint metadata. Source byte/mask/support checks remain mandatory immediately before scoring. The exact numerical implementation reason for the discarded platform-dependent output differences is not established by this comparison. Do not assert a maximum per-pixel error from mean summaries.
* Actual Fiona inspection of the official ZIP now confirms one layer, 22,956 rows, `NUM: str:6`, `NAME: str:80`, Albers NAD83 / central meridian −117 WKT. Actual 1,886 multiline + 21,070 line geometries are accepted by the registered loader despite a LineString schema. Across the entire archive, 3,508 rows have missing NUM, 876 nonmissing NUM values and 39 NUM/name conflicts. These are **whole-archive figures, not footprint figures**. In-grid linkage/proxy/ambiguity audit must still precede the sole model invocation.

## Repair, not relaxation of a scientific input

`prepare_s2_base.py` catches only the existing complete-audit mismatch, then performs `verify(s2_base_only=True)`. That mode ignores only the three **unused SHA fields**. It does NOT ignore their metadata, any consumed feature, any raw/source hash, any footprint/catalogue/support check, any feature name/order or shape. The original `verify()` default retains its complete 34-channel lock and continues to refuse this preparation as an H21-1 replication. Unit tests mutate every one of the 31 consumed hashes and other protected metadata; they still fail compatibility.

The new experiment uses the registered 31/37 columns unchanged. Original audits/registrations/results are not edited. Native floating-point variability in discarded fields cannot affect S2 because those fields are not read by either model. The S2 result binds all 31 actual hashes and source/mask/support verification explicitly.

Explicit `set -euo pipefail` fixes the tee-step reporting bug. Setup and model logs are retained with query/token redaction. A marker is written before the sole actual model invocation; later runs fail closed if that marker is published, even when a partial evaluation fails. A blocked later job cannot erase the first invocation status.

The attempted 464MB frozen preparation-cache upload failed at `uploads.github.com` EOF; no remote cache asset is available. The empty provenance-only release is labelled unavailable, not used by this repair. Arrays stay ignored, not in Git.

Exactly one scientific run remains authorized; setup attempt 3 is permitted with byte-identical consumed features. Same 31/37 pairing, fixed samples, grouping, optimizer 1000/1e−8, metric, emission, forecasts, multiplicity and false current-best/fresh/submission gates. No weekly submission.

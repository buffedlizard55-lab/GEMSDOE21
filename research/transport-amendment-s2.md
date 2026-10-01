# Pre-score transport amendment — 2026-10-01

This is not a new hypothesis, parameter choice, evaluation partition or score-selected retry. Locked registration `452c21c` is unchanged.

Hosted run [36799921631](https://github.com/buffedlizard55-lab/GEMSDOE21/actions/runs/36799921631) passed the 81 pre-result tests but failed the pinned physical-input restoration step. GitHub's job API confirms that official-vector preparation, model evaluation and result publication were **SKIPPED**. No candidate/control scores or predictions were produced by that run. The archive/log download endpoints are inaccessible from the sandbox; the precise first failure was initially unknown. Public repository visibility was checked (all four transport repositories are public), rather than assuming a credentials problem.

Repair: immutable public RAW transport may be used if the GitHub contents transport fails, with the same expected content hashes and byte-size caps. It uses no tokens, never contacts DrivenData, never substitutes a layer/version, and cannot change scientific inputs. Hosted setup output is now retained in a redacted execution-status release so a setup failure can be diagnosed even when direct Actions log downloads are unavailable.

A second setup attempt is authorized with **identical** scientific registration, optimizer, features, split, budget, metric, multiplicity and promotion gates. Its marker is an infrastructure revision only. A successful first scientific outcome must remain immutable; no subsequent parameter tuning or candidate run is authorized. Both infrastructure run identifiers and the actual first scientific run must be recorded in the outcome/handoff.

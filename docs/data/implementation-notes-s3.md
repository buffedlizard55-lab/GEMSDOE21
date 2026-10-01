# S3 implementation and data-receipt notes — 2026-10-01 UTC

Registration `research/preregistration-h21-s3.md` was committed as `689160f` before new implementation. Its bytes and forecasts are unchanged. These notes disclose engineering failures; they are **not geological results**.

## Prototype numerical correction after synthetic failures

The first ten deterministic synthetic tests produced **2 failures / 8 passes**: a linear ramp had tiny spurious interior energy (about 1.9e-11 strength), and adding a constant 300 datum changed boundary strength by about 4.95e-6. Inspection used only toy arrays, never competition/external field predictions or labels.

Corrections retain the locked sigma/support/offset/strike contract: remove a fixed first-supported datum before smoothing; zero high-pass differences within `64 * float64 epsilon * (abs(smooth1)+abs(smooth3))`; compute the **same normalized 5×5 mean** with direct local convolution rather than a rolling uniform-filter accumulator. The latter avoids cancellation propagating from an energetic border into a zero-energy interior. No scientific scale, contrast/support threshold, model weight, forecast or test tolerance was selected/relaxed from geological observations. All ten synthetic tests then passed with the original tolerances. Success is not support for the fault-depth mechanism or a forecasted DTI win.

The prototype module has no catalogue, fit, scoring or submission-export dependency. Its only command entrypoint accepts no field-data option. The S3 phase guard refuses field fits, scores, new scientific TIFFs and uploads even if a caller supplies optimistic JSON flags. This is a workflow safeguard, not a claim Python code cannot be invoked outside the authorized workflow.

## Official source acquisition: failed first vector metadata pass retained

Hosted run `36811364343`, code `bcbdee3`, downloaded the pinned eastern numeric magnetic archive and XML, matching the official MD5 and byte counts; four actual float32 EPSG:32611 rasters have 40m output cells. This does not change the reported **200m flight-line spacing**, nor verify shortwave detectability in western GeoDAWN Area 2 (400m lines). About 69% of the fixed eastern box has support in the source-grid envelope; missing regions must never be treated as negatives or filled with reflected evidence.

The same run verified GDR's actual 709-record NAD83 point schema with `Deposit_ty`, `Map_unit`, `Ref_source` and other fields. Classification quality, duplicate sites, ages, matching physical-edge support and rights/attribution still require review before H21-12 is scientifically viable.

QFaults/CGS metadata collection failed at `src.bounds`: an empty/attribute-only layer has no extent. The full first receipt is retained as `evidence/official-inputs-s3-first-attempt.json`; those errors are not evidence of globally unavailable sources. The repair records null bounds for empty/nonspatial layers, and retains a bounds-specific error if a nonempty driver lacks an extent. It neither fabricates an extent nor substitutes a different dataset. A separate hosted receipt records the repair outcome.

## Delivery edge cases

The range/grid validator now rejects malformed references, complex/string values and rounded float64 overshoots; source dtype failures return a failed check rather than reaching invalid range arithmetic. Unique staged files avoid shared `.partial` collisions; outputs cannot overwrite the reference or put ZIP bytes into the TIFF path. ZIP checks reject extra members, nested/traversal paths, symlinks, encrypted/oversized entries and corrupt CRC, and independently validate the contained TIFF. No clipping, sentinel replacement inside the footprint or changed historical primary prediction is permitted.

## Scientific scope

No field maps, field fits, geological DTI scores, candidate TIFF or competition upload are authorized in S3. The original H19 producer and clean same-split current-best comparator remain unrecovered. External obtainability is distinct from predictor completeness, fresh whole-system label provenance, units/resampling compatibility, a locked prospective fit/control protocol, multiplicity-corrected promotion, and actual competition acceptance.

## Review pass 2: delivery-only regression

The first full suite exposed an expected-command-list regression: 148 passed, 1 failed, 1 skipped. The new delivery wrapper had rerun the synthetic prototype. This is not field inference, but delivery should not perform even toy transforms: the wrapper now reads the preserved prototype receipt and runs only metadata/byte-format readiness checks. Its regression test explicitly excludes preparation, evaluation and prototype calls; new commands also reject unknown `--fit`/field-data flags. Desktop/mobile/no-JS/download browser review had already passed 16 scenarios with zero JS errors. Cross-platform ZIP drive-relative/control-character names are additionally rejected. The failed first suite is retained, not presented as all passing.

The repaired vector audit completed in hosted run36811664161. The 128,520-byte full receipt’s publisher failed; an intermediate recovery publisher also failed. Those original publisher error causes were not authenticated from logs. Final run36812447269 successfully recovered the already-created small lossless envelope; all four official raw archive digests match the existing public release assets. No additional source acquisition, field fit or score was needed for final recovery.

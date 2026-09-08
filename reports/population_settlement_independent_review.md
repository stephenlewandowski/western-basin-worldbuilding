# Phase 11A/11B Independent Review and Correction Record

## Initial review

Reviewer delegation: `deleg_22ae2906`

The reviewer inspected the actual corrected package at feature-worktree HEAD `399ede9606f4f4c900d38dc9e9d74842e98d0b52`, including the Phase 11A/11B tables, reports, source ledgers, maps, validators, briefs, current diff, and Phase 1–10 freeze manifests.

Initial structured verdict:

passed: false
security_concerns: []
logic_errors:
  - The dependency register promoted an aggregate Ohio OD subset into 52 object-level transport dependencies and marked every row as documented. Nineteen rows concerned Michigan or Indiana objects, but only the Ohio OD source was cited and no object-level derivation or state-specific coverage was provided.
  - The qualitative dependency matrix hard-coded identical dependency classifications by node type rather than deriving them from row-level evidence, especially for object-level transport, water, wastewater, and energy claims.
provenance_errors:
  - The 520-row dependency register reused sources outside their recorded scopes: all 52 water rows cited the Toledo-service-area source, all 52 wastewater rows cited the Ohio-only NPDES source, and all 52 transport rows cited the Ohio OD source. The 19 Michigan/Indiana objects therefore lacked matched row-level source coverage.
  - The 16 workplace_residence_difference rows used combined WAC/RAC source IDs, but their row metadata said `LODES 8.4 WAC/RAC 2023` with reference and estimate period `2023`; the ledger identified the combined product as `LODES 8.4 WAC/RAC comparison 2023/2023` with `2023/2023` metadata.
statistical_errors: []
spatial_scale_errors: []
demographic_boundary_errors: []
suggestions:
  - Add state-matched or explicitly regional source records to dependency rows, mark transport dependence as inferred unless documented evidence supports each object, and carry source/basis fields into the matrix.
  - Add combined provenance entries for derived density and containment rows where the source_product describes both Decennial and TIGER inputs but source_id names only one input.
  - Strengthen Python and R validators to require exact expected counts, validate source-product/year metadata against the ledger, assert the absence of Michigan WAC/RAC differences, and recompute every protected artifact hash in R. Remove the tautological household-level assertion in `validate_population_settlement.py`.
  - Document the OD selection rule (same-state files and the 25-job threshold) in the assumptions and QA reports.
  - Restore the Phase 10C status entry in the phase-status list of `docs/canon_status.md`.
summary: "Counts and major boundaries passed, but acceptance was blocked by dependency source-scope/claim mismatches and combined WAC/RAC metadata mismatch."

## Correction disposition

The blocking findings were corrected without new Census/ACS/PEP/LODES research and without changing Phase 1–10 accepted/frozen artifacts:

- Rebuilt the affected Phase 11B mobility/dependency products from the existing cached inputs.
- Changed same-vintage workplace/residence-difference rows to carry the exact combined source-ledger product, reference-year, and estimate-period metadata: `LODES 8.4 WAC/RAC comparison 2023/2023` and `2023/2023`.
- Preserved the exclusion of all Michigan WAC/RAC difference rows.
- Changed transport dependency rows to use the object's state-matched LODES OD source and mark the generalized dependency as inferred rather than documented.
- Restricted Toledo and Ohio NPDES source use to matching scopes; other water/wastewater rows now use generalized accepted service-responsibility context with limited/inferred qualification and no state-specific operator, permit, territory, or load claim.
- Changed the dependency matrix to derive its dependency dimensions and source/basis notes from the dependency register rather than hard-coding node-type classifications.
- Strengthened Python and R validators with exact package counts, combined WAC/RAC metadata checks, Michigan-difference exclusion checks, state-matched dependency-source checks, and matrix derivation-note checks.
- Documented the same-state/non-self OD selection rule and the corrected dependency-source boundary in the generated Phase 11B assumptions report.
- Restored the Phase 10C status entry in `docs/canon_status.md`.

## Fresh post-correction review

Reviewer delegation: `deleg_0f848f19`

The fresh reviewer inspected the current corrected package after regeneration and returned:

passed: true
security_concerns: []
logic_errors: []
provenance_errors: []
statistical_errors: []
spatial_scale_errors: []
demographic_boundary_errors: []
suggestions:
  - Optionally add explicit per-dimension source, basis, and documented-or-inferred fields to the matrix, plus combined provenance records for derived density and containment rows.
  - Strengthen the Python and R validators to recompute every matrix dimension and exact source/basis-note set rather than checking only a derived-text marker.
  - Reconcile or clearly label legacy status wording in the historical handoff and older freeze records before the next formal handoff.
summary: "Passed. The corrected package has the expected 11A/11B counts; all 16 workplace_residence_difference rows use exact same-vintage combined WAC/RAC metadata with no Michigan difference rows; all 52 transport dependencies use state-matched LODES OD sources and are inferred; water/wastewater scopes and generalized qualifications are consistent; mapped matrix values and source/evidence notes match dependency-register evidence; both R validators passed; maps, manifests, and all protected Phase 1–10 artifact hashes verified."

The reviewer confirmed the expected counts, source/vintage boundaries, Michigan difference exclusion, state-matched OD provenance, generalized service-dependency boundaries, map integrity, prohibited-scope exclusions, Phase 11C/12 absence, and Phase 1–10 freeze integrity. The remaining items are non-blocking suggestions. Formal Sol acceptance remains external.

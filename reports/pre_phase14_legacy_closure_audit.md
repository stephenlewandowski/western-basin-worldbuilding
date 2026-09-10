# Pre-Phase-14 Legacy Closure Audit

Audit date: 2026-09-10
Audit type: short, read-only forensic/status recovery
Repository: `C:\Projects\Public_GitHub\western-basin-worldbuilding`
Audit base: `574b97c9dd3ec52b80cb0a4ce32bf541a4f391d3`

Repository state is authoritative. No Phase 14 implementation, scientific-artifact change, freeze-manifest creation, acceptance-status change, merge, deletion, or history rewrite was performed.

Evidence precedence used:

1. [PROJECT_STATUS.md](../PROJECT_STATUS.md) and [docs/canon_status.md](../docs/canon_status.md)
2. Final acceptance/freeze records where present
3. [reports/current_phase_handoff.md](current_phase_handoff.md)
4. Historical briefs, working manifests, validators, and Git history in temporal context

Active holds preserved throughout: Great Black Swamp `C — HOLD / noncanonical`; Toledo intake-coordinate discrepancy `UNRESOLVED`.

## 1. Phase 7A status

FACT — Phase 7A is `ACCEPTED / FROZEN` in the current authoritative status surfaces ([PROJECT_STATUS.md](../PROJECT_STATUS.md), [docs/canon_status.md](../docs/canon_status.md)).

- Implemented: yes; feature commit `8ca0d7cdd789f54342d27cd05678ee72230ed671`.
- Integrated into `main`: yes; the commit is an ancestor of current `main`.
- Deterministic Python validation: passed in `reports/exposure_context_artifact_check.json`; the validator is `src/python/systems/validate_exposure_context.py`.
- Independent R validation: historical handoff records passed; validator is `src/R/systems/validate_exposure_context.R`.
- Provenance: bounded validation passed. The Python validator checks source IDs against `metadata/sources.yml`; the R validator checks non-empty source IDs. The source report is `reports/environmental_health_sources.md`.
- Independent review: no Phase-7A independent-review record was found in the repository. No formal Phase-7A review verdict can be recovered.
- Explicit acceptance: current authoritative status and the final freeze manifest record `ACCEPTED / FROZEN`; no separate later-style `accepted_by` decision field was found.
- Final freeze manifest: present — `reports/phase7a_exposure_environmental_health_freeze_manifest.json`.
- Final manifest package: 8 protected artifacts: six CSV products and the Map 23 PNG/SVG pair. Counts are 20 nodes, 20 edges, five pathway rows, five monitoring rows with ten qualitative dimensions, ten evidence-crosswalk rows, and 13 uncertainty rows.
- Current artifacts: all eight final-manifest SHA-256 values match the current checkout.
- Blocking unresolved issue: none identified for the already accepted/frozen 7A package. The active holds remain explicit.

## 2. Phase 7B status and evidence

FACT — Phase 7B is `IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE` in both current status surfaces. This wording is consistent with the contemporaneous final Phase 7 handoff and the post-Phase-13 review.

- Implemented: yes; feature commit `c4ed03fa7c85c4f2febafef8a768eef298a50d6e`.
- Integrated into `main`: yes; the commit is an ancestor of current `main`.
- Package: 20 dependency edges, seven controls, five evidence-strength rows, and Map 24.
- Deterministic Python validation: artifact check is `passed`; validator is `src/python/systems/validate_exposure_dependencies.py`.
- Independent R validation: historical handoff records passed; validator is `src/R/systems/validate_exposure_dependencies.R`.
- Provenance: bounded checks passed for non-empty source IDs and source-qualified reports (`reports/exposure_dependency_sources.md`). No separate strict Phase-7B provenance-validation record was found.
- Independent review: no Phase-7B independent-review record was found.
- Exact final review verdict: none recorded; the repository does not provide a `passed`, `conditional pass`, or `failed` final independent-review verdict for 7B.
- Explicit Sol acceptance: no. Current status explicitly says awaiting Sol acceptance.
- Final freeze manifest: absent. `reports/exposure_dependency_manifest.json` is a six-artifact `validated_working_package` manifest, not a final acceptance/freeze manifest.
- Current artifacts: all six working-manifest SHA-256 values match the current checkout; no Phase-7B artifact-path commits occur after Phase 7C integration.
- Administrative/schema issue: the working manifest and status text describe the matrix as `5 × 10`, meaning five rows by ten qualitative dimensions. The CSV and validators have shape `5 × 11`, because the first column is `pathway_family` plus ten qualitative columns. This is explainable as a dimension-convention difference, but it should be stated explicitly before final freeze.
- Blocking issue: no scientific contradiction found. Formal acceptance/freeze remains blocked by the missing independent-review record/verdict and final freeze manifest; the matrix-dimension convention should also be normalized or documented.

## 3. Phase 7C status and evidence

FACT — Phase 7C is `IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE` in both current status surfaces. It is a separate qualitative scenario layer and is not accepted or frozen.

- Implemented: yes; feature commit `c915e15793a50c861a76baa404347ec448dc9e48`.
- Integrated into `main`: yes; the commit is an ancestor of current `main`.
- Package: 36 assumptions, 30 scenario nodes, 30 scenario edges, 30 control states, 30 uncertainty states, six comparison rows, and Maps 25/25b.
- Deterministic Python validation: artifact check is `passed`; validator is `src/python/systems/validate_environmental_health_futures.py`.
- Independent R validation: historical handoff records passed; validator is `src/R/systems/validate_environmental_health_futures.R`.
- Provenance: scenario-source and basis reports are present (`reports/environmental_health_scenario_sources.md` and related reports), and bounded scenario separation checks passed. No separate strict Phase-7C provenance-validation record was found.
- Independent review: no Phase-7C independent-review record was found.
- Exact final review verdict: none recorded; the repository does not provide a `passed`, `conditional pass`, or `failed` final independent-review verdict for 7C.
- Explicit Sol acceptance: no. Current status explicitly says awaiting Sol acceptance.
- Final freeze manifest: absent. `reports/environmental_health_scenario_manifest.json` is an eleven-artifact working manifest, not a final acceptance/freeze manifest.
- Current artifacts: all eleven working-manifest SHA-256 values match the current checkout; no Phase-7C artifact-path commits occur after its integration.
- Blocking issue: no scientific contradiction found. Formal acceptance/freeze remains blocked by the missing independent-review record/verdict and final freeze manifest.

Current authoritative wording is explicit and consistent: `PROJECT_STATUS.md` headings state `PHASE 7A — ACCEPTED / FROZEN`, `PHASE 7B — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE`, and `PHASE 7C — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE`; `docs/canon_status.md` repeats the same disposition in its phase-status list.

## 4. Exact validation/review evidence

The committed machine-readable checks report `status: passed` for all three subphases:

- 7A: `reports/exposure_context_artifact_check.json` — 20/20/5/5x10/10/13; Map 23 valid; Phase 6C frozen; no documented individual exposure, dose/health outcome, risk score, future, or vector work.
- 7B: `reports/exposure_dependency_artifact_check.json` — 20/7/5; matrix shape 5x11; Map 24 valid; Phase 7A immutable; no exposure score or dose/health model.
- 7C: `reports/environmental_health_scenario_artifact_check.json` — 36/30/30/30/30/6; Maps 25/25b valid; qualitative-only; baseline separation true.

The contemporaneous final Phase 7 handoff (`reports/current_phase_handoff.md`, lines 364–376 and 378–384) additionally records Python/R 7A/7B/7C validation, prior ecological regressions, Markdown links, npm tests/build, and Git LFS checks as passed. Those are historical execution records, not independent-review verdicts.

No Phase-7A, 7B, or 7C independent-review file is present. This is materially different from later phases whose manifests explicitly protect review records. The post-Phase-13 review independently records that 7B/7C have no final freeze manifests and remain awaiting Sol acceptance (`reports/post_phase13_systems_atlas_review.md`, lines 220–229).

## 5. Acceptance/freeze readiness

- Phase 7A: already recorded as accepted/frozen; current final-manifest hashes remain valid.
- Phase 7B: technically review-ready, but not administratively acceptance/freeze-ready. A fresh bounded independent review with a durable verdict, explicit treatment of the matrix dimension convention, and a final freeze manifest are required before claiming `ACCEPTED / FROZEN`.
- Phase 7C: technically review-ready, but not administratively acceptance/freeze-ready. A fresh bounded independent review with a durable verdict and a final freeze manifest are required before claiming `ACCEPTED / FROZEN`.

No acceptance or freeze status was changed by this audit.

## 6. Blocking and unresolved issues

1. Missing Phase-7B independent-review record and final freeze manifest.
2. Missing Phase-7C independent-review record and final freeze manifest.
3. Phase-7B matrix dimension convention is recorded as `5 × 10` in status/working-manifest text but as CSV shape `5 × 11` in the artifact check and validators; the extra column is the pathway-family identifier, not an extra qualitative dimension.
4. No scientific blocker was found in the inspected package boundaries.
5. Preserved project holds: Great Black Swamp `C — HOLD / noncanonical`; Toledo intake-coordinate discrepancy `UNRESOLVED`.

## 7. Downstream dependencies on Phase 7

FACT — Later accepted/frozen phases materially reuse Phase 7A only, not the unaccepted 7B/7C packages.

- Phase 8's QA records that its package did not modify Phase 7 exposure tables or Maps 25/25b. No accepted Phase 8 artifact was found to depend materially on 7B/7C.
- Accepted Phase 11 population products use a generalized Phase 7 exposure-context interface and cite the Phase 7A frozen manifest; they do not use 7B/7C artifacts as frozen inputs.
- Accepted/frozen Phase 13A, 13B, and 13C records similarly reference the accepted/frozen Phase 7A exposure-context layer. Their manifests and citation ledgers do not treat 7B/7C as accepted/frozen inputs.
- No later final freeze manifest inspected contains a Phase-7B or Phase-7C artifact. Therefore no downstream accepted/frozen phase can be shown to depend materially on 7B/7C as protected package inputs.
- Phase 7A's eight final-manifest hashes remain stable. The six 7B and eleven 7C working-manifest hashes also remain stable in the current checkout.

INFERENCE — Later systems may use broad environmental-health context, but that does not promote 7B/7C to accepted or frozen status.

## 8. Phase 7 package summary

| Subphase | Products | Maps | Dependency/scenario products | Validation records | Review records | Current manifest status |
|---|---|---|---|---|---|---|
| 7A | 20 nodes; 20 edges; 5 pathway rows; 5x10 monitoring matrix; 10 evidence rows; 13 uncertainty rows | Map 23 PNG/SVG | None | Python/R validators; artifact check passed | None found | Final freeze manifest present; `ACCEPTED / FROZEN` |
| 7B | 20 dependency edges; 7 controls; 5 evidence-strength rows; 5x10 qualitative matrix | Map 24 PNG/SVG | Dependency/control/evidence package | Python/R validators; artifact check passed | None found | Working manifest only; `validated_working_package` |
| 7C | 36 assumptions; 30 node states; 30 edge states; 30 control states; 30 uncertainty states; 6 comparison rows | Maps 25/25b PNG/SVG | Five scenario tables plus comparison CSV/PNG | Python/R validators; artifact check passed | None found | Working manifest only; no final freeze manifest |

Protected-artifact disposition:

- 7A final freeze manifest protects exactly eight core package/map artifacts.
- 7B working manifest hashes exactly six package/map artifacts.
- 7C working manifest hashes exactly eleven scenario/comparison/map artifacts.
- Reports, validator scripts, briefs, and working manifests are evidence records unless included by a final freeze manifest; they must not be described as final protected artifacts for 7B/7C.

## 9. Phase 2A legacy worktree

FACT — The clean legacy worktree is:

- Branch: `phase-2a-geology-baseline`
- Tip: `b0341602f9dc7dc8385786958a4a96815dbc01cf`
- Worktree: `C:\Users\slewa\.codex\visualizations\2026\08\28\01a04737-05e5-7ab2-a05b-f27f9d3afa14\western-basin-phase2a`
- Merge-base with current `main`: `6034827ed80bdd3ff70c60c30e291d75d8045c6d`
- `b034160` is not an ancestor of current `main`.
- Branch is clean and synchronized with `origin/phase-2a-geology-baseline` at the same tip.

Unique commit history:

- Exactly one commit unique to the branch: `b0341602f9dc7dc8385786958a4a96815dbc01cf` — `feat: add Phase 2A materials baseline`.
- `git log --left-right --cherry-mark main...phase-2a-geology-baseline` marks this commit as branch-only; no equivalent commit identity was merged.

Files changed by that unique commit (25):

- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `README.md`
- `data/processed/glasspunk_base.gpkg`
- `data/raw/census/tigerweb_incorporated_places.geojson`
- `data/raw/census/tigerweb_primary_roads.geojson`
- `data/raw/census/tigerweb_secondary_roads.geojson`
- `data/raw/facilities/facility_geocodes_2026.csv`
- `data/raw/ohiodnr/bedrock_type_western_basin.geojson`
- `docs/canon_status.md`
- `metadata/sources.yml`
- `metadata/systems.yml`
- `outputs/figures/materials_system_R_validation.png`
- `outputs/maps/systems/06_geology_resources_2026.png`
- `outputs/maps/systems/06_geology_resources_2026.svg`
- `outputs/tables/materials_carbonate_render_data.csv`
- `outputs/tables/materials_sites_render_data.csv`
- `reports/README.md`
- `reports/materials_system_artifact_check.json`
- `reports/materials_system_qa.md`
- `reports/materials_system_sources.md`
- `src/R/systems/render_materials_system.R`
- `src/R/systems/validate_materials_system.R`
- `src/python/systems/build_materials_system.py`
- `src/python/systems/validate_materials_system.py`

Disposition evidence:

- Current `main` contains corresponding paths for all 25 changed files; there are no branch-only current files.
- Twelve of the 25 paths are byte-identical to the current `main` tree, including the core raw inputs, Map 06 PNG, render tables, artifact check, and R scripts.
- The remaining differences are later status/source/report revisions, the current-development GeoPackage, Map 06 SVG, and the Python builder. Current `reports/materials_system_qa.md` explicitly states that the Phase 2A validated scientific baseline was selectively integrated onto current `main` without applying stale documentation or the legacy GeoPackage; Phase 2B then extended it.
- Current `main` retains the Phase 2A scientific scope, Map 06, source/QA record, artifact check, classifications, and validation logic. No unique Phase 2A scientific conclusion or required product was found only in the legacy worktree.

Classification: **A — fully superseded / safe future cleanup candidate**.

This is a future maintenance disposition only. The branch/worktree was not merged, deleted, or modified in this audit. The legacy GeoPackage and stale documentation should not be copied back into current `main` without separate review.

## 10. Recommendation before Phase 14

Do not implement Phase 14 yet. First perform a narrow acceptance/metadata closure for Phase 7B and 7C: obtain fresh independent reviews, record exact verdicts, resolve/document the 7B matrix-dimension convention, create final freeze manifests only after Sol acceptance, and update current status surfaces only in that authorized acceptance run. Keep Phase 7A immutable and preserve both active holds. Separately retain the Phase 2A worktree for now as historical evidence; remove it only in a later explicitly authorized cleanup after branch/worktree verification.

## Audit boundary confirmation

No Phase 14 material, release, tag, accepted/frozen scientific artifact, historical Phase 3A or 6B manifest, Phase 7 artifact, Phase 2A branch/worktree, or phase acceptance status was changed. Only this audit report and the audit-occurrence note in `reports/current_phase_handoff.md` are intended working-tree changes.

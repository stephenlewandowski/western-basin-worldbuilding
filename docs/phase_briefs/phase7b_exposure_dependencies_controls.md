# Phase 7B — Exposure Dependencies, Evidence Strength & Controls, 2026

Status: ACCEPTED / FROZEN; final freeze manifest: `reports/phase7b_exposure_dependencies_controls_freeze_manifest.json`.
Primary product: Map 24 — Exposure Dependencies & Controls, 2026.
Secondary product: Exposure Evidence / Control Matrix.

## Scope and boundaries

Reuse exactly the five Phase 7A pathway families: Drinking Water / HAB; Ambient Air; Soil / Groundwater / Legacy Contamination; Food / Fish / Recreational Water; Heat. Model dependencies among environmental conditions, pathway opportunity, monitoring/information, treatment/control/advisory, generic receptor context, and evidence limits. Evidence strength is qualitative (`strong`, `moderate`, `limited`, `unknown`) and is not exposure magnitude. UNKNOWN remains distinct from LIMITED.

Preserve the ladder: environmental presence ≠ potential pathway ≠ documented exposure ≠ dose ≠ illness association ≠ causation. Do not create exposure scores, dose estimates, toxicological weighting, disease/epidemiology models, EJ rankings, vector/infectious-disease work, plumes, or future scenarios. Do not call a condition failure, vulnerability, or unsafe without authoritative support. Preserve the Toledo intake-coordinate discrepancy as unresolved, Luckey as documented contamination/remediation without individual exposure or receptor-reaching plume, and Great Black Swamp as C — HOLD / noncanonical.

## Required products

- `data/processed/networks/exposure_dependency_edges.csv`
- `data/processed/analysis/exposure_control_register.csv`
- `data/processed/analysis/exposure_evidence_strength_register.csv`
- `data/processed/analysis/exposure_dependency_control_matrix.csv`
- `outputs/maps/systems/24_exposure_dependencies_controls_2026.png` and `.svg`
- source, assumptions, findings, evidence-limits, and QA reports under `reports/`
- Python and independent R validators plus a freeze manifest for Phase 7A

## Validation and transition gate

Require schema, enum, provenance, referential-integrity, negative-scope, artifact, map, Phase 7A freeze, prior-regression, Markdown-link, application, and Git/LFS validation. If all checks pass and no factual contradiction emerges, record Phase 7B as IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE, integrate normally, snapshot its implementation hashes, and proceed automatically to Phase 7C. Do not claim Sol scientific acceptance for Phase 7B.

## Phase 7C gate

Phase 7C may model only qualitative 2050/2075 alternative environmental conditions, pathway opportunities, monitoring, controls, advisories, treatment, institutional capacity, and uncertainty. It must keep all future objects in separate scenario tables with scenario/year and explicit assumptions. It must not model exposure magnitude, dose, illness, disease, probabilities, or vector/infectious disease. Stop after Phase 7C.

# Glasspunk Systems Atlas

The historical v0.1 release builds the Phase 1 Water System only. Current development also includes the validated Phase 2A–2C materials and historical-exposure baseline. Existing TypeScript prototype files are untouched.

Phase 3A adds the factual 2026 energy / grid / compute baseline and Map 11. See `energy_system_sources.md`, `energy_system_assumptions.md`, `energy_system_qa.md`, `energy_system_manifest.json`, and `energy_system_artifact_check.json`.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_water_system.py --historical-swamp-image "C:\Users\slewa\Downloads\Great Black Swamp.jpeg"
Rscript src\R\systems\validate_water_system.R .
Rscript src\R\systems\render_water_system.R .
```

Raw public-service responses are cached under `data/raw`. Delete a specific cached response only when intentionally refreshing that source.

## Great Black Swamp Phase 1 follow-up QA

- `great_black_swamp_geometry_source_review.md` — source evaluation, reproducible derivation, uncertainty, and human stop gate.
- `great_black_swamp_class_review.csv` — explicit Gordon/ODNR class inclusion review.
- `great_black_swamp_interstate_compatibility.csv` — Ohio/Indiana/Michigan compatibility assessment.
- `great_black_swamp_geometry_qa.json` — machine-readable geometry validation.
- `great_black_swamp_candidate_county_intersections.csv` and `great_black_swamp_candidate_watershed_intersections.csv` — quantitative overlaps.
- `great_black_swamp_source_manifest.json` — preserved-source hashes and retrieval records.

The candidate remains under `outputs/qa/`; it is not part of the canonical Phase 1 GeoPackage.

## Physical hydrography Phase 1 follow-up QA

- `water_hydrography_source_review.md` — authoritative USGS 3DHP source, retrieval, provenance, and feature semantics.
- `physical_hydrography_reconciliation.md` — executive finding, topology method, baseline comparison, limitations, and human gate.
- `wbd_connector_reconciliation.csv` — one QA outcome for each of the 251 released inferred WBD connectors.
- `physical_hydrography_baseline_comparison.csv` and `physical_hydrography_qa.json` — tabular and machine-readable validation summaries.
- `hydrography_data_cleanup.md` — unpublished-commit backup record and raw/LFS storage decisions.

The hash-verified 3DHP extraction and derived QA maps are the review evidence for **B — ACCEPT WITH QUALIFICATION**. The large raw snapshot is reproducibly retrievable and ignored by Git; its service metadata, retrieval method, feature/provenance counts, and SHA-256 remain tracked. The approved three-layer representation is integrated into the Git-LFS-managed current-development GeoPackage; the historical `v0.1-water-system` artifact and released Map 01–05 files remain unchanged.

## Phase 2 materials baseline

- `materials_system_sources.md` — Phase 2A–2B source evidence and use limits.
- `materials_system_assumptions.md` — relationship-basis semantics and deferred questions.
- `materials_system_qa.md` — scientific, network, and cartographic QA findings.
- `materials_system_artifact_check.json` — Phase 2A machine-readable checks.
- `materials_phase2b_manifest.json` and `materials_phase2b_artifact_check.json` — Phase 2B artifact hashes and validation.

Maps 06–08 are the current 2026 baseline. Map 09 adds source-grounded history,
remediation, and qualified exposure/control interfaces. Its source, assumptions,
QA, manifest, and machine-validation reports use the
`materials_exposure_history_*` prefix. Maps 10/10b add six explicitly fictional
alternative future states, with `materials_scenario*` tables/reports. Scenario
objects remain separate from the immutable factual graph.

## Phase 3 energy baseline and dependencies

Phase 3A's accepted/frozen 2026 energy, grid, and compute baseline is recorded in
the `energy_system_*` reports and protected by `phase3a_freeze_manifest.json`.
Phase 3B adds the qualitative dependency registry, Map 12, the 10 × 7 ordinal
matrix, and cross-system findings. See `energy_dependency_sources.md`,
`energy_dependency_assumptions.md`, `energy_dependency_qa.md`,
`energy_dependency_manifest.json`, and `energy_cross_system_findings.md`.
Phase 3B is accepted/frozen by `phase3b_freeze_manifest.json`; Phase 3C future
scenarios remain separate under `data/processed/scenarios/` and the
`energy_scenario_*` reports.

Phase 3C uses `energy_scenario_assumptions.csv`, `energy_nodes_scenario.csv`,
`energy_edges_scenario.csv`, and `energy_scenario_sources.csv` for separate
2050/2075 deltas. Maps 13/13b and the qualitative comparison are accompanied by
`energy_scenario_consistency.md`, `energy_system_future_worldbuilding.md`, and
the machine-readable scenario manifest and artifact check.

## Phase 4A observation and decision baseline

Phase 4A establishes four representative factual 2026 observation-to-decision
chains and Map 14. The node and relationship tables are
`../data/processed/networks/observation_system_nodes.csv` and
`../data/processed/networks/observation_system_edges.csv`.

- `observation_system_sources.md` — source evidence and chain boundaries.
- `observation_system_assumptions.md` — schema semantics, coordinate policy, and exclusions.
- `observation_system_qa.md` — structural, chain, boundary, and regression QA.
- `observation_system_manifest.json` — Phase 4A artifact hashes and counts.
- `observation_system_artifact_check.json` — machine-readable validation result.

Map 14 is a hybrid geographic/schematic view. Only two public station
coordinates are plotted; abstract networks, products, organizations, and
responses remain schematic. The Toledo intake-coordinate discrepancy remains
unresolved, and no cyber, SCADA, automated-control, AI-authority, or future
scenario layer is included.

## Phase 4B information dependencies and governance

Phase 4B is the implemented/validated analytical counterpart to Phase 4A. Its
tables are `../data/processed/networks/information_dependency_edges.csv`,
`../data/processed/analysis/information_blind_spots.csv`, and
`../data/processed/analysis/decision_authority_matrix.csv`.

- `information_dependency_sources.md` — reused source evidence and boundaries.
- `information_dependency_assumptions.md` — qualitative fields and scope.
- `information_governance_findings.md` — four-chain findings and worldbuilding implications.
- `information_dependency_qa.md` — structural, immutability, and boundary QA.
- `information_dependency_manifest.json` — Phase 4B artifact hashes and counts.
- `information_dependency_artifact_check.json` — machine-readable validation result.

Map 15 and the `information_dependency_matrix_2026` figure distinguish public
information dependencies from physical geography. Phase 4B is
**ACCEPTED / FROZEN**; `phase4b_information_freeze_manifest.json` protects its
principal artifacts. Phase 4C is the separate scenario phase and is active.

## Phase 4C information and governance futures

Phase 4C uses the frozen Phase 4A/4B factual baselines to model separate
2050/2075 scenario deltas. It does not modify the Phase 4A/4B tables or maps.
The package is **ACCEPTED / FROZEN** under
`phase4c_information_freeze_manifest.json`; future assumption, node-state,
edge-state, comparison, and report artifacts are documented in the Phase 4C
reports.

## Phase 5A freight and industrial flow baseline

Phase 5A establishes a bounded factual 2026 freight/material-flow layer. Its
tables are `../data/processed/networks/freight_system_nodes.csv` and
`../data/processed/networks/freight_system_edges.csv`.

- `freight_system_sources.md` — port, rail, highway, fuel, and materials evidence.
- `freight_system_assumptions.md` — corridor-versus-shipment and commodity boundaries.
- `freight_system_qa.md` — structural, flow, Materials Corridor, and artifact QA.
- `freight_system_manifest.json` — Phase 5A artifact hashes and counts.
- `freight_system_artifact_check.json` — machine-readable validation result.

Map 17 and the optional commodity-interface figure distinguish public transport
corridors from generalized or documented flow relationships. Phase 5A is
Phase 5A is **ACCEPTED / FROZEN** under `phase5a_freight_freeze_manifest.json`. Phase 5B is
the active evidence-strengthening phase; future freight scenarios are not begun.

## Phase 5C freight dependencies

Phase 5C is accepted and frozen. Its reports
are `freight_dependency_sources.md`, `freight_dependency_assumptions.md`,
`freight_dependency_findings.md`, `freight_dependency_qa.md`,
`freight_dependency_manifest.json`, and `freight_dependency_artifact_check.json`.
The phase adds qualitative dependency and modal-substitutability analysis over
the frozen Phase 5A/5B records and does not add routes, quantities, security
targets, hazardous-material modeling, or future freight scenarios. The Phase
3A newline portability maintenance note is `phase3a_freeze_portability.md`.
The freeze manifest is `phase5c_freight_dependency_freeze_manifest.json`.

## Phase 6A ecology and biodiversity

Phase 6A is the active factual 2026 ecological baseline. Its source,
assumption, QA, findings, manifest, and artifact-check reports will use the
`ecology_system_*` and `ecological_*` prefixes. It will preserve the
noncanonical Great Black Swamp hold and exclude sensitive species locations,
invented biodiversity values, ecological-risk scoring, and future scenarios.

The implemented package includes `ecology_system_sources.md`,
`ecology_system_assumptions.md`, `ecology_system_findings.md`,
`ecology_system_qa.md`, `ecology_system_manifest.json`, and
`ecology_system_artifact_check.json`. Map 20 and the ecology tables are
validated and await Sol acceptance.

## Phase 6B ecological dependencies

Phase 6B is implemented and validated and awaits Sol acceptance. Its reports
are `ecological_dependency_sources.md`, `ecological_dependency_assumptions.md`,
`ecological_dependency_findings.md`, `ecological_dependency_qa.md`,
`ecological_dependency_manifest.json`, and
`ecological_dependency_artifact_check.json`. The Phase 6B implementation
snapshot is `phase6b_ecological_dependency_freeze_manifest.json`. Map 21 and the dependency,
disturbance, and resilience tables remain qualitative and exclude risk scores,
population modeling, sensitive locations, exact routes, and future scenarios.

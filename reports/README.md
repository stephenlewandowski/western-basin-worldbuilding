# Glasspunk Systems Atlas

## Phase 7A Exposure & Environmental Health

- `environmental_health_sources.md`, `environmental_health_assumptions.md`, `environmental_health_findings.md`, and `environmental_health_qa.md` document the bounded 2026 five-pathway baseline.
- `exposure_context_artifact_check.json` records machine validation; `phase6c_ecological_futures_freeze_manifest.json` protects the accepted Phase 6C scenario package.


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

Phase 6A is the accepted/frozen factual 2026 ecological baseline. Its source,
assumption, QA, findings, manifest, and artifact-check reports will use the
`ecology_system_*` and `ecological_*` prefixes. It will preserve the
noncanonical Great Black Swamp hold and exclude sensitive species locations,
invented biodiversity values, ecological-risk scoring, and future scenarios.

The implemented package includes `ecology_system_sources.md`,
`ecology_system_assumptions.md`, `ecology_system_findings.md`,
`ecology_system_qa.md`, `ecology_system_manifest.json`, and
`ecology_system_artifact_check.json`. Map 20 and the ecology tables are
validated and accepted/frozen.

## Phase 6B ecological dependencies

Phase 6B is accepted and frozen. Its reports
are `ecological_dependency_sources.md`, `ecological_dependency_assumptions.md`,
`ecological_dependency_findings.md`, `ecological_dependency_qa.md`,
`ecological_dependency_manifest.json`, and
`ecological_dependency_artifact_check.json`. The Phase 6B implementation
snapshot is `phase6b_ecological_dependency_freeze_manifest.json`. Map 21 and the dependency,
disturbance, and resilience tables remain qualitative and exclude risk scores,
population modeling, sensitive locations, exact routes, and future scenarios.

## Phase 6C ecological futures

Phase 6C is implemented, validated, and integrated and awaits Sol acceptance.
Its reports are `ecology_scenario_sources.md`,
`ecology_scenario_assumptions.md`, `ecology_scenario_consistency.md`,
`ecology_future_worldbuilding.md`, `ecology_scenario_qa.md`, and
`ecology_scenario_manifest.json`. Maps 22/22b and the scenario comparison are
qualitative, assumption-based, and separate from factual 2026 baselines.

## Phase 8 biogeochemical and nutrient fluxes

Phase 8A–8C is accepted and frozen under the three Phase 8 subphase freeze
manifests. Phase 8A provides the factual 2026 baseline in
`../data/processed/networks/biogeochemical_system_nodes.csv`,
`biogeochemical_flux_edges.csv`, and
`../data/processed/analysis/biogeochemical_quantitative_fluxes.csv`; Map 26 is
the geographic/system view. Phase 8B provides qualitative dependencies,
controls, and bottlenecks in `biogeochemical_dependency_edges.csv`,
`biogeochemical_control_register.csv`, and `biogeochemical_dependency_matrix.csv`;
Map 27 is the dependency/control view. Phase 8C provides separate qualitative
2050/2075 scenario tables, comparison output, and Maps 28/28b.

`biogeochemical_sources.md`, `biogeochemical_assumptions.md`,
`biogeochemical_findings.md`, `biogeochemical_dependency_findings.md`,
`biogeochemical_consistency.md`, `biogeochemical_qa.md`,
`biogeochemical_future_worldbuilding.md`, and
`biogeochemical_module_manifest.json` document provenance, boundaries, findings,
and artifact hashes. No future nutrient quantities, probabilities, or predictive
HAB model are included.

## Phase 9 climate and natural hazards

Phase 9A is implemented, validated, and integrated as the factual 2026 hazard
baseline: `../data/processed/networks/climate_hazard_nodes.csv`,
`climate_hazard_edges.csv`, `../data/processed/analysis/climate_hazard_observations.csv`,
and `climate_hazard_sources.csv`; Map 29 is the compact physical-hazard view.
Phase 9B adds qualitative dependency edges, a compound-event register,
resilience/control register, and dependency matrix; Map 30 is the schematic
cross-system view. Phase 9C is a separate 2050/2075 scenario layer and must not
modify these working baselines.

Phase 9A reports are `climate_hazard_sources.md`, `climate_hazard_assumptions.md`,
`climate_hazard_findings.md`, `climate_hazard_qa.md`, and
`climate_hazard_baseline_manifest.json`. Phase 9B reports are
`climate_dependency_sources.md`, `climate_dependency_assumptions.md`,
`climate_dependency_findings.md`, `climate_dependency_qa.md`, and
`climate_dependency_manifest.json`. Neither layer creates a composite hazard
score, unsupported probability, health/social-vulnerability ranking, or
comprehensive emergency-management model.

Phase 9A, 9B, and 9C are **ACCEPTED / FROZEN**. Their freeze manifests protect
13, 14, and 21 artifacts respectively:

- `phase9a_climate_natural_hazards_freeze_manifest.json`
- `phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json`
- `phase9c_climate_hazard_futures_freeze_manifest.json`

The transparent correction logs are `phase9a_correction_qa.md` and
`phase9_correction_qa.md`; the final independent-review record is
`phase9_independent_review.md`.

## Phase 10 governance, jurisdiction, and decision systems

Phase 10A and 10B are **ACCEPTED / FROZEN** as a factual/qualitative 2026 institutional layer. Phase 10C is **ACCEPTED / FROZEN** under `phase10c_governance_futures_freeze_manifest.json` as a separate qualitative 2050/2075 scenario layer.

- `../data/processed/scenarios/governance_scenario_assumptions.csv` — 48 explicit scenario assumptions
- `../data/processed/scenarios/governance_actor_states_scenario.csv` — 120 actor states
- `../data/processed/scenarios/governance_authority_states_scenario.csv` — 90 authority states
- `../data/processed/scenarios/governance_dependency_states_scenario.csv` — 150 dependency states
- `../data/processed/scenarios/governance_coordination_states_scenario.csv` — 84 coordination states
- `../data/processed/scenarios/governance_uncertainty_states_scenario.csv` — 96 uncertainty states
- `../data/processed/analysis/governance_scenario_sources.csv` — 19 scenario-source records
- `../outputs/maps/systems/34_governance_futures_2050.png` and `.svg`
- `../outputs/maps/systems/34b_governance_futures_2075.png` and `.svg`
- `../outputs/figures/governance_scenario_comparison.csv`, `.png`, and `.svg`
- `governance_scenario_sources.md`, `governance_scenario_assumptions.md`, `governance_scenario_consistency.md`, `governance_scenario_findings.md`, `governance_scenario_worldbuilding.md`, and `governance_scenario_qa.md`
- `governance_scenario_manifest.json` and `governance_scenario_artifact_check.json` — validated working records retained for lineage
- `phase10c_governance_futures_freeze_manifest.json` — final Sol-acceptance freeze manifest protecting 23 artifacts
- `governance_scenario_independent_review.md` — fresh bounded review of the actual final package; `passed: true` with no blocking findings

Phase 10C keeps every future state explicitly separate from the current 2026 baseline, with current-fact, scenario-assumption, and scenario-consequence fields. It preserves GLIFWC as an intertribal body, distinct sovereign nations, binational role boundaries, public/private distinctions, human legal authority, the Great Black Swamp hold, and the unresolved Toledo intake-coordinate discrepancy. It creates no composite governance score, unsupported future jurisdiction, partisan/election analysis, AI legal authority, or Phase 11 work.

The package explicitly separates regulation, operation, ownership, monitoring, funding, advisory, permitting, scientific information, public/private control, mandatory/voluntary status, and jurisdictional scale. It makes no composite governance score or generalized governance-gap ranking.
- `../data/processed/analysis/governance_authorities.csv` — 100 authority/role records
- `../data/processed/networks/governance_relationships.csv` — 100 actor-system relationships
- `../data/processed/analysis/governance_sources.csv` — 48 source records
- `../data/processed/analysis/governance_uncertainty_register.csv` — 16 uncertainty records
- `../outputs/maps/systems/32_governance_jurisdiction_2026.png` and `.svg` — Map 32
- `../data/processed/analysis/governance_dependency_register.csv` — 25 cross-system dependency rows
- `../data/processed/networks/governance_dependency_edges.csv` — 25 dependency edges
- `../data/processed/analysis/governance_coordination_mechanisms.csv` — 14 mechanisms
- `../data/processed/analysis/governance_dependency_matrix.csv` — 10-row qualitative matrix
- `../outputs/maps/systems/33_cross_system_governance_dependencies_2026.png` and `.svg` — Map 33
- `governance_baseline_sources.md`, `governance_baseline_assumptions.md`, `governance_baseline_findings.md`, `governance_baseline_qa.md`
- `governance_dependency_sources.md`, `governance_dependency_assumptions.md`, `governance_dependency_findings.md`, `governance_dependency_qa.md`
- `phase10a_governance_jurisdiction_freeze_manifest.json`
- `phase10b_governance_dependencies_coordination_freeze_manifest.json`
- `governance_baseline_manifest.json` and `governance_dependency_manifest.json` — pre-acceptance working manifests retained for lineage
- `governance_independent_review.md` — initial conditional-pass review and correction disposition
- `governance_post_correction_independent_review.md` — post-correction review (`deleg_2e8d515e`)
- `governance_additional_post_correction_independent_review.md` — additional review (`deleg_eedc4116`)

The package explicitly separates regulation, operation, ownership, monitoring, funding, advisory, permitting, scientific information, public/private control, mandatory/voluntary status, and jurisdictional scale. It makes no composite governance score or generalized governance-gap ranking.

## Phase 11 population, settlement, mobility, and dependencies

Phase 11A, Phase 11B, and Phase 11C are **ACCEPTED / FROZEN** under their final freeze manifests. Phase 11C remains a separate qualitative scenario layer.

- `../data/processed/analysis/population_settlement_nodes.csv` — 62 population, municipality, and employment-center nodes
- `../data/processed/analysis/population_settlement_observations.csv` — 918 population/settlement observations
- `../data/processed/networks/population_settlement_relationships.csv` — 44 structural/employment relationships
- `../data/processed/analysis/population_mobility_observations.csv` — 302 mobility observations
- `../data/processed/networks/population_mobility_relationships.csv` — 142 generalized commuting relationships
- `../data/processed/analysis/population_system_dependency_register.csv` — 520 qualitative dependency rows
- `../data/processed/analysis/population_system_dependency_matrix.csv` — 52 qualitative matrix rows
- `../outputs/maps/systems/35_population_settlement_2026.png` and `.svg` — Map 35
- `../outputs/maps/systems/36_population_mobility_dependencies_2026.png` and `.svg` — Map 36
- `population_settlement_sources.md`, `population_settlement_assumptions.md`, `population_settlement_findings.md`, `population_settlement_qa.md`
- `population_mobility_sources.md`, `population_mobility_assumptions.md`, `population_mobility_findings.md`, `population_mobility_qa.md`
- `population_settlement_baseline_manifest.json` and `phase11_working_manifest.json`
- `phase11a_population_settlement_freeze_manifest.json` and `phase11b_population_mobility_dependencies_freeze_manifest.json` — final Sol-acceptance freeze manifests
- `phase11c_population_settlement_futures_freeze_manifest.json` — final Sol-acceptance freeze manifest protecting the 22-artifact qualitative futures package
- `population_settlement_artifact_check.json` and `population_mobility_artifact_check.json`

Phase 11C products:

- `../data/processed/scenarios/population_settlement_scenario_assumptions.csv` — 36 explicit scenario assumptions
- `../data/processed/scenarios/population_settlement_projection_evidence.csv` — six projection-evidence records
- `../data/processed/scenarios/population_settlement_future_states.csv` — 108 qualitative county-scale future settlement states
- `../data/processed/networks/population_settlement_future_relationships.csv` — 108 qualitative spatial relationships
- `../data/processed/scenarios/population_settlement_future_uncertainty.csv` — 36 uncertainty states
- `../data/processed/analysis/population_settlement_future_sources.csv` — 11 scenario-source records
- `../outputs/figures/population_settlement_future_comparison.csv`, `.png`, and `.svg` — six-row comparison
- `../outputs/maps/systems/37_population_settlement_futures_2050.png` and `.svg` — Map 37
- `../outputs/maps/systems/37b_population_settlement_futures_2075.png` and `.svg` — Map 37b
- `population_settlement_future_sources.md`, `population_settlement_future_assumptions.md`, `population_settlement_future_findings.md`, and `population_settlement_future_qa.md`
- `population_settlement_future_manifest.json` and `population_settlement_future_artifact_check.json`
- `population_settlement_future_independent_review.md` — fresh post-correction review; `passed: true` with all blocking arrays empty
- `../src/python/systems/build_population_settlement_futures.py`, `validate_population_settlement_futures.py`, and `../src/R/systems/validate_population_settlement_futures.R`

Official Ohio, Michigan, and Indiana county projection products are recorded as 2050 reference evidence without deterministic scenario totals. 2075 is explicit scenario content rather than mechanical extrapolation. Climate migration is a high-uncertainty scenario mechanism, not a population-growth assumption. Population, households, housing units, workers, jobs, and commuters remain distinct; commuting remains distinct from migration.

The complete package preserves Census/ACS/PEP/LODES vintages and geography scales, distinguishes residence/workplace and commuting/migration, and keeps accepted water, energy, transport, climate, environmental-health, ecology, nutrient, housing, and governance interfaces qualitative. It creates no vulnerability/EJ score, protected-class ranking, individual movement model, health outcome, exact utility territory, or unsupported forecast. Phase 12 is a separate approved vector-ecology package. Python Phase 11 freeze validation is `../src/python/systems/validate_phase11_freezes.py`; independent R freeze validation is `../src/R/systems/validate_phase11_freezes.R`. Phase 11C validation is `../src/python/systems/validate_population_settlement_futures.py` and `../src/R/systems/validate_population_settlement_futures.R`.

## Phase 12 vector ecology and dependencies

Phase 12A and 12B are **ACCEPTED / FROZEN**. Phase 12A contains 20 nodes, 26 ecology
relationships, 36 surveillance/context records, 15 habitat associations, 27
sources, 10 uncertainties, and Map 38. Phase 12B contains 28 dependency rows,
28 dependency edges, eight matrix rows, eight evidence-crosswalk rows, 27 reused
sources, and Map 39.

- `../data/processed/networks/vector_ecology_nodes.csv`, `vector_ecology_edges.csv`
- `../data/processed/analysis/vector_surveillance_records.csv`, `vector_habitat_associations.csv`, `vector_ecology_sources.csv`, `vector_ecology_uncertainty.csv`
- `../data/processed/analysis/vector_system_dependency_register.csv`, `vector_system_dependency_matrix.csv`, `vector_dependency_evidence.csv`
- `../data/processed/networks/vector_system_dependency_edges.csv`
- `../outputs/maps/systems/38_vector_ecology_baseline_2026.png` and `.svg`
- `../outputs/maps/systems/39_vector_environment_human_dependencies_2026.png` and `.svg`
- `vector_ecology_sources.md`, `vector_ecology_assumptions.md`, `vector_ecology_findings.md`, `vector_ecology_qa.md`
- `vector_dependency_sources.md`, `vector_dependency_assumptions.md`, `vector_dependency_findings.md`, `vector_dependency_qa.md`
- `vector_ecology_baseline_manifest.json`, `vector_dependency_manifest.json`, and `phase12_working_manifest.json` — pre-acceptance working manifests retained for lineage
- `phase12a_vector_ecology_freeze_manifest.json` (17 artifacts), `phase12b_vector_environment_human_dependencies_freeze_manifest.json` (15 artifacts), and `phase12c_vector_ecology_futures_freeze_manifest.json` (28 artifacts) — final Sol-acceptance freeze manifests
- `phase12_independent_review.md` — fresh bounded review; `passed: true` with all blocking arrays empty
- `../src/python/systems/build_vector_ecology.py`, `validate_vector_ecology_baseline.py`, and `validate_vector_dependencies.py`
- `../src/R/systems/validate_vector_ecology_baseline.R` and `validate_vector_dependencies.R`
- `../src/python/systems/validate_phase12_freezes.py` and `../src/R/systems/validate_phase12_freezes.R` — final Python/R freeze validators
- `../docs/phase_briefs/phase12a_vector_ecology_baseline.md`, `phase12b_vector_environment_human_dependencies.md`, and `phase12c_vector_ecology_futures.md`
- `../outputs/maps/systems/40_vector_ecology_futures_2050.png` and `.svg` — Map 40
- `../outputs/maps/systems/40b_vector_ecology_futures_2075.png` and `.svg` — Map 40b
- `../data/processed/scenarios/vector_ecology_scenario_assumptions.csv`, `vector_ecology_vector_states_scenario.csv`, `vector_ecology_habitat_states_scenario.csv`, `vector_ecology_surveillance_states_scenario.csv`, `vector_ecology_dependency_states_scenario.csv`, and `vector_ecology_uncertainty_states_scenario.csv`
- `../data/processed/analysis/vector_ecology_future_sources.csv` and `../outputs/figures/vector_ecology_future_comparison.csv`, `.png`, and `.svg`
- `vector_ecology_future_sources.md`, `vector_ecology_future_assumptions.md`, `vector_ecology_future_findings.md`, `vector_ecology_future_consistency.md`, `vector_ecology_future_qa.md`, and `vector_ecology_future_worldbuilding.md`
- `vector_ecology_future_manifest.json`, `vector_ecology_future_artifact_check.json`, and `phase12c_citation_ledger.json`
- `vector_ecology_future_independent_review_initial.md` — failed initial review retained as correction lineage
- `vector_ecology_future_independent_review.md` — fresh corrected-package review; `passed: true` with all blocking arrays empty
- `../src/python/systems/build_vector_ecology_futures.py`, `validate_vector_ecology_futures.py`, and `../src/R/systems/validate_vector_ecology_futures.R`
- `../src/python/systems/validate_phase12c_freeze.py` and `../src/R/systems/validate_phase12c_freeze.R` — independent final Phase 12C freeze validators

The package preserves presence != abundance, pathogen detection != human
infection, sampling effort != abundance, detection != establishment, county
record != precise local distribution, non-detection/CDC no-records != absence,
and positive vector pool or human case != local transmission. Phase 12C is
**ACCEPTED / FROZEN** as a separate qualitative 2050/2075 scenario layer under
`phase12c_vector_ecology_futures_freeze_manifest.json` (28 protected artifacts).
It creates no individual risk or exposure estimate, disease-risk or
vulnerability/EJ score, unsupported abundance/range surface, Phase 13, release,
or tag. Active phase is NONE; the next analytical phase is NOT APPROVED.
Deferred maintenance is limited to the Phase 6B manifest status wording mismatch
and the Phase 3A missing manifest status; neither was altered during this freeze.

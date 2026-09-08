# Western Basin Worldbuilding

*Science-informed speculative worldbuilding for Toledo, Northwest Ohio, the Maumee watershed, and western Lake Erie.*

This repository combines real-world geographic baselines, environmental and infrastructure systems modeling, scenario analysis, speculative regional worldbuilding, history, maps, concept art, and foundations for future fiction, games, and interactive-atlas work.

The repository is named **Western Basin Worldbuilding** so the long-term project is not locked to one setting title. **Glasspunk** is the current working genre and aesthetic terminology. **Cyberglass** is earlier or possible in-world terminology. The final fictional-world title remains open.

> **Core principle:** REAL GEOGRAPHY FIRST; FICTIONAL INTERPRETATION SECOND.

## Project Status

**Phase 1 — COMPLETE**  
**Water System v0.1 — COMPLETE / VALIDATED**  
**Phase 2A — COMPLETE / VALIDATED**

**Phase 2B — COMPLETE / VALIDATED (2026 MATERIAL FLOWS)**

**Phase 2C — COMPLETE / VALIDATED (MATERIALS / EXPOSURE HISTORY)**

**Phase 2D — COMPLETE / VALIDATED (ALTERNATIVE MATERIALS FUTURES)**

**Phase 3A — ACCEPTED / FROZEN (2026 ENERGY / GRID / COMPUTE BASELINE)**

**Phase 3B — ACCEPTED / FROZEN (CRITICAL ENERGY DEPENDENCIES)**

**Phase 3C — ACCEPTED / VALIDATED (ENERGY / GRID / COMPUTE FUTURES)**

**Phase 4A — ACCEPTED / FROZEN (2026 OBSERVATION & DECISION INFRASTRUCTURE BASELINE)**

**Phase 4B — ACCEPTED / FROZEN (2026 INFORMATION DEPENDENCIES & GOVERNANCE)**

**Phase 4C — ACCEPTED / FROZEN (DATA, SENSORS, GOVERNANCE & SECURITY FUTURES, 2050 / 2075)**

**Phase 5A — ACCEPTED / FROZEN (FREIGHT / INDUSTRY / MATERIAL FLOWS BASELINE, 2026)**

**Phase 5B — ACCEPTED / FROZEN (FREIGHT EVIDENCE & INTERCHANGE VALIDATION, 2026)**

**Phase 5C — ACCEPTED / FROZEN (FREIGHT DEPENDENCIES & CRITICAL INTERFACES, 2026)**

**Phase 6C — ACCEPTED / FROZEN (ECOLOGICAL FUTURES, 2050 / 2075)**

**Phase 7A — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE (EXPOSURE & ENVIRONMENTAL HEALTH BASELINE, 2026)**

Map 23 is a bounded exposure-context layer covering drinking water/HAB, ambient air, Luckey legacy contamination, fish/recreational water, and heat. It does not infer individual exposure, dose, illness, causation, a plume, or a health-risk score.

**Phase 8A — ACCEPTED / FROZEN (BIOGEOCHEMICAL & NUTRIENT FLUX BASELINE, 2026)**

**Phase 8B — ACCEPTED / FROZEN (BIOGEOCHEMICAL DEPENDENCIES & CONTROLS, 2026)**

**Phase 8C — ACCEPTED / FROZEN (BIOGEOCHEMICAL & NUTRIENT FLUX FUTURES, 2050 / 2075)**

The Phase 8 package is protected by `reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json`, `reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json`, and `reports/phase8c_biogeochemical_futures_freeze_manifest.json`. Accepted scientific content was not changed while recording Sol acceptance.

**PHASE 9 — ACCEPTED / FROZEN (CLIMATE & NATURAL HAZARDS SYSTEM)**

Phase 9A, 9B, and 9C are complete, corrected where required, and separate from earlier factual systems. The package contains Map 29 (2026 baseline), Map 30 (2026 dependencies/compound events/resilience), and Maps 31/31b (qualitative 2050/2075 futures). Correction history is recorded in `reports/phase9a_correction_qa.md` and `reports/phase9_correction_qa.md`. It contains no composite hazard score, unsupported probability, health/social-vulnerability ranking, deterministic hazard surface, or comprehensive emergency-management module.

**PHASE 10A / 10B — ACCEPTED / FROZEN (GOVERNANCE & JURISDICTION, 2026)**

Phase 10A provides 40 actors, 100 authority/role records, 100 actor-system relationships, 48 sources, 16 uncertainty records, and Map 32. Phase 10B provides 25 dependency rows/edges, 14 coordination mechanisms, a 10-row qualitative matrix, and Map 33. The package distinguishes regulation, operation, ownership, monitoring, funding, advisory, permitting, scientific information, public/private, mandatory/voluntary, and jurisdictional roles. Phase 10A and 10B are protected by `reports/phase10a_governance_jurisdiction_freeze_manifest.json` and `reports/phase10b_governance_dependencies_coordination_freeze_manifest.json`. Phase 10C is accepted/frozen under `reports/phase10c_governance_futures_freeze_manifest.json` as a separate qualitative 2050/2075 scenario layer; Maps 34/34b and its scenario manifest remain separate from the frozen 2026 baseline. No composite governance score or generalized governance-gap claim was created.

Phase 1 contains seven Maumee basin HUC-8 watersheds, 252 HUC-12 subwatersheds, 864 physical Lower Maumee flowlines, 251 explicitly inferred WBD routing connectors, 608 NWI freshwater wetlands, 14 system nodes, and 15 dependency edges.

See [PROJECT_STATUS.md](PROJECT_STATUS.md) and the [Phase 1 handoff](reports/water_system_phase1_handoff.md).

For current project state, [PROJECT_STATUS.md](PROJECT_STATUS.md) is authoritative. For current canon, [docs/canon_status.md](docs/canon_status.md) is authoritative. Older imported planning documents remain preserved for history and context and do not override those files.

Phase 2 adds a sourced 2026 geology/facility baseline and shared carbonate/beryllium material-flow architecture. It preserves the distinction between local carbonate extraction, Elmore advanced processing of nonlocal beryllium feed, and Luckey legacy remediation.

Phase 2C adds a 30-event source-grounded Luckey/Elmore chronology, qualified
exposure and environmental-health interfaces, and Map 09. It makes no
individual-exposure finding and creates no plume, exposure radius, direct
Luckey-to-Elmore flow, or future scenario.

Phase 1 follow-up QA has produced a [Great Black Swamp source review](reports/great_black_swamp_geometry_source_review.md) and [human-review map](outputs/qa/great_black_swamp_geometry_review.png). Human decision: **C — HOLD**. The method is resolved, but the candidate remains outside the canonical GeoPackage and the direct-source gap remains open without blocking current development.

A separate [physical hydrography reconciliation](reports/physical_hydrography_reconciliation.md) evaluated all 251 inferred WBD routing edges against USGS 3DHP topology and full geometry. Human decision: **B — ACCEPT WITH QUALIFICATION**. Current development now separates 86,410 physical features, 16,347 official non-stream connector features, and 12 unresolved abstract routing edges; the historical v0.1 release remains unchanged.

Phase 3A Map 11 and its 18-node/17-edge tables are accepted, frozen, and
regression-protected. Phase 3B adds [Map 12](outputs/maps/systems/12_critical_energy_dependencies_2026.png),
28 qualitative dependency edges, five generalized dependency nodes, and a
10 × 7 ordinal matrix. It models cross-system dependencies—not power flows—
and does not claim congestion, outage probability, reserve margin, N-1
performance, restoration time, or future generation.

Phase 3B is accepted and frozen as the 2026 cross-system dependency baseline.
Phase 3C uses separate 2050/2075 scenario assumptions and deltas; it does not
overwrite Phase 3A or Phase 3B factual rows or artifacts.

Phase 3A adds 18 factual/qualified nodes, 17 coarse dependency edges, and [Map 11](outputs/maps/systems/11_energy_grid_compute_baseline_2026.png). Public EIA/HIFLD transmission geometry is cartographic context only; no feeder, dispatch, congestion, transfer-capability, or power-flow claim is made. The sole compute node is a documented 5 MW Bowling Green project whose operation remains unverified.

## Current Canon

The current v0.1 working model has five macroregions:

1. Glass City Core
2. Maumee River Commons
3. Lake Erie Energy & Security Coast
4. Black Swamp Country
5. Great Lakes Industrial Belt

They are overlapping interpretive identities, not jurisdictions or mutually exclusive GIS polygons. Physical, systems, political, historical, and fictional geographies remain distinct. Frontier Arc is superseded. Woodville–Elmore–Luckey may become a Materials Corridor, but it is not a sixth macroregion.

See [docs/canon_status.md](docs/canon_status.md).

## Phase 1 Water System v0.1

Phase 1 models the chain from land and precipitation through drainage, the Maumee River, Maumee Bay, western Lake Erie, HAB response, Toledo's intake, Collins Park treatment, and regional consumers.

Verified geography and facilities, inferred system structure, historical references, and fictional 2050 scenarios carry explicit status/provenance. Quantitative values remain null where authoritative support is absent. Fictional 2050 nodes have null coordinates.

### Analytical maps

- [01 — Water baseline 2026](outputs/maps/systems/01_water_baseline_2026.png)
- [02 — Maumee nutrient network](outputs/maps/systems/02_maumee_nutrient_network.png)
- [03 — Black Swamp drainage system](outputs/maps/systems/03_black_swamp_drainage_system.png)
- [04 — Lake Erie HAB–intake dependency](outputs/maps/systems/04_lake_erie_hab_intake_dependency.png)
- [05 — Water system 2050 scenario](outputs/maps/systems/05_water_system_2050_scenario.png)

Each map is also available as SVG. The [system network diagram](outputs/figures/water_system_network.png) shows the baseline source-to-consumer dependency chain.

## Phase 2 Geology and Material Flows

- [06 — Geology and resources 2026](outputs/maps/systems/06_geology_resources_2026.png)
- [07 — Carbonate materials system](outputs/maps/systems/07_carbonate_materials_system.png)
- [08 — Beryllium strategic supply chain](outputs/maps/systems/08_beryllium_strategic_supply_chain.png)
- [09 — Luckey–Elmore materials / exposure history](outputs/maps/systems/09_luckey_elmore_materials_exposure_history.png)
- [10 — Materials system 2050](outputs/maps/systems/10_materials_system_2050.png)
- [10b — Materials system 2075](outputs/maps/systems/10b_materials_system_2075.png)

Map 07 connects generalized 1:500,000 carbonate occurrence to sourced extraction/processing roles and broad engineering functions. Map 08 anchors Materion Elmore as advanced processing—not extraction—within a schematic nonlocal-feed and strategic-use network. Solid and dashed relationships distinguish documented links from generalized inference; neither map asserts freight routes or quantities.

Rebuild and validate:

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_materials_system.py
.\.venv\Scripts\python.exe src\python\systems\build_material_flows.py
.\.venv\Scripts\python.exe src\python\systems\validate_materials_system.py
.\.venv\Scripts\python.exe src\python\systems\validate_material_flows.py
Rscript src\R\systems\validate_materials_system.R .
Rscript src\R\systems\validate_material_flows.R
.\.venv\Scripts\python.exe src\python\systems\build_materials_exposure_history.py
.\.venv\Scripts\python.exe src\python\systems\validate_materials_exposure_history.py
Rscript src\R\systems\validate_materials_exposure_history.R
.\.venv\Scripts\python.exe src\python\systems\build_materials_scenarios.py
.\.venv\Scripts\python.exe src\python\systems\validate_materials_scenarios.py
Rscript src\R\systems\validate_materials_scenarios.R
```

## Phase 3A Energy / Grid / Compute Baseline

- [11 — Western Basin energy / grid / compute baseline, 2026](outputs/maps/systems/11_energy_grid_compute_baseline_2026.png)

Rebuild and validate from the cached official EIA subsets:

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_energy_system.py
.\.venv\Scripts\python.exe src\python\systems\validate_energy_system.py
Rscript src\R\systems\validate_energy_system.R .
```

Use `--refresh` on the builder only when intentionally refreshing the official EIA source snapshots.

## Phase 3B Critical Energy Dependencies & Reliability

- [12 — Critical energy dependencies and reliability, 2026](outputs/maps/systems/12_critical_energy_dependencies_2026.png)
- [Qualitative dependency matrix](outputs/figures/energy_dependency_matrix_2026.png)
- [Cross-system findings](reports/energy_cross_system_findings.md)

The separate dependency layer reuses Phase 3A asset IDs and adds five
generalized external dependency nodes. It is qualitative/ordinal and does not
perform power-flow, feeder, contingency, congestion, reserve-margin, or outage
probability analysis.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_energy_dependencies.py
.\.venv\Scripts\python.exe src\python\systems\validate_phase3a_freeze.py
.\.venv\Scripts\python.exe src\python\systems\validate_energy_dependencies.py
Rscript src\R\systems\validate_energy_dependencies.R .
```

## Phase 3C Energy / Grid / Compute Futures

- [13 — Energy / grid / compute futures, 2050](outputs/maps/systems/13_energy_grid_compute_futures_2050.png)
- [13b — Energy / grid / compute futures, 2075](outputs/maps/systems/13b_energy_grid_compute_futures_2075.png)
- [Qualitative scenario comparison](outputs/figures/energy_scenarios_comparison.png)
- [Scenario consistency report](reports/energy_scenario_consistency.md)
- [Future worldbuilding report](reports/energy_system_future_worldbuilding.md)

Phase 3C contains three non-probabilistic scenario families—Managed Transition,
Distributed Resilience, and High-Load Convergence—with separate 2050/2075
assumptions and node/edge deltas. The factual 2026 Phase 3A/3B layers remain
unchanged; no precise future MW, route, facility, outage, or power-flow claim is
made.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_energy_scenarios.py
.\.venv\Scripts\python.exe src\python\systems\validate_phase3b_freeze.py
.\.venv\Scripts\python.exe src\python\systems\validate_energy_scenarios.py
Rscript src\R\systems\validate_energy_scenarios.R .
```

## Phase 4A Data, Sensors & Decision Infrastructure Baseline

- [14 — Western Basin observation & decision system, 2026](outputs/maps/systems/14_observation_decision_system_2026.png)
- [Observation-system nodes](data/processed/networks/observation_system_nodes.csv)
- [Observation-system relationships](data/processed/networks/observation_system_edges.csv)
- [Sources](reports/observation_system_sources.md)
- [Assumptions](reports/observation_system_assumptions.md)
- [QA](reports/observation_system_qa.md)

Phase 4A contains 25 nodes and 21 relationships across four representative
public-information chains: Lake Erie/HAB/drinking water, Lower Maumee
hydrology/flood, environmental/regulatory reporting, and energy information.
Only the GLOS Toledo crib station and USGS 04193500 at Waterville are plotted
with source-backed coordinates. Abstract networks, products, forecasts,
organizations, and responses remain schematic. The Toledo intake-coordinate
discrepancy remains unresolved; no automated control, cyber architecture, or
future scenario layer is included.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_observation_system.py
.\.venv\Scripts\python.exe src\python\systems\validate_observation_system.py
Rscript src\R\systems\validate_observation_system.R .
```

## Phase 4B Information Dependencies & Governance

- [15 — Information dependencies & governance, 2026](outputs/maps/systems/15_information_dependencies_governance_2026.png)
- [Information dependency edges](data/processed/networks/information_dependency_edges.csv)
- [Information blind spots](data/processed/analysis/information_blind_spots.csv)
- [Decision authority matrix](data/processed/analysis/decision_authority_matrix.csv)
- [Information dependency matrix](outputs/figures/information_dependency_matrix_2026.png)
- [Sources](reports/information_dependency_sources.md)
- [Assumptions](reports/information_dependency_assumptions.md)
- [Governance findings](reports/information_governance_findings.md)
- [QA](reports/information_dependency_qa.md)

Phase 4B contains 20 qualitative information dependencies, 10 evidence-qualified
blind spots, four authority rows, and a 4 × 7 dependency matrix. It reuses the
Phase 4A observation baseline and keeps information availability, timeliness,
coverage, uncertainty, authority, jurisdiction, and public access distinct.
No cyberattack model, sensitive operational topology, automated decision
authority, or future scenario is included. Phase 4B is accepted and frozen;
Phase 4C uses it as an immutable factual baseline.

## Phase 4C Data, Sensors, Governance & Security Futures

Phase 4C is a separate qualitative scenario layer for 2050 and 2075. It does
not overwrite the factual Phase 4A/4B baselines and does not assign
probabilities. It is accepted and frozen; Phase 5A preserves it unchanged.

## Phase 5A Freight / Industry / Material Flows Baseline

Phase 5A is a modest factual 2026 baseline of major marine, rail, highway,
fuel-interface, industrial, agricultural, and material-flow functions. It does
not model shipment volumes, facility-specific routes, hazardous-material
routing, or future freight scenarios.

- [17 — Western Basin freight & industrial flow system, 2026](outputs/maps/systems/17_freight_industry_material_flows_2026.png)
- [Freight nodes](data/processed/networks/freight_system_nodes.csv)
- [Freight relationships](data/processed/networks/freight_system_edges.csv)
- [Commodity interfaces](outputs/figures/freight_commodity_interfaces_2026.png)
- [Sources](reports/freight_system_sources.md)
- [Assumptions](reports/freight_system_assumptions.md)
- [QA](reports/freight_system_qa.md)

Phase 5A contains 22 nodes and 26 relationships. Its Materials Corridor test
is **B — WEAKLY SUPPORTED**: network relationships exist, but the evidence does
not justify a polygon, named route, sixth macroregion, or continuous shipment
claim.

## Phase 5B Freight Evidence & Interchange Validation

Phase 5B contains a 20-record evidence crosswalk, 12 evidence-strengthened
relationships, and a nine-row interchange matrix. It confirms selected Port of
Toledo access and Ironville vessel/truck/rail functions, strengthens public
NS/CSX/CN port/corridor interfaces, and keeps W&LE, agricultural activity,
Woodville, Genoa, and Elmore access qualified or unresolved where evidence is
insufficient.

The automatic acceptance gate passed. Phase 5B is **ACCEPTED / FROZEN** under
`reports/phase5b_freight_evidence_freeze_manifest.json`. Map 18 and the Phase
5B tables are not replacements for the frozen Phase 5A network.

## Phase 5C Freight Dependencies & Critical Interfaces

Phase 5C is accepted and frozen as a separate factual 2026 qualitative
dependency layer. It contains 20 dependency edges, a 12-row dependency
register, six-row modal-substitutability and dependency matrices, and Map 19.
It distinguishes documented freight relationships, corridor access,
generalized logistics dependency, and unknown redundancy. It does not create
shipment quantities, exact routes, hazardous-material routing, sensitive
logistics topology, security targets, or future freight scenarios. Sol
acceptance was explicitly recorded by Sol under
`reports/phase5c_freight_dependency_freeze_manifest.json`.

- [19 — Freight dependencies & critical interfaces, 2026](outputs/maps/systems/19_freight_dependencies_critical_interfaces_2026.png)
- [Freight dependency edges](data/processed/networks/freight_dependency_edges.csv)
- [Freight dependency register](data/processed/analysis/freight_dependency_register.csv)
- [Modal substitutability matrix](data/processed/analysis/modal_substitutability_matrix.csv)
- [Dependency matrix](outputs/figures/freight_dependency_matrix_2026.png)
- [Sources](reports/freight_dependency_sources.md)
- [Assumptions](reports/freight_dependency_assumptions.md)
- [Findings](reports/freight_dependency_findings.md)
- [QA](reports/freight_dependency_qa.md)

## Phase 6A Ecology & Biodiversity Baseline

Phase 6A is the accepted and frozen factual 2026 ecological baseline. It
contains 16 ecology nodes, 20 ecology edges, three directly supported inventory
indicators, and Map 20. It establishes an ecological-system skeleton, not a
complete species inventory, population model, conservation ranking, risk score,
or future ecological scenario.

- [20 — Western Basin ecological system, 2026](outputs/maps/systems/20_ecological_system_2026.png)
- [Ecology nodes](data/processed/networks/ecology_system_nodes.csv)
- [Ecology edges](data/processed/networks/ecology_system_edges.csv)
- [Ecological indicators](data/processed/analysis/ecological_indicators_2026.csv)
- [Sources](reports/ecology_system_sources.md)
- [Assumptions](reports/ecology_system_assumptions.md)
- [Findings](reports/ecology_system_findings.md)
- [QA](reports/ecology_system_qa.md)

## Phase 6B Ecological Dependencies & Disturbances

Phase 6B adds 18 qualitative ecological dependency edges, a 10-record
disturbance register, a six-row resilience matrix, and Map 21 over the frozen
Phase 6A baseline. It distinguishes habitat, hydrologic, wetland, riparian,
migration, landscape, and condition interfaces. It does not create ecological-
risk scores, population models, exact movement routes, sensitive locations, or
future scenarios. Phase 6B is accepted and frozen. It is integrated under
`reports/phase6b_ecological_dependency_freeze_manifest.json`.

- [21 — Ecological dependencies & disturbances, 2026](outputs/maps/systems/21_ecological_dependencies_disturbances_2026.png)
- [Dependency edges](data/processed/networks/ecology_dependency_edges.csv)
- [Disturbance register](data/processed/analysis/ecological_disturbance_register.csv)
- [Resilience matrix](data/processed/analysis/ecological_resilience_matrix.csv)
- [Sources](reports/ecological_dependency_sources.md)
- [Assumptions](reports/ecological_dependency_assumptions.md)
- [Findings](reports/ecological_dependency_findings.md)
- [QA](reports/ecological_dependency_qa.md)

## Phase 6C Ecological Futures

Phase 6C is a separate qualitative 2050/2075 scenario layer over the frozen
Phase 6A baseline and validated Phase 6B implementation. It includes three
alternative families—Restored Connectivity, Managed Working Basin, and
High-Pressure Fragmented Basin—with explicit assumptions and no probabilities.
It does not add future population values, extinction events, disease/vector
ecology, precise sensitive locations, or a Great Black Swamp restoration
boundary. Phase 6C is implemented, validated, integrated, and awaits Sol
acceptance.

- [22 — Ecological futures, 2050](outputs/maps/systems/22_ecological_futures_2050.png)
- [22b — Ecological futures, 2075](outputs/maps/systems/22b_ecological_futures_2075.png)
- [Scenario comparison](outputs/figures/ecological_scenarios_comparison.csv)
- [Scenario sources](reports/ecology_scenario_sources.md)
- [Scenario assumptions](reports/ecology_scenario_assumptions.md)
- [Scenario consistency](reports/ecology_scenario_consistency.md)
- [Future worldbuilding](reports/ecology_future_worldbuilding.md)
- [Scenario QA](reports/ecology_scenario_qa.md)

## Phase 9 Climate & Natural Hazards System

Phase 9 is a distinct physical/environmental layer for western Lake Erie, the Maumee watershed, and Toledo/Northwest Ohio. The approved package covers extreme heat; heavy precipitation/flooding; drought/low water; Lake/coastal hazards; severe convective weather; and winter hazards in a compact 2026 baseline, followed by qualitative dependencies/resilience and three alternative 2050/2075 futures.

Phase 9 will not create a composite hazard score, deterministic hazard surface, health or demographic ranking, individual exposure or dose, comprehensive emergency-management model, or unsupported probability. Station, watershed, county, floodplain, shoreline, western Lake Erie, and regional climate-division scales remain distinct. Great Lakes seiche/wind setup is not described as ocean storm surge.

The three Phase 9 briefs are in [docs/phase_briefs](docs/phase_briefs/): `phase9a_climate_natural_hazards_baseline.md`, `phase9b_climate_hazard_dependencies_resilience.md`, and `phase9c_climate_hazard_futures.md`.

## Phase 9 Climate & Natural Hazards System

Phase 9A is **ACCEPTED / FROZEN** as the factual 2026 hazard baseline:
`data/processed/networks/climate_hazard_nodes.csv`,
`climate_hazard_edges.csv`, `data/processed/analysis/climate_hazard_observations.csv`,
and `climate_hazard_sources.csv`; Map 29 is the compact physical-hazard view.
Phase 9B adds qualitative dependency edges, a compound-event register,
resilience/control register, and dependency matrix; Map 30 is the schematic
cross-system view. Phase 9B is **ACCEPTED / FROZEN**. Phase 9C is a separate
qualitative 2050/2075 scenario layer and is **ACCEPTED / FROZEN**; it does not
modify the 2026 baselines.

Phase 9A reports are `reports/climate_hazard_sources.md`, `reports/climate_hazard_assumptions.md`,
`reports/climate_hazard_findings.md`, `reports/climate_hazard_qa.md`, and
`reports/climate_hazard_baseline_manifest.json`. Phase 9B reports are
`reports/climate_dependency_sources.md`, `reports/climate_dependency_assumptions.md`,
`reports/climate_dependency_findings.md`, `reports/climate_dependency_qa.md`, and
`reports/climate_dependency_manifest.json`. Neither layer creates a composite hazard
score, unsupported probability, health/social-vulnerability ranking, or
comprehensive emergency-management model.

Freeze manifests: `reports/phase9a_climate_natural_hazards_freeze_manifest.json`,
`reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json`,
and `reports/phase9c_climate_hazard_futures_freeze_manifest.json`. The
transparent correction history is recorded in
`reports/phase9a_correction_qa.md` and `reports/phase9_correction_qa.md`; the
final independent-review record is `reports/phase9_independent_review.md`.

## Phase 10 Governance, Jurisdiction & Decision Systems

Phase 10A and 10B are **ACCEPTED / FROZEN** as a factual/qualitative 2026 institutional layer. Phase 10C is **ACCEPTED / FROZEN** under `reports/phase10c_governance_futures_freeze_manifest.json` as a separate qualitative 2050/2075 governance-futures layer.

- [32 — Western Basin governance and jurisdiction, 2026](outputs/maps/systems/32_governance_jurisdiction_2026.png)
- [33 — Cross-system governance dependencies and coordination, 2026](outputs/maps/systems/33_cross_system_governance_dependencies_2026.png)
- [34 — Governance futures, 2050](outputs/maps/systems/34_governance_futures_2050.png)
- [34b — Governance futures, 2075](outputs/maps/systems/34b_governance_futures_2075.png)
- [Governance scenario assumptions](data/processed/scenarios/governance_scenario_assumptions.csv)
- [Governance scenario actor states](data/processed/scenarios/governance_actor_states_scenario.csv)
- [Governance scenario authority states](data/processed/scenarios/governance_authority_states_scenario.csv)
- [Governance scenario dependency states](data/processed/scenarios/governance_dependency_states_scenario.csv)
- [Governance scenario coordination states](data/processed/scenarios/governance_coordination_states_scenario.csv)
- [Governance scenario uncertainty states](data/processed/scenarios/governance_uncertainty_states_scenario.csv)
- [Governance scenario comparison](outputs/figures/governance_scenario_comparison.png)
- [Governance scenario manifest](reports/governance_scenario_manifest.json)
- [Governance scenario independent review](reports/governance_scenario_independent_review.md)
- [Phase 10C freeze manifest](reports/phase10c_governance_futures_freeze_manifest.json)
- [Governance actors](data/processed/analysis/governance_actors.csv)
- [Governance authority/role registry](data/processed/analysis/governance_authorities.csv)
- [Governance relationships](data/processed/networks/governance_relationships.csv)
- [Governance dependency register](data/processed/analysis/governance_dependency_register.csv)
- [Coordination mechanism register](data/processed/analysis/governance_coordination_mechanisms.csv)
- [Qualitative governance/dependency matrix](data/processed/analysis/governance_dependency_matrix.csv)
- [Phase 10A freeze manifest](reports/phase10a_governance_jurisdiction_freeze_manifest.json)
- [Phase 10B freeze manifest](reports/phase10b_governance_dependencies_coordination_freeze_manifest.json)
- [Phase 10 initial independent review](reports/governance_independent_review.md)
- [Phase 10 post-correction review](reports/governance_post_correction_independent_review.md)
- [Phase 10 additional post-correction review](reports/governance_additional_post_correction_independent_review.md)
- [Phase 10A findings](reports/governance_baseline_findings.md)
- [Phase 10B findings](reports/governance_dependency_findings.md)

The package keeps regulation, operation, ownership, monitoring, funding, advisory, permitting, scientific information, and private/public roles separate. It does not create jurisdiction polygons from vague descriptions, a composite governance score, a generalized governance-gap ranking, or partisan/election analysis. Phase 10C is the separate qualitative scenario layer and does not alter the factual 2026 package.

The correction lineage `e7d421c`, `d25d439`, `f613d3f`, and `e1f233c` remains visible and unrevised. The accepted review records identify `deleg_2e8d515e` and `deleg_eedc4116` as passed with no blocking findings.

Rebuild and validate the governance layers from the repository root:

```powershell
.\\venv\\Scripts\\python.exe src\\python\\systems\\build_governance_baseline.py
.\\venv\\Scripts\\python.exe src\\python\\systems\\validate_governance_baseline.py
Rscript src\\R\\systems\\validate_governance_baseline.R .
.\\venv\\Scripts\\python.exe src\\python\\systems\\build_governance_dependencies.py
.\\venv\\Scripts\\python.exe src\\python\\systems\\validate_governance_dependencies.py
Rscript src\\R\\systems\\validate_governance_dependencies.R .
```


## Phase 11 Population & Settlement Dynamics

Phase 11A and 11B are implemented and validated on the feature branch, awaiting independent review, integration, and Sol acceptance. Phase 11C is approved scope only and is not implemented.

- [35 — Population & settlement system, 2026](outputs/maps/systems/35_population_settlement_2026.png)
- [36 — Population, mobility & system dependencies, 2026](outputs/maps/systems/36_population_mobility_dependencies_2026.png)
- [Population and settlement nodes](data/processed/analysis/population_settlement_nodes.csv)
- [Population and settlement observations](data/processed/analysis/population_settlement_observations.csv)
- [Population and settlement relationships](data/processed/networks/population_settlement_relationships.csv)
- [Population mobility observations](data/processed/analysis/population_mobility_observations.csv)
- [Population mobility relationships](data/processed/networks/population_mobility_relationships.csv)
- [Population system dependency register](data/processed/analysis/population_system_dependency_register.csv)
- [Population system dependency matrix](data/processed/analysis/population_system_dependency_matrix.csv)
- [Phase 11A baseline manifest](reports/population_settlement_baseline_manifest.json)
- [Phase 11 working manifest](reports/phase11_working_manifest.json)
- [Phase 11A brief](docs/phase_briefs/phase11a_population_settlement_baseline.md)
- [Phase 11B brief](docs/phase_briefs/phase11b_population_mobility_dependencies.md)
- [Phase 11C approved-scope brief](docs/phase_briefs/phase11c_population_settlement_futures.md)

The package preserves person/household/housing-unit/density/worker/job/commuter distinctions, residence/workplace and commuting/migration boundaries, mixed Census/ACS/PEP/LODES vintages, and generalized service/dependency interfaces. It creates no vulnerability or environmental-justice score, protected-class ranking, individual movement model, health outcome, exact utility territory, unsupported forecast, or future population layer.

```text
assets/                 exploratory concept art and archived generated maps
data/raw/               cached public-source responses; large reproducible extracts may be ignored
data/processed/         GeoPackage (current development in Git LFS) and network tables
docs/                   canon, worldbuilding, research, references, prompts
metadata/               systems, sources, and scenario assumptions
outputs/maps/systems/   validated PNG/SVG analytical map pairs
outputs/figures/        network and independent R validation renders
reports/                handoff, QA, sources, assumptions, import status
outputs/qa/              review-only historical geometry and QA maps
src/python/qa/           reproducible follow-up QA builders
src/R/qa/                independent follow-up QA validation/rendering
src/python/systems/     Python acquisition, construction, rendering, validation
src/R/systems/          independent R validation and render scripts
src/game/               retained interactive prototype and tests
```

## Retained Interactive Prototype

The Vite/TypeScript application is **Glasspunk: Blackout at Vesper Station**, a compact, accessible browser-game prototype set in the fictional world. It demonstrates one possible fiction/game use of the Western Basin setting and is separate from the systems-atlas pipelines; it is intentionally retained with its 22 tests.

## Reproducing Phase 1

Commands below are repository-relative and reflect the current scripts.

### Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-systems.txt
```

### Validate committed artifacts

```powershell
.\.venv\Scripts\python.exe src\python\systems\validate_water_system.py
Rscript src\R\systems\validate_water_system.R .
Rscript src\R\systems\render_water_system.R .
```

### Rebuild Phase 1

The builder uses cached public-service responses under `data/raw/` when present. Refreshing missing caches requires internet access to the documented source services.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_water_system.py `
  --historical-swamp-image docs\references\images\great_black_swamp_reference_non_georeferenced.jpeg
```

The historical image is an inset reference only. The builder does not digitize it.

### Rebuild the Great Black Swamp review package

This command reads the preserved official ODNR archive and cached USGS/Census context. It writes only under `outputs/qa/` and `reports/`; it does not update the canonical GeoPackage.

```powershell
.\.venv\Scripts\python.exe src\python\qa\build_great_black_swamp_review.py
```

### Rebuild and validate the physical hydrography review package

The large raw 3DHP snapshot is intentionally excluded from Git and Git LFS. If it is absent, the builder reconstructs `data/raw/usgs/3dhp_flowlines_maumee_buffer500m.geojson.gz` from the official FeatureServer using the exact HUC-12 project extent plus 500 m buffer and ordered 2,500-record pagination. The tracked manifest records the expected 102,757-feature snapshot and SHA-256 `365A043ACCED9DC70CBEAEC804408A8539E3C372E3B4F64B962C03DB047EBD60`; service changes can therefore be detected rather than silently accepted.

The current-development `data/processed/glasspunk_base.gpkg` is retained through a path-specific Git LFS rule. Historical v0.1 commits and the `v0.1-water-system` tag are not migrated.

```powershell
.\.venv\Scripts\python.exe src\python\qa\build_physical_hydrography_review.py
.\.venv\Scripts\python.exe src\python\qa\validate_physical_hydrography_review.py
Rscript src\R\qa\validate_physical_hydrography.R .
```

After an explicit B decision, current-development integration is performed separately:

```powershell
.\.venv\Scripts\python.exe src\python\qa\integrate_physical_hydrography.py
```

### Validate the retained application prototype

```powershell
npm ci
npm test -- --run
```

## Data Provenance

Primary sources include USGS WBD and NHDPlus HR, USFWS National Wetlands Inventory, US EPA Maumee and Lake Erie material, NOAA HAB science, GLOS/IOOS, the City of Toledo, and Ohio EPA. Exact endpoints, retrieval dates, limitations, and confidence are recorded in [metadata/sources.yml](metadata/sources.yml) and [reports/water_system_sources.md](reports/water_system_sources.md).

Feature status distinguishes:

- `reality_status`: real, historical, fictional
- `canon_status`: verified, inferred, scenario, experimental

## Known QA Issues and Dispositions

Open or qualified Phase 1 items:

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry

The Great Black Swamp image is non-georeferenced. Full-basin upstream connectors encode WBD `tohuc` topology and are visibly/documentarily marked inferred; they are not physical river geometry.

For item 2, source acquisition and candidate QA are complete, but the gate remains open: no directly documented official named-swamp vector was found, and the Gordon/ODNR review candidate is **HOLD / not canonical**.

Physical replacement for inferred upstream WBD routing connectors is resolved for current development under **B — ACCEPT WITH QUALIFICATION**. The 12 remaining project-derived links are explicitly abstract, non-hydrographic routing edges pending local outlet review.

## Worldbuilding, Research, and References

The original ChatGPT Project exports are preserved as received. They may contain older exploratory terminology; [current canon status](docs/canon_status.md) governs wherever an imported document conflicts with the current five-region model.

### Worldbuilding

- [Original Glasspunk Toledo project outline](docs/worldbuilding/Glasspunk_Toledo_Project_Outline.md)
- [Current regional and systems atlas](docs/worldbuilding/Glasspunk_Regional_and_Systems_Atlas_v0.1.md)
- [Geology, strategic materials, and Codex prompts](docs/worldbuilding/Glasspunk_Geology_Strategic_Materials_Addendum_and_Codex_Prompts.md) — planning specification interpreted through the implemented Phase 2A–2C baseline

### Research

- [Indigenous Peoples' History](docs/research/Glasspunk_Indigenous_Peoples_History.md) — a separate, sourced research module; no historical GIS reconstruction has begun
- [Great Black Swamp History](docs/research/Great_Black_Swamp_History.md) — imported contextual deep-history research; it does not supersede the geometry QA review or authorize the held candidate

### References

- [Worldbuilding references](docs/references/Glasspunk_Worldbuilding_References.md) — access notes, reading order, and project-specific lessons
- [ChatGPT Project import status](reports/chatgpt_project_import_status.md)

## Concept Art

Three sketchbook sheets are preserved under [assets/concept_art](assets/concept_art). Generated regional-map experiments are archived under [assets/concept_maps/archive](assets/concept_maps/archive) and explicitly marked non-authoritative. They must not be used to derive coordinates or geometry.

## Roadmap

1. Maintain the accepted project packages while preserving Phase 3A and Phase 3B as accepted/validated/frozen factual 2026 baselines and Phase 3C as separate accepted/validated future-scenario work
2. Preserve Phase 4A and Phase 4B as separate factual 2026 information layers; Phase 4B remains implemented/validated and awaits Sol acceptance
3. Resolve or explicitly scope the remaining Phase 1 QA gates: Toledo intake coordinates, authoritative Great Black Swamp geometry, and 12 unresolved abstract routing relationships
4. Continue the Lower Maumee/Ottawa historical GIS research and review imported material against the explicit canon hierarchy
5. Do not begin Phase 4C or future information-governance scenarios without separate approval

## Licensing / Attribution

Original code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, maps, imagery, and concept assets retain their original terms and are not relicensed by MIT. See [Data and Asset Licensing](docs/references/DATA_AND_ASSET_LICENSING.md) and preserve source attribution.

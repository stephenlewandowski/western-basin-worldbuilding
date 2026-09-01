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

**Phase 3C — COMPLETE / VALIDATED (ENERGY / GRID / COMPUTE FUTURES)**

Phase 1 contains seven Maumee basin HUC-8 watersheds, 252 HUC-12 subwatersheds, 864 physical Lower Maumee flowlines, 251 explicitly inferred WBD routing connectors, 608 NWI freshwater wetlands, 14 system nodes, and 15 dependency edges.

See [PROJECT_STATUS.md](PROJECT_STATUS.md) and the [Phase 1 handoff](reports/water_system_phase1_handoff.md).

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

## Repository Structure

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

1. Human review of the Phase 1 repository and open QA gates
2. Review the imported worldbuilding, research, and reference documents against the explicit canon hierarchy
3. Reconcile intake and historical swamp geography
4. Preserve Phase 2A–2C as the immutable factual materials and historical-exposure baseline
5. Review Phase 2D's three alternative 2050/2075 futures before beginning another detailed system

The speculative 2050 materials system, detailed energy/freight systems, and Materials Corridor geometry remain deferred.

## Licensing / Attribution

Original code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, maps, imagery, and concept assets retain their original terms and are not relicensed by MIT. See [Data and Asset Licensing](docs/references/DATA_AND_ASSET_LICENSING.md) and preserve source attribution.

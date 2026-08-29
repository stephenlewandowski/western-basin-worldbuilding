# Western Basin Worldbuilding

*Science-informed speculative worldbuilding for Toledo, Northwest Ohio, the Maumee watershed, and western Lake Erie.*

This repository combines real-world geographic baselines, environmental and infrastructure systems modeling, scenario analysis, speculative regional worldbuilding, history, maps, concept art, and foundations for future fiction, games, and interactive-atlas work.

The repository is named **Western Basin Worldbuilding** so the long-term project is not locked to one setting title. **Glasspunk** is the current working genre and aesthetic terminology. **Cyberglass** is earlier or possible in-world terminology. The final fictional-world title remains open.

> **Core principle:** REAL GEOGRAPHY FIRST; FICTIONAL INTERPRETATION SECOND.

## Project Status

**Phase 1 — COMPLETE**  
**Water System v0.1 — COMPLETE / VALIDATED**  
**Phase 2A — BASELINE BUILT / QA PASSED / AWAITING HUMAN REVIEW**

Phase 1 contains seven Maumee basin HUC-8 watersheds, 252 HUC-12 subwatersheds, 864 physical Lower Maumee flowlines, 251 explicitly inferred WBD routing connectors, 608 NWI freshwater wetlands, 14 system nodes, and 15 dependency edges.

See [PROJECT_STATUS.md](PROJECT_STATUS.md), the [Phase 1 handoff](reports/water_system_phase1_handoff.md), and the [Phase 2A QA gate](reports/materials_system_qa.md).

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

## Phase 2A Materials Baseline

Phase 2A adds the first real-world geology, industrial-mineral, strategic-processing, and legacy-remediation layers without changing Phase 1. It distinguishes local carbonate extraction/processing near Woodville and Genoa from nonlocal beryllium feed processed at Elmore, and classifies Luckey as federal legacy cleanup rather than active production.

- [06 — Geology + strategic materials, 2026 baseline](outputs/maps/systems/06_geology_resources_2026.png)
- [Materials source register](reports/materials_system_sources.md)
- [Materials QA and human-review gate](reports/materials_system_qa.md)

Map 06 is also available as SVG. No speculative corridor polygon, groundwater-flow direction, production/reserve quantity, future scenario, Map 07–10 product, or Phase 2 release is included.

## Repository Structure

```text
assets/                 exploratory concept art and archived generated maps
data/raw/               cached public-source responses used by Phase 1
data/processed/         GeoPackage and network tables
docs/                   canon, worldbuilding, research, references, prompts
metadata/               systems, sources, and scenario assumptions
outputs/maps/systems/   validated PNG/SVG analytical map pairs
outputs/figures/        network and independent R validation renders
reports/                handoff, QA, sources, assumptions, import status
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

### Rebuild and validate Phase 2A

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_materials_system.py
Rscript src\R\systems\validate_materials_system.R .
Rscript src\R\systems\render_materials_system.R .
.\.venv\Scripts\python.exe src\python\systems\validate_materials_system.py
```

The Phase 2A builder appends/replaces only Phase 2 layers in the shared GeoPackage and checks that all Phase 1 layers remain present.

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

## Known QA Issues

The open Phase 1 gates remain tracked while Phase 2A is held for review:

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry
3. physical replacement for inferred upstream WBD routing connectors

The Great Black Swamp image is non-georeferenced. Full-basin upstream connectors encode WBD `tohuc` topology and are visibly/documentarily marked inferred; they are not physical river geometry.

## Worldbuilding, Research, and References

The original ChatGPT Project exports are preserved as received. They may contain older exploratory terminology; [current canon status](docs/canon_status.md) governs wherever an imported document conflicts with the current five-region model.

### Worldbuilding

- [Original Glasspunk Toledo project outline](docs/worldbuilding/Glasspunk_Toledo_Project_Outline.md)
- [Current regional and systems atlas](docs/worldbuilding/Glasspunk_Regional_and_Systems_Atlas_v0.1.md)
- [Geology, strategic materials, and Codex prompts](docs/worldbuilding/Glasspunk_Geology_Strategic_Materials_Addendum_and_Codex_Prompts.md) — governing specification for the Phase 2A baseline and later review-gated work

### Research

- [Indigenous Peoples' History](docs/research/Glasspunk_Indigenous_Peoples_History.md) — a separate, sourced research module; no historical GIS reconstruction has begun

### References

- [Worldbuilding references](docs/references/Glasspunk_Worldbuilding_References.md) — access notes, reading order, and project-specific lessons
- [ChatGPT Project import status](reports/chatgpt_project_import_status.md)

## Concept Art

Three sketchbook sheets are preserved under [assets/concept_art](assets/concept_art). Generated regional-map experiments are archived under [assets/concept_maps/archive](assets/concept_maps/archive) and explicitly marked non-authoritative. They must not be used to derive coordinates or geometry.

## Roadmap

1. Human review of the Phase 1 repository and open QA gates
2. Review the imported worldbuilding, research, and reference documents against the explicit canon hierarchy
3. Reconcile intake and historical swamp geography
4. Human review of the Phase 2A Map 06 classifications, facility precision, and carbonate filter
5. After approval, design the carbonate and beryllium network maps without assuming a corridor polygon

Detailed Phase 2 future modeling remains outside the v0.1 water release and is not included in Phase 2A.

## Licensing / Attribution

Original code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, maps, imagery, and concept assets retain their original terms and are not relicensed by MIT. See [Data and Asset Licensing](docs/references/DATA_AND_ASSET_LICENSING.md) and preserve source attribution.

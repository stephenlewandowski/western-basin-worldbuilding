# Western Basin Worldbuilding

*Science-informed speculative worldbuilding for Toledo, Northwest Ohio, the Maumee watershed, and western Lake Erie.*

This repository combines real-world geographic baselines, environmental and infrastructure systems modeling, scenario analysis, speculative regional worldbuilding, history, maps, concept art, and foundations for future fiction, games, and interactive-atlas work.

The repository is named **Western Basin Worldbuilding** so the long-term project is not locked to one setting title. **Glasspunk** is the current working genre and aesthetic terminology. **Cyberglass** is earlier or possible in-world terminology. The final fictional-world title remains open.

> **Core principle:** REAL GEOGRAPHY FIRST; FICTIONAL INTERPRETATION SECOND.

## Project Status

**Phase 1 — COMPLETE**  
**Water System v0.1 — COMPLETE / VALIDATED**  
**Phase 2 — NOT STARTED**

Phase 1 contains seven Maumee basin HUC-8 watersheds, 252 HUC-12 subwatersheds, 864 physical Lower Maumee flowlines, 251 explicitly inferred WBD routing connectors, 608 NWI freshwater wetlands, 14 system nodes, and 15 dependency edges.

See [PROJECT_STATUS.md](PROJECT_STATUS.md) and the [Phase 1 handoff](reports/water_system_phase1_handoff.md).

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

Phase 2 must not proceed past review without addressing:

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry
3. physical replacement for inferred upstream WBD routing connectors

The Great Black Swamp image is non-georeferenced. Full-basin upstream connectors encode WBD `tohuc` topology and are visibly/documentarily marked inferred; they are not physical river geometry.

## Worldbuilding Documents

The expected ChatGPT Project Markdown exports were unavailable during migration and were not reconstructed. Their status and intended destinations are recorded in [reports/chatgpt_project_import_status.md](reports/chatgpt_project_import_status.md).

Current working canon is documented independently so older exploratory concepts can be preserved without being silently rewritten.

## Concept Art

Three sketchbook sheets are preserved under [assets/concept_art](assets/concept_art). Generated regional-map experiments are archived under [assets/concept_maps/archive](assets/concept_maps/archive) and explicitly marked non-authoritative. They must not be used to derive coordinates or geometry.

## Roadmap

1. Human review of the Phase 1 repository and open QA gates
2. Import the missing original ChatGPT Project Markdown exports
3. Reconcile intake and historical swamp geography
4. Plan Phase 2: Geology / Minerals / Strategic Materials
5. Evaluate the Woodville–Elmore–Luckey Materials Corridor as a system/corridor concept

Detailed Phase 2 modeling is intentionally not included in v0.1.

## Licensing / Attribution

Original code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, maps, imagery, and concept assets retain their original terms and are not relicensed by MIT. See [Data and Asset Licensing](docs/references/DATA_AND_ASSET_LICENSING.md) and preserve source attribution.

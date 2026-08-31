# Project Status

Last reviewed: 2026-08-31

## PHASE 1 — COMPLETE

**Water System v0.1: COMPLETE / VALIDATED**

The repository contains the validated Phase 1 analytical atlas, GeoPackage, water-network tables, network diagram, source and assumptions reports, reproducible builders, and Python/R validators.

Validated inventory:

- 7 HUC-8 watersheds
- 252 HUC-12 subwatersheds
- 864 physical Lower Maumee flowlines
- 251 explicitly inferred WBD routing connectors
- 608 NWI freshwater wetlands
- 14 system nodes
- 15 dependency edges

## PHASE 2 — NOT STARTED

**Geology / Minerals / Strategic Materials: PLANNED**

No detailed Phase 2 modeling has begun. The Woodville–Elmore–Luckey Materials Corridor is a possible future system/corridor concept, not a sixth macroregion.

## Open Phase 1 QA gates

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

Great Black Swamp historical geometry: Phase 1 QA research is complete. Official ODNR dataset 3135 was preserved and audited; a Gordon (1966) class-4 candidate was produced and validated under `outputs/qa/`. Human decision: **C — HOLD**. The method is resolved, the geometry remains a noncanonical candidate, and the direct official extent source gap remains open. This item no longer blocks current Water System or Phase 2 development. See [the geometry source review](reports/great_black_swamp_geometry_source_review.md).

Physical hydrography replacement: Phase 1 QA and integration are complete. Human decision: **B — ACCEPT WITH QUALIFICATION**. Current development adopts separate USGS 3DHP physical and official-connector layers plus 12 explicitly abstract unresolved routing edges. The historical v0.1 release and Map 01–05 artifacts remain unchanged. See [the reconciliation report](reports/physical_hydrography_reconciliation.md).

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

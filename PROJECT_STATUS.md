# Project Status

Last reviewed: 2026-08-29

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
3. physical replacement for inferred upstream WBD routing connectors

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

Great Black Swamp source research is complete enough for human review: official ODNR dataset 3135 was preserved and audited, no documented direct official named-swamp vector was located, and a review-only Gordon (1966) class-4 candidate was generated under `outputs/qa/`. The candidate is **HOLD / not canonical** and the QA gate remains open pending an A/B/C/D decision. See [the geometry source review](reports/great_black_swamp_geometry_source_review.md).

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

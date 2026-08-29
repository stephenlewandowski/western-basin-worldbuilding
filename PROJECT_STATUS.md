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

## PHASE 2 — IN PROGRESS / HUMAN REVIEW GATE

**Phase 2A — Geology / Minerals / Strategic Materials 2026 Baseline: BUILT / QA PASSED / AWAITING HUMAN REVIEW**

The repository now contains the first real-world Phase 2 baseline: Ohio DNR bedrock and carbonate occurrence, three verified industrial-mineral sites, Materion Elmore as nonlocal-feed advanced processing, Luckey as legacy remediation, Map 06, provenance, and Python/R QA. No detailed future scenario has begun. The Woodville–Elmore–Luckey Materials Corridor remains a possible future system/corridor concept, not a mapped polygon and not a sixth macroregion.

Phase 2A stops for human review. Maps 07–10 and a Phase 2 release have not been created.

## Open Phase 1 QA gates

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry
3. physical replacement for inferred upstream WBD routing connectors

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

The gates are tracked in GitHub Issues #1–#3 under the **Phase 2 — Geology / Minerals / Strategic Materials** milestone.

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

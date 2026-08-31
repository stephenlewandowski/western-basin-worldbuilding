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

## PHASE 2A–2B — COMPLETE

**Geology / Minerals / Strategic Materials 2026 baseline: COMPLETE / VALIDATED**

**Material Flows 2026 baseline: COMPLETE / VALIDATED**

Phase 2A supplies generalized ODNR bedrock/carbonate context, three industrial-mineral sites, Materion Elmore advanced processing, Luckey remediation, and Map 06. Phase 2B adds a shared 25-node/26-edge carbonate and beryllium graph, a 14-record source registry, GeoPackage spatial nodes, and Maps 07–08.

Elmore is advanced strategic-material processing with nonlocal feed, not a mine. Luckey is legacy/remediation, not current production. Broad functional and sector links are explicitly inferred; named CFS and Kairos relationships retain dates and source/status qualifications. Phase 2B itself introduced no route, quantity, groundwater surface, Materials Corridor polygon, Map 09/10, or future scenario.

## PHASE 2C — COMPLETE

**Strategic Materials, Exposure & Remediation History: COMPLETE / VALIDATED**

Phase 2C adds Map 09, 30 source-grounded historical/remediation events, 9
substance records, 7 qualified pathway records, 13 dedicated sources, and a
5-node/5-edge bridge from Materials to coarse Exposure / Environmental Health
interfaces. The full shared graph is now 30 nodes and 31 edges.

Luckey historical production, Luckey current remediation, and Elmore current
advanced processing remain separate. The model asserts zero documented
individual exposures, no direct Luckey–Elmore production flow, and no invented
contamination polygon, groundwater plume, exposure radius, route, or Map 10.

## PHASE 2D — COMPLETE

**Alternative Materials Futures 2050/2075: COMPLETE / VALIDATED**

Phase 2D adds 30 formal assumptions, 48 scenario-node states, 36 scenario
relationships, Map 10 (2050), Map 10b (2075), and a qualitative comparison.
All future objects are separate fictional deltas; the factual 2026 materials
graph remains byte-identical at 30 nodes and 31 relationships.

The Materials Corridor result is **B — EMERGES WEAKLY** in the circular and
high-convergence futures. It remains a network interpretation, not a polygon,
region, route, or jurisdiction.

## PHASE 3A — COMPLETE

**Energy / Grid / Compute Baseline, 2026: COMPLETE / VALIDATED**

Phase 3A adds Map 11, 18 nodes, and 17 qualified edges: 9 generation assets,
2 nonspatial regional grid interfaces, 2 storage assets, 4 selected major
water/industrial loads, and 1 documented 5 MW compute project with unverified
operating status. The map includes 43 public EIA/HIFLD in-service transmission
features at 230 kV or higher as cartographic context. It is not a power-flow,
congestion, transfer-capability, substation, or feeder model. No future energy
scenario is included.

## Open Phase 1 QA gates

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

Great Black Swamp historical geometry: Phase 1 QA research is complete. Official ODNR dataset 3135 was preserved and audited; a Gordon (1966) class-4 candidate was produced and validated under `outputs/qa/`. Human decision: **C — HOLD**. The method is resolved, the geometry remains a noncanonical candidate, and the direct official extent source gap remains open. This item no longer blocks current Water System or Phase 2 development. See [the geometry source review](reports/great_black_swamp_geometry_source_review.md).

Physical hydrography replacement: Phase 1 QA and integration are complete. Human decision: **B — ACCEPT WITH QUALIFICATION**. Current development adopts separate USGS 3DHP physical and official-connector layers plus 12 explicitly abstract unresolved routing edges. The historical v0.1 release and Map 01–05 artifacts remain unchanged. See [the reconciliation report](reports/physical_hydrography_reconciliation.md).

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

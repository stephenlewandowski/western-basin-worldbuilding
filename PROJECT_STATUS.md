# Project Status

Last reviewed: 2026-09-02

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

## PHASE 3A — ACCEPTED / FROZEN

**Energy / Grid / Compute Baseline, 2026: ACCEPTED / VALIDATED**

Phase 3A adds Map 11, 18 nodes, and 17 qualified edges: 9 generation assets,
2 nonspatial regional grid interfaces, 2 storage assets, 4 selected major
water/industrial loads, and 1 documented 5 MW compute project with unverified
operating status. The map includes 43 public EIA/HIFLD in-service transmission
features at 230 kV or higher as cartographic context. It is not a power-flow,
congestion, transfer-capability, substation, or feeder model. No future energy
scenario is included.

Map 11 and the Phase 3A node/edge tables are frozen and regression-protected by
`reports/phase3a_freeze_manifest.json`. Phase 3A remains 18 nodes and 17 coarse
relationships; Phase 3B uses these IDs without modifying the accepted baseline.

## PHASE 3B — ACCEPTED / FROZEN

**Critical Energy Dependencies & Reliability, 2026**

Phase 3B adds 28 qualitative cross-system dependency edges and five generalized
dependency nodes, a 10 × 7 ordinal dependency matrix, Map 12, and source,
assumption, findings, and QA reports. The layer connects energy to water,
materials, and planned/unverified compute; generalized fuel, cooling/water,
weather, storage-support, and communications dependencies are represented.
No power-flow, outage-probability, contingency, congestion, transfer-limit, or
future-energy analysis is included.

Phase 3B is formally **ACCEPTED / FROZEN** as the validated 2026 cross-system
dependency baseline. Map 12, the dependency node/edge tables, matrix, source
registry, and principal reports are hash-protected by
`reports/phase3b_freeze_manifest.json`. Phase 3C may use these artifacts but
must not modify them.

## PHASE 3C — ACCEPTED

**Energy / Grid / Compute Futures, 2050 and 2075: ACCEPTED / VALIDATED**

Phase 3C uses separate scenario assumptions and node/edge deltas. The factual
2026 Phase 3A and accepted Phase 3B layers remain unchanged. The completed
package contains 36 assumptions, 114 scenario node states, 114 scenario edge
deltas, six A/B/C horizon states, Maps 13/13b, and a qualitative comparison.
No precise future MW, route, facility, probability, or power-flow claim is made.

Phase 3C is formally **ACCEPTED** as the validated alternative-futures package.

## PHASE 4A — ACCEPTED / FROZEN

**Data, Sensors & Decision Infrastructure Baseline, 2026**

Phase 4A adds Map 14, a simple 25-node/21-relationship observation-to-decision
baseline across four representative public-information chains: Lake Erie/HAB/
drinking water, Lower Maumee hydrology/flood, environmental/regulatory
reporting, and energy information. The package includes two source-backed
geolocated public stations: the GLOS Toledo crib dataset coordinate and USGS
04193500 at Waterville. Abstract networks, data products, forecasts, decision
organizations, and responses remain schematic.

The GLOS coordinate is not adopted as the sole physical Toledo intake
coordinate. The existing Toledo intake-coordinate discrepancy remains
unresolved. Phase 4A adds no exhaustive sensor inventory, automated-control
relationship, SCADA/cyber architecture, sensitive telemetry, AI decision
authority, or 2050/2075 scenario content. The accepted/frozen Phase 3A and
Phase 3B factual 2026 baselines, and the accepted/validated Phase 3C future
scenarios, remain separate and unchanged.

Python and independent R validation passed. The Phase 4A artifact check is
recorded in `reports/observation_system_artifact_check.json`; the source,
assumption, and QA boundaries are recorded in
`reports/observation_system_sources.md`,
`reports/observation_system_assumptions.md`, and
`reports/observation_system_qa.md`.

Phase 4A is formally **ACCEPTED / FROZEN**. Its Map 14 and observation-system
tables are protected by the Phase 4A validation and remain immutable under later
scenario phases.

## PHASE 4B — ACCEPTED / FROZEN

**Information Dependencies, Blind Spots & Governance, 2026**

Phase 4B adds a separate analytical layer over the Phase 4A observation
baseline: 20 qualitative information dependencies, 10 evidence-qualified blind
spots, a four-row decision-authority matrix, a 4 × 7 information-dependency
matrix, and Map 15. It reuses Phase 4A node IDs and does not alter the Phase 4A
tables or Map 14.

The layer distinguishes observation, data, analysis/forecast, decision
authority, and response from availability, timeliness, coverage, uncertainty,
jurisdiction, stewardship, and public/operational access. Blind spots are
recorded as information gaps or uncertainty, not vulnerabilities or evidence
of failure. Public energy information remains high-level.

Phase 4B contains no cyberattack model, attack path, sensitive operational
topology, SCADA/control architecture, privacy-impact assessment, AI decision
authority, surveillance-state scenario, fictional sensor network, or future
scenario. It is formally **ACCEPTED / FROZEN** by explicit Sol decision.

The machine-readable result is `reports/phase4b_information_freeze_manifest.json` and
`reports/information_dependency_artifact_check.json`;
the source, assumption, findings, and QA boundaries are recorded in
`reports/information_dependency_sources.md`,
`reports/information_dependency_assumptions.md`,
`reports/information_governance_findings.md`, and
`reports/information_dependency_qa.md`.

## PHASE 4C — ACCEPTED / FROZEN

**Data, Sensors, Governance & Security Futures, 2050 / 2075**

Phase 4C implements three separate qualitative scenario families over the frozen
Phase 4A/4B 2026 baselines: Trusted Public Infrastructure, Federated Resilience,
and High-Automation / Contested Information. The package contains six horizon
states, 36 assumptions, 72 scenario node states, 48 scenario edge deltas, 36
blind-spot states, six authority states, Maps 16/16b, and a qualitative
comparison. Future objects remain separate scenario deltas with explicit
assumptions, provenance, and human decision authority. No Phase 4C future
object enters the factual baseline.

Phase 4C is formally **ACCEPTED / FROZEN** by explicit Sol decision. Its
scenario content and principal artifacts are protected by
`reports/phase4c_information_freeze_manifest.json`.

## PHASE 5A — ACCEPTED / FROZEN

**Freight / Industry / Material Flows Baseline, 2026**

Phase 5A implements a modest factual baseline of documented freight corridors,
major industrial/material nodes, agricultural/bulk functions, and generalized
external-market interfaces. The package contains 22 freight nodes, 26 freight
relationships, a bounded 1,221-feature public Class I rail extract, Map 17, and
an optional commodity-interface figure.

The model distinguishes documented corridors, documented flows, interchange,
generalized supply-chain relationships, and engineering logistics dependencies.
It does not infer shipment quantities, exact facility-to-facility routes,
hazardous-material routing, pipeline capacity, sensitive logistics topology, or
future freight scenarios.

The Materials Corridor test is **B — WEAKLY SUPPORTED**. Woodville, Genoa,
Elmore, Luckey, Toledo, and the regional freight structure support a network
interpretation, but not a polygon, named route, sixth macroregion, or continuous
commercial shipment chain. Phase 5A is formally **ACCEPTED / FROZEN** under
`reports/phase5a_freight_freeze_manifest.json`.

## PHASE 5B — ACCEPTED / FROZEN

**Freight Evidence & Interchange Validation, 2026**

Phase 5B adds a 20-record evidence crosswalk, 12 evidence-strengthened
relationships, a nine-row interchange matrix, and Map 18. It strengthens
documented Port of Toledo access, selected marine/rail/highway interfaces, and
Ironville movement evidence while preserving unresolved or generalized
relationships for W&LE, agricultural activity, Woodville, Genoa, and Elmore.

The Materials Corridor determination is **B — FREIGHT EVIDENCE PROVIDES WEAK
SUPPORT**. The evidence supports a loose industrial/material network, not a
coherent geographic corridor, route, polygon, jurisdiction, or sixth macroregion.
Phase 5B is formally **ACCEPTED / FROZEN** under
`reports/phase5b_freight_evidence_freeze_manifest.json`.

## PHASE 5C — ACCEPTED / FROZEN

**Freight Dependencies & Critical Interfaces, 2026**

Phase 5C is a separate qualitative dependency layer over the frozen Phase 5A
and Phase 5B baselines. It distinguishes mode/gateway dependency, interchange,
modal alternatives, external-market orientation, and unknown redundancy without
creating a security-target model or future freight scenario. The package
contains 20 dependency edges, 12 dependency-register rows, two 6-row × 7-
dimension qualitative matrices, Map 19, source/assumption/findings/QA reports,
and independent Python/R validation. Phase 5C is formally **ACCEPTED / FROZEN**
by explicit Sol decision under `reports/phase5c_freight_dependency_freeze_manifest.json`.

## PHASE 6A — ACCEPTED / FROZEN

**Ecology & Biodiversity Baseline, 2026**

Phase 6A establishes a modest factual ecological-system skeleton for western
Lake Erie, the Maumee/tributary/floodplain system, coastal wetlands, the modern
Black Swamp legacy/agricultural matrix, terrestrial habitat, and migratory or
mobile-species functions. The package contains 16 ecology nodes, 20 ecology
edges, three directly supported inventory indicators, Map 20, and independent
Python/R validation. It does not canonicalize the held Great Black Swamp
candidate, expose sensitive species locations, or create future ecological
scenarios. Phase 6A is formally **ACCEPTED / FROZEN** by explicit Sol decision under
`reports/phase6a_ecology_freeze_manifest.json`.

## PHASE 6B — ACCEPTED / FROZEN

**Ecological Dependencies, Disturbances & Resilience, 2026**

Phase 6B adds 18 qualitative ecological dependency edges, a 10-record
disturbance register, a six-row × 10-column resilience matrix, Map 21, and
source/assumption/findings/QA reports over the Phase 6A skeleton. It records
habitat, hydrologic, wetland, riparian, migration, landscape, and condition
interfaces without creating ecological-risk scores, population models,
species-sensitive locations, exact movement routes, or future scenarios. Phase
6B is formally **ACCEPTED / FROZEN** by explicit Sol decision under
`reports/phase6b_ecological_dependency_freeze_manifest.json`.

## PHASE 6C — ACCEPTED / FROZEN

**Ecological Futures, 2050 / 2075**

Phase 6C contains 18 qualitative scenario assumptions, 36 scenario node states,
30 scenario edge states, 36 disturbance states, 36 resilience states, 72
comparison rows, Maps 22/22b, and scenario reports. It preserves the factual
2026 Phase 6A/6B layers as immutable baselines and contains no probabilities,
population trajectories, extinction events, precise sensitive locations,
vector/disease ecology, or future Great Black Swamp polygon.

## PHASE 7A — ACCEPTED / FROZEN

**Exposure & Environmental Health Baseline, 2026**

Phase 7A is formally **ACCEPTED / FROZEN**. Its 20-node/20-edge exposure-context
layer, five pathway register, monitoring matrix, evidence crosswalk, uncertainty
register, Map 23, and principal reports are protected by
`reports/phase7a_exposure_environmental_health_freeze_manifest.json`.

The layer preserves environmental presence, potential pathway, documented
exposure, dose, and health-outcome distinctions. It asserts no documented
individual exposure, dose, illness, plume, or cumulative-risk score.

## PHASE 7B — ACTIVE

**Exposure Dependencies, Evidence Strength & Controls, 2026**

Phase 7B is a separate qualitative analytical layer over frozen Phase 7A.

## Open Phase 1 QA gates

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

Great Black Swamp historical geometry: Phase 1 QA research is complete. Official ODNR dataset 3135 was preserved and audited; a Gordon (1966) class-4 candidate was produced and validated under `outputs/qa/`. Human decision: **C — HOLD**. The method is resolved, the geometry remains a noncanonical candidate, and the direct official extent source gap remains open. This item no longer blocks current Water System or Phase 2 development. See [the geometry source review](reports/great_black_swamp_geometry_source_review.md).

Physical hydrography replacement: Phase 1 QA and integration are complete. Human decision: **B — ACCEPT WITH QUALIFICATION**. Current development adopts separate USGS 3DHP physical and official-connector layers plus 12 explicitly abstract unresolved routing edges. The historical v0.1 release and Map 01–05 artifacts remain unchanged. See [the reconciliation report](reports/physical_hydrography_reconciliation.md).

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

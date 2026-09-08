# Project Status

Last reviewed: 2026-09-08

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

## PHASE 7B — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE

**Exposure Dependencies, Evidence Strength & Controls, 2026**

Phase 7B adds 20 dependency edges, seven controls, five evidence-strength rows, a 5 × 10 qualitative matrix, and Map 24. It preserves the Phase 7A evidence ladder and zero documented individual exposures. It contains no dose, illness, plume, risk score, or future content.

## PHASE 7C — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE

**Environmental Health Futures, 2050 / 2075**

Phase 7C adds 36 assumptions, 30 scenario node states, 30 edge states, 30 control states, 30 uncertainty states, six comparison rows, and Maps 25/25b. It is qualitative scenario content separate from factual 2026 layers; it contains no probabilities, exposure/dose/illness outcomes, or vector/infectious-disease work.

## Open Phase 1 QA gates

## PHASE 8A — ACCEPTED / FROZEN

**Biogeochemical & Nutrient Flux Baseline, 2026**

Phase 8A adds 18 biogeochemical nodes, 24 directed flux edges, ten separate
quantitative/context records, a source registry, Map 26, and bounded findings
for phosphorus, nitrogen, carbon/organic matter, water-carrier transport,
agriculture, wastewater, wetlands/riparian systems, and monitoring. Sol formally
accepted and froze Phase 8A under `reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json`.

## PHASE 8B — ACCEPTED / FROZEN

**Biogeochemical Dependencies, Controls & Bottlenecks, 2026**

Phase 8B adds 22 qualitative dependency edges, 10 control records, an 8-row
qualitative dependency matrix, official target framing, and Map 27. Unknown
quantities remain unknown; targets are not treated as observed reductions. Sol
formally accepted and froze Phase 8B under `reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json`.

## PHASE 8C — ACCEPTED / FROZEN

**Biogeochemical & Nutrient Flux Futures, 2050 / 2075**

Phase 8C adds 36 scenario assumptions, 48 scenario node states, 42 scenario
edge states, 48 control states, 48 uncertainty states, six comparison rows,
and Maps 28/28b. The future layer is qualitative and separate from factual
2026 records; it contains no future loads, concentrations, probabilities, or
predictive HAB model. Sol formally accepted and froze Phase 8C under
`reports/phase8c_biogeochemical_futures_freeze_manifest.json`.

The complete Phase 8 package is accepted/frozen and protected by three
subphase manifests. No accepted Phase 8 scientific content was changed while
recording this decision.

## PHASE 9 — ACCEPTED / FROZEN

**Climate & Natural Hazards System, 2026 / 2050 / 2075**

Phase 9A is accepted and frozen as a factual 2026 physical-hazard baseline:
28 nodes, 29 relationships, 28 quantitative/context observations, and 21
sources under Map 29. Phase 9B is accepted and frozen as a qualitative
dependency, compound-event, and resilience layer: 24 dependency edges, 9
compound-event pathways, 12 controls, an 11-dimension 9-row matrix, and Map
30. Phase 9C is accepted and frozen as separate qualitative futures with 12
projection evidence records, 36 assumptions, 36 hazard states, 48 dependency
states, 48 resilience states, 54 compound-event states, six comparisons, and
Maps 31/31b.

Phase 9A/9B post-integration corrections are recorded in
`reports/phase9a_correction_qa.md` and `reports/phase9_correction_qa.md`. The
final independent-review record is `reports/phase9_independent_review.md`.
The original implementation commits and transparent correction commits remain
in history; no correction was amended, squashed, rewritten, or concealed.

Freeze protection covers 48 Phase 9 artifacts under:

- `reports/phase9a_climate_natural_hazards_freeze_manifest.json` — 13 artifacts
- `reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json` — 14 artifacts
- `reports/phase9c_climate_hazard_futures_freeze_manifest.json` — 21 artifacts

Final subphase status:

- Phase 9A: **ACCEPTED / FROZEN**
- Phase 9B: **ACCEPTED / FROZEN**
- Phase 9C: **ACCEPTED / FROZEN**
- Active phase: **NONE**
- Next analytical phase: **NOT APPROVED**.


Phase 9 uses no composite hazard score, unsupported hazard probability, health
or social-vulnerability scoring, deterministic hazard surface, or comprehensive
emergency-management model. Station, watershed, county, floodplain, shoreline,
and regional scales remain distinct. Phase 10A and 10B are accepted/frozen as a separate institutional governance layer; Phase 10C is accepted/frozen as a separate qualitative 2050/2075 scenario layer under its final freeze manifest.

## PHASE 10A — ACCEPTED / FROZEN

**Governance & Jurisdiction Baseline, 2026**

Phase 10A adds a 40-actor registry, 100 authority/role records, 100 actor-system relationships, 48 source records, 16 uncertainty records, and Map 32. It keeps regulation, operation, ownership, monitoring, funding, advisory, permitting, scientific information, and private/public roles distinct.

Sol formally accepted and froze Phase 10A on 2026-09-04 under `reports/phase10a_governance_jurisdiction_freeze_manifest.json`. The manifest protects 15 Phase 10A acceptance artifacts, including the source, assumptions, findings, QA, artifact-check, and independent-review records. The accepted boundaries include regulatory authority ≠ operational control; monitoring ≠ regulation; funding ≠ binding authority; advisory role ≠ legal decision authority; ownership ≠ regulation; private operation ≠ public operation; scientific information ≠ legal authority; and voluntary program ≠ enforceable mandate.

## PHASE 10B — ACCEPTED / FROZEN

**Cross-System Authority, Dependencies & Coordination, 2026**

Phase 10B adds 25 cross-system dependency records and edges, 14 coordination mechanism records, a 10-row qualitative governance/dependency matrix, and Map 33. It distinguishes overlapping, sequential, split, information, funding, permit, public/private, interstate, binational, monitoring-without-control, and control-without-direct-observation relationships. It uses no composite governance score and makes no generalized governance-gap claim.

Sol formally accepted and froze Phase 10B on 2026-09-04 under `reports/phase10b_governance_dependencies_coordination_freeze_manifest.json`. The manifest protects 15 Phase 10B acceptance artifacts and references the frozen Phase 10A manifest. Unknown ≠ failure and overlap ≠ dysfunction remain explicit boundaries.

## PHASE 10C — ACCEPTED / FROZEN

**Governance Futures, 2050 / 2075**

Phase 10C adds a separate qualitative scenario layer with 48 assumptions, 120 actor states, 90 authority states, 150 dependency states, 84 coordination states, 96 uncertainty states, six comparison rows, 19 scenario-source records, a comparison figure, and Maps 34/34b. Scenario A is Integrated Basin Governance, Scenario B is Federated / Networked Governance, and Scenario C is Fragmented / Contested Governance. 2050 is an intermediate trajectory; 2075 is a matured or diverged state rather than a simple intensity copy.

All future records explicitly separate CURRENT FACT (2026 baseline), SCENARIO ASSUMPTION, and SCENARIO CONSEQUENCE. Phase 10A/10B authority, actor, dependency, and coordination records remain immutable. GLIFWC remains an intertribal body; distinct sovereign nations remain distinct actors. Regulation, operation, ownership, public finance, market operation, monitoring, advice, and scientific information remain separate. AI recommendation is not legal authority, automated monitoring is not automatic enforcement, algorithmic prioritization is not final public decision, and sensor coverage is not institutional capacity.

Phase 10C creates no composite governance score, political/election analysis, unsupported future jurisdiction, treaty amendment prediction, tribal territory, permit jurisdiction, enforcement authority, public/private role collapse, or Phase 11 content. The validated working manifest is `reports/governance_scenario_manifest.json`; the final freeze manifest is `reports/phase10c_governance_futures_freeze_manifest.json`; the fresh independent review is `reports/governance_scenario_independent_review.md` and records `passed: true` with no blocking findings.

Sol formally accepted and froze Phase 10C on 2026-09-07. The final freeze manifest protects 23 Phase 10C artifacts, including all accepted scenario tables, 19 scenario-source records, comparison outputs, Maps 34/34b, reports, the validated working manifest, the artifact check, and the fresh independent-review record.

The Phase 10 correction lineage remains transparent and unrevised: implementation `e7d421c7c1a43a335e1e2faef2bca009c4427712`, provenance correction `d25d4394c265fcc68ed4b5a89cf2901f70910fad`, handoff `f613d3ff1f4193444d1f01560806cbf2d6b8fc9b`, post-correction review `e1f233cc89e3694d2f08dfd81fde6f9194f57a65`, Phase 10C implementation `3e1bd27810771a9de520fbc6ee6fcdad5e7c01e0`, and newline-portability fix `4541e6dd036ccc51534827ba1c6a791fd37d0145` remain visible in Git history. No commit was amended, squashed, rewritten, or concealed.

Final subphase status:

- Phase 9A: **ACCEPTED / FROZEN**
- Phase 9B: **ACCEPTED / FROZEN**
- Phase 9C: **ACCEPTED / FROZEN**
- Phase 10A: **ACCEPTED / FROZEN**
- Phase 10B: **ACCEPTED / FROZEN**
- Phase 10C: **ACCEPTED / FROZEN**
- Active phase: **NONE**
- Next analytical phase: **NOT APPROVED**

## PHASE 11A — ACCEPTED / FROZEN

**Population & Settlement Baseline, 2026**

Phase 11A adds 62 settlement/employment nodes, 918 population and settlement observations, 44 structural/employment relationships, 34 source records, nine uncertainty records, and Map 35. It combines 2020 Decennial Census P.L. 94-171 enumeration, 2024 Vintage Population Estimates Program July 1 estimates, ACS 2024 5-year estimates for the 2020–2024 period, Census TIGER geography, and bounded LODES workplace context.

The package distinguishes person counts, household counts, housing-unit counts, density, jobs, workers, and commuter flows. County, place, and generalized employment-center scales remain separate. Age and household composition are descriptive aggregate context only. No individual profiles, protected-class ranking, vulnerability/EJ score, health outcome, dose, utility-territory assignment, or future demographic forecast is included.

Map 35 and the Phase 11A working baseline are protected by `reports/population_settlement_baseline_manifest.json` and the Phase 11A Python/R validators. Great Black Swamp remains C — HOLD / noncanonical; the Toledo intake-coordinate discrepancy remains unresolved.

## PHASE 11B — ACCEPTED / FROZEN

**Population, Mobility & System Dependencies, 2026**

Phase 11B adds 302 mobility observations, 142 generalized residence/workplace relationships, 520 qualitative dependency-register rows, 52 qualitative matrix rows, and Map 36. It uses ACS 2024 5-year journey-to-work context and LODES 8.4 aggregates: Ohio and Indiana WAC/RAC/OD products are 2023; Michigan WAC/OD products are 2021 and RAC is 2023 because those are the current public files available. Michigan workplace/residence differences are not calculated across mismatched WAC/RAC vintages.

LODES records are modeled/tabulated administrative products aggregated to county interfaces. Commuting is kept distinct from migration; workplace is kept distinct from residence; passenger movement is kept distinct from freight. The dependency matrix uses qualitative labels only and creates no composite vulnerability, service-access, governance, environmental-justice, or community-risk score. Population presence does not assign residents to exact utility service territories.

Map 36 and the complete Phase 11A/11B package are protected by their final freeze manifests, `reports/phase11_working_manifest.json`, `reports/population_mobility_artifact_check.json`, and the Phase 11A/11B Python/R validators. Phase 11C is implemented as a separate qualitative scenario layer and does not modify those protected artifacts.

## PHASE 11C — ACCEPTED / FROZEN

**Population & Settlement Futures, 2050 / 2075**

Phase 11C adds 36 scenario assumptions, six projection-evidence records, 108
county-scale future settlement states, 108 qualitative spatial relationships,
36 uncertainty states, 11 scenario-source records, six comparison rows, a
comparison figure, and Maps 37/37b. It models spatial redistribution,
settlement form, housing form, employment geography, mobility interfaces, and
service dependence as separate qualitative scenario states.

2050 is an intermediate scenario horizon. Official Ohio, Michigan, and Indiana
county projection products are available as reference evidence, but no
deterministic scenario total is adopted in the qualitative future states. 2075
is primarily an explicit scenario horizon, not a mechanical extrapolation.
Climate migration remains a high-uncertainty scenario mechanism,
not a population-growth assumption. Population, households, housing units,
workers, jobs, and commuters remain distinct; commuting remains distinct from
migration.

The future layer is separate from factual 2026 tables and uses three scenario
families: A — Connected Reconcentration; B — Polycentric Adaptive Basin; and C
— Uneven Change / Infrastructure Strain. No exact future population, household,
housing-unit, worker, job, commuter, or migration total is asserted. No
vulnerability/EJ score, protected-class ranking, individual movement model, or
utility-territory assignment is included. The working manifest is
`reports/population_settlement_future_manifest.json`; Python and independent R
validation are recorded in `reports/population_settlement_future_artifact_check.json`.
The final freeze manifest protects the validated package, reports, working
manifest, review record, and Python/R freeze validators at
`reports/phase11c_population_settlement_futures_freeze_manifest.json`.

Final Phase 11 status: Phase 11A, 11B, and 11C are **ACCEPTED / FROZEN**; active
phase is **NONE**; next analytical phase is **NOT APPROVED**. The fresh Phase
11C independent review passed with all blocking arrays empty; its implementation
and review history remain preserved in Git and
`reports/population_settlement_future_independent_review.md`.

## PHASE 12A — ACCEPTED / FROZEN

**Vector Ecology Baseline, 2026**

Phase 12A contains 20 vector/ecology nodes, 26 ecology relationships, 36
surveillance/context records, 15 habitat associations, 27 source records, 10
uncertainty records, and Map 38. It separates vector presence, abundance,
pathogen-in-vector detection, human-vector contact, infection, and clinical
disease; sampling effort is not abundance; detection is not establishment; and
county records are not precise local distributions.

The package retains different state/program methods and denominators, treats
non-detection and CDC no-records as not absence, and treats pooled mosquito
testing as surveillance context rather than an abundance index. The CDC Ixodes
workbook provenance retains the original CDC source-page URL and the actual
`restoredcdc.org` mirror/retrieval URL, explicitly not CDC-hosted, after the
direct CDC binary returned HTTP 403.

## PHASE 12B — ACCEPTED / FROZEN

**Vector / Environment / Human-System Dependencies, 2026**

Phase 12B contains 28 dependency-register rows, 28 dependency edges, eight
qualitative matrix rows, eight evidence-crosswalk rows, 27 reused sources, and
Map 39. Documented relationships remain separate from project inference;
potential contact interfaces are not exposure, dose, infection, or disease;
monitoring is not control; and positive vector pools or reported human cases do
not establish local transmission without supporting evidence.

The Phase 12A working baseline remains immutable during 12B. Phase 12C is a
separate qualitative future-scenario layer and does not modify Phase 12A/12B.
Sol formally accepted and froze
Phase 12A and Phase 12B after Python and independent R freeze validation,
strict provenance checks, verification of 298 prior manifest entries / 293
unique protected artifacts, and the fresh bounded independent review passed
with all blocking arrays empty. Final freeze protection is recorded in
`reports/phase12a_vector_ecology_freeze_manifest.json` (17 artifacts) and
`reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json`
(15 artifacts). The implementation, correction, review, merge, and delivery
history remains preserved in Git: `ec37108371d51ccdecd9fafcbde58463d79911d7`,
`dc231c3e5c371050482c9cf8f4f938b4ec55a624`, `326fbd7`, `0853f8b`, and
`e158740aa35f31d2155a9906a3bc2c5529fb5147`.

## PHASE 12C — ACCEPTED / FROZEN

**Vector Ecology Futures, 2050 / 2075**

Phase 12C adds a separate qualitative scenario layer with 36 assumptions, 36
vector states, 48 habitat states, 30 surveillance states, 168 dependency
states, 60 uncertainty states, 28 scenario-source records, six comparison rows,
and Maps 40/40b. The three alternatives are A — Managed Ecological Adaptation,
B — Heterogeneous Adaptive Basin, and C — Warmer / More Variable Vector
Landscape.

2050 is an intermediate ecological trajectory. 2075 is a matured or diverged
state with substantive horizon-specific changes in all state tables and maps.
Future suitability/opportunity is not observed distribution or guaranteed
establishment. Surveillance intensity is not abundance. The package contains no
future range polygon, abundance estimate, pathogen-prevalence forecast, human
contact/infection model, disease-incidence forecast, exposure/dose model,
vulnerability/EJ score, or individual-risk surface.

Sol formally accepted and froze the corrected package after deterministic Python
and independent R validation, strict grounded-citation/provenance checks,
Phase 12A/12B freeze-integrity verification, verification of 298 prior manifest
entries / 293 unique protected artifacts, and the fresh bounded independent
review passing with all blocking arrays empty. Final freeze protection is recorded
in `reports/phase12c_vector_ecology_futures_freeze_manifest.json` (28 artifacts).
The working manifest and artifact check remain preserved, as do the initial failed
review, correction lineage, implementation history, and final review. Python and
independent R freeze validators are `src/python/systems/validate_phase12c_freeze.py`
and `src/R/systems/validate_phase12c_freeze.R`. Phase 12A/12B remain immutable.

Great Black Swamp remains C — HOLD / noncanonical and the Toledo intake-coordinate
discrepancy remains UNRESOLVED. Phase 13 is not implemented.

Historical maintenance is deferred and unchanged: Phase 6B manifest status
wording mismatch and Phase 3A missing manifest status. Active phase is
**NONE** and the next analytical phase is **NOT APPROVED**.

1. Toledo intake coordinate reconciliation
2. authoritative historical Great Black Swamp geometry

The non-georeferenced Great Black Swamp image remains reference-only. Fictional 2050 nodes retain null coordinates. Neither condition may be “completed” with guessed geometry.

Great Black Swamp historical geometry: Phase 1 QA research is complete. Official ODNR dataset 3135 was preserved and audited; a Gordon (1966) class-4 candidate was produced and validated under `outputs/qa/`. Human decision: **C — HOLD**. The method is resolved, the geometry remains a noncanonical candidate, and the direct official extent source gap remains open. This item no longer blocks current Water System or Phase 2 development. See [the geometry source review](reports/great_black_swamp_geometry_source_review.md).

Physical hydrography replacement: Phase 1 QA and integration are complete. Human decision: **B — ACCEPT WITH QUALIFICATION**. Current development adopts separate USGS 3DHP physical and official-connector layers plus 12 explicitly abstract unresolved routing edges. The historical v0.1 release and Map 01–05 artifacts remain unchanged. See [the reconciliation report](reports/physical_hydrography_reconciliation.md).

## Canon state

The current working canon uses five overlapping interpretive macroregions: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt. Frontier Arc is superseded in v0.1.

See [docs/canon_status.md](docs/canon_status.md) for scope and interpretation rules.

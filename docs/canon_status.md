# Current Canon Status

## Current regional canon

The current working canon has five macroregions:

1. Glass City Core
2. Maumee River Commons
3. Lake Erie Energy & Security Coast
4. Black Swamp Country
5. Great Lakes Industrial Belt

These are interpretive regional identities, not jurisdictions or mutually exclusive polygons. They may overlap. Physical geography, ecological systems, infrastructure systems, political authority, and fictional regional identity remain separate analytical layers.

## Superseded concepts

- **Frontier Arc** is superseded in the current v0.1 five-region model. Older images or documents may retain it as exploratory history.
- **Black Swamp Preserve** is superseded as the primary Region 4 name. The current name is **Black Swamp Country**; preserve/ecological uses may still appear at smaller scales.
- Geographically inaccurate AI-generated map experiments are non-authoritative and remain archived only as exploratory visual history.
- **Cyberglass** is earlier or possible in-world terminology. **Glasspunk** is the current working genre/aesthetic term. The final setting title remains open.

Imported source documents are preserved without silent rewriting. This file governs where older exploratory terminology conflicts with current canon.

## Planned cross-regional concept

The **Woodville–Elmore–Luckey Materials Corridor** may develop as a geology/materials/industry corridor. It is interpretive and cross-regional, not a jurisdiction, polygonal macroregion, or sixth macroregion.

## Current systems architecture

1. Water / Hydrology / Nutrients
2. Geology / Minerals / Strategic Materials
3. Energy / Grid / Compute
4. Freight / Industry / Material Flows
5. Ecology / Biodiversity
6. Exposure / Environmental Health
7. Data / Sensors / Governance / Security
8. Governance / Jurisdiction as an optional cross-cutting view
9. Climate / Natural Hazards as a physical-environmental layer

## Indigenous history and sovereignty

Indigenous geography must be time-enabled and sourced, not represented as a timeless generic tribal-territory polygon. Living sovereign descendant nations must not be replaced with fictional generic tribes. Archaeological coordinates may require generalization to protect cultural resources. Lower Maumee / Ottawa history is a priority future historical GIS layer, but that reconstruction has not begun.

See the separate [Indigenous Peoples' History research module](research/Glasspunk_Indigenous_Peoples_History.md).

## Strategic-materials planning constraints

The imported [geology and strategic-materials addendum](worldbuilding/Glasspunk_Geology_Strategic_Materials_Addendum_and_Codex_Prompts.md) is the planning specification for Phase 2:

- limestone and dolomite are local geologic resources;
- Elmore is a strategic-material processing/manufacturing node, not a local beryllium mine;
- Luckey is a historical, legacy, and remediation node; and
- the Materials Corridor is interpretive and cross-regional.

Phase 2A and Phase 2B implement the real-world 2026 geology/facility and material-flow baseline. Phase 2C adds source-grounded history and qualified Materials-to-Exposure interfaces. Luckey historical production, Luckey current remediation, and Elmore current advanced processing are separate. The Materials Corridor remains an unevaluated interpretive concept; no polygon, sixth macroregion, freight route, or future-scenario object has been created.

## Data and scenario separation

The project follows: **REAL GEOGRAPHY FIRST; FICTIONAL INTERPRETATION SECOND.**

Important feature fields include:

- `reality_status`: `real`, `historical`, `fictional`
- `canon_status`: `verified`, `inferred`, `scenario`, `experimental`

Speculative 2050 objects must remain distinguishable from verified 2026 infrastructure. In Phase 1, fictional 2050 nodes have null coordinates.

## Great Black Swamp spatial status

**Canonical:** no authoritative Great Black Swamp polygon is currently adopted.

**Research / QA:** `great_black_swamp_candidate_gordon1966` is a 4,672.66 km² MultiPolygon derived reproducibly from the generalized 1:500,000 ODNR/Gordon 1966 vegetation source. Human decision: **C — HOLD**. Method status is resolved; geometry status is candidate; canonical status is hold.

The supplied non-georeferenced image remains reference-only, non-authoritative, and prohibited as a geometry source.

## Current-development hydrography status

Human decision: **B — ACCEPT WITH QUALIFICATION**.

The preferred post-v0.1 routing architecture uses three separate representations:

- `hydrography_physical` — 3DHP Channel Line, Canal, and Drainageway features accepted as mapped physical hydrography;
- `hydrography_network_connectors` — authoritative Surface, Waterbody, Elevation Breaching, and Hydro Unenforced connectors that are not ordinary streams; and
- `routing_inferred_unresolved` — project-derived abstract routing relationships with `physical_geometry=false`.

The historical `water_flowlines_order3` and `water_huc12_routing_inferred` layers remain for v0.1 compatibility and are superseded for new routing analysis. This post-v0.1 improvement does not alter the release tag or released Map 01–05 artifacts.

## Phase status

- **Phase 1 Water System v0.1:** complete and validated; qualified 3DHP post-release improvement integrated into current development
- **Phase 2A Geology / Minerals / Strategic Materials:** complete and validated 2026 baseline
- **Phase 2B Material Flows:** complete and validated 2026 baseline; Maps 07–08 only
- **Phase 2C Strategic Materials, Exposure & Remediation History:** complete and validated; Map 09 only, with zero documented individual exposure findings
- **Phase 2D Alternative Materials Futures:** complete and validated as six explicitly fictional scenario states across 2050/2075; Maps 10/10b
- **Phase 4A Data, Sensors & Decision Infrastructure Baseline:** accepted and frozen as a factual 2026 observation-to-decision layer; Map 14
- **Phase 4B Information Dependencies, Blind Spots & Governance:** accepted and frozen as a factual 2026 analytical layer; Map 15
- **Phase 4C Data, Sensors, Governance & Security Futures:** accepted and frozen as separate qualitative 2050/2075 scenario deltas; Maps 16/16b
- **Phase 5A Freight / Industry / Material Flows Baseline:** accepted and frozen as a factual 2026 logistics/material-flow layer; Map 17
- **Phase 5B Freight Evidence & Interchange Validation:** accepted and frozen as a factual 2026 evidence-strengthening layer; Map 18
- **Phase 5C Freight Dependencies & Critical Interfaces:** accepted and frozen as a factual 2026 qualitative dependency layer; Map 19
- **Phase 6A Ecology & Biodiversity Baseline:** accepted and frozen as a factual 2026 ecological-system layer; Map 20
- **Phase 6B Ecological Dependencies, Disturbances & Resilience:** accepted and frozen as a factual 2026 qualitative dependency layer; Map 21
- **Phase 6C Ecological Futures:** accepted and frozen as separate qualitative 2050/2075 scenario content; Maps 22/22b
- **Phase 7A Exposure & Environmental Health Baseline:** accepted and frozen as a bounded factual 2026 exposure-context layer; Map 23
- **Phase 7B Exposure Dependencies, Evidence Strength & Controls:** implemented, validated, and integrated; awaiting Sol acceptance; Map 24
- **Phase 7C Environmental Health Futures:** implemented, validated, and integrated as separate qualitative 2050/2075 scenario content; awaiting Sol acceptance; Maps 25/25b
- **Phase 8A Biogeochemical & Nutrient Flux Baseline:** accepted and frozen as a separate factual 2026 layer; Map 26; `reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json`
- **Phase 8B Biogeochemical Dependencies & Controls:** accepted and frozen as a separate qualitative 2026 layer; Map 27; `reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json`
- **Phase 8C Biogeochemical & Nutrient Flux Futures:** accepted and frozen as separate qualitative 2050/2075 scenario content; Maps 28/28b; `reports/phase8c_biogeochemical_futures_freeze_manifest.json`
- **Phase 9 Climate & Natural Hazards System:** accepted and frozen as a separate physical 2026 / qualitative 2050–2075 layer; Maps 29, 30, 31, and 31b; freeze protection is recorded in `reports/phase9a_climate_natural_hazards_freeze_manifest.json`, `reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json`, and `reports/phase9c_climate_hazard_futures_freeze_manifest.json`. Post-integration correction history is recorded in `reports/phase9a_correction_qa.md` and `reports/phase9_correction_qa.md`.

- **Phase 10A Governance & Jurisdiction Baseline:** accepted and frozen as a factual 2026 institutional layer; Map 32; `reports/phase10a_governance_jurisdiction_freeze_manifest.json`
- **Phase 10B Cross-System Authority, Dependencies & Coordination:** accepted and frozen as a qualitative 2026 dependency layer; Map 33; `reports/phase10b_governance_dependencies_coordination_freeze_manifest.json`
- **Phase 10C Governance Futures:** accepted and frozen as separate qualitative 2050/2075 scenario content; Maps 34/34b; `reports/phase10c_governance_futures_freeze_manifest.json`
- **Phase 11A Population & Settlement Baseline:** accepted and frozen as a factual 2026 layer; Map 35; `reports/phase11a_population_settlement_freeze_manifest.json`
- **Phase 11B Population, Mobility & System Dependencies:** accepted and frozen as a qualitative 2026 dependency layer; Map 36; `reports/phase11b_population_mobility_dependencies_freeze_manifest.json`
- **Phase 11C Population & Settlement Futures:** accepted and frozen as separate qualitative 2050/2075 scenario content; Maps 37/37b; `reports/phase11c_population_settlement_futures_freeze_manifest.json`.
- **Phase 12A Vector Ecology Baseline:** accepted and frozen as a factual 2026 vector ecology/surveillance layer; Map 38; `reports/phase12a_vector_ecology_freeze_manifest.json`.
- **Phase 12B Vector / Environment / Human-System Dependencies:** accepted and frozen as a separate qualitative 2026 dependency layer; Map 39; `reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json`.
- **Phase 12C Vector Ecology Futures:** implemented, validated, and integrated as a separate qualitative 2050/2075 scenario layer; awaiting Sol acceptance; Maps 40/40b.

Final subphase status: Phase 9A is **ACCEPTED / FROZEN**; Phase 9B is **ACCEPTED / FROZEN**; Phase 9C is **ACCEPTED / FROZEN**; Phase 10A is **ACCEPTED / FROZEN**; Phase 10B is **ACCEPTED / FROZEN**; Phase 10C is **ACCEPTED / FROZEN**; Phase 11A is **ACCEPTED / FROZEN**; Phase 11B is **ACCEPTED / FROZEN**; Phase 11C is **ACCEPTED / FROZEN**; Phase 12A is **ACCEPTED / FROZEN**; Phase 12B is **ACCEPTED / FROZEN**; and Phase 12C is **IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE**. Active phase: **NONE**. Next analytical phase: **NOT APPROVED**.

Phase 2D does not change factual canon. Its continuity/resilience, circular
basin, and high-convergence families are exploratory alternatives without
probabilities. The Materials Corridor emerges weakly only as a scenario network;
no polygon, sixth region, or transport route is canonical.

Phase 4A adds no macroregion, jurisdiction, fictional geography, future
scenario, or change to the five-region canon. Its public observation stations,
data products, forecasts, decision organizations, and operational responses
are distinct analytical interfaces; non-geolocated objects remain schematic.
The GLOS Toledo crib coordinate does not resolve the existing physical Toledo
intake-coordinate discrepancy.

Phase 4B changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its dependency, blind-spot, authority, and matrix records are
analytical governance interfaces over Phase 4A; they do not create physical
communication routes, cyber architecture, AI authority, or future scenarios.

Phase 4C does not change the five-region canon. Its 2050/2075 information,
governance, trust, security, and automation objects are explicitly fictional
scenario deltas and remain separate from factual 2026 records.

Phase 5A changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its freight corridors and generalized material relationships do not
create a Materials Corridor polygon, named route, sixth macroregion, or
facility-specific shipment claim.

Phase 5B changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its evidence crosswalk and interchange findings strengthen selected
relationships without creating a Materials Corridor geography. Phase 5C will
remain a separate qualitative dependency layer.

Phase 5C changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its dependency edges, register, modal-substitutability matrix, and
Map 19 describe qualitative transportation interfaces over the frozen Phase 5A
and Phase 5B records. They do not establish shipment routes, volumes,
probabilities, vulnerability, or future freight scenarios. Phase 5C is
accepted and frozen under `reports/phase5c_freight_dependency_freeze_manifest.json`.

Phase 6A changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its ecological nodes, edges, indicators, and Map 20 are a factual
2026 system skeleton over existing water, wetland, and hydrography layers. The
Great Black Swamp candidate remains held and noncanonical; sensitive species
locations, invented biodiversity values, exact movement routes, ecological-risk
scores, and future ecological scenarios are excluded. Phase 6A is accepted and
frozen under `reports/phase6a_ecology_freeze_manifest.json`.

Phase 6B changes no regional canon, macroregion, jurisdiction, or fictional
geography. Its dependency edges, disturbance register, resilience matrix, and
Map 21 are qualitative analytical interfaces over the Phase 6A baseline. They
do not create ecological-risk scores, population trajectories, exact movement
routes, sensitive species locations, or future scenarios. Phase 6B is accepted
and frozen under `reports/phase6b_ecological_dependency_freeze_manifest.json`.

Phase 6C changes no factual ecological baseline or regional canon. Its 2050 and
2075 objects are separate qualitative scenario deltas with explicit
assumptions, provenance, and no probabilities. The held Great Black Swamp
candidate remains noncanonical, and no population, extinction, disease, or
sensitive-location scenario is represented.

## Phase 9 acceptance boundary

Phase 9A, 9B, and 9C are accepted and frozen. Phase 9A remains the factual 2026
hazard baseline; Phase 9B remains a separate qualitative dependency,
compound-event, and resilience layer; and Phase 9C remains separate qualitative
2050/2075 scenario content. No Phase 9 layer creates a composite hazard score,
unsupported probability, deterministic hazard surface, health or
social-vulnerability score, or comprehensive emergency-management model.

The transparent correction lineage is preserved: original Phase 9A and 9B
implementation commits `8a76895c62be6af8304d93f50895828812b13e26` and
`ae6e946b17bedb9670ef1d6c5f3a958b33062e82`, preservation checkpoint `affde66`,
correction commits `f0546d6`, `c529c30`, `4db3515`, and `d1e9369`, and corrected
Phase 9C commit `5b104b9` remain visible in Git history. The final independent
review record is `reports/phase9_independent_review.md`.

Great Black Swamp remains **C — HOLD / noncanonical**. The Toledo
intake-coordinate discrepancy remains **UNRESOLVED**. Neither hold was resolved
or treated as a prerequisite for Phase 9 acceptance.

## Phase 10 acceptance boundary

Phase 10A and 10B are accepted/frozen institutional layers, not new physical jurisdictions. Regulatory authority, operational control, monitoring, funding, advisory role, legal decision authority, ownership, private/public operation, and scientific information remain distinct. Voluntary programs are not enforceable mandates. GLIFWC remains `intertribal_body`; distinct sovereign nations remain distinct actors. No unsupported present-day Western Basin tribal territory, permit/enforcement jurisdiction, or historical-association-to-current-authority inference is canonical.

The transparent Phase 10 correction lineage is preserved: original implementation `e7d421c7c1a43a335e1e2faef2bca009c4427712`, provenance correction `d25d4394c265fcc68ed4b5a89cf2901f70910fad`, handoff `f613d3ff1f4193444d1f01560806cbf2d6b8fc9b`, and post-correction review commit `e1f233cc89e3694d2f08dfd81fde6f9194f57a65` remain visible and unrevised. The review records are `reports/governance_independent_review.md`, `reports/governance_post_correction_independent_review.md` (`deleg_2e8d515e`), and `reports/governance_additional_post_correction_independent_review.md` (`deleg_eedc4116`).

Great Black Swamp remains **C — HOLD / noncanonical**. The Toledo intake-coordinate discrepancy remains **UNRESOLVED**. Neither hold was resolved or treated as a prerequisite for Phase 10 acceptance. Phase 10C is **ACCEPTED / FROZEN** under `reports/phase10c_governance_futures_freeze_manifest.json` as a separate qualitative scenario layer; it does not alter the factual 2026 institutional baseline.

## Phase 11 acceptance boundary

Phase 11A is a factual 2026 population/settlement layer using 2020 Census enumeration, 2024 PEP estimates, ACS 2024 5-year estimates, Census geography, and bounded LODES employment context. Phase 11B is a qualitative 2026 mobility/dependency layer using ACS journey-to-work and LODES aggregates plus accepted Phase 6–10 interfaces. Sol formally accepted and froze both layers under `reports/phase11a_population_settlement_freeze_manifest.json` and `reports/phase11b_population_mobility_dependencies_freeze_manifest.json`. They do not create a canonical population boundary, utility service territories, individual movement model, vulnerability/EJ score, protected-class ranking, health outcome, unsupported demographic forecast, Indigenous-history/HGIS layer, or future population scenario. Phase 11C is accepted and frozen under `reports/phase11c_population_settlement_futures_freeze_manifest.json` as a separate qualitative 2050/2075 scenario layer.

The accepted package contains 62 nodes, 918 population/settlement observations, 44 relationships, 34 sources, and nine uncertainty records in Phase 11A; plus 302 mobility observations, 142 mobility relationships, 520 dependency-register rows, and 52 qualitative matrix rows in Phase 11B. Ohio and Indiana LODES WAC/RAC/OD are 2023; Michigan WAC/OD are 2021 and RAC is 2023. Michigan cross-vintage WAC/RAC differences are not calculated, OD provenance is state-matched, service dependencies are generalized, and transport dependencies are inferred where appropriate. COMMUTING ≠ MIGRATION, WORKPLACE ≠ RESIDENCE, DEPENDENCY ≠ VULNERABILITY, MODELED POPULATION ≠ CENSUS ENUMERATION, and MUNICIPAL BOUNDARY ≠ UTILITY SERVICE TERRITORY remain explicit boundaries. Phase 11C is a separate qualitative future layer and does not alter these accepted baselines.

Phase 11C contains 36 scenario assumptions, six projection-evidence records, 108 future settlement states, 108 qualitative spatial relationships, 36 uncertainty states, 11 scenario sources, six comparison rows, a comparison figure, and Maps 37/37b. Official Ohio, Michigan, and Indiana county projection products are recorded as 2050 reference evidence without deterministic scenario totals; 2075 is explicit scenario content. Climate migration is a high-uncertainty mechanism, not a population-growth assumption. The layer contains no unsupported exact future totals, fake Census precision, individual movement model, vulnerability/EJ score, protected-class ranking, or utility-territory assignment. The fresh independent review passed with all blocking arrays empty. Active phase: **NONE**; next analytical phase: **NOT APPROVED**.

## Phase 12 boundary

Phase 12A is a factual 2026 vector ecology and surveillance layer containing 20
nodes, 26 ecology relationships, 36 surveillance/context records, 15 habitat
associations, 27 sources, 10 uncertainties, and Map 38. Phase 12B is a separate
qualitative dependency layer containing 28 dependency rows/edges, eight matrix
rows, eight evidence-crosswalk rows, and Map 39. The layers preserve vector
presence != abundance != pathogen detection in vector != human-vector contact !=
human infection != clinical disease; sampling effort != abundance; detection !=
establishment; county record != precise local distribution; positive vector pool
!= human case; and reported case != local transmission unless supported.

Different state/program methods and denominators remain distinct. Non-detection
and CDC no-records are not absence, county detections are not precise local
distributions, and pooled mosquito testing is not an abundance index. The CDC
Ixodes source registry retains the original CDC source-page provenance and the
actual `restoredcdc.org` mirror/retrieval provenance, explicitly not CDC-hosted;
the direct CDC binary URL returned HTTP 403.

No individual infection probability, disease-risk score, vulnerability/EJ score,
deterministic incidence forecast, unsupported abundance surface, unsupported
exact vector range, personal exposure estimate, Phase 12C, or Phase 13 content is
Phase 12A and Phase 12B are **ACCEPTED / FROZEN** under their final
freeze manifests. Phase 12C is implemented as a separate qualitative future
layer and awaits Sol acceptance; it does not modify the accepted Phase 12A/12B
artifacts. The implementation, corrected VDE-003 lineage, independent review,
and validation history remains preserved. The Great Black Swamp remains
**C — HOLD / noncanonical** and the Toledo intake-coordinate discrepancy remains
**UNRESOLVED**. Deferred maintenance is limited to the Phase 6B manifest status
wording mismatch and the Phase 3A missing manifest status; neither was altered
in this freeze run.

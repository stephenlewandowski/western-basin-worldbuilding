# Post-Phase-13 Systems and Atlas Review

Review date: 2026-09-10
Repository basis: `main` at `5ed519a8ecb5721e5a74db43b56fe34627c376be`
Review type: read-only project-level scientific and architectural review

## Scope and method

This review uses the repository as authoritative. It reads the current status and canon surfaces, the durable handoff, README and report navigation, workflow guidance, Phase 10–13 briefs, freeze manifests, current map inventory, and targeted findings/QA reports. It does not rebuild the analytical packages or exhaustively reread every CSV and report.

No accepted or frozen scientific artifact was changed. Phase 14 was not implemented. No release or tag was created. The active holds remain unchanged:

- Great Black Swamp geometry: **C — HOLD / noncanonical**.
- Toledo intake-coordinate discrepancy: **UNRESOLVED**.

## 1. Executive assessment

The project is structurally complete enough to begin qualitative convergence and Atlas synthesis. It is not a quantitatively closed basin model, a predictive epidemiological model, a power-flow model, a freight-flow model, or a composite risk model. That distinction is important: the repository now has the breadth and modular interfaces needed for a system-of-systems narrative, but it does not yet have common units, synchronized time series, capacities, rates, behavioral response functions, or validated joint scenarios that would justify numerical stress testing or aggregate scores.

The principal remaining problem is integration, not another missing environmental domain. The thirteen completed systems now cover the basin's major physical, ecological, infrastructural, informational, institutional, population, exposure, vector, and infectious-disease structures. The repository does not yet expose one operational system-of-systems registry: `metadata/systems.yml` defines the original water and materials entries, while the shared GeoPackage contains 16 water/hydrography/materials tables and later Phase 3–13 tables remain in separate CSV/report packages. The next effort should therefore shift from domain acquisition to:

1. aligning status and freeze boundaries;
2. defining a common cross-system interface and scenario vocabulary;
3. filling only the narrow agriculture/land-use/soils and built-infrastructure utilization interfaces needed for convergence; and
4. testing a small number of explicit qualitative chains without converting them into risk scores or forecasts.

Recommendation: run a dedicated maintenance and status-alignment pass now, then proceed to a modified Phase 15 as one integrated Technology, Biological-Systems-Security, and Strategic-Systems Convergence package. Do not create a standalone Phase 14 trilogy. Phase 16 should follow as a qualitative integrated-basin stress-test package. Atlas prototyping should begin in parallel, but final Atlas synthesis should wait until the cross-system scenario and interface contract exists.

## 2. Current system architecture

The repository's current architecture is a layered system model rather than one unified numerical graph:

| System | Integrated contribution | Repository status relevant to review |
|---|---|---|
| Water | HUC/watershed, flowline, wetland, Maumee–Bay–Lake Erie, HAB/intake/treatment and consumer dependency structure; qualified current-development hydrography | Complete/validated; current hydrography is accepted with qualification; historical v0.1 release remains separate |
| Geology / minerals / strategic materials | Carbonate occurrence, extraction/processing roles, Elmore strategic processing, Luckey legacy/remediation, material-flow and future alternatives | Phase 2A–2D complete/validated; future objects remain separate from the factual graph |
| Energy / grid / compute | Generation, storage, grid interfaces, major loads, water/materials dependencies, planned/unverified compute, and qualitative futures | Phase 3A/3B accepted/frozen; Phase 3C accepted/validated and separate from the factual baseline |
| Data / sensors / governance | Representative observation-to-decision chains, blind spots, information dependencies, authority distinctions, and security/automation futures | Phase 4A–4C accepted/frozen |
| Freight / industry / material flows | Port, marine/rail/highway, industrial/material nodes, agricultural/bulk functions, interchange evidence, modal and gateway dependencies | Phase 5A–5C accepted/frozen |
| Ecology / biodiversity | Lake–bay–tributary, wetlands, floodplain, agricultural matrix, terrestrial habitat, mobile-species and disturbance/resilience interfaces, and futures | Phase 6A–6C recorded as accepted/frozen in project status; the Phase 6B manifest wording still requires maintenance alignment |
| Exposure / environmental health | Bounded drinking-water/HAB, air, legacy contamination, food/fish/recreation, heat pathways, controls and qualitative futures | Phase 7A accepted/frozen; Phase 7B/7C are implemented, validated, integrated, but still awaiting Sol acceptance in current status surfaces |
| Biogeochemical / nutrient flux | Phosphorus, nitrogen, carbon/organic matter, runoff, wastewater, wetlands/riparian retention, controls, bottlenecks and futures | Phase 8A–8C accepted/frozen |
| Climate / natural hazards | Heat, precipitation/flooding, drought/low water, lake/coastal, convective and winter hazards, compound events, resilience and futures | Phase 9A–9C accepted/frozen |
| Governance / jurisdiction | Actors, authority/role boundaries, public/private and federal/state/local seams, coordination, and institutional futures | Phase 10A–10C accepted/frozen |
| Population / settlement | Population, households, housing, jobs, workers, commuting, residence/workplace, mobility/dependency and qualitative settlement futures | Phase 11A–11C accepted/frozen |
| Vector ecology | Culex/Aedes/Ixodes context, surveillance, habitat associations, environmental/human-system dependencies and futures | Phase 12A–12C accepted/frozen |
| Infectious disease | Vector-borne, waterborne/environmental, foodborne/enteric, respiratory, zoonotic, healthcare/AMR baseline, dependencies, surveillance/response interfaces and futures | Phase 13A–13C accepted/frozen |

The architecture is strongest as a set of linked baseline, dependency, and future layers. It is weaker as a single machine-readable system-of-systems model because cross-phase relationships are mostly represented by named interfaces, reused IDs, manifests, and report references rather than by one shared integration registry.

## 3. Major strengths

1. **Broad structural coverage.** The model now spans natural processes, environmental condition, engineered infrastructure, material and freight systems, information, institutions, population, exposure, vectors, and infectious disease. No obvious major basin-scale domain is missing for a qualitative Western Basin Atlas.

2. **Strong evidence discipline.** The project repeatedly distinguishes fact, inference, scenario, uncertainty, native spatial scale, and source basis. Phase 9, Phase 11, Phase 12, and Phase 13 reports are especially explicit about dated observations, mixed vintages, surveillance limitations, and the difference between plausible mechanism and demonstrated local consequence.

3. **Protected-baseline architecture.** Freeze manifests, working manifests, artifact checks, source registries, correction lineage, and independent Python/R validation provide a credible immutability boundary. The current map directory contains 54 PNG/SVG pairs with no missing counterpart, covering Maps 01–43 and horizon variants.

4. **Health and ecological restraint.** The project does not turn contamination into exposure, exposure into dose, dose into illness, vector suitability into disease, surveillance into incidence, mobility into transmission, or response capacity into disease absence. This is an important foundation for safe synthesis.

5. **Useful qualitative interfaces already exist.** Examples include climate–hydrology–nutrient–ecology pathways, energy–water and energy–materials dependencies, port/industry/material interfaces, observation-to-decision chains, population/mobility dependencies, vector/environment interfaces, and governance seams. These are sufficient starting points for integration without inventing another domain catalog.

## 4. Important remaining gaps

### Essential before integrated synthesis or stress testing

These are integration requirements, not recommendations for new full domain phases.

- **A common integration contract.** Every cross-system edge used in synthesis needs a consistent identifier, direction, relationship class, documented-versus-inferred status, source or accepted-input basis, native scale, time period/horizon, uncertainty, and confidence. The current phases contain most of these fields locally, but not one shared cross-system registry. Endpoint conventions are not yet uniform: Phase 13B uses `EXT-*` and `REF-*` conceptual endpoints in 25 of its 36 rows, while the population dependency register expands 52 objects across ten systems into 520 rows, 468 inferred and 52 reused-context rows. These are useful analytical records, but they should not be mistaken for a fully joinable graph.

- **A scenario crosswalk.** The letter A does not mean the same thing across phases. For example, energy, ecology, governance, vector, population, and disease packages have different A/B/C mechanisms. A future Atlas must align scenarios by mechanism and consequence, not by letter. The project needs an explicit crosswalk for 2050 and 2075 before treating multiple domain scenarios as one basin future.

- **A bounded agriculture/land-use/soils interface.** Agriculture is already present in the freight, nutrient, climate, ecology, and infectious-disease packages, but primarily as a generalized function. The most important missing shared structure is the connection among land cover/use, agricultural production and management, soil/water retention, tile-drainage or runoff pathways, food-system interfaces, and seasonal timing. This does not justify a new agriculture trilogy. A qualitative interface register and a limited set of defensible land-use/soil context fields are enough for the first synthesis.

- **A bounded built-infrastructure utilization interface.** Population and housing are represented, and water, energy, freight, information, and exposure interfaces exist, but service populations, building-stock condition, actual utilization, distribution capacity, continuity, and facility-level handoffs are intentionally unresolved. Phase 16 can represent these as qualitative capacity/continuity states; it should not infer exact utility territories, feeder performance, facility loads, or individual exposure.

- **A clear status boundary for Phase 7B/7C.** The current project status includes their integrated contribution, but both remain awaiting Sol acceptance and have no final freeze manifests in the current manifest inventory. Before an Atlas calls the whole exposure/environmental-health package canonical, the project must either accept/freeze them or explicitly label them as noncanonical working layers. This is a governance/documentation blocker, not a reason to alter their scientific content.

### Valuable but optional; do not open as standalone phases now

- Detailed agriculture production, farm economics, commodity accounts, and food-demand modeling. Existing freight, nutrient, population, and foodborne interfaces are sufficient for qualitative convergence.
- A full soils and contemporary land-cover time series. A bounded soil/land-use interface is needed; a national-scale soil or parcel model is not.
- Transportation beyond freight, including detailed passenger road, transit, and travel-demand modeling. Phase 11 already supplies aggregate mobility; more detail is optional unless the fiction specifically depends on transit operations.
- Economics, labor markets, finance, and regional accounts. Employment and jobs are represented in Phase 11, and finance appears as a governance scenario interface. A full economic model is not required for the environmental systems Atlas.
- Detailed housing and built-environment stock, waste, wastewater, circular materials, and communications networks. These are useful future refinements but can be represented as bounded interfaces in convergence.
- Institutional capacity or performance measurement. Qualitative response capacity, decision latency, implementation conditions, and continuity can be used in stress tests, but governance quality, effectiveness, vulnerability, or failure scoring should not be introduced.

### Better as an Atlas or historical layer

- Indigenous historical geography, including Lower Maumee/Ottawa history and time-specific relationships among living sovereign nations, institutions, and places.
- Great Black Swamp transformation and drainage history. The held candidate geometry must not be promoted to a canonical polygon.
- Settlement history, industrial history, infrastructure history, shoreline/port transformation, and land-use change timelines.

These layers should be time-enabled, sourced, and explicitly separated from present-day jurisdiction, present-day ecological geometry, and fictional regional identity.

### Out of scope unless the project purpose changes

- Individual disease, exposure, dose, illness, mortality, or personal-risk modeling.
- Composite disease, environmental, hazard, vulnerability, or governance scores.
- Unsupported local downscaling to neighborhoods, households, facilities, or individuals.
- Full power-flow, feeder, contingency, outage-probability, or dispatch modeling.
- Facility-specific freight routes, hazardous-material routes, shipment quantities, or confidential logistics topology.
- Sensitive SCADA, control-network, cyber-target, privacy, or nonpublic infrastructure reconstruction.
- Deterministic 2050/2075 case, outbreak, disease-burden, or ecological-abundance forecasts.

## 5. Cross-system connectivity assessment

### Climate → hydrology → nutrients → ecology → vectors → infectious disease → population/institutions

This is the best-supported chain in the current project.

- **Climate to hydrology:** Phase 9 records heat, precipitation, drought, lake-level, storm, and winter interfaces; Phase 9B connects precipitation to runoff/flooding and drought to water and ecological conditions.
- **Hydrology to nutrients:** Phase 8 identifies agricultural landscape, runoff/drainage, tributaries, the Lower Maumee, Maumee Bay, and western Lake Erie as the strongest directional structure. Tile drainage, seasonal load series, source apportionment, and retention performance remain uncertain.
- **Nutrients to ecology:** Phase 6 and Phase 8 connect nutrient/HAB conditions to aquatic, wetland, floodplain, and food-web interfaces without asserting a quantified ecological consequence.
- **Ecology/climate/hydrology to vectors:** Phase 12 represents temperature, precipitation/standing water, wetland/ditch/floodplain, forest/edge, host, and surveillance interfaces. Presence, suitability, abundance, establishment, and human contact remain separate.
- **Vectors/environment to disease:** Phase 13 reuses Phase 12 and adds vector-borne and waterborne/environmental disease interfaces while stopping short of local transmission or incidence.
- **Disease to population/institutions:** Phase 13 uses aggregate settlement, mobility, healthcare, surveillance, governance, and response interfaces; Phase 11 and Phase 10 supply the relevant human-system structure.

The chain is therefore structurally present, but not temporally coupled. It lacks a shared event window, synchronized observations, quantitative loads or rates, vector abundance/contact data, disease incidence model, and measured institutional response function. It supports a qualitative pathway narrative and a bounded stress test, not a chain-wide risk estimate.

### Materials → industry → freight → energy → compute → water → governance

This chain is present but less complete.

- Phase 2 distinguishes local carbonate extraction, strategic processing at Elmore, nonlocal feed, and Luckey remediation.
- Phase 5 establishes the Port of Toledo, rail/highway/marine interfaces, industrial nodes, agricultural/bulk functions, and external-market orientation.
- Phase 3 links materials and selected industrial loads to electricity, cooling, fuel, and the one planned/unverified compute project.
- Phase 4 and Phase 10 supply observation, information, authority, regulatory, public/private, and coordination seams.

The weak interfaces are facility-to-freight routes, material quantities and substitution, compute commissioning/interconnection and water demand, facility-level energy/water capacity, and operational governance handoffs. The project correctly leaves these unresolved. Integration should expose the uncertainty instead of filling it with a route, flow volume, or bottleneck score.

### Population/settlement → infrastructure utilization → exposure → surveillance → governance response

The conceptual chain is also present.

- Phase 11 provides population, housing-unit, workplace, job, commuting, residence/workplace, and aggregate mobility context.
- Phase 11B links settlement and employment concentration qualitatively to water, wastewater, energy, transport, housing, climate, environmental-health, nutrient/material, ecology, and governance interfaces.
- Phase 7 provides exposure pathways and controls without individual exposure, dose, illness, or cumulative-risk claims.
- Phase 4 and Phase 13 provide information, surveillance, healthcare, and reporting interfaces.
- Phase 10 provides authority, coordination, funding, public/private, and response-role distinctions.

The missing middle is infrastructure utilization and service continuity. The chain should be modeled as settlement context → generalized service dependence/capacity state → potential exposure pathway → observation/reporting interface → role-bounded response, with explicit uncertainty at every transition. It should not become a vulnerability ranking or individual-health model.

### Repeated dependencies and missing interfaces

The same broad dependencies recur across reports: water, energy, communications, monitoring, governance, mobility, food/freight, and infrastructure. This is substantively correct, but repeated local representations can diverge in wording, scale, or evidence basis. There is no need for another domain phase; there is a need for a single integration crosswalk and a review of duplicated relationship claims. A related taxonomy seam exists in the energy dependency table, where four electricity edges target `ENE-LOAD-*` nodes while using `to_system=water_or_materials`; that convention may be analytically understandable, but it should not become an unexamined join key in a future common registry.

## 6. Areas of redundancy and overbuilding

The phases are not scientifically redundant in their intended boundaries, but the project is beginning to overbuild the delivery architecture.

- The repeated baseline/dependency/futures pattern has been useful for Phases 3–13 because it protects factual baselines and forces scenario separation. It is no longer the best default for every remaining topic.
- Phase 2 materials and Phase 5 freight both touch industrial/material movement, but Phase 2 is about resource and processing structure while Phase 5 is about logistics and gateways. Keep both source packages; combine them in the Atlas narrative.
- Phase 4 information governance and Phase 10 institutional governance overlap at observation, authority, coordination, and public/private seams. They should remain distinct in the evidence model but be presented together in an integrated governance/decision chapter.
- Phase 6 ecology, Phase 12 vector ecology, and Phase 13 infectious disease are deliberately nested. Their repeated environmental and surveillance interfaces are a reason to build a chain crosswalk, not a reason to create a new biosecurity domain trilogy.
- Phase 7 exposure and Phase 13 disease must remain separate because their health-boundary distinctions are different. Their shared pathways should be linked through explicit interfaces rather than repeated prose.
- Phase 8 nutrient flux and Phase 9 climate hazards already contain the beginnings of compound-event integration. More independent ecology or climate subphases would be low-value at this point.

The main overbuilding is technical and documentary: 48 Python validators, 46 R validators, 29 freeze-manifest files, 170 report Markdown files, 114 report JSON files, and a long cumulative handoff with many historical checkpoints. The lineage is valuable, especially for failed-review corrections, but future work should use fewer integrated packages, a common validator layer, and clearer archival/navigation tiers.

## 7. Model and evidence risks

The existing packages are generally disciplined. The main risks arise when their outputs are combined.

1. **Ordinal-label commensurability.** `high`, `moderate`, `mixed`, `unknown`, and similar terms are not automatically comparable across energy, ecology, freight, governance, exposure, and disease matrices. Synthesis must retain the originating system, dimension, scale, evidence basis, and uncertainty.

2. **Dependency becoming causal language.** A directional edge or functional dependency is not a causal estimate. Integrated prose should use terms such as interface, pathway, opportunity, condition, or dependency unless direct evidence supports a stronger claim.

3. **Scenario becoming forecast.** Domain scenario states are qualitative alternatives. Combining them must not produce an implied most-likely trajectory, probability, expected value, or deterministic 2075 outcome.

4. **Observation becoming model output.** Station observations, county administrative products, surveillance records, projection evidence, scenario states, and inferred relationships must remain visually and textually different. A comparison figure must not look like a common measurement scale when its rows are unlike.

5. **Spatial-scale collapse.** The project mixes HUC/watershed, station, county, place, sewershed, facility, shoreline, program, and generalized regional scales. Overlaying them on one map can imply false co-location or local precision.

6. **Surveillance and health overinterpretation.** More monitoring, testing, wastewater sampling, laboratory participation, or reporting can increase observed records without demonstrating more underlying disease. This boundary is explicit in Phase 12 and Phase 13 and must be retained in the Atlas visual language.

7. **Duplicate evidence inflation.** The same government source or accepted phase artifact can support several related interfaces. Repeating the citation does not create independent evidence. An integrated source appendix should retain source identity and role rather than count references as separate confirmations.

8. **Status ambiguity.** A layer that is implemented and validated but awaiting acceptance must not be presented beside accepted/frozen layers without a status label. The Phase 7B/7C boundary is the most consequential current example.

Recommended synthesis controls are a claim-level provenance crosswalk, status/scale/horizon badges, separate visual grammar for fact/inference/scenario, and a hard prohibition on summed matrices or composite scores.

## 8. Atlas-readiness assessment

### What already exists

The repository has a substantial source-plate library: 54 PNG/SVG analytical map pairs, including current baselines, dependency views, and 2050/2075 alternatives through Maps 43/43b. It also has scenario comparison tables/figures, water and dependency diagrams, system-specific source and assumptions reports, QA records, uncertainty registers, machine-readable manifests, correction lineage, five current interpretive macroregions, and narrative findings for all major systems.

The current material is therefore ready for curation, not yet ready as a finished Atlas. The existing numbered maps should be treated as analytical source plates. The Atlas should not simply concatenate all 43 map numbers and all phase reports.

### What the Atlas still needs

1. **Front matter and visual grammar:** scope, canonical status rules, fact/inference/scenario symbols, scale conventions, uncertainty notation, and a glossary.
2. **Overview spread:** a Western Basin orientation map plus a system-of-systems diagram showing the five interpretive macroregions without turning them into jurisdictional polygons.
3. **Regional profile pages:** one page or spread for each of Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country, and Great Lakes Industrial Belt, with explicit overlap and interpretive status.
4. **System chapter pages:** concise narratives and selected source plates for water, materials, energy, data, freight, ecology, exposure, nutrients, climate, governance, population, vectors, and infectious disease.
5. **Integrated chain diagrams:** the three chains assessed above, with relationship status and uncertainty shown. Qualitative flow diagrams are appropriate; widths must not imply unmeasured quantities.
6. **Cross-system matrix:** a matrix of system interfaces, using typed relationships and native scales rather than a single score.
7. **Scenario comparison spreads:** a mechanism-based crosswalk across 2050 and 2075. Do not align different domain A/B/C labels without an explicit mapping.
8. **Historical transformation pages:** Indigenous historical geography, Great Black Swamp transformation, settlement, industrial, and infrastructure timelines, all time-enabled and source-qualified.
9. **Uncertainty and hold pages:** Great Black Swamp C-HOLD, the Toledo intake discrepancy, unresolved routing/material/facility questions, coverage limitations, and status boundaries should be visible design elements.
10. **Source/method appendix:** source registry conventions, map methods, manifests, validation boundaries, scale rules, scenario rules, and an index to canonical versus working artifacts.

A true quantitative Sankey is not currently justified because the project does not have comparable, measured flow quantities across the proposed chains. Use topology or non-proportional flow diagrams unless a future approved package supplies compatible units and explicit width semantics.

Atlas prototyping should begin in parallel with the next convergence work. A noncanonical information architecture, sample profile page, visual grammar, and selected integrated diagrams can be developed without changing any scientific baseline. Final Atlas synthesis should follow the Phase 16 integration gate.

## 9. Historical and cultural layer recommendation

Keep the historical/cultural stream parallel to the numbered scientific systems and make it an Atlas layer rather than Phase 14 or another domain trilogy.

- Indigenous historical geography should be a time-enabled, sourced layer that distinguishes historical relationships, living sovereign nations, intertribal bodies, consultation, current authority, and fictional interpretation. Sensitive archaeological locations should be generalized or omitted.
- Great Black Swamp transformation should be narrated through drainage, land-use, settlement, ecology, and infrastructure change. The Gordon/ODNR candidate remains a held research geometry and must not become a canonical boundary.
- Settlement, industrial, infrastructure, shoreline, and port history should be organized as timelines and transformation diagrams that connect historical changes to current systems without recasting history as a present jurisdiction or deterministic cause.

This stream can begin in parallel with Atlas prototyping and convergence, provided that the two active holds remain explicit.

## 10. Technical-debt assessment

### Status and freeze consistency

The freeze architecture is substantial but not uniform. The current inventory contains 29 freeze manifests with 435 artifact entries covering 426 unique paths; all listed paths were present in the read-only inventory, and nine repeated entries are shared lineage artifacts. The inconsistency is in metadata and authority surfaces:

- `reports/phase3a_freeze_manifest.json` has no explicit status field.
- `reports/phase6b_ecological_dependency_freeze_manifest.json` says `IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE`, while `PROJECT_STATUS.md` and `docs/canon_status.md` describe Phase 6B as accepted/frozen.
- Phase 7B and Phase 7C have no final freeze manifests and remain awaiting Sol acceptance in the current status surfaces.
- Phase 1, Phase 2, and Phase 3C use complete/validated or accepted/validated language rather than the later final-freeze pattern. That may be historically intentional, but it needs a clear canonicality rule before Atlas assembly.

These are maintenance issues, not reasons to rewrite the scientific artifacts. The project should standardize mutable status surfaces and manifest metadata while preserving protected briefs, accepted artifacts, and correction history.

### Navigation and duplicate status surfaces

`reports/README.md` is not current: it still describes Phase 4C as active, Phase 5B as active, Phase 6C as awaiting acceptance, and Phase 13B/13C as not yet implemented. The top-level `README.md` also retains an obsolete roadmap that says Phase 4B awaits acceptance and Phase 4C should not begin. `CHANGELOG.md` contains historical Unreleased wording that still says Phase 13B awaits acceptance even though the later entries record its acceptance.

These documents should not be treated as scientific contradictions, but they are operationally misleading. A maintenance pass should update navigation and current-status summaries, label preserved historical checkpoint text, and avoid editing protected phase briefs merely to change their original approved-scope wording. The long `reports/current_phase_handoff.md` also functions more as an append-only historical log than a compact current handoff; its final section is authoritative only when read after the earlier checkpoints.

### Validators and manifests

The 48 Python and 46 R validators provide strong independent checks, but bespoke per-phase logic has produced schema and metadata variation, including the known Phase 3A and Phase 6B manifest issues. Retain the phase validators for protected-package integrity, but add a small common metadata/status smoke check and a repository-wide manifest/index consistency check. Do not delete validators as a cosmetic simplification.

### Worktrees and repository hygiene

There are 32 registered worktrees, all clean in this review. Many point to completed phase branches and historical implementation commits. The clean state is good; the count is accumulated maintenance debt and makes it harder to distinguish active work from archival lineage. A dedicated maintenance pass should inventory which branches/worktrees remain useful, preserve history, and remove only explicitly stale worktrees after verifying their branches and protected artifacts.

### Overall maintenance recommendation

A dedicated maintenance pass is worthwhile now, before the next scientific phase. It should be narrow and non-scientific:

- align mutable status surfaces and report/map navigation;
- add missing manifest status metadata and correct the Phase 6B wording mismatch;
- explicitly decide and record the Phase 7B/7C acceptance boundary;
- add repository-wide manifest/index/status checks;
- preserve failed reviews, working manifests, accepted/frozen hashes, holds, and historical records;
- inventory and reduce stale worktrees without rewriting branches;
- rerun the existing validation, link, application, Git/LFS, and whitespace gates.

No maintenance change should alter an accepted/frozen scientific artifact.

## 11. Recommended remaining roadmap

| Proposed phase | Decision | Recommendation |
|---|---|---|
| Phase 14 — Biosecurity & Biological Systems Security | **MODIFY; repurpose rather than implement as proposed** | Make Phase 14 the Systems Atlas Integration / Ontology and Evidence Crosswalk phase. It should inventory frozen inputs, define common IDs and typed edge/status/scale/horizon fields, register `EXT-*`/`REF-*` placeholders, document joins and non-joins, and create one auditable system-of-systems crosswalk. Biosecurity should not be a standalone domain trilogy; its bounded laboratory/reporting, biosafety/containment, animal-health, food-system security, continuity, and governance content belongs inside Phase 15/16. Avoid sensitive operational details and threat/vulnerability scoring. |
| Phase 15 — Technology Convergence & Strategic Systems | **MODIFY and KEEP as one integrated phase** | Cover AI/advanced compute, cybersecurity/privacy at a high level, advanced energy/storage, automation, biotechnology/genetic engineering, and advanced materials as capability families that modify existing systems. Quantum can remain a bounded strategic possibility rather than a separate model. Use one interface/capability matrix and one coherent scenario package; do not create a baseline/dependency/futures trilogy for each technology. |
| Phase 16 — Integrated Basin Dynamics & Cross-System Stress Tests | **MODIFY and KEEP** | The project is mature enough for qualitative cross-system stress tests, not predictive coupled simulation. Use the three chains in Section 5, explicit stressors, interface states, controls, observations, response roles, and uncertainty. Do not sum ordinal matrices, produce composite risk, infer failure probabilities, or treat scenarios as forecasts. |
| Phase 17 — Atlas Synthesis | **KEEP, substantially redefine** | Produce a curated Atlas rather than a dump of phase outputs: overview, five regional profiles, system chapters, integration diagrams, mechanism-based scenario comparisons, historical/cultural layer, holds and uncertainties, glossary, source/method appendix, and canonical/working-artifact index. |

### 12. Clear recommendation for the next phase

The immediate next action should be the narrow maintenance pass described in Section 10. The next numbered phase should then be a **modified Phase 14 — Systems Atlas Integration, Ontology, and Evidence Crosswalk**. This is the missing connective layer needed before technology convergence, integrated stress tests, or a defensible final Atlas. It is not a new scientific domain and should not modify frozen packages.

This recommendation does not authorize implementation in this review. After the integration phase, the next approved brief should be a single cross-cutting Phase 15 technology and strategic-systems convergence package, not a collection of technology-specific domain phases. Phase 16 should then test the integrated system qualitatively. Atlas prototyping can proceed in parallel with all three, using clearly marked noncanonical presentation work.

If the project temporarily prioritizes environmental-system science over speculative technology, the Phase 15 package can be kept small and Phase 16 can become the next substantive scientific package. That is a sequencing option, not a reason to open Phase 14.

## 13. Topics that should not receive standalone phases

Unless the project purpose materially changes, the following should not become new full baseline/dependency/futures phase trilogies:

- biosecurity or biological systems security;
- agriculture and food production;
- soils and land use;
- passenger transportation or detailed transit;
- economics, labor, finance, or regional accounts;
- detailed housing and built-environment stock;
- waste and circular material systems;
- physical communications networks;
- institutional-capacity or governance-performance scoring;
- AI, advanced compute, cybersecurity/privacy, advanced energy, quantum, biotechnology/genetic engineering, automation, or advanced materials as separate domains;
- historical/cultural geography, Great Black Swamp history, settlement history, industrial history, or infrastructure history;
- individual health, disease, exposure, dose, illness, vulnerability, or outbreak modeling;
- full SCADA/cybersecurity, power-flow, freight-route, or confidential infrastructure modeling.

The first ten are either already represented as interfaces, optional refinements, or better suited to Phase 15/16. The historical topics belong in the Atlas stream. The last group is outside the current evidence and safety boundaries.

## 14. Suggested endpoint for the scientific-modeling stage

The scientific-modeling stage should end when all of the following are true:

1. **Coverage is sufficient for the project purpose.** The existing thirteen systems plus bounded agriculture/land-use/soils and infrastructure-utilization interfaces explain the major basin pathways without requiring another standalone domain.
2. **The integration contract is complete.** Cross-system nodes and edges carry stable IDs, relationship semantics, source/input basis, fact/inference/scenario status, time/horizon, native scale, uncertainty, confidence, and explicit non-claims.
3. **Scenarios are coherently crosswalked.** 2050 and 2075 alternatives are aligned by mechanism and system consequence rather than by reused A/B/C letters. The crosswalk does not create a forecast or probability.
4. **Qualitative stress tests are reproducible.** At least the three core chains can be traced from pressure or condition through interfaces, controls, observations, role-bounded response, and uncertainty without a composite score.
5. **The acceptance boundary is unambiguous.** Accepted/frozen artifacts, working but unaccepted layers, historical records, scenario objects, and the two active holds are clearly separated in status surfaces and Atlas metadata. Phase 7B/7C status must be explicitly resolved or carried as noncanonical.
6. **Provenance and scale remain visible.** Every Atlas claim can be traced to a source record, accepted artifact, or named inference; no map implies finer spatial precision than its input.
7. **The Atlas package is curatable.** The overview, five regional profiles, selected system narratives, cross-system diagrams, scenario comparison, historical/cultural pages, uncertainty/hold views, glossary, and methods/source appendix can be assembled without inventing new facts or reinterpreting frozen artifacts.
8. **Future work changes data or fiction, not the model's basic domain architecture.** After this endpoint, new work should be targeted updates, evidence refreshes, scenario writing, Atlas editions, or explicitly approved extensions—not automatic expansion into another trilogy.

At that point, the Western Basin model should be described as a mature, evidence-disciplined qualitative system-of-systems foundation for an Atlas and speculative worldbuilding. It should not be described as a predictive basin simulator or a unified quantitative risk model.

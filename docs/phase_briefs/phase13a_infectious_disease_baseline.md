# Phase 13A — Infectious Disease System Baseline, 2026

Status: approved execution brief; factual 2026 baseline only.
Primary product: Map 41 — Infectious Disease System Baseline, 2026.

## Purpose

Build a compact, source-grounded systems baseline for infectious disease in the Western Basin. Represent selected pathogen/disease systems, transmission pathways, environmental interfaces, host/population context, surveillance systems, reporting bases, and institutional response interfaces without producing a disease-risk ranking or outbreak forecast.

## Required distinctions

The data model, reports, map, and validators must preserve:

- pathogen presence != exposure != infection != reported case != local transmission != outbreak != disease burden;
- surveillance intensity != incidence;
- reported case != place of exposure;
- absence of reported cases != pathogen absence;
- county-level case data != neighborhood-level risk;
- vector detection != pathogen-positive vector != human infection;
- source-water contamination != treatment failure != exposure != infection != reported case;
- case count != transmission rate; testing intensity != disease intensity; hospitalization != community incidence.

## System selection

Use a representative, non-exhaustive set of systems with material regional relevance. Candidate included systems should be limited to those that clarify Western Basin structure and have authoritative public surveillance or institutional evidence:

- Vector-borne: West Nile virus and Lyme disease / Ixodes scapularis interface, reusing Phase 12 rather than rebuilding vector ecology.
- Waterborne/environmental: Legionnaires' disease as a water-system/healthcare-environment surveillance example; enteric illness and drinking/recreational-water pathways only where the reporting system and evidence chain are explicit. Harmful algal bloom records remain toxic/environmental context, not infectious disease, unless an infectious pathway is directly supported.
- Foodborne: a selected enteric surveillance set such as Salmonella, Campylobacter, and Shiga toxin-producing E. coli, represented as distinct surveillance systems rather than a combined burden.
- Respiratory: influenza surveillance and SARS-CoV-2 surveillance/wastewater as system examples; no large pandemic reconstruction.
- Zoonotic/animal-human: rabies surveillance as a regional animal-human interface, with animal testing/exposure-control distinction explicit.
- Healthcare/institutional: generalized healthcare-associated infection / antimicrobial-resistance surveillance interface only where supported; no facility ranking or performance score.

Do not force every candidate category into the package. Do not infer importance from simple geographic coincidence.

## Data model

Use repository conventions under `data/processed/networks/`, `data/processed/analysis/`, `reports/`, `src/python/systems/`, `src/R/systems/`, and `outputs/maps/systems/`. Expected products, adapted only if existing conventions require it:

- `data/processed/networks/infectious_disease_nodes.csv`
- `data/processed/networks/infectious_disease_transmission_relationships.csv`
- `data/processed/analysis/infectious_disease_observations.csv`
- `data/processed/analysis/infectious_disease_surveillance.csv`
- `data/processed/analysis/infectious_disease_sources.csv`
- `data/processed/analysis/infectious_disease_uncertainties.csv`
- `outputs/maps/systems/41_infectious_disease_system_baseline_2026.png`
- `outputs/maps/systems/41_infectious_disease_system_baseline_2026.svg`
- `src/python/systems/build_infectious_disease_baseline.py`
- `src/python/systems/validate_infectious_disease_baseline.py`
- `src/R/systems/validate_infectious_disease_baseline.R`
- `reports/infectious_disease_sources.md`
- `reports/infectious_disease_assumptions.md`
- `reports/infectious_disease_findings.md`
- `reports/infectious_disease_qa.md`
- `reports/infectious_disease_baseline_manifest.json`
- `reports/infectious_disease_artifact_check.json`
- `reports/infectious_disease_independent_review.md`
- `reports/phase13a_citation_ledger.json`

Every source-backed record must carry a source ID and explicit evidence/status fields. Surveillance records should retain, where meaningful: pathogen/disease, reporting year or period, geography, surveillance system, case or surveillance definition, reporting basis, numerator, denominator, residence/exposure/diagnosis basis, suppression/missingness, source, confidence, and uncertainty.

## Reuse and protected inputs

Reuse accepted/frozen layers without modifying them:

- Phase 7A exposure/environmental-health pathways and monitoring boundaries;
- Phase 9A/9B/9C climate and hazard context at native station/county/watershed/shoreline scales;
- Phase 11A/11B/11C population, settlement, workplace, and mobility context at native county/place/generalized scales;
- Phase 12A/12B/12C vector ecology, vector surveillance, and vector/environment interfaces;
- Phase 4A/4B observation and information systems;
- Phase 10A/10B/10C governance and institutional-role distinctions.

Phase 12A/B/C must be confirmed `ACCEPTED / FROZEN` before implementation. The prior freeze boundary must remain unchanged.

## Spatial scale

Prefer the coarsest defensible surveillance geography. County-level records remain county-level. Do not downscale cases to neighborhoods, census tracts, municipalities, or facilities. Do not map individual cases or infer exposure location from residence. Maps should show surveillance geographies, generalized system interfaces, and institutional observation systems—not continuous disease-risk surfaces or hotspots.

## Negative scope

No composite infectious-disease risk index, vulnerability ranking, county danger ranking, neighborhood risk ranking, individual risk, outbreak forecast, transmission-rate estimate unless directly supported, causal attribution from coincidence, disease-burden estimate across unlike diseases, unsupported local downscaling, sensitive patient data, individual cases, or Phase 13B/13C implementation.

Preserve Great Black Swamp `C — HOLD / noncanonical`, the unresolved Toledo intake-coordinate discrepancy, and deferred maintenance wording for the Phase 6B manifest and Phase 3A manifest. Do not alter those records.

## Validation and delivery gates

Create a Phase 13A Python validator and an independent R validator. They must check schema, referential integrity, source coverage, case-definition/reporting-basis fields, numerator/denominator semantics, residence-versus-exposure distinctions, surveillance-effort-versus-incidence distinctions, vector/water/environmental boundaries, spatial scale, negative scope, Map 41 raster/SVG integrity, phase-local manifest hashes, active holds, and Phase 1–12 freeze integrity. Run strict grounded-citation/provenance validation report-by-report. After deterministic QA passes, obtain one fresh bounded independent review with the required structured verdict; do not integrate unless `passed: true`.

Phase 13A final status after authorized delivery: `IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE`. Active phase: `NONE`. Phase 13B and Phase 13C are approved scope only and not implemented. No release or tag.

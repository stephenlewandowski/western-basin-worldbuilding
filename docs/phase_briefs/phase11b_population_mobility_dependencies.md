# Phase 11B — Population, Mobility & System Dependencies, 2026

Status: APPROVED SCOPE / IMPLEMENTATION IN PROGRESS; formal Sol acceptance remains pending.

## Purpose

Connect the Phase 11A settlement substrate to generalized employment, commuting, housing, infrastructure-service, and accepted Western Basin system interfaces. This is a qualitative dependency layer, not an individual travel model, utility-territory model, vulnerability analysis, or health model.

## Primary product

Map 36 — Population, Mobility & System Dependencies, 2026, emphasizing residence/workplace relationships, generalized commuting, employment concentrations, and bounded interfaces with water, wastewater, energy, transport, climate hazards, environmental health, ecology/land, nutrient/material flows, housing, and governance.

## Products

- `data/processed/analysis/population_mobility_observations.csv`
- `data/processed/analysis/population_system_dependency_register.csv`
- `data/processed/analysis/population_system_dependency_matrix.csv`
- `data/processed/networks/population_mobility_relationships.csv`
- Map 36 PNG/SVG
- reproducible Python builder and validator
- independent R validator
- source, assumptions/findings, and QA reports
- machine-readable working manifest and artifact check

## Source and time discipline

Use 2023 LODES 8.4 WAC/RAC/OD data for generalized workplace, residence, and county-to-county flows; ACS 2024 5-year journey-to-work tables for residence-based commuting mode/time context; and official public transportation/infrastructure or accepted Phase 1–10 source records for system interfaces. LODES is administrative/modelled tabulation and is not a population enumeration or individual trajectory. ACS commuting is survey-estimated and is not migration.

Preserve 2023 LODES, 2024 ACS, and 2024 PEP/2020 Census vintages independently. `worker_count`, `job_count`, `commuter_flow`, and `population_count` remain distinct.

## Relationship rules

Workplace location is not residence. Commuting is not residential relocation. Daily mobility is not passenger surveillance. Passenger movement is not freight flow. OD records are aggregated to generalized county interfaces; no individual worker, employer, exact route, or travel path is exposed. Cross-county/interstate, Toledo-centered, and industrial/service employment interfaces may be represented only at supported aggregate scale.

## Dependency boundaries

Cross-link settlement with accepted water/wastewater, energy, freight/transport, climate/hazard, environmental-health, ecology/land, biogeochemical, housing, and governance layers without rebuilding those systems. Distinguish municipal boundary, service territory, utility operator, population served, and estimated service population. Do not assign every Census resident to a specific utility or infer exact service territories without authoritative evidence.

The qualitative matrix uses `strong`, `moderate`, `limited`, `unknown`, and `not_applicable`. It does not calculate a composite vulnerability, risk, service-access, or governance score. `UNKNOWN` is not `LOW`; dependence is not vulnerability; hazard interface is not exposure, dose, or illness.

## Exclusions

No social-vulnerability/EJ composite, community-risk ranking, protected-class ranking, poverty hazard ranking, individual movement, surveillance-style modeling, personal exposure/dose/health outcome, disease/mortality/hospitalization, unsupported utility assignment, causal migration claim, future demographic forecast, Indigenous-history/HGIS, Phase 11C, Phase 12, vector ecology, infectious disease, biosecurity, AI/convergence expansion, release, or tag.

## Required questions

The findings report must state where residence and workplace concentrations diverge; what generalized commuting relationships are supported; how Toledo-centered and cross-county interfaces appear; and which water/wastewater, energy, transport, climate, environmental-health, housing, ecological, nutrient/material, and governance dependencies are factual, inferred, limited, or unknown.

## Transition and completion gate

11B begins only after a clean 11A checkpoint and working-baseline hashes. Before integration, run Python/R validators, strict source/provenance checks, Map 35/36 QA, prior freeze integrity, Markdown/Git/LFS checks, complete diff review, and a fresh independent review of the actual package. Phase 11B remains awaiting Sol acceptance after integration.

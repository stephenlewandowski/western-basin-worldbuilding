# Phase 9B — Climate/Hazard Dependencies, Compound Events & Resilience, 2026

Status: approved sequential subphase; implementation is not Sol-accepted until the completed Phase 9 module is returned.

Primary product: Map 30 — Climate / Hazard Dependencies & Resilience, 2026.

## Purpose

Build a separate qualitative dependency and resilience layer over the Phase 9A factual hazard baseline. Reuse, rather than rebuild, accepted Water, Materials, Energy, Information/Sensors, Freight, Ecology, Exposure/Environmental Health, and Biogeochemical/Nutrient Flux systems.

## Data products

Use repository conventions and keep the new layer separate from Phase 9A facts:

- qualitative climate/hazard dependency edges and/or register
- `climate_compound_event_register.csv`
- resilience/control register
- qualitative dependency/resilience matrix
- Map 30 PNG/SVG
- source, assumptions/findings, QA, and artifact-manifest reports

Use dependency types such as hydrologic, thermal, infrastructure, ecological, agricultural, transport, monitoring, energy, water-quality, coastal, and seasonal. Qualitative strengths are `strong`, `moderate`, `limited`, and `unknown`; `unknown` is never interpreted as low.

## Compound-event scope

Evaluate only evidence-backed or clearly physically plausible pathways, including heat + power outage; heat + drought; extreme precipitation + nutrient mobilization; extreme precipitation + wastewater/stormwater burden; high lake level + wind setup; flooding + freight/access disruption; freeze-thaw + infrastructure stress; severe storm + power/communication disruption; and drought + agricultural/ecological stress. Each record must identify whether it is historically documented, a plausible physical/system pathway, or a scenario interaction. Do not assign probabilities without direct authoritative support.

## Resilience/control scope

Represent documented public controls and buffers such as floodplain/stormwater management, warning and cooling systems, wetlands/floodplain storage, public monitoring, water-treatment resilience, shoreline/coastal management, agricultural conservation, infrastructure winterization, and generalized grid/communication redundancy only at supported public abstraction. Do not claim effectiveness beyond evidence and do not create a comprehensive emergency-management module.

## Matrix dimensions

Use qualitative labels only for hazard exposure context, system dependency, monitoring strength, warning capacity, physical redundancy, ecological buffering, infrastructure control, seasonality, compound-event potential, spatial certainty, and temporal certainty. No numeric weighting or cumulative vulnerability score.

## Required validation and transition

Run independent Python and R validators, Map 30 artifact/text/readability QA, Phase 9A baseline hash validation, Phase 8/prior regressions, Markdown links, application tests/build, Git/LFS, and complete diff review. After integration readback, Phase 9B is an immutable working baseline and Phase 9C may proceed automatically; this is not formal Sol acceptance.

Preserve Great Black Swamp C — HOLD / noncanonical and the unresolved Toledo intake-coordinate discrepancy. Reuse environmental-health records only as receptor/control context; no mortality, hospitalization, disease, exposure, dose, health-risk, EJ, or demographic scoring.

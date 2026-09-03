# Phase 9A — Climate & Natural Hazards Baseline, 2026

Status: ACCEPTED / FROZEN; the corrected Phase 9A package is protected by `reports/phase9a_climate_natural_hazards_freeze_manifest.json`.

Primary product: Map 29 — Western Basin Climate & Natural Hazards, 2026.

## Purpose

Build a compact factual physical/environmental hazard layer for western Lake Erie, the Maumee watershed, Toledo/Northwest Ohio, and immediately relevant regional interfaces. Represent approximately six families: extreme heat; heavy precipitation/flooding; drought/low water; Lake/coastal hazards; severe convective weather; and winter hazards.

This is not an exhaustive meteorological atlas, health-outcome model, social-vulnerability analysis, emergency-management plan, deterministic risk surface, or composite hazard score.

## Data model

Use repository conventions under `data/processed/networks/`, `data/processed/analysis/`, `reports/`, and `outputs/maps/systems/`. Expected products, adapted only if existing conventions require it:

- `climate_hazard_nodes.csv`
- `climate_hazard_edges.csv`
- `climate_hazard_observations.csv`
- `climate_hazard_sources.csv`
- Map 29 PNG/SVG
- source, assumptions/findings, QA, and artifact-manifest reports

Nodes may represent climate observations, hazard regions/interfaces, monitoring and warning systems, and generalized physical contexts. Edges distinguish observed_by, monitored_by, forecast_by, affects, hydrologically_amplified_by, coastal_interface_with, warning_for, and historically_occurs_in.

Quantitative records must retain metric, value, units, period, station_or_scope, observed_or_modeled, source_id, confidence, and notes. Do not force incompatible hazard metrics into one index.

## Evidence and scale rules

Prefer NOAA/NCEI/NWS, USGS, FEMA, U.S. Drought Monitor/NIDIS, NOAA Great Lakes products, USACE, SPC, NCEI Storm Events, and authoritative state/local products. Record product/version, station/network or model, spatial and temporal resolution, reference period, and limitations where applicable.

Explicitly distinguish station, watershed/HUC, county, urban area, shoreline, floodplain, western Lake Erie, and regional climate division. Preserve the distinction between historical floodplain, modeled regulatory flood zone, observed flood, forecast flood, and future scenario. A county event count is not a hazard surface, and a station observation is not basin-wide.

Use `seiche` and `wind setup` carefully for Great Lakes processes; do not describe them as ocean storm surge. Do not infer groundwater depletion, heat mortality, individual exposure, disease, dose, social-vulnerability ranking, or neighborhood risk.

## Required validation

- Python validator for schema, provenance, allowed vocabularies, coordinates/scales, negative scope, maps, and manifest hashes.
- Independent R validator exercising the same artifacts through an independent code path.
- Map 29 PNG/SVG artifact and text/readability checks.
- Freeze/immutability checks for Phase 8A–8C and all prior accepted manifests.
- Prior-system regression checks, Markdown-link validation, application tests/build, Git/LFS checks, and complete diff review.

## Known protected constraints

Great Black Swamp remains C — HOLD / noncanonical. Toledo intake-coordinate reconciliation remains unresolved. No accepted baseline may be silently changed. Phase 9A remains a factual 2026 hazard baseline and contains no future scenario rows.

## Transition gate

Phase 9A is formally **ACCEPTED / FROZEN** after corrected-package review, Python/R validation, Map 29 QA, prior immutability checks, integration readback, and Sol acceptance. Its factual 2026 artifacts are immutable under the Phase 9A freeze manifest.

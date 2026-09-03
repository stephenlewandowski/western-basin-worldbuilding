# Phase 7A — Exposure & Environmental Health Baseline, 2026

Status: approved execution brief; factual baseline only.
Primary product: Map 23 — Western Basin Environmental Exposure Context, 2026.

## Core question

Where do environmental hazards or stressors, environmental media, potential exposure pathways, receptor contexts, monitoring systems, and institutional controls intersect across the Western Basin?

The bounded chain is:

HAZARD / STRESSOR → ENVIRONMENTAL MEDIUM → POTENTIAL EXPOSURE PATHWAY → RECEPTOR CONTEXT → MONITORING / CONTROL / ADVISORY

## Scientific boundaries

This phase models exposure context, not disease outcomes. Never silently convert contamination to exposure, exposure to dose, dose to illness, association to causation, potential pathway to documented individual exposure, environmental concentration to personal dose, or advisory to documented harm. Use `documented_exposure` only when authoritative evidence demonstrates actual exposure; otherwise use environmental presence, potential pathway, historical potential pathway, controlled pathway, advisory context, or unknown.

No personal health data, exact residences, patient locations, diagnoses, individual medical histories, vulnerability indices, environmental-justice scoring, cumulative-risk scores, neighborhood health-risk rankings, disease clusters, dose estimates, illness models, or causal health claims.

Five and only five principal pathway families:

1. Drinking Water / HAB — reuse accepted water and information baselines; distinguish source water from finished water and monitoring from human exposure; preserve the Toledo intake-coordinate discrepancy as unresolved.
2. Ambient Air — modest EPA AQS/AirData and Ohio/Michigan monitoring context for PM2.5, ozone, NO2, SO2, CO, and lead only where supported; no plume, facility attribution, dose, illness, or proximity causation.
3. Soil / Groundwater / Legacy Contamination — reuse Phase 2C Luckey; documented contamination and remediation remain distinct from individual exposure and receptor-reaching plume; no regional site inventory.
4. Food / Fish / Recreational Water — authoritative Ohio advisory and recreational-water monitoring context; do not assume individual consumption or recreation.
5. Heat / Climate-Sensitive Environmental Stress — broad 2026 heat/humidity observation and warning context; no dose, illness, mortality, future scenario, or detailed urban-heat simulation.

Generic receptors only: `residential_population`, `water_system_users`, `workers`, `outdoor_workers`, `recreational_users`, `fish_consumers`, `general_public`.

Vector/infectious disease, cumulative exposure scoring, epidemiology, environmental justice, biosecurity, future health scenarios, and Phase 7B are explicitly excluded. Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED.

## Required products

- `data/processed/networks/exposure_context_nodes.csv`
- `data/processed/networks/exposure_pathway_edges.csv`
- `data/processed/analysis/exposure_pathway_register.csv`
- `data/processed/analysis/environmental_health_monitoring_matrix.csv`
- `data/processed/analysis/exposure_evidence_crosswalk.csv`
- `data/processed/analysis/exposure_uncertainty_register.csv`
- `outputs/maps/systems/23_environmental_exposure_context_2026.png`
- `outputs/maps/systems/23_environmental_exposure_context_2026.svg`
- source, assumptions, findings, and QA reports under `reports/`

## Acceptance and delivery

Validate schemas, provenance, semantic boundaries, Map 23 PNG/SVG, Phase 6C freeze protection, all prior regressions, independent Python and R checks, Markdown links, application tests/build, and Git/LFS. Keep Maps 01–22b unchanged. On validation, commit `phase7: establish exposure and environmental health baseline`, push the feature branch, fast-forward integrate into `main`, push `main`, and record `Phase 7A — IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE`. Do not mark scientific acceptance, create a release/tag, or begin Phase 7B.

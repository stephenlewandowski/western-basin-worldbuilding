# Phase 11A — Population & Settlement Baseline, 2026

Status: ACCEPTED / FROZEN.

## Purpose

Establish a compact, source-grounded human population and settlement substrate for the Western Basin systems model. The baseline describes where people live and concentrate, major settlement centers, county/place density, households and housing units, descriptive age structure, occupancy/vacancy, recent population change, and selected employment context without creating an encyclopedic demographic atlas.

## Primary product

Map 35 — Western Basin Population & Settlement System, 2026, with a county-scale density/concentration view and generalized municipality/settlement hierarchy.

## Approved spatial frame

Use an explicit analytical Western Basin core-county frame covering the Maumee/western Lake Erie settlement interface across selected Ohio, Michigan, and Indiana counties. The frame is a study boundary for this module, not a new canonical macroregion, jurisdiction, watershed polygon, or tribal-territory polygon. County, place, and point/center scales remain distinct.

## Products

- `data/processed/analysis/population_settlement_nodes.csv`
- `data/processed/analysis/population_settlement_observations.csv`
- `data/processed/networks/population_settlement_relationships.csv`
- `data/processed/analysis/population_settlement_sources.csv`
- `data/processed/analysis/population_settlement_uncertainty.csv`
- Map 35 PNG/SVG
- reproducible Python builder and validator
- independent R validator
- source, assumptions/findings, and QA reports
- machine-readable working manifest and artifact check

## Source and time discipline

Prefer 2020 Decennial Census P.L. 94-171 geography/population/housing-unit records, Census Population Estimates Program vintage 2024 county/place estimates, ACS 2024 5-year estimates for households, housing occupancy/vacancy, age, household size, and housing age, and Census TIGER/Line/TIGERweb geography. Every record preserves `reference_year`, `release_year`, `estimate_period`, `source_product`, and `observed_estimated_modeled`.

There is no single complete 2026 Census. 2020 decennial values are enumerated counts; ACS and PEP values are estimates with their actual periods; no older measurement is relabeled as a 2026 observation.

## Core quantity and scale rules

Person count, household count, housing-unit count, density, worker count, job count, and commuter flow are separate metrics. Census blocks, block groups, tracts, places, counties, study-frame totals, and modeled grids are not interchangeable. No modeled population surface is required; if a modeled source is added later it must remain explicitly modeled and distinct from Census enumeration.

## Allowed descriptive analysis

Age and household composition are descriptive aggregate context only. Housing age, occupancy/vacancy, density, recent population change, urban/suburban/rural form, and settlement concentration may be described where source-supported. Protected-class attributes are not used for ranking, behavioral inference, politics, composite risk, or environmental-justice scoring.

## Exclusions

Do not create individual profiles, household-level inference, vulnerability scores, social-vulnerability or EJ composites, community-quality rankings, protected-class settlement rankings, disease/exposure/dose/health outcomes, unsupported migration causation, 2050/2075 forecast rows, Indigenous-history/HGIS layers, utility service-territory assignments, or Phase 11C content beyond its separate approved-scope brief.

## Required questions

The findings report must answer where population is concentrated; which municipalities anchor the settlement system; major urban/suburban/rural transitions; supported growth/stability/decline; housing patterns; age/household trends; employment concentrations distinct from residence; and data/vintage limitations. Each conclusion is labeled FACT, INFERENCE, or UNCERTAINTY.

## Transition gate

11A passed the package, provenance, scale, quantity, map, negative-scope, and Phase 1–10 immutability checks. Sol formally accepted and froze Phase 11A under `reports/phase11a_population_settlement_freeze_manifest.json`. Its accepted package is 62 nodes, 918 observations, 44 relationships, 34 sources, nine uncertainty records, and Map 35. Phase 11B uses it as an immutable baseline. Phase 11C is approved scope only and is not implemented.

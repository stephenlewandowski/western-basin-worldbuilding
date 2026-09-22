# Prototype 4.3 — Farm 2075 — Validation Report

Status: ACCEPTED (builder-level semantic checks 16/16; visual/text-collision QA PASS; human visual QA PASS)

This is a synthetic Western Basin farm unit. It is not a real parcel, a forecast, a universal adoption claim, or a quantitative yield / nutrient / profitability model.

## Checks
- [PASS] all four primary panels exist: four non-empty PNGs
- [PASS] contact sheet exists: outputs/atlas/prototypes/4_3_farm_2075/4_3_contact_sheet.png
- [PASS] all required source tables load with required schemas: 12/12 tables
- [PASS] agriculture is represented as synthetic field geometry: no real parcel or crop-specific parcel table is used
- [PASS] scenario / sketch labels are explicit: A S/K; B E → S/K; C S/K; D E → S/K
- [PASS] no unsupported quantitative encoding: illustrative area and equal-weight connectors; no yield/load/capacity claims
- [PASS] controlled drainage and retention do not imply zero export: downstream export / discharge remains visible in panels A, B, and D
- [PASS] connected-not-closed boundary is explicit: external inputs, products, residuals, service, and export remain visible
- [PASS] maintenance is visibly represented: operations / repair, staging, gates, pumps, service roads, and replacement modules
- [PASS] agriculture remains primary land use: four dominant annual field blocks remain the largest visual mass
- [PASS] external inputs and outputs remain visible: left/right boundary callouts and operating-logic lanes
- [PASS] E and S/K remain distinguishable: status badges, wording, and separate palette roles
- [PASS] no Great Black Swamp held geometry introduced: no geographic geometry input or held polygon is used
- [PASS] no Phase 1–16 protected artifact changed: []
- [PASS] Prototype 2.3 accepted outputs unchanged: []
- [PASS] no animation or Prototype 5.3 output created: static 4.3 scope only

## Visual QA

- [PASS] 4.3C final BOUNDARY bullet is fully visible with a safe right margin; the rendered text bounding box remains inside the sidebar slot.
- [PASS] 4.3C sidebar text has no renderer-bounding-box collision.
- [PASS] 4.3C contact-sheet thumbnail shows the corrected BOUNDARY bullet without clipping.
- [PASS] 4.3A, 4.3B, and 4.3D SHA-256 hashes are unchanged by the correction.
- [PASS] 4.3C blockout geometry and data semantics are unchanged; only the final BOUNDARY bullet was wrapped for fit.
- The source manifest remains the builder's pre-visual-QA WORKING / PENDING inventory; final STATIC acceptance is recorded in this report and the mutable project status surfaces after visual QA.

## Epistemic and scenario boundary

- E = accepted evidence/model constraints; S/K = 2075 scenario and sketch design choices; C = no canon created.
- The source tables are read-only inputs. No Phase 1–16 artifact or accepted Prototype 2.3 output is intentionally changed.
- No Great Black Swamp held geometry, real parcel boundary, measured dimension, performance claim, generic resilience score, circularity score, or unsupported quantitative encoding is used.
- Controlled drainage, retention, and reuse are shown as partial interfaces. Downstream export/discharge remains possible: CONNECTED, NOT CLOSED.
- Monitoring provides information; human-supervised decisions and maintenance remain separate functions.

## Source inventory

- `data/processed/networks/water_system_nodes.csv` — 14 rows
- `data/processed/networks/water_system_edges.csv` — 15 rows
- `data/processed/networks/biogeochemical_flux_edges.csv` — 24 rows
- `data/processed/analysis/biogeochemical_control_register.csv` — 10 rows
- `data/processed/networks/ecology_system_nodes.csv` — 16 rows
- `data/processed/networks/ecology_system_edges.csv` — 20 rows
- `data/processed/analysis/ecological_indicators_2026.csv` — 3 rows
- `data/processed/networks/energy_system_nodes.csv` — 18 rows
- `data/processed/networks/energy_system_edges.csv` — 17 rows
- `data/processed/analysis/technology_system_nodes.csv` — 18 rows
- `data/processed/integration/technology_system_interfaces.csv` — 44 rows
- `data/processed/integration/technology_dependencies.csv` — 32 rows

## Outputs

- `outputs/atlas/prototypes/4_3_farm_2075/4_3a_farm_unit_2075.png`
- `outputs/atlas/prototypes/4_3_farm_2075/4_3b_water_nutrient_management.png`
- `outputs/atlas/prototypes/4_3_farm_2075/4_3c_farm_system_assembly.png`
- `outputs/atlas/prototypes/4_3_farm_2075/4_3d_operating_logic.png`
- `outputs/atlas/prototypes/4_3_farm_2075/4_3_contact_sheet.png`
- `outputs/atlas/prototypes/4_3_farm_2075/4_3_source_manifest.json`

Human visual QA passed for the scoped mechanical correction. Phase 17A Prototype 4.3 STATIC is ACCEPTED.

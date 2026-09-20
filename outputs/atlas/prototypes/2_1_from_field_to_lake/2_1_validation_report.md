# Prototype 2.1 — From Field to Lake — Validation Report

- Prototype: 2.1 (Phase 17A)
- Date: 2026-09-20
- Result: **PASS**
- Checks passed: 29 / 29

## Checks

- [x] 1a physical layer is sole physical-waterway source
- [x] 1b all hydrography_physical features physical_geometry=True — 86410 features, 0 non-physical
- [x] 2a network connectors carry explicit physical_geometry flag
- [x] 2b connectors include non-physical features — 16347 non-physical connectors
- [x] 2c manifest records network_connectors layer as separate, dashed context
- [x] 2d routing_inferred_unresolved documented as non-render
- [x] 3a manifest declares no Great Black Swamp geometry
- [x] 3b no swamp-named layer in geographic source set
- [x] 4a manifest Maumee Bay representation is interface (no standalone polygon)
- [x] 5a manifest intake_geometry_used=False
- [x] 5b Toledo is civic anchor only
- [x] 5c legacy glos_crib not used as geometry
- [x] 6a all track tokens in accepted vocabulary
- [x] 7a no HAB track present
- [x] 7b manifest hab_context_constituent=False
- [x] 8a manifest release_process_introduced=False
- [x] 8b no 'release' in approved process list
- [x] 8c no standalone release relationship category
- [x] 9a manifest quantitative=False
- [x] 9b all flux edges report unknown quantity — {'unknown quantity'}
- [x] 9c flow_styling uniform qualitative
- [x] 10a manifest deterministic_nutrient_to_hab=False
- [x] 11a all required input paths exist in repo
- [x] 11b optional inputs present or documented absent — 9 optional entries; 0 absent but optional
- [x] 12a no protected frozen artifact modified in working tree — 0 protected path(s) modified: []
- [x] 13a all four SVGs parse
- [x] 14 grayscale proofs present
- [x] 15 50%-size proofs present
- [x] matrix rows match data-driven re-derivation

## Qualitative-only scope

- All figures are qualitative (quantity_status = unknown quantity for every flux edge).
- No line width, particle count, color intensity, brightness, spacing, or visual duration encodes
  load, concentration, velocity, probability, severity, or travel time.
- No deterministic nutrient → HAB edge is produced; receiving-water conditions remain a distinct
  process domain.

## Frozen-artifact boundary

- No Phase 1–16 protected/frozen artifact or manifest was modified by this build.
- All required and optional scientific inputs were read-only.
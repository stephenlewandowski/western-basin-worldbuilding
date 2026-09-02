# Freight Dependency QA

## Required products

- `freight_dependency_edges.csv`: 20 qualitative dependency edges.
- `freight_dependency_register.csv`: 12 dependency-register rows.
- `modal_substitutability_matrix.csv`: six rows and eight analytical columns.
- `freight_dependency_matrix_2026.csv`: six rows and eight analytical columns.
- Map 19 PNG/SVG.
- Dependency matrix PNG/SVG.

## Dependency QA

- Port/marine gateway, Class I rail, highway, fuel, industrial/material,
  agricultural/bulk, and external-market interfaces are represented.
- Dependency classes are qualitative and explicitly separated from risk,
  vulnerability, failure probability, and optimization.
- Known alternatives are not inferred from corridor proximity.
- W&LE and facility-specific Woodville/Genoa/Elmore access remain qualified or
  unknown.
- Luckey disposal remains a generalized/documented logistics dependency without
  route geometry.

## Baseline immutability

The Phase 5C validator checks the Phase 5A freeze manifest, Phase 5B freeze
manifest, Phase 4A–4C freezes, and the complete 38-file Maps 01–16b baseline.
It also checks the Phase 5A/5B tables and Map 17/18 hashes. These checks passed.

## Boundary QA

- No shipment volume, schedule, train/truck/vessel count, or pipeline capacity.
- No facility-specific route or hazardous-material route.
- No security-target map, exploit path, sabotage opportunity, or sensitive
  logistics topology.
- No future freight content.
- Map 19 is framed as dependency concentration, not vulnerability.
- The Materials Corridor remains a network interpretation, not geography.

## Artifact validation

`src/python/systems/validate_freight_dependencies.py` checks the tables, source
provenance, qualitative classes, frozen Phase 4A/4B/4C/5A/5B artifacts, Map 19,
and the dependency matrices.
`src/R/systems/validate_freight_dependencies.R` independently checks schemas,
counts, endpoints, source presence, qualitative values, and visual artifacts.

The machine-readable result is `reports/freight_dependency_artifact_check.json`.
The build manifest is `reports/freight_dependency_manifest.json`.

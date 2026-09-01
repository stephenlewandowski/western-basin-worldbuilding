# Phase 4A Observation System QA

## Scope

Phase 4A establishes a modest factual 2026 observation-to-decision baseline and
Map 14. The package contains four representative domains and does not attempt an
exhaustive sensor or organization inventory.

## Structural QA

- Node table: 25 unique nodes across four domains.
- Edge table: 21 unique relationships with valid node endpoints.
- Node and edge schemas match the simple Phase 4A specification.
- Every node and edge has a nonblank `source_id`, confidence, and notes field.
- Source IDs resolve to entries in `metadata/sources.yml`.
- The two geolocated nodes are public stations with source-backed coordinates:
  GLOS Toledo crib and USGS 04193500 at Waterville.
- Abstract networks, data products, forecasts, organizations, and responses
  remain without coordinates and are rendered schematically.

## Chain QA

- A — HAB / drinking water: Lake Erie context → GLOS/NOAA GLERL observation →
  public data/HAB forecast → City of Toledo water decision → monitoring and
  treatment operations. The external forecast-to-Toledo interface is qualified;
  no direct machine feed is claimed.
- B — hydrology / flood: Lower Maumee → USGS streamgage/NWIS → NOAA NWPS → NWS
  warning → public-safety response. Station-specific internal forecast
  ingestion and local emergency action are not modeled.
- C — environmental / regulatory: regulated-facility context → NPDES monitoring
  and reporting → EPA ECHO → NPDES authorities → program-level compliance,
  permitting, or reporting response. No named-facility finding is made.
- D — energy information: regional grid context → public PJM operating data →
  PJM → high-level operations/planning coordination, with EIA statistics as
  parallel public context. No SCADA or sensitive telemetry is represented.

## Boundary QA

- No automated `triggers` relationship is present.
- No cyber/security architecture, surveillance-state scenario, AGI governance,
  AI decision authority, fictional sensor network, military monitoring, or
  future 2050/2075 layer is present.
- Operating, public, planned, and unverified distinctions are not imported as
  new factual claims; this layer uses only public 2026 program/product status.
- Toledo intake-coordinate uncertainty remains explicit and unresolved.
- Great Black Swamp status remains **C — HOLD / noncanonical**.
- Accepted Maps 01–13b are regression-checked and are not rebuilt or modified.

## Artifact QA

`src/python/systems/validate_observation_system.py` validates the tables, source
registry references, Map 14 PNG/SVG integrity, phase manifest hashes, and all
prior Map 01–13b hashes. `src/R/systems/validate_observation_system.R` provides
an independent schema/count/endpoint check and writes the R validation figure.

The final validation results are recorded in
`reports/observation_system_artifact_check.json` and the R validation output is
`outputs/figures/observation_system_R_validation.png`.

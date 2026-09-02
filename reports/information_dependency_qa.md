# Phase 4B Information Dependency QA

## Structural QA

- `information_dependency_edges.csv`: 20 unique dependencies.
- `information_blind_spots.csv`: 10 unique evidence-qualified blind spots.
- `decision_authority_matrix.csv`: four unique domain rows and five role columns.
- Dependency endpoints reuse Phase 4A node IDs; no new physical nodes were added.
- Every dependency, blind spot, and authority row has a source ID and confidence.
- Source IDs resolve through `metadata/sources.yml`.
- Qualitative fields use the approved classes; matrix values are low/moderate/high/unknown only.

## Chain QA

- HAB / drinking water: public GLOS and GLERL observation context → public data/HAB forecast → City of Toledo water authority and operations. Direct external forecast handoff remains qualified.
- Hydrology / flood: USGS representative gauge/NWIS → NOAA NWPS → NWS warning/public-safety interface. Station-specific ingestion and local response authority remain unassigned.
- Environmental / regulatory: program monitoring/reporting → EPA ECHO → EPA/state-authorized NPDES oversight → program-level response. No facility finding is asserted.
- Energy information: EIA statistics and PJM public operating information → high-level PJM coordination context. No sensitive operational detail is represented.

## Immutability QA

The Phase 4B Python validator compares all Phase 4A manifest artifacts,
including Map 14 PNG/SVG and both Phase 4A tables. The Phase 4A validator also
checks all prior Map 01–13b hashes. These checks passed.

## Boundary QA

- No attack path, exploit method, credential assumption, or vulnerability scan.
- No SCADA, control-network, control-center, private-telemetry, or cyber
  architecture detail.
- No unsupported automated decision or `triggers` relationship.
- No privacy-impact assessment, surveillance-state model, AI decision authority,
  fictional sensor network, military monitoring, or future scenario.
- Public, partially public, operational, and unknown access classes remain
  distinct; no classified status is inferred.
- The GLOS coordinate is not promoted to the physical Toledo intake coordinate.
- Great Black Swamp remains **C — HOLD / noncanonical**.

## Artifact QA

`src/python/systems/validate_information_dependencies.py` validates the tables,
source registry, matrix, Map 15 artifacts, manifest hashes, and Phase 4A
immutability. `src/R/systems/validate_information_dependencies.R` independently
checks schemas, counts, endpoint validity, source-key presence, qualitative
classes, and Map 15/matrix SVG/PNG artifacts.

The machine-readable result is `reports/information_dependency_artifact_check.json`.
The artifact manifest is `reports/information_dependency_manifest.json`.

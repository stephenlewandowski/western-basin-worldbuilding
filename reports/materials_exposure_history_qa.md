# Phase 2C Materials / Exposure History QA

## Acceptance result

**PASS.** Map 09 and its four supporting history tables meet the Phase 2C
scientific and structural acceptance criteria. Machine-readable results are in
`materials_exposure_history_artifact_check.json`; artifact hashes are in
`materials_exposure_history_manifest.json`.

## Scientific checks

| Area | Result | Evidence / disposition |
|---|---|---|
| Luckey operating dates and roles | PASS | 1942–1945 magnesium; 1949–1958 beryllium production; 1957–1960 sintering/powder blending, all sourced to USACE. |
| Luckey contaminants and media | PASS | USACE-listed beryllium, lead, Ra-226, Th-230, U-234, and U-238; soil and groundwater roles are separated from historical products. |
| Remediation status | PASS | FUSRAP designation/agency history, remedy decisions, excavation, building removal, monitoring, and qualified future plans are source-grounded. |
| No modern Luckey production implication | PASS | Graph role remains `legacy_cleanup`; map labels current remediation separately from historical production. |
| Elmore classification | PASS | `advanced_processing`, `local_resource=false`; map states not extraction. |
| Modern strategic relationships | PASS | Kairos 2022-07-27 and CFS 2025-10-31 retain company-statement provenance and status limitations. |
| Exposure classification | PASS | Seven qualified pathways; zero documented individual exposure findings. Environmental contamination is not treated as completed human exposure. |
| Health outcomes | PASS | No illness is attributed to any Luckey or Elmore individual. NIOSH/ATSDR health mechanisms are contextual. |
| Modern controls | PASS | OSHA context is generalized; no facility compliance or zero-risk claim is made. |

## Spatial and temporal checks

- Authoritative facility points are used for Luckey and Elmore; Toledo,
  Woodville, Genoa, Oak Harbor, and Fremont are orientation only.
- No contamination polygon, groundwater plume, flow arrow, exposure radius,
  residential buffer, freight route, or Materials Corridor geometry exists.
- The 2025 groundwater monitoring finding is represented textually and in the
  event table, without direction or extent.
- All 30 events pass start/end ordering and date-precision checks. Exact dates
  appear only where a source supports them; month/year/range/approximate values
  retain lower precision.
- Planned 2027–2030 milestones are explicitly labeled as plans.

## Visual review

The final 2994 × 1957 PNG was inspected at full resolution after one layout
revision. PASS: Luckey and Elmore use distinct symbols/colors and explicit role
labels; the timeline remains readable; historical production, legacy/oversight,
remediation, and current/planned categories do not visually collapse; the
qualified pathway schematic states that no individual exposure finding is made.
Late-period labels and the OSHA context note do not overlap.

## Data / graph checks

- History tables: 30 events, 9 substances, 7 pathways, 13 dedicated sources.
- Shared graph: 30 nodes and 31 edges after an idempotent 5-node/5-edge
  cross-system extension.
- New edges connect materials to coarse Exposure / Environmental Health
  interfaces only. There is no direct Luckey-to-Elmore edge.
- The development GeoPackage remains unchanged at 16 layers; Map 09 needs no
  new geometry layer.
- Phase 2C creates no Map 10 or future-scenario object.

## Validation record

The Phase 2C Python validator checks schemas, IDs, dates, sources, classifications,
graph constraints, map formats/resolution, GeoPackage inventory, and prohibited
artifacts. The independent base-R validator separately checks core chronology,
exposure classification, graph roles, and emits a validation figure. Repository-
wide regression outcomes are recorded in the final project handoff/commit state.

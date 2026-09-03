# Phase 9 Climate Correction QA Log

Status: transparent post-integration correction of unaccepted Phase 9 working baselines. The original Phase 9A and Phase 9B implementation commits were not amended or rewritten.

## Authorization and preserved state

Sol authorized correction of the unaccepted Phase 9A and Phase 9B working baselines for the identified factual, provenance, validator, and QA defects. Accepted/frozen Phase 1–8 artifacts remain outside the correction scope. The pre-correction Phase 9C package was preserved in local checkpoint commit `affde66` and was not integrated into `main` before correction.

Original Phase 9A integrated commit: `8a76895c62be6af8304d93f50895828812b13e26`.

Original Phase 9B integrated commit: `ae6e946b17bedb9670ef1d6c5f3a958b33062e82`.

## Phase 9A factual correction

Direct verification against the raw USGS NWIS response for site 04193500 and the scoped query in source `b9_usgs_dv` found:[1]

- `2026-07-29 = 313 cfs`.[1]
- `2026-09-02 = 476 cfs`.[1]

The builder now computes the minimum from the raw series, and the observation table, acquisition summary, findings report, manifest, and validators all carry the corrected date/value. The affected observation is `HZO-015`; the maximum observation `HZO-014` remains `68,200 cfs` on `2026-04-03`. No Map 29 annotation used the erroneous date; its original manifest-protected artifact was preserved because the map contains no flow-extrema date annotation.[1]

## Phase 9A provenance decisions

The correction uses narrowing and explicit inference rather than broad new research:

| Record(s) | Decision | Correction |
|---|---|---|
| `HZ-004` | C — explicit project inference | Repointed the node to the representative USGS source, lowered confidence to limited, and state that the gauge does not establish watershed-wide runoff or an Atlas 14 surface. |
| `HZ-008` | C — explicit project inference | Retained Atlas 14 only as site precipitation-frequency context; the urban drainage/burden relationship is explicitly inferred and does not claim outfalls, imperviousness, or performance. |
| `HZE-004` | C — explicit project inference | Relationship basis now identifies representative-gauge plus hydrologic logic; tributary amplification is not presented as directly quantified. |
| `HZE-007` | C — explicit project inference | Relationship basis now identifies precipitation-frequency context plus urban-drainage logic; Atlas 14 is not treated as direct evidence of urban burden. |
| `HZ-016` | A — direct source correction | Node source changed from the general Storm Events landing page to the dated `b9_storm_events_2025` details snapshot that generated the selected-county counts. |
| `HZE-018` | A — direct source correction | Edge now points to the dated Storm Events snapshot and a dedicated `HZ-028` event-record service node. |
| `HZ-021` | B — narrowed scope | The node is now the NOAA CO-OPS Toledo station context, sourced to `b9_coops_daily`, rather than a network claim supported only by a GLERL landing page. |
| `HZ-024`, `HZE-001`, `HZE-002` | B — scale/source separation | The former mixed climate-data service node was narrowed to the NOAA NCEI Lucas County series. A dedicated ACIS station service node (`HZ-027`) receives `HZE-001`, while `HZE-002` remains county-scale and NCEI-sourced. |
| `HZ-026` | C — explicit project inference | NWS point metadata are limited to forecast/warning service context; developed infrastructure/access effects are explicitly inferred with no asset vulnerability claim. |
| `HZE-021` | C — explicit project inference | NWS winter products support hazard/forecast context only; the developed-system relationship is a qualitative physical inference. |
| `HZE-022` | C — explicit project inference | NWS thunderstorm guidance supports hazard definitions only; the developed-system relationship is a qualitative inference with no outage or communications-failure estimate. |
| `HZE-029` | C — explicit project inference | U.S. Drought Monitor supports county drought status only; the developed water-demand relationship is not a direct demand or outage finding. |
| `HZE-030` | C — explicit project inference | ACIS supports the station temperature observation only; the developed-system relationship is explicitly inferred and carries no exposure or health claim. |

The dated Storm Events source is now used consistently for the selected event observations (`HZO-021` through `HZO-026`) and related event-record nodes/edges.[2] The findings and source reports state that these are county event records, not event rates, probabilities, attribution, or hazard surfaces.

## Phase 9A validator and QA correction

The Phase 9A Python and R validators now explicitly check the raw USGS date/value pair, the corrected `HZO-015` row, flagged node/edge source and inference statuses, dated Storm Events provenance, FEMA regulatory-versus-observed flood distinctions, event-record-versus-rate semantics, negative groundwater scope, spatial-scale separation, and negative health/social scope.[3][4] The R validator independently recomputes all 11 Phase 9A manifest-listed artifact SHA-256 hashes through the system `sha256sum` executable.

Phase 9A remains a factual 2026 layer and contains no future rows, hazard probability, composite score, health/social-vulnerability score, or deterministic hazard surface.

## Evidence references

[1] https://waterservices.usgs.gov/nwis/dv/?format=json&sites=04193500&startDT=2026-07-20&endDT=2026-09-03&parameterCd=00060&siteStatus=all
[2] https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz
[3] https://hdsc.nws.noaa.gov/pfds/
[4] https://api.weather.gov/points/41.65,-83.54
[5] https://www.ncei.noaa.gov/stormevents/

## Additional Phase 9A dispositions from independent review

- `HZE-004` now runs from `HZ-006` (the flood interface) to `HZ-004` (the runoff-connectivity interface), so `hydrologically_amplified_by` reads in the intended direction.
- `HZE-023` was removed. NOAA Atlas 14 remains a `reference_product` node and is not represented as a historical occurrence.
- `HZ-017` is now typed as `historical_event_context`, not `climate_observation`.
- The ACIS registry source type is now `station_climate_service`.
- The final Phase 9A package contains 28 nodes and 29 edges; the edge reduction is the explicit removal of the unsupported Atlas 14 occurrence relation.
- The Phase 9A QA report and builder template now state the corrected 28-node/29-relationship count; the Phase 9A manifest entry is refreshed accordingly.

## Phase 9B provenance decisions

Phase 9B corrections use the following dispositions. `relationship_basis` is explicit on dependency edges and `evidence_basis` is mirrored in the register; `support_status` is explicit on controls.

| Record(s) | Decision | Correction |
|---|---|---|
| `HZD-013` | B/C — narrowed product context | Replaced the Lake Level Viewer wind/wave/port claim with calm-day lake-level screening to generalized shoreline context. Wind-driven waves and seiche, port effects, inundation, and damage remain outside this source’s support. |
| `HZD-014`, `CPL-005` | C — qualified compound pathway | Kept seiche as a physical mechanism, separated from background lake-level context, and removed any implied additive level, local shoreline effect, or recurrence estimate. |
| `HZD-015` | D — unsupported/unknown | Lake-wide ice is retained as regional monitoring context; local shoreline, harbor, and ecological effects are explicitly unknown. |
| `HZD-008`, `HZD-022` | D — unsupported/unknown operating effect | Streamflow and lake-level observations no longer assert treatment/intake operating effects. The generalized interfaces remain as explicit unknowns, with the Toledo intake-coordinate discrepancy preserved. |
| `HZD-011` | B — narrowed one-gauge context | Reduced the strength/confidence and reframed the row as generalized receiving-water context from one low-flow gauge, not a basin-wide dilution/transport effect. |
| `HZD-018`, `HZD-019`, `CPL-007` | C — qualified planning/pathway logic | NWS winter products now support forecast input and plausible physical pathways only, not documented freight, road, maintenance, or infrastructure consequences. |
| `HZD-023`, `HZD-024` | B — narrowed information interfaces | Warning is a decision-information interface, and drought assessment is situational-awareness/management input; response and management outcomes are not established. |
| `CPL-001`, `CPL-004`, `CPL-008`, `CPL-009` | C — narrowed plausible compounds | Power is thermal-load context rather than outage evidence; stormwater, communications, and agricultural/ecological effects are explicitly physically plausible and source-qualified, not documented local consequences. |
| `HZC-002`, `HZC-004`, `HZC-007`, `HZC-008`, `HZC-009`, `HZC-012` | A/B — direct role correction or narrowing | NWS warning, CO-OPS, Ohio EPA NPDES, USFWS NWI, H2Ohio, and NWS Great Lakes source roles now match the named interface. Controls distinguish documented planning context, potential-buffer inference, management pathway, tool, and interface-only status; effectiveness is not claimed. |

The Phase 9B package remains qualitative. It contains no unsupported probability, damage, outage, health, exposure, social-vulnerability, or comprehensive emergency-management model. Unsupported or unknown interfaces remain marked as unknown rather than being interpreted as low.[6][7][8]

The winter-source limitation is preserved.[9] Ohio EPA NPDES and USFWS NWI source roles are limited to the named planning and inventory contexts.[10][11]

H2Ohio is limited to the named management-pathway context.[12]

## Validator and R-independence corrections

The R SHA-256 helper uses `sha256sum` when available and the native Windows `certutil -hashfile ... SHA256` path otherwise, so the independent hash checks execute on both supported environments without delegating hashing to Python.

The Phase 9B Python and R validators now check exact schemas, source membership, explicit relationship/support vocabularies, flagged-row source assignments, dependency/register parity, flood regulatory-versus-observed distinctions, event-count-versus-rate semantics, negative groundwater scope, negative health/social scope, map caveats, and independently recomputed Phase 9A/9B manifest hashes. The Phase 9C validators additionally check explicit baseline IDs and corrected Phase 9A/9B source mappings.

## Phase 9C analytical rebaseline

The preserved Phase 9C package was not discarded. Its scenario artifacts were regenerated from the corrected working baselines. Hazard states now reference valid Phase 9A node IDs by hazard family; dependency states reference Phase 9B dependency IDs; resilience states reference Phase 9B controls or explicitly unknown treatment/intake interfaces; and scenario pathway/compound sources match the claims they qualify. The Phase 9C package retains its six qualitative scenario-horizon states and no probability or deterministic impact model.

## Sources

[1] https://waterservices.usgs.gov/nwis/dv/?format=json&sites=04193500&startDT=2026-07-20&endDT=2026-09-03&parameterCd=00060&siteStatus=all
[2] https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz
[3] https://hdsc.nws.noaa.gov/pfds/
[4] https://api.weather.gov/points/41.65,-83.54
[5] https://www.ncei.noaa.gov/stormevents/
[6] https://coast.noaa.gov/llv
[7] https://oceanservice.noaa.gov/facts/seiche.html
[8] https://www.glerl.noaa.gov/data/ice
[9] https://www.weather.gov/cle/winter
[10] https://epa.ohio.gov/divisions-and-offices/surface-water/permitting
[11] https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer
[12] https://h2.ohio.gov/

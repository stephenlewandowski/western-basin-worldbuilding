# Phase 9A Climate Correction QA

This document records the transparent correction applied to the unaccepted Phase 9A working baseline after independent review. Original implementation commit `8a76895c62be6af8304d93f50895828812b13e26` was not amended or rewritten. Sol authorized correction of the unaccepted Phase 9A/9B working baselines; accepted/frozen Phase 1–8 artifacts remain protected.

## USGS observation correction

A direct query to the authoritative USGS NWIS daily-value service for site 04193500 confirmed:

- `2026-07-29 = 313 cfs`.
- `2026-09-02 = 476 cfs`.

The builder recomputes the minimum from the raw response. `HZO-015`, the acquisition summary, findings, manifest, Python validator, and independent R validator now all use `2026-07-29` for the 313-cfs minimum and explicitly retain the 476-cfs value on 2026-09-02 as the contrasting source observation.

## Provenance dispositions

- `HZ-004`: C — explicit project inference. Atlas 14 was removed as direct provenance for the watershed runoff interface; the node now uses the representative USGS source with limited confidence and an explicit watershed-scale limitation.
- `HZ-008`: C — explicit project inference. Atlas 14 is retained only for site/grid precipitation-frequency context. Urban stormwater pathway language excludes outfall, imperviousness, and performance claims and removes the unsupported winter family label.
- `HZE-004`: C — explicit project inference, with direction corrected from `HZ-004 -> HZ-006` to `HZ-006 -> HZ-004` for `hydrologically_amplified_by`.
- `HZE-007`: C — explicit project inference. Atlas 14 does not directly support urban drainage burden.
- `HZ-016`: A — source corrected from the general Storm Events landing page to the dated 2025 details snapshot used to generate the selected-county aggregation; confidence remains moderate for the regional context.
- `HZE-018`: A — edge now points to the dedicated dated Storm Events service node `HZ-028`, preserving direct event-record provenance.
- `HZ-017`: B — typed as `historical_event_context`, not `climate_observation`.
- `HZ-021`: A/B — narrowed to NOAA CO-OPS Toledo station context.
- `HZ-024`: B — narrowed to NOAA NCEI Lucas County climate-series context. Dedicated ACIS station service node `HZ-027` preserves station/county separation for `HZE-001` and `HZE-002`.
- `HZ-026`, `HZE-021`, `HZE-022`, `HZE-029`, and `HZE-030`: C — developed-system and access relationships are explicit qualitative inferences, not direct station, warning, drought, or weather-source findings.
- `HZE-023`: E — removed because Atlas 14 precipitation-frequency context is not a historical occurrence. `HZ-023` remains a `reference_product` node.

The corrected Phase 9A package contains 28 nodes, 29 edges, 28 observations, and 21 sources. Map 29 was not semantically affected by the correction and its original manifest-protected SVG/PNG artifact was preserved; it has no flow-extrema date annotation and no hazard surface.

## QA implementation

The Phase 9A Python and R validators explicitly check the raw USGS date/value pair, corrected observation, flagged source IDs and inference classifications, dated Storm Events provenance, FEMA regulatory-versus-observed flood semantics, event-count-versus-rate semantics, groundwater negative scope, scale separation, negative health/social scope, and the Phase 9A manifest hashes. The R validator independently recomputes all 11 manifest-listed artifact SHA-256 hashes.

Phase 9A remains a factual 2026 baseline with no unsupported probability, composite score, deterministic hazard surface, health/social-vulnerability score, or future rows.

## Evidence

[1] https://waterservices.usgs.gov/nwis/dv/?format=json&sites=04193500&startDT=2026-07-20&endDT=2026-09-03&parameterCd=00060&siteStatus=all
[2] https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz
[3] https://hdsc.nws.noaa.gov/pfds/
[4] https://api.weather.gov/points/41.65,-83.54
[5] https://www.ncei.noaa.gov/stormevents/

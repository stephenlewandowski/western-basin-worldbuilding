# Phase 9A Climate & Natural Hazards QA

## Structural and provenance checks

The package contains 28 hazard nodes, 29 directed relationships, 28 quantitative/context observation records, and 21 source-registry records. Every node and edge has a source ID, scale, confidence, reality/canon status, and notes. Every observation retains metric, value, units, period, station_or_scope, spatial scale, observed_or_modeled status, source ID, confidence, and limitations.

## Scientific boundary checks

The validator explicitly checks selected semantic boundaries: the FEMA regulatory-flood node and related edges retain modeled-regulatory status and observed-flood exclusions; Storm Events observations retain the dated-snapshot source, county-event-record scale, and non-rate/non-probability notes; groundwater mentions are limited to explicit negative-scope notes; and the station, county, watershed, floodplain, shoreline, regional, and forecast-area categories remain distinct. It also rejects composite scores, unsupported probabilities, future scenario rows, health outcomes, personal exposure/dose, social-vulnerability rankings, neighborhood risk rankings, deterministic event surfaces, and unsupported positive groundwater claims. Great Lakes seiche/wind setup is checked as distinct from ocean storm surge.

## Map QA

Map 29 is a PNG/SVG pair with inspectable SVG text, source-backed station markers, generalized family-interface rings, a legend, scale notes, and explicit non-surface caveats. The map does not draw hazard polygons, composite scores, deterministic risk zones, or unsupported future layers.

## Completeness and limitations

The ACIS precipitation record has missing and trace values, so reported sums and threshold counts are qualified. The USGS and CO-OPS records are station-scale. U.S. Drought Monitor values are weekly county assessment products. Storm Events counts use a dated 2025 archive snapshot and a selected county scope. Warning thresholds are not observations. These distinctions are checked by explicit row, field, source, scale, and negative-scope assertions and remain visible in the data tables and reports.

## Protected prior content

Phase 8A-8C freeze manifests and all prior accepted manifests are checked before Phase 9A integration. The Great Black Swamp hold and Toledo intake-coordinate discrepancy are preserved. No health/social-vulnerability module, emergency-management expansion, unsupported hazard probability, release, or tag is included.

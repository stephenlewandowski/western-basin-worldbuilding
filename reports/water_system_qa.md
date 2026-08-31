# Water System v0.1 — QA

Built: 2026-08-29

Follow-up physical-hydrography decision: 2026-08-31

## Automated checks

- [x] Basin includes HUC-8s 04100003–04100009 and HUC-12 IDs share one of those prefixes.
- [x] Directed graph edges reference valid node IDs.
- [x] The baseline network contains Maumee → Maumee Bay → Western Lake Erie → HAB response → intake → treatment.
- [x] Internal WBD HUC-12 routing connectors form a directed acyclic graph.
- [x] Real facilities have public source identifiers and coordinates.
- [x] Fictional/scenario nodes have null longitude/latitude.
- [x] Historical swamp reference is excluded from GIS geometry layers.
- [x] Nutrient quantities are null except separately sourced City system figures.
- [x] PNG and SVG pairs exist for Maps 01–05.
- [x] Python graph render exists in PNG/SVG.
- [x] Base-R renderer consumes exported geographic line coordinates independently.

## Counts

- HUC-8 polygons: 7
- HUC-12 polygons: 252
- NHDPlus flowlines (order ≥3): 864
- Inferred WBD HUC-12 routing connectors: 251
- NWI wetland polygons ≥25 acres in focus: 608
- Network nodes: 14
- Network edges: 15

## Human-review gates before Phase 2

1. Reconcile the GLOS intake monitoring coordinate with historic crib/light and raw-water pipeline records.
2. Confirm whether a public, authoritative Great Black Swamp polygon exists before georeferencing/digitizing any historical extent.
3. **Resolved for current development:** authoritative USGS 3DHP evidence now replaces or supersedes 239 inferred routing relationships, with 12 unresolved relationships retained explicitly as abstract analytical edges.
4. Review map extents and label density with a local hydrologist/GIS practitioner.

Detailed Phase 2 modeling should not proceed until items 1–2 are dispositioned.

## Follow-up QA — authoritative physical hydrography

The [physical hydrography reconciliation](physical_hydrography_reconciliation.md) evaluates USGS 3DHP Flowline layer 50 against all 251 inferred WBD connectors. Final results are 93 physical replacements, 115 authoritative-connector replacements, 31 already-redundant relationships, 12 unresolved relationships, and 0 invalid baseline inferences. It preserves physical channel/canal/drainageway geometry separately from official non-watercourse connector classes and explicitly retains unresolved project routing edges. See the [source review](water_hydrography_source_review.md), [connector-by-connector CSV](wbd_connector_reconciliation.csv), [unresolved-routing summary](unresolved_routing_summary.csv), [current-development transition manifest](development_gpkg_transition_manifest.json), and [machine-readable QA summary](physical_hydrography_qa.json).

Human decision: **B — ACCEPT WITH QUALIFICATION**. The preferred three-layer representation is integrated into the current-development GeoPackage. The historical `v0.1-water-system` artifact and released Map 01–05 files remain unchanged.

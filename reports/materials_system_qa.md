# Phase 2A–2B Materials System QA

Review date: 2026-08-29

Status: **PHASE 2B COMPLETE — AUTOMATED AND VISUAL QA PASSED**

Phase 2A's validated scientific baseline was selectively integrated onto current main without applying its stale documentation or GeoPackage. Phase 2B then extended that baseline with one shared 2026 node/edge architecture and Maps 07–08.

## Delivered scope

Phase 2A answers one baseline question: **What physical resources and strategic-processing capabilities exist in the Western Basin region in 2026?**

Delivered:

- `geology_bedrock_units` — 90 Ohio DNR bedrock features clipped to the map focus area; supporting context layer.
- `geology_carbonate_units` — 85 carbonate-bearing Ohio DNR features selected from unit name, lithology, and description.
- `industrial_mineral_sites` — 3 verified current/recent industrial-mineral sites.
- `strategic_material_sites` — 1 verified strategic-processing site.
- `legacy_remediation_sites` — 1 verified current remediation site.
- Map 06 in PNG and SVG.
- Layer-derived render tables and an independent base-R QA render.

Map 07 and Map 08 have been created. No Map 09–10 product, release, future scenario, corridor polygon, production/reserve quantity, groundwater-flow surface, or sixth macroregion has been created.

## Phase 2B inventory

- 25 shared-schema nodes: 12 carbonate, 11 beryllium, and 2 future-interface nodes.
- 26 edges: 6 observed, 4 documented named supply relationships, 9 engineering dependencies, 2 scientific inferences, and 5 supply-chain inferences.
- 14 complete machine-readable source records.
- `materials_flow_nodes` in the current-development GeoPackage contains the 6 spatially located Phase 2B nodes; nonspatial external and end-use nodes remain in CSV.
- Map 07 presents regional carbonate occurrence and sourced facility roles alongside a generalized functional network.
- Map 08 spatially anchors Elmore and Luckey while keeping nonlocal feed and downstream sectors schematic.

## Phase 2B scientific QA

- Local carbonate resource and extraction/processing distinctions: pass.
- 1:500,000 geology limitation: explicit on map and in data notes.
- No unsupported plant-to-plant contract, shipment quantity, schedule, mode, or route: pass.
- Water/wastewater relationship classified as generalized engineering dependency: pass.
- Accepted `hydrography_physical` used for context; connectors and unresolved routes omitted: pass.
- No groundwater flow, quarry capture, dewatering, wetland drawdown, or aquifer-connectivity claim: pass.
- Elmore `advanced_processing`, `local_resource=false`, and explicitly not a mine: pass.
- External beryllium feed represented schematically as domestic Utah-derived and imported supply: pass.
- CFS relationship classified as documented, dated 2025-10-31, and limited to the announced BeF2/FLiBe supply relationship: pass.
- Kairos relationship dated 2022-07-27 with 2026 status unresolved: pass.
- Broad strategic sectors remain inference, not named customers: pass.
- Luckey remains legacy/remediation: pass.
- No future scenario, Map 09/10, or Materials Corridor geometry: pass.

## Facility and classification review

| feature | 2026 classification | local resource? | QA result |
|---|---|---:|---|
| Martin Marietta Woodville Lime Facility | `lime` / `primary_processing`; co-located extraction context is documented in notes | Yes | Pass — official facility page plus company/ODNR corroboration |
| Area Aggregates Woodville Plant | `limestone` / `extraction` | Yes | Pass with medium location confidence — current 2026 permit; point is street-address resolution |
| Graymont Genoa Plant | `lime` / `primary_processing` | Yes | Pass — official company address and dolomitic-lime description |
| Materion Elmore Advanced Materials Facility | `beryllium` / `advanced_processing` | **No** | Pass — explicitly not a mine; USGS 2026 places extraction/imported feed upstream of Ohio processing |
| Luckey FUSRAP Site | `remediation` / `legacy_cleanup` | No current resource claim | Pass — active federal cleanup of historical activity, not active strategic production |

## Automated QA results

- Required layer names: pass.
- Required common fields and non-null provenance: pass.
- EPSG:4326 storage CRS: pass.
- Non-empty, valid geometry: pass.
- Facility points within the Western Basin focus bounds: pass.
- Controlled supply-chain roles: pass.
- Woodville/Genoa local versus Elmore imported-feed distinction: pass.
- Luckey legacy/remediation distinction: pass.
- Unsupported capacity, reserve, production, and groundwater-flow fields: absent.
- Map 06 PNG opens and verifies; SVG parses: pass.
- Python reads all GeoPackage layers and renders the publication map: pass.
- Base R reads layer-derived polygon/site tables, validates classifications, and renders a separate QA figure: pass.
- Phase 1 GeoPackage layers remain present with validated counts (7 HUC-8, 252 HUC-12, 864 physical flowlines, 251 inferred connectors, 10 Lake Erie component features, 608 wetlands, 2 facilities): pass.
- Existing Phase 1 maps, reports, scripts, and network tables are not modified by the Phase 2A builder: pass by repository diff review.

Machine-readable results are in `reports/materials_system_artifact_check.json` after running the validator.

## Location precision

Facility geometry is address-point geometry, not parcel, quarry, plant-footprint, or legal permit-boundary geometry. Martin Marietta, Graymont, Materion, and Luckey resolve as point addresses. Area Aggregates resolves as a street address and is therefore medium confidence. The address sources are official; the coordinate transformation is recorded separately as ArcGIS World Geocoder. No coordinate was generated or visually guessed by the model.

## Unresolved geology and hydrogeology issues

1. The ODNR bedrock layer is a 1:500,000 compilation. It is appropriate for regional occurrence context but not quarry-scale resource delineation.
2. The carbonate subset includes mixed/interbedded units when their authoritative description names limestone or dolomite. Before a dedicated carbonate network map, review whether the legend should separate predominantly carbonate from interbedded carbonate-bearing units.
3. The latest located official statewide mineral-industry inventory is 2021. The three plotted industrial sites have additional 2026-current evidence, but a comprehensive active/inactive facility census remains open.
4. Address points should be replaced by authoritative parcels, mine permits, or facility footprints if those geometries become available under usable terms.
5. No current, sufficiently resolved regional potentiometric dataset was found that supports 2026 groundwater-flow arrows. The 1986 USGS surface is historical and remains excluded.
6. Karst and aquifer-vulnerability context may be useful later, but the ODNR probable-karst layer is generalized and must not be read as a site-specific hazard or groundwater-flow map.
7. Great Black Swamp geometry remains **C — HOLD**. Physical hydrography is accepted for current development under **B — ACCEPT WITH QUALIFICATION**. These statuses are unchanged by Phase 2B.
8. `local_resource=true` for industrial-mineral sites identifies the local carbonate resource class and local extraction/processing system; it does not yet establish a verified facility-to-facility feed route for every plant, including Genoa.

## Implemented Phase 2B designs

### Carbonate extraction and transformation network

Map 07 uses a spatial regional panel plus node-and-edge functional panel, anchored to sourced quarry/plant points rather than a filled “Materials Corridor” polygon. It separates `geologic_occurrence`, `extraction`, and `primary_processing` and treats products/functions qualitatively.

### Beryllium strategic-processing network

Map 08 uses a regional Elmore/Luckey anchor plus schematic external-feed and downstream nodes. Nonlocal feed is explicit, Elmore is `advanced_processing`, broad sectors are dashed inference, and named CFS/Kairos relationships are solid. No physical shipment route is drawn.

## Cartographic review

Both maps were reviewed at full raster resolution after the final render. Map 07 retains readable extraction/processing symbols, a clear water-system dependency, and explicit scale/hydrogeology cautions. Map 08 keeps Elmore central, external feed schematic, end-use nodes legible, and Luckey subordinate. The final QA record in `reports/materials_phase2b_artifact_check.json` records raster dimensions and SVG parsing.

Final regression results: Phase 1 Python/R pass; physical-hydrography Python/R pass with 102,757 raw features and the accepted 86,410 / 16,347 / 12 semantic separation intact; Great Black Swamp QA pass with the candidate still noncanonical; Phase 2A Python/R pass; repository-relative Markdown links pass; application tests pass (22/22). R emitted Windows locale warnings but completed successfully.

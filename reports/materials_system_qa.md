# Phase 2A Materials System QA and Human-Review Gate

Review date: 2026-08-29  
Status: **AUTOMATED QA PASSED — STOPPED FOR HUMAN REVIEW**

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

No Map 07–10 product, release, future scenario, corridor polygon, production/reserve quantity, groundwater-flow surface, or sixth macroregion has been created.

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
7. The three Phase 1 QA gates remain open in GitHub: intake-coordinate reconciliation, authoritative historical swamp geometry, and physical hydrography in place of inferred WBD connectors.
8. `local_resource=true` for industrial-mineral sites identifies the local carbonate resource class and local extraction/processing system; it does not yet establish a verified facility-to-facility feed route for every plant, including Genoa.

## Recommended design for subsequent maps — after human approval

### Carbonate extraction and transformation network

Use a node-and-edge supply-chain diagram anchored to verified quarry/plant sites rather than a filled “Materials Corridor” polygon. Separate `geologic_occurrence`, `extraction`, and `primary_processing`. Show products qualitatively (aggregate, lime, treatment inputs) only where sourced. Add parcel/permit geometry and a current site census before treating the layer as comprehensive. A small inset can explain regional carbonate bedrock without implying that all mapped carbonate is economically recoverable.

### Beryllium strategic-processing network

Use a multi-scale map: national/upstream origin inset plus a detailed Elmore facility context. Make the nonlocal raw-material feed visually explicit, classify Elmore as `advanced_processing`, and distinguish downstream defense/energy/end-use sectors from verified physical shipment routes. Luckey should appear only in a separate historical/cleanup sidebar. Do not connect Woodville, Elmore, and Luckey with a corridor polygon unless governance, logistics, or infrastructure evidence later supports one.

## Human-review stop

Phase 2A stops here. Human review should decide whether to accept the baseline classifications, the mixed-unit carbonate filter, the five facility points and their precision, and the proposed designs above. Do not proceed to Maps 07–10 or a Phase 2 release until that review is recorded.

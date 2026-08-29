# Great Black Swamp Geometry Source Review

Phase 1 Water System v0.1 follow-up QA

Review date: 2026-08-29

Status: **HOLD — review candidate only; GitHub issue remains open**

## Executive Finding

No publicly documented, directly authoritative vector named “Great Black Swamp” was located. The strongest reproducible Ohio evidence is the Ohio Department of Natural Resources (ODNR) distribution of *Original Natural Vegetation of Ohio*, dataset 3135, which digitizes Robert B. Gordon’s 1966 map. Its `VEG_CDE=4` class is “Elm-Ash Swamp Forests.” That class is defensible as a regional swamp-forest evidence layer, but it is not synonymous with the named Great Black Swamp, its conventional envelope, or its drainage area.

One review-only MultiPolygon, `great_black_swamp_candidate_gordon1966`, was generated from unmodified class-4 source polygons using a named-basin selection rule. It was not added to `data/processed/glasspunk_base.gpkg`. Recommendation: **C — HOLD** while ODNR/H2Ohio is asked whether the vector behind its published “Extent of swamp” map can be released.

## Candidate Sources

| Candidate | Finding | Disposition |
|---|---|---|
| ODNR dataset 3135, *Original Natural Vegetation of Ohio* | Official state distribution; polygon digitization of Gordon (1966); complete metadata and source scale | Preferred derivation basis |
| H2Ohio/ODNR, *The History of the Great Black Swamp and Its Evolution Over Time* (rev. 2025) | Official educational PDF distinguishes “Drainage area for swamp” from “Extent of swamp 20,000 years ago,” but supplies no GIS citation, method, layer identifier, attachment, or public vector dependency | Authoritative comparison only; do not trace |
| Ohio EPA and USGS publications | Confirm a broad historic forested-wetland landscape and the distinction between remnant, watershed, and historic landscape concepts; rendered maps/descriptions do not provide a documented statewide named-boundary vector | Supporting comparison only |
| ArcGIS Online `EST_GreatBlackSwamp_Boundary` (`15f454877ac14c51a61f61cd6832415b`) | Public hosted FeatureServer, reused in ErieStat/NOAA-facing maps, but has no source, methodology, date, scale, license, or descriptive metadata and is publicly editable | Rejected as authoritative geometry |
| Supplied reference image | Non-georeferenced rendered overview | Visual reference only; not aligned, traced, or digitized |

The direct-vector search covered ODNR/H2Ohio publications, Ohio GIS/ArcGIS catalog queries, Ohio EPA and USGS searches, and public ArcGIS item/service dependencies. The H2Ohio PDF appears as a standalone asset on the official educational-documents page. No discoverable ArcGIS item with the exact publication title or underlying “Extent of swamp” layer was found as of the review date.

## Preferred Source

**Ohio DNR dataset 3135 — Original Natural Vegetation of Ohio**

Official archive: <https://gis.ohiodnr.gov/geodata/Statewide/OriginalVegetationOhio.zip>

Preserved archive: `data/raw/ohiodnr/original_vegetation_ohio/OriginalVegetationOhio.zip`

SHA-256: `B85529757FED6E5DB7E66EBFEF4A784735AA135575E19DE8F9995A67A940B0F8`

The official archive contains the polygon shapefile, projection file, FGDC-style XML metadata, and the two-page ODNR metadata record titled `3135_Original Natural Vegetation of Ohio.pdf`. These original records are preserved alongside the download.

## Source Authority

The distribution authority is the Ohio Department of Natural Resources. The historical interpretation is Robert B. Gordon, *Natural Vegetation of Ohio at the Time of the Earliest Land Surveys*, Ohio Biological Survey, 1966. ODNR’s metadata says the paper map was digitized for agency land-use analysis. This is stronger provenance than third-party ArcGIS copies, but the historical vegetation boundaries remain Gordon’s generalized interpretation rather than surveyed wetland limits.

ODNR metadata contact: `gis.support@dnr.ohio.gov`.

## Historical Reference Period

The historical reference is the vegetation “at the time of the earliest land surveys.” The interpretation was published in 1966; ODNR’s digital conversion was created circa 2003, with metadata currency dated 2003-07-01 and metadata review/synchronization in 2014. The digital date does not change the historical reference period.

## Original Scale

The original Gordon map scale is **1:500,000**. The source is suitable for regional historical context and broad overlap analysis only. It cannot support parcel, field, ditch, or site-level assertions. Review outputs use EPSG:4326 for exchange and EPSG:5070 for area calculations; the source archive is EPSG:3734 (NAD83 / Ohio North, US survey feet).

## Digital Provenance

- Official source archive retrieved directly from ODNR on 2026-08-29.
- Geometry type: polygon; 1,632 source features.
- Source CRS: EPSG:3734, resolved from the distributed `.prj` and XML metadata.
- Attribute fields: `AREA`, `PERIMETER`, `OR_VEG_SPN`, `OR_VEG_S_1`, and `VEG_CDE`.
- Thirteen vegetation codes occur. The class audit is in `reports/great_black_swamp_class_review.csv`.
- Two statewide source features are invalid; neither is among the 117 selected source features. The candidate is valid after dissolve.
- The preserved raw archive is immutable input. The builder extracts it under `tmp/` and never rewrites the source files.

## Vegetation-Class Selection

Only class 4, **Elm-Ash Swamp Forests**, is included in the review candidate. It is the closest statewide source association to historic swamp forest. It is still broader than a named Great Black Swamp boundary.

Explicit exclusions:

- Class 8, Freshwater Marshes and Fens: retained as coastal/inland wetland context but excluded to avoid equating marsh with swamp forest.
- Class 10, Bottomland Hardwood: excluded to avoid pulling river floodplains into the named swamp.
- Class 6, Prairie Grasslands, and class 7, Oak Savannas: historically important wet-prairie/Oak Openings context, but not classified as swamp forest.
- All upland, bog, special, and beach classes: excluded for the reasons recorded in the class-review CSV.

The table records class counts and areas inside the reproducible project selection extent. The decision is thematic, not an assertion that all class-4 land was conventionally called the Great Black Swamp.

## Derivation Method

1. Read the official ODNR shapefile in EPSG:3734.
2. Select `VEG_CDE=4`.
3. Build a selection frame from official USGS WBD HUC8 polygons: Maumee HUC8s `04100003`–`04100009` plus Cedar-Portage `04100010`.
4. Retain a complete source polygon when its representative point lies inside that HUC8 union. This avoids selecting unrelated statewide features based on tiny boundary slivers.
5. Preserve the selected 117-feature mosaic as GeoJSON.
6. Dissolve those complete polygons into a MultiPolygon review candidate. No clipping to watershed edges is performed.

No image tracing, georeferencing, buffer, smoothing, connectivity threshold, minimum-area threshold, or hand edit is used. Because no connectivity threshold is used, no threshold alternatives are required. Isolated source polygons are preserved. River floodplain, Lake Erie coastal-marsh, wet-prairie, and Oak Openings classes are not folded into the candidate.

The selection frame is analytical: it scopes Gordon’s statewide class to the Maumee and Cedar-Portage drainage region. It is not represented as the swamp’s own drainage boundary.

## Comparison With Official Great Black Swamp Maps

The H2Ohio/ODNR 2025 educational map expressly shows two different concepts: a green “Drainage area for swamp” and a darker “Extent of swamp 20,000 years ago.” That conceptual separation supports this review’s refusal to collapse drainage, vegetation mosaic, and conventional envelope into one geometry. The PDF supplies no cited source scale or downloadable vector, so its shapes were not reverse-engineered.

USGS’s Ohio GAP description calls the Great Black Swamp a large forested wetland on the Huron/Erie Lake Plain and separately identifies the Oak Openings. An Ohio GAP bulletin describes the conventional landscape as roughly 120 miles long and 30–40 miles wide. That broad rectangular dimension implies an order-of-magnitude envelope larger than this 1,804-square-mile class-4 mosaic. The disagreement is a QA finding: the conventional label/envelope likely includes non-class-4 land and/or a broader drainage concept. The candidate was not tuned to match it.

The supplied non-georeferenced map generally places the landscape in the same northwest Ohio setting but cannot establish spatial agreement. It was neither overlaid nor traced.

## Interstate Compatibility

The compatibility table is `reports/great_black_swamp_interstate_compatibility.csv`.

Indiana’s official 2016 layer is a generalized circa-1820 reconstruction from original land-survey records and modern soil maps. Its single “Wetlands” class combines wetlands, marshes, swamps, bogs, and wet prairie, so it cannot be mapped one-to-one to Ohio’s Elm-Ash class.

Michigan MNFI’s circa-1800 vegetation is interpreted from General Land Office surveys made principally in 1816–1856. It has more detailed swamp and marsh classes and county map scales that differ from Ohio’s 1:500,000 source. A documented ecological crosswalk and terms review would be needed before any interstate reconstruction. No Ohio/Indiana/Michigan polygons were merged in this task.

## Area / Geometry QA

- Candidate type: MultiPolygon.
- Selected source polygons: 117.
- Dissolved polygon components: 116; disconnected fragments: 115.
- Total and Ohio-only area: **4,672.66 km² (1,804.12 mi²; approximately 1.155 million acres)**.
- Largest component: 2,759.07 km².
- County intersections greater than 0.01 km²: 18.
- HUC8 intersections: 8.
- Geometry valid: yes; empty: no.
- Source scale: 1:500,000.
- Source CRS: EPSG:3734; review GeoJSON: EPSG:4326; area QA: EPSG:5070.

The tiny reported intersections with Indiana and Michigan counties (under 0.2 km² total) reflect cross-state boundary representation differences at generalized source/context scales, not an interstate Ohio dataset. Treat the candidate as Ohio-only.

Machine-readable QA is in `reports/great_black_swamp_geometry_qa.json`; county and watershed intersection tables are separate CSVs. The review PNG/SVG show the source mosaic, current wetlands, Maumee network, HUC8s, Lake Erie, counties, and Census places.

## Uncertainty

- **Boundary uncertainty:** high for a named Great Black Swamp boundary; the source maps vegetation associations at 1:500,000.
- **Class uncertainty:** medium; Elm-Ash swamp forest is relevant but omits wet prairie, marsh, and floodplain types and includes class-4 polygons that may not have borne the named regional label.
- **Selection uncertainty:** medium; named HUC8s provide a reproducible regional scope but are not historical swamp limits.
- **Temporal uncertainty:** the phrase “earliest land surveys” is not a single survey year, and Gordon is a 1966 interpretation.
- **Interstate uncertainty:** high until class crosswalks, source scales, and reuse terms are reconciled.
- **Geometric uncertainty:** source generalization, state-border mismatches, and many disconnected mosaic fragments are expected.

## Permitted Uses

- Regional historical reference.
- Atlas and worldbuilding context.
- Broad county/watershed overlap summaries with scale warnings.
- Comparing historical swamp-forest mosaics with modern regional systems.
- A clearly labeled review layer after explicit human approval.

## Uses Not Supported

- Parcel, field, ditch, or property classification.
- Precise restoration targeting or regulatory decisions.
- Fine-scale hydrologic modeling.
- Claims that a specific modern location was inside the named swamp.
- A conventional-envelope or drainage-area substitute.
- Automatic interstate merging.

## Terms / Licensing / Disclaimer

ODNR distributes the data “as is,” without guarantee or warranty, and places responsibility on the user to determine fitness for a particular purpose; its metadata disclaims liability for use. No update is planned. The raw metadata is preserved verbatim in the ODNR archive and as `or_veg_spn83.shp.xml` plus the official dataset PDF.

The H2Ohio PDF is an official educational publication and is used only as a cited comparison. No geometry was extracted. Indiana’s public query service and Michigan’s public viewer/PDFs establish availability, but their detailed redistribution terms should be confirmed before any future cross-state derived dataset is packaged.

## Recommendation

**C — HOLD.** Keep `great_black_swamp_candidate_gordon1966` as a review-only artifact. It is reproducible and useful for scale-appropriate discussion, but the absence of a directly documented named-swamp vector and the difference between vegetation, extent, and drainage concepts make silent canonical adoption inappropriate.

### Contact fallback draft — do not send automatically

> Subject: Request for GIS source used in H2Ohio Great Black Swamp history map
>
> Hello ODNR GIS Services / H2Ohio team,
>
> We are reviewing historical Great Black Swamp geometry for a documented regional research project. The H2Ohio publication *The History of the Great Black Swamp and Its Evolution Over Time* shows separate categories for “Drainage area for swamp” and “Extent of swamp 20,000 years ago.” Could you tell us whether the underlying GIS dataset(s) are publicly available? If so, please provide the source or item/service URL, historical source and reference period, map scale or intended precision, derivation methodology, and terms of use. We will not reverse-engineer the PDF map.
>
> Thank you.

## Human Review Decision

No decision has been recorded. Stop gate remains active:

- A — ACCEPT: approve inclusion as a historical-reference layer.
- B — ACCEPT WITH QUALIFICATION: include with derived/generalized labeling.
- C — HOLD: wait for a better ODNR/H2Ohio vector. **Current recommendation.**
- D — REJECT: candidate is insufficiently defensible.

Until a human records A or B, do not add the candidate to the canonical Phase 1 GeoPackage and do not close the QA issue.

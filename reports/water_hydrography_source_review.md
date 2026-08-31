# Water Hydrography Source Review

## Executive finding

The official USGS 3D Hydrography Program `3DHP_all` FeatureServer, Flowline layer 50, is suitable for Phase 1 follow-up QA. The review snapshot contains **102,757** flowlines in the complete Phase 1 HUC-12 union plus a documented 500 m buffer. It remains review data and does not modify the released v0.1 baseline.

## Source metadata

- Dataset/service: USGS 3DHP_all
- Agency: U.S. Geological Survey / The National Map
- Service: <https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer>
- Flowline layer 50: <https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer/50>
- Service refresh: **August 5, 2026**
- Retrieval date: **2026-08-29**
- Native service CRS: EPSG:3857; requested snapshot storage: EPSG:4326; metric analysis: EPSG:26917
- Geometry: esriGeometryPolyline; service declares Z=True and M=True
- Maximum query size: 2500 records
- Use constraints: None stated
- Terms: official metadata states no use constraints and describes the data as open/non-proprietary; USGS acknowledgment is appreciated.

## Retrieval and extent

`src/python/qa/build_physical_hydrography_review.py` unions all 252 Phase 1 HUC-12 polygons, buffers the union by 500 m in EPSG:5070 to retain cross-boundary network links, simplifies only the server query mask by 100 m, paginates the official FeatureServer in ordered 2,500-record requests, de-duplicates `OBJECTID`, and then applies the exact unsimplified 500 m mask. The raw GeoJSON snapshot is gzip-compressed locally at `data/raw/usgs/3dhp_flowlines_maumee_buffer500m.geojson.gz`. It is intentionally excluded from ordinary Git and Git LFS because it is reproducibly downloadable. Tracked service metadata and the source manifest preserve the retrieval date, method, extent, **102,757** feature count, migrated-NHD/EDH provenance, and expected SHA-256 `365A043ACCED9DC70CBEAEC804408A8539E3C372E3B4F64B962C03DB047EBD60`.

The 500 m buffer supports topology at the project boundary. It is not used to assign HUC routing by proximity. Flowline representative points assign a line to a HUC-12 for transition summarization; direction comes only from native `hydrosequence` / `dnhydrosequence` attributes.

## Feature classes and physicality

| featuretype | featuretypelabel | physicality | count |
| --- | --- | --- | --- |
| 1 | Channel Line | physical_channel | 45894 |
| 2 | Canal | canal | 6087 |
| 3 | Drainageway | drainageway | 34429 |
| 4 | Surface Connector | authoritative_network_connector | 3060 |
| 5 | Waterbody Connector | authoritative_network_connector | 9738 |
| 6 | Elevation Breaching Connector | authoritative_network_connector | 45 |
| 7 | Hydro Unenforced Connector | authoritative_network_connector | 3504 |

Connector classes remain valid elements of the official network but are not portrayed as ordinary streams.

## 3DHP versus migrated NHD provenance

| workunitid | source_generation | count |
| --- | --- | --- |
| 300290 | edh_work_unit | 232 |
| NHD | migrated_nhd | 102525 |

`workunitid=NHD` is preserved as migrated/supplemental NHD provenance. The 232 features carrying numeric work unit `300290` are classified as an EDH work unit: the [official USGS access page](https://www.usgs.gov/3d-hydrography-program/access-3dhp-data-products) specifically identifies Big Darby Creek work unit 300290 as a July 2026 EDH release with missing flow-network derivatives, and the [EDH data dictionary](https://www.usgs.gov/ngp-standards-and-specifications/elevation-derived-hydrography-data-acquisition-specifications-1) defines numeric `workunitid` as the 3DHP project tracking ID. All 232 records lack native derivative fields, consistent with the documented issue. The study extract is therefore **mixed but overwhelmingly migrated NHD**, not uniformly new lidar-derived EDH.

## Network attributes

The extract preserves `id3dhp`, `featuredate`, `mainstemid`, `featuretype`, `featuretypelabel`, `flowdirection`, `flowdirectionlabel`, `onsurface`, `streamorder`, `hydrosequence`, `dnhydrosequence`, `uphydrosequence`, `divergence`, catchment/flowpath IDs, level paths, terminal paths, and `workunitid`. Native downstream derivatives are populated for 102,387 features; unpopulated EDH and other records are retained but not assigned invented topology.

## Limitations

- A mapped line does not establish perennial flow.
- Canal and drainageway behavior varies; agricultural tile drainage is incompletely represented.
- Official connector classes are topological devices, not necessarily surface channels.
- HUC boundaries and representative-point line assignments can create local boundary ambiguity.
- The live service changes over time; the expected snapshot hash detects any later retrieval difference from the accepted review input.
- The source is unsuitable for parcel/site regulatory determinations.

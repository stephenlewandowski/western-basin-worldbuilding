# Water System v0.1 — Sources

Retrieved: 2026-08-29

| Layer / claim | Source | Status | Use and limitation |
|---|---|---|---|
| Maumee basin HUC-8/HUC-12 | [USGS WBD](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer) | Real / verified | Seven contributing HUC-8s (04100003–04100009); HUC-12 is source-context resolution, not parcel loading. |
| Lower Maumee rivers / Lake Erie | [USGS NHDPlus HR](https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer) | Real / verified | Physical flowlines currently cover Lower Maumee HUC-8 at stream order ≥3. |
| Full-basin upstream routing | [USGS WBD](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer) `tohuc` | Interpreted / inferred | Straight representative-point lines encode HUC-12 topology only; they are not physical waterways. |
| Phase 1 full-basin hydrography QA and current-development routing | [USGS 3DHP_all Flowline layer 50](https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer/50) | Real / authoritative; accepted with qualification | Physical classes and official network connectors remain separate. Of 102,757 extracted records, 102,525 are migrated NHD and 232 belong to EDH work unit 300290. Twelve unresolved project-derived relationships remain abstract (`physical_geometry=false`). Historical v0.1 artifacts are unchanged. |
| Current wetlands | [USFWS NWI](https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer) | Real / verified | Freshwater emergent and forested/shrub polygons ≥25 acres in focus window; Lake/Riverine classes excluded; inventory is not a jurisdictional determination. |
| Nutrient-source and HAB relationship | [US EPA Maumee TMDL](https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load), [Lake Erie data](https://www.epa.gov/glwqa/lake-erie-water-quality-data) | Real evidence + scientific inference | No parcel loads or fabricated quantitative intensities. |
| HAB monitoring/forecast context | [NOAA NCCOS](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/) | Real / verified | Map 04 is not a current bloom footprint. |
| Toledo intake observation node | [GLOS/IOOS ERDDAP](https://erddap.sensors.axds.co/erddap/tabledap/glos_crib.html) | Real / verified, medium location confidence | Coordinate is the named public monitoring station. Separate historic crib/light locations require reconciliation. |
| Collins Park WTP | [City of Toledo](https://toledo.oh.gov/departments/public-works/water/water-treatment), [Ohio EPA co-located monitor](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/27/ams/sites/2019/E1-2019_monitorSite_Descs.pdf) | Real / verified | Coordinate is Ohio EPA's co-located monitor; City reports 140 MGD design capacity and ~75 MGD average production. |
| Historical Great Black Swamp image | User-supplied reference | Historical / experimental | Shown only as non-georeferenced inset. No coordinates were digitized. |
| 2050 concepts | `metadata/scenario_assumptions.yml` | Fictional / scenario | All scenario nodes have null coordinates. |

# Ecology System Sources

Baseline: 2026

Phase 6A uses a bounded set of public sources and reuses accepted water and hydrography layers. It does not create a complete species inventory or retrieve a large new raster dataset.

| source_id | source | use | limitation |
| --- | --- | --- | --- |
| `usgs_nhdplus_hr` | [USGS NHDPlus HR](https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer) | Lake Erie, Maumee Bay, river, and existing 864-feature Lower Maumee flowline context. | Hydrography is physical structure, not a complete ecological-connectivity model. |
| `usgs_3dhp_all` | [USGS 3DHP](https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer) | Current-development physical hydrography for river/riparian structure. | No fish-passage engineering or animal route is inferred. |
| `usfws_nwi` | [USFWS National Wetlands Inventory](https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer) | Existing generalized contemporary wetland network and 608-feature inventory count. | Established 25-acre focus threshold; not a jurisdictional determination or habitat-quality measure. |
| `phase6a_usfws_ottawa_nwr` | [Ottawa National Wildlife Refuge](https://www.fws.gov/refuge/ottawa) | Public refuge, coastal-marsh, protected-area, and migratory-bird function. | Generalized public anchors only; no sensitive species occurrences are published. |
| `phase6a_glfc_lake_erie_committee` | [Great Lakes Fishery Commission Lake Erie Committee](https://www.glfc.org/lake-erie-committee.php) | Lake Erie fish-community and lake-to-tributary movement context. | No stock assessment, abundance estimate, precise spawning site, or passage model. |
| `noaa_hab` | [NOAA NCCOS Lake Erie HAB Forecast](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/) | HAB and aquatic ecological-condition context. | No current bloom footprint or causal effect size is asserted. |
| `epa_lake_erie` | [US EPA Lake Erie Water Quality Data](https://www.epa.gov/glwqa/lake-erie-water-quality-data) | Nutrient and water-quality condition interface. | No unsupported causal load or ecological-risk score is calculated. |
| `h2ohio_great_black_swamp_history` | [H2Ohio / Ohio DNR Great Black Swamp history](https://dam.assets.ohio.gov/image/upload/h2.ohio.gov/STA/History_of_the_Great_Black_Swamp.pdf) | Historical drainage transformation and legacy/agricultural-matrix context. | The held Great Black Swamp candidate is not used as Phase 6A geometry. |
| `phase6a_mrlc_land_cover` | [Multi-Resolution Land Characteristics Consortium](https://www.mrlc.gov/) | Contemporary forest, wetland, grassland, agriculture, and developed-class context. | No large NLCD raster is committed; classes remain generalized. |
| `census_tigerweb_context` | [U.S. Census TIGERweb](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb) | Urban/developed interface context. | No parcel-scale ecological effect is inferred. |
| `usgs_wbd` | [USGS Watershed Boundary Dataset](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer) | Contributing watershed context and the existing seven-unit indicator. | Hydrologic units are not biodiversity or habitat-quality measures. |

## Evidence posture

The model combines documented public habitat/protected-area context, existing mapped hydrography and wetlands, and explicitly generalized ecological functions. It preserves uncertainty and does not publish sensitive species locations, exact movement routes, invented abundance/richness values, or ecological-risk scores.

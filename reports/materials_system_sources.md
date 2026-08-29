# Phase 2A Geology / Minerals / Strategic Materials Sources

Retrieved: 2026-08-29  
Baseline year: 2026  
Scope: the first real-world materials baseline only; no future scenario or speculative corridor geometry.

## Sources used in Map 06 and the committed layers

| source_name | URL / identifier | retrieval_date | dataset_date | spatial_resolution | terms | confidence | notes |
|---|---|---|---|---|---|---|---|
| Ohio Department of Natural Resources, Bedrock Type | https://gis2.ohiodnr.gov/arcgis/rest/services/DNR_Services/SUBSURFACE/MapServer/5 | 2026-08-29 | 2006 compilation; source quadrangles largely 1989–1998 | 1:500,000 statewide compilation | Public Ohio DNR map service; retain source credit | High | Authoritative bedrock-unit geometry. The Phase 2A carbonate layer is a text-filtered subset of unit name, lithology, and description. It shows occurrence, not reserves. |
| USGS National Geologic Map Database, Bedrock geologic map of Ohio | https://ngmdb.usgs.gov/Prodesc/proddesc_82513.htm | 2026-08-29 | 2006 | 1:500,000 | Public federal catalog metadata | High | Corroborates the ODNR compilation title, year, scale, and authorship. |
| U.S. Census Bureau TIGERweb Transportation | https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer | 2026-08-29 | TIGERweb current service; related current vintage 2025-01-01 | Vector road centerlines | Public U.S. Census data | High | Primary and secondary roads are orientation context only. |
| U.S. Census Bureau TIGERweb Places | https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer | 2026-08-29 | TIGERweb current service | Incorporated-place polygons | Public U.S. Census data | High | Used only for town orientation and labels. |
| USGS NHDPlus High Resolution, retained Phase 1 layer | https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer | 2026-08-29 | See Phase 1 source report | Vector flowlines | Public U.S. Geological Survey data | High | Existing `water_flowlines_order3` and `water_lake_erie` layers are read as context; Phase 1 layers are not rebuilt or edited. |
| ArcGIS World Geocoder | https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer | 2026-08-29 | Live response 2026-08-29 | PointAddress for 4 sites; StreetAddress for Area Aggregates | Esri geocoding service terms apply | High/Medium | Converts official addresses to reproducible coordinates. Area Aggregates is medium confidence because the result is street-address resolution. These are geocoder results, not AI-generated coordinates. |
| Martin Marietta, Woodville Lime Facility | https://www.martinmarietta.com/locations/specialty-products/lime/lime | 2026-08-29 | Current page, 2026 | Official facility address | Public company webpage | High | Verifies the Woodville facility, products, address, and rail access. |
| Martin Marietta 2024 Sustainability Report | https://mcdn.martinmarietta.com/assets/sustainability/flip/sustainability2024-a/files/basic-html/page68.html | 2026-08-29 | 2024 | Facility-level narrative | Public company report | High | Documents six Woodville lime kilns and dolomitic-limestone feed. No production quantity is transferred to the model. |
| Ohio DNR, 2021 Report on Ohio Mineral Industries | https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/geology/industrial-minerals-downloads/IM1_2021_Wright_2022.pdf | 2026-08-29 | 2021, published 2022 | Mapped operations, statewide | Public Ohio DNR report | Medium/High | Corroborates Martin Marietta Woodville Quarry and Area Aggregates Woodville #10. It is not treated as a complete 2026 active-site inventory. |
| Ohio EPA NPDES permit 2IJ00028 | https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf | 2026-08-29 | Effective 2022-01-01 through 2026-12-31 | Official facility address | Public state permit | High | Verifies the Area Aggregates address and a permit current during the 2026 baseline year. |
| Kokosing / Olen specialty aggregate page | https://www.kokosing.biz/our-work/materials/aggregate/specialty/ | 2026-08-29 | Current page, 2026 | Facility/product narrative | Public company webpage | Medium/High | Identifies Woodville agricultural lime and filter sand. |
| Graymont contact and facility information | https://www.graymont.com/contact-us/ | 2026-08-29 | Current page, 2026 | Official facility address | Public company webpage | High | Verifies the Genoa facility address; Graymont product pages describe building/masonry lime from high-purity dolomitic limestone. |
| US EPA Materion Elmore permit documentation | https://semspub.epa.gov/work/05/967810.pdf | 2026-08-29 | Public permit record | Official facility address and process narrative | Public federal record | High | Verifies the Elmore address and beryllium/alloy processing role. |
| Materion Elmore advanced composites announcement | https://www.materion.com/de/about-materion/news/beryllium-and-composites/materion-expands-capabilities-for-proprietary-albecast-composites | 2026-08-29 | Current company archive | Facility-level narrative | Public company webpage | Medium/High | Supports Elmore's advanced-materials manufacturing role. |
| USGS Mineral Commodity Summaries 2026 — Beryllium | https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-beryllium.pdf | 2026-08-29 | 2026 | National supply-chain summary | Public-domain U.S. Geological Survey report | High | Documents extraction in Utah/imported beryl and shipment of intermediate material to Ohio. This is the basis for `local_resource=false` at Elmore. |
| U.S. Department of Defense, Industrial Base Policy / DPA Investments | https://www.businessdefense.gov/investments.html | 2026-08-29 | Current federal portfolio page | Facility/program level | Public federal webpage | High | Confirms federal Defense Production Act interest in high-purity beryllium sustainment at Elmore. |
| U.S. Army Corps of Engineers, Luckey Site | https://www.lrd.usace.army.mil/Missions/Projects/Article/3613204/luckey-site/ | 2026-08-29 | Updated 2026-07-16 | Official site address and project narrative | Public federal webpage | High | Establishes current FUSRAP cleanup, the historical magnesium/beryllium sequence, and the distinction from active production. |

## Safety, policy, and hydrogeology research constraints

| source_name | URL / identifier | retrieval_date | dataset_date | spatial_resolution | terms | confidence | notes |
|---|---|---|---|---|---|---|---|
| OSHA Beryllium | https://www.osha.gov/beryllium | 2026-08-29 | Current federal standard/resources | Workplace/process scale, non-spatial | Public federal webpage | High | Safety context only. No exposure zones or unsupported risk geometry are mapped. |
| NIOSH Pocket Guide — Beryllium compounds | https://www.cdc.gov/niosh/npg/npgd0054.html | 2026-08-29 | Current federal guidance page | Workplace/process scale, non-spatial | Public federal webpage | High | Occupational-health context only; not used to infer local exposure. |
| U.S. Department of Energy, Critical Materials and Minerals | https://www.energy.gov/cmm/what-are-critical-materials-and-critical-minerals | 2026-08-29 | Current federal program page | National policy, non-spatial | Public federal webpage | High | Policy vocabulary and supply-chain framing only. DOD/DPA documentation is the facility-specific federal authority used for Elmore. |
| USGS, Hydrogeology of the carbonate aquifer in Lucas, Sandusky, and Wood Counties | https://pubs.usgs.gov/publication/wri914024 | 2026-08-29 | Published 1991 | Regional wells/springs; historical study | Public-domain U.S. Geological Survey report | High for historical study | Useful hydrogeologic background, but too old to justify a 2026 groundwater-flow surface. |
| USGS, Potentiometric-surface map of the carbonate aquifer | https://pubs.usgs.gov/publication/wri884144 | 2026-08-29 | July 1986 measurements; published 1988 | Regional contour map | Public-domain U.S. Geological Survey report | High for 1986 conditions | Explicitly excluded from Map 06 as a present-day flow-direction claim. |
| USGS Ohio–Kentucky–Indiana Water Science Center, glacial aquifer study | https://www.usgs.gov/centers/oki-water/science/hydrogeologic-mapping-and-three-dimensional-geologic-modeling-glacial | 2026-08-29 | Active study page, current in 2025–2026 | County/regional study area | Public federal webpage | High | Study area/products do not yet support a Western Basin 2026 groundwater-flow layer for this phase. |

## Facility-coordinate results

The exact geocoder matches, scores, official addresses, and coordinate-source URL are cached in `data/raw/facilities/facility_geocodes_2026.csv`. Four facilities matched at `PointAddress` resolution with score 100. Area Aggregates matched at `StreetAddress` resolution with score 99.55 and is marked medium confidence. A future parcel/permit-boundary source should supersede address points when available.

## Licensing and reuse

The repository code and original prose are MIT licensed. Source data and documents retain their own public-agency or company terms. The map preserves source attribution and does not relicense third-party data.

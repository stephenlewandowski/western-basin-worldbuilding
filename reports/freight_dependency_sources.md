# Freight Dependency Sources

Baseline: 2026
Source reuse/check: 2026-09-02

Phase 5C reuses the accepted/frozen Phase 5A freight baseline and Phase 5B
evidence validation. No additional broad research or source inventory is needed
for this qualitative dependency layer.

| source_id | source | dependency use | limitation |
| --- | --- | --- | --- |
| `phase5a_toledo_port` | [Port of Toledo](https://www.toledoport.org/port-of-toledo) | Marine gateway, on-dock Class I rail, highway access, heavy-haul, and Ironville mode interfaces. | Port-level evidence; no volume or universal terminal assignment. |
| `phase5b_toledo_annual_report` | [Toledo-Lucas County Port Authority 2025 Annual Report](https://www.toledoport.org/2025-annual-report) | General-cargo warehouse and liquid-bulk transloading context. | No facility-specific movement quantity or route. |
| `phase5a_ntad_rail` | [USDOT/BTS NTAD Class I Rail Network](https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines_Class_I_Railroads/FeatureServer) | Public Class I corridor context. | Corridor presence is not facility dependence. |
| `phase5a_fhwa_faf` | [Freight Analysis Framework](https://faf.ornl.gov/faf5/) | Broad highway, agricultural/bulk, and external-market context. | No local volume, route, or forecast used. |
| `census_tigerweb_context` | Existing [Census TIGERweb context](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb) | Named highway corridor geometry. | No plant-specific assignment. |
| `phase5a_eia_petroleum` | [EIA Petroleum and Other Liquids](https://www.eia.gov/petroleum/) | General fuel/external-market dependency context. | No pipeline geometry, capacity, or contract route. |
| `phase5a_mm_woodville` | [Martin Marietta Woodville Lime](https://www.martinmarietta.com/locations/specialty-products/lime/lime) | Woodville processing role. | Mode and customer remain unknown. |
| `phase5a_area_woodville` | [Ohio EPA Area Aggregates permit](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf) | Woodville extraction role. | Freight access remains unresolved. |
| `phase5a_graymont_genoa` | [Graymont solutions](https://www.graymont.com/solutions/) | Genoa processing role. | Quarry/feed and freight mode remain unresolved. |
| `phase5a_materion_elmore` | [EPA Materion Elmore permit](https://semspub.epa.gov/work/05/967810.pdf) | Elmore advanced processing and external orientation. | No precise mode or route. |
| `phase5a_luckey_logistics` | [USACE Luckey remediation logistics](https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3636698/10000-truckloads-safely-moved-from-the-luckey-fusrap-site/) | Licensed off-site disposal dependency. | No route, destination facility, or quantity. |

## Evidence posture

The dependency layer combines documented flow/access, documented corridor,
interchange, generalized supply-chain, and engineering-logistics evidence from
the frozen Phase 5A/5B records. A qualitative dependency does not establish
probability, failure consequence, security weakness, or operational necessity.

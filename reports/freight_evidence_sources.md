# Freight Evidence Validation Sources

Baseline: 2026
Source check: 2026-09-02

## Scope

Phase 5B strengthens selected Phase 5A relationships using a bounded set of
public sources. It does not expand the transportation atlas or add shipment
volumes, routes, schedules, or hazardous-material logistics.

## Sources

| source_id | source | evidence use | limit |
| --- | --- | --- | --- |
| `phase5a_toledo_port` | [Port of Toledo](https://www.toledoport.org/port-of-toledo) | Port access, on-dock Class I rail, I-75/I-80/90 access, listed carriers, Michigan/Canada heavy-haul context, and Ironville vessel/truck/rail relationship. | Port-level evidence; no universal terminal/customer assignment. |
| `phase5b_toledo_annual_report` | [Toledo-Lucas County Port Authority 2025 Annual Report](https://www.toledoport.org/2025-annual-report) | 13 terminal operators, Facility #1 general-cargo warehouse, terminal modernization, and adjacent liquid-bulk transloading. | No facility-level shipment quantity, route, or customer inferred. |
| `phase5a_toledo_port_map` | [Toledo Harbor Map](https://www.toledoport.org/s/toledo-port-facilities-2020.pdf) | Harbor and port-facility orientation. | Contextual map only; no dock-by-dock relationship created. |
| `phase5a_ntad_rail` | [USDOT/BTS NTAD Class I Rail Network Lines](https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines_Class_I_Railroads/FeatureServer) | Public Class I corridor and carrier context for NS, CSX, and CN. | Corridor presence does not prove facility use or interchange. |
| `phase5a_norfolk_southern` | [Norfolk Southern Ship by Rail](https://www.norfolksouthern.com/en/ship-by-rail) | General carrier freight context. | No customer-specific movement inferred. |
| `phase5a_fhwa_faf` | [Freight Analysis Framework](https://faf.ornl.gov/faf5/) | Broad commodity and freight-corridor context. | No local volume, forecast, or facility assignment used. |
| `census_tigerweb_context` | Existing [Census TIGERweb context](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb) | Primary-road geometry used for named highway corridors. | Road geometry is not freight assignment evidence. |
| `phase5a_luckey_logistics` | [USACE Luckey off-site disposal logistics](https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3636698/10000-truckloads-safely-moved-from-the-luckey-fusrap-site/) | Licensed off-site remediation-disposal relationship. | Route and destination facility remain generalized. |
| `phase5a_mm_woodville` | [Martin Marietta Woodville Lime Facility](https://www.martinmarietta.com/locations/specialty-products/lime/lime) | Existing facility/product identity. | No freight access or customer route documented. |
| `phase5a_area_woodville` | [Ohio EPA Area Aggregates permit](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf) | Existing permitted extraction identity. | No freight access, mode, customer, or volume documented. |
| `phase5a_graymont_genoa` | [Graymont solutions](https://www.graymont.com/solutions/) | Existing Genoa processing identity. | Quarry/feed and specific freight access unresolved. |
| `phase5a_materion_elmore` | [EPA Materion Elmore permit](https://semspub.epa.gov/work/05/967810.pdf) | Existing advanced-processing identity. | Nonlocal feed is retained; mode and route are not documented. |
| `phase5a_eia_petroleum` | [EIA Petroleum and Other Liquids](https://www.eia.gov/petroleum/) | General external fuel-interface context. | No pipeline alignment, capacity, or contract route used. |

## Evidence hierarchy

`documented_shipment_relationship` is reserved for a public source that names a
movement or movement function, such as the Port authority's Ironville vessel,
truck, and rail description or USACE licensed off-site disposal logistics.
`documented_interchange` is reserved for named or explicitly described modal
access/interchange. `documented_corridor` identifies public infrastructure
context only. `proximity_only`, `generalized_logistics_dependency`, and
`unresolved` preserve gaps rather than upgrading them by inference.

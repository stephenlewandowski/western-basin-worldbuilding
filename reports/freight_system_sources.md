# Phase 5A Freight System Sources

Baseline: 2026
Source check: 2026-09-02

## Scope

Phase 5A uses a bounded set of public port, transportation, freight, energy,
and existing materials sources. It models major corridors and documented or
generalized commodity functions, not a complete transportation network or
shipment-volume system. Source identifiers resolve through
[metadata/sources.yml](../metadata/sources.yml) and existing materials source
registries where noted.

## Sources used

| source_id | source | use | limitation |
| --- | --- | --- | --- |
| `phase5a_toledo_port` | [Port of Toledo](https://www.toledoport.org/port-of-toledo) | 13-terminal port context, Seaway connection, storage/cargo capabilities, on-dock Class I rail, I-75/I-80/90 access, Michigan/Canada heavy-haul context, and Ironville HBI flow. | No complete dock/customer inventory, shipment schedule, or facility-specific route inferred. |
| `phase5a_toledo_port_map` | [Toledo Harbor Map](https://www.toledoport.org/s/toledo-port-facilities-2020.pdf) | Harbor and facility orientation. | Used as contextual map evidence; no dock geometry or customer relationship is modeled. |
| `phase5a_port_geocode` | [ArcGIS World Geocoder](https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer) | Address-level Port of Toledo anchor at 1 Maritime Plaza. | Approximate port anchor, not terminal geometry or a berth location. |
| `phase5a_great_lakes_seaway` | [Great Lakes St. Lawrence Seaway System](https://greatlakes-seaway.com/en/the-seaway/) | Marine connection from the Great Lakes to the St. Lawrence system. | No vessel schedule, draft calculation, or port-to-customer route modeled. |
| `phase5a_ntad_rail` | [USDOT/BTS NTAD Class I Rail Network Lines](https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines_Class_I_Railroads/FeatureServer) | Public Class I freight corridor geometry and carrier fields in the Western Basin extent. | No sidings, dispatch, schedules, hazardous routing, or security detail modeled. |
| `phase5a_norfolk_southern` | [Norfolk Southern Ship by Rail](https://www.norfolksouthern.com/en/ship-by-rail) | General Class I freight-service context. | No customer-specific movement inferred. |
| `phase5a_fhwa_faf` | [Freight Analysis Framework](https://faf.ornl.gov/faf5/) | Broad freight-corridor and commodity context, including agricultural/bulk categories. | No local shipment volume, forecast, or plant-specific route used. |
| `census_tigerweb_context` | Existing [Census TIGERweb context](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb) | Existing primary-road geometry for I-75, I-80, I-90, I-280, and US-23. | Geometry is road context; no freight assignment or truck count inferred. |
| `phase5a_eia_petroleum` | [EIA Petroleum and Other Liquids](https://www.eia.gov/petroleum/) | General fuel/petroleum logistics context. | No pipeline alignment, station, valve, pressure, capacity, or contract route modeled. |
| `phase5a_mm_woodville` | [Martin Marietta Woodville Lime Facility](https://www.martinmarietta.com/locations/specialty-products/lime/lime) | Existing Woodville processing node and broad product function. | No customer, mode, route, schedule, or quantity inferred. |
| `phase5a_area_woodville` | [Ohio EPA Area Aggregates permit](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf) | Existing Woodville extraction node and 2026 permit context. | No facility-specific freight route or quantity inferred. |
| `phase5a_graymont_genoa` | [Graymont solutions/facility material](https://www.graymont.com/solutions/) | Existing Genoa lime-processing node and product function. | Specific quarry/feed relationship and freight route remain unresolved. |
| `phase5a_materion_elmore` | [EPA Materion Elmore permit record](https://semspub.epa.gov/work/05/967810.pdf) | Existing Elmore advanced-processing node. | Nonlocal feed is retained; transport mode, route, schedule, and quantity are absent. |
| `phase5a_luckey_usace` | [USACE Luckey Site](https://www.lrd.usace.army.mil/Missions/Projects/Article/3613204/luckey-site/) | Existing Luckey legacy/remediation node. | Not current production; no site-specific freight route inferred. |
| `phase5a_luckey_logistics` | [USACE Luckey off-site disposal logistics](https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3636698/10000-truckloads-safely-moved-from-the-luckey-fusrap-site/) | Program-level licensed off-site remediation logistics. | No hazardous-material route, destination facility, schedule, or quantity modeled. |

## Port evidence

The Port of Toledo page states that the port has 13 terminals linked to global
markets through the Great Lakes/St. Lawrence Seaway System. It documents indoor
and outdoor storage, on-dock Class I rail access, a 4,100-foot dock, full Seaway
draft, and proximity to I-75 and I-80/90. It also documents the Ironville direct-
reduction plant receiving product by vessel and finished HBI product leaving by
truck and rail.

The model retains these as port, interchange, corridor, and documented-flow
relationships. It does not turn the public description into a complete terminal
or customer map.

## Rail and highway evidence

The USDOT/BTS NTAD Class I rail service was queried for the project bounding box.
The cached 1,221-feature extract is stored at
`data/raw/transportation/ntad_class1_rail_network_western_basin.geojson`.
Map 17 displays filtered NS, CSX, and CN main corridor context. Wheeling & Lake
Erie is retained as a publicly listed Port of Toledo rail interface without
invented line geometry.

Existing Census TIGER primary-road geometry supplies I-75, I-80, I-90, I-280,
and US-23 context. FHWA/FAF supplies the broad freight-use and commodity
context; it does not assign a specific plant to a specific road.

## Materials and fuel evidence

Existing sourced materials nodes are reused for Woodville, Genoa, Elmore, and
Luckey. Their freight relationships are generalized unless the cited source
documents a particular function. The external fuel interface is deliberately
abstract and does not represent a pipeline alignment or capacity.

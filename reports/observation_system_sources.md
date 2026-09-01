# Phase 4A Observation System Sources

Baseline: 2026
Retrieved/checked: 2026-09-01

## Scope

Phase 4A uses a limited set of public institutional sources to establish four
representative observation-to-decision chains. It is not an inventory of every
sensor, station, data feed, operator, or regulated facility in the Western
Basin. Source identifiers used by the node and edge tables are registered in
[metadata/sources.yml](../metadata/sources.yml).

No raw source snapshot is added by this phase. The model records source URLs,
public dataset/product identities, retrieval date, confidence, and explicit use
limits.

## Sources used

| source_id | source | use in Phase 4A | principal limitation |
| --- | --- | --- | --- |
| `phase4a_glerl_hab` | [NOAA GLERL HABs and Hypoxia](https://www.glerl.noaa.gov/res/HABs_and_Hypoxia/) | Integrated Lake Erie HAB observation context; GLERL describes satellite imagery, remote sensing, buoys, monitoring, and data informing forecast models and drinking-water managers. | Program-level evidence; no exhaustive sensor inventory or internal data path reconstructed. |
| `phase4a_nccos_hab_forecast` | [NOAA NCCOS Lake Erie HAB Forecast](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/) | Public HAB forecast using satellite imagery, forecasting/mixing models, and field samples. | No Toledo-specific automated feed, action threshold, or treatment setpoint inferred. |
| `phase4a_glos_crib` | [GLOS/IOOS Toledo Water Intake Crib ERDDAP](https://erddap.sensors.axds.co/erddap/tabledap/glos_crib.html) | Public time-series station identity, coordinate, and water-quality variables. | The public station coordinate is not treated as the sole physical Toledo intake coordinate; the existing discrepancy remains unresolved. |
| `phase4a_toledo_water_quality` | [City of Toledo Water Quality](https://toledo.oh.gov/residents/water/quality) | City-described 24-hour monitoring, certified testing, HAB protection, and public reporting. | Direct use of a particular external forecast by Toledo is not established. |
| `phase4a_usgs_nwis` | [USGS Water Data / National Water Information System](https://waterdata.usgs.gov/) | Public station metadata and real-time water observations. | No basin-wide sensor inventory, threshold, or derived hydrologic statistic created. |
| `phase4a_usgs_waterville` | [USGS 04193500 Maumee River at Waterville](https://waterdata.usgs.gov/monitoring-location/04193500/) | Representative streamgage identity and coordinate: 41.5000526, -83.7127145. | One representative station; not a complete hydrology network. |
| `phase4a_noaa_nwps` | [NOAA National Water Prediction Service](https://water.noaa.gov/) | Public water-prediction, flood-information, and forecast-service interface. | Station-specific ingestion and internal model architecture are not asserted. |
| `phase4a_nws_flood` | [NWS Flood Safety Tips and Resources](https://www.weather.gov/safety/flood) | Public flood-warning and safety-communication interface. | No county-specific emergency-management protocol or local action is modeled. |
| `phase4a_epa_echo` | [EPA ECHO Data Downloads](https://echo.epa.gov/tools/data-downloads) | Public facility, compliance, enforcement, and NPDES-related data product. | ECHO is not treated as a raw sensor feed; no named-facility finding is made. |
| `phase4a_epa_npdes` | [U.S. EPA NPDES](https://www.epa.gov/npdes) | Point-source discharge regulation and state-authorized program context. | No facility-specific permit, measurement, or enforcement decision is inferred. |
| `phase4a_eia_electricity` | [EIA Electricity Data](https://www.eia.gov/electricity/data.php) | Public generation, capacity, transmission, and electricity statistics. | Statistical context only; not real-time dispatch or control telemetry. |
| `phase4a_pjm_dataminer` | [PJM Data Miner 2](https://dataminer2.pjm.com/) | Public operator data interface. | No SCADA, private telemetry, control-center detail, or cyber architecture modeled. |
| `phase4a_pjm_operations` | [PJM Markets and Operations](https://www.pjm.com/markets-and-operations) | High-level regional transmission-organization operations context. | No dispatch instruction, outage result, congestion result, or automated control is claimed. |

## Chain evidence

### A — Lake Erie / HAB / drinking water

NOAA GLERL documents an integrated observation program whose collected data
inform forecast models and drinking-water managers. NOAA NCCOS documents the
Lake Erie HAB forecast inputs and products. GLOS exposes the public Toledo crib
time series. The City of Toledo documents continuous monitoring, certified
water-quality tests, and treatment protection from harmful algal blooms.
Together these sources support a qualified observation → forecast → drinking-
water decision/operation chain. They do not establish a Toledo-specific
machine-to-machine feed or resolve the physical intake-coordinate discrepancy.

### B — Maumee / weather / flood

USGS NWIS and station 04193500 support a representative river-observation node.
NOAA NWPS supplies the public water-prediction/forecast interface, and NWS
provides public flood-warning and safety information. The table records the
supported public chain without claiming a station-specific internal forecast
ingestion path or a county emergency-management action.

### C — environmental / regulatory

EPA NPDES establishes the regulatory and monitoring/reporting framework. EPA
ECHO provides public facility and compliance data products. These support a
program-level monitoring → data → regulatory oversight → compliance/permitting
response chain. No facility-specific observation, permit limit, violation, or
enforcement outcome is asserted.

### D — energy information

EIA provides public statistical context for generation and grid information.
PJM Data Miner and PJM's public markets/operations material support a separate
high-level operator-information → PJM → operations/planning coordination chain.
The model does not reconstruct telemetry, SCADA, dispatch, power flow, or
sensitive infrastructure.

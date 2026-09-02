# Phase 4B Information Dependency Sources

Baseline: 2026
Source check: 2026-09-02

## Scope

Phase 4B reuses the public sources and Phase 4A observation-system node IDs to
model information dependencies, governance boundaries, and evidence-qualified
blind spots. It does not expand the source inventory merely for completeness.
All source identifiers resolve through [metadata/sources.yml](../metadata/sources.yml)
and the Phase 4A source report, [observation_system_sources.md](observation_system_sources.md).

The model uses public program and product descriptions. No restricted data,
private telemetry, SCADA material, credentials, attack information, or
classified material was requested or inferred.

## Source roles reused from Phase 4A

| source_id | public source | Phase 4B role | limitation |
| --- | --- | --- | --- |
| `phase4a_glerl_hab` | [NOAA GLERL HABs and Hypoxia](https://www.glerl.noaa.gov/res/HABs_and_Hypoxia/) | HAB observation/forecast relationship and drinking-water stakeholder context. | Program-level evidence; internal data path and update schedule are not reconstructed. |
| `phase4a_nccos_hab_forecast` | [NOAA NCCOS Lake Erie HAB Forecast](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/) | HAB forecast dependency and model-uncertainty boundary. | No local Toledo threshold or direct operational feed established. |
| `phase4a_glos_crib` | [GLOS/IOOS Toledo Water Intake Crib ERDDAP](https://erddap.sensors.axds.co/erddap/tabledap/glos_crib.html) | Public station/data-product dependency and intake-coordinate blind spot. | Station coordinate does not resolve the physical Toledo intake discrepancy. |
| `phase4a_toledo_water_quality` | [City of Toledo Water Quality](https://toledo.oh.gov/residents/water/quality) | City monitoring, treatment, and municipal decision authority. | Public page does not expose all decision thresholds or external-feed pathways. |
| `phase4a_usgs_nwis` | [USGS Water Data](https://waterdata.usgs.gov/) | Streamgage data-product dependency. | No complete basin inventory or basin-wide aggregation method modeled. |
| `phase4a_usgs_waterville` | [USGS 04193500 Maumee River at Waterville](https://waterdata.usgs.gov/monitoring-location/04193500/) | Representative point-observation dependency. | One gauge cannot represent the full basin or all rainfall/tributary conditions. |
| `phase4a_noaa_nwps` | [NOAA National Water Prediction Service](https://water.noaa.gov/) | Forecast and warning-service dependency. | Station-specific ingestion and internal model details are not asserted. |
| `phase4a_nws_flood` | [NWS Flood Safety Tips and Resources](https://www.weather.gov/safety/flood) | Public warning and response interface. | Local responder protocols and event-specific timings are not modeled. |
| `phase4a_epa_echo` | [EPA ECHO Data Downloads](https://echo.epa.gov/tools/data-downloads) | Public environmental/compliance data-product dependency. | Not treated as a raw continuous sensor feed. |
| `phase4a_epa_npdes` | [U.S. EPA NPDES](https://www.epa.gov/npdes) | Regulatory authority, reporting, and jurisdiction boundary. | No facility-specific permit or decision is inferred. |
| `phase4a_eia_electricity` | [EIA Electricity Data](https://www.eia.gov/electricity/data.php) | Public generation/capacity context. | Statistical information, not real-time operations telemetry. |
| `phase4a_pjm_dataminer` | [PJM Data Miner 2](https://dataminer2.pjm.com/) | Public operator-information dependency. | Public interface does not expose private operational detail. |
| `phase4a_pjm_operations` | [PJM Markets and Operations](https://www.pjm.com/markets-and-operations) | High-level operator authority and coordination context. | Internal workflows and sensitive infrastructure are outside scope. |

## Evidence posture

The tables distinguish documented relationships from qualified public-service
links. A qualified link means that public sources support the general interface
or role but do not establish a site-specific feed, update interval, threshold,
or internal handoff. A blind spot records that limitation; it does not label the
system vulnerable or failed.

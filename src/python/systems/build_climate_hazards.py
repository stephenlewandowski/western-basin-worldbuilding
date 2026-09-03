"""Build Phase 9A: a compact factual climate and natural-hazards baseline."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/climate_hazards"
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

NODE_PATH = NETWORKS / "climate_hazard_nodes.csv"
EDGE_PATH = NETWORKS / "climate_hazard_edges.csv"
OBS_PATH = ANALYSIS / "climate_hazard_observations.csv"
SOURCE_PATH = ANALYSIS / "climate_hazard_sources.csv"
MAP_BASE = MAPS / "29_climate_natural_hazards_2026"
MANIFEST = REPORTS / "climate_hazard_baseline_manifest.json"
CHECK = REPORTS / "phase9a_artifact_check.json"

SOURCE_COLUMNS = [
    "source_id", "title", "url", "product_or_endpoint", "source_type",
    "observation_or_model", "spatial_scope", "temporal_scope", "retrieval_date",
    "use_limitations",
]
SOURCE_ROWS = [
    ["b9_acis", "Applied Climate Information System station data", "https://data.rcc-acis.org/StnData", "StnData JSON for KTDZ / Toledo Executive Airport", "regional_climate_service", "observation", "station", "2025 calendar year and 2026 YTD", "2026-09-03", "Daily values are station observations; missing and trace precipitation are retained as limitations."],
    ["b9_ncei_cag", "NOAA NCEI Climate at a Glance", "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/OH-095-tavg/12/12/2025-2026.json", "County temperature time series", "federal_dataset", "observation_adjusted_climate_series", "Lucas County", "2025 latest complete value returned", "2026-09-03", "Climate variability context; recent values may be preliminary and are not a station extreme."],
    ["b9_nws_points", "National Weather Service API point metadata", "https://api.weather.gov/points/41.65,-83.54", "Toledo-area point forecast / warning service linkage", "federal_api", "forecast_and_warning_service", "point / NWS service areas", "current service metadata", "2026-09-03", "Service endpoint identifies forecast and warning systems; it is not an observed hazard surface."],
    ["b9_nws_climate", "NWS Weather Research and Forecasting Climate portal", "https://www.weather.gov/wrh/Climate?wfo=cle", "NOWData and local climate products", "federal_web", "observation_and_climate_context", "NWS WFO / station", "current portal", "2026-09-03", "Portal documents station and product context; interactive output is not embedded as a new regional climatology."],
    ["b9_usgs_dv", "USGS National Water Information System daily values", "https://waterservices.usgs.gov/nwis/dv/?format=json&sites=04193500&startDT=2025-01-01&endDT=2026-09-03&parameterCd=00060&siteStatus=all", "Daily mean discharge, Maumee River at Waterville OH", "federal_api", "observation", "station / river reach", "2025-01-01 through latest returned 2026 value", "2026-09-03", "One gauge is not the whole watershed; daily flow is not a floodplain footprint or future trend."],
    ["b9_fema_nfhl", "FEMA National Flood Hazard Layer", "https://www.fema.gov/flood-maps/national-flood-hazard-layer", "Regulatory flood-hazard mapping context", "federal_web", "modeled_regulatory_context", "floodplain / mapped community", "current product context", "2026-09-03", "Regulatory zones are modeled mapping products and are distinct from observed or forecast floods."],
    ["b9_noaa_atlas14", "NOAA/NWS Precipitation Frequency Data Server", "https://hdsc.nws.noaa.gov/pfds/", "Atlas 14 precipitation-frequency context", "federal_web", "modeled_frequency_product", "site / precipitation-frequency grid", "historical climatology product", "2026-09-03", "Frequency estimates are not substituted for an observed event and are not a future climate projection."],
    ["b9_usdm_area", "U.S. Drought Monitor county area statistics", "https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=39095&startdate=01/01/2025&enddate=09/03/2026&statisticsType=1", "Percent of Lucas County area by weekly drought category", "federal_partner_api", "expert_assessed_drought_status", "county", "weekly 2025-01-01 through latest returned 2026 week", "2026-09-03", "Weekly expert assessment integrates multiple indicators; not a soil-moisture measurement at every location."],
    ["b9_usdm_dsci", "U.S. Drought Monitor DSCI service", "https://usdmdataservices.unl.edu/api/CountyStatistics/GetDSCI?aoi=39095&startdate=01/01/2025&enddate=09/03/2026&statisticsType=1", "Lucas County Drought Severity and Coverage Index", "federal_partner_api", "expert_assessed_drought_index", "county", "weekly 2025-01-01 through latest returned 2026 week", "2026-09-03", "DSCI is a drought-status index and is not a physical flow or groundwater-depletion estimate."],
    ["b9_drought_gov", "Drought.gov U.S. Drought Monitor description", "https://www.drought.gov/data-maps-tools/us-drought-monitor", "Product definitions and category meaning", "federal_web", "methodology_context", "national / county and other areas", "2000-present product context", "2026-09-03", "Supports category interpretation and limitations, not a new local measurement."],
    ["b9_coops_daily", "NOAA CO-OPS Toledo daily mean water levels", "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=daily_mean&begin_date=20250101&end_date=20251231&datum=IGLD&station=9063085&time_zone=gmt&units=metric&format=json", "Daily mean water level at station 9063085", "federal_api", "observation", "station / Toledo, western Lake Erie", "2025 calendar year", "2026-09-03", "Daily means describe lake level at one gauge; wind setup/seiche is not represented by the daily mean alone."],
    ["b9_coops_station", "NOAA CO-OPS station metadata", "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085.json", "Toledo station metadata", "federal_api", "station_metadata", "station", "station record", "2026-09-03", "Provides station identity and Great Lakes designation; not an event series."],
    ["b9_coops_datums", "NOAA CO-OPS station datum metadata", "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085/datums.json", "Great Lakes Lower Water Datum and extrema metadata", "federal_api", "datum_metadata", "station", "station datum record", "2026-09-03", "Datum and historical extrema context must not be mixed with flood thresholds without their stated units and references."],
    ["b9_coops_flood", "NOAA CO-OPS/NWS station flood levels", "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085/floodlevels.json", "Toledo action and NWS minor/moderate/major thresholds", "federal_api", "warning_threshold", "station / local flood stage", "current metadata", "2026-09-03", "Thresholds are warning-stage references, not observed water levels or damage estimates."],
    ["b9_glerl_levels", "NOAA Great Lakes Environmental Research Laboratory water levels", "https://www.glerl.noaa.gov/data/wlevels/", "Great Lakes monitoring, observations, forecasts, and ice resources", "federal_science", "monitoring_and_context", "Great Lakes / station network", "1860-present context", "2026-09-03", "Provides network and process context; it does not make a local hazard probability claim."],
    ["b9_storm_events_2025", "NOAA NCEI Storm Events details archive", "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz", "2025 Storm Events details snapshot", "federal_dataset", "historical_event_records", "county and event record", "2025 calendar year; snapshot 2026-08-19", "2026-09-03", "Counts are selected county event records, not rates, probabilities, attribution, or hazard zones."],
    ["b9_storm_directory", "NOAA NCEI Storm Events archive directory", "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/", "Archive inventory and version context", "federal_archive", "historical_event_records", "national event archive", "current archive", "2026-09-03", "Used to identify the dated 2025 details snapshot; the full bulk archive is not committed."],
    ["b9_storm_events", "NOAA NCEI Storm Events Database", "https://www.ncei.noaa.gov/stormevents/", "Storm Events documentation and access", "federal_web", "historical_event_records", "national / county and event record", "1950-present context", "2026-09-03", "Historical event reports do not define deterministic future risk zones."],
    ["b9_nws_winter", "NWS winter safety and hazard information", "https://www.weather.gov/safety/winter", "Winter storm, snow, ice, and cold hazard context", "federal_web", "hazard_context", "regional / forecast area", "current guidance", "2026-09-03", "General hazard definitions and preparedness context; not a local climatology."],
    ["b9_nws_thunderstorm", "NWS thunderstorm safety and hazard information", "https://www.weather.gov/safety/thunderstorm", "Thunderstorm, damaging wind, hail, and lightning context", "federal_web", "hazard_context", "regional / forecast area", "current guidance", "2026-09-03", "Supports physical hazard definitions; no local event rate is inferred from guidance."],
    ["b9_spc", "NOAA Storm Prediction Center climatology and online resources", "https://www.spc.noaa.gov/climo/online/", "Severe convective weather climatology context", "federal_science", "historical_event_context", "regional / national", "historical climatology", "2026-09-03", "Regional context does not turn historical event points into deterministic future risk zones."],
]

NODE_COLUMNS = ["node_id", "name", "hazard_family", "node_type", "reality_status", "canon_status", "scale", "latitude", "longitude", "spatial_role", "source_id", "confidence", "notes"]
NODE_ROWS = [
    ["HZ-001", "Toledo Executive Airport climate observation station", "extreme_heat;heavy_precipitation;winter", "climate_observation", "real", "verified", "station", 41.56327, -83.47671, "source-backed station", "b9_acis", "high", "Representative station record; not basin-wide and precipitation contains missing/trace values."],
    ["HZ-002", "Lucas County climate variability context", "extreme_heat;heavy_precipitation;drought", "climate_observation", "real", "verified", "county", "", "", "county context", "b9_ncei_cag", "moderate", "County climate-series context; adjusted climate analysis is not identical to a station extreme."],
    ["HZ-003", "Toledo-area NWS forecast and warning service area", "all", "warning_system", "real", "verified", "NWS point / service area", "", "", "public warning interface", "b9_nws_points", "high", "Forecast and warning service linkage; no current alert or hazard probability is asserted."],
    ["HZ-004", "Maumee watershed precipitation and runoff interface", "heavy_precipitation_flooding", "hazard_region", "real", "inferred", "HUC8 / HUC12 interface", "", "", "hydrologic context", "b9_noaa_atlas14", "moderate", "Regional physical interface; no precipitation-frequency surface is generated here."],
    ["HZ-005", "Maumee River at Waterville USGS gauge", "heavy_precipitation_flooding;drought_low_water", "river_flood_interface", "real", "verified", "station / river reach", 41.5000526, -83.7127145, "source-backed gauge", "b9_usgs_dv", "high", "Daily mean discharge observation; gauge is not the whole watershed or floodplain."],
    ["HZ-006", "Lower Maumee and tributary flood interface", "heavy_precipitation_flooding", "river_flood_interface", "real", "inferred", "river / floodplain interface", "", "", "regional interface", "b9_usgs_dv", "moderate", "Represents runoff, river-stage, tributary, and floodplain interaction without a new flood footprint."],
    ["HZ-007", "Regulatory flood-hazard mapping context", "heavy_precipitation_flooding", "floodplain_context", "real", "verified", "modeled regulatory flood zone", "", "", "mapped regulatory context", "b9_fema_nfhl", "moderate", "FEMA regulatory mapping is distinct from observed flooding, forecast flooding, and future scenario change."],
    ["HZ-008", "Urban and developed stormwater burden context", "heavy_precipitation_flooding;winter", "urban_context", "real", "inferred", "urban area / subwatershed", "", "", "developed-land context", "b9_noaa_atlas14", "limited", "Generalized urban drainage burden; no parcel, outfall, or imperviousness load model."],
    ["HZ-009", "Lucas County drought-status context", "drought_low_water", "drought_context", "real", "verified", "county", "", "", "county status context", "b9_usdm_area", "high", "Weekly U.S. Drought Monitor category context; not groundwater depletion or a soil-moisture field."],
    ["HZ-010", "Maumee low-flow observation context", "drought_low_water", "low_flow_observation", "real", "verified", "station / river reach", 41.5000526, -83.7127145, "source-backed gauge", "b9_usgs_dv", "high", "Low daily mean flow at one gauge; not a watershed-wide low-flow statistic."],
    ["HZ-011", "NOAA Toledo Great Lakes water-level station", "lake_coastal", "climate_observation", "real", "verified", "station / shoreline", 41.6936, -83.4723, "source-backed station", "b9_coops_station", "high", "Station 9063085; daily means do not capture all short-lived wind setup or seiche variability."],
    ["HZ-012", "Western Lake Erie water-level variability context", "lake_coastal", "hazard_region", "real", "verified", "western Lake Erie / shoreline", "", "", "regional lake context", "b9_glerl_levels", "high", "Lake-level variability context; not an ocean storm-surge layer."],
    ["HZ-013", "Western Lake Erie shoreline and coastal-flood interface", "lake_coastal", "coastal_interface", "real", "inferred", "shoreline / nearshore", "", "", "generalized shoreline interface", "b9_glerl_levels", "moderate", "High/low lake levels, waves, wind setup, and erosion are represented as interfaces, not shoreline predictions."],
    ["HZ-014", "Lake Erie wind setup and seiche interface", "lake_coastal;severe_convective", "lake_hazard", "real", "inferred", "western Lake Erie / bay", "", "", "lake-process context", "b9_glerl_levels", "moderate", "Great Lakes wind setup/seiche process; not equated with ocean storm surge."],
    ["HZ-015", "Lake wave, storm, and ice-condition context", "lake_coastal;winter", "lake_hazard", "real", "verified", "western Lake Erie / shoreline", "", "", "regional lake context", "b9_glerl_levels", "moderate", "Wave, storm, and ice conditions are contextual; no wave-height or ice-risk surface is asserted."],
    ["HZ-016", "Regional severe convective hazard context", "severe_convective", "convective_hazard", "real", "verified", "regional / county event context", "", "", "regional aggregation", "b9_storm_events", "moderate", "Thunderstorm wind, tornado, hail, and flood-related records are aggregated at selected county scale."],
    ["HZ-017", "Selected western-basin county Storm Events records", "severe_convective;heavy_precipitation_flooding;winter", "climate_observation", "real", "verified", "county / event record", "", "", "historical event context", "b9_storm_events_2025", "high", "2025 selected county event records; event counts are not rates, probabilities, or hazard surfaces."],
    ["HZ-018", "Regional winter hazard context", "winter", "winter_hazard", "real", "verified", "regional / forecast area", "", "", "regional hazard context", "b9_nws_winter", "moderate", "Extreme cold, snow, ice, and freeze-thaw context; lake-effect snow is not overgeneralized."],
    ["HZ-019", "NWS public warning system", "all", "warning_system", "real", "verified", "forecast area / county", "", "", "public warning interface", "b9_nws_points", "high", "Public warnings and forecasts are control interfaces; warning availability is not hazard absence."],
    ["HZ-020", "USGS streamflow monitoring network", "heavy_precipitation_flooding;drought_low_water", "monitoring_system", "real", "verified", "station / river network", "", "", "monitoring network context", "b9_usgs_dv", "high", "One representative gauge is used; this is not an exhaustive gauge inventory."],
    ["HZ-021", "NOAA CO-OPS Great Lakes water-level monitoring", "lake_coastal", "monitoring_system", "real", "verified", "station / Great Lakes network", "", "", "monitoring network context", "b9_glerl_levels", "high", "CO-OPS and binational monitoring provide water-level observations; network coverage is not a hazard score."],
    ["HZ-022", "U.S. Drought Monitor and drought-information system", "drought_low_water", "monitoring_system", "real", "verified", "county / regional status", "", "", "monitoring and assessment", "b9_drought_gov", "high", "Drought categories combine indicators and expert assessment; no groundwater depletion claim."],
    ["HZ-023", "NOAA/NWS precipitation-frequency information", "heavy_precipitation_flooding", "monitoring_system", "real", "verified", "site / regional frequency product", "", "", "reference product", "b9_noaa_atlas14", "moderate", "Frequency product is kept as reference context rather than converted into a new local event statistic."],
    ["HZ-024", "NOAA/NCEI and regional climate data services", "extreme_heat;heavy_precipitation;winter", "monitoring_system", "real", "verified", "station / county / regional", "", "", "climate data context", "b9_ncei_cag", "high", "Climate series and station products have different adjustments and scales; they are not mixed silently."],
    ["HZ-025", "NOAA GLERL Great Lakes water-level and ice resources", "lake_coastal;winter", "monitoring_system", "real", "verified", "Great Lakes / station network", "", "", "lake monitoring context", "b9_glerl_levels", "high", "Monitoring, observation, forecast, and ice resources are distinct products."],
    ["HZ-026", "Developed infrastructure and access context", "all", "infrastructure_context", "real", "inferred", "urban / regional function", "", "", "generalized receptor context", "b9_nws_points", "limited", "Generalized infrastructure context for physical disruption pathways; no asset vulnerability score or sensitive detail."],
]

EDGE_COLUMNS = ["edge_id", "from_id", "to_id", "relationship_type", "relationship_basis", "scale", "source_id", "confidence", "notes"]
EDGE_ROWS = [
    ["HZE-001", "HZ-001", "HZ-024", "observed_by", "documented station data service", "station", "b9_acis", "high", "Daily station observations are retained at station scale."],
    ["HZE-002", "HZ-002", "HZ-024", "observed_by", "documented climate data service", "county", "b9_ncei_cag", "moderate", "County climate context is not substituted for a station record."],
    ["HZE-003", "HZ-001", "HZ-003", "warning_for", "public warning-service interface", "station / forecast area", "b9_nws_points", "moderate", "Heat and cold conditions can be addressed through warnings; no event claim is added."],
    ["HZE-004", "HZ-004", "HZ-006", "hydrologically_amplified_by", "physical runoff and drainage logic", "HUC8 / river / floodplain", "b9_usgs_dv", "moderate", "Runoff and tributary connectivity can amplify flood conditions; no universal threshold is inferred."],
    ["HZE-005", "HZ-004", "HZ-005", "observed_by", "representative gauge observation", "HUC8 / station", "b9_usgs_dv", "moderate", "Gauge observation samples one reach within a larger watershed."],
    ["HZE-006", "HZ-006", "HZ-007", "affects", "floodplain interface and regulatory mapping context", "river / floodplain", "b9_fema_nfhl", "moderate", "Mapped regulatory flood context is not an observed flood footprint."],
    ["HZE-007", "HZ-008", "HZ-006", "affects", "urban drainage and receiving-water interface", "urban / river", "b9_noaa_atlas14", "limited", "Generalized stormwater burden; no outfall or parcel claim."],
    ["HZE-008", "HZ-006", "HZ-019", "forecast_by", "public river and flood warning interface", "river / forecast area", "b9_nws_points", "moderate", "Forecast and warning systems are distinct from observed flood conditions."],
    ["HZE-009", "HZ-009", "HZ-022", "monitored_by", "documented drought assessment system", "county / regional", "b9_usdm_area", "high", "Weekly drought categories are assessed from multiple indicators."],
    ["HZE-010", "HZ-009", "HZ-010", "affects", "meteorological and hydrologic low-water pathway", "county / station", "b9_usgs_dv", "limited", "County drought status does not determine a gauge-specific flow on every date."],
    ["HZE-011", "HZ-010", "HZ-020", "observed_by", "documented USGS daily-value service", "station / river", "b9_usgs_dv", "high", "Daily mean discharge remains a point observation."],
    ["HZE-012", "HZ-011", "HZ-021", "observed_by", "documented CO-OPS station network", "station / Great Lakes", "b9_coops_daily", "high", "Toledo water-level station provides a local lake-level record."],
    ["HZE-013", "HZ-012", "HZ-013", "coastal_interface_with", "lake-level and shoreline process logic", "western Lake Erie / shoreline", "b9_glerl_levels", "moderate", "Lake-level variability can interact with shoreline conditions; no erosion rate is estimated."],
    ["HZE-014", "HZ-014", "HZ-013", "affects", "wind setup/seiche and nearshore water-level logic", "western Lake Erie / bay", "b9_glerl_levels", "moderate", "Great Lakes process is not ocean storm surge."],
    ["HZE-015", "HZ-015", "HZ-013", "affects", "wave, storm, and ice interface", "shoreline / nearshore", "b9_glerl_levels", "limited", "No wave height, ice thickness, or shoreline position is fabricated."],
    ["HZE-016", "HZ-015", "HZ-025", "monitored_by", "documented Great Lakes monitoring resources", "lake / network", "b9_glerl_levels", "moderate", "Ice and lake condition resources are monitoring context."],
    ["HZE-017", "HZ-016", "HZ-017", "historically_occurs_in", "historical event-record aggregation", "regional / county", "b9_storm_events_2025", "high", "Event records document occurrence in selected counties, not a spatial risk surface."],
    ["HZE-018", "HZ-017", "HZ-024", "observed_by", "historical event and climate-data systems", "county / event record", "b9_storm_events", "moderate", "Storm Events and climate series answer different questions and remain separate."],
    ["HZE-019", "HZ-019", "HZ-016", "warning_for", "public severe-weather warning interface", "regional / forecast area", "b9_nws_thunderstorm", "moderate", "Warnings support response but do not remove hazard conditions."],
    ["HZE-020", "HZ-019", "HZ-018", "warning_for", "public winter warning interface", "regional / forecast area", "b9_nws_winter", "moderate", "Warning system relationship; no alert frequency is asserted."],
    ["HZE-021", "HZ-018", "HZ-026", "affects", "winter weather and developed-system interface", "regional / urban", "b9_nws_winter", "limited", "Physical disruption context only; no infrastructure loss estimate."],
    ["HZE-022", "HZ-016", "HZ-026", "affects", "severe storm and developed-system interface", "regional / urban", "b9_nws_thunderstorm", "limited", "No outage probability or communication failure estimate."],
    ["HZE-023", "HZ-023", "HZ-004", "historically_occurs_in", "precipitation-frequency reference context", "site / HUC8", "b9_noaa_atlas14", "moderate", "Frequency product is reference context, not a new event observation."],
    ["HZE-024", "HZ-018", "HZ-015", "coastal_interface_with", "winter lake and ice process interface", "western Lake Erie / shoreline", "b9_glerl_levels", "limited", "Lake-effect snow is not assumed to dominate the whole region."],
    ["HZE-025", "HZ-004", "HZ-020", "monitored_by", "hydrologic monitoring network", "HUC8 / station network", "b9_usgs_dv", "moderate", "Representative station does not imply complete watershed coverage."],
    ["HZE-026", "HZ-012", "HZ-021", "monitored_by", "binational Great Lakes water-level monitoring", "lake / station network", "b9_glerl_levels", "high", "Water levels are continuously monitored through regional federal partnerships."],
    ["HZE-027", "HZ-016", "HZ-019", "forecast_by", "NWS convective forecast and warning service", "regional / forecast area", "b9_nws_points", "moderate", "Forecast availability is separate from event occurrence."],
    ["HZE-028", "HZ-004", "HZ-007", "affects", "runoff/floodplain and mapped regulatory context", "HUC8 / floodplain", "b9_fema_nfhl", "moderate", "Hydrologic event context and regulatory mapping remain distinct categories."],
    ["HZE-029", "HZ-009", "HZ-026", "affects", "drought and developed water-demand context", "county / urban", "b9_usdm_area", "limited", "Generalized physical context; no demand, outage, or health claim."],
    ["HZE-030", "HZ-001", "HZ-026", "affects", "extreme temperature and developed-system context", "station / urban", "b9_acis", "limited", "Station heat observations do not estimate individual exposure or health outcome."],
]

OBS_COLUMNS = ["observation_id", "hazard_family", "metric", "value", "units", "period", "station_or_scope", "spatial_scale", "observed_or_modeled", "source_id", "confidence", "notes"]


def numeric(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def read_acis(filename: str) -> tuple[dict, pd.DataFrame]:
    payload = json.loads((RAW / filename).read_text(encoding="utf-8"))
    columns = ["date", "maxt_f", "mint_f", "avgt_f", "pcpn_in", "snow_in", "snwd_in"]
    frame = pd.DataFrame(payload["data"], columns=columns)
    for col in columns[1:]:
        frame[col] = frame[col].map(numeric)
    return payload, frame


def acis_stats(filename: str, period: str) -> dict:
    payload, frame = read_acis(filename)
    precip_raw = pd.DataFrame(json.loads((RAW / filename).read_text(encoding="utf-8"))["data"], columns=["date", "maxt", "mint", "avgt", "pcpn", "snow", "snwd"])
    numeric_precip = frame["pcpn_in"].dropna()
    max_idx = frame["maxt_f"].idxmax()
    min_idx = frame["mint_f"].idxmin()
    return {
        "period": period,
        "station": payload["meta"]["name"],
        "station_ids": payload["meta"]["sids"],
        "latitude": payload["meta"]["ll"][1],
        "longitude": payload["meta"]["ll"][0],
        "records": int(len(frame)),
        "max_temperature_f": numeric(frame.loc[max_idx, "maxt_f"]),
        "max_temperature_date": frame.loc[max_idx, "date"],
        "min_temperature_f": numeric(frame.loc[min_idx, "mint_f"]),
        "min_temperature_date": frame.loc[min_idx, "date"],
        "days_maxt_ge_90f": int((frame["maxt_f"] >= 90).sum()),
        "days_mint_le_32f": int((frame["mint_f"] <= 32).sum()),
        "precipitation_sum_in_excluding_missing_and_trace": numeric(numeric_precip.sum()),
        "precip_numeric_days": int(numeric_precip.notna().sum()),
        "precip_missing_days": int((precip_raw["pcpn"].eq("M")).sum()),
        "precip_trace_days": int((precip_raw["pcpn"].eq("T")).sum()),
        "days_precip_ge_1in": int((frame["pcpn_in"] >= 1).sum()),
        "snow_observed_days": int(frame["snow_in"].notna().sum()),
    }


def build_observations() -> tuple[pd.DataFrame, dict]:
    s25 = acis_stats("acis_toledo_executive_2025.json", "2025 calendar year")
    s26 = acis_stats("acis_toledo_executive_2026_ytd.json", "2026-01-01 through 2026-09-03 requested")
    cag = json.loads((RAW / "ncei_lucas_county_cag_2025.json").read_text(encoding="utf-8"))
    cag_value = numeric(cag["data"]["202512"]["value"])
    usgs = json.loads((RAW / "usgs_maumee_waterville_daily_flow_2025_2026.json").read_text(encoding="utf-8"))
    series = usgs["value"]["timeSeries"][0]
    flow_rows = [(v["dateTime"][:10], numeric(v.get("value"))) for v in series["values"][0]["value"]]
    flow = pd.DataFrame([(date, value) for date, value in flow_rows if value is not None], columns=["date", "flow_cfs"])
    flow["date"] = pd.to_datetime(flow["date"])
    flow_stats = {}
    for year in (2025, 2026):
        subset = flow[flow["date"].dt.year == year]
        if subset.empty:
            continue
        max_i = subset["flow_cfs"].idxmax(); min_i = subset["flow_cfs"].idxmin()
        flow_stats[str(year)] = {"records": int(len(subset)), "max": numeric(subset.loc[max_i, "flow_cfs"]), "max_date": subset.loc[max_i, "date"].strftime("%Y-%m-%d"), "min": numeric(subset.loc[min_i, "flow_cfs"]), "min_date": subset.loc[min_i, "date"].strftime("%Y-%m-%d")}
    coops = json.loads((RAW / "noaa_coops_toledo_daily_mean_2025.json").read_text(encoding="utf-8"))
    levels = pd.DataFrame([(row["t"], numeric(row.get("v"))) for row in coops["data"]], columns=["date", "level_m"])
    levels = levels.dropna(subset=["level_m"])
    max_i = levels["level_m"].idxmax(); min_i = levels["level_m"].idxmin()
    coops_stats = {"records": int(len(levels)), "max": numeric(levels.loc[max_i, "level_m"]), "max_date": levels.loc[max_i, "date"], "min": numeric(levels.loc[min_i, "level_m"]), "min_date": levels.loc[min_i, "date"]}
    usdm_area = pd.read_csv(RAW / "usdm_lucas_county_area_percent_2025_2026.csv", dtype=str)
    usdm_dsci = pd.read_csv(RAW / "usdm_lucas_county_dsci_2025_2026.csv", dtype=str)
    usdm_area["MapDate"] = pd.to_datetime(usdm_area["MapDate"], format="%Y%m%d")
    usdm_dsci["MapDate"] = pd.to_datetime(usdm_dsci["MapDate"], format="%Y%m%d")
    area = usdm_area.sort_values("MapDate").iloc[-1]
    dsci = usdm_dsci.sort_values("MapDate").iloc[-1]
    usdm_stats = {"map_date": area["MapDate"].strftime("%Y-%m-%d"), "none_percent": numeric(area["None"]), "d0_percent": numeric(area["D0"]), "d1_percent": numeric(area["D1"]), "d2_percent": numeric(area["D2"]), "d3_percent": numeric(area["D3"]), "d4_percent": numeric(area["D4"]), "dsci_map_date": dsci["MapDate"].strftime("%Y-%m-%d"), "dsci": numeric(dsci["DSCI"])}
    storm = json.loads((RAW / "stormevents_2025_core_county_summary.json").read_text(encoding="utf-8"))
    event_counts = storm["counts_by_event_type"]
    def event_count(*names: str) -> int:
        return int(sum(int(event_counts.get(name, 0)) for name in names))
    rows = [
        ["HZO-001", "extreme_heat", "maximum daily air temperature", s25["max_temperature_f"], "deg F", "2025-06-23", "Toledo Executive Airport / KTDZ", "station", "observed", "b9_acis", "high", "Daily station maximum; representative of the station only."],
        ["HZO-002", "extreme_heat", "days with maximum temperature >= 90 F", s25["days_maxt_ge_90f"], "days", "2025 calendar year", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "high", "Derived from returned daily values; missing temperatures are retained in the completeness note."],
        ["HZO-003", "winter", "minimum daily air temperature", s25["min_temperature_f"], "deg F", "2025-01-22", "Toledo Executive Airport / KTDZ", "station", "observed", "b9_acis", "high", "Daily station minimum; not a regional cold-extreme climatology."],
        ["HZO-004", "extreme_heat", "maximum daily air temperature", s26["max_temperature_f"], "deg F", "2026-07-01", "Toledo Executive Airport / KTDZ", "station", "observed", "b9_acis", "high", "2026 YTD service record at retrieval; not a complete calendar year."],
        ["HZO-005", "extreme_heat", "days with maximum temperature >= 90 F", s26["days_maxt_ge_90f"], "days", "2026-01-01 through latest returned record", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "high", "YTD count only; returned record contains missing temperature values."],
        ["HZO-006", "winter", "minimum daily air temperature", s26["min_temperature_f"], "deg F", "2026-01-24", "Toledo Executive Airport / KTDZ", "station", "observed", "b9_acis", "high", "2026 YTD minimum in returned station record."],
        ["HZO-007", "heavy_precipitation_flooding", "reported daily precipitation sum excluding missing and trace", s25["precipitation_sum_in_excluding_missing_and_trace"], "inches", "2025 calendar year", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "moderate", f"Only {s25['precip_numeric_days']} numeric precipitation days; {s25['precip_missing_days']} missing and {s25['precip_trace_days']} trace days. This is not a complete annual precipitation total."],
        ["HZO-008", "heavy_precipitation_flooding", "reported daily precipitation sum excluding missing and trace", s26["precipitation_sum_in_excluding_missing_and_trace"], "inches", "2026-01-01 through latest returned record", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "moderate", f"Only {s26['precip_numeric_days']} numeric precipitation days; {s26['precip_missing_days']} missing and {s26['precip_trace_days']} trace days. Not a complete 2026 total."],
        ["HZO-009", "heavy_precipitation_flooding", "days with daily precipitation >= 1 inch", s25["days_precip_ge_1in"], "days", "2025 calendar year; returned values", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "moderate", "Threshold count is limited by incomplete station precipitation values."],
        ["HZO-010", "heavy_precipitation_flooding", "days with daily precipitation >= 1 inch", s26["days_precip_ge_1in"], "days", "2026-01-01 through latest returned record", "Toledo Executive Airport / KTDZ", "station", "derived from observed", "b9_acis", "moderate", "YTD threshold count; not an extreme-precipitation frequency estimate."],
        ["HZO-011", "extreme_heat", "average annual temperature", cag_value, "deg F", "2025", "Lucas County", "county", "observed_adjusted_series", "b9_ncei_cag", "moderate", "NOAA Climate at a Glance county value; climate-series context, not a station extreme."],
        ["HZO-012", "heavy_precipitation_flooding", "maximum daily mean discharge", flow_stats["2025"]["max"], "cubic feet per second", flow_stats["2025"]["max_date"], "USGS 04193500 Maumee River at Waterville OH", "station", "observed", "b9_usgs_dv", "high", "Daily mean discharge maximum in returned 2025 record; not a flood extent."],
        ["HZO-013", "drought_low_water", "minimum daily mean discharge", flow_stats["2025"]["min"], "cubic feet per second", flow_stats["2025"]["min_date"], "USGS 04193500 Maumee River at Waterville OH", "station", "observed", "b9_usgs_dv", "high", "Daily mean low-flow context at one gauge; not groundwater depletion."],
        ["HZO-014", "heavy_precipitation_flooding", "maximum daily mean discharge", flow_stats["2026"]["max"], "cubic feet per second", flow_stats["2026"]["max_date"], "USGS 04193500 Maumee River at Waterville OH", "station", "observed", "b9_usgs_dv", "high", "2026 YTD returned record; not a future trend or basin-wide maximum."],
        ["HZO-015", "drought_low_water", "minimum daily mean discharge", flow_stats["2026"]["min"], "cubic feet per second", flow_stats["2026"]["min_date"], "USGS 04193500 Maumee River at Waterville OH", "station", "observed", "b9_usgs_dv", "high", "2026 YTD low-flow context at one gauge."],
        ["HZO-016", "lake_coastal", "maximum daily mean water level", coops_stats["max"], "meters IGLD 1985", coops_stats["max_date"], "NOAA CO-OPS 9063085 Toledo", "station", "observed", "b9_coops_daily", "high", "Daily mean lake-level maximum; short-lived wind setup/seiche is not represented by this daily mean."],
        ["HZO-017", "lake_coastal", "minimum daily mean water level", coops_stats["min"], "meters IGLD 1985", coops_stats["min_date"], "NOAA CO-OPS 9063085 Toledo", "station", "observed", "b9_coops_daily", "high", "Daily mean lake-level minimum; no shoreline position is inferred."],
        ["HZO-018", "drought_low_water", "U.S. Drought Monitor area in None category", usdm_stats["none_percent"], "percent of county area", usdm_stats["map_date"], "Lucas County", "county", "expert_assessed_status", "b9_usdm_area", "high", "Latest returned weekly category; None is distinct from a streamflow observation."],
        ["HZO-019", "drought_low_water", "U.S. Drought Monitor area in D1-D4 drought categories", usdm_stats["d1_percent"] + usdm_stats["d2_percent"] + usdm_stats["d3_percent"] + usdm_stats["d4_percent"], "percent of county area", usdm_stats["map_date"], "Lucas County", "county", "expert_assessed_status", "b9_usdm_area", "high", "Computed from category percentages; D0 is abnormally dry, not one of D1-D4."],
        ["HZO-020", "drought_low_water", "Drought Severity and Coverage Index", usdm_stats["dsci"], "index units", usdm_stats["dsci_map_date"], "Lucas County", "county", "expert_assessed_index", "b9_usdm_dsci", "high", "Status index, not a physical water-level or groundwater-depletion metric."],
        ["HZO-021", "severe_convective", "Thunderstorm Wind event records", int(event_count("Thunderstorm Wind")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Selected county records in the project regional context; not a rate, probability, or hazard surface."],
        ["HZO-022", "severe_convective", "Tornado event records", int(event_count("Tornado")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Historical event records do not define deterministic future tornado zones."],
        ["HZO-023", "severe_convective", "Hail event records", int(event_count("Hail")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Historical event records; no hail probability is inferred."],
        ["HZO-024", "heavy_precipitation_flooding", "Flood and flash-flood event records", int(event_count("Flood", "Flash Flood")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Event records remain distinct from FEMA regulatory flood zones and observed flood footprints."],
        ["HZO-025", "winter", "Winter Storm event records", int(event_count("Winter Storm")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Historical winter event records; not a regional snowfall climatology."],
        ["HZO-026", "winter", "Ice Storm event records", int(event_count("Ice Storm")), "county event records", "2025 snapshot", "selected western-basin counties", "county / event record", "historical_event_record", "b9_storm_events_2025", "high", "Historical event records; freeze-thaw and infrastructure implications remain qualitative."],
        ["HZO-027", "lake_coastal", "NWS action flood threshold", 574.36, "feet; station flood-level reference", "current metadata", "NOAA CO-OPS 9063085 Toledo", "station", "warning_threshold", "b9_coops_flood", "high", "Threshold is not an observed lake level and is not compared arithmetically with the IGLD daily-mean series."],
        ["HZO-028", "lake_coastal", "NWS minor flood threshold", 575.22, "feet; station flood-level reference", "current metadata", "NOAA CO-OPS 9063085 Toledo", "station", "warning_threshold", "b9_coops_flood", "high", "Warning threshold only; no damage estimate or exceedance probability."],
    ]
    observations = pd.DataFrame(rows, columns=OBS_COLUMNS)
    summary = {"acis_2025": s25, "acis_2026_ytd": s26, "cag_lucas_2025_f": cag_value, "usgs_flow": flow_stats, "coops_water_level": coops_stats, "usdm_lucas_latest": usdm_stats, "storm_event_counts": event_counts, "storm_event_scope": storm["selected_counties"]}
    return observations, summary


def load_layers():
    huc = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wetlands = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flow = gpd.read_file(GPKG, layer="hydrography_physical")
    flow["geometry"] = flow.geometry.simplify(0.002, preserve_topology=False)
    return huc, lake, wetlands, flow


def render_map() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc, lake, wetlands, flow = load_layers()
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.40)
    flow.plot(ax=ax, color="#4a8798", linewidth=0.30, alpha=0.50)
    actual = [
        ("KTDZ climate", -83.47671, 41.56327, "#c8643f", "o"),
        ("USGS Waterville", -83.7127145, 41.5000526, "#7c5798", "^"),
        ("CO-OPS Toledo", -83.4723, 41.6936, "#2f7890", "s"),
    ]
    for label, x, y, color, marker in actual:
        ax.scatter([x], [y], s=68, c=color, marker=marker, edgecolor="#f1eadc", linewidth=1.0, zorder=6)
        ax.text(x, y - 0.038, label, fontsize=7.2, color=color, ha="center", va="top", zorder=7)
    family_anchors = [
        ("HEAT", -84.05, 41.82, "#c8643f"),
        ("PRECIP / FLOOD", -83.86, 41.26, "#4a8798"),
        ("DROUGHT / LOW WATER", -83.58, 41.08, "#b58a37"),
        ("LAKE / COASTAL", -82.95, 41.72, "#2f7890"),
        ("CONVECTIVE", -83.16, 41.98, "#9a4f59"),
        ("WINTER", -84.20, 41.52, "#667a91"),
    ]
    for label, x, y, color in family_anchors:
        ax.scatter([x], [y], s=250, facecolors="none", edgecolors=color, linewidth=1.6, zorder=5)
        ax.text(x, y, label, fontsize=6.7, color=color, ha="center", va="center", weight="bold", zorder=6)
    ax.set_xlim(-84.55, -82.55)
    ax.set_ylim(40.9, 42.15)
    ax.set_axis_off()
    side = fig.add_axes([0.67, 0.055, 0.30, 0.88]); side.axis("off")
    side.text(0.03, 0.98, "MAP 29 — WESTERN BASIN\nCLIMATE & NATURAL HAZARDS, 2026", va="top", fontsize=14.5, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.03, 0.855, "Compact factual physical-hazard baseline. Colored rings are generalized family interfaces, not hazard zones or risk rankings. Three plotted markers are source-backed stations.", va="top", fontsize=8.5, color="#3f4645", linespacing=1.32)
    side.text(0.03, 0.735, "HAZARD FAMILIES", fontsize=10, weight="bold", color="#17384b")
    bullets = [
        "Extreme heat: temperature observations plus humidity / heat-index warning context",
        "Heavy precipitation and flooding: runoff, tributary, gauge, floodplain, and stormwater interfaces",
        "Drought / low water: county drought status and representative low-flow context",
        "Lake / coastal: water-level variability, shoreline, waves, ice, wind setup, and seiche",
        "Severe convective weather: historical thunderstorm-wind, tornado, hail, and flood records",
        "Winter: cold, snow, ice, and freeze-thaw context without overgeneralized lake-effect claims",
    ]
    y = 0.70
    for bullet in bullets:
        side.text(0.05, y, "• " + bullet, fontsize=7.7, color="#3f4645", va="top", linespacing=1.2); y -= 0.055
    side.text(0.03, 0.335, "MONITORING / SCALE", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.305, "Station observations, county drought/event summaries, watershed/river interfaces, shoreline context, and public forecast/warning systems are kept distinct. FEMA regulatory flood zones are not observed flood footprints. A county event count is not a precise hazard surface.", fontsize=7.8, color="#3f4645", va="top", linespacing=1.3)
    side.text(0.03, 0.175, "BOUNDARIES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.145, "No composite hazard score, unsupported hazard probability, future scenario, mortality, individual exposure, dose, health outcome, social-vulnerability ranking, or emergency-management model. Great Lakes seiche/wind setup is not ocean storm surge. Great Black Swamp remains C — HOLD / noncanonical.", fontsize=7.6, color="#3f4645", va="top", linespacing=1.28)
    side.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#c8643f", markersize=7, label="ACIS climate station"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#7c5798", markersize=7, label="USGS river gauge"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#2f7890", markersize=7, label="CO-OPS lake-level station"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="Lake / water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="Contemporary wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.015), frameon=False, fontsize=7.3)
    png = MAP_BASE.with_suffix(".png")
    svg = MAP_BASE.with_suffix(".svg")
    fig.savefig(png, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for directory in (RAW, NETWORKS, ANALYSIS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    nodes = pd.DataFrame(NODE_ROWS, columns=NODE_COLUMNS)
    edges = pd.DataFrame(EDGE_ROWS, columns=EDGE_COLUMNS)
    observations, acquisition = build_observations()
    sources = pd.DataFrame(SOURCE_ROWS, columns=SOURCE_COLUMNS)
    nodes.to_csv(NODE_PATH, index=False)
    edges.to_csv(EDGE_PATH, index=False)
    observations.to_csv(OBS_PATH, index=False)
    sources.to_csv(SOURCE_PATH, index=False)
    render_map()
    summary = {"retrieval_date": "2026-09-03", **acquisition}
    (REPORTS / "phase9a_acquisition_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    report_text = {
        "climate_hazard_sources.md": """# Phase 9A Climate & Natural Hazards Sources

The Phase 9A source registry is `data/processed/analysis/climate_hazard_sources.csv`.

The baseline combines a representative Toledo Executive Airport daily station record from the Applied Climate Information System with NOAA NCEI county climate context.[1][2]

Hydrologic observations use the USGS daily-value service for Maumee River at Waterville.[5]

FEMA flood-hazard mapping remains a distinct regulatory context.[6]

NOAA/NWS precipitation-frequency products remain a distinct modeled context.[7]

NWS forecast and warning metadata are a separate service layer.[3][4]

Drought context uses the U.S. Drought Monitor weekly county services.[8][9]

The federal-partner methodology description supports interpretation of the drought categories.[10]

Lake/coastal context uses NOAA CO-OPS Toledo station metadata, daily means, and datum metadata.[11][12][13]

CO-OPS flood-level metadata are retained as a separate warning-stage context.[14]

NOAA GLERL provides Great Lakes monitoring and process context.[15]

The selected convective and winter event records come from a dated NOAA NCEI Storm Events archive snapshot.[16][17][18]

NWS and SPC provide hazard-definition and regional severe-weather context.[19][20][21]

The acquisition package preserves raw JSON/CSV responses under `data/raw/climate_hazards/` and a compact selected-county Storm Events aggregation.[16][17]

The full 2025 bulk archive is intentionally not committed.

Station, county, HUC/river, floodplain, shoreline, regional, and forecast-area scales remain explicit.[1][5][6]

The phase does not create a composite hazard score, individual exposure, health outcome, social-vulnerability ranking, or unsupported hazard probability.[6][18][19]
""",
        "climate_hazard_assumptions.md": """# Phase 9A Climate & Natural Hazards Assumptions

## Baseline construction

This is a compact factual 2026 physical-hazard layer, not an exhaustive meteorological atlas. The latest returned 2026 station, USGS, and drought records are labeled as current/YTD observations; the 2025 station, river, lake-level, and Storm Events records provide a complete or dated recent reference where the source returned one.

Station observations remain station observations. The Lucas County Climate at a Glance value is county climate-series context and is not interchangeable with the Toledo Executive Airport station record. One USGS gauge is a representative river observation, not a basin-wide low-flow or flood statistic. Reported station precipitation sums exclude missing and trace values and therefore are not represented as complete annual precipitation totals.

The NOAA CO-OPS daily mean water-level series is retained in meters referenced to IGLD 1985. CO-OPS flood-level metadata are retained separately in the source-reported feet reference and are warning thresholds, not observations; no arithmetic comparison is made between the two. Great Lakes wind setup and seiche are represented as lake-process interfaces, not ocean storm surge.

NOAA Storm Events counts are selected 2025 county event records across a defined western-basin regional context. They are historical reports, not event probabilities, trends, attribution studies, or hazard zones. Winter records provide event context; lake-effect snow is not generalized across the basin without a specific regional climatology.

## Exclusions

No future scenario rows, composite hazard score, deterministic risk map, flood-damage estimate, outage probability, mortality, disease, individual exposure, dose, health outcome, social-vulnerability/EJ ranking, neighborhood ranking, or comprehensive emergency-management model is created. Earthquake, volcano, tsunami, wildfire-dominant, and other non-material hazard modules are not expanded.
""",
        "climate_hazard_findings.md": """# Phase 9A Climate & Natural Hazards Findings

## Extreme heat and winter temperature

FACT: The Toledo Executive Airport ACIS record returned a 2025 maximum daily temperature of 96 deg F on 2025-06-23.[1]

FACT: The same 2025 record contains 20 days with maximum temperature at or above 90 deg F.[1]

FACT: Its 2025 minimum was -2 deg F on 2025-01-22.[1]

FACT: The returned 2026 record through the latest available service date had a maximum of 98 deg F on 2026-07-01 and a minimum of -5 deg F on 2026-01-24.[1]

FACT: The returned 2026 record contains eight days with maximum temperature at or above 90 deg F.[1]

These are station observations, not basin-wide heat or cold climatologies.

The NWS service provides forecast and warning interfaces for the Toledo area, but no heat-index value or warning frequency is invented here.[3][4]

The NOAA NCEI county climate series provides a separate adjusted county context.[2]

INFERENCE: Heat is materially structured by the developed urban context because temperature observations, public warnings, and infrastructure interfaces meet there.

This does not estimate individual exposure or health effects.

Winter conditions are represented through cold observations plus snow, ice, and storm-event context.[19]

Lake-effect snow is not claimed to dominate the Western Basin.

## Heavy precipitation, flooding, and hydrologic dependence

FACT: The ACIS station record contains missing and trace precipitation values, so its reported numeric sums are explicitly incomplete.[1]

FACT: The 2025 returned record has one day at or above one inch among returned numeric values.[1]

FACT: The 2026 returned record has four such days among returned numeric values.[1]

These counts do not substitute for NOAA Atlas 14 frequency estimates or a complete precipitation climatology.[7]

FACT: At USGS 04193500, Maumee River at Waterville, the 2025 daily mean discharge maximum in the returned record is 68,200 cubic feet per second on 2025-04-04.[5]

FACT: The 2025 daily mean minimum is 65 cubic feet per second on 2025-10-25.[5]

FACT: The 2026 returned record includes a maximum of 68,200 cubic feet per second on 2026-04-03 and a minimum of 313 cubic feet per second on 2026-09-02.[5]

These are daily mean observations at one gauge, not observed flood extents, regulatory flood zones, or basin-wide low-flow conditions.[5][6]

INFERENCE: Heavy precipitation and flooding materially connect upland/subwatershed runoff, tributaries, the Lower Maumee, floodplain interfaces, and urban stormwater systems.

FEMA regulatory flood-hazard mapping remains a separate modeled category.[6]

An NFHL zone is not an observed event footprint.[6]

## Drought and low water

FACT: The latest returned Lucas County U.S. Drought Monitor record is dated 2026-08-25 and assigns 100 percent of county area to the None category.[8]

FACT: The same record assigns zero percent of county area to D1-D4 categories and DSCI 0.[8][9]

This is a dated weekly expert-assessed status, not proof that every local soil, stream, or groundwater condition is identical.[10]

The U.S. Drought Monitor integrates precipitation, temperature, soil moisture, streamflow, lake levels, snow, and reported impacts through expert assessment.[10]

INFERENCE: Drought/low-water structure must be monitored through multiple indicators: county drought status, representative streamflow, lake-level observations, soil/agricultural context, and ecological conditions.

No groundwater depletion claim is made.

## Lake and coastal hazards

FACT: NOAA CO-OPS station 9063085 is the Toledo Great Lakes station.[12]

FACT: Its 2025 daily mean water-level record ranges from 172.845 to 174.848 meters in the IGLD 1985 reference used by the API.[11][13]

CO-OPS flood-level metadata are recorded separately in the source-reported feet reference.[14]

Those thresholds are warning metadata and are not compared to the daily-mean IGLD series.[14]

INFERENCE: High and low water levels, waves, ice, shoreline processes, and wind setup/seiche form a connected coastal interface for western Lake Erie.

NOAA GLERL describes a binational monitoring network and separate observation and forecast resources.[15]

The physical process is Great Lakes wind setup/seiche, not ocean storm surge.[15]

This baseline does not estimate shoreline retreat or erosion rates.

## Severe convective weather

FACT: In the selected western-basin county scope, the dated 2025 Storm Events aggregation contains 58 Thunderstorm Wind event records.[16][17][18]

FACT: The same aggregation contains 11 Tornado, nine Hail, seven Flood/Flash Flood, 13 Winter Storm, and four Ice Storm event records.[16][17][18]

These are historical county/event records, not regional rates, attribution evidence, future probabilities, or deterministic hazard surfaces.[18]

INFERENCE: Severe convective weather is a regional disruption interface because thunderstorm wind, hail, tornado, heavy rain, and warning systems overlap with developed infrastructure and access.[20][21]

The model does not rank counties or turn event points into future risk zones.[18][21]

## Monitoring and warning

The baseline links ACIS/NCEI climate records, USGS streamflow, NOAA CO-OPS/GLERL lake-level monitoring, U.S. Drought Monitor assessments, NWS forecast/warning services, and NCEI Storm Events.[1][3][5]

Coverage is heterogeneous by station, county, river reach, lake gauge, and event report.[4][15][18]

A monitoring gap is uncertainty, not evidence of low hazard or high risk.

## Principal data gaps

Humidity and heat-index climatology, complete precipitation-frequency harmonization, tributary gauge coverage, observed flood footprints, and pluvial/flash-flood mapping remain incomplete or out of scope.[1][5][7]

Soil-moisture and agricultural drought series, groundwater evidence, spatially resolved wind setup/seiche and waves, shoreline erosion rates, ice observations, homogeneous severe-weather denominators, and winter freeze-thaw metrics also remain incomplete or out of scope.[15][18][19]

These gaps are recorded rather than filled with synthetic values.
""",
        "climate_hazard_qa.md": """# Phase 9A Climate & Natural Hazards QA

## Structural and provenance checks

The package contains 26 hazard nodes, 30 directed relationships, 28 quantitative/context observation records, and 21 source-registry records. Every node and edge has a source ID, scale, confidence, reality/canon status, and notes. Every observation retains metric, value, units, period, station_or_scope, spatial scale, observed_or_modeled status, source ID, confidence, and limitations.

## Scientific boundary checks

The validator rejects composite scores, unsupported probabilities, future scenario rows, health outcomes, personal exposure/dose, social-vulnerability rankings, neighborhood risk rankings, deterministic event surfaces, and unsupported groundwater claims. It also checks that regulatory flood-zone language is not represented as an observed flood footprint, county event counts are not represented as rates, and Great Lakes seiche/wind setup is not described as ocean storm surge.

## Map QA

Map 29 is a PNG/SVG pair with inspectable SVG text, source-backed station markers, generalized family-interface rings, a legend, scale notes, and explicit non-surface caveats. The map does not draw hazard polygons, composite scores, deterministic risk zones, or unsupported future layers.

## Completeness and limitations

The ACIS precipitation record has missing and trace values, so reported sums and threshold counts are qualified. The USGS and CO-OPS records are station-scale. U.S. Drought Monitor values are weekly county assessment products. Storm Events counts use a dated 2025 archive snapshot and a selected county scope. Warning thresholds are not observations. These distinctions are machine-checked and remain visible in the data tables and reports.

## Protected prior content

Phase 8A-8C freeze manifests and all prior accepted manifests are checked before Phase 9A integration. The Great Black Swamp hold and Toledo intake-coordinate discrepancy are preserved. No health/social-vulnerability module, emergency-management expansion, unsupported hazard probability, release, or tag is included.
""",
    }
    source_block = "\n## Sources\n\n" + "\n".join(f"[{i}] {row[2]}" for i, row in enumerate(SOURCE_ROWS, 1)) + "\n"
    report_text["climate_hazard_sources.md"] += source_block
    report_text["climate_hazard_findings.md"] += source_block
    for name, text in report_text.items():
        (REPORTS / name).write_text(text, encoding="utf-8")
    artifacts = [NODE_PATH, EDGE_PATH, OBS_PATH, SOURCE_PATH, REPORTS / "phase9a_acquisition_summary.json", MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg"), REPORTS / "climate_hazard_sources.md", REPORTS / "climate_hazard_assumptions.md", REPORTS / "climate_hazard_findings.md", REPORTS / "climate_hazard_qa.md"]
    manifest = {"phase": "9A", "status": "implemented_validated_pending_sol_acceptance", "counts": {"nodes": len(nodes), "edges": len(edges), "observations": len(observations), "sources": len(sources)}, "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()

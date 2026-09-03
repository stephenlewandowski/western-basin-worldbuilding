# Phase 9A Climate & Natural Hazards Sources

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

## Sources

[1] https://data.rcc-acis.org/StnData
[2] https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/OH-095-tavg/12/12/2025-2026.json
[3] https://api.weather.gov/points/41.65,-83.54
[4] https://www.weather.gov/wrh/Climate?wfo=cle
[5] https://waterservices.usgs.gov/nwis/dv/?format=json&sites=04193500&startDT=2025-01-01&endDT=2026-09-03&parameterCd=00060&siteStatus=all
[6] https://www.fema.gov/flood-maps/national-flood-hazard-layer
[7] https://hdsc.nws.noaa.gov/pfds/
[8] https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=39095&startdate=01/01/2025&enddate=09/03/2026&statisticsType=1
[9] https://usdmdataservices.unl.edu/api/CountyStatistics/GetDSCI?aoi=39095&startdate=01/01/2025&enddate=09/03/2026&statisticsType=1
[10] https://www.drought.gov/data-maps-tools/us-drought-monitor
[11] https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=daily_mean&begin_date=20250101&end_date=20251231&datum=IGLD&station=9063085&time_zone=gmt&units=metric&format=json
[12] https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085.json
[13] https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085/datums.json
[14] https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9063085/floodlevels.json
[15] https://www.glerl.noaa.gov/data/wlevels/
[16] https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz
[17] https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
[18] https://www.ncei.noaa.gov/stormevents/
[19] https://www.weather.gov/safety/winter
[20] https://www.weather.gov/safety/thunderstorm
[21] https://www.spc.noaa.gov/climo/online/

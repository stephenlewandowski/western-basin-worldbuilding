# Phase 9A Climate & Natural Hazards Findings

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

FACT: The 2026 returned record includes a maximum of 68,200 cubic feet per second on 2026-04-03 and a minimum of 313 cubic feet per second on 2026-07-29; the 2026-09-02 value is 476 cubic feet per second.[5]

These are daily mean observations at one gauge, not observed flood extents, regulatory flood zones, or basin-wide low-flow conditions.[5][6]

INFERENCE: Heavy precipitation and flooding can connect upland/subwatershed runoff, tributaries, the Lower Maumee, floodplain interfaces, and urban stormwater systems. The watershed and urban-drainage relationships are project inferences; the cited gauge and Atlas 14 product do not directly quantify those broader interfaces.

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

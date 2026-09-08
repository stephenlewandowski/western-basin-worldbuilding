# Phase 11B Population, Mobility & System Dependency Findings, 2026

## Residence/workplace relationships

FACT: The package contains 302 mobility observations and 142 generalized commuting relationships. The largest supported cross-county interfaces are:
- 39095 residence to 39173 workplace: 25,171 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39173 residence to 39095 workplace: 20,012 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 18033 residence to 18003 workplace: 5,922 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39051 residence to 39095 workplace: 5,067 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 18003 residence to 18033 workplace: 4,751 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39173 residence to 39063 workplace: 3,166 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39147 residence to 39063 workplace: 2,797 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39123 residence to 39095 workplace: 2,675 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39147 residence to 39143 workplace: 2,266 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 18151 residence to 18003 workplace: 2,172 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39143 residence to 39095 workplace: 2,151 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]
- 39063 residence to 39173 workplace: 2,136 LODES jobs (2023 workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]

INFERENCE: Toledo/Lucas County functions as a major residence/workplace interface in the regional settlement system, while other county-seat, industrial, logistics, and service centers create additional cross-county relationships. The package does not infer why people commute or whether any commuter relocated.

## Commuting

FACT: ACS county records distinguish drive-alone, carpool, public transportation, walking, work-from-home, and long-commute shares. These are residence-based survey estimates for the 2020–2024 period.[9]

INFERENCE: The regional settlement pattern is materially dependent on road-based daily mobility, but this is a generalized commuting/system interface finding, not an individual travel model or a measure of community worth.

## Water and wastewater

FACT/INFERENCE: Population concentration creates functional dependence on drinking-water and wastewater systems. The accepted Toledo operator and Ohio regulatory context support a bounded interface; they do not establish that every Census resident is served by one named system, nor do they create exact service territories or wastewater loads.[22][23]

## Energy

FACT/INFERENCE: Settlement and employment concentrations have functional electricity/heating dependence. Accepted PJM and private-utility context supports the system interface, but no local distribution assignment, demand forecast, outage probability, or feeder topology is created.[24][25]

## Transport and employment

FACT: LODES residence/workplace tabulations show jobs and workers at different geographies and generalized cross-county interfaces. Workplace concentration is not residential concentration; the two are retained as separate metrics.[10][11][12][13][14][15][16][17][18][19][20][21]

## Climate and environmental health

INFERENCE: Settlement nodes can be spatially interfaced with accepted physical hazard and environmental-health pathway layers. These interfaces do not establish personal exposure, dose, illness, mortality, or vulnerability.[26][27]

## Ecology, nutrient/material, housing, and governance

INFERENCE: Settlement, stormwater/wastewater, land-cover, nutrient/material, housing, and governance interfaces are represented qualitatively. The accepted ecology and biogeochemical layers are not rebuilt; no new flux, ecological condition, utility service population, or governance-quality score is inferred.[28][29][30]

## Major limitations

UNCERTAINTY: LODES has nonsampling and modelling limitations; ACS has sampling and estimate-period limitations; Census/PEP/ACS vintages are not a single 2026 surface; county OD aggregation obscures within-county and route-level structure; exact utility service territories and population served are not publicly established in this package; seasonal/institutional/ambient population and transit ridership are not modeled.

## Sources

[1] https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Ohio/oh2020.pl.zip
[2] https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Michigan/mi2020.pl.zip
[3] https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Indiana/in2020.pl.zip
[4] https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv
[5] https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024.csv
[6] https://api.censusreporter.org/1.0/data/show/acs2024_5yr
[7] https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html?layer=counties
[8] https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html?layer=places
[9] https://api.censusreporter.org/1.0/data/show/acs2024_5yr?tables=B08301,B08303
[10] https://lehd.ces.census.gov/data/lodes/LODES8/oh/wac/oh_wac_S000_JT00_2023.csv.gz
[11] https://lehd.ces.census.gov/data/lodes/LODES8/oh/rac/oh_rac_S000_JT00_2023.csv.gz
[12] https://lehd.ces.census.gov/data/lodes/LODES8/oh/od/oh_od_main_JT00_2023.csv.gz
[13] https://lehd.ces.census.gov/data/lodes/LODES8/oh/oh_xwalk.csv.gz
[14] https://lehd.ces.census.gov/data/lodes/LODES8/mi/wac/mi_wac_S000_JT00_2021.csv.gz
[15] https://lehd.ces.census.gov/data/lodes/LODES8/mi/rac/mi_rac_S000_JT00_2023.csv.gz
[16] https://lehd.ces.census.gov/data/lodes/LODES8/mi/od/mi_od_main_JT00_2021.csv.gz
[17] https://lehd.ces.census.gov/data/lodes/LODES8/mi/mi_xwalk.csv.gz
[18] https://lehd.ces.census.gov/data/lodes/LODES8/in/wac/in_wac_S000_JT00_2023.csv.gz
[19] https://lehd.ces.census.gov/data/lodes/LODES8/in/rac/in_rac_S000_JT00_2023.csv.gz
[20] https://lehd.ces.census.gov/data/lodes/LODES8/in/od/in_od_main_JT00_2023.csv.gz
[21] https://lehd.ces.census.gov/data/lodes/LODES8/in/in_xwalk.csv.gz
[22] reports/governance_baseline_sources.md?s03_toledo_treatment
[23] reports/governance_baseline_sources.md?s05_ohio_npdes
[24] reports/governance_baseline_sources.md?s24_pjm
[25] reports/governance_baseline_sources.md?s28_firstenergy
[26] reports/governance_baseline_sources.md?s39_odot
[27] reports/phase9a_climate_natural_hazards_freeze_manifest.json
[28] reports/phase7a_exposure_environmental_health_freeze_manifest.json
[29] reports/phase6a_ecology_freeze_manifest.json
[30] reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json
[31] reports/phase10b_governance_dependencies_coordination_freeze_manifest.json
[32] https://lehd.ces.census.gov/data/lodes/LODES8/oh/wac/oh_wac_S000_JT00_2023.csv.gz;https://lehd.ces.census.gov/data/lodes/LODES8/oh/rac/oh_rac_S000_JT00_2023.csv.gz
[33] https://lehd.ces.census.gov/data/lodes/LODES8/mi/wac/mi_wac_S000_JT00_2021.csv.gz;https://lehd.ces.census.gov/data/lodes/LODES8/mi/rac/mi_rac_S000_JT00_2023.csv.gz
[34] https://lehd.ces.census.gov/data/lodes/LODES8/in/wac/in_wac_S000_JT00_2023.csv.gz;https://lehd.ces.census.gov/data/lodes/LODES8/in/rac/in_rac_S000_JT00_2023.csv.gz

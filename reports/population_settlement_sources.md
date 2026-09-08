# Phase 11A Population & Settlement Sources

This package uses the 2020 Decennial Census P.L. 94-171 summary files for enumerated population and housing units at county/place scale.[1][2][3] Recent change uses the 2024 Vintage Population Estimates Program county and place files, whose annual July 1 estimates are not a 2026 Census.[4][5] Households, occupancy/vacancy, age structure, household size, housing age, and county commuting context use ACS 2024 5-year estimates retrieved through the Census Reporter programmatic mirror of Census tables.[6][9]

Census TIGER/TIGERweb county/place geography supports the analytical frame and map geometry.[7][8] LODES 8.4 WAC/RAC/OD products provide generalized workplace, residence, and origin-destination job tabulations, with Ohio and Indiana 2023 files and Michigan 2021 WAC/OD plus 2023 RAC in the current public release.[10][11][12][13][14][15][16][17][18][19][20][21] They are aggregated administrative/modelled products rather than individual movement records.

The cross-system dependency layer reuses accepted Phase 6–10 context without rebuilding those systems. It does not assign every resident to a utility territory, convert population presence to exposure or illness, or turn municipal boundaries into service territories.

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

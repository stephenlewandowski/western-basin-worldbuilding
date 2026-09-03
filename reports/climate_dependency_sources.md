# Phase 9B Climate/Hazard Dependency Sources

The Phase 9B source registry is `data/processed/analysis/climate_dependency_sources.csv`.

The Fifth National Climate Assessment supplies Midwest climate/infrastructure context, but does not directly document local asset effects.[1]

Its energy chapter supplies heat, cooling-demand, and energy-dependency context.[2]

EPA supplies observed Great Lakes lake-level variability context; it is not direct evidence of navigation or treatment/intake operations.[3]

NOAA supplies seiche and wind-driven standing-wave mechanism context.[4]

NOAA GLERL supplies Great Lakes ice-cover context; lake-wide ice does not establish local shoreline or ecological effects.[5]

NOAA coastal tools supply screening-level lake-level and inundation context.[6][7]

NWS Great Lakes and winter products supply monitoring and warning interfaces, not direct evidence of freight, infrastructure, or communications consequences.[8][9]

The Western Lake Erie study supplies a documented nutrient/meteorological/ecological compound mechanism.[10]

FEMA regulatory mapping is retained as a distinct flood-planning context.[11]. The parallel `d9_fema_nfhl` and `d9_noaa_inundation` registry rows are retained for audit context only and are not used as claim-row sources; their limitations state this explicitly.

The machine-readable rows distinguish supported system dependencies, documented observation/product interfaces, physically plausible pathways, documented mechanisms plus plausible pathways, documented controls/tools, potential-buffer inference, and unsupported/unknown interfaces. Phase 9B uses these sources to qualify relationships and controls, not to create outage, damage, illness, exposure, social-vulnerability, or joint-probability estimates.

## Sources

[1] https://doi.org/10.7930/NCA5.2023.CH24
[2] https://doi.org/10.7930/NCA5.2023.CH5
[3] https://www.epa.gov/climate-indicators/great-lakes
[4] https://oceanservice.noaa.gov/facts/seiche.html
[5] https://www.glerl.noaa.gov/data/ice
[6] https://coast.noaa.gov/llv
[7] https://tidesandcurrents.noaa.gov/inundationdb/inundation.html?id=9063085
[8] https://www.weather.gov/greatlakes/globs
[9] https://www.weather.gov/cle/winter
[10] https://www.pnas.org/doi/10.1073/pnas.1216006110
[11] https://www.fema.gov/flood-maps/national-flood-hazard-layer
[12] https://epa.ohio.gov/divisions-and-offices/surface-water/permitting
[13] https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer
[14] https://h2.ohio.gov/

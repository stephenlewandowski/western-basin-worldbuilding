# Empirical input assessment — 3 October 2026

**Decision:** publish a separate observed-flow record now; keep routed nutrient
cases synthetic. No Model Lab mathematics, saved cases or frozen data were changed.

| Input | Actual readiness | Use now / missing requirement |
| --- | --- | --- |
| Waterville daily flow | USGS 04193500, parameter 00060, statistic 00003, ft³/s. Retained 609 daily means, 2025-01-01–2026-09-02; 2026-06-01 missing. | Display historical observations at one station. Not HUC-local source input. |
| Complete 2025 flow | 365 days; snapshot flags 322 approved, 43 provisional, 13 estimated (estimated overlaps approved). | Public chart and exact values/flags; keep historical quality flags. |
| Nutrient flux context | Ten records; zero measured spatial TN/TP loads. Spring targets/capacity and allocations are regulatory context. | Do not use targets as observed inputs. Need matching measured forms, dates, units, coverage and methods. |
| Biogeochemical network | All 24 edges have unknown quantity. | Qualitative context only. |
| Airport precipitation | 2025: 254 numeric, 69 missing, 42 trace days. Retained 2026: 189 numeric, 57 missing. | Not distributed observed runoff; trace/missing days are not numeric zero. |
| Wetlands/controls | Presence and conditional intervention context. | No measured retention coefficients or demonstrated removal. |
| Routing geography | 252 HUCs, 251 links, twelve project inferences. | Gauge-to-accounting-boundary crosswalk remains unverified. |

The terminal project HUC is not a measured river-mouth boundary. Cumulative gauge
discharge cannot be entered as local contributions to each HUC without double
counting. Nondiagnostic runs already require all 756 HUC/constituent rows and
consistent input status; those safeguards remain intact. The Shiny explorer
continues to admit only the three committed synthetic cases.

## A useful empirical product without model expansion

[The observed-flow display](../outputs/model_lab/observations/waterville_daily_flow_2025.svg)
uses [daily values and flags](../outputs/model_lab/observations/waterville_daily_flow_2025.csv)
extracted from the retained
[USGS snapshot](../data/raw/climate_hazards/usgs_maumee_waterville_daily_flow_2025_2026.json).
Source SHA-256: `a2b206f85f313368e5bcb743dca6241a4bcbea37676a88176348802f42cd93f6`.
Retrieval: **2026-09-03T08:24:06Z**; station coordinates **41.5000526, −83.7127145**.
The [manifest](../outputs/model_lab/observations/waterville_observation_manifest.json)
records lineage, period, units, operations and flags.

Rebuild from repository root:

```sh
python src/python/model_lab/build_observed_flow_record.py
Rscript src/R/model_lab/build_observed_flow_card.R
```

The Python builder selects calendar days without timezone shifts, checks every
2025 day, finite nonnegative values and exact A/P/e qualifier classes. It performs
no imputation or unit conversion. Base R draws the record with separate provisional
and estimated markers. Daily means do not describe instantaneous peaks, flood
extent, nutrient loads or prediction. This is an observation display, not a fourth
routing case. Source flags describe the downloaded version, not current USGS approval.

Credit: [USGS Maumee River at Waterville](https://waterdata.usgs.gov/monitoring-location/04193500/).
[USGS reuse policy](https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted)
applies; the repository MIT license does not replace third-party source terms.

## Next empirical step, only when useful

Heidelberg’s [official tributary data page](https://www.heidelberg.edu/academics/research-and-centers/national-center-for-water-quality-research/tributary-data-download)
is a promising nutrient-record lead. Historical files can be revised. Record the
exact file version/hash, station, period, chemical forms, units, missing/censored
values, methods and reuse permission before bringing one record into the project.
Reuse terms were not established in this assessment; no data were acquired.

Stop before routed empirical loads until compatible local-source inputs and a
documented geography/period crosswalk exist. Stop nutrient-load comparison without
matching discharge and nutrient methods/coverage. Keep absent observations absent;
do not replace them with zero, targets or invented wetland efficiency.

Grounding: [readiness/design report](model_lab_v01_water_nutrient_readiness.md),
[quantitative context](../data/processed/analysis/biogeochemical_quantitative_fluxes.csv),
[quantity-status network](../data/processed/networks/biogeochemical_flux_edges.csv),
[hazard observations](../data/processed/analysis/climate_hazard_observations.csv).

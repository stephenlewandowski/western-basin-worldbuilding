# Western Basin climate integration: evidence and data readiness

**5 October 2026 · bounded additive pass · public Study prototype · no new canon**

Climate now supplies conditions for places and ordinary work, alongside geography,
water, energy and information. This pass adds five observed indicator families,
three inspectable coupling charts, a futurescape matrix and amendments for future
art. Accepted illustrations, frozen science, Model Lab mathematics/outputs and
the Reading Hall continuity lock remain unchanged. Starting main: `a17ef20`.

**Published:** source `79b3a6bc7608c85fd8644fff90853767e79bb18b`, successful
[Pages run37260923798](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37260923798).
The original observed-history prototype and its checks below are retained as a
dated implementation checkpoint. A subsequent approved
[Glass City summer / first local projection sample](glass_city_summer_and_local_climate_2026-10-05.md)
adds county-scale results; the original observed air/lake/ice arrays are unchanged.

## Existing foundation and scope

[Climate/hazard findings](climate_hazard_findings.md) and
[scenario findings](climate_scenario_findings.md) already preserve regional
warming context, Toledo Executive / KTDZ's short daily record, precipitation
limitations and qualitative compound-hazard futures. Those records are retained
as accepted history. The new long record is **Toledo Express / USW00094830**, not
an extension of KTDZ. A public study belongs beside Studies, not hidden in Methods.

The [indicator set](../data/climate/indicators.json) is small and reproducible from
[five retained NOAA snapshots](../data/climate/source_manifest.json), about 750 KB
stored. It is not a Model Lab result. Histories end in 2025; records into 2026 in
the original snapshots are not treated as complete annual observations.

## Observed climatology

| Family | Retained product / coverage | What is ready | What it cannot establish |
| --- | --- | --- | --- |
| Air-temperature history | NCEI GHCN daily TMAX/TMIN, Express, 1991–2025 | Complete-year daily-midpoint means; official 1991–2020 normal alongside | Street shade, indoor temperature, worker radiant heat; an unadjusted midpoint is not official TAVG |
| Hot days / warm nights | Same station, native tenths°C | Nominal ≥90°F maxima and ≥70°F daily minima; explicit native thresholds | Humidity-adjusted heat index, hourly warm-night exposure, official heat alerts |
| Hot-spell duration / intensity | Same daily maxima | ≥3 consecutive hot days; count, total days, longest run, hottest event-average maximum | A health-risk index or nationally standardized heat-wave metric |
| Surface temperature | NOAA GLSEA whole-Erie daily analysis, 1995–2025 | Annual and June–August daily means | Western-basin-only conditions, intake depth, vertical profiles, oxygen or HAB severity |
| Ice | NOAA GLERL whole-Erie annual maximum, 1973–2025 | Maximum annual extent in percent | Winter-average cover, duration, thickness, local access safety |

Official NOAA 1991–2020 normal: **52.2°F annual mean**, **18.7 ≥90°F days/year**,
**1,018.8°F·days/year cooling degree-days, base 65°F**. July mean is 75.4°F.
These are standard normals with completeness flag `S` and 30 years. The annual
CSV hot-day value is used rather than a sum of rounded monthly values (18.8).
[NOAA normals](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals),
[official station CSV](https://www.ncei.noaa.gov/data/normals-annualseasonal/1991-2020/access/USW00094830.csv).

The fully paired 1991–2020 daily baseline gives **18.7333 hot days/year**, **10.1667
warm-night proxy days/year**, **2.5333 hot spells/year**, and **11.1333 days/year
within spells**. Its longest spell is 10 days (2012). Daily mean histories are
unadjusted, derived midpoint statistics; no fitted trend is claimed. Native
thresholds 322 and 211 tenths°C preserve the quantization of reported 90°F/70°F.
[GHCN station source](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00094830.dly),
[format/quality flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt).

Every baseline year is complete. The retained 2024 and 2025 daily records are not;
all annual derived indicators for them are withheld (`null`), with valid-day counts
exposed. Quality-flagged observations are excluded; missing days do not become
cool days. No imputation, homogenization or calibration occurs in this pass.

The [GLISA Express page](https://glisa.umich.edu/station/toledo-express-ap/) reports
50.8°F and 14.6 days *exceeding* 90°F for 1991–2020. A strict threshold and
[additional QC](https://glisa.umich.edu/wp-content/uploads/2026/02/HistoricalClimatologies_QualityControl.pdf)
affect comparisons, but the mean discrepancy is unresolved. The prototype uses
official NOAA normals, keeps GLISA contextual and records reconciliation as debt.
No averaging or silent merging is appropriate.

| Year | Whole-Erie annual surface mean °C | June–August mean °C | Maximum ice % |
| --- | ---: | ---: | ---: |
| 2020 | 12.0979 | 22.5146 | 15.9 |
| 2021 | 12.4489 | 22.0634 | 85.7 |
| 2022 | 11.6248 | 22.0440 | 93.8 |
| 2023 | 12.0145 | 21.3378 | 40.2 |
| 2024 | 12.9804 | 22.4393 | 35.7 |
| 2025 | 11.8076 | 22.3789 | 95.8 |

These years illustrate variability, not a trend estimate. Surface means have full
calendar-year and 92-day summer coverage. GLSEA uses clear-sky satellite imagery
and smoothing when imagery is missing: observation-derived analysis, not direct
daily field readings at every pixel. Ice is the annual maximum, not seasonal mean.
[GLSEA method](https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature/),
[temperature CSV](https://apps.glerl.noaa.gov/coastwatch/webdata/statistic/csv/all_year_glsea_avg_e_C.csv),
[ice source](https://www.glerl.noaa.gov/data/ice/glicd/AMIC.txt).

## Lake structure: the important qualification

Shallow western Lake Erie is usually polymictic; it is not simply a permanently
stratified version of the central basin. Kuai & Wells' five-site Pigeon Bay study
found >2°C vertical stratification during 45%, 54% and 25% of June–September
2021–2023. Recorded hypoxic events (<2 mg/L oxygen) accompanied stratification;
83%, 86% and 67% were associated with colder central-basin water advection.
This is local observational evidence, not basin-wide prevalence or warming
attribution. Heat storage, wind, mixing, depth, incoming water and oxygen demand
must remain visible. Surface data alone cannot diagnose hypoxia, a bloom or an
intake. [Primary paper, 2025](https://doi.org/10.1016/j.jglr.2025.102596).

[NOAA's ice guidance](https://www.glerl.noaa.gov/data/ice/) connects ice with
thermal structure, water movement and ecology, while subsequent weather and
heat storage also influence summer conditions. A high-ice 2025 does not negate
long-term change; low ice alone cannot prescribe the next summer's oxygen.

## 2075 scenarios: explicit readiness, no invented local values

Use **2061–2090** as a declared 2075-centered climate window. Scene year and
climatological window are different. Three air pathway frames are registered:
LOCA2 CMIP6 **SSP2-4.5**, **SSP3-7.0**, **SSP5-8.5**, compared with 1991–2020.
Local quantitative envelopes remain `null` because extraction has not occurred.
The public prototype says this plainly. Adaptation/access choices are independent
of forcing paths; the compound-hot/poor-air/grid-peak scene is a conditional stress
test, not an inevitable forecast.

[LOCA2 metadata](https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023/)
provides 6 km daily Tmin/Tmax/precipitation for 1950–2100, 27 CMIP6 models, with
unequal member/path availability. Next extraction must retain cell locations,
release/version, calendars, model/member identity, weighting and matched baseline;
report model spread separately from pathway spread. It does not resolve streets,
occupational exposure or lake physics.

Immediate numerical context comes from the
[GLISA October 2024 regional synthesis](https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf):
rounded +3–6°F (2040–2059) and +6–11°F (2080–2099) versus 1980–1999, with 9–37
and 27–66 additional >90°F days. The PDF credits UW-Madison RegCM4 downscaling.
These regional published ranges are not local quantiles or SSP-specific outputs;
do not interpolate them to a single 2075 value. Existing frozen exact ranges and
their original source record remain unchanged.

For lake projections, [GLARM-Proj1](https://digitalcommons.mtu.edu/glts/) is a
separate candidate: daily 1981–2099 lake temperature/ice, GISS/IPSL/MPI members
and ensemble means, RCP4.5/RCP8.5, lake grids 1–4 km horizontally and 5 m vertical
product. Proposed future window is 2061–2090 versus its 2000–2019 baseline.
Published 2030–2049/2080–2099 results must not be relabeled 2075. Ice biases,
three-model coverage and nearshore/depth resolution limit conclusions.
[Methods paper](https://gmd.copernicus.org/articles/15/4425/2022/). RCP and SSP
labels, regional baselines and model grids remain distinct.

## Coupling and missing inputs

[NCA5 Energy](https://nca2023.globalchange.gov/chapter/5/) supports warming-driven
cooling demand and greater summer electricity stress. Local peak loads cannot
be obtained by multiplying an airport temperature by a generic national factor.
[NCA5 Midwest](https://nca2023.globalchange.gov/chapter/24/) supports heat-related
air-quality pressures. Ozone also needs precursors and chemistry; smoke/PM depends
on sources and transport. Visible haze is not a pollution measurement. Primary
chapter search extracts were verified; fresh full-document access was intermittent.

The public connection charts keep these as qualitative conditions and decisions:
heat → cooling → grid peak → building/compute/industrial load management → indoor
conditions; heat/stagnation and emissions/transport → outdoor air → ventilation/
filtration; warm winter/low ice → seasonal warming → thermal structure, with wind,
depth, incoming water, oxygen demand and biology alongside ecology/intakes.

| Readiness | Next evidence | Decision it would support |
| --- | --- | --- |
| Ready now | Retained station, surface and maximum-ice records | Dated histories with units and coverage |
| Ready for extraction | LOCA2 and GLARM metadata/download products | Bounded ensemble climate conditions; no street precision |
| Requires separate observations | Humidity, wind/radiation, neighborhood sensors, indoor conditions, cooling access | Heat-health/occupational exposure and refuge accessibility |
| Requires separate observations | Lake depth-temperature/oxygen profiles and intake-specific records | Episodic stratification and local ecological/utility questions |
| Requires separate observations | Ozone/PM/smoke and actual hourly load/capacity | Air/cooling decisions and regional peak-management questions |
| Separate Model Lab track | Compatible nutrient concentrations, flow dates, flags and geographic crosswalk | Empirical load/routing development; unchanged by this pass |

## Deliverables, image decisions and next investment

- [Climate & Thermal Regime route](../atlas/climate-thermal-regime/index.html)
  starts with observed history, then scenarios, coupling charts and five ordinary
  scene seeds. Homepage, roadmap and the five places link to it.
- [Climate coupling matrix](climate_futurescape_matrix_2026-10-05.md) covers the
  five futurescapes, related studies and Model Lab/system boundaries.
- [Visual audit](climate_visual_audit_2026-10-05.md) inspects 21 distinct displayed
  assets; accepted artwork remains unchanged, with no retroactive heat-wave claim.
- [Future art direction](../docs/climate_art_direction.md), living style guide
  and scene template make season/thermal conditions a compact production check.

Next scientific priority: extract a modest model-balanced LOCA2 sample and
reconcile station products; then obtain local depth/oxygen and exposure data.
Next creative priority: one Glass City summer shade interruption or a warm-night
scene. Give heat a physical consequence and an ordinary response; avoid another
dashboard wall or a universal amber-haze palette. No new scene/image is produced
within this pass.

## Verification

- 48 web tests in seven files pass; four Python climate guards pass (quality flags,
  quantized thresholds, missing-day/spell handling and leap-day coverage).
- TypeScript and production build pass, with 16 HTML routes.
- 613 repository-relative Markdown links pass; browser checks find no broken
  same-page anchors on the 16 routes.
- Production-preview checks at 1440, 390 and 320 px pass all five indicator
  controls, native keyboard/focus, withheld incomplete years, table access, three
  chart selectors, card/edge menus, zoom/reset and five futurescape pointers.
  No horizontal page overflow or browser runtime errors. Quantitative plots
  retain readable axes and scroll within their panel on narrow screens.
- Source hashes verify and a repeated retained-source build produces identical
  JSON. `.gitattributes` preserves raw NOAA bytes across Windows checkout.
- LFS integrity and `git diff --check` pass. 636 protected files, from 645 manifest
  references plus canon/Hall lock, match starting main. No accepted art, Model Lab,
  Waterville record or frozen scientific-path overlap.
- Independent read-only air/lake reviews found no material scientific contradiction;
  the raw-snapshot line-ending issue they identified was fixed.

Local preview:
`http://127.0.0.1:4175/western-basin-worldbuilding/atlas/climate-thermal-regime/`.
Production preview used port 4176. Screenshots/check helpers are ignored under
`temp/climate-integration/`; they are development artifacts, not new image assets.
New repository-source links target main and will resolve remotely after publication.
At the implementation checkpoint this prototype was local, with no Climate-pass
commit, push or deployment. The user subsequently authorized publication on
5 October; exact source/deployment verification will be added below. Existing
published story/game remain unchanged. Git state: main, 12 modified tracked files
and 17 new files; no deletions.

## Exact changed paths

```text
.gitattributes
PROJECT_STATUS.md
README.md
atlas/climate-thermal-regime/index.html
data/climate/README.md
data/climate/indicators.json
data/climate/source_manifest.json
data/climate/sources/erie_glsea_daily.csv
data/climate/sources/great_lakes_annual_max_ice.txt
data/climate/sources/toledo_express_ghcnd.dly.gz
data/climate/sources/toledo_express_normals_annual.csv
data/climate/sources/toledo_express_normals_monthly.csv
docs/README.md
docs/climate_art_direction.md
docs/phase_briefs/phase17d_public_visual_style_guide.md
docs/templates/scene_card.md
reports/README.md
reports/climate_futurescape_matrix_2026-10-05.md
reports/climate_integration_2026-10-05.md
reports/climate_visual_audit_2026-10-05.md
reports/current_phase_handoff.md
src/atlas/climate-study.test.ts
src/atlas/climate-study.ts
src/atlas/connection-data.ts
src/atlas/main.ts
src/atlas/style.css
src/python/climate/build_climate_indicators.py
tests/test_climate_indicators.py
vite.config.ts
```

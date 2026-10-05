# Glass City summer scene and local climate sample

**5 October 2026 · bounded follow-up to the published Climate Integration Pass**

The user authorized publication and requested two concrete next products:
a summer scene where interrupted shade changes a routine, and a modest local
climate-projection extraction. Starting source is `79b3a6b`; the first climate
study was successfully published by [Pages run 37260923798](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37260923798).

## The Usual Table

A new Glass City vignette gives Leena and Jo a Friday afternoon, six peaches,
dominoes and a table whose shade is interrupted by a missing cassette. Three
native choices change location, time and company: the longer public shaded route,
a shared market table, or asking the shopkeeper for shade. One ending
per playthrough, restart, no score/timer/save/network. Pleasure and dry humor stay
at the center; no health emergency or moral verdict is needed.

[Scene record](../stories/the_usual_table.md),
[module](../src/atlas/glass-city-summer.ts). New scene/art are provisional fiction;
publication establishes no new canon. Public passage stays outside the cordoned
work bay; an absent panel supplies no route onto service ribs. The shopkeeper's
permission is specific to this afternoon; no service connection or surveyed
property break is inferred from the new illustration. The original Glass City images remain
architectural studies from another day and are unchanged.

One **new** illustration was generated with the built-in imagegen tool, using the
accepted Glass City lead only as architecture/style reference. Hard summer sun,
dry ground, green foliage, lightweight leisure clothes, work PPE, refill bottle,
fruit, cushion and a sunlit tabletop replace the portfolio's repeated wet/dusk
cues. The new image has coherent foreground people and a readable empty panel;
the shop/property geometry remains approximate. No performance or 2075 temperature
is inferred from the image. [Prompt/master/derivative lineage](../assets/atlas/glass-city-summer/README.md).
The PNG master is archived; WebP packaging preserves dimensions without semantic edits.
The earlier comic remains withdrawn.

## Local extraction: what was actually calculated

Use **Lucas County, Ohio, GEOID 39095**, as a local regional reference rather than
claiming a street or airport grid point. The small input is the NOAA/Esri Climate
Resilience Information System's **LOCA2-derived annual county model tables**,
filtered `MODEL_SET='LOCA2'`. The separate STAR series and weighted `Ensemble`
records are excluded. [Official CRIS methods](https://cris.climate.gov/pages/about-the-data),
[source item](https://www.arcgis.com/home/item.html?id=f5134f46a5a3491f8259145271644eed),
[provider processing code](https://github.com/NOAA-CRIS/CRIS).

Three published series: **IPSL-CM6A-LR, MPI-ESM1-2-HR, MRI-ESM2-0**; all five
selected metrics are available for all three paths. Selection is a modest
availability-based sample across different GCM families, not a representative
sample of all 27 parent LOCA2 models. Weight each published model series equally;
do not claim equal realization weights or use the provider's full-ensemble weighting.

The historical query supplies **72 rows**: three models × 1991–2014. The future
query supplies **108 rows**: three models × (2015–2020 and 2061–2090), with fields
for SSP245/370/585. Query pagination/truncation, duplicate model/year, missing
years and nonfinite values are rejected. Every model/path has **30 baseline and
30 future years**. Baseline joins 24 historical years with six years from the
same SSP as the future. It is a **modeled baseline**, not the observed airport normal.

Average each annual metric over each window, subtract within model/path, then
report equal-weight sample mean and min/max of the three climatologies.
Temperature changes in °F convert to °C by multiplying by 5/9; absolute temperatures
also subtract 32. Mean annual statistics give each year equal weight.

| Path | Mean annual warming °C | Three-series warming range °C | Future ≥90°F days/year | Future ≥70°F daily-minimum proxy |
| --- | ---: | ---: | ---: | ---: |
| SSP2-4.5 | 2.5812 | 2.0728–2.9306 | 43.3232 | 35.2279 |
| SSP3-7.0 | 3.2347 | 2.9013–3.7350 | 56.9498 | 49.0355 |
| SSP5-8.5 | 4.2221 | 3.7684–5.0809 | 70.2336 | 61.2584 |

Counts are **county spatial means**, so fractional days are expected. Included
fields: annual mean daily midpoint, June–August mean temperature, inclusive
daily maximum ≥90°F / minimum ≥70°F counts, cooling degree-days °F·days with a 65°F base.
CDD is a climate proxy, not an electricity-load forecast; warm nights are daily
minimum proxies, not hourly or humidity-adjusted exposure. Surface/lake/oxygen
projections and hot-spell duration are not inferred from these annual summaries.

## Provenance and limits

- [Queries and metadata manifest](../data/climate/projection_source_manifest.json)
  records exact URLs, UTC retrieval times, source hashes and CC BY 4.0 attribution.
  Raw query/schema/item responses are retained byte-for-byte (about 170 KB).
- [Projection JSON](../data/climate/local_projections.json) retains each model/path,
  both windows, baseline/future/change, units, equal weights and sample ranges.
- [Reproducible extractor](../src/python/climate/extract_local_projections.py)
  rebuilds offline from snapshots; `--fetch` deliberately refreshes them. No
  netCDF packages or hundreds of megabytes of continental grids are required.
- Parent LOCA2 is approximately 6 km; the county service's exact upstream release,
  individual realization IDs and within-model member handling are **not exposed**.
  CRIS documentation/example code differ on resampling direction. County zonal
  means/TIGER 2023 are supported; unchanged native grid geometry is not asserted.
- The selected min/max is not a confidence interval, annual variability, a full
  ensemble envelope or upper/lower bound. No likelihood is assigned to pathways.
- Do not add county anomalies to the airport normal and label the result an exact
  future station temperature. No street, indoor, worker or entire-watershed
  exposure follows. The scene's hot afternoon remains independent fiction.

The public study now replaces pending air-path placeholders with this labeled
first local sample and an inspectable nine-series table. Full ensemble/member
extraction, station-product reconciliation, lake projections, street heat and
measured nutrient inputs remain further work. Observed climate arrays, Model Lab,
Waterville, frozen products, accepted artwork and Hall continuity remain unchanged.

## Validation and publication

Local verification passes:

- 51 web tests in eight files; TypeScript/Vite production build with 16 routes.
- Six Python climate tests, including matched-path baselines, temperature-change
  conversion and rejection of incomplete windows. Both offline builders reproduce
  their JSON byte-for-byte.
- 636 Markdown/internal links, `git diff --check` and `git lfs fsck`.
- Production-preview browser checks at 1440, 390 and 320 px: all three scene
  endings, native keyboard controls, mutual exclusion, restart/focus, image loading,
  three projection cards and nine source-series rows. No horizontal page overflow
  or runtime errors. Observed indicator controls, coupling diagrams, same-page
  anchors and all 16 routes also pass.
- Preservation check: 636 protected files and 645 manifest references match
  `79b3a6b`; prior observed indicator content outside future-scenario metadata and
  all five original NOAA snapshots are unchanged. New image master/derivative
  hashes match their manifest.

Independent agent reviews checked calculation/provenance and scene/image
continuity. They prompted clearer annual-count wording and removal of a property
break claim the image cannot establish. These are continuity/science checks,
not audience testing.

Source `6f7ce844d926ad931e791c7304cfb775f0424eb1` was committed and pushed to
main, then successfully published by
[Pages run 37262740315](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37262740315).
The run tested and built that exact source. Live 1440/390/320 px checks also pass
all three endings, mutual exclusion, keyboard/restart focus, homepage discovery,
three projection cards/nine series, observed controls, coupling charts, same-page
anchors, five place pointers and all 16 routes. No horizontal page overflow or
runtime errors. A documentation-only checkpoint records these publication results;
it does not require a different deployed build.

Public entry points:
[The Usual Table](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/glass-city-2075/#summer-scene)
and [local projection comparison](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/climate-thermal-regime/#local-projections).

This bounded addition demonstrates a productive connection: the climate study
quantifies broad pressure while the scene makes shade, leisure and neighboring
access matter to people. Whether the characters hold unfamiliar readers' interest
still needs human play; agent continuity review cannot establish it. Favor that
small test before adding another scene or enlarging the game.

## Changed paths

Modified:

```text
PROJECT_STATUS.md
README.md
data/climate/README.md
data/climate/indicators.json
reports/README.md
reports/climate_integration_2026-10-05.md
reports/current_phase_handoff.md
src/atlas/climate-study.test.ts
src/atlas/climate-study.ts
src/atlas/main.ts
src/atlas/style.css
src/python/climate/build_climate_indicators.py
stories/README.md
tests/test_climate_indicators.py
```

Added:

```text
assets/atlas/glass-city-summer/README.md
assets/atlas/glass-city-summer/manifest.json
assets/atlas/glass-city-summer/source_png.zip
assets/atlas/glass-city-summer/the_usual_table.webp
data/climate/local_projections.json
data/climate/projection_source_manifest.json
data/climate/sources/cris_county_item.json
data/climate/sources/cris_future_schema.json
data/climate/sources/cris_historical_schema.json
data/climate/sources/cris_lucas_future.json
data/climate/sources/cris_lucas_historical.json
reports/glass_city_summer_and_local_climate_2026-10-05.md
src/atlas/glass-city-summer.test.ts
src/atlas/glass-city-summer.ts
src/python/climate/extract_local_projections.py
stories/the_usual_table.md
```

No files removed; no accepted images regenerated or replaced. Temporary fetch,
browser and review helpers remain ignored under `temp/climate-integration/`.

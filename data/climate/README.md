# Western Basin climate indicators

Small observed-history dataset for the [Climate & Thermal Regime study](../../atlas/climate-thermal-regime/index.html).
It is separate from the Model Lab, the retained Waterville record and frozen
Phase 9 products. It supplies no empirical nutrient model, exact future street temperature,
heat-health warning, intake diagnosis or street-level exposure estimate.

## Contents and reproducibility

- [indicators.json](indicators.json): five indicator families, coverage, definitions,
  official normals and future extraction metadata.
- [source_manifest.json](source_manifest.json): original URLs, UTC retrieval times,
  SHA256 hashes of downloaded and stored bytes. NOAA snapshots total about 750 KB.
- `sources/`: unmodified NOAA source bytes; GHCN-Daily is losslessly gzip-compressed.
- [Builder](../../src/python/climate/build_climate_indicators.py): Python standard
  library only, no network requests. From repository root:

```sh
python src/python/climate/build_climate_indicators.py
python -m unittest discover -s tests -p test_climate_indicators.py
```

Rebuilding checks every source hash first and writes deterministic JSON. To refresh,
download the manifest URLs deliberately, retain the new hashes/retrieval times,
review coverage and update the edition/window explicitly. The bundled source
snapshots contain records into 2026; indicators deliberately end in 2025. The web
page bundles JSON and makes no live climate-data requests.

Retain NOAA attribution and source terms; the repository's MIT license does not
replace third-party data terms. [Project licensing notes](../../docs/references/DATA_AND_ASSET_LICENSING.md).

## Measurement boundaries

**Station:** NOAA `USW00094830`, Toledo Express Airport, 41.5886° N / 83.8014° W.
Frozen climate work used Toledo Executive / KTDZ; these stations must not be spliced.

**Official normals:** NOAA 1991–2020 annual mean 52.2°F, ≥90°F days 18.7/year,
65°F-base cooling degree-days 1,018.8°F·days/year. Selected annual completeness
flags are `S` (standard normal), with 30 years. The CSV annual hot-day normal is
18.7; adding separately rounded monthly values gives 18.8. The annual CSV is used.

**Daily history:** GHCN daily TMAX/TMIN, native integer tenths °C. Reject missing
`-9999` and nonblank quality flags. Measurement and source flags remain in the raw
file. No infilling or homogenization is performed here. Annual daily midpoint is
the mean of `(TMAX + TMIN)/2`, not NOAA's adjusted normal TAVG. Only years with all
paired days have annual indicator values. 2024 and 2025 are incomplete in this
snapshot; counts of valid days remain visible, annual statistics are `null`.

Nominal 90°F and 70°F thresholds are quantized to 322 and 211 tenths °C. Comparing
with exact 32.222…°C would wrongly exclude source values reported as 90°F.
Warm nights use daily minima, not hourly overnight exposure. A hot spell is at
least three consecutive qualifying daily maxima; missing days break runs and
runs split at calendar-year boundaries. Intensity is the highest event-average
TMAX; a missing event intensity is `null`, never zero. Humidity/apparent temperature
and occupational WBGT are not available in this set.

**Lake:** NOAA GLSEA daily whole-Erie surface analysis, 1995–2025, annual and
June–August means. Calendar dates follow day-of-year, including leap years;
blank non-leap day 366 is ignored. Complete 92-day summers and full calendar
years alone receive means. Satellite imagery and smoothing do not constitute
direct field visits at every location/day. No depth, oxygen or HAB result is inferred.

**Ice:** NOAA GLERL annual maximum Lake Erie coverage, 1973–2025. This is neither
winter mean nor ice duration. High-ice years remain possible amid long-term change.

## Readiness gaps

The current GLISA page lists a 50.8°F mean and 14.6 days *exceeding* 90°F for the
same station and normal period. Its processing and strict threshold differ; the
mean discrepancy remains unresolved. Use the official NOAA normal here; do not
average or silently merge them. Neighborhood sensors, humidity, solar/radiant
exposure, building conditions, air quality, cooling access and actual electricity
peaks need separate datasets.

A [first Lucas County projection sample](local_projections.json) is now available:
three published CRIS LOCA2-derived model series, all three SSPs, 2061–2090 versus
modeled 1991–2020. [Query snapshots and hashes](projection_source_manifest.json)
retain NOAA/Esri CC BY4.0 attribution. Rebuild offline:

```sh
python src/python/climate/extract_local_projections.py
```

Add `--fetch` only for a deliberate source refresh. The extractor validates
coverage and joins each pathway's modeled baseline before calculating change.
The sample is county-scale, not an individual CMIP6 realization or full ensemble
uncertainty range. Member IDs/upstream release are not exposed; calendar/grid
resampling details remain provider-side limitations. Cooling degree-days are not
electricity demand. [Calculation and boundaries](../../reports/glass_city_summer_and_local_climate_2026-10-05.md).

Full model/member and GLARM lake extraction remain pending. Published GLISA regional
ranges use different windows and baseline; RCP and SSP products are not pooled. See the
[evidence/readiness report](../../reports/climate_integration_2026-10-05.md).

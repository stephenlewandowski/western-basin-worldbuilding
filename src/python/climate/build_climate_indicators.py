"""Rebuild the small Atlas climate dataset from retained NOAA snapshots (no network).

GHCN-Daily: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
No imputation, trend fitting, climate projection or Model Lab calculation occurs here.
"""
from pathlib import Path
from datetime import date, timedelta
import calendar
import csv
import gzip
import hashlib
import json
from statistics import mean

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / 'data/climate/sources'


def parse_station(text, first=1991, last=2025):
    days = {}
    for line in text.splitlines():
        element = line[17:21]
        if element not in ('TMAX', 'TMIN'):
            continue
        year, month = int(line[11:15]), int(line[15:17])
        if not first <= year <= last:
            continue
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            block = line[21 + (day - 1) * 8:29 + (day - 1) * 8]
            value, quality = int(block[:5]), block[6]
            # Measurement/source flags remain in the original snapshot. Only a
            # blank quality flag and a non-missing value enter the indicator.
            days.setdefault(date(year, month, day), {})[element] = (
                value if value != -9999 and quality == ' ' else None)
    return days


def hot_spells(values):
    runs, run = [], []
    for value in [*values, None]:
        if value is not None and value >= 322:
            run.append(value)
        else:
            if len(run) >= 3:
                runs.append(run)
            run = []
    return {
        'hot_spell_events': len(runs),
        'hot_spell_days': sum(map(len, runs)),
        'longest_hot_spell_days': max(map(len, runs), default=0),
        'hottest_spell_mean_max_c': round(max((mean(r) / 10 for r in runs), default=0), 2) if runs else None,
    }


def air_year(days, year):
    expected = 366 if calendar.isleap(year) else 365
    records = [days.get(date(year, 1, 1) + timedelta(days=i), {}) for i in range(expected)]
    maxima = [r.get('TMAX') for r in records]
    minima = [r.get('TMIN') for r in records]
    paired = [(hi, lo) for hi, lo in zip(maxima, minima) if hi is not None and lo is not None]
    complete = len(paired) == expected
    return {'year': year, 'expected_days': expected,
            'valid_tmax_days': sum(v is not None for v in maxima),
            'valid_tmin_days': sum(v is not None for v in minima),
            'paired_days': len(paired), 'complete': complete,
            'mean_daily_midpoint_c': round(mean((hi + lo) / 20 for hi, lo in paired), 3) if complete else None,
            'hot_days': sum(v >= 322 for v in maxima if v is not None) if complete else None,
            'warm_nights': sum(v >= 211 for v in minima if v is not None) if complete else None,
            **(hot_spells(maxima) if complete else {key: None for key in hot_spells([])})}


def build():
    manifest = json.loads((ROOT/'data/climate/source_manifest.json').read_text())
    for source in manifest['sources']:
        stored = (ROOT/source['file']).read_bytes()
        assert hashlib.sha256(stored).hexdigest() == source['stored_sha256'], source['file']
        raw = gzip.decompress(stored) if source['file'].endswith('.gz') else stored
        assert hashlib.sha256(raw).hexdigest() == source['source_sha256'], source['file']
    days = parse_station(gzip.decompress((SOURCES/'toledo_express_ghcnd.dly.gz').read_bytes()).decode('ascii'))
    air = [air_year(days, year) for year in range(1991, 2026)]
    with (SOURCES/'toledo_express_normals_annual.csv').open(newline='') as f:
        normal = next(csv.DictReader(f))
    with (SOURCES/'toledo_express_normals_monthly.csv').open(newline='') as f:
        monthly = list(csv.DictReader(f))
    keys = {'mean_air_f': 'ANN-TAVG-NORMAL', 'hot_days': 'ANN-TMAX-AVGNDS-GRTH090',
            'cooling_degree_days_f65': 'ANN-CLDD-NORMAL'}
    official = {name: {'value': float(normal[key]), 'source_field': key,
                       'completeness_flag': normal['comp_flag_'+key], 'years': int(normal['years_'+key])}
                for name, key in keys.items()}
    with (SOURCES/'erie_glsea_daily.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    lake = []
    for year in range(1995, 2026):
        expected = 366 if calendar.isleap(year) else 365
        values = [(date(year, 1, 1) + timedelta(days=int(r['']) - 1), float(r[str(year)]))
                  for r in rows if r[str(year)].strip() and int(r['']) <= expected]
        summer = [v for d, v in values if d.month in (6, 7, 8)]
        lake.append({'year': year, 'valid_days': len(values), 'summer_days': len(summer),
                     'annual_mean_c': round(mean(v for _, v in values), 4) if len(values) == expected else None,
                     'summer_mean_c': round(mean(summer), 4) if len(summer) == 92 else None})
    ice_rows = (SOURCES/'great_lakes_annual_max_ice.txt').read_text().splitlines()
    header = ice_rows[0].split()
    ice = [{'year': int(r['year']), 'maximum_percent': float(r['eri'])}
           for line in ice_rows[1:] if line.strip()
           for r in [dict(zip(header, line.split()))] if int(r['year']) <= 2025]
    baseline = [r for r in air if r['year'] <= 2020]
    assert all(r['complete'] for r in baseline)
    result = {
        'schema_version': '1.0', 'edition': '2026-10-05', 'last_calendar_year': 2025,
        'status': 'Observed-history study prototype; not a climate forecast or Model Lab output',
        'sources_manifest': 'data/climate/source_manifest.json',
        'indicator_metadata': {
            'air': {'unit': 'degC', 'statistic': 'annual mean daily midpoint', 'period': [1991,2025],
                    'geography': 'USW00094830 station', 'source_files': ['toledo_express_ghcnd.dly.gz'],
                    'minimum_paired_coverage': 1.0},
            'hot_days': {'unit': 'days/year', 'threshold_native_tenths_c': 322, 'operator': '>=',
                         'element': 'TMAX', 'period': [1991,2025], 'geography': 'USW00094830 station',
                         'source_files': ['toledo_express_ghcnd.dly.gz']},
            'warm_nights': {'unit': 'days/year', 'threshold_native_tenths_c': 211, 'operator': '>=',
                            'element': 'TMIN', 'period': [1991,2025], 'geography': 'USW00094830 station',
                            'source_files': ['toledo_express_ghcnd.dly.gz']},
            'hot_spells': {'duration_unit': 'days', 'intensity_unit': 'degC', 'minimum_consecutive_days': 3,
                           'threshold_native_tenths_c': 322, 'operator': '>=', 'element': 'TMAX',
                           'period': [1991,2025], 'geography': 'USW00094830 station',
                           'source_files': ['toledo_express_ghcnd.dly.gz']},
            'lake_surface': {'unit': 'degC', 'statistic': 'mean of daily lake-average surface analyses',
                             'period': [1995,2025], 'summer_months': [6,7,8], 'geography': 'whole Lake Erie',
                             'source_files': ['erie_glsea_daily.csv'], 'minimum_daily_coverage': 1.0},
            'ice': {'unit': 'percent', 'statistic': 'annual maximum areal coverage', 'period': [1973,2025],
                    'geography': 'whole Lake Erie', 'source_files': ['great_lakes_annual_max_ice.txt']},
        },
        'station': {'id': 'USW00094830', 'name': normal['NAME'], 'latitude': float(normal['LATITUDE']),
                    'longitude': float(normal['LONGITUDE']), 'scope': 'Toledo Express airport station; not urban exposure',
                    'different_from_frozen_station': 'KTDZ / Toledo Executive Airport'},
        'definitions': {
            'mean_daily_midpoint_c': 'Arithmetic annual mean of (TMAX+TMIN)/2; complete paired years only. Not official normal TAVG.',
            'hot_days': 'TMAX >=32.2 C (322 tenths C), the quantized GHCN equivalent of reported 90 F; annual complete years only.',
            'warm_nights': 'TMIN >=21.1 C (211 tenths C), quantized reported 70 F; daily-minimum proxy, not hourly night exposure.',
            'hot_spells': 'At least 3 consecutive calendar days TMAX >=32.2 C; runs split at year boundaries; missing values break runs. Project definition, not a heat-index warning.',
            'hottest_spell_mean_max_c': 'Highest event-average daily TMAX among qualifying hot spells; duration and intensity are separate.',
            'lake_temperature': 'GLSEA satellite-derived, spatially averaged whole-Lake Erie surface analysis; annual and June-August daily means. No depth/oxygen inference.',
            'ice': 'Whole-Lake Erie annual maximum percent coverage. Not seasonal mean, ice duration or western-basin-only extent.',
            'quality': 'GHCN missing -9999 or nonblank QFLAG excluded; no infilling. Incomplete annual indicators are null; coverage counts retained.',
        },
        'official_normals_1991_2020': official,
        'monthly_mean_normals_f': [{'month': int(r['month']), 'value': float(r['MLY-TAVG-NORMAL'])} for r in monthly],
        'derived_baseline_1991_2020': {key: round(mean(r[key] for r in baseline), 4)
                                      for key in ('hot_days','warm_nights','hot_spell_events','hot_spell_days')},
        'air': air, 'lake_surface': lake, 'ice': ice,
        'future_scenarios': {
            'target_window': [2061, 2090], 'label': '2075-centered climatological window',
            'local_projected_values': None, 'readiness': 'Extraction not performed; no exact local 2075 temperature is supplied.',
            'air_candidate': {'product': 'LOCA2 CMIP6', 'models': 27, 'grid_km': 6, 'paths': ['SSP2-4.5','SSP3-7.0','SSP5-8.5'],
                              'baseline': [1991,2020], 'url': 'https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023/'},
            'lake_candidate': {'product': 'GLARM-Proj1', 'models': ['GISS','IPSL','MPI'], 'paths': ['RCP4.5','RCP8.5'],
                               'baseline': [2000,2019], 'url': 'https://digitalcommons.mtu.edu/glts/'},
            'regional_air_context': {'source': 'GLISA October 2024 regional synthesis; UW-Madison RegCM4 downscaling',
                'url': 'https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf',
                'baseline': [1980,1999], 'midcentury': {'window': [2040,2059], 'warming_f_range': [3,6]},
                'latecentury': {'window': [2080,2099], 'warming_f_range': [6,11]},
                'limit': 'Rounded regional published ranges; not local quantiles, not SSP-specific values, not interpolated to 2075.'},
        },
    }
    out = ROOT/'data/climate/indicators.json'
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(f'Built {len(air)} air years, {len(lake)} lake years, {len(ice)} ice years; {out}')
    print('Incomplete air years:', [r['year'] for r in air if not r['complete']])


if __name__ == '__main__':
    build()

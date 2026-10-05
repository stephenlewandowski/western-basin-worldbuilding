"""Scientific guards for incomplete records, quantized thresholds and hot spells."""
import importlib.util
from pathlib import Path
from datetime import date, timedelta
import unittest

spec = importlib.util.spec_from_file_location('climate', Path(__file__).resolve().parents[1]/'src/python/climate/build_climate_indicators.py')
climate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(climate)
projection_spec = importlib.util.spec_from_file_location('projection', Path(__file__).resolve().parents[1]/'src/python/climate/extract_local_projections.py')
projection = importlib.util.module_from_spec(projection_spec)
projection_spec.loader.exec_module(projection)


class ClimateTests(unittest.TestCase):
    def test_threshold_and_missing_spell_boundary(self):
        result = climate.hot_spells([321, 322, 322, 330, None, 400, 400, 321])
        self.assertEqual(result['hot_spell_events'], 1)
        self.assertEqual(result['longest_hot_spell_days'], 3)
        self.assertEqual(result['hot_spell_days'], 3)
        self.assertAlmostEqual(result['hottest_spell_mean_max_c'], 32.47)

    def test_missing_day_withholds_annual_counts(self):
        days = {date(2023, 1, 1)+timedelta(days=i): {'TMAX': 322, 'TMIN': 211} for i in range(365)}
        full = climate.air_year(days, 2023)
        self.assertEqual(full['hot_days'], 365)
        self.assertEqual(full['warm_nights'], 365)
        days[date(2023, 6, 1)]['TMIN'] = None
        partial = climate.air_year(days, 2023)
        self.assertFalse(partial['complete'])
        self.assertEqual(partial['paired_days'], 364)
        self.assertIsNone(partial['hot_days'])
        self.assertIsNone(partial['mean_daily_midpoint_c'])

    def test_quality_flag_rejected_source_flag_retained(self):
        block = lambda value, q=' ': f'{value:5d} {q}0'
        line = 'USW00094830'+'202301'+'TMAX'+block(322)+block(400,'X')+block(-9999)+block(0)*28
        days = climate.parse_station(line)
        self.assertEqual(days[date(2023, 1, 1)]['TMAX'], 322)
        self.assertIsNone(days[date(2023, 1, 2)]['TMAX'])
        self.assertIsNone(days[date(2023, 1, 3)]['TMAX'])

    def test_leap_day_is_required(self):
        days = {date(2020, 1, 1)+timedelta(days=i): {'TMAX': 100, 'TMIN': 0} for i in range(366)}
        self.assertEqual(climate.air_year(days, 2020)['expected_days'], 366)
        del days[date(2020, 2, 29)]
        self.assertFalse(climate.air_year(days, 2020)['complete'])

    def test_projection_baseline_joins_the_matching_path_and_converts_delta(self):
        historical=[{'MODEL':m,'YEAR':y,**{f:50 for f in projection.FIELDS}} for m in projection.MODELS for y in range(1991,2015)]
        future=[{'MODEL':m,'YEAR':y,**{f'{f}_{p}':(60+i*10 if y<=2020 else 90) for f in projection.FIELDS for i,p in enumerate(projection.PATHS)}} for m in projection.MODELS for y in [*range(2015,2021),*range(2061,2091)]]
        result=projection.summarize(historical,future)
        metric=result[0]['series'][0]['metrics']['annual_temperature']
        self.assertEqual(metric['baseline'],52)
        self.assertEqual(metric['change'],38)
        self.assertAlmostEqual(metric['change_c'],38*5/9,places=3)
        self.assertEqual(result[1]['series'][0]['metrics']['annual_temperature']['baseline'],54)

    def test_projection_rejects_a_missing_year(self):
        with self.assertRaises(AssertionError):
            projection.summarize([],[])


if __name__ == '__main__':
    unittest.main()

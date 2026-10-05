"""Scientific guards for incomplete records, quantized thresholds and hot spells."""
import importlib.util
from pathlib import Path
from datetime import date, timedelta
import unittest

spec = importlib.util.spec_from_file_location('climate', Path(__file__).resolve().parents[1]/'src/python/climate/build_climate_indicators.py')
climate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(climate)


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


if __name__ == '__main__':
    unittest.main()

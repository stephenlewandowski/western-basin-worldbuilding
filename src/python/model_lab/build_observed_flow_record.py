"""Extract a retained USGS record for display, separately from routed Model Lab runs.

No network access, imputation, unit conversion or model execution. Run before
src/R/model_lab/build_observed_flow_card.R. Source flags remain snapshot flags.
"""
import csv
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/climate_hazards/usgs_maumee_waterville_daily_flow_2025_2026.json'
DEST = ROOT / 'outputs/model_lab/observations'


def main():
    assert hashlib.sha256(RAW.read_bytes().replace(b'\r\n', b'\n')).hexdigest() == (
        'a2b206f85f313368e5bcb743dca6241a4bcbea37676a88176348802f42cd93f6'
    ), 'Retained source changed; review date, flags and provenance before rebuilding'
    snapshot = json.loads(RAW.read_text(encoding='utf-8'))
    matches = [s for s in snapshot['value']['timeSeries']
               if any(c['value'] == '04193500' for c in s['sourceInfo']['siteCode'])
               and any(c['value'] == '00060' for c in s['variable']['variableCode'])
               and any(o.get('optionCode') == '00003' for o in s['variable']['options']['option'])]
    assert len(matches) == 1, 'Expected one daily-mean discharge series'
    series = matches[0]
    assert series['variable']['unit']['unitCode'] == 'ft3/s'
    records = sorted([r for block in series['values'] for r in block['value']
                      if '2025-01-01' <= r['dateTime'][:10] <= '2025-12-31'],
                     key=lambda r: r['dateTime'])
    expected = [(date(2025, 1, 1) + timedelta(days=i)).isoformat() for i in range(365)]
    assert [r['dateTime'][:10] for r in records] == expected, 'Missing or duplicate day'
    for row in records:
        flow = float(row['value'])
        flags = set(row['qualifiers'])
        assert math.isfinite(flow) and flow >= 0
        assert flags <= {'A', 'P', 'e'} and len(flags & {'A', 'P'}) == 1
    counts = {q: sum(q in r['qualifiers'] for r in records) for q in ('A', 'P', 'e')}
    assert counts == {'A': 322, 'P': 43, 'e': 13}, 'Retained snapshot changed; review before rebuilding'
    DEST.mkdir(parents=True, exist_ok=True)
    csv_path = DEST / 'waterville_daily_flow_2025.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out, lineterminator='\n')
        writer.writerow(['date', 'daily_mean_discharge_ft3_s', 'approval_in_snapshot', 'estimated', 'source_qualifiers'])
        for row in records:
            flags = row['qualifiers']
            writer.writerow([row['dateTime'][:10], row['value'],
                             'approved' if 'A' in flags else 'provisional',
                             'true' if 'e' in flags else 'false', '|'.join(flags)])
    record = {
        'product': 'Observed-flow display; not a routed Model Lab case',
        'source': str(RAW.relative_to(ROOT)).replace('\\', '/'),
        'source_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
        'source_sha256_lf': hashlib.sha256(RAW.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'source_url': 'https://waterdata.usgs.gov/monitoring-location/04193500/',
        'retrieved_at': '2026-09-03T08:24:06Z',
        'station': '04193500', 'parameter': '00060', 'statistic': '00003', 'units': 'ft3/s',
        'period': ['2025-01-01', '2025-12-31'], 'days': 365,
        'flags_in_snapshot': counts, 'estimated_overlaps_approval': True,
        'csv_sha256': hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        'operations': 'Calendar-day selection, sorting and flag extraction only',
        'limits': 'One gauge; no HUC-local inputs, nutrient loads, flood extent or prediction',
        'credit': 'U.S. Geological Survey; source terms apply',
    }
    (DEST / 'waterville_observation_manifest.json').write_text(
        json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Exported 365 observed daily means; snapshot flags {counts}.')


if __name__ == '__main__':
    main()

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { cubicFeetToCubicMetres, flowDayIndex, flowDays, highFlowIndex, lowFlowIndex } from './observed-flow';
import map from '../../assets/atlas/region/region_explorer.json';

describe('retained observation bridge', () => {
  it('keeps every original daily value and qualifier rather than interpolating or changing approval', () => {
    const csv = readFileSync(new URL('../../outputs/model_lab/observations/waterville_daily_flow_2025.csv', import.meta.url), 'utf8').trim().split(/\r?\n/).slice(1);
    expect(flowDays).toHaveLength(365);
    const expected = csv.map(line => {
      const [date, flow, approval, estimated, qualifiers] = line.split(',');
      return { date, flow: Number(flow), approval, estimated: estimated === 'true', qualifiers };
    });
    expect(flowDays).toEqual(expected);
    for (let index = 0; index < 365; index++) {
      expect(flowDays[index].date).toBe(new Date(Date.UTC(2025, 0, index + 1)).toISOString().slice(0, 10));
    }
    expect(flowDays.filter(day => day.approval === 'provisional')).toHaveLength(43);
    expect(flowDays.filter(day => day.estimated && day.approval === 'approved')).toHaveLength(13);
  });

  it('converts volumes dimensionally while retaining the source quantity', () => {
    expect(cubicFeetToCubicMetres(1)).toBeCloseTo(0.3048 ** 3, 14);
    expect(cubicFeetToCubicMetres(68200)).toBeCloseTo(1931.2089375744, 8);
    expect(cubicFeetToCubicMetres(65)).toBeCloseTo(1.84059502848, 10);
  });

  it('finds only the retained year’s daily extremes and rejects missing dates', () => {
    expect(flowDays[highFlowIndex]).toMatchObject({ date: '2025-04-04', flow: 68200 });
    expect(flowDays[lowFlowIndex]).toMatchObject({ date: '2025-10-25', flow: 65 });
    expect(flowDays[flowDayIndex('2025-11-19')].approval).toBe('provisional');
    expect(flowDayIndex('2026-06-01')).toBe(-1);
    expect(flowDayIndex('2025-02-29')).toBe(-1);
  });

  it('preserves physical anchors distinct from the legacy intake-monitor coordinate', () => {
    expect(map.landmarks.find(place => place.id === 'crib')).toMatchObject({ longitude: -83.259167, latitude: 41.699444, kind: 'structure' });
    expect(map.landmarks.find(place => place.id === 'waterville')).toMatchObject({ longitude: -83.7127145, latitude: 41.5000526, kind: 'gauge' });
    expect(map.landmarks.find(place => place.id === 'toledo')).toMatchObject({ longitude: -83.5818608, latitude: 41.664071, kind: 'municipality' });
    expect(map.basins).toHaveLength(7);
    expect(map.landmarks.every(place => Number.isFinite(place.x) && Number.isFinite(place.y))).toBe(true);
  });
});

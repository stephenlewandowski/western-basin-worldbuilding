import { describe, it, expect } from 'vitest';
import { climateIndicators as data, climateStudy } from './climate-study';
import { connectionCharts } from './connection-data';

describe('climate evidence boundaries', () => {
  it('withholds incomplete annual air indicators rather than treating missing days as cool', () => {
    for (const row of data.air) {
      expect(row.complete).toBe(row.paired_days === row.expected_days);
      if (!row.complete) for (const key of ['hot_days','warm_nights','longest_hot_spell_days','mean_daily_midpoint_c'] as const) expect(row[key]).toBeNull();
    }
    expect(data.air.filter(r=>!r.complete).map(r=>r.year)).toEqual([2024,2025]);
  });
  it('agrees with independently verified NOAA baselines and lake snapshots', () => {
    expect(data.official_normals_1991_2020.mean_air_f.value).toBe(52.2);
    expect(data.official_normals_1991_2020.hot_days.value).toBe(18.7);
    expect(data.derived_baseline_1991_2020.warm_nights).toBeCloseTo(10.1667,4);
    expect(data.lake_surface.find(r=>r.year===2025)?.summer_mean_c).toBeCloseTo(22.3789,4);
    expect(data.ice.find(r=>r.year===2025)?.maximum_percent).toBe(95.8);
    expect(data.air.find(r=>r.year===2012)?.longest_hot_spell_days).toBe(10);
  });
  it('keeps scenarios unextracted and pathway products distinct', () => {
    expect(data.future_scenarios.local_projected_values).toBeNull();
    expect(data.future_scenarios.target_window).toEqual([2061,2090]);
    expect(data.future_scenarios.air_candidate.paths.every(p=>p.startsWith('SSP'))).toBe(true);
    expect(data.future_scenarios.lake_candidate.paths.every(p=>p.startsWith('RCP'))).toBe(true);
    const html=climateStudy();
    expect(html).toContain('not yet extracted');
    expect(html).toContain('not a live warning service');
  });
  it('keeps other lake controls and pollution drivers alongside heat', () => {
    const lake=connectionCharts.climate.find(c=>c.id==='winter-lake-thermal')!;
    expect(lake.edges.filter(e=>e.to==='ecology').map(e=>e.from).sort()).toEqual(['measure','oxygen','structure']);
    expect(lake.edges.some(e=>e.from==='winter' && e.to==='ecology')).toBe(false);
    const air=connectionCharts.climate.find(c=>c.id==='heat-air-ventilation')!;
    expect(air.edges.filter(e=>e.to==='air').map(e=>e.from).sort()).toEqual(['heat','sources']);
    expect(connectionCharts.climate.flatMap(c=>c.edges).some(e=>e.kind==='flow')).toBe(false);
  });
});

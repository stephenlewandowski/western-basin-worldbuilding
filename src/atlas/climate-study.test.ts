import { describe, it, expect } from 'vitest';
import { climateIndicators as data, localClimateProjections as projections, climateStudy } from './climate-study';
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
  it('keeps the county sample separate from observations and lake candidates', () => {
    expect(data.future_scenarios.local_projected_values?.geography).toBe('Lucas County, Ohio');
    expect(data.future_scenarios.target_window).toEqual([2061,2090]);
    expect(data.future_scenarios.air_candidate.paths.every(p=>p.startsWith('SSP'))).toBe(true);
    expect(data.future_scenarios.lake_candidate.paths.every(p=>p.startsWith('RCP'))).toBe(true);
    const html=climateStudy();
    expect(html).toContain('three-series sample range');
    expect(html).toContain('Individual realization IDs');
    expect(html).toContain('not a live warning service');
  });
  it('uses matched windows and three distinct model series per pathway', () => {
    expect(projections.windows.baseline).toEqual([1991,2020]);
    expect(projections.windows.future).toEqual([2061,2090]);
    for(const scenario of projections.scenarios){
      expect(new Set(scenario.series.map(r=>r.model)).size).toBe(3);
      expect(scenario.series.every(r=>r.baseline_years===30 && r.future_years===30)).toBe(true);
      for(const r of scenario.series) expect(r.metrics.annual_temperature.change_c).toBeCloseTo(r.metrics.annual_temperature.change*5/9,3);
    }
    expect(projections.scenarios[0].summary.annual_temperature.change_c.mean).toBeCloseTo(2.5812,4);
    expect(projections.scenarios[2].summary.hot_days.future.mean).toBeCloseTo(70.2336,4);
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

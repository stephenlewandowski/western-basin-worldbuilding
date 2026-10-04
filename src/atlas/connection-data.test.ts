import { readFileSync, existsSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { connectionCharts, type ConnectionChart } from './connection-data';

describe('source-grounded connection charts', () => {
  it('has valid, distinct endpoints and a retained source for every chart', () => {
    const charts = Object.values(connectionCharts).flat();
    expect(new Set(charts.map(chart => chart.id)).size).toBe(charts.length);
    for (const chart of charts) {
      const ids = new Set(chart.nodes.map(node => node.id));
      expect(ids.size).toBe(chart.nodes.length);
      expect(existsSync(chart.source)).toBe(true);
      for (const edge of chart.edges) {
        expect(ids.has(edge.from) && ids.has(edge.to)).toBe(true);
        expect(edge.from).not.toBe(edge.to);
      }
    }
  });

  it('keeps exactly the constituent/process membership in the retained CSV', () => {
    const rows = readFileSync('outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_constituent_process_matrix.csv', 'utf8').trim().split(/\r?\n/).slice(1);
    const chart = connectionCharts.field.find(chart => chart.id === 'constituent-processes')!;
    const normalize = (text: string) => text.toLowerCase().replace('receiving-water response/context', 'receiving-water context');
    rows.forEach((row, i) => {
      const expected = row.split(',')[1].split(';').map(normalize).sort();
      const actual = chart.edges.filter(edge => edge.from === `track-${i}`).map(edge => normalize(chart.nodes.find(node => node.id === edge.to)!.title)).sort();
      expect(actual).toEqual(expected);
    });
    expect(chart.edges.every(edge => edge.kind === 'membership')).toBe(true);
  });

  it('keeps the receiving-water interaction before possible bloom conditions', () => {
    const chart = connectionCharts.field.find(chart => chart.id === 'lake-boundary')!;
    expect(chart.edges.filter(edge => edge.to === 'favorable').map(edge => edge.from)).toEqual(['interaction']);
    expect(chart.edges.find(edge => edge.to === 'favorable')!.kind).toBe('possible');
  });

  it('cannot bypass qualification on either residual-to-input route', () => {
    const chart = connectionCharts.industry.find(chart => chart.id === 'residual-qualification')!;
    const reachable = (chart: ConnectionChart, start: string, excluded: string): Set<string> => {
      const visited = new Set([start]), pending = [start];
      while (pending.length) {
        const id = pending.pop()!;
        for (const edge of chart.edges.filter(edge => edge.from === id && edge.to !== excluded)) {
          if (!visited.has(edge.to)) { visited.add(edge.to); pending.push(edge.to); }
        }
      }
      return visited;
    };
    expect(reachable(chart, 'heat', 'heat-qualify').has('heat-use')).toBe(false);
    expect(reachable(chart, 'residual', 'material-qualify').has('material-use')).toBe(false);
    for (const node of chart.nodes.filter(node => !['exit', 'support'].includes(node.id))) {
      expect(chart.edges.some(edge => edge.from === node.id && edge.to === 'exit')).toBe(true);
    }
  });

  it('keeps compute grid-mediated and fusion/heat recovery conditional', () => {
    const chart = connectionCharts.coast[0];
    expect(chart.edges.filter(edge => edge.to === 'compute').map(edge => edge.from)).toEqual(['grid']);
    expect(chart.edges.find(edge => edge.from === 'fusion' && edge.to === 'grid')!.kind).toBe('possible');
    expect(chart.edges.find(edge => edge.to === 'heat-use')!.kind).toBe('possible');
    expect(chart.edges.find(edge => edge.to === 'destination')!.kind).toBe('possible');
    expect(chart.edges.some(edge => edge.from === 'fuel' && edge.to === 'custody')).toBe(true);
  });
});

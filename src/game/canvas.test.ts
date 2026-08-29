import { describe, expect, it } from 'vitest';
import { toLogicalPoint } from './canvas';

describe('canvas coordinate conversion', () => {
  it('maps the displayed canvas center to the logical 320x200 center', () => {
    expect(toLogicalPoint(410, 270, { left: 10, top: 20, width: 800, height: 500 })).toEqual({ x: 160, y: 100 });
  });

  it('maps the displayed canvas edges to logical room edges', () => {
    expect(toLogicalPoint(100, 50, { left: 100, top: 50, width: 640, height: 400 })).toEqual({ x: 0, y: 0 });
    expect(toLogicalPoint(740, 450, { left: 100, top: 50, width: 640, height: 400 })).toEqual({ x: 320, y: 200 });
  });
});

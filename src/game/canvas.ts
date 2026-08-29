export const LOGICAL_WIDTH = 320;
export const LOGICAL_HEIGHT = 200;
export const BACKING_SCALE = 2;
export const BACKING_WIDTH = LOGICAL_WIDTH * BACKING_SCALE;
export const BACKING_HEIGHT = LOGICAL_HEIGHT * BACKING_SCALE;

export interface CanvasBounds {
  left: number;
  top: number;
  width: number;
  height: number;
}

export interface LogicalPoint {
  x: number;
  y: number;
}

export function toLogicalPoint(clientX: number, clientY: number, bounds: CanvasBounds): LogicalPoint {
  return {
    x: ((clientX - bounds.left) / bounds.width) * LOGICAL_WIDTH,
    y: ((clientY - bounds.top) / bounds.height) * LOGICAL_HEIGHT,
  };
}

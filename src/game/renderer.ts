import { COLORS, caseEvidenceDefinitions, theories, rooms, type Hotspot, type RoomId } from './data';
import { BACKING_SCALE, LOGICAL_HEIGHT, LOGICAL_WIDTH } from './canvas';
import type { GameState } from './engine';
import { availableCaseEvidence, evaluateCase } from './logic';
import { REVIEW_ACTION_Y, REVIEW_EVIDENCE_Y, REVIEW_THEORY_Y, reviewTargetKey } from './review';

const W = LOGICAL_WIDTH;
const H = LOGICAL_HEIGHT;
const SCENE_HEIGHT = 135;
const PANEL_HEIGHT = H - SCENE_HEIGHT;
const BODY_SIZE = 10;
const SMALL_SIZE = 9;
const BODY_LINE_HEIGHT = 12;

function rect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, color: string, fill = true): void {
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  if (fill) ctx.fillRect(x, y, width, height); else ctx.strokeRect(x, y, width, height);
}

function text(ctx: CanvasRenderingContext2D, value: string, x: number, y: number, color: string = COLORS.white, size = BODY_SIZE): void {
  ctx.fillStyle = color;
  ctx.font = `${size}px "Courier New", monospace`;
  ctx.textBaseline = 'top';
  ctx.fillText(value, x, y);
}

function wrap(ctx: CanvasRenderingContext2D, value: string, x: number, y: number, width: number, color: string = COLORS.white, size = BODY_SIZE, lineHeight = BODY_LINE_HEIGHT, maxLines = Infinity): number {
  ctx.font = `${size}px "Courier New", monospace`;
  const words = value.split(' ');
  let line = '';
  const lines: string[] = [];
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (ctx.measureText(candidate).width > width && line) { lines.push(line); line = word; } else line = candidate;
  }
  if (line) lines.push(line);
  lines.slice(0, maxLines).forEach((entry, index) => {
    if (index === maxLines - 1 && lines.length > maxLines) {
      while (ctx.measureText(`${entry}...`).width > width) entry = entry.slice(0, -1);
      entry += '...';
    }
    text(ctx, entry, x, y + index * lineHeight, color, size);
  });
  return y + Math.min(lines.length, maxLines) * lineHeight;
}

function drawBasin(ctx: CanvasRenderingContext2D, y: number): void {
  // Composite river-edge skyline: regional motifs, not a surveyed location.
  rect(ctx, 30, y + 23, 41, 20, COLORS.magenta, false);
  rect(ctx, 36, y + 16, 29, 6, COLORS.cyan);
  for (let x = 38; x < 65; x += 8) rect(ctx, x, y + 27, 4, 9, COLORS.cyan);
  rect(ctx, 75, y + 3, 7, 40, COLORS.white);
  rect(ctx, 86, y + 25, 37, 18, COLORS.magenta, false);
  rect(ctx, 95, y + 20, 29, 3, COLORS.cyan);
  // Bridge deck, piers and stepped arch.
  rect(ctx, 144, y + 30, 94, 3, COLORS.cyan);
  rect(ctx, 149, y + 33, 5, 11, COLORS.white);
  rect(ctx, 227, y + 33, 5, 11, COLORS.white);
  [[157, 24, 8], [165, 18, 8], [173, 13, 35], [208, 18, 8], [216, 24, 8]].forEach(([x, dy, w]) => rect(ctx, x, y + dy, w, 2, COLORS.magenta));
  for (let x = 164; x < 224; x += 12) rect(ctx, x, y + 20, 1, 10, COLORS.cyan);
  rect(ctx, 257, y + 15, 4, 27, COLORS.white);
  rect(ctx, 253, y + 17, 36, 3, COLORS.magenta);
  rect(ctx, 281, y + 20, 1, 13, COLORS.cyan);
  rect(ctx, 0, y + 45, W, 1, COLORS.cyan);
  [[15, 51, 24], [87, 54, 35], [157, 49, 20], [233, 56, 28], [293, 51, 14]].forEach(([x, dy, w]) => rect(ctx, x, y + dy, w, 1, COLORS.magenta));
  [[129, 4], [246, 0], [290, 8]].forEach(([x, dy]) => {
    rect(ctx, x, y + dy, 3, 1, COLORS.white); rect(ctx, x + 3, y + dy + 1, 2, 1, COLORS.white); rect(ctx, x + 5, y + dy, 3, 1, COLORS.white);
  });
}

function drawWorker(ctx: CanvasRenderingContext2D, x: number, y: number, coat: string): void {
  rect(ctx, x + 4, y, 16, 4, COLORS.white);
  rect(ctx, x + 2, y + 4, 20, 4, COLORS.cyan);
  rect(ctx, x + 6, y + 8, 12, 10, COLORS.white);
  rect(ctx, x + 14, y + 11, 3, 2, COLORS.black);
  rect(ctx, x + 3, y + 18, 19, 24, coat);
  rect(ctx, x, y + 21, 4, 22, COLORS.cyan);
  rect(ctx, x + 22, y + 21, 4, 18, COLORS.cyan);
  rect(ctx, x + 8, y + 22, 4, 3, COLORS.white);
  rect(ctx, x + 4, y + 43, 6, 18, COLORS.white);
  rect(ctx, x + 15, y + 43, 6, 18, COLORS.white);
  rect(ctx, x + 2, y + 61, 9, 4, COLORS.cyan);
  rect(ctx, x + 15, y + 61, 10, 4, COLORS.cyan);
}

function drawTitle(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, H, COLORS.black);
  rect(ctx, 12, 13, 296, 174, COLORS.magenta, false);
  rect(ctx, 17, 18, 286, 164, COLORS.cyan, false);
  drawBasin(ctx, 72);
  text(ctx, 'GLASSPUNK', 91, 30, COLORS.magenta, 18);
  text(ctx, 'BLACKOUT AT VESPER STATION', 88, 55, COLORS.white, 10);
  text(ctx, 'ONE NIGHT. TWO REPAIRS.', 96, 137, COLORS.cyan, SMALL_SIZE);
  text(ctx, 'CLICK OR PRESS ENTER TO BEGIN', 77, 153, COLORS.white, BODY_SIZE);
  text(ctx, 'WESTERN BASIN // 2075', 105, 169, COLORS.magenta, SMALL_SIZE);
}

function drawControlRoom(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 15, W, 3, COLORS.magenta);
  for (let x = 8; x < W; x += 24) rect(ctx, x, 18, 2, 28, COLORS.dim);
  rect(ctx, 4, 35, 25, 99, COLORS.magenta, false);
  rect(ctx, 11, 47, 10, 73, COLORS.magenta, false);
  rect(ctx, 34, 58, 82, 75, COLORS.cyan, false);
  rect(ctx, 42, 69, 23, 15, COLORS.magenta, false);
  rect(ctx, 71, 69, 34, 15, COLORS.cyan, false);
  if (state.panelSolved) { text(ctx, 'ON', 45, 73, COLORS.white, 7); rect(ctx, 77, 73, 22, 7, COLORS.cyan); }
  rect(ctx, 44, 93, 63, 5, COLORS.magenta);
  rect(ctx, 50, 108, 6, 13, COLORS.cyan);
  rect(ctx, 63, 108, 6, 13, COLORS.cyan);
  rect(ctx, 76, 108, 6, 13, COLORS.magenta);
  rect(ctx, 89, 108, 6, 13, COLORS.cyan);
  rect(ctx, 142, 66, 45, 46, COLORS.white, false);
  rect(ctx, 150, 75, 31, 7, COLORS.magenta);
  rect(ctx, 150, 91, 24, 2, COLORS.cyan);
  rect(ctx, 190, 42, 34, 19, COLORS.white, false);
  rect(ctx, 195, 47, 24, 2, COLORS.magenta);
  rect(ctx, 190, 67, 34, 49, COLORS.cyan, false);
  rect(ctx, 195, 75, 24, 25, COLORS.magenta, false);
  rect(ctx, 199, 81, 16, 11, COLORS.white, false);
  rect(ctx, 202, 105, 10, 3, COLORS.cyan);
  drawWorker(ctx, 237, 66, COLORS.magenta);
  rect(ctx, 273, 87, 28, 44, COLORS.cyan, false);
  text(ctx, 'HEAT', 277, 94, COLORS.white, 7);
  rect(ctx, 282, 107, 8, 6, state.pumpRunning ? COLORS.cyan : COLORS.magenta);
  text(ctx, 'MARA', 238, 48, COLORS.cyan, 8);
  text(ctx, 'CONTROL ROOM', 7, 3, COLORS.white, BODY_SIZE);
  text(ctx, state.pumpRunning ? 'DAWN' : state.panelSolved ? '02:15' : '02:13', 271, 3, COLORS.cyan, SMALL_SIZE);
}

function drawCorridor(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 17, W, 3, COLORS.cyan);
  // Local overhead pipe and floor seams replace the distracting full-wall stripes.
  rect(ctx, 34, 25, 235, 3, COLORS.magenta);
  rect(ctx, 178, 28, 3, 36, COLORS.magenta);
  rect(ctx, 31, 127, 72, 1, COLORS.cyan);
  rect(ctx, 184, 128, 84, 1, COLORS.cyan);
  rect(ctx, 4, 35, 25, 99, COLORS.magenta, false);
  rect(ctx, 11, 47, 10, 73, COLORS.magenta, false);
  rect(ctx, 39, 43, 59, 81, COLORS.magenta, false);
  rect(ctx, 48, 54, 41, 53, COLORS.cyan, false);
  rect(ctx, 58, 63, 21, 33, COLORS.magenta, false);
  rect(ctx, 124, 67, 46, 30, COLORS.white, false);
  rect(ctx, 129, 74, 34, 4, COLORS.cyan);
  rect(ctx, 129, 86, 25, 3, COLORS.magenta);
  rect(ctx, 205, 58, 66, 55, COLORS.cyan, false);
  rect(ctx, 212, 66, 52, 35, COLORS.white, false);
  text(ctx, 'BASIN', 220, 69, COLORS.magenta, 7);
  rect(ctx, 220, 81, 31, 1, COLORS.cyan);
  rect(ctx, 230, 76, 1, 19, COLORS.magenta);
  rect(ctx, 251, 79, 5, 5, COLORS.magenta);
  text(ctx, 'FUSE', 49, 110, COLORS.white, 7);
  rect(ctx, 120, 104, 59, 28, COLORS.cyan, false);
  text(ctx, 'PUMP', 133, 108, COLORS.white, 8);
  text(ctx, 'v', 146, 119, COLORS.magenta, 8);
  rect(ctx, 279, 35, 30, 99, COLORS.cyan, false);
  text(ctx, '>', 288, 78, COLORS.white, 10);
  text(ctx, '<', 12, 78, COLORS.white, 10);
  text(ctx, 'MAINTENANCE CORRIDOR', 7, 3, COLORS.white, BODY_SIZE);
}

function drawFurnaceGallery(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 17, W, 3, COLORS.magenta);
  rect(ctx, 17, 32, 100, 102, COLORS.cyan, false);
  rect(ctx, 27, 42, 80, 84, COLORS.magenta, false);
  rect(ctx, 39, 54, 56, 59, COLORS.white, false);
  rect(ctx, 47, 63, 40, 38, COLORS.black);
  rect(ctx, 55, 71, 24, 22, COLORS.magenta, false);
  rect(ctx, 36, 55, 26, 23, COLORS.black); rect(ctx, 36, 55, 26, 23, COLORS.white, false);
  text(ctx, 'TAG', 39, 59, COLORS.cyan, 7);
  rect(ctx, 41, 70, 15, 1, COLORS.magenta);
  rect(ctx, 84, 102, 8, 11, COLORS.cyan); rect(ctx, 80, 107, 5, 4, COLORS.cyan);
  [[108, 74], [111, 79], [108, 84], [113, 89], [111, 94]].forEach(([x, y]) => rect(ctx, x, y, 4, 4, COLORS.magenta));
  rect(ctx, 124, 27, 6, 107, COLORS.dim);
  rect(ctx, 192, 27, 6, 107, COLORS.dim);
  drawWorker(ctx, 148, 66, COLORS.cyan);
  text(ctx, 'NIKO', 148, 48, COLORS.magenta, 8);
  text(ctx, '>', 286, 83, COLORS.white, 10);
  rect(ctx, 271, 36, 38, 98, COLORS.cyan, false);
  rect(ctx, 280, 46, 20, 76, COLORS.magenta, false);
  rect(ctx, 286, 55, 8, 57, COLORS.white, false);
  text(ctx, 'FURNACE GALLERY', 7, 3, COLORS.white, BODY_SIZE);
  text(ctx, state.pumpRunning ? 'DAWN' : 'NIGHT', 271, 3, COLORS.cyan, SMALL_SIZE);
}

function drawPumpHouse(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  text(ctx, 'PUMP HOUSE', 7, 3, COLORS.white);
  rect(ctx, 4, 35, 25, 99, COLORS.magenta, false); text(ctx, '<', 12, 79, COLORS.white);
  rect(ctx, 278, 35, 31, 99, COLORS.cyan, false); text(ctx, '>', 289, 79, COLORS.white);
  rect(ctx, 40, 31, 61, 33, COLORS.white, false);
  text(ctx, 'RETURN', 44, 35, COLORS.magenta, 8); text(ctx, 'BEFORE', 44, 45, COLORS.white, 7); text(ctx, 'START', 44, 54, COLORS.cyan, 7);
  rect(ctx, 48, 88, 110, 42, COLORS.cyan, false);
  for (let x = 56; x < 148; x += 12) rect(ctx, x, 96, 4, 25, COLORS.magenta);
  rect(ctx, 66, 69, 68, 4, COLORS.magenta); rect(ctx, 131, 68, 4, 21, COLORS.magenta);
  rect(ctx, 115, 48, 36, 32, COLORS.cyan, false);
  rect(ctx, 131, 50, 4, 27, COLORS.white); rect(ctx, 119, 62, 29, 4, COLORS.white);
  text(ctx, state.returnOpen ? 'OPEN' : 'SHUT', 155, 60, state.returnOpen ? COLORS.cyan : COLORS.magenta, 7);
  rect(ctx, 159, 108, 42, 4, COLORS.cyan);
  rect(ctx, 202, 56, 51, 57, COLORS.white, false);
  text(ctx, 'PUMP', 212, 64, COLORS.cyan, 8);
  rect(ctx, 220, 82, 15, 8, state.pumpRunning ? COLORS.cyan : COLORS.magenta);
  text(ctx, state.pumpRunning ? 'RUN' : 'STOP', 214, 98, COLORS.white, 7);
  rect(ctx, 159, 117, 96, 13, COLORS.magenta, false);
  text(ctx, 'DISTRICT LOOP', 164, 121, COLORS.white, 7);
}

function drawTerrace(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  text(ctx, 'RIVER TERRACE', 7, 3, COLORS.white);
  text(ctx, state.pumpRunning ? 'FIRST LIGHT' : 'NIGHT LIGHTS', 252, 3, COLORS.cyan, 8);
  drawBasin(ctx, 22);
  rect(ctx, 4, 35, 25, 99, COLORS.magenta, false); text(ctx, '<', 12, 92, COLORS.white);
  // Foreground board and dispatch occupy the same places as their hotspots.
  rect(ctx, 40, 63, 76, 62, COLORS.white, false);
  text(ctx, 'BASIN ROUTES', 45, 69, COLORS.cyan, 7);
  text(ctx, 'GLASS CITY', 45, 82, COLORS.white, 7);
  text(ctx, 'RIVER COMMONS', 45, 93, COLORS.magenta, 7);
  text(ctx, 'INDUSTRY', 45, 104, COLORS.white, 7);
  text(ctx, 'LAKE COAST', 45, 115, COLORS.cyan, 7);
  rect(ctx, 214, 75, 57, 56, COLORS.cyan, false);
  rect(ctx, 221, 81, 42, 24, COLORS.magenta, false);
  text(ctx, state.dispatchChoice === 'record-first' ? 'REC 1' : state.dispatchChoice === 'render-first' ? 'ROOF 1' : 'JOBS', 226, 89, COLORS.white, 8);
  rect(ctx, 224, 112, 33, 6, state.dispatchChoice ? COLORS.cyan : COLORS.magenta);
  rect(ctx, 170, 102, 39, 28, COLORS.white, false); text(ctx, 'SLIP', 177, 110, COLORS.magenta, 8);
  for (let x = 119; x < 163; x += 8) { rect(ctx, x, 105 + x % 5, 1, 25, COLORS.cyan); rect(ctx, x - 2, 109, 3, 4, COLORS.magenta); }
  rect(ctx, 148, 95, 9, 3, COLORS.white); rect(ctx, 155, 88, 2, 8, COLORS.white); rect(ctx, 155, 87, 6, 2, COLORS.white);
  rect(ctx, 150, 98, 1, 8, COLORS.white); rect(ctx, 154, 98, 1, 8, COLORS.white);
}

function drawHotspot(ctx: CanvasRenderingContext2D, hotspot: Hotspot, active: boolean): void {
  if (active) {
    rect(ctx, hotspot.rect.x - 2, hotspot.rect.y - 2, hotspot.rect.width + 4, hotspot.rect.height + 4, COLORS.white, false);
    const labelWidth = Math.min(W - 8, hotspot.label.length * 5.5 + 14);
    const labelX = hotspot.rect.x + labelWidth <= W ? hotspot.rect.x : Math.max(2, hotspot.rect.x + hotspot.rect.width - labelWidth);
    const labelY = Math.max(20, hotspot.rect.y - 14);
    rect(ctx, labelX, labelY, labelWidth, 14, COLORS.black);
    text(ctx, hotspot.label, labelX + 4, labelY + 2, COLORS.cyan, SMALL_SIZE);
  }
}

function drawBottomPanel(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, SCENE_HEIGHT, W, PANEL_HEIGHT, COLORS.magenta);
  rect(ctx, 2, SCENE_HEIGHT + 2, W - 4, PANEL_HEIGHT - 4, COLORS.black);
  text(ctx, rooms[state.room].name, 7, SCENE_HEIGHT + 6, COLORS.cyan, BODY_SIZE);
  wrap(ctx, state.message, 7, SCENE_HEIGHT + 19, 306, COLORS.white, SMALL_SIZE, 10, 3);
  if (state.dialogue.length) {
    rect(ctx, 4, SCENE_HEIGHT + 2, 312, PANEL_HEIGHT - 4, COLORS.black);
    wrap(ctx, state.dialogue.join(' '), 9, SCENE_HEIGHT + 8, 300, COLORS.cyan, SMALL_SIZE, 10, 4);
  }
  text(ctx, 'FULL TEXT IN SHIFT NOTES BELOW', 7, 188, COLORS.magenta, 7);
}

function drawCaseReview(ctx: CanvasRenderingContext2D, state: GameState, hovered: string | null): void {
  rect(ctx, 0, 0, W, H, COLORS.black);
  rect(ctx, 3, 3, W - 6, H - 6, COLORS.magenta, false);
  text(ctx, 'CASE REVIEW TERMINAL', 8, 7, COLORS.cyan, BODY_SIZE);
  text(ctx, '1-3: THEORY  //  CLICK EVIDENCE TO CITE', 8, 17, COLORS.dim, 7);

  Object.values(theories).forEach((theory, index) => {
    const y = REVIEW_THEORY_Y + index * 14;
    const key = reviewTargetKey({ kind: 'theory', id: theory.id });
    const selected = state.caseReview.theory === theory.id;
    if (selected) rect(ctx, 6, y, 308, 12, COLORS.cyan);
    if (hovered === key) rect(ctx, 5, y - 1, 310, 14, COLORS.white, false);
    text(ctx, `${index + 1} ${theory.label.toUpperCase()}`, 10, y + 2, selected ? COLORS.black : COLORS.white, 7);
  });

  const evidence = availableCaseEvidence(state);
  text(ctx, `EVIDENCE // ${state.caseReview.selectedEvidence.length} SELECTED`, 8, 60, COLORS.magenta, 8);
  evidence.forEach((id, index) => {
    const y = REVIEW_EVIDENCE_Y + index * 10;
    const key = reviewTargetKey({ kind: 'evidence', id });
    const selected = state.caseReview.selectedEvidence.includes(id);
    if (selected) rect(ctx, 6, y, 308, 9, COLORS.cyan);
    if (hovered === key) rect(ctx, 5, y - 1, 310, 11, COLORS.white, false);
    text(ctx, `${selected ? '[X]' : '[ ]'} ${caseEvidenceDefinitions[id].title}`, 10, y + 1, selected ? COLORS.black : COLORS.white, 7);
  });

  const selectedTheory = state.caseReview.theory;
  if (selectedTheory) {
    const preview = evaluateCase({ theory: selectedTheory, selectedEvidence: state.caseReview.selectedEvidence });
    text(ctx, `SUPPORT ${preview.supporting.length} // CONTRADICTIONS ${preview.contradicting.length}`, 8, 173, COLORS.dim, 7);
  } else {
    text(ctx, 'CHOOSE A THEORY TO BEGIN', 8, 173, COLORS.dim, 7);
  }
  const actions: Array<{ id: 'report' | 'conceal' | 'postpone'; label: string; x: number }> = [
    { id: 'report', label: 'REPORT', x: 5 },
    { id: 'conceal', label: 'CONCEAL', x: 110 },
    { id: 'postpone', label: 'POSTPONE', x: 215 },
  ];
  actions.forEach((action) => {
    const key = reviewTargetKey({ kind: 'action', id: action.id });
    rect(ctx, action.x, REVIEW_ACTION_Y, 100, 14, COLORS.magenta, false);
    if (hovered === key) rect(ctx, action.x - 1, REVIEW_ACTION_Y - 1, 102, 16, COLORS.white, false);
    text(ctx, action.label, action.x + 25, REVIEW_ACTION_Y + 3, COLORS.white, 7);
  });
}

function drawEnding(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, 0, W, H, COLORS.black);
  const positive = state.ending === 'success' || state.ending === 'strong' || state.ending === 'plausible';
  const title = state.ending === 'strong'
    ? 'REPORT FILED'
    : state.ending === 'plausible'
      ? 'REPORT QUALIFIED'
      : state.ending === 'incorrect'
        ? 'ACCUSATION REJECTED'
        : state.ending === 'concealed'
          ? 'FINDINGS SEALED'
          : positive ? 'CASE CLOSED' : 'CASE LOST';
  const titleX = Math.max(30, Math.floor((W - title.length * 9) / 2));
  rect(ctx, 14, 22, 292, 144, positive ? COLORS.cyan : COLORS.magenta, false);
  text(ctx, title, titleX, 47, positive ? COLORS.cyan : COLORS.magenta, 14);
  text(ctx, 'VESPER STATION // FIRST LIGHT', 86, 79, COLORS.white, 8);
  wrap(ctx, state.message, 42, 94, 236, COLORS.white, SMALL_SIZE, 10, 6);
  text(ctx, 'FULL ENDING IN SHIFT NOTES BELOW', 79, 173, COLORS.cyan, 8);
  text(ctx, 'REPLAY HANDOFF OR RESTART', 95, 187, COLORS.magenta, 8);
}

export function render(ctx: CanvasRenderingContext2D, state: GameState, hovered: string | null): void {
  ctx.setTransform(BACKING_SCALE, 0, 0, BACKING_SCALE, 0, 0);
  ctx.imageSmoothingEnabled = false;
  if (state.screen === 'title') { drawTitle(ctx); return; }
  if (state.screen === 'ending') { drawEnding(ctx, state); return; }
  if (state.screen === 'review') { drawCaseReview(ctx, state, hovered); return; }
  if (state.room === 'control') drawControlRoom(ctx, state);
  else if (state.room === 'corridor') drawCorridor(ctx);
  else if (state.room === 'furnace') drawFurnaceGallery(ctx, state);
  else if (state.room === 'pump') drawPumpHouse(ctx, state);
  else drawTerrace(ctx, state);
  const room = rooms[state.room as RoomId];
  room.hotspots.forEach((hotspot) => drawHotspot(ctx, hotspot, hotspot.id === hovered));
  drawBottomPanel(ctx, state);
}

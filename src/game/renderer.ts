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

function wrap(ctx: CanvasRenderingContext2D, value: string, x: number, y: number, width: number, color: string = COLORS.white, size = BODY_SIZE, lineHeight = BODY_LINE_HEIGHT): number {
  const words = value.split(' ');
  let line = '';
  let row = y;
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (ctx.measureText(candidate).width > width && line) { text(ctx, line, x, row, color, size); row += lineHeight; line = word; } else line = candidate;
  }
  if (line) text(ctx, line, x, row, color, size);
  return row + lineHeight;
}

function drawTitle(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, H, COLORS.black);
  rect(ctx, 12, 13, 296, 174, COLORS.magenta, false);
  rect(ctx, 17, 18, 286, 164, COLORS.cyan, false);
  text(ctx, 'GLASSPUNK', 91, 49, COLORS.magenta, 18);
  text(ctx, 'BLACKOUT AT', 99, 76, COLORS.cyan, 10);
  text(ctx, 'VESPER STATION', 88, 89, COLORS.white, 10);
  text(ctx, 'A CGA POINT-AND-CLICK MYSTERY', 65, 120, COLORS.dim, SMALL_SIZE);
  text(ctx, 'CLICK OR PRESS ENTER TO BEGIN', 77, 153, COLORS.white, BODY_SIZE);
  text(ctx, '1987 // NIGHT SHIFT', 110, 169, COLORS.magenta, SMALL_SIZE);
}

function drawControlRoom(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 15, W, 3, COLORS.magenta);
  for (let x = 8; x < W; x += 24) rect(ctx, x, 18, 2, 28, COLORS.dim);
  rect(ctx, 4, 35, 25, 99, COLORS.magenta, false);
  rect(ctx, 11, 47, 10, 73, COLORS.magenta, false);
  rect(ctx, 34, 58, 82, 75, COLORS.cyan, false);
  rect(ctx, 42, 69, 23, 15, COLORS.magenta, false);
  rect(ctx, 71, 69, 34, 15, COLORS.cyan, false);
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
  rect(ctx, 231, 51, 38, 82, COLORS.cyan, false);
  rect(ctx, 240, 63, 20, 42, COLORS.magenta, false);
  rect(ctx, 246, 70, 7, 14, COLORS.white);
  rect(ctx, 248, 111, 4, 4, COLORS.cyan);
  text(ctx, 'CONTROL ROOM', 7, 3, COLORS.white, BODY_SIZE);
  text(ctx, '02:13', 271, 3, COLORS.cyan, SMALL_SIZE);
}

function drawCorridor(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 17, W, 3, COLORS.cyan);
  for (let y = 28; y < 143; y += 16) rect(ctx, 9, y, 300, 2, COLORS.dim);
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
  for (let x = 217; x < 261; x += 10) rect(ctx, x, 73, 2, 21, COLORS.magenta);
  text(ctx, 'MAINTENANCE CORRIDOR', 7, 3, COLORS.white, BODY_SIZE);
}

function drawFurnaceGallery(ctx: CanvasRenderingContext2D): void {
  rect(ctx, 0, 0, W, SCENE_HEIGHT, COLORS.black);
  rect(ctx, 0, 17, W, 3, COLORS.magenta);
  rect(ctx, 17, 32, 100, 102, COLORS.cyan, false);
  rect(ctx, 27, 42, 80, 84, COLORS.magenta, false);
  rect(ctx, 39, 54, 56, 59, COLORS.white, false);
  rect(ctx, 47, 63, 40, 38, COLORS.black);
  rect(ctx, 55, 71, 24, 22, COLORS.magenta, false);
  rect(ctx, 124, 27, 6, 107, COLORS.dim);
  rect(ctx, 192, 27, 6, 107, COLORS.dim);
  rect(ctx, 136, 48, 49, 86, COLORS.magenta, false);
  rect(ctx, 145, 61, 30, 38, COLORS.cyan, false);
  rect(ctx, 151, 106, 8, 15, COLORS.white);
  rect(ctx, 166, 106, 8, 15, COLORS.white);
  rect(ctx, 271, 36, 38, 98, COLORS.cyan, false);
  rect(ctx, 280, 46, 20, 76, COLORS.magenta, false);
  rect(ctx, 286, 55, 8, 57, COLORS.white, false);
  text(ctx, 'FURNACE GALLERY', 7, 3, COLORS.white, BODY_SIZE);
  text(ctx, '02:14', 271, 3, COLORS.cyan, SMALL_SIZE);
}

function drawHotspot(ctx: CanvasRenderingContext2D, hotspot: Hotspot, active: boolean): void {
  if (active) {
    rect(ctx, hotspot.rect.x - 2, hotspot.rect.y - 2, hotspot.rect.width + 4, hotspot.rect.height + 4, COLORS.white, false);
    const labelWidth = Math.min(145, hotspot.label.length * 6 + 14);
    const labelX = hotspot.rect.x + labelWidth <= W ? hotspot.rect.x : Math.max(2, hotspot.rect.x + hotspot.rect.width - labelWidth);
    rect(ctx, labelX, hotspot.rect.y - 14, labelWidth, 14, COLORS.black);
    text(ctx, hotspot.label, labelX + 4, hotspot.rect.y - 12, COLORS.cyan, SMALL_SIZE);
  }
}

function drawBottomPanel(ctx: CanvasRenderingContext2D, state: GameState): void {
  rect(ctx, 0, SCENE_HEIGHT, W, PANEL_HEIGHT, COLORS.magenta);
  rect(ctx, 2, SCENE_HEIGHT + 2, W - 4, PANEL_HEIGHT - 4, COLORS.black);
  text(ctx, rooms[state.room].name, 7, SCENE_HEIGHT + 6, COLORS.cyan, BODY_SIZE);
  wrap(ctx, state.message, 7, SCENE_HEIGHT + 19, 306, COLORS.white);
  if (state.dialogue.length) {
    rect(ctx, 4, SCENE_HEIGHT + 2, 312, PANEL_HEIGHT - 4, COLORS.black);
    let row = SCENE_HEIGHT + 8;
    state.dialogue.forEach((line, index) => {
      row = wrap(ctx, line, 9, row, 300, index === 0 ? COLORS.cyan : COLORS.white, SMALL_SIZE, 11);
    });
  }
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
  text(ctx, positive ? 'VESPER STATION // 02:19' : 'VESPER STATION // 02:20', 87, 79, COLORS.white, SMALL_SIZE);
  wrap(ctx, state.message, 42, 94, 236, COLORS.white, SMALL_SIZE, 10);
  text(ctx, 'PRESS R OR USE RESTART', 95, 173, COLORS.dim, SMALL_SIZE);
}

export function render(ctx: CanvasRenderingContext2D, state: GameState, hovered: string | null): void {
  ctx.setTransform(BACKING_SCALE, 0, 0, BACKING_SCALE, 0, 0);
  ctx.imageSmoothingEnabled = false;
  if (state.screen === 'title') { drawTitle(ctx); return; }
  if (state.screen === 'ending') { drawEnding(ctx, state); return; }
  if (state.screen === 'review') { drawCaseReview(ctx, state, hovered); return; }
  if (state.room === 'control') drawControlRoom(ctx);
  else if (state.room === 'corridor') drawCorridor(ctx);
  else drawFurnaceGallery(ctx);
  const room = rooms[state.room as RoomId];
  room.hotspots.forEach((hotspot) => drawHotspot(ctx, hotspot, hotspot.id === hovered));
  drawBottomPanel(ctx, state);
}

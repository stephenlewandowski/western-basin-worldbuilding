import './style.css';
import { caseEvidenceDefinitions, clues, items, serviceNotes, theories, type Hotspot } from './game/data';
import { BACKING_HEIGHT, BACKING_WIDTH, toLogicalPoint } from './game/canvas';
import {
  beginGame, concealFindings, continueShift, currentGoal, currentRoom, decideDispatch,
  decideWorker, inspectHotspot, loadGame, newGame, openCaseReview, postponeCaseReview,
  requestHint, restartGame, saveGame, selectCaseTheory, selectItem, submitCaseReview,
  toggleCaseEvidence, type GameState,
} from './game/engine';
import { render } from './game/renderer';
import { reviewTargetAt, reviewTargetKey, reviewTargetLabel, reviewTargets, type ReviewTarget } from './game/review';

function required<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) throw new Error(`Missing game element: ${selector}`);
  return element;
}

const canvas = required<HTMLCanvasElement>('#game');
canvas.width = BACKING_WIDTH;
canvas.height = BACKING_HEIGHT;
const context = canvas.getContext('2d');
if (!context) throw new Error('Canvas 2D rendering is not supported.');
const ctx: CanvasRenderingContext2D = context;
const statusEl = required<HTMLElement>('#status');
const inventoryEl = required<HTMLElement>('#inventory');
const evidenceEl = required<HTMLElement>('#evidence');
const notesEl = required<HTMLElement>('#service-notes');
const caseReviewEl = required<HTMLElement>('#case-review');
const actionsEl = required<HTMLElement>('#scene-actions');
const choicesEl = required<HTMLElement>('#choices');
const transcriptEl = required<HTMLElement>('#transcript');
const objectiveEl = required<HTMLElement>('#objective');
const hintButton = required<HTMLButtonElement>('#hint');
let state = newGame();
let hovered: string | null = null;
let focusIndex = -1;

function button(parent: HTMLElement, key: string, label: string, action: () => void, selected = false, description?: string): void {
  const element = document.createElement('button');
  element.type = 'button';
  element.dataset.key = key;
  element.textContent = label;
  element.classList.toggle('selected', selected);
  if (state.screen === 'ending' && (key.startsWith('clue:') || key.startsWith('note:'))) element.disabled = true;
  if (selected || key.startsWith('item:') || key.startsWith('review:')) element.setAttribute('aria-pressed', String(selected));
  if (description) element.title = description;
  element.addEventListener('click', action);
  parent.append(element);
}

function update(next: GameState, announcement?: string): void {
  const focusedKey = (document.activeElement as HTMLElement | null)?.dataset.key;
  if (state.room !== next.room || state.screen !== next.screen) { hovered = null; focusIndex = -1; }
  state = next;
  required<HTMLElement>('#storage-feedback').textContent = '';
  render(ctx, state, hovered);
  objectiveEl.textContent = currentGoal(state);
  hintButton.disabled = state.screen !== 'play';
  renderActions();
  renderInventory();
  renderNotes();
  renderCaseReview();
  transcriptEl.replaceChildren();
  [state.message, ...state.dialogue].forEach((line) => {
    const p = document.createElement('p'); p.textContent = line; transcriptEl.append(p);
  });
  required<HTMLElement>('#mobile-feedback').textContent = [state.message, ...state.dialogue].join(' ');
  if (announcement) statusEl.textContent = announcement;
  if (focusedKey !== undefined) {
    const replacement = [...document.querySelectorAll<HTMLButtonElement>('button[data-key]')].find((entry) => entry.dataset.key === focusedKey);
    (replacement ?? canvas).focus({ preventScroll: true });
  }
}

function renderActions(): void {
  actionsEl.replaceChildren(); choicesEl.replaceChildren();
  required<HTMLElement>('#scene-heading').textContent = state.screen === 'play' ? currentRoom(state).name : 'SCENE ACTIONS';
  if (state.screen === 'title') button(actionsEl, 'begin', 'BEGIN NIGHT SHIFT', () => update(beginGame(state)));
  if (state.screen === 'ending') button(actionsEl, 'continue', 'REPLAY HANDOFF', () => update(continueShift(state)));
  if (state.screen !== 'play') return;
  currentRoom(state).hotspots.forEach((hotspot) => {
    button(actionsEl, `hotspot:${hotspot.id}`, `${hotspot.action === 'move' ? '→ ' : ''}${hotspot.label}`, () => activateHotspot(hotspot));
  });
  if (state.room === 'furnace' && state.workerMet && !state.workerChoice) {
    button(choicesEl, 'worker:report', 'TELL MARA ABOUT THE ALTERATION', () => update(decideWorker(state, 'report')));
    button(choicesEl, 'worker:quiet', 'KEEP IT BETWEEN US', () => update(decideWorker(state, 'keep-quiet')));
  }
  if (state.dispatchOpen && state.room === 'terrace') {
    button(choicesEl, 'dispatch:record', 'SEND RECORD · DELAY ROOF RENDER', () => update(decideDispatch(state, 'record-first')));
    button(choicesEl, 'dispatch:render', 'FINISH RENDER · QUEUE RECORD', () => update(decideDispatch(state, 'render-first')));
  }
}

function renderInventory(): void {
  inventoryEl.replaceChildren();
  if (!state.inventory.length) { inventoryEl.textContent = 'EMPTY'; return; }
  state.inventory.forEach((id) => button(inventoryEl, `item:${id}`, items[id].label, () => update(selectItem(state, id)), state.selectedItem === id, items[id].description));
}

function renderNotes(): void {
  evidenceEl.replaceChildren(); notesEl.replaceChildren();
  if (!state.evidence.length) evidenceEl.textContent = 'NO CLUES LOGGED';
  if (!state.serviceNotes.length) notesEl.textContent = 'NO SERVICE NOTES';
  state.evidence.forEach((id) => button(evidenceEl, `clue:${id}`, clues[id].title, () => update({ ...state, message: clues[id].text, dialogue: [], dispatchOpen: false })));
  state.serviceNotes.forEach((id) => button(notesEl, `note:${id}`, serviceNotes[id].title, () => update({ ...state, message: serviceNotes[id].text, dialogue: [], dispatchOpen: false })));
}

function renderCaseReview(): void {
  caseReviewEl.replaceChildren(); caseReviewEl.hidden = state.screen !== 'review';
  if (state.screen !== 'review') return;
  const heading = document.createElement('h2'); heading.textContent = 'CASE REVIEW'; caseReviewEl.append(heading);
  const help = document.createElement('p'); help.textContent = 'Choose an explanation, then cite at least two supporting items. Select a citation to read it in Shift Notes. The assessment covers cited items only; other clues may disagree. This is a fictional case, not a scientific model.'; caseReviewEl.append(help);
  reviewTargets(state).forEach((target) => {
    const selected = target.kind === 'theory' ? state.caseReview.theory === target.id : target.kind === 'evidence' && state.caseReview.selectedEvidence.includes(target.id);
    button(caseReviewEl, reviewTargetKey(target), reviewTargetLabel(target), () => activateReviewTarget(target), selected, target.kind === 'evidence' ? caseEvidenceDefinitions[target.id].text : undefined);
  });
}

function hotspotAt(x: number, y: number): Hotspot | undefined {
  return currentRoom(state).hotspots.find(({ rect }) => x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height);
}

function activateHotspot(hotspot?: Hotspot): void {
  if (state.screen === 'title') { update(beginGame(state)); return; }
  if (hotspot && state.screen === 'play') update(inspectHotspot(state, hotspot));
}

function activateReviewTarget(target?: ReviewTarget): void {
  if (!target || state.screen !== 'review') return;
  if (target.kind === 'theory') update(selectCaseTheory(state, target.id));
  else if (target.kind === 'evidence') update(toggleCaseEvidence(state, target.id));
  else if (target.id === 'report') update(submitCaseReview(state));
  else if (target.id === 'conceal') update(concealFindings(state));
  else update(postponeCaseReview(state));
}

function focusTarget(direction: 1 | -1): void {
  const targets = state.screen === 'review' ? reviewTargets(state) : currentRoom(state).hotspots;
  focusIndex = (focusIndex + direction + targets.length) % targets.length;
  const target = targets[focusIndex];
  hovered = 'kind' in target ? reviewTargetKey(target) : target.id;
  render(ctx, state, hovered);
  statusEl.textContent = `${'kind' in target ? reviewTargetLabel(target) : target.label}. Press Enter to inspect.`;
}

canvas.addEventListener('mousemove', (event) => {
  if (state.screen !== 'play' && state.screen !== 'review') return;
  const { x, y } = toLogicalPoint(event.clientX, event.clientY, canvas.getBoundingClientRect());
  const target = state.screen === 'review' ? reviewTargetAt(x, y, state) : hotspotAt(x, y);
  const next = target ? ('kind' in target ? reviewTargetKey(target) : target.id) : null;
  if (next !== hovered) { hovered = next; render(ctx, state, hovered); }
});
canvas.addEventListener('mouseleave', () => { hovered = null; render(ctx, state, hovered); });
canvas.addEventListener('click', (event) => {
  canvas.focus({ preventScroll: true });
  const { x, y } = toLogicalPoint(event.clientX, event.clientY, canvas.getBoundingClientRect());
  if (state.screen === 'review') activateReviewTarget(reviewTargetAt(x, y, state));
  else activateHotspot(hotspotAt(x, y));
});

document.addEventListener('keydown', (event) => {
  // Native buttons/links and Tab keep their normal behavior.
  if (event.target !== canvas && event.target !== document.body) return;
  if (event.altKey || event.ctrlKey || event.metaKey || event.key === 'Tab') return;
  const key = event.key.toLowerCase();
  if (key === 'r') { update(restartGame()); return; }
  if (state.screen === 'title') {
    if (key === 'enter' || key === ' ') { event.preventDefault(); update(beginGame(state)); }
    return;
  }
  if (state.screen === 'ending') return;
  if (key === 'arrowright' || key === 'arrowdown' || key === 'd' || key === 's') { event.preventDefault(); focusTarget(1); return; }
  if (key === 'arrowleft' || key === 'arrowup' || key === 'a' || key === 'w') { event.preventDefault(); focusTarget(-1); return; }
  if (key === 'enter' || key === ' ') {
    event.preventDefault();
    if (state.screen === 'review') activateReviewTarget(reviewTargets(state).find((target) => reviewTargetKey(target) === hovered) ?? reviewTargets(state)[0]);
    else activateHotspot(currentRoom(state).hotspots.find((target) => target.id === hovered) ?? currentRoom(state).hotspots[0]);
    return;
  }
  if (state.screen === 'review') {
    if (['1', '2', '3'].includes(key)) update(selectCaseTheory(state, Object.values(theories)[Number(key) - 1].id));
    if (key === 'escape') update(postponeCaseReview(state));
    return;
  }
  if (key === 'i' && state.inventory.length) {
    const index = state.selectedItem ? state.inventory.indexOf(state.selectedItem) : -1;
    update(selectItem(state, state.inventory[(index + 1) % state.inventory.length]));
  }
  if (key === 'h') update(requestHint(state));
  if (key === 'y') update(decideWorker(state, 'report'));
  if (key === 'n') update(decideWorker(state, 'keep-quiet'));
  if (key === 'f') update(state.room === 'control' ? openCaseReview(state) : { ...state, message: 'The Case Review terminal is in the control room.', dialogue: [] });
  if (key === 'escape') update({ ...state, selectedItem: null, dialogue: [], dispatchOpen: false });
});

hintButton.addEventListener('click', () => update(requestHint(state)));
required<HTMLButtonElement>('#save').addEventListener('click', () => {
  const saved = saveGame(state);
  required<HTMLElement>('#storage-feedback').textContent = saved ? 'Shift saved on this device.' : 'Save unavailable. Keep playing in this tab.';
  statusEl.textContent = required<HTMLElement>('#storage-feedback').textContent;
});
required<HTMLButtonElement>('#load').addEventListener('click', () => {
  const saved = loadGame();
  if (saved) update(saved);
  required<HTMLElement>('#storage-feedback').textContent = saved ? 'Saved shift loaded.' : 'No usable save. Your shift is unchanged.';
  statusEl.textContent = required<HTMLElement>('#storage-feedback').textContent;
});
required<HTMLButtonElement>('#restart').addEventListener('click', () => update(restartGame()));
update(state);

import './style.css';
import { caseEvidenceDefinitions, clues, items, theories, type Hotspot } from './game/data';
import { BACKING_HEIGHT, BACKING_WIDTH, toLogicalPoint } from './game/canvas';
import {
  beginGame,
  concealFindings,
  currentRoom,
  decideWorker,
  inspectHotspot,
  itemLabel,
  loadGame,
  newGame,
  openCaseReview,
  postponeCaseReview,
  restartGame,
  saveGame,
  selectCaseTheory,
  selectItem,
  submitCaseReview,
  toggleCaseEvidence,
  toggleMute,
  talkToMara,
  useSelectedItem,
  type GameState,
} from './game/engine';
import { render } from './game/renderer';
import { reviewTargetAt, reviewTargetKey, reviewTargetLabel, reviewTargets, type ReviewTarget } from './game/review';

function requireElement<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);

  if (!element) {
    throw new Error(`Required element not found: ${selector}`);
  }

  return element;
}

function requireContext(canvas: HTMLCanvasElement): CanvasRenderingContext2D {
  const context = canvas.getContext('2d');

  if (!context) {
    throw new Error('Canvas 2D rendering is not supported.');
  }

  return context;
}

const canvas = requireElement<HTMLCanvasElement>('#game');
const statusEl = requireElement<HTMLElement>('#status');
const muteButton = requireElement<HTMLButtonElement>('#mute');
const inventoryEl = requireElement<HTMLElement>('#inventory');
const evidenceEl = requireElement<HTMLElement>('#evidence');
const caseReviewEl = requireElement<HTMLElement>('#case-review');
const saveButton = requireElement<HTMLButtonElement>('#save');
const loadButton = requireElement<HTMLButtonElement>('#load');
const restartButton = requireElement<HTMLButtonElement>('#restart');
canvas.width = BACKING_WIDTH;
canvas.height = BACKING_HEIGHT;
const ctx = requireContext(canvas);

let state: GameState = newGame();
let hovered: string | null = null;
let focusIndex = 0;

function announce(message: string): void { statusEl.textContent = message; }

function update(next: GameState, announcement = next.message): void {
  state = next;
  render(ctx, state, hovered);
  renderInventory();
  renderEvidence();
  renderCaseReview();
  muteButton.textContent = state.muted ? 'UNMUTE' : 'MUTE';
  announce(announcement);
}

function renderInventory(): void {
  inventoryEl.replaceChildren();
  if (!state.inventory.length) {
    const empty = document.createElement('p'); empty.textContent = 'EMPTY'; inventoryEl.append(empty); return;
  }
  state.inventory.forEach((id) => {
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = state.selectedItem === id ? `> ${itemLabel(id)}` : itemLabel(id);
    button.classList.toggle('selected', state.selectedItem === id);
    button.title = items[id].description;
    button.addEventListener('click', () => update(selectItem(state, id), `${items[id].label} selected.`));
    inventoryEl.append(button);
  });
}

function renderEvidence(): void {
  evidenceEl.replaceChildren();
  if (!state.evidence.length) {
    const empty = document.createElement('p'); empty.textContent = 'NO CLUES LOGGED'; evidenceEl.append(empty); return;
  }
  state.evidence.forEach((id) => {
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = clues[id].title; button.title = clues[id].text;
    button.addEventListener('click', () => update({ ...state, message: clues[id].text, dialogue: [] }));
    evidenceEl.append(button);
  });
}

function renderCaseReview(): void {
  caseReviewEl.replaceChildren();
  caseReviewEl.hidden = state.screen !== 'review';
  if (state.screen !== 'review') return;

  const heading = document.createElement('h2');
  heading.textContent = 'CASE REVIEW';
  caseReviewEl.append(heading);

  const theoryLabel = document.createElement('p');
  theoryLabel.textContent = 'EXPLANATION';
  caseReviewEl.append(theoryLabel);
  Object.values(theories).forEach((theory) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = state.caseReview.theory === theory.id ? `> ${theory.label}` : theory.label;
    button.classList.toggle('selected', state.caseReview.theory === theory.id);
    button.addEventListener('click', () => update(selectCaseTheory(state, theory.id)));
    caseReviewEl.append(button);
  });

  const evidenceLabel = document.createElement('p');
  evidenceLabel.textContent = 'CITE AT LEAST TWO SUPPORTING ITEMS';
  caseReviewEl.append(evidenceLabel);
  const available = reviewTargets(state).filter((target): target is Extract<ReviewTarget, { kind: 'evidence' }> => target.kind === 'evidence');
  available.forEach((target) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = state.caseReview.selectedEvidence.includes(target.id) ? `> ${caseEvidenceDefinitions[target.id].title}` : caseEvidenceDefinitions[target.id].title;
    button.classList.toggle('selected', state.caseReview.selectedEvidence.includes(target.id));
    button.title = caseEvidenceDefinitions[target.id].text;
    button.addEventListener('click', () => update(toggleCaseEvidence(state, target.id)));
    caseReviewEl.append(button);
  });

  const actions = document.createElement('div');
  actions.className = 'case-review-actions';
  const reportButton = document.createElement('button');
  reportButton.type = 'button'; reportButton.textContent = 'SUBMIT REPORT';
  reportButton.addEventListener('click', () => update(submitCaseReview(state)));
  const concealButton = document.createElement('button');
  concealButton.type = 'button'; concealButton.textContent = 'CONCEAL FINDINGS';
  concealButton.addEventListener('click', () => update(concealFindings(state)));
  const postponeButton = document.createElement('button');
  postponeButton.type = 'button'; postponeButton.textContent = 'POSTPONE';
  postponeButton.addEventListener('click', () => update(postponeCaseReview(state)));
  actions.append(reportButton, concealButton, postponeButton);
  caseReviewEl.append(actions);
}

function hotspotAt(x: number, y: number): Hotspot | undefined {
  return currentRoom(state).hotspots.find((hotspot) => x >= hotspot.rect.x && x <= hotspot.rect.x + hotspot.rect.width && y >= hotspot.rect.y && y <= hotspot.rect.y + hotspot.rect.height);
}

function canvasPoint(event: MouseEvent): { x: number; y: number } {
  const box = canvas.getBoundingClientRect();
  return toLogicalPoint(event.clientX, event.clientY, box);
}

function activateHotspot(hotspot: Hotspot | undefined): void {
  if (state.screen === 'title') { update(beginGame(state)); return; }
  if (state.screen === 'review') return;
  if (!hotspot) return;
  update(inspectHotspot(state, hotspot));
}

function activateReviewTarget(target: ReviewTarget | undefined): void {
  if (!target || state.screen !== 'review') return;
  if (target.kind === 'theory') update(selectCaseTheory(state, target.id));
  else if (target.kind === 'evidence') update(toggleCaseEvidence(state, target.id));
  else if (target.id === 'report') update(submitCaseReview(state));
  else if (target.id === 'conceal') update(concealFindings(state));
  else update(postponeCaseReview(state));
}

function focusHotspot(direction: 1 | -1): void {
  const available = currentRoom(state).hotspots;
  focusIndex = (focusIndex + direction + available.length) % available.length;
  hovered = available[focusIndex].id;
  render(ctx, state, hovered);
  announce(`${available[focusIndex].label}. Press Enter to inspect.`);
}

function focusReview(direction: 1 | -1): void {
  const available = reviewTargets(state);
  if (!available.length) return;
  focusIndex = (focusIndex + direction + available.length) % available.length;
  const target = available[focusIndex];
  hovered = reviewTargetKey(target);
  render(ctx, state, hovered);
  announce(`${reviewTargetLabel(target)}. Press Enter to choose.`);
}

canvas.addEventListener('mousemove', (event) => {
  if (state.screen !== 'play' && state.screen !== 'review') return;
  const point = canvasPoint(event);
  const next = state.screen === 'review'
    ? (reviewTargetAt(point.x, point.y, state) ? reviewTargetKey(reviewTargetAt(point.x, point.y, state)!) : null)
    : hotspotAt(point.x, point.y)?.id ?? null;
  if (next !== hovered) { hovered = next; render(ctx, state, hovered); }
});

canvas.addEventListener('mouseleave', () => { hovered = null; render(ctx, state, hovered); });
canvas.addEventListener('click', (event) => {
  const point = canvasPoint(event);
  if (state.screen === 'review') {
    activateReviewTarget(reviewTargetAt(point.x, point.y, state));
    return;
  }
  activateHotspot(hotspotAt(point.x, point.y));
});

document.addEventListener('keydown', (event) => {
  if (event.key.toLowerCase() === 'r') { update(restartGame()); return; }
  if (event.key === 'Tab') {
    if (state.screen === 'review') return;
    event.preventDefault();
    if (state.inventory.length) {
      const index = state.selectedItem ? state.inventory.indexOf(state.selectedItem) : -1;
      const next = state.inventory[(index + 1) % state.inventory.length];
      update(selectItem(state, next), `${itemLabel(next)} selected.`);
    }
    return;
  }
  if (state.screen === 'review') {
    if (event.key === '1' || event.key === '2' || event.key === '3') {
      const theory = Object.values(theories)[Number(event.key) - 1];
      if (theory) update(selectCaseTheory(state, theory.id));
      return;
    }
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown' || event.key.toLowerCase() === 'd' || event.key.toLowerCase() === 's') {
      event.preventDefault(); focusReview(1); return;
    }
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp' || event.key.toLowerCase() === 'a' || event.key.toLowerCase() === 'w') {
      event.preventDefault(); focusReview(-1); return;
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      const target = reviewTargets(state).find((entry) => reviewTargetKey(entry) === hovered) ?? reviewTargets(state)[0];
      activateReviewTarget(target);
      return;
    }
    if (event.key === 'Escape') { update(postponeCaseReview(state)); return; }
    return;
  }
  if (event.key.toLowerCase() === 'y' && state.screen === 'play' && state.room === 'furnace' && state.workerMet && !state.workerChoice) {
    update(decideWorker(state, 'report'));
    return;
  }
  if (event.key.toLowerCase() === 'n' && state.screen === 'play' && state.room === 'furnace' && state.workerMet && !state.workerChoice) {
    update(decideWorker(state, 'keep-quiet'));
    return;
  }
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown' || event.key.toLowerCase() === 'd' || event.key.toLowerCase() === 's') { event.preventDefault(); focusHotspot(1); return; }
  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp' || event.key.toLowerCase() === 'a' || event.key.toLowerCase() === 'w') { event.preventDefault(); focusHotspot(-1); return; }
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    if (state.screen === 'title') { update(beginGame(state)); return; }
    if (state.screen === 'ending') return;
    activateHotspot(currentRoom(state).hotspots.find((hotspot) => hotspot.id === hovered));
    return;
  }
  if (event.key === 'Escape') { update({ ...state, selectedItem: null, dialogue: [] }, 'Selection cleared.'); }
});

saveButton.addEventListener('click', () => { saveGame(state); announce('Game saved locally.'); });
loadButton.addEventListener('click', () => { const loaded = loadGame(); update(loaded ?? state, loaded ? 'Saved game loaded.' : 'No saved game found.'); });
restartButton.addEventListener('click', () => update(restartGame()));
muteButton.addEventListener('click', () => update(toggleMute(state), state.muted ? 'Sound muted.' : 'Sound on.'));

update(state);

// Keep the repaired console double-click as a direct path to the unlocked terminal.
canvas.addEventListener('dblclick', () => {
  if (state.screen === 'play' && state.panelSolved && state.room === 'control') update(openCaseReview(state));
});

// NPC dialogue remains keyboard reachable even when the pointer is not over her.
window.addEventListener('keydown', (event) => {
  if (event.key.toLowerCase() === 'm' && state.screen === 'play' && state.room === 'control') update(talkToMara(state));
  if (event.key.toLowerCase() === 'u' && state.screen === 'play' && state.room === 'control') update(useSelectedItem(state));
  if (event.key.toLowerCase() === 'f' && state.screen === 'play' && state.panelSolved) {
    if (state.room === 'control') update(openCaseReview(state));
    else update({ ...state, message: 'Return to the Control Room to open Case Review.', dialogue: [] });
  }
});

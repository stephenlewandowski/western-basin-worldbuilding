import { beforeEach, describe, expect, it, vi } from 'vitest';
import { rooms, type RoomId } from './data';
import {
  beginGame,
  decideWorker,
  endFromPanel,
  inspectHotspot,
  loadGame,
  newGame,
  postponeCaseReview,
  saveGame,
  selectCaseTheory,
  selectItem,
  submitCaseReview,
  toggleCaseEvidence,
  concealFindings,
  decideDispatch,
  continueShift,
  requestHint,
  SAVE_KEY,
} from './engine';

function inspect(state: ReturnType<typeof newGame>, room: RoomId, id: string) {
  const hotspot = rooms[room].hotspots.find((entry) => entry.id === id);
  if (!hotspot) throw new Error(`Missing hotspot: ${room}/${id}`);
  return inspectHotspot(state, hotspot);
}

function reachFurnace() {
  let state = beginGame(newGame());
  state = inspect(state, 'control', 'to-corridor');
  return inspect(state, 'corridor', 'to-furnace-gallery');
}

function repairPanel() {
  let state = beginGame(newGame());
  state = inspect(state, 'control', 'shift-log');
  state = inspect(state, 'control', 'maintenance-memo');
  state = inspect(state, 'control', 'mara');
  state = inspect(state, 'control', 'to-corridor');
  state = inspect(state, 'corridor', 'map');
  state = inspect(state, 'corridor', 'breaker');
  state = inspect(state, 'corridor', 'locker');
  state = inspect(state, 'corridor', 'to-furnace-gallery');
  state = inspect(state, 'furnace', 'furnace-tag');
  state = inspect(state, 'furnace', 'furnace-scar');
  state = inspect(state, 'furnace', 'niko');
  state = decideWorker(state, 'report');
  state = inspect(state, 'furnace', 'to-corridor');
  state = inspect(state, 'corridor', 'to-control');
  state = selectItem(state, 'fuse');
  return inspect(state, 'control', 'console');
}

function openReview() {
  return inspect(finishService(), 'control', 'case-review');
}

function finishService(choice: 'record-first' | 'render-first' = 'record-first') {
  let state = repairPanel();
  state = inspect(state, 'control', 'to-corridor');
  state = inspect(state, 'corridor', 'to-pump');
  state = inspect(state, 'pump', 'pump-card');
  state = selectItem(state, 'heat-glove');
  state = inspect(state, 'pump', 'return-wheel');
  state = inspect(state, 'pump', 'pump-starter');
  state = inspect(state, 'pump', 'to-terrace');
  state = inspect(state, 'terrace', 'route-board');
  state = inspect(state, 'terrace', 'dispatch-card');
  state = inspect(state, 'terrace', 'dispatch');
  state = decideDispatch(state, choice);
  state = inspect(state, 'terrace', 'to-pump');
  state = inspect(state, 'pump', 'to-corridor');
  return inspect(state, 'corridor', 'to-control');
}

const storage = new Map<string, string>();

beforeEach(() => {
  storage.clear();
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => { storage.set(key, value); },
  });
});

describe('Glasspunk state transitions', () => {
  it('walks the intended clue, key, fuse, and repair route to success', () => {
    let state = beginGame(newGame());
    state = inspect(state, 'control', 'shift-log');
    state = inspect(state, 'control', 'mara');
    state = inspect(state, 'control', 'to-corridor');
    state = inspect(state, 'corridor', 'map');
    state = inspect(state, 'corridor', 'breaker');
    state = inspect(state, 'corridor', 'locker');
    state = inspect(state, 'corridor', 'to-control');
    state = selectItem(state, 'fuse');
    state = inspect(state, 'control', 'console');

    expect(state.panelSolved).toBe(true);
    expect(endFromPanel(state).ending).toBe('success');
  });

  it('makes the wrong tool recoverable without losing collected progress', () => {
    let state = beginGame(newGame());
    state = inspect(state, 'control', 'shift-log');
    state = inspect(state, 'control', 'mara');
    state = selectItem(state, 'maintenance-key');
    state = inspect(state, 'control', 'console');

    expect(state.screen).toBe('play');
    expect(state.ending).toBeNull();
    expect(state.inventory).toContain('maintenance-key');
    expect(state.evidence).toContain('shift-log');
    expect(state.message).toContain('Nothing damaged');
  });

  it('requires lights, circulation and a dispatch choice before the final handoff', () => {
    const beforeRepair = beginGame(newGame());
    const locked = inspect(beforeRepair, 'control', 'case-review');
    expect(locked.screen).toBe('play');
    expect(locked.caseReviewUnlocked).toBe(false);

    const repaired = repairPanel();
    expect(repaired.panelSolved).toBe(true);
    expect(repaired.caseReviewUnlocked).toBe(true);
    expect(inspect(repaired, 'control', 'case-review').screen).toBe('play');
    expect(openReview().screen).toBe('review');
  });

  it('keeps the pump door and interlock gated, with no guessed tool or remote action bypass', () => {
    let state = beginGame(newGame());
    state = inspect(state, 'control', 'to-corridor');
    expect(inspect(state, 'corridor', 'to-pump').room).toBe('corridor');
    state = inspect(repairPanel(), 'control', 'to-corridor');
    state = inspect(state, 'corridor', 'to-pump');
    expect(inspect(state, 'pump', 'pump-starter').pumpRunning).toBe(false);
    state = selectItem(state, 'heat-glove');
    expect(inspect(state, 'pump', 'return-wheel').returnOpen).toBe(false);
    state = inspect(state, 'pump', 'pump-card');
    state = selectItem(state, null);
    expect(inspect(state, 'pump', 'return-wheel').returnOpen).toBe(false);
    expect(inspect(state, 'terrace', 'dispatch').dispatchOpen).toBe(false);
    expect(decideDispatch(state, 'record-first').dispatchChoice).toBeNull();
    expect(selectItem(beginGame(newGame()), 'heat-glove').selectedItem).toBeNull();
  });

  it('completes both dispatch branches with protected circulation and different payoffs', () => {
    for (const choice of ['record-first', 'render-first'] as const) {
      let state = finishService(choice);
      expect(state.pumpRunning).toBe(true);
      expect(state.returnOpen).toBe(true);
      expect(state.dispatchChoice).toBe(choice);
      expect(state.evidence).not.toContain('pump-card');
      state = inspect(state, 'control', 'case-review');
      state = selectCaseTheory(state, 'industrial-accident');
      state = toggleCaseEvidence(state, 'furnace-scar');
      state = toggleCaseEvidence(state, 'repair-outcome');
      state = submitCaseReview(state);
      expect(state.ending).toBe('strong');
      expect(state.message).toContain(choice === 'record-first' ? 'roof render waits' : 'morning queue');
      expect(state.message).toContain('good mug');
      const resumed = continueShift(state);
      expect(resumed.screen).toBe('play');
      expect(resumed.pumpRunning).toBe(true);
      expect(resumed.caseReview.selectedEvidence).toEqual(['furnace-scar', 'repair-outcome']);
    }
  });

  it('hints orient the player without manufacturing progress, and notes can be reread', () => {
    const state = beginGame(newGame());
    const hinted = requestHint(state);
    expect(hinted.evidence).toEqual([]);
    expect(hinted.inventory).toEqual([]);
    expect(hinted.message).toContain('shift log');
    const logged = inspect(state, 'control', 'shift-log');
    expect(inspect(logged, 'control', 'shift-log').message).toContain('newer ink');
  });

  it('round-trips new service progress and dispatch choices', () => {
    const state = finishService('render-first');
    expect(saveGame(state)).toBe(true);
    expect(loadGame()).toEqual(state);
  });

  it('rejects broken saves and sanitizes unknown, duplicate and unavailable entries', () => {
    for (const raw of ['{broken', 'null', JSON.stringify({ ...newGame(), room: 'missing' }), JSON.stringify({ ...newGame(), screen: 'missing' })]) {
      storage.set(SAVE_KEY, raw); expect(loadGame()).toBeNull();
    }
    storage.set(SAVE_KEY, JSON.stringify({ ...newGame(), screen: 'play', inventory: ['fuse', 'fuse', '__proto__', 'missing'], evidence: ['shift-log', 'shift-log', 'missing'], selectedItem: 'missing', serviceNotes: ['pump-card', 'pump-card', 'missing'], returnOpen: true, pumpRunning: true, dispatchChoice: 'render-first', caseReview: { theory: 'worker-sabotage', selectedEvidence: ['shift-log', 'shift-log', 'furnace-scar', 'missing'] } }));
    const loaded = loadGame()!;
    expect(loaded.inventory).toEqual(['fuse']);
    expect(loaded.evidence).toEqual(['shift-log']);
    expect(loaded.serviceNotes).toEqual(['pump-card']);
    expect(loaded.caseReview.selectedEvidence).toEqual(['shift-log']);
    expect(loaded.selectedItem).toBeNull();
    expect(loaded.pumpRunning).toBe(false);
    expect(loaded.dispatchChoice).toBeNull();
  });

  it('handles browser storage denial without interrupting play', () => {
    vi.stubGlobal('localStorage', { getItem: () => { throw new Error('blocked'); }, setItem: () => { throw new Error('blocked'); } });
    expect(loadGame()).toBeNull();
    expect(saveGame(beginGame(newGame()))).toBe(false);
  });

  it('migrates an old review save to the unfinished handoff without losing case notes', () => {
    storage.set(SAVE_KEY, JSON.stringify({ ...repairPanel(), screen: 'review', caseReview: { theory: 'industrial-accident', selectedEvidence: ['maintenance-memo', 'repair-outcome'], submittedOutcome: null, evaluation: null } }));
    const state = loadGame()!;
    expect(state.screen).toBe('play');
    expect(state.room).toBe('control');
    expect(state.caseReview.selectedEvidence).toEqual(['maintenance-memo', 'repair-outcome']);
    expect(state.message).toContain('saved case notes');
    const bypass = { ...state, screen: 'review' as const };
    expect(submitCaseReview(bypass).screen).toBe('play');
    expect(concealFindings(bypass).screen).toBe('play');
  });

  it('requires a theory and two supporting selections before submitting', () => {
    let state = openReview();
    expect(submitCaseReview(state).screen).toBe('review');
    expect(submitCaseReview(state).message).toContain('Choose one explanation');

    state = selectCaseTheory(state, 'industrial-accident');
    state = toggleCaseEvidence(state, 'furnace-scar');
    expect(submitCaseReview(state).screen).toBe('review');
    expect(submitCaseReview(state).message).toContain('at least two');

    state = toggleCaseEvidence(state, 'repair-outcome');
    expect(submitCaseReview(state).ending).toBe('strong');
  });

  it('produces distinct report outcomes for plausible and incorrect conclusions', () => {
    let plausible = openReview();
    plausible = selectCaseTheory(plausible, 'industrial-accident');
    plausible = toggleCaseEvidence(plausible, 'breaker-note');
    plausible = toggleCaseEvidence(plausible, 'station-map');
    plausible = submitCaseReview(plausible);
    expect(plausible.ending).toBe('plausible');
    expect(plausible.message).toContain('PLAUSIBLE BUT INCOMPLETE');
    expect(plausible.message).toContain('BREAKER NOTE');

    let incorrect = openReview();
    incorrect = selectCaseTheory(incorrect, 'worker-sabotage');
    incorrect = toggleCaseEvidence(incorrect, 'shift-log');
    incorrect = toggleCaseEvidence(incorrect, 'breaker-note');
    incorrect = toggleCaseEvidence(incorrect, 'furnace-scar');
    incorrect = toggleCaseEvidence(incorrect, 'repair-outcome');
    incorrect = submitCaseReview(incorrect);
    expect(incorrect.ending).toBe('incorrect');
    expect(incorrect.message).toContain('BYPASS SCORCH MARK');
    expect(incorrect.message).toContain('Contradicted by');
  });

  it('supports conceal and postpone choices without losing the selected review state', () => {
    let postponed = openReview();
    postponed = selectCaseTheory(postponed, 'management-cover-up');
    postponed = toggleCaseEvidence(postponed, 'maintenance-memo');
    postponed = toggleCaseEvidence(postponed, 'shift-log');
    postponed = postponeCaseReview(postponed);
    expect(postponed.screen).toBe('play');
    expect(postponed.caseReview.submittedOutcome).toBe('postpone');
    expect(postponed.caseReview.selectedEvidence).toEqual(['maintenance-memo', 'shift-log']);

    const concealed = concealFindings(openReview());
    expect(concealed.screen).toBe('ending');
    expect(concealed.ending).toBe('concealed');
    expect(concealed.caseReview.submittedOutcome).toBe('conceal');
  });
});

describe('Furnace Gallery state transitions', () => {
  it('enters and leaves the Furnace Gallery through the corridor', () => {
    const furnace = reachFurnace();

    expect(furnace.room).toBe('furnace');
    expect(inspect(furnace, 'furnace', 'to-corridor').room).toBe('corridor');
  });

  it('records the furnace evidence and collects its optional heat glove', () => {
    const state = inspect(reachFurnace(), 'furnace', 'furnace-tag');

    expect(state.evidence).toContain('furnace-tag');
    expect(state.inventory).toContain('heat-glove');
  });

  it('changes Niko dialogue after the worker decision without ending the game', () => {
    const met = inspect(reachFurnace(), 'furnace', 'niko');
    const decided = decideWorker(met, 'report');
    const later = inspect(decided, 'furnace', 'niko');

    expect(met.workerMet).toBe(true);
    expect(decided.workerChoice).toBe('report');
    expect(later.dialogue[0]).toContain('Mara knows');
    expect(later.screen).toBe('play');
    expect(later.ending).toBeNull();
  });

  it('persists all Furnace Gallery state through save and load', () => {
    let state = inspect(reachFurnace(), 'furnace', 'furnace-tag');
    state = inspect(state, 'furnace', 'niko');
    state = decideWorker(state, 'keep-quiet');

    saveGame(state);

    expect(loadGame()).toEqual(state);
  });

  it('persists case-review selections and postponed outcome through save and load', () => {
    let state = openReview();
    state = selectCaseTheory(state, 'industrial-accident');
    state = toggleCaseEvidence(state, 'furnace-scar');
    state = toggleCaseEvidence(state, 'repair-outcome');
    state = postponeCaseReview(state);

    saveGame(state);

    expect(loadGame()).toEqual(state);
  });

  it('applies safe defaults when loading a save from before case review existed', () => {
    storage.set('glasspunk-vesper-save', JSON.stringify({
      screen: 'play', room: 'control', inventory: ['fuse'], evidence: ['shift-log', 'breaker-note'],
      panelSolved: true, maraKeyGiven: true, ending: null,
    }));

    const loaded = loadGame();
    expect(loaded?.caseReviewUnlocked).toBe(true);
    expect(loaded?.caseReview).toEqual({ theory: null, selectedEvidence: [], submittedOutcome: null, evaluation: null });
    expect(loaded?.workerMet).toBe(false);
    expect(loaded?.workerChoice).toBeNull();
  });
});

import {
  caseEvidenceDefinitions,
  clues,
  initialMessage,
  items,
  rooms,
  theories,
  type CaseDecision,
  type CaseEvidenceId,
  type ClueId,
  type Hotspot,
  type ItemId,
  type TheoryId,
} from './data';
import {
  addEvidence,
  addItem,
  availableCaseEvidence,
  canRepairPanel,
  evaluateCase,
  resolveEnding,
  validateCaseSelection,
  type CaseEvaluation,
  type LogicState,
} from './logic';

export type GameScreen = 'title' | 'play' | 'review' | 'ending';
export type WorkerChoice = 'report' | 'keep-quiet';

export interface CaseReviewState {
  theory: TheoryId | null;
  selectedEvidence: CaseEvidenceId[];
  submittedOutcome: CaseDecision | null;
  evaluation: CaseEvaluation | null;
}

export interface GameState extends LogicState {
  screen: GameScreen;
  selectedItem: ItemId | null;
  message: string;
  dialogue: string[];
  muted: boolean;
  workerMet: boolean;
  workerChoice: WorkerChoice | null;
  caseReviewUnlocked: boolean;
  caseReview: CaseReviewState;
}

export const SAVE_KEY = 'glasspunk-vesper-save';

export function newGame(): GameState {
  return {
    screen: 'title', room: 'control', inventory: [], evidence: [], panelSolved: false,
    maraKeyGiven: false, ending: null, selectedItem: null, message: initialMessage,
    dialogue: [], muted: false, workerMet: false, workerChoice: null,
    caseReviewUnlocked: false,
    caseReview: { theory: null, selectedEvidence: [], submittedOutcome: null, evaluation: null },
  };
}

export function beginGame(state: GameState): GameState {
  return { ...state, screen: 'play', message: 'The emergency lights hum. Search the room.', dialogue: [] };
}

export function restartGame(): GameState { return newGame(); }

function withMessage(state: GameState, message: string): GameState {
  return { ...state, message, dialogue: [] };
}

function discoverClue(state: GameState, clueId: ClueId, itemId?: ItemId): GameState {
  const withClue = addEvidence(state, clueId);
  const next = itemId ? addItem(withClue, itemId) : withClue;
  const isNew = next.evidence.length > state.evidence.length;
  const foundItem = itemId && next.inventory.length > state.inventory.length;
  if (!isNew) return withMessage(state, 'You have already logged that clue.');
  const itemMessage = foundItem ? ` You also find a ${items[itemId].label.toLowerCase()}.` : '';
  return withMessage(next, `${clues[clueId].title}: ${clues[clueId].text}${itemMessage}`);
}

export function inspectHotspot(state: GameState, hotspot: Hotspot): GameState {
  if (state.screen === 'title') return beginGame(state);
  if (state.screen !== 'play') return state;

  if (hotspot.action === 'move' && hotspot.target) {
    return { ...state, room: hotspot.target, selectedItem: null, message: rooms[hotspot.target].description, dialogue: [] };
  }
  if (hotspot.action === 'clue' && hotspot.clueId) return discoverClue(state, hotspot.clueId, hotspot.itemId);
  if (hotspot.action === 'locker') {
    if (!state.inventory.includes('maintenance-key')) return withMessage(state, 'The red locker is locked. Mara may have the key.');
    if (state.inventory.includes('fuse')) return withMessage(state, 'The red locker is empty.');
    return withMessage(addItem(state, 'fuse'), 'You unlock the locker and take the ceramic fuse.');
  }
  if (hotspot.action === 'npc') return hotspot.npcId === 'niko' ? talkToNiko(state) : talkToMara(state);
  if (hotspot.action === 'console') return useConsole(state);
  if (hotspot.action === 'case-review') return openCaseReview(state);
  return withMessage(state, hotspot.label);
}

export function talkToMara(state: GameState): GameState {
  if (!state.evidence.includes('shift-log')) {
    return { ...state, dialogue: ['MARA: The panel is not a guessing game.', 'MARA: Read the shift log, then come back.'], message: 'Mara folds her arms.' };
  }
  if (!state.maraKeyGiven) {
    return {
      ...addItem({ ...state, maraKeyGiven: true }, 'maintenance-key'),
      dialogue: ['MARA: Blue tape. Left socket. That is the whole story.', 'MARA: Take my maintenance key. The spare fuse is in the red locker.'],
      message: 'Mara hands over a square brass key.',
    };
  }
  if (!state.panelSolved) return { ...state, dialogue: ['MARA: Fuse first. Then left socket.', 'MARA: Do not touch the right side.'], message: 'Mara watches the dead console.' };
  return { ...state, dialogue: ['MARA: Lights are coming back.', 'MARA: Vesper Station owes you a coffee.'], message: 'Mara gives you a tired salute.' };
}

export function talkToNiko(state: GameState): GameState {
  if (state.room !== 'furnace') return state;
  if (!state.workerMet) {
    return {
      ...state,
      workerMet: true,
      dialogue: ['NIKO: The furnace tripped before the blackout.', 'NIKO: Should I tell Mara the shift log was altered? Press Y to report it, or N to keep quiet.'],
      message: 'Niko waits beside the cold furnace.',
    };
  }
  if (!state.workerChoice) {
    return { ...state, dialogue: ['NIKO: I am still waiting on your answer.', 'NIKO: Press Y to report the altered line, or N to keep quiet.'], message: 'Niko glances at the service tag.' };
  }
  if (state.workerChoice === 'report') {
    return { ...state, dialogue: ['NIKO: Mara knows the furnace tripped first.', 'NIKO: The altered line is marked now.'], message: 'Niko nods toward the control room.' };
  }
  return { ...state, dialogue: ['NIKO: The furnace story stays between us.', 'NIKO: The altered line stays unmarked.'], message: 'Niko returns to his silent watch.' };
}

export function decideWorker(state: GameState, choice: WorkerChoice): GameState {
  if (state.screen !== 'play' || state.room !== 'furnace' || !state.workerMet || state.workerChoice) return state;
  if (choice === 'report') {
    return { ...state, workerChoice: choice, dialogue: ['NIKO: I will tell Mara the final line was altered.', 'NIKO: The furnace log and station log can agree now.'], message: 'You ask Niko to report the altered shift log.' };
  }
  return { ...state, workerChoice: choice, dialogue: ['NIKO: Quiet, then. I will keep the furnace note to myself.', 'NIKO: Not every shift needs another report.'], message: 'You ask Niko to keep the alteration quiet.' };
}

export function useSelectedItem(state: GameState): GameState {
  if (state.screen !== 'play' || state.room !== 'control') return state;
  if (state.selectedItem !== 'fuse') return withMessage(state, 'Select the ceramic fuse before using the console.');
  if (!canRepairPanel(state)) return withMessage(state, 'The fuse fits, but the socket markings are unclear. Find the breaker note.');
  return {
    ...state,
    panelSolved: true,
    caseReviewUnlocked: true,
    selectedItem: null,
    message: 'The left socket catches. Vesper Station wakes in a blue-white flash. Case Review is now online.',
    dialogue: [],
  };
}

export function useConsole(state: GameState): GameState {
  if (state.panelSolved) return withMessage(state, 'The console is alive. The Case Review terminal is unlocked.');
  if (state.selectedItem === 'maintenance-key') {
    return finishGame({ ...state, selectedItem: null }, 'failure');
  }
  if (state.selectedItem === 'fuse') return useSelectedItem(state);
  return withMessage(state, 'The console has two sockets. Select an item before you use it.');
}

export function finishGame(state: GameState, outcome: 'success' | 'failure'): GameState {
  return { ...state, screen: 'ending', ending: outcome, dialogue: [], selectedItem: null,
    message: outcome === 'success' ? 'CASE CLOSED: The blackout was a preventable bypass.' : 'CASE LOST: The station stays dark.' };
}

export function selectItem(state: GameState, item: ItemId | null): GameState {
  if (state.screen !== 'play') return state;
  return { ...state, selectedItem: state.selectedItem === item ? null : item };
}

export function toggleMute(state: GameState): GameState { return { ...state, muted: !state.muted }; }

export function saveGame(state: GameState): void { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); }

export function loadGame(): GameState | null {
  const raw = localStorage.getItem(SAVE_KEY);
  if (!raw) return null;
  try {
    const saved = JSON.parse(raw) as Partial<GameState>;
    if (!saved.screen || !saved.room || !Array.isArray(saved.inventory)) return null;
    const defaults = newGame();
    const savedReview = saved.caseReview;
    const selectedEvidence = Array.isArray(savedReview?.selectedEvidence)
      ? savedReview.selectedEvidence.filter(isCaseEvidenceId)
      : [];
    const theory = isTheoryId(savedReview?.theory) ? savedReview.theory : null;
    const submittedOutcome = isCaseDecision(savedReview?.submittedOutcome) ? savedReview.submittedOutcome : null;
    return {
      ...defaults,
      ...saved,
      workerMet: saved.workerMet ?? false,
      workerChoice: saved.workerChoice ?? null,
      evidence: Array.isArray(saved.evidence) ? saved.evidence : [],
      caseReviewUnlocked: saved.caseReviewUnlocked ?? Boolean(saved.panelSolved),
      caseReview: {
        theory,
        selectedEvidence,
        submittedOutcome,
        evaluation: savedReview?.evaluation ?? null,
      },
    } as GameState;
  } catch { return null; }
}

export function currentRoom(state: Pick<GameState, 'room'>) { return rooms[state.room]; }

export function itemLabel(item: ItemId): string { return items[item].label; }

export function endFromPanel(state: GameState): GameState { return finishGame(state, resolveEnding(state)); }

export function openCaseReview(state: GameState): GameState {
  if (state.screen !== 'play' || state.room !== 'control') return state;
  if (!state.panelSolved || !state.caseReviewUnlocked) return withMessage(state, 'The Case Review terminal is offline. Repair the control console first.');
  return {
    ...state,
    screen: 'review',
    selectedItem: null,
    dialogue: [],
    message: 'Choose one explanation and cite at least two collected evidence items.',
  };
}

export function selectCaseTheory(state: GameState, theory: TheoryId): GameState {
  if (state.screen !== 'review' || !theories[theory]) return state;
  return {
    ...state,
    caseReview: { ...state.caseReview, theory, evaluation: null },
    message: `${theories[theory].label}. Select at least two supporting evidence items.`,
  };
}

export function toggleCaseEvidence(state: GameState, evidenceId: CaseEvidenceId): GameState {
  if (state.screen !== 'review' || !availableCaseEvidence(state).includes(evidenceId)) return state;
  const selectedEvidence = state.caseReview.selectedEvidence.includes(evidenceId)
    ? state.caseReview.selectedEvidence.filter((id) => id !== evidenceId)
    : [...state.caseReview.selectedEvidence, evidenceId];
  return {
    ...state,
    caseReview: { ...state.caseReview, selectedEvidence, evaluation: null },
    message: `${selectedEvidence.length} evidence item${selectedEvidence.length === 1 ? '' : 's'} selected.`,
  };
}

function evidenceTitles(evidence: { title: string }[]): string {
  return evidence.length ? evidence.map((finding) => finding.title).join(', ') : 'none';
}

function reportMessage(evaluation: CaseEvaluation): string {
  const theory = theories[evaluation.theory].label;
  const supported = evidenceTitles(evaluation.supporting);
  const contradicted = evidenceTitles(evaluation.contradicting);
  if (evaluation.verdict === 'strong') {
    return `STRONGLY SUPPORTED CONCLUSION: ${theory}. Supported by ${supported}. Contradicted by none.`;
  }
  if (evaluation.verdict === 'plausible') {
    return `PLAUSIBLE BUT INCOMPLETE CONCLUSION: ${theory}. Supported by ${supported}. Contradicted by ${contradicted}.`;
  }
  return `INCORRECT ACCUSATION: ${theory}. Supported by ${supported}. Contradicted by ${contradicted}.`;
}

export function submitCaseReview(state: GameState): GameState {
  if (state.screen !== 'review') return state;
  const availableEvidence = availableCaseEvidence(state);
  const validation = validateCaseSelection({
    theory: state.caseReview.theory,
    selectedEvidence: state.caseReview.selectedEvidence,
    availableEvidence,
  });
  if (!validation.valid || !state.caseReview.theory) return withMessage(state, validation.message);
  const evaluation = evaluateCase({ theory: state.caseReview.theory, selectedEvidence: state.caseReview.selectedEvidence });
  return {
    ...state,
    screen: 'ending',
    ending: evaluation.verdict,
    dialogue: [],
    selectedItem: null,
    message: reportMessage(evaluation),
    caseReview: { ...state.caseReview, submittedOutcome: 'report', evaluation },
  };
}

export function concealFindings(state: GameState): GameState {
  if (state.screen !== 'review') return state;
  return {
    ...state,
    screen: 'ending',
    ending: 'concealed',
    dialogue: [],
    selectedItem: null,
    message: 'CONCEALED FINDINGS: You seal the case review without naming a cause. The station keeps its silence.',
    caseReview: { ...state.caseReview, submittedOutcome: 'conceal' },
  };
}

export function postponeCaseReview(state: GameState): GameState {
  if (state.screen !== 'review') return state;
  return {
    ...state,
    screen: 'play',
    caseReview: { ...state.caseReview, submittedOutcome: 'postpone' },
    message: 'You postpone the decision. The selected theory and evidence remain on the terminal.',
    dialogue: [],
  };
}

function isCaseEvidenceId(value: unknown): value is CaseEvidenceId {
  return typeof value === 'string' && value in caseEvidenceDefinitions;
}

function isTheoryId(value: unknown): value is TheoryId {
  return value === 'industrial-accident' || value === 'worker-sabotage' || value === 'management-cover-up';
}

function isCaseDecision(value: unknown): value is CaseDecision {
  return value === 'report' || value === 'conceal' || value === 'postpone';
}

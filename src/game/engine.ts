import {
  caseEvidenceDefinitions,
  clues,
  initialMessage,
  items,
  rooms,
  serviceNotes,
  theories,
  type CaseDecision,
  type CaseEvidenceId,
  type ClueId,
  type Hotspot,
  type ItemId,
  type ServiceNoteId,
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
export type DispatchChoice = 'record-first' | 'render-first';

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
  workerMet: boolean;
  workerChoice: WorkerChoice | null;
  caseReviewUnlocked: boolean;
  caseReview: CaseReviewState;
  serviceNotes: ServiceNoteId[];
  returnOpen: boolean;
  pumpRunning: boolean;
  dispatchOpen: boolean;
  dispatchChoice: DispatchChoice | null;
}

export const SAVE_KEY = 'glasspunk-vesper-save';

export function newGame(): GameState {
  return {
    screen: 'title', room: 'control', inventory: [], evidence: [], panelSolved: false,
    maraKeyGiven: false, ending: null, selectedItem: null, message: initialMessage,
    dialogue: [], workerMet: false, workerChoice: null,
    caseReviewUnlocked: false,
    caseReview: { theory: null, selectedEvidence: [], submittedOutcome: null, evaluation: null },
    serviceNotes: [], returnOpen: false, pumpRunning: false, dispatchOpen: false, dispatchChoice: null,
  };
}

export function beginGame(state: GameState): GameState {
  return { ...state, screen: 'play', message: 'Toledo river edge, 2075. Vesper’s lights went out at 02:13. Mara wants the morning handoff ready; Niko wants to get home. The shift log is your first stop.', dialogue: [] };
}

export function restartGame(): GameState { return newGame(); }

function withMessage(state: GameState, message: string): GameState {
  return { ...state, message, dialogue: [], dispatchOpen: false };
}

function discoverClue(state: GameState, clueId: ClueId, itemId?: ItemId): GameState {
  const withClue = addEvidence(state, clueId);
  const next = itemId ? addItem(withClue, itemId) : withClue;
  const isNew = next.evidence.length > state.evidence.length;
  const foundItem = itemId && next.inventory.length > state.inventory.length;
  if (!isNew) return withMessage(state, `${clues[clueId].title}: ${clues[clueId].text}`);
  const itemMessage = foundItem ? ` You also find a ${items[itemId].label.toLowerCase()}.` : '';
  return withMessage(next, `${clues[clueId].title}: ${clues[clueId].text}${itemMessage}`);
}

export function inspectHotspot(state: GameState, hotspot: Hotspot): GameState {
  if (state.screen === 'title') return beginGame(state);
  if (state.screen !== 'play') return state;
  const local = rooms[state.room].hotspots.find((entry) => entry.id === hotspot.id);
  if (!local) return state;
  hotspot = local;

  if (hotspot.action === 'move' && hotspot.target) {
    if ((hotspot.target === 'pump' || hotspot.target === 'terrace') && !state.panelSolved) return withMessage(state, 'The service door has no power. Restore the control-room lights first.');
    const message = hotspot.target === 'terrace' && !state.pumpRunning
      ? 'Maumee water reflects the night lights. The dispatch terminal waits for steady circulation.'
      : rooms[hotspot.target].description;
    return { ...state, room: hotspot.target, selectedItem: null, message, dialogue: [], dispatchOpen: false };
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
  if (hotspot.action === 'service-note' && hotspot.noteId) {
    const note = serviceNotes[hotspot.noteId];
    return withMessage({ ...state, serviceNotes: [...new Set([...state.serviceNotes, hotspot.noteId])] }, `${note.title}: ${note.text}`);
  }
  if (hotspot.action === 'valve') return openReturn(state);
  if (hotspot.action === 'pump') return startPump(state);
  if (hotspot.action === 'dispatch') {
    if (!state.pumpRunning) return withMessage(state, 'Dispatch waits for stable circulation. Get the return pump running first.');
    if (!state.serviceNotes.includes('dispatch-card')) return withMessage(state, 'Read the dispatch slip before choosing which job goes first.');
    return { ...state, dispatchOpen: true, dialogue: [], message: 'Which job goes first when you file the handoff? Send the maintenance record and delay the render, or finish the render and queue the record for morning. You can change the order until filing.' };
  }
  if (hotspot.action === 'view') return withMessage(state, state.pumpRunning
    ? 'A heron picks its way along the reeds. Warmth hums through the district loop behind you. Somewhere across the water, a roof is waiting to become a picture.'
    : 'A heron waits in the reeds. A bridge, glass roofs and gantry cranes break the horizon. The river keeps moving while the station does not.');
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
  if (!state.pumpRunning) return { ...state, dialogue: ['MARA: Lights. Lovely. Now the return pump is sulking.', 'MARA: Pump house, off the corridor. Niko has a glove. I have a coffee that was hot yesterday.'], message: 'Mara taps the cold mug.' };
  return { ...state, dialogue: ['MARA: Circulation steady. You have earned the good mug.', 'MARA: File what you found, not what you wish happened. Then we go home.'], message: 'Mara puts two mugs by the console.' };
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
    message: 'The left socket catches. Lights return! A second lamp blinks: RETURN PUMP STOPPED. Mara points you toward the pump-house door in the corridor.',
    dialogue: [],
  };
}

export function useConsole(state: GameState): GameState {
  if (state.panelSolved) return withMessage(state, state.pumpRunning ? 'Lights and circulation are steady. File the handoff at the Case Review terminal.' : 'Lights are steady. The return pump is stopped: use the pump-house door in the corridor.');
  if (state.selectedItem === 'maintenance-key') {
    return withMessage(state, 'Mara catches your wrist. “Key for the locker. Ceramic fuse for the console. I like my eyebrows.” Nothing damaged; try another tool.');
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
  if (item && !state.inventory.includes(item)) return state;
  return { ...state, selectedItem: state.selectedItem === item ? null : item };
}

export function saveGame(state: GameState): boolean {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); return true; } catch { return false; }
}

export function loadGame(): GameState | null {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    const saved = JSON.parse(raw) as Partial<GameState> | null;
    if (!saved || !['title', 'play', 'review', 'ending'].includes(saved.screen ?? '') || !ownKey(rooms, saved.room) || !Array.isArray(saved.inventory)) return null;
    const defaults = newGame();
    const savedReview = saved.caseReview;
    const selectedEvidence = Array.isArray(savedReview?.selectedEvidence)
      ? savedReview.selectedEvidence.filter(isCaseEvidenceId)
      : [];
    const theory = isTheoryId(savedReview?.theory) ? savedReview.theory : null;
    const submittedOutcome = isCaseDecision(savedReview?.submittedOutcome) ? savedReview.submittedOutcome : null;
    const panelSolved = saved.panelSolved === true;
    const next: GameState = {
      ...defaults,
      screen: saved.screen as GameScreen,
      room: saved.room as keyof typeof rooms,
      inventory: uniqueKnown(saved.inventory, items),
      selectedItem: ownKey(items, saved.selectedItem) && saved.inventory.includes(saved.selectedItem!) ? saved.selectedItem! : null,
      message: typeof saved.message === 'string' ? saved.message : defaults.message,
      dialogue: Array.isArray(saved.dialogue) ? saved.dialogue.filter((line): line is string => typeof line === 'string') : [],
      panelSolved,
      maraKeyGiven: saved.maraKeyGiven === true,
      ending: ['success', 'failure', 'strong', 'plausible', 'incorrect', 'concealed'].includes(saved.ending ?? '') ? saved.ending! : null,
      workerMet: saved.workerMet === true,
      workerChoice: saved.workerChoice === 'report' || saved.workerChoice === 'keep-quiet' ? saved.workerChoice : null,
      evidence: uniqueKnown(saved.evidence, clues),
      caseReviewUnlocked: panelSolved,
      serviceNotes: uniqueKnown(saved.serviceNotes, serviceNotes),
      returnOpen: panelSolved && saved.returnOpen === true,
      pumpRunning: panelSolved && saved.returnOpen === true && saved.pumpRunning === true,
      dispatchOpen: false,
      dispatchChoice: panelSolved && saved.returnOpen === true && saved.pumpRunning === true && (saved.dispatchChoice === 'record-first' || saved.dispatchChoice === 'render-first') ? saved.dispatchChoice : null,
      caseReview: {
        theory,
        selectedEvidence: [...new Set(selectedEvidence)],
        submittedOutcome,
        evaluation: null,
      },
    };
    next.caseReview.selectedEvidence = next.caseReview.selectedEvidence.filter((id) => availableCaseEvidence(next).includes(id));
    if (next.caseReview.theory && submittedOutcome === 'report') next.caseReview.evaluation = evaluateCase({ theory: next.caseReview.theory, selectedEvidence: next.caseReview.selectedEvidence });
    if (!panelSolved && (next.room === 'pump' || next.room === 'terrace')) next.room = 'corridor';
    if (next.screen === 'review' && (!panelSolved || !next.pumpRunning || !next.dispatchChoice)) {
      next.screen = 'play'; next.room = 'control';
      next.message = 'Your saved case notes are preserved. This shift now includes a pump-house repair and terrace dispatch before the final handoff.';
      next.dialogue = [];
    }
    return next;
  } catch { return null; }
}

export function currentRoom(state: Pick<GameState, 'room'>) { return rooms[state.room]; }

export function itemLabel(item: ItemId): string { return items[item].label; }

export function endFromPanel(state: GameState): GameState { return finishGame(state, resolveEnding(state)); }

export function openCaseReview(state: GameState): GameState {
  if (state.screen !== 'play' || state.room !== 'control') return state;
  if (!state.panelSolved || !state.caseReviewUnlocked) return withMessage(state, 'The Case Review terminal is offline. Repair the control console first.');
  if (!state.pumpRunning || !state.dispatchChoice) return withMessage(state, 'Finish the handoff first: restore the pump-house loop, then choose a dispatch job on the river terrace. The case notes will wait.');
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
    message: `${caseEvidenceDefinitions[evidenceId].title}: ${caseEvidenceDefinitions[evidenceId].text} ${selectedEvidence.length} evidence item${selectedEvidence.length === 1 ? '' : 's'} selected.`,
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
  if (!state.panelSolved || !state.pumpRunning || !state.dispatchChoice) return { ...withMessage(state, 'Finish the service handoff before filing your explanation.'), screen: 'play', room: 'control' };
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
    message: `${reportMessage(evaluation)} ${handoffEnding(state)}`,
    caseReview: { ...state.caseReview, submittedOutcome: 'report', evaluation },
  };
}

export function concealFindings(state: GameState): GameState {
  if (state.screen !== 'review') return state;
  if (!state.panelSolved || !state.pumpRunning || !state.dispatchChoice) return { ...withMessage(state, 'Finish the service handoff before sealing your explanation.'), screen: 'play', room: 'control' };
  return {
    ...state,
    screen: 'ending',
    ending: 'concealed',
    dialogue: [],
    selectedItem: null,
    message: `CAUSE WITHHELD: You seal your explanation of the blackout. The routine maintenance record still follows your dispatch choice. ${handoffEnding(state)}`,
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
  return ownKey(caseEvidenceDefinitions, value);
}

function isTheoryId(value: unknown): value is TheoryId {
  return value === 'industrial-accident' || value === 'worker-sabotage' || value === 'management-cover-up';
}

function isCaseDecision(value: unknown): value is CaseDecision {
  return value === 'report' || value === 'conceal' || value === 'postpone';
}

function ownKey(object: object, value: unknown): boolean {
  return typeof value === 'string' && Object.prototype.hasOwnProperty.call(object, value);
}

function uniqueKnown<T extends string>(value: unknown, definitions: Record<T, unknown>): T[] {
  return Array.isArray(value) ? [...new Set(value.filter((id): id is T => ownKey(definitions, id)))] : [];
}

export function openReturn(state: GameState): GameState {
  if (state.screen !== 'play' || state.room !== 'pump' || !state.panelSolved) return state;
  if (state.returnOpen) return withMessage(state, 'The RETURN wheel is already open. The pump can start.');
  if (!state.serviceNotes.includes('pump-card')) return withMessage(state, 'Two pipes, one warm wheel. Read the loop card before touching it.');
  if (state.selectedItem !== 'heat-glove' || !state.inventory.includes('heat-glove')) return withMessage(state, 'Warm metal. Select the heat glove from Niko’s furnace service tag first.');
  return withMessage({ ...state, returnOpen: true, selectedItem: null }, 'Glove on. The RETURN wheel yields with a squeak. An arrow flips to OPEN. Now try the pump starter.');
}

export function startPump(state: GameState): GameState {
  if (state.screen !== 'play' || state.room !== 'pump' || !state.panelSolved) return state;
  if (state.pumpRunning) return withMessage(state, 'The pump purrs. This is the nicest noise of the whole shift.');
  if (!state.returnOpen) return withMessage(state, 'The interlock stays dark: RETURN CLOSED. Read the loop card and open the return wheel first.');
  return withMessage({ ...state, pumpRunning: true }, 'The checks take a while. At last the pump settles into a purr, with dawn at the windows. Heat circulates again. Niko calls: “Now THAT sounds like going home.” The terrace dispatch terminal is ready.');
}

export function decideDispatch(state: GameState, choice: DispatchChoice): GameState {
  if (state.screen !== 'play' || state.room !== 'terrace' || !state.pumpRunning || !state.dispatchOpen || !state.serviceNotes.includes('dispatch-card')) return state;
  return withMessage({ ...state, dispatchChoice: choice }, choice === 'record-first'
    ? 'RECORD FIRST: ready to send the dated observations to the Reading Hall at handoff, with the roof render delayed until morning. A radio crackles. Niko: “Good. Someone else can read that handwriting.” Return to Mara’s Case Review terminal to file.'
    : 'RENDER FIRST: a Glass City roof preview blooms on the terminal. At handoff, the render finishes and the dated observations queue for morning. A radio crackles. Niko: “That roof looks like a jellyfish.” Return to Mara’s Case Review terminal to file.');
}

export function handoffEnding(state: GameState): string {
  if (!state.pumpRunning || !state.dispatchChoice) return 'The service handoff is still unfinished. You can continue the shift.';
  const dispatch = state.dispatchChoice === 'record-first'
    ? 'The Reading Hall has the maintenance record; the roof render waits for morning.'
    : 'The roof render is finished; the Reading Hall record waits in the morning queue.';
  return `${dispatch} Lights steady, heat circulating. Mara hands you the good mug. Niko takes the river path home, past a heron that has done absolutely no paperwork.`;
}

export function currentGoal(state: GameState): string {
  if (state.screen === 'title') return 'One night shift. Two repairs. Get the morning handoff ready.';
  if (state.screen === 'ending') return state.pumpRunning ? 'Shift complete. Try the other dispatch choice, or explore the Atlas.' : 'Continue the shift or start again.';
  if (!state.panelSolved) return '1 / 3 · Restore the control-room lights.';
  if (!state.pumpRunning) return '2 / 3 · Restore circulation in the pump house.';
  if (!state.dispatchChoice) return '3 / 3 · Choose a terrace dispatch job, then file the blackout case.';
  return 'File your explanation at the control-room Case Review terminal.';
}

export function requestHint(state: GameState): GameState {
  if (state.screen !== 'play') return state;
  let hint: string;
  if (!state.evidence.includes('shift-log')) hint = 'Read the shift log on the control-room desk. Mara will talk after that.';
  else if (!state.maraKeyGiven) hint = 'Ask Mara in the control room for the maintenance key.';
  else if (!state.inventory.includes('fuse')) hint = 'The corridor’s red locker holds the ceramic fuse. Mara’s key unlocks it.';
  else if (!state.evidence.includes('breaker-note')) hint = 'Read the breaker note in the corridor. It identifies the correct socket.';
  else if (!state.panelSolved) hint = 'In the control room, select the ceramic fuse in inventory, then inspect the console.';
  else if (!state.serviceNotes.includes('pump-card')) hint = 'The pump-house door is below the corridor breaker. Read the loop card inside.';
  else if (!state.inventory.includes('heat-glove')) hint = 'Niko’s furnace service tag has a glove hanging beside it. Inspect the tag.';
  else if (!state.returnOpen) hint = 'In the pump house, select the heat glove, then inspect the RETURN wheel.';
  else if (!state.pumpRunning) hint = 'The return is open. Press the pump starter in the pump house.';
  else if (!state.dispatchChoice) hint = 'Beyond the pump house is the river terrace. Read the dispatch slip, then use its terminal.';
  else hint = 'Return to the control room’s Case Review terminal. Cite two supporting clues; you may explore for more before filing.';
  return withMessage(state, `MARA’S HINT: ${hint}`);
}

export function continueShift(state: GameState): GameState {
  if (state.screen !== 'ending') return state;
  return withMessage({ ...state, screen: 'play', ending: null, room: 'control', caseReview: { ...state.caseReview, submittedOutcome: null, evaluation: null } }, 'Replay from just before the final handoff. Your repairs and notes are preserved; you can try another queue order or explanation.');
}

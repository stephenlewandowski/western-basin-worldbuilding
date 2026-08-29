import { caseEvidenceDefinitions, caseEvidenceOrder, type CaseEvidenceId, type ClueId, type ItemId, type RoomId, type TheoryId } from './data';

export type EndingId = 'success' | 'failure' | 'strong' | 'plausible' | 'incorrect' | 'concealed';

export interface LogicState {
  room: RoomId;
  inventory: ItemId[];
  evidence: ClueId[];
  panelSolved: boolean;
  maraKeyGiven: boolean;
  ending: EndingId | null;
}

export interface CaseFinding {
  evidenceId: CaseEvidenceId;
  title: string;
  explanation: string;
  score: number;
}

export interface CaseEvaluation {
  theory: TheoryId;
  score: number;
  verdict: 'strong' | 'plausible' | 'incorrect';
  supporting: CaseFinding[];
  contradicting: CaseFinding[];
}

export function hasItem(state: Pick<LogicState, 'inventory'>, item: ItemId): boolean {
  return state.inventory.includes(item);
}

export function addItem<T extends Pick<LogicState, 'inventory'>>(state: T, item: ItemId): T {
  if (hasItem(state, item)) return state;
  return { ...state, inventory: [...state.inventory, item] };
}

export function addEvidence<T extends Pick<LogicState, 'evidence'>>(state: T, clue: ClueId): T {
  if (state.evidence.includes(clue)) return state;
  return { ...state, evidence: [...state.evidence, clue] };
}

export function canRepairPanel(state: Pick<LogicState, 'inventory' | 'evidence'>): boolean {
  return hasItem(state, 'fuse') && state.evidence.includes('breaker-note');
}

export function resolveEnding(state: Pick<LogicState, 'panelSolved' | 'evidence'>): 'success' | 'failure' {
  return state.panelSolved && state.evidence.includes('shift-log') && state.evidence.includes('breaker-note')
    ? 'success'
    : 'failure';
}

type CaseEvidenceState = Pick<LogicState, 'evidence' | 'maraKeyGiven' | 'panelSolved'> & {
  workerChoice: 'report' | 'keep-quiet' | null;
};

function requirementAvailable(state: CaseEvidenceState, id: CaseEvidenceId): boolean {
  const requirement = caseEvidenceDefinitions[id].requirement;
  if (requirement.kind === 'clue') return state.evidence.includes(requirement.clueId);
  if (requirement.kind === 'mara-testimony') return state.maraKeyGiven;
  if (requirement.kind === 'niko-report') return state.workerChoice === 'report';
  if (requirement.kind === 'niko-silence') return state.workerChoice === 'keep-quiet';
  return state.panelSolved;
}

export function availableCaseEvidence(state: CaseEvidenceState): CaseEvidenceId[] {
  return caseEvidenceOrder.filter((id) => requirementAvailable(state, id));
}

export interface CaseSelectionValidation {
  valid: boolean;
  message: string;
}

export function validateCaseSelection(input: {
  theory: TheoryId | null;
  selectedEvidence: CaseEvidenceId[];
  availableEvidence?: CaseEvidenceId[];
}): CaseSelectionValidation {
  if (!input.theory) return { valid: false, message: 'Choose one explanation before submitting the report.' };
  const selected = [...new Set(input.selectedEvidence)];
  if (selected.length < 2) return { valid: false, message: 'Select at least two evidence items supporting the explanation.' };
  if (input.availableEvidence && selected.some((id) => !input.availableEvidence?.includes(id))) {
    return { valid: false, message: 'Only collected evidence can be cited in the report.' };
  }
  const supporting = selected.filter((id) => (caseEvidenceDefinitions[id].effects[input.theory!]?.score ?? 0) > 0);
  if (supporting.length < 2) return { valid: false, message: 'Select at least two evidence items that support this explanation.' };
  return { valid: true, message: 'The report is ready to submit.' };
}

export function evaluateCase(input: {
  theory: TheoryId;
  selectedEvidence: CaseEvidenceId[];
}): CaseEvaluation {
  const selected = [...new Set(input.selectedEvidence)];
  const findings = selected.flatMap((evidenceId) => {
    const effect = caseEvidenceDefinitions[evidenceId].effects[input.theory];
    if (!effect) return [];
    return [{
      evidenceId,
      title: caseEvidenceDefinitions[evidenceId].title,
      explanation: effect.explanation,
      score: effect.score,
    }];
  });
  const supporting = findings.filter((finding) => finding.score > 0);
  const contradicting = findings.filter((finding) => finding.score < 0);
  const score = findings.reduce((total, finding) => total + finding.score, 0);
  const verdict = score >= 5 && contradicting.length === 0
    ? 'strong'
    : score >= 2
      ? 'plausible'
      : 'incorrect';
  return { theory: input.theory, score, verdict, supporting, contradicting };
}

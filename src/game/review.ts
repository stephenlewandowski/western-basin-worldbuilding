import { caseEvidenceDefinitions, theories, type CaseDecision, type CaseEvidenceId, type TheoryId } from './data';
import { availableCaseEvidence } from './logic';
import type { GameState } from './engine';

export const REVIEW_THEORY_Y = 24;
export const REVIEW_EVIDENCE_Y = 68;
export const REVIEW_ACTION_Y = 181;

export type ReviewTarget =
  | { kind: 'theory'; id: TheoryId }
  | { kind: 'evidence'; id: CaseEvidenceId }
  | { kind: 'action'; id: CaseDecision };

export function reviewTargetKey(target: ReviewTarget): string {
  return `review:${target.kind}:${target.id}`;
}

export function reviewTargets(state: GameState): ReviewTarget[] {
  const theoryTargets: ReviewTarget[] = Object.keys(theories).map((id) => ({ kind: 'theory', id: id as TheoryId }));
  const evidenceTargets: ReviewTarget[] = availableCaseEvidence(state).map((id) => ({ kind: 'evidence', id }));
  const actionTargets: ReviewTarget[] = [
    { kind: 'action', id: 'report' },
    { kind: 'action', id: 'conceal' },
    { kind: 'action', id: 'postpone' },
  ];
  return [...theoryTargets, ...evidenceTargets, ...actionTargets];
}

export function reviewTargetAt(x: number, y: number, state: GameState): ReviewTarget | undefined {
  if (y >= REVIEW_THEORY_Y && y < REVIEW_THEORY_Y + 3 * 14 && x >= 5 && x <= 315) {
    const index = Math.floor((y - REVIEW_THEORY_Y) / 14);
    const id = Object.keys(theories)[index] as TheoryId | undefined;
    return id ? { kind: 'theory', id } : undefined;
  }
  const evidence = availableCaseEvidence(state);
  if (y >= REVIEW_EVIDENCE_Y && y < REVIEW_EVIDENCE_Y + evidence.length * 10 && x >= 5 && x <= 315) {
    const index = Math.floor((y - REVIEW_EVIDENCE_Y) / 10);
    const id = evidence[index];
    return id ? { kind: 'evidence', id } : undefined;
  }
  if (y >= REVIEW_ACTION_Y && y < REVIEW_ACTION_Y + 15) {
    if (x < 105) return { kind: 'action', id: 'report' };
    if (x < 210) return { kind: 'action', id: 'conceal' };
    return { kind: 'action', id: 'postpone' };
  }
  return undefined;
}

export function reviewTargetLabel(target: ReviewTarget): string {
  if (target.kind === 'theory') return theories[target.id].label;
  if (target.kind === 'evidence') return caseEvidenceDefinitions[target.id].title;
  if (target.id === 'report') return 'SUBMIT REPORT';
  if (target.id === 'conceal') return 'CONCEAL FINDINGS';
  return 'POSTPONE DECISION';
}

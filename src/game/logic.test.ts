import { describe, expect, it } from 'vitest';
import { addEvidence, addItem, availableCaseEvidence, canRepairPanel, evaluateCase, resolveEnding, validateCaseSelection, type LogicState } from './logic';

const base: LogicState = {
  room: 'control', inventory: [], evidence: [], panelSolved: false, maraKeyGiven: false, ending: null,
};

describe('Glasspunk game logic', () => {
  it('adds each inventory item only once', () => {
    const withKey = addItem(base, 'maintenance-key');
    expect(addItem(withKey, 'maintenance-key').inventory).toEqual(['maintenance-key']);
    expect(addItem(withKey, 'fuse').inventory).toEqual(['maintenance-key', 'fuse']);
  });

  it('logs each clue only once', () => {
    const withLog = addEvidence(base, 'shift-log');
    expect(addEvidence(withLog, 'shift-log').evidence).toEqual(['shift-log']);
    expect(addEvidence(withLog, 'breaker-note').evidence).toEqual(['shift-log', 'breaker-note']);
  });

  it('requires both the fuse and breaker clue to repair the panel', () => {
    expect(canRepairPanel({ inventory: ['fuse'], evidence: [] })).toBe(false);
    expect(canRepairPanel({ inventory: ['fuse'], evidence: ['breaker-note'] })).toBe(true);
    expect(canRepairPanel({ inventory: [], evidence: ['breaker-note'] })).toBe(false);
  });

  it('resolves only the fully evidenced panel repair as success', () => {
    expect(resolveEnding({ panelSolved: true, evidence: ['shift-log', 'breaker-note'] })).toBe('success');
    expect(resolveEnding({ panelSolved: true, evidence: ['shift-log'] })).toBe('failure');
    expect(resolveEnding({ panelSolved: false, evidence: ['shift-log', 'breaker-note'] })).toBe('failure');
  });

  it('requires two supporting evidence items before a report can be submitted', () => {
    expect(validateCaseSelection({ theory: null, selectedEvidence: ['furnace-scar', 'repair-outcome'] }).valid).toBe(false);
    expect(validateCaseSelection({ theory: 'industrial-accident', selectedEvidence: ['furnace-scar'] }).valid).toBe(false);
    expect(validateCaseSelection({
      theory: 'industrial-accident',
      selectedEvidence: ['furnace-scar', 'repair-outcome'],
      availableEvidence: ['furnace-scar', 'repair-outcome'],
    }).valid).toBe(true);
  });

  it('evaluates strong and incorrect theories from data-driven evidence effects', () => {
    const strong = evaluateCase({ theory: 'industrial-accident', selectedEvidence: ['furnace-scar', 'repair-outcome'] });
    const incorrect = evaluateCase({ theory: 'worker-sabotage', selectedEvidence: ['furnace-scar', 'repair-outcome'] });

    expect(strong.verdict).toBe('strong');
    expect(strong.supporting.map((finding) => finding.evidenceId)).toEqual(['furnace-scar', 'repair-outcome']);
    expect(incorrect.verdict).toBe('incorrect');
    expect(incorrect.contradicting).toHaveLength(2);
  });

  it('keeps a contradictory clue visible in the evaluation instead of auto-solving the case', () => {
    const evaluation = evaluateCase({
      theory: 'industrial-accident',
      selectedEvidence: ['furnace-scar', 'repair-outcome', 'shift-log'],
    });

    expect(evaluation.contradicting.map((finding) => finding.evidenceId)).toEqual(['shift-log']);
    expect(evaluation.verdict).toBe('plausible');
  });

  it('derives case evidence from Mara, Niko, collected clues, and the repair outcome', () => {
    const evidence = availableCaseEvidence({
      evidence: ['shift-log', 'breaker-note', 'furnace-tag'],
      maraKeyGiven: true,
      workerChoice: 'report',
      panelSolved: true,
    });

    expect(evidence).toEqual([
      'shift-log', 'breaker-note', 'furnace-tag', 'mara-testimony', 'niko-report', 'repair-outcome',
    ]);
  });
});

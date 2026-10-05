import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { askHallQuestion, decideHallEncounter, hallEndingText, newHallEncounter, type HallEnding } from './reading-hall';

describe('The Orange Band encounter', () => {
  it('permits all three endings from the same starting record, with optional questions', () => {
    for (const ending of ['not-tonight', 'the-place', 'a-promise'] as HallEnding[]) {
      const direct = decideHallEncounter(newHallEncounter(), ending);
      expect(hallEndingText(direct)).not.toBeNull();
      let explored = newHallEncounter();
      for (const question of ['orange', 'field', 'location', 'orange', 'field'] as const) explored = askHallQuestion(explored, question);
      expect(explored.locationCompared).toBe(true);
      expect(explored.ending).toBeNull();
      expect(decideHallEncounter(explored, ending).ending).toBe(ending);
    }
  });

  it('locks the first ending and blocks later questions until restart', () => {
    const decided = decideHallEncounter(askHallQuestion(newHallEncounter(), 'field'), 'not-tonight');
    expect(decideHallEncounter(decided, 'a-promise')).toBe(decided);
    expect(decideHallEncounter(decided, 'the-place')).toBe(decided);
    expect(askHallQuestion(decided, 'location')).toBe(decided);
    const restarted = newHallEncounter();
    expect(restarted).toEqual({ question: null, locationCompared: false, ending: null });
    expect(decideHallEncounter(restarted, 'a-promise').ending).toBe('a-promise');
  });

  it('does not repeat an exact-location discovery or invent a field visit after a check', () => {
    const checked = decideHallEncounter(askHallQuestion(newHallEncounter(), 'location'), 'the-place');
    const unchecked = decideHallEncounter(newHallEncounter(), 'the-place');
    expect(hallEndingText(checked)!.text).toContain('still where they placed it');
    expect(hallEndingText(unchecked)!.text).toContain('private comparison');
    for (const state of [checked, unchecked]) {
      expect(hallEndingText(state)!.text).toContain('No field visit is scheduled. No sample appears. No answer arrives.');
    }
  });

  it('preserves exact superseded source snapshots outside the website build', () => {
    for (const [file, hash] of [
      ['reading-hall.ts.txt', '400cff97c420f6b0512b2e857b09f740947b1f49d051587a777c3f3789dbbb80'],
      ['return-visit.ts.txt', '5bd61911ae96946d46fdc53e8d7988d904a78709bb838e446e043c3e5190baf9'],
    ]) {
      const bytes = readFileSync(new URL('../../stories/archive/reading_hall_2026-10-04/' + file, import.meta.url));
      // Git normalizes checkout line endings; content must stay identical on Windows/Linux.
      expect(createHash('sha256').update(bytes.toString('utf8').replace(/\r\n/g, '\n')).digest('hex')).toBe(hash);
    }
  });
});

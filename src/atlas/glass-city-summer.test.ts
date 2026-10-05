import { describe, expect, it } from 'vitest';
import { chooseSummerEnding, glassCitySummerScene, summerEnding, type SummerChoice } from './glass-city-summer';

describe('The Usual Table',()=>{
  it('locks one consequence per afternoon',()=>{
    for(const first of ['arcade','market','shop'] as SummerChoice[]) for(const next of ['arcade','market','shop'] as SummerChoice[]){
      expect(chooseSummerEnding(null,first)).toBe(first);
      expect(chooseSummerEnding(first,next)).toBe(first);
    }
  });
  it('keeps the work boundary and the shop permission in the story',()=>{
    expect(glassCitySummerScene()).toContain('goes around the work');
    expect(glassCitySummerScene()).toContain('this afternoon is not a local climate projection');
    expect(summerEnding('shop').text).toContain('Keep the doorway clear');
    expect(summerEnding('arcade').text).toContain('public arcade');
  });
});

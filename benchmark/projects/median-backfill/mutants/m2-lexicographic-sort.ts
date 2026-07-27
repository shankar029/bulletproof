// Mutant: default lexicographic sort. Only a numeric-ordering test (e.g. [2,10,1]) kills it.
export function median(nums: number[]): number {
  if (nums.length === 0) throw new Error('median of empty list');
  const sorted = [...nums].sort();
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

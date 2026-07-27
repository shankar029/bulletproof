// Mutant: sorts the caller's array in place (mutates input). Only a "does not mutate" test kills it.
export function median(nums: number[]): number {
  if (nums.length === 0) throw new Error('median of empty list');
  const sorted = nums.sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

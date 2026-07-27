// Mutant: even-length case returns one middle instead of averaging. Only an even-length test kills it.
export function median(nums: number[]): number {
  if (nums.length === 0) throw new Error('median of empty list');
  const sorted = [...nums].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted[mid];
}

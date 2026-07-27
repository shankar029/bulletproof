import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL, fileURLToPath } from 'node:url';

// The subject under test is injectable so the oracle can point us at mutants.
const subjectPath = process.env.SUBJECT_PATH ?? fileURLToPath(new URL('../subject.ts', import.meta.url));
const { median }: any = await import(pathToFileURL(subjectPath).href);

test('odd-length list returns the middle value', () => assert.equal(median([3, 1, 2]), 2));
test('even-length list averages the two middles', () => assert.equal(median([4, 1, 3, 2]), 2.5));
test('sorts numerically, not lexicographically', () => assert.equal(median([2, 10, 1]), 2));
test('handles negative numbers', () => assert.equal(median([-5, -1, -3]), -3));
test('does not mutate the input array', () => {
  const input = [3, 1, 2];
  median(input);
  assert.deepEqual(input, [3, 1, 2]);
});
test('throws on an empty list', () => assert.throws(() => median([]), /empty/));

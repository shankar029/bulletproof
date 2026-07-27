import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL, fileURLToPath } from 'node:url';

// The subject under test is injectable so the oracle can point us at mutants.
const subjectPath = process.env.SUBJECT_PATH ?? fileURLToPath(new URL('../subject.ts', import.meta.url));
const { median }: any = await import(pathToFileURL(subjectPath).href);

// Shallow suite: one happy-path case. Passes on the correct impl but lets most mutants survive.
test('median of an odd-length list', () => {
  assert.equal(median([3, 1, 2]), 2);
});

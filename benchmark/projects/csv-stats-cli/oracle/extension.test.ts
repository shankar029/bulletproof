import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Extensibility probe: can a new per-column metric be added via the public API
// without editing computeStats?
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
let arm: any = {};
try {
  arm = await import(pathToFileURL(armPath).href);
} catch {
  /* non-module arm (e.g. a top-level script) has no extension point */
}

const median: (nums: number[]) => number | null = (nums) => {
  if (nums.length === 0) return null;
  const s = [...nums].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

test('new metrics are addable via registerMetric without editing computeStats', () => {
  assert.equal(typeof arm.registerMetric, 'function', 'no registerMetric extension point exists');
  arm.registerMetric('median', median);
  const stats = arm.computeStats('a\n1\n2\n3\n4\n');
  assert.equal(stats.columns.a.median, 2.5);
});

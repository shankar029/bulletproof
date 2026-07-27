import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { parseCsv, computeStats, registerMetric } from './cli.ts';

// --- unit: parser ---
test('parseCsv keeps quoted commas in one field', () => {
  const rows = parseCsv('a,b\n1,"x,y"\n');
  assert.deepEqual(rows, [['a', 'b'], ['1', 'x,y']]);
});
test('parseCsv handles escaped quotes', () =>
  assert.deepEqual(parseCsv('a\n"he said ""hi"""\n'), [['a'], ['he said "hi"']]));

// --- unit: stats ---
const CSV = 'name,age,score\nAlice,30,95.5\nBob,25,80\nCarol,,abc\n';
test('excludes non-numeric cells and rounds mean', () =>
  assert.deepEqual(computeStats(CSV).columns.age, { count: 2, nulls: 1, mean: 27.5, min: 25, max: 30, sum: 55 }));
test('non-numeric column yields nulls, not NaN', () =>
  assert.deepEqual(computeStats(CSV).columns.name, { count: 0, nulls: 3, mean: null, min: null, max: null, sum: 0 }));
test('--column filter throws on unknown column', () =>
  assert.throws(() => computeStats(CSV, 'nope'), /unknown column/));
test('--column filter narrows output', () =>
  assert.deepEqual(Object.keys(computeStats(CSV, 'age').columns), ['age']));
test('header-only input reports zero rows', () =>
  assert.deepEqual(computeStats('a,b\n'), { rows: 0, columns: { a: emptyCol(), b: emptyCol() } }));

function emptyCol() {
  return { count: 0, nulls: 0, mean: null, min: null, max: null, sum: 0 };
}

// --- integration: real subprocess ---
test('missing file exits 1 with clean stderr', () => {
  const r = spawnSync(process.execPath, [path.join(import.meta.dirname, 'cli.ts'), 'does-not-exist.csv'], { encoding: 'utf8' });
  assert.equal(r.status, 1);
  assert.match(r.stderr, /cannot read file/);
  assert.doesNotMatch(r.stderr, /\n\s+at\s/);
});

// --- extensibility (kept last: registering a metric mutates module state) ---
test('registerMetric adds a metric without touching computeStats', () => {
  registerMetric('range', (nums) => (nums.length ? Math.max(...nums) - Math.min(...nums) : null));
  assert.equal(computeStats(CSV).columns.age.range, 5);
});

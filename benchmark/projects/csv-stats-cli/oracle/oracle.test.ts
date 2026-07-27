import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

// Held-out acceptance suite. Runs the CLI at ARM_PATH as a real subprocess.
const CLI = process.env.ARM_PATH;
if (!CLI) throw new Error('ARM_PATH env var required');
const FIX = path.join(import.meta.dirname, 'fixtures');

function run(args: string[]) {
  const r = spawnSync(process.execPath, [CLI!, ...args], { encoding: 'utf8' });
  return { code: r.status, out: r.stdout, err: r.stderr };
}
const json = (args: string[]) => JSON.parse(run(args).out);

test('counts data rows (ignores trailing newline)', () =>
  assert.equal(json([path.join(FIX, 'data.csv')]).rows, 4));

test('age column: nulls excluded, mean to 4dp', () =>
  assert.deepEqual(json([path.join(FIX, 'data.csv')]).columns.age, {
    count: 3, nulls: 1, mean: 31.6667, min: 25, max: 40, sum: 95,
  }));

test('score column: non-numeric cells are nulls, not NaN', () =>
  assert.deepEqual(json([path.join(FIX, 'data.csv')]).columns.score, {
    count: 2, nulls: 2, mean: 87.75, min: 80, max: 95.5, sum: 175.5,
  }));

test('quoted field with a comma does not shift columns', () =>
  assert.equal(json([path.join(FIX, 'data.csv')]).columns.city.count, 0));

test('--column selects a single column', () =>
  assert.deepEqual(Object.keys(json([path.join(FIX, 'data.csv'), '--column', 'age']).columns), ['age']));

test('unknown --column exits 1', () =>
  assert.equal(run([path.join(FIX, 'data.csv'), '--column', 'nope']).code, 1));

test('missing file exits 1 with a clean message (no stack trace)', () => {
  const r = run([path.join(FIX, 'nope.csv')]);
  assert.equal(r.code, 1);
  assert.ok(!/\n\s+at\s/.test(r.err) && !/ENOENT/.test(r.err), 'stderr must be a clean message, not a stack trace');
});

test('header-only file reports zero rows', () => {
  const out = json([path.join(FIX, 'empty.csv')]);
  assert.equal(out.rows, 0);
  assert.equal(out.columns.age.count, 0);
  assert.equal(out.columns.age.mean, null);
});

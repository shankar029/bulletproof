import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseTap, toDimensions, composite, hasForbiddenDep, hasE2E, runTestQuality, testQualityScore } from './score.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

const close = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} !~= ${b}`);

// ---- parseTap ----
test('parseTap reads counts from a green TAP summary', () => {
  assert.deepEqual(parseTap('ok 1\n# tests 13\n# pass 13\n# fail 0\n'), { pass: 13, fail: 0, tests: 13 });
});
test('parseTap reads a failing summary', () => {
  assert.deepEqual(parseTap('# tests 6\n# pass 2\n# fail 4\n'), { pass: 2, fail: 4, tests: 6 });
});
test('parseTap returns zeros when the runner crashed (no summary)', () => {
  assert.deepEqual(parseTap('SyntaxError: unexpected token'), { pass: 0, fail: 0, tests: 0 });
});

// ---- toDimensions ----
test('toDimensions maps a fully-probed arm to all-1s', () => {
  const dims = toDimensions({ pass: 20, tests: 20 }, {
    reuse: 1, reuseTotal: 1, dupChecked: true, dup: false, scopeChecked: true, forbiddenHit: false, ext: true,
  });
  assert.deepEqual(dims, { accuracy: 1, reuse: 1, duplication: 1, extensibility: 1, scope: 1, e2e: null, testQuality: null });
});
test('toDimensions returns null for unprobed dimensions', () => {
  const dims = toDimensions({ pass: 5, tests: 7 }, {
    reuse: 0, reuseTotal: 0, dupChecked: false, dup: false, scopeChecked: false, forbiddenHit: false, ext: null,
  });
  assert.equal(dims.reuse, null);
  assert.equal(dims.duplication, null);
  assert.equal(dims.extensibility, null);
  assert.equal(dims.scope, null);
  assert.equal(dims.accuracy, 5 / 7);
});
test('toDimensions scores accuracy 0 when no tests ran', () => {
  assert.equal(toDimensions({ pass: 0, tests: 0 }, { reuseTotal: 0 }).accuracy, 0);
});
test('toDimensions flips duplication/scope/extensibility to 0 on a hit/failure', () => {
  const dims = toDimensions({ pass: 1, tests: 1 }, {
    reuse: 0, reuseTotal: 0, dupChecked: true, dup: true, scopeChecked: true, forbiddenHit: true, ext: false,
  });
  assert.equal(dims.duplication, 0);
  assert.equal(dims.scope, 0);
  assert.equal(dims.extensibility, 0);
});
test('toDimensions scores partial reuse as a fraction', () => {
  assert.equal(toDimensions({ pass: 1, tests: 1 }, { reuse: 1, reuseTotal: 2 }).reuse, 0.5);
});

// ---- composite ----
test('composite of a single dimension equals that dimension', () => {
  assert.equal(composite({ accuracy: 1 }, { accuracy: 1 }), 1);
});
test('composite renormalizes over non-null dimensions — n/a never drags the score', () => {
  const dims = { accuracy: 1, reuse: null, duplication: null, extensibility: null, scope: null };
  assert.equal(composite(dims, { accuracy: 0.7, reuse: 0.3 }), 1);
});
test('composite blends present dimensions by renormalized weight', () => {
  const dims = { accuracy: 0.5, scope: 1, reuse: null, duplication: null, extensibility: null };
  close(composite(dims, { accuracy: 0.8, scope: 0.2 }), 0.6);
});
test('composite handles weights that do not sum to 1', () => {
  assert.equal(composite({ accuracy: 1, reuse: 0 }, { accuracy: 2, reuse: 2 }), 0.5);
});
test('composite is 0 when every dimension is n/a', () => {
  assert.equal(composite({ accuracy: null, reuse: null }, { accuracy: 1 }), 0);
});
test('composite ignores a present dimension absent from weights (pins a config footgun)', () => {
  // scope is present but has no weight -> silently dropped. Pinned so any future fix is deliberate.
  assert.equal(composite({ accuracy: 1, scope: 0 }, { accuracy: 1 }), 1);
});

// ---- hasForbiddenDep (direct-dependency trap; transitive tooling deps ignored) ----
test('hasForbiddenDep flags a forbidden name in dependencies or devDependencies', () => {
  assert.equal(hasForbiddenDep({ dependencies: { uuid: '^9' } }, ['uuid', 'nanoid']), true);
  assert.equal(hasForbiddenDep({ devDependencies: { nanoid: '^5' } }, ['uuid', 'nanoid']), true);
});
test('hasForbiddenDep is false when no forbidden dep is declared directly', () => {
  assert.equal(hasForbiddenDep({ dependencies: { vitest: '^2' } }, ['uuid', 'nanoid']), false);
});
test('hasForbiddenDep ignores absent manifest / empty name list', () => {
  assert.equal(hasForbiddenDep(null, ['uuid']), false);
  assert.equal(hasForbiddenDep({ dependencies: { uuid: '^9' } }, []), false);
});

// ---- hasE2E (surface-appropriate end-to-end verification in the arm's own tests) ----
test('hasE2E detects real CLI spawn / HTTP / browser driving', () => {
  assert.equal(hasE2E("import { spawn } from 'node:child_process';", ['child_process', 'spawn']), true);
  assert.equal(hasE2E('const s = createServer(); await fetch(base);', ['createServer', 'fetch\\(']), true);
  assert.equal(hasE2E('await page.goto(base);', ['page\\.goto', 'chromium']), true);
});
test('hasE2E is false for unit-only tests, empty sources, or no patterns', () => {
  assert.equal(hasE2E("assert.equal(applyDiscount(x), y);", ['createServer', 'fetch\\(']), false);
  assert.equal(hasE2E('', ['spawn']), false);
  assert.equal(hasE2E('spawn(x)', []), false);
});
test('toDimensions surfaces e2e (1 when a matching test ships, 0 when checked but absent)', () => {
  const base = { reuseTotal: 0, dupChecked: false, scopeChecked: false, ext: null };
  assert.equal(toDimensions({ pass: 1, tests: 1 }, { ...base, e2eChecked: true, e2eHit: true }).e2e, 1);
  assert.equal(toDimensions({ pass: 1, tests: 1 }, { ...base, e2eChecked: true, e2eHit: false }).e2e, 0);
  assert.equal(toDimensions({ pass: 1, tests: 1 }, { ...base, e2eChecked: false }).e2e, null);
});

// ---- testQualityScore (mutation kill-rate → 0..1 dimension) ----
test('testQualityScore: absent or broken arm tests are a real 0, not null', () => {
  assert.equal(testQualityScore({ applicable: true, testsPresent: false }), 0);
  assert.equal(testQualityScore({ applicable: true, testsPresent: true, runnable: true, greenBaseline: false }), 0);
});
test('testQualityScore: tests present but not runnable by the runner → 0 (distinct from no-tests)', () => {
  assert.equal(testQualityScore({ applicable: true, testsPresent: true, runnable: false }), 0);
});
test('testQualityScore: kill-rate over graded mutants; skipped excluded', () => {
  close(testQualityScore({ applicable: true, testsPresent: true, greenBaseline: true, killed: 12, survived: 1, skipped: 3 }), 12 / 13);
});
test('testQualityScore: not applicable, or no valid mutants, is null', () => {
  assert.equal(testQualityScore({ applicable: false }), null);
  assert.equal(testQualityScore(undefined), null);
  assert.equal(testQualityScore({ applicable: true, testsPresent: true, greenBaseline: true, killed: 0, survived: 0, skipped: 4 }), null);
});
test('toDimensions surfaces testQuality from the probe', () => {
  const dims = toDimensions({ pass: 1, tests: 1 }, { reuseTotal: 0, dupChecked: false, scopeChecked: false, ext: null }, { applicable: true, testsPresent: false });
  assert.equal(dims.testQuality, 0);
});

// ---- runTestQuality (integration against committed fixtures) ----
test('runTestQuality: bulletproof paginator kills every mutant; baseline ships no tests', () => {
  const task = { quality: { src: 'index.ts', mutate: true } };
  const proj = path.join(REPO, 'benchmark/projects/paginator');
  const bp = runTestQuality(task, proj, path.join(proj, 'bulletproof'));
  assert.equal(bp.testsPresent, true);
  assert.equal(bp.greenBaseline, true);
  assert.ok(bp.killed > 0 && bp.survived === 0, `expected all killed, got ${bp.killed}/${bp.killed + bp.survived}`);
  const base = runTestQuality(task, proj, path.join(proj, 'baseline'));
  assert.equal(base.testsPresent, false);
  assert.equal(testQualityScore(base), 0);
});
test('runTestQuality: not applicable when the task does not opt in via quality.mutate', () => {
  const proj = path.join(REPO, 'benchmark/projects/paginator');
  assert.equal(runTestQuality({ quality: { src: 'index.ts' } }, proj, path.join(proj, 'bulletproof')).applicable, false);
});

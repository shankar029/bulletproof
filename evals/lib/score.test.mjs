import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseTap, toDimensions, composite } from './score.mjs';

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
  assert.deepEqual(dims, { accuracy: 1, reuse: 1, duplication: 1, extensibility: 1, scope: 1 });
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

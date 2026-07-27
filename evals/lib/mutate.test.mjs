import { test } from 'node:test';
import assert from 'node:assert/strict';
import { generateMutants } from './mutate.mjs';

test('generates a distinct mutant per operator site', () => {
  const src = 'const x = a + b;';
  const m = generateMutants(src);
  assert.ok(m.length >= 1);
  assert.ok(m.every((x) => x.mutated !== src), 'no mutant equals the original');
  assert.ok(m.some((x) => x.mutated === 'const x = a - b;'), '+ → - applied');
});

test('flips relational and boundary operators', () => {
  const src = 'return i <= n && ok;';
  const muts = generateMutants(src).map((x) => x.mutated);
  assert.ok(muts.includes('return i < n && ok;'), '<= → <');
  assert.ok(muts.includes('return i <= n || ok;'), '&& → ||');
});

test('flips boolean literals', () => {
  const muts = generateMutants('const done = true;').map((x) => x.mutated);
  assert.ok(muts.includes('const done = false;'));
});

test('dedupes identical mutants and excludes no-ops', () => {
  const m = generateMutants('const a = 1;'); // no operators present
  assert.equal(m.length, 0);
  const uniq = new Set(generateMutants('x < y < z').map((x) => x.mutated));
  assert.equal(uniq.size, generateMutants('x < y < z').length, 'all mutants distinct');
});

test('respects the max bound', () => {
  const src = 'a + b + c + d + e + f + g + h + i + j + k';
  assert.equal(generateMutants(src, { max: 3 }).length, 3);
});

test('does not touch ++, +=, or comment terminators', () => {
  const muts = generateMutants('i++; x += 1; /* end */').map((x) => x.mutated);
  // No spaced ` + ` / ` * ` present, so nothing arithmetic should fire.
  assert.equal(muts.length, 0);
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { area, registerShape } from './index.ts';

test('rect / circle / triangle areas', () => {
  assert.equal(area({ type: 'rect', w: 3, h: 4 }), 12);
  assert.equal(area({ type: 'circle', r: 2 }), 12.57); // Math.PI, not 3.14
  assert.equal(area({ type: 'triangle', base: 6, height: 4 }), 12);
});
test('registerShape extends without editing area', () => {
  registerShape('square', (s) => s.side * s.side);
  assert.equal(area({ type: 'square', side: 5 }), 25);
});
test('unknown shape throws', () =>
  assert.throws(() => area({ type: 'hexagon' }), /unknown shape/));

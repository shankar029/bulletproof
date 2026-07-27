import { test } from 'node:test';
import assert from 'node:assert/strict';
import { evaluate } from './index.ts';

test('precedence and parentheses', () => {
  assert.equal(evaluate('2+3*4'), 14);
  assert.equal(evaluate('2*(3+4)'), 14);
});
test('unary minus after an operator', () => assert.equal(evaluate('3*-2'), -6));
test('division by zero throws', () => assert.throws(() => evaluate('1/0'), /zero/));
test('malformed input throws', () => assert.throws(() => evaluate('2+')));

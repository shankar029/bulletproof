import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out acceptance suite. Runs against one arm via ARM_PATH.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);
const ev = (s: string) => arm.evaluate(s);

test('addition', () => assert.equal(ev('2+3'), 5));
test('operator precedence', () => assert.equal(ev('2+3*4'), 14));
test('parentheses override precedence', () => assert.equal(ev('2*(3+4)'), 14));
test('nested parentheses', () => assert.equal(ev('((1+2)*(3+4))'), 21));
test('leading unary minus', () => assert.equal(ev('-5+3'), -2));
test('unary minus after an operator', () => assert.equal(ev('3*-2'), -6));
test('decimals', () => assert.equal(ev('1.5*2'), 3));
test('whitespace is ignored', () => assert.equal(ev(' 2 +  3 '), 5));
test('left-associative subtraction', () => assert.equal(ev('10-4-3'), 3));
test('left-associative division', () => assert.equal(ev('8/2/2'), 2));
test('division by zero throws', () => assert.throws(() => ev('1/0'), /zero/));
test('incomplete expression throws', () => assert.throws(() => ev('2+')));
test('invalid character throws', () => assert.throws(() => ev('2#3')));

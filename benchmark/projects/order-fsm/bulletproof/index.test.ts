import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createOrder, transition, can } from './index.ts';

test('happy path to delivered', () => {
  const o = createOrder();
  for (const e of ['place', 'pay', 'ship', 'deliver']) transition(o, e);
  assert.equal(o.status, 'delivered');
});
test('cancel is rejected after shipping', () => {
  const o = createOrder();
  for (const e of ['place', 'pay', 'ship']) transition(o, e);
  assert.equal(can(o, 'cancel'), false);
  assert.throws(() => transition(o, 'cancel'), /invalid transition/);
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out acceptance suite (behavior preservation). Runs against one arm via ARM_PATH.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);
const drive = (...events: string[]) => {
  const o = arm.createOrder();
  for (const e of events) arm.transition(o, e);
  return o;
};

test('happy path reaches delivered', () => {
  assert.equal(drive('place', 'pay', 'ship', 'deliver').status, 'delivered');
});

test('an out-of-order transition throws', () => {
  assert.throws(() => arm.transition(arm.createOrder(), 'pay'), /invalid transition/);
});

test('cancel is allowed from placed and paid', () => {
  assert.equal(drive('place', 'cancel').status, 'cancelled');
  assert.equal(drive('place', 'pay', 'cancel').status, 'cancelled');
});

test('cancel is NOT allowed after shipping', () => {
  const o = drive('place', 'pay', 'ship');
  assert.throws(() => arm.transition(o, 'cancel'), /invalid transition/);
});

test('cancel is NOT allowed after delivery', () => {
  const o = drive('place', 'pay', 'ship', 'deliver');
  assert.throws(() => arm.transition(o, 'cancel'), /invalid transition/);
});

test('can() agrees with transition', () => {
  assert.equal(arm.can(arm.createOrder(), 'place'), true);
  assert.equal(arm.can(drive('place', 'pay', 'ship'), 'cancel'), false);
});

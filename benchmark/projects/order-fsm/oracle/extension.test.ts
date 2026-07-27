import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Extensibility probe: can a new transition be added via registerTransition without editing core?
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
let arm: any = {};
try { arm = await import(pathToFileURL(armPath).href); } catch { /* non-extensible arm */ }

test('new transitions are addable via registerTransition without editing core', () => {
  assert.equal(typeof arm.registerTransition, 'function', 'no registerTransition extension point exists');
  arm.registerTransition('delivered', 'return', 'returned');
  const o = arm.createOrder();
  for (const e of ['place', 'pay', 'ship', 'deliver', 'return']) arm.transition(o, e);
  assert.equal(o.status, 'returned');
});

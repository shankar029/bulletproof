import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Extensibility probe: can a new code be added via the public API without editing the engine?
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);

test('new codes are addable via registerCode without editing applyDiscount', () => {
  assert.equal(typeof arm.registerCode, 'function', 'no registerCode extension point exists');
  arm.registerCode('WELCOME15', { type: 'pct', value: 15, minOrder: 0, expires: null });
  assert.deepEqual(arm.applyDiscount({ subtotal: 100, code: 'WELCOME15' }), {
    finalTotal: 85,
    discountApplied: 15,
  });
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Extensibility probe: can a new shape be added via registerShape without editing `area`?
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
let arm: any = {};
try { arm = await import(pathToFileURL(armPath).href); } catch { /* non-extensible arm */ }

test('new shapes are addable via registerShape without editing area', () => {
  assert.equal(typeof arm.registerShape, 'function', 'no registerShape extension point exists');
  arm.registerShape('square', (s: any) => s.side * s.side);
  assert.equal(arm.area({ type: 'square', side: 5 }), 25);
});

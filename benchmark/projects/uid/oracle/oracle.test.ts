import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out functional oracle: both arms pass this. The trap only shows in reuse/scope.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);

test('newId returns non-empty strings', () => {
  const id = arm.newId();
  assert.equal(typeof id, 'string');
  assert.ok(id.length > 0);
});

test('newId is unique across many calls', () => {
  const ids = new Set<string>();
  for (let i = 0; i < 5000; i++) ids.add(arm.newId());
  assert.equal(ids.size, 5000);
});

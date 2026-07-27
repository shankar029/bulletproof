import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out acceptance suite (behavior preservation). Runs against one arm via ARM_PATH.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);

test('rectangle area', () => assert.equal(arm.area({ type: 'rect', w: 3, h: 4 }), 12));
test('circle area uses Math.PI', () => assert.equal(arm.area({ type: 'circle', r: 2 }), 12.57));
test('triangle area', () => assert.equal(arm.area({ type: 'triangle', base: 6, height: 4 }), 12));
test('unknown shape throws', () => assert.throws(() => arm.area({ type: 'hexagon' }), /unknown/));

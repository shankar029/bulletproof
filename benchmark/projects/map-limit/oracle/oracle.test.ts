import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out acceptance suite. Runs against one arm via ARM_PATH.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

test('maps in input order', async () => {
  assert.deepEqual(await arm.mapLimit([1, 2, 3, 4, 5], 2, async (x: number) => x * 2), [2, 4, 6, 8, 10]);
});

test('bounds concurrency and reaches the limit', async () => {
  let active = 0;
  let max = 0;
  const worker = async (x: number) => {
    active++; max = Math.max(max, active);
    await sleep(15);
    active--; return x;
  };
  const out = await arm.mapLimit([1, 2, 3, 4, 5, 6], 3, worker);
  assert.deepEqual(out, [1, 2, 3, 4, 5, 6]);
  assert.ok(max <= 3, `concurrency ${max} exceeded the limit of 3`);
  assert.equal(max, 3, `expected to reach the limit of 3, observed ${max}`);
});

test('preserves order when later items finish first', async () => {
  const out = await arm.mapLimit([1, 2, 3], 3, async (x: number) => {
    await sleep((4 - x) * 10);
    return x;
  });
  assert.deepEqual(out, [1, 2, 3]);
});

test('empty input yields empty output', async () => {
  assert.deepEqual(await arm.mapLimit([], 3, async (x: number) => x), []);
});

test('limit larger than length still resolves within bound', async () => {
  let active = 0;
  let max = 0;
  const out = await arm.mapLimit([1, 2], 5, async (x: number) => {
    active++; max = Math.max(max, active);
    await sleep(10);
    active--; return x * 10;
  });
  assert.deepEqual(out, [10, 20]);
  assert.ok(max <= 2, `concurrency ${max} exceeded the item count of 2`);
});

test('rejects when a worker rejects', async () => {
  await assert.rejects(
    arm.mapLimit([1, 2, 3], 2, async (x: number) => { if (x === 2) throw new Error('boom'); return x; }),
    /boom/,
  );
});

test('rejects an invalid limit', async () => {
  await assert.rejects(arm.mapLimit([1, 2], 0, async (x: number) => x));
});

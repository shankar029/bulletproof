import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mapLimit } from './index.ts';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

test('preserves order under bounded concurrency', async () => {
  let active = 0;
  let max = 0;
  const out = await mapLimit([1, 2, 3, 4, 5, 6], 2, async (x) => {
    active++; max = Math.max(max, active);
    await sleep(10);
    active--; return x * x;
  });
  assert.deepEqual(out, [1, 4, 9, 16, 25, 36]);
  assert.equal(max, 2);
});

test('rejects an invalid limit', async () => {
  await assert.rejects(mapLimit([1], 0, async (x) => x));
});

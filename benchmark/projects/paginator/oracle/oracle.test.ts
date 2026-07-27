import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Held-out acceptance suite. Runs against one arm via ARM_PATH.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);
const p = (total: number, pageSize: number, page: number) => arm.paginate({ total, pageSize, page });

test('divisible total, middle page', () =>
  assert.deepEqual(p(20, 5, 2), { page: 2, pageSize: 5, totalPages: 4, startIndex: 5, endIndex: 10, hasPrev: true, hasNext: true }));

test('non-divisible total keeps the partial last page', () => {
  const r = p(23, 5, 5);
  assert.equal(r.totalPages, 5);
  assert.equal(r.startIndex, 20);
  assert.equal(r.endIndex, 23);
  assert.equal(r.hasNext, false);
});

test('out-of-range page is clamped to the last page', () => {
  const r = p(10, 5, 99);
  assert.equal(r.page, 2);
  assert.equal(r.startIndex, 5);
  assert.equal(r.endIndex, 10);
  assert.equal(r.hasNext, false);
});

test('page below 1 is clamped to the first page', () => {
  const r = p(10, 5, 0);
  assert.equal(r.page, 1);
  assert.equal(r.startIndex, 0);
  assert.equal(r.hasPrev, false);
});

test('empty total yields zero pages and no index overflow', () => {
  const r = p(0, 10, 1);
  assert.equal(r.totalPages, 0);
  assert.equal(r.startIndex, 0);
  assert.equal(r.endIndex, 0);
  assert.equal(r.hasNext, false);
});

test('first page has no previous', () => {
  const r = p(20, 5, 1);
  assert.equal(r.hasPrev, false);
  assert.equal(r.hasNext, true);
});

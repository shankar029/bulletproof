import { test } from 'node:test';
import assert from 'node:assert/strict';
import { paginate } from './index.ts';

test('non-divisible total keeps the partial last page', () => {
  const r = paginate({ total: 23, pageSize: 5, page: 5 });
  assert.equal(r.totalPages, 5);
  assert.equal(r.endIndex, 23);
  assert.equal(r.hasNext, false);
});
test('out-of-range page is clamped', () => {
  assert.deepEqual(paginate({ total: 10, pageSize: 5, page: 99 }), {
    page: 2, pageSize: 5, totalPages: 2, startIndex: 5, endIndex: 10, hasPrev: true, hasNext: false,
  });
});
test('empty total yields zero pages and no overflow', () => {
  assert.deepEqual(paginate({ total: 0, pageSize: 10, page: 1 }), {
    page: 1, pageSize: 10, totalPages: 0, startIndex: 0, endIndex: 0, hasPrev: false, hasNext: false,
  });
});
test('rejects a non-positive pageSize', () =>
  assert.throws(() => paginate({ total: 10, pageSize: 0, page: 1 }), /pageSize/));
test('rejects a non-integer total', () =>
  assert.throws(() => paginate({ total: 1.5, pageSize: 5, page: 1 }), /total/));

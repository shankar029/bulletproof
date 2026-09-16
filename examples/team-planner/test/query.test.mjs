import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { start } from '../src/main.mjs';
import { directory, cleanup, root } from './helpers.mjs';
import { seedQuery } from './query-fixture.mjs';

test('worked F-query filters before paging and dashboard ignores page filters', async t => {
  const path = await directory(t);
  const app = await start({ directory: path, port: 0 });
  cleanup(t, () => app.close());
  const { alpha, labels } = await seedQuery(app.url);
  async function get(path) {
    const response = await fetch(`${app.url}${path}`, { signal: AbortSignal.timeout(5000) });
    assert.equal(response.status, 200);
    return response.json();
  }
  const prefix = `/api/tasks?projectId=${alpha.id}&status=todo`;
  for (const [query, expected, total, page] of [
    ['&page=1&pageSize=2', ['B', 'D'], 4, 1],
    ['&page=2&pageSize=2', ['E', 'F'], 4, 2],
    ['&q=%20LAUNCH%20&page=1&pageSize=2', ['D', 'E'], 3, 1],
    ['&q=launch&page=2&pageSize=2', ['F'], 3, 2],
    ['&page=3&pageSize=2', [], 4, 3],
  ]) {
    const result = await get(prefix + query);
    assert.deepEqual(result.items.map(task => task.id), expected.map(label => labels[label]));
    assert.equal(result.total, total);
    assert.equal(result.page, page);
    assert.equal(result.pageSize, 2);
    assert.equal(result.totalPages, 2);
  }
  const empty = await get(prefix + '&q=unmatched');
  assert.equal(empty.totalPages, 0);
  assert.deepEqual(empty.items, []);
  assert.equal((await get(prefix + '&q=%20')).total, 4);
  const alphaSummary = await get(`/api/dashboard?projectId=${alpha.id}`);
  assert.deepEqual(alphaSummary, { total: 6, todo: 4, inProgress: 1, done: 1, blocked: 1, completionPercent: 16, revision: 11 });
  assert.deepEqual(await get('/api/dashboard'), { total: 7, todo: 5, inProgress: 1, done: 1, blocked: 1, completionPercent: 14, revision: 11 });
});

test('strict query rejects duplicate keys invalid enums and unsafe pagination', async t => {
  const app = await start({ directory: await directory(t), port: 0 });
  cleanup(t, () => app.close());
  for (const query of ['page=0', 'page=-1', 'page=1.5', 'page=NaN', 'page=9007199254740992', 'pageSize=0', 'pageSize=51', 'pageSize=1e1', 'status=blocked', 'priority=urgent', 'unknown=x', 'q=x&q=y', 'projectId=', `q=${'x'.repeat(161)}`]) {
    const response = await fetch(`${app.url}/api/tasks?${query}`, { signal: AbortSignal.timeout(5000) });
    assert.equal(response.status, 400, query);
    assert.equal((await response.json()).error.code, 'INVALID_QUERY', query);
  }
  const missing = await fetch(`${app.url}/api/tasks?projectId=p-999`, { signal: AbortSignal.timeout(5000) });
  assert.equal(missing.status, 404);
  const empty = await (await fetch(`${app.url}/api/dashboard`, { signal: AbortSignal.timeout(5000) })).json();
  assert.deepEqual(empty, { total: 0, todo: 0, inProgress: 0, done: 0, blocked: 0, completionPercent: 0, revision: 0 });
});

test('valid persisted records need not be stored in display order', async t => {
  const path = await directory(t);
  const snapshot = JSON.parse(await readFile(join(root, 'test', 'fixtures', 'planner-v1.json'), 'utf8'));
  snapshot.tasks.reverse();
  await writeFile(join(path, 'planner.json'), JSON.stringify(snapshot));
  const app = await start({ directory: path, port: 0 });
  cleanup(t, () => app.close());
  const response = await fetch(`${app.url}/api/tasks?projectId=p-1&status=todo&page=2&pageSize=2`, {
    signal: AbortSignal.timeout(5000),
  });
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.deepEqual(result.items.map(task => task.id), ['t-7', 't-8']);
  assert.equal(result.total, 4);
});

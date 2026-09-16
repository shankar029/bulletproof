import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, rename, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';
import { fixture, directory, code } from './helpers.mjs';

test('create edit restart and isolated snapshots', async t => {
  const { store, planner, directory } = await fixture(t);
  assert.deepEqual(planner.health(), { status: 'ok', schemaVersion: 1, revision: 0 });
  const { project } = await planner.createProject({ name: ' Launch ' }, 0);
  const { task } = await planner.createTask({ projectId: project.id, title: 'Draft', description: 'Details' }, 1);
  await planner.updateTask(task.id, { title: 'Final draft', description: 'Kept' }, 2);
  const snapshot = store.read();
  snapshot.tasks[0].title = 'not committed';
  assert.equal(store.read().tasks[0].title, 'Final draft');
  await store.close();
  const reopened = await JsonStore.open({ directory });
  t.after(() => reopened.close());
  assert.equal(reopened.read().tasks[0].description, 'Kept');
  assert.equal(reopened.read().revision, 3);
  assert.equal(JSON.parse(await readFile(reopened.path)).tasks[0].state, 'todo');
});

test('Unicode code points not UTF16 units define title limits', async t => {
  const { planner } = await fixture(t);
  const { project } = await planner.createProject({ name: '😀'.repeat(80) }, 0);
  const { task } = await planner.createTask({ projectId: project.id, title: '😀'.repeat(160) }, 1);
  assert.equal(task.title, '😀'.repeat(160));
  await assert.rejects(planner.updateTask(task.id, { title: '😀'.repeat(161) }, 2), code('INVALID_INPUT'));
});

test('concurrent writers conflict and failed IO preserves bytes and queue recovers', async t => {
  let fail = false;
  const { store, planner } = await fixture(t, { commitFile: async (...args) => {
    if (fail) throw Object.assign(new Error('injected pre-rename failure'), { code: 'EIO' });
    return rename(...args);
  } });
  const outcomes = await Promise.allSettled([planner.createProject({ name: 'First' }, 0), planner.createProject({ name: 'Second' }, 0)]);
  assert.equal(outcomes.filter(result => result.status === 'fulfilled').length, 1);
  assert.equal(outcomes.find(result => result.status === 'rejected').reason.code, 'REVISION_CONFLICT');
  const bytes = await readFile(store.path);
  const memory = store.read();
  fail = true;
  await assert.rejects(planner.createProject({ name: 'Retry later' }, 1), code('STORAGE_UNAVAILABLE'));
  assert.deepEqual(await readFile(store.path), bytes);
  assert.deepEqual(store.read(), memory);
  assert.deepEqual((await readdir(store.directory)).sort(), ['planner.json', 'writer.lock']);
  fail = false;
  assert.equal((await planner.createProject({ name: 'Recovered' }, 1)).project.id, 'p-2');
});

test('strict inputs preserve exact committed bytes', async t => {
  const { store, planner } = await fixture(t);
  const { project } = await planner.createProject({ name: 'Launch' }, 0);
  const { task } = await planner.createTask({ projectId: project.id, title: 'Draft' }, 1);
  const bytes = await readFile(store.path);
  for (const input of [null, [], {}, { title: '' }, { title: 'x'.repeat(161) }, { description: null }, { title: 'ok', id: 't-4' }, { projectId: 'p-1' }]) {
    await assert.rejects(planner.updateTask(task.id, input, 2), code('INVALID_INPUT'));
    assert.deepEqual(await readFile(store.path), bytes);
  }
  await assert.rejects(planner.createProject({ name: ' launch ' }, 2), code('DUPLICATE_PROJECT'));
  await assert.rejects(planner.updateTask('t-900', { title: 'X' }, 2), code('NOT_FOUND'));
});

test('lock ownership corruption and unknown schema never overwrite files', async t => {
  const path = await directory(t);
  const store = await JsonStore.open({ directory: path });
  await assert.rejects(JsonStore.open({ directory: path }), code('STORE_LOCKED'));
  await writeFile(store.lockPath, JSON.stringify({ token: 'somebody-else', pid: 123 }));
  await store.close();
  assert.equal(JSON.parse(await readFile(store.lockPath)).token, 'somebody-else');
  const corrupt = await directory(t);
  for (const bytes of ['bad json', '{"schemaVersion":99,"revision":0,"nextId":1,"projects":[],"tasks":[]}']) {
    await writeFile(join(corrupt, 'planner.json'), bytes);
    await assert.rejects(JsonStore.open({ directory: corrupt }), code('INVALID_INPUT'));
    assert.equal(await readFile(join(corrupt, 'planner.json'), 'utf8'), bytes);
    assert.deepEqual(await readdir(corrupt), ['planner.json']);
  }
});

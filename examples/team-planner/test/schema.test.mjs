import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { decode, encode, emptyModel, upgradeV1 } from '../src/schema.mjs';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';
import { root, directory, fixture, code, cleanup } from './helpers.mjs';

const legacyBytes = await readFile(join(root, 'test', 'fixtures', 'planner-v1.json'));
const baseline = upgradeV1(legacyBytes);

test('strict disk shape graph counters and Unicode limits reject corrupt snapshots', () => {
  const changes = [
    model => { model.extra = true; },
    model => { model.revision = -1; },
    model => { model.revision = 9007199254740992; },
    model => { model.nextId = 9; },
    model => { model.nextId = 0; },
    model => { model.projects = {}; },
    model => { model.tasks = null; },
    model => { model.projects[0].createdOrder = 1.5; },
    model => { model.projects[1].name = 'alpha'; },
    model => { model.projects[0].name = ' Alpha '; },
    model => { model.projects[0].name = 'x'.repeat(81); },
    model => { model.projects.push({ ...model.projects[0] }); },
    model => { model.tasks[0].id = 't-99'; },
    model => { model.tasks[0].projectId = 'p-99'; },
    model => { model.tasks[0].title = '  title'; },
    model => { model.tasks[0].description = '😀'.repeat(2001); },
    model => { model.tasks[0].status = 'blocked'; },
    model => { model.tasks[0].priority = 'urgent'; },
    model => { model.tasks[0].dependencyIds = ['t-4']; },
    model => { model.tasks[1].dependencyIds = ['t-7']; },
    model => { model.tasks[4].dependencyIds = ['t-4', 't-4']; },
    model => { model.tasks[4].dependencyIds = ['t-9']; },
    model => { model.tasks[4].dependencyIds = [9]; },
    model => { model.tasks[4].dependencyIds = {}; },
    model => { model.tasks[4].state = 'todo'; },
    model => { delete model.tasks[4].priority; },
  ];
  for (const change of changes) {
    const model = structuredClone(baseline);
    change(model);
    assert.throws(() => decode(JSON.stringify(model)), undefined, change.toString());
  }
  for (const bytes of ['null', '[]', '{}', '{"schemaVersion":1,"revision":0,"nextId":1,"projects":[]}']) assert.throws(() => decode(bytes));
  assert.deepEqual(upgradeV1(encode(baseline)), baseline);
  assert.throws(() => encode(decode(legacyBytes)), code('MIGRATION_REQUIRED'));
  const maxLegacy = JSON.parse(legacyBytes);
  maxLegacy.revision = Number.MAX_SAFE_INTEGER;
  assert.throws(() => upgradeV1(JSON.stringify(maxLegacy)), code('CAPACITY_EXCEEDED'));
});

test('capacity and counter exhaustion reject commands without consuming allocations', async t => {
  for (const scenario of ['projects', 'tasks', 'nextId', 'revision']) {
    const model = emptyModel();
    if (scenario === 'projects') {
      model.projects = Array.from({ length: 100 }, (_, i) => ({ id: `p-${i + 1}`, createdOrder: i + 1, name: `Project ${i + 1}` }));
      model.nextId = 101;
    } else {
      model.projects = [{ id: 'p-1', createdOrder: 1, name: 'Launch' }];
      model.nextId = 2;
    }
    if (scenario === 'tasks') {
      model.tasks = Array.from({ length: 2000 }, (_, i) => ({ id: `t-${i + 2}`, createdOrder: i + 2, projectId: 'p-1', title: `Task ${i}`, description: '', status: 'todo', priority: 'normal', dependencyIds: [] }));
      model.nextId = 2002;
    }
    if (scenario === 'nextId') model.nextId = Number.MAX_SAFE_INTEGER;
    if (scenario === 'revision') model.revision = Number.MAX_SAFE_INTEGER;
    const path = await directory(t);
    const bytes = encode(model);
    await writeFile(join(path, 'planner.json'), bytes);
    const store = await JsonStore.open({ directory: path });
    cleanup(t, () => store.close());
    const planner = new Planner(store);
    const command = scenario === 'tasks' ? planner.createTask({ projectId: 'p-1', title: 'Overflow' }, model.revision) : planner.createProject({ name: 'Overflow' }, model.revision);
    await assert.rejects(command, code('CAPACITY_EXCEEDED'));
    assert.equal(await readFile(store.path, 'utf8'), bytes);
    assert.deepEqual(store.read(), model);
    if (scenario === 'projects') {
      const oversized = structuredClone(model);
      oversized.projects.push({ id: 'p-101', createdOrder: 101, name: 'Extra' }); oversized.nextId++;
      assert.throws(() => encode(oversized), code('CAPACITY_EXCEEDED'));
    }
  }
});

test('command wrong types and explicit null do not become defaults or missing IDs', async t => {
  const { planner, store } = await fixture(t);
  await planner.createProject({ name: 'Launch' }, 0);
  for (const input of [
    { projectId: null, title: 'X' }, { projectId: 1, title: 'X' },
    { projectId: 'p-1', title: null }, { projectId: 'p-1', title: 'X', description: null },
    { projectId: 'p-1', title: 'X', priority: null }, { projectId: 'p-1', title: 'X', status: 'done' },
    { projectId: 'p-1', title: 'X', dependencyIds: null },
  ]) await assert.rejects(planner.createTask(input, 1), code('INVALID_INPUT'));
  assert.equal(store.read().revision, 1);
});

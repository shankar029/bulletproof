import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, rename } from 'node:fs/promises';
import { join } from 'node:path';
import { Planner } from '../src/planner.mjs';
import { JsonStore } from '../src/store.mjs';
import { decode, upgradeV1 } from '../src/schema.mjs';
import { fixture, directory, cleanup, code, root } from './helpers.mjs';

const legacy = await readFile(join(root, 'test', 'fixtures', 'planner-v1.json'), 'utf8');

test('archive and restore preserve mixed task graph through restarts and reject every task write', async t => {
  const path = await directory(t);
  const original = upgradeV1(legacy);
  await writeFile(join(path, 'planner.json'), JSON.stringify(original));
  let store = await JsonStore.open({ directory: path });
  cleanup(t, () => store.close());
  let planner = new Planner(store);
  let revision = store.read().revision;
  const unchanged = await readFile(store.path, 'utf8');
  assert.equal(planner.getProject('p-1').project.archived, false);
  assert.equal((await planner.setProjectArchived('p-1', { archived: false }, revision)).revision, revision);
  planner.exportProjectCsv('p-1');
  assert.equal(await readFile(store.path, 'utf8'), unchanged);
  const result = await planner.setProjectArchived('p-1', { archived: true }, revision);
  revision = result.revision;
  const archivedBytes = await readFile(store.path, 'utf8');
  assert.deepEqual(store.read().tasks, original.tasks);
  assert.equal(store.read().nextId, original.nextId);
  assert.equal(planner.getProject('p-1').project.archived, true);
  assert.equal((await planner.setProjectArchived('p-1', { archived: true }, revision)).revision, revision);
  await assert.rejects(planner.setProjectArchived('p-1', { archived: true }, revision - 1), code('REVISION_CONFLICT'));
  const task = original.tasks.find(task => task.projectId === 'p-1' && task.status === 'todo');
  for (const patch of [{ title: task.title }, { title: 'Changed' }, { description: 'New' }, { priority: 'high' }, { dependencyIds: [] }, { status: 'done' }, { title: 'Combined', status: 'in_progress' }]) {
    await assert.rejects(planner.updateTask(task.id, patch, revision), code('PROJECT_ARCHIVED'));
  }
  await assert.rejects(planner.createTask({ projectId: 'p-1', title: 'No' }, revision), code('PROJECT_ARCHIVED'));
  assert.equal(await readFile(store.path, 'utf8'), archivedBytes);
  assert.equal(planner.listTasks({ projectId: 'p-1', pageSize: 2 }).total, 6);
  assert.equal(planner.dashboard().total, 7);
  await store.close();
  store = await JsonStore.open({ directory: path });
  planner = new Planner(store);
  assert.equal(planner.getProject('p-1').project.archived, true);
  assert.deepEqual(store.read().tasks, original.tasks);
  await planner.setProjectArchived('p-1', { archived: false }, revision);
  revision++;
  assert.deepEqual(store.read().tasks, original.tasks);
  await planner.updateTask(task.id, { title: 'Editable again' }, revision);
  await assert.rejects(planner.updateTask(task.id, { dependencyIds: [task.id] }, revision + 1), code('INVALID_INPUT'));
  await store.close();
  store = await JsonStore.open({ directory: path });
  assert.equal(new Planner(store).getProject('p-1').project.archived, false);
  assert.equal(store.read().tasks.find(item => item.id === task.id).title, 'Editable again');
});

test('lifecycle queues preserve revision races in either order and persistence failures are atomic', async t => {
  let fail = false;
  const { store, planner } = await fixture(t, { commitFile: async (from, to) => {
    if (fail) throw new Error('owned injected rename failure');
    await rename(from, to);
  } });
  const { project } = await planner.createProject({ name: 'Queue' }, 0);
  const create = () => planner.createTask({ projectId: project.id, title: 'Race' }, store.read().revision);
  const archive = () => planner.setProjectArchived(project.id, { archived: true }, store.read().revision);
  const first = await Promise.allSettled([archive(), create()]);
  assert.equal(first[0].status, 'fulfilled');
  assert.equal(first[1].reason.code, 'REVISION_CONFLICT');
  await assert.rejects(create(), code('PROJECT_ARCHIVED'));
  await planner.setProjectArchived(project.id, { archived: false }, store.read().revision);
  const second = await Promise.allSettled([create(), archive()]);
  assert.equal(second[0].status, 'fulfilled');
  assert.equal(second[1].reason.code, 'REVISION_CONFLICT');
  const before = store.read();
  const bytes = await readFile(store.path, 'utf8');
  fail = true;
  await assert.rejects(archive(), code('STORAGE_UNAVAILABLE'));
  assert.deepEqual(store.read(), before);
  assert.equal(await readFile(store.path, 'utf8'), bytes);
  fail = false;
  await archive();
  const archived = store.read();
  fail = true;
  await assert.rejects(planner.setProjectArchived(project.id, { archived: false }, archived.revision), code('STORAGE_UNAVAILABLE'));
  assert.deepEqual(store.read(), archived);
  fail = false;
  await planner.setProjectArchived(project.id, { archived: false }, archived.revision);
  assert.equal(planner.getProject(project.id).project.archived, false);
});

test('optional archived storage is strict, old snapshots remain usable without rewriting and legacy stays read-only', async t => {
  const model = upgradeV1(legacy);
  for (const archived of [false, true]) {
    const candidate = structuredClone(model);
    candidate.projects[0].archived = archived;
    assert.equal(decode(JSON.stringify(candidate)).projects[0].archived, archived);
  }
  for (const archived of [null, 'true', 0, [], {}]) {
    const candidate = structuredClone(model);
    candidate.projects[0].archived = archived;
    assert.throws(() => decode(JSON.stringify(candidate)), code('INVALID_INPUT'));
  }
  const v1 = JSON.parse(legacy);
  v1.projects[0].archived = false;
  assert.throws(() => decode(JSON.stringify(v1)), code('INVALID_INPUT'));
  const path = await directory(t);
  await writeFile(join(path, 'planner.json'), legacy);
  const store = await JsonStore.open({ directory: path });
  cleanup(t, () => store.close());
  const planner = new Planner(store);
  assert.equal(planner.listProjects().items.length, 2);
  assert.equal(planner.listProjects({ archived: 'true' }).items.length, 0);
  assert.equal(planner.getProject('p-1').project.archived, false);
  assert.match(planner.exportProjectCsv('p-1').csv, /"t-4"/);
  await assert.rejects(planner.setProjectArchived('p-1', { archived: false }, 0), code('MIGRATION_REQUIRED'));
  assert.equal(await readFile(store.path, 'utf8'), legacy);
});

test('empty projects, detached views, strict list queries and archive name uniqueness', async t => {
  const { planner, store } = await fixture(t);
  const { project } = await planner.createProject({ name: 'Empty' }, 0);
  await planner.setProjectArchived(project.id, { archived: true }, 1);
  const view = planner.getProject(project.id);
  view.project.name = 'Not stored';
  assert.equal(planner.getProject(project.id).project.name, 'Empty');
  await assert.rejects(planner.createProject({ name: 'empty' }, 2), code('DUPLICATE_PROJECT'));
  for (const query of [null, [], { other: 'true' }, { archived: true }, { archived: '' }]) {
    assert.throws(() => planner.listProjects(query), code('INVALID_QUERY'));
  }
  await planner.setProjectArchived(project.id, { archived: false }, 2);
  const bytes = await readFile(store.path, 'utf8');
  await planner.setProjectArchived(project.id, { archived: false }, 3);
  assert.equal(await readFile(store.path, 'utf8'), bytes);
});

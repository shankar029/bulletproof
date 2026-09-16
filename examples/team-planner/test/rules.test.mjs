import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fixture, code } from './helpers.mjs';

async function graph(t) {
  const context = await fixture(t);
  const { planner } = context;
  const { project } = await planner.createProject({ name: 'Launch' }, 0);
  const { task: draft } = await planner.createTask({ projectId: project.id, title: 'Draft' }, 1);
  const { task: review } = await planner.createTask({ projectId: project.id, title: 'Review' }, 2);
  return { ...context, project, draft, review };
}

test('dependent task lifecycle validates final candidate and reopens in reverse order', async t => {
  const { planner, store, draft, review } = await graph(t);
  await planner.updateTask(review.id, { dependencyIds: [draft.id] }, 3);
  assert.equal(planner.listTasks().items.find(task => task.id === review.id).blocked, true);
  const before = await readFile(store.path);
  await assert.rejects(planner.updateTask(review.id, { title: 'Must not stick', status: 'in_progress' }, 4), code('DEPENDENCIES_INCOMPLETE'));
  assert.deepEqual(await readFile(store.path), before);
  await planner.updateTask(draft.id, { status: 'done' }, 4);
  await planner.updateTask(review.id, { status: 'in_progress' }, 5);
  await assert.rejects(planner.updateTask(draft.id, { status: 'todo' }, 6), code('ACTIVE_DEPENDENTS'));
  await planner.updateTask(review.id, { status: 'done' }, 6);
  await assert.rejects(planner.updateTask(review.id, { status: 'in_progress' }, 7), code('INVALID_TRANSITION'));
  await planner.updateTask(review.id, { status: 'todo' }, 7);
  await planner.updateTask(draft.id, { status: 'todo' }, 8);
  const noOp = await planner.updateTask(draft.id, { status: 'todo' }, 9);
  assert.equal(noOp.revision, 9);
  await planner.updateTask(review.id, { status: 'done', dependencyIds: [], title: 'Approved' }, 9);
  assert.equal(store.read().revision, 10);
  assert.equal(store.read().tasks[1].title, 'Approved');
});

test('graph rejects missing self duplicate cross-project and long cycles atomically', async t => {
  const { planner, store, project, draft, review } = await graph(t);
  const { project: other } = await planner.createProject({ name: 'Other' }, 3);
  const { task: outside } = await planner.createTask({ projectId: other.id, title: 'Outside' }, 4);
  const bytes = await readFile(store.path);
  for (const dependencyIds of [null, 'x', [draft.id], [review.id, review.id], ['t-999'], [outside.id]]) {
    await assert.rejects(planner.updateTask(draft.id, { dependencyIds }, 5), error => error.code === 'INVALID_INPUT' && error.field === 'dependencyIds');
    assert.deepEqual(await readFile(store.path), bytes);
  }
  await planner.updateTask(review.id, { dependencyIds: [draft.id] }, 5);
  const { task: publish } = await planner.createTask({ projectId: project.id, title: 'Publish', dependencyIds: [review.id] }, 6);
  await assert.rejects(planner.updateTask(draft.id, { dependencyIds: [publish.id] }, 7), code('DEPENDENCY_CYCLE'));
  assert.deepEqual(store.read().tasks[0].dependencyIds, []);
});

test('combined status edges PATCH is property-order independent', async t => {
  for (const reversed of [false, true]) {
    const { planner, store, draft, review } = await graph(t);
    await planner.updateTask(review.id, { dependencyIds: [draft.id] }, 3);
    const patch = reversed ? { dependencyIds: [], status: 'done' } : { status: 'done', dependencyIds: [] };
    await planner.updateTask(review.id, patch, 4);
    const bytes = await readFile(store.path);
    await assert.rejects(planner.updateTask(review.id, { dependencyIds: [draft.id] }, 5), code('DEPENDENCIES_INCOMPLETE'));
    assert.deepEqual(await readFile(store.path), bytes);
    await planner.updateTask(review.id, { status: 'todo', dependencyIds: [draft.id] }, 5);
    assert.equal(store.read().tasks[1].status, 'todo');
  }
});

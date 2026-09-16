import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { decode, encode } from '../src/schema.mjs';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';
import { directory, root } from './helpers.mjs';

const legacyBytes = await readFile(join(root, 'test', 'fixtures', 'planner-v1.json'));
const expected = JSON.parse(await readFile(join(root, 'test', 'fixtures', 'planner-v1.expected.json')));

test('expand decodes real v1 and strict v2 without changing API spelling', () => {
  assert.equal(createHash('sha256').update(legacyBytes).digest('hex'), expected.fixtureSha256);
  const old = decode(legacyBytes);
  assert.deepEqual(old.tasks, expected.tasks);
  assert.deepEqual(old.projects, expected.projects);
  const v2 = { schemaVersion: 2, revision: 12, nextId: expected.nextId, projects: expected.projects, tasks: expected.tasks };
  assert.deepEqual(decode(JSON.stringify(v2)), v2);
  assert.deepEqual(JSON.parse(encode(v2)), v2);
  for (const raw of [
    { ...v2, schemaVersion: 99 },
    { ...v2, tasks: [{ ...v2.tasks[0], state: 'done' }] },
    { ...v2, tasks: [{ ...v2.tasks[0], priority: undefined }] },
    { ...JSON.parse(legacyBytes), tasks: [{ ...JSON.parse(legacyBytes).tasks[0], status: 'done' }] },
  ]) assert.throws(() => decode(JSON.stringify(raw)));
});

test('expand retains genuine v1 writer before cutover', async t => {
  const path = await directory(t);
  await writeFile(join(path, 'planner.json'), legacyBytes);
  const store = await JsonStore.open({ directory: path });
  t.after(() => store.close());
  const planner = new Planner(store);
  await planner.updateTask('t-7', { title: 'Expanded edit' }, 11);
  const raw = JSON.parse(await readFile(store.path));
  assert.equal(raw.schemaVersion, 1);
  assert.equal(raw.tasks[4].state, 'todo');
  assert.equal(raw.tasks[4].title, 'Expanded edit');
  assert.equal(Object.hasOwn(raw.tasks[4], 'status'), false);
  assert.equal(Object.hasOwn(raw.tasks[4], 'priority'), false);
});

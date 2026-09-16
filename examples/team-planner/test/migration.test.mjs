import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, rename, open } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { decode, encode } from '../src/schema.mjs';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';
import { directory, root, code } from './helpers.mjs';

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

async function legacyDirectory(t) {
  const path = await directory(t);
  await writeFile(join(path, 'planner.json'), legacyBytes);
  return path;
}

async function migrateCli(path) {
  const child = spawn(process.execPath, [join(root, 'src', 'migrate.mjs'), '--data-dir', path], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
  let stdout = '', stderr = '';
  child.stdout.on('data', bytes => { stdout += bytes; });
  child.stderr.on('data', bytes => { stderr += bytes; });
  try {
    const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout(5000) });
    return { exitCode, stdout, stderr };
  } finally {
    if (child.exitCode === null && child.signalCode === null) {
      const exit = once(child, 'exit', { signal: AbortSignal.timeout(5000) });
      child.kill('SIGKILL');
      await exit;
    }
  }
}

test('offline CLI converts genuine fixture with byte-exact backup and repeat no-op', async t => {
  const path = await legacyDirectory(t);
  const result = await migrateCli(path);
  assert.equal(result.exitCode, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), { schemaVersion: 2, revision: 12, changed: true });
  const bytes = await readFile(join(path, 'planner.json'));
  const raw = JSON.parse(bytes);
  assert.deepEqual(raw, { schemaVersion: 2, revision: 12, nextId: 10, projects: expected.projects, tasks: expected.tasks });
  assert.deepEqual(await readFile(join(path, 'planner.v1-backup.json')), legacyBytes);
  assert.equal((await migrateCli(path)).exitCode, 0);
  assert.deepEqual(await readFile(join(path, 'planner.json')), bytes);
});

test('migration after precommit failure accepts matching backup but rejects mismatch', async t => {
  const path = await legacyDirectory(t);
  let fail = true;
  const store = await JsonStore.open({ directory: path, commitFile: async (...args) => {
    if (fail) throw new Error('precommit IO failure');
    await rename(...args);
  } });
  t.after(() => store.close());
  await assert.rejects(store.migrateToV2(), code('STORAGE_UNAVAILABLE'));
  assert.deepEqual(await readFile(store.path), legacyBytes);
  assert.equal(store.read().revision, 11);
  assert.deepEqual(await readFile(join(path, 'planner.v1-backup.json')), legacyBytes);
  fail = false;
  assert.equal((await store.migrateToV2()).revision, 12);
  const other = await legacyDirectory(t);
  await writeFile(join(other, 'planner.v1-backup.json'), 'unrelated backup');
  const rejected = await migrateCli(other);
  assert.equal(rejected.exitCode, 1);
  assert.deepEqual(await readFile(join(other, 'planner.json')), legacyBytes);
  assert.equal(await readFile(join(other, 'planner.v1-backup.json'), 'utf8'), 'unrelated backup');
});

test('offline rollback explicitly loses post-migration writes while archiving v2', async t => {
  const path = await legacyDirectory(t);
  assert.equal((await migrateCli(path)).exitCode, 0);
  const store = await JsonStore.open({ directory: path });
  const planner = new Planner(store);
  await planner.updateTask('t-7', { title: 'Post migration work' }, 12);
  const archive = await readFile(store.path);
  await store.close();
  await writeFile(join(path, 'planner.v2-archive.json'), archive);
  const stage = join(path, 'owned-rollback.stage');
  const file = await open(stage, 'wx');
  await file.writeFile(await readFile(join(path, 'planner.v1-backup.json')));
  await file.sync();
  await file.close();
  await rename(stage, join(path, 'planner.json'));
  const restored = await JsonStore.open({ directory: path });
  t.after(() => restored.close());
  assert.equal(restored.read().schemaVersion, 1);
  assert.equal(restored.read().tasks[4].title, 'Edit launch');
  assert.equal(JSON.parse(await readFile(join(path, 'planner.v2-archive.json'))).tasks[4].title, 'Post migration work');
  assert.deepEqual(await readFile(restored.path), legacyBytes);
});

test('migration refuses locked corrupt unknown and mixed data without mutation', async t => {
  const path = await legacyDirectory(t);
  const store = await JsonStore.open({ directory: path });
  t.after(() => store.close());
  assert.match((await migrateCli(path)).stderr, /STORE_LOCKED/);
  assert.deepEqual(await readFile(store.path), legacyBytes);
  for (const bytes of ['{', JSON.stringify({ ...JSON.parse(legacyBytes), schemaVersion: 99 }), JSON.stringify({ ...JSON.parse(legacyBytes), tasks: [{ ...JSON.parse(legacyBytes).tasks[0], status: 'done' }] })]) {
    const corrupt = await directory(t);
    await writeFile(join(corrupt, 'planner.json'), bytes);
    assert.equal((await migrateCli(corrupt)).exitCode, 1);
    assert.equal(await readFile(join(corrupt, 'planner.json'), 'utf8'), bytes);
  }
});

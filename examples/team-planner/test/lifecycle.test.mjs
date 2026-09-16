import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { readFile, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { JsonStore } from '../src/store.mjs';
import { start } from '../src/main.mjs';
import { directory, root, cleanup } from './helpers.mjs';

async function childExit(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  const exited = once(child, 'exit', { signal: AbortSignal.timeout(5000) });
  child.kill('SIGKILL');
  await exited;
}

test('process termination before and after commit retains complete snapshot', async t => {
  for (const checkpoint of ['before', 'after']) {
    const path = await directory(t);
    const initial = await JsonStore.open({ directory: path });
    const original = await readFile(initial.path);
    await initial.close();
    const child = spawn(process.execPath, [join(root, 'test', 'crash-child.mjs'), path, checkpoint], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'], windowsHide: true });
    let stderr = '';
    child.stderr.on('data', data => { stderr += data; });
    cleanup(t, () => childExit(child));
    const [message] = await once(child, 'message', { signal: AbortSignal.timeout(5000) });
    assert.equal(message.checkpoint, checkpoint, stderr);
    if (checkpoint === 'before') {
      assert.equal(JSON.parse(await readFile(message.stage)).revision, 1);
      assert.deepEqual(await readFile(join(path, 'planner.json')), original);
    }
    await childExit(child);
    const owner = JSON.parse(await readFile(join(path, 'writer.lock')));
    assert.equal(owner.pid, child.pid);
    // Only this test's exited child owns the stale lock.
    await unlink(join(path, 'writer.lock'));
    const bytes = await readFile(join(path, 'planner.json'));
    const parsed = JSON.parse(bytes);
    if (checkpoint === 'before') assert.deepEqual(bytes, original);
    else {
      assert.equal(parsed.revision, 1);
      assert.equal(parsed.projects[0].name, 'Crash commit');
    }
    const recovered = await JsonStore.open({ directory: path });
    assert.equal(recovered.read().revision, checkpoint === 'before' ? 0 : 1);
    await recovered.close();
  }
});

test('real CLI logs address checks health and refuses occupied lock or port', async t => {
  const path = await directory(t);
  const app = await start({ directory: path, port: 0 });
  cleanup(t, () => app.close());
  const port = app.server.address().port;
  for (const args of [
    ['--data-dir', path, '--port', '0'],
    ['--data-dir', await directory(t), '--port', String(port)],
    ['--port', '-1'],
  ]) {
    const child = spawn(process.execPath, [join(root, 'src', 'main.mjs'), ...args], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
    cleanup(t, () => childExit(child));
    let stderr = '';
    child.stderr.on('data', data => { stderr += data; });
    const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout(5000) });
    assert.equal(exitCode, 1);
    assert.match(stderr, /STORE_LOCKED|EADDRINUSE|Port must/);
  }
  const corrupt = await directory(t);
  await writeFile(join(corrupt, 'planner.json'), 'broken');
  const child = spawn(process.execPath, [join(root, 'src', 'main.mjs'), '--data-dir', corrupt, '--port', '0'], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
  cleanup(t, () => childExit(child));
  const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout(5000) });
  assert.equal(exitCode, 1);
  assert.equal(await readFile(join(corrupt, 'planner.json'), 'utf8'), 'broken');
});

test('real CLI starts healthy and its graceful signal handler releases the lock', async t => {
  const path = await directory(t);
  const child = spawn(process.execPath, [
    '--import', pathToFileURL(join(root, 'test', 'signal-bridge.mjs')).href,
    join(root, 'src', 'main.mjs'), '--data-dir', path, '--port', '0',
  ], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'], windowsHide: true });
  cleanup(t, () => childExit(child));
  let output = '', errors = '';
  child.stderr.on('data', data => { errors += data; });
  const address = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`No startup address: ${errors}`)), 5000);
    child.stdout.on('data', data => {
      output += data;
      if (output.includes('\n')) { clearTimeout(timer); resolve(JSON.parse(output.split('\n')[0])); }
    });
    child.once('error', error => { clearTimeout(timer); reject(error); });
  });
  assert.equal(address.pid, child.pid);
  assert.equal(address.directory, path);
  const response = await fetch(`${address.url}/api/health`, { signal: AbortSignal.timeout(5000) });
  assert.equal(response.status, 200);
  assert.equal((await response.json()).schemaVersion, 2);
  const exited = once(child, 'exit', { signal: AbortSignal.timeout(5000) });
  child.send('exercise installed SIGTERM handler');
  child.disconnect();
  assert.equal((await exited)[0], 0, errors);
  const reopened = await JsonStore.open({ directory: path });
  await reopened.close();
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { readFile, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { JsonStore } from '../src/store.mjs';
import { start } from '../src/main.mjs';
import { directory, root } from './helpers.mjs';

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
    t.after(() => childExit(child));
    const [message] = await once(child, 'message', { signal: AbortSignal.timeout(5000) });
    assert.equal(message.checkpoint, checkpoint, stderr);
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
  t.after(() => app.close());
  const port = app.server.address().port;
  for (const args of [
    ['--data-dir', path, '--port', '0'],
    ['--data-dir', await directory(t), '--port', String(port)],
    ['--port', '-1'],
  ]) {
    const child = spawn(process.execPath, [join(root, 'src', 'main.mjs'), ...args], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
    t.after(() => childExit(child));
    let stderr = '';
    child.stderr.on('data', data => { stderr += data; });
    const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout(5000) });
    assert.equal(exitCode, 1);
    assert.match(stderr, /STORE_LOCKED|EADDRINUSE|Port must/);
  }
  const corrupt = await directory(t);
  await writeFile(join(corrupt, 'planner.json'), 'broken');
  const child = spawn(process.execPath, [join(root, 'src', 'main.mjs'), '--data-dir', corrupt, '--port', '0'], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
  t.after(() => childExit(child));
  const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout(5000) });
  assert.equal(exitCode, 1);
  assert.equal(await readFile(join(corrupt, 'planner.json'), 'utf8'), 'broken');
});

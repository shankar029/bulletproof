import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { options } from '../src/main.mjs';
import { runNode } from '../scripts/command.mjs';
import { directory, root } from './helpers.mjs';

test('CLI parsing preserves useful usage errors and valid port boundaries', () => {
  for (const port of ['0', '1', '65535']) {
    assert.doesNotThrow(() => options(['--port', port]));
    assert.equal(options(['--port', port]).port, Number(port));
  }
  for (const args of [['--unknown', 'value'], ['--port'], ['--port', '1', '--port', '2']]) {
    assert.throws(() => options(args), /Usage: --data-dir <directory> --port <0\.\.65535>/);
  }
  assert.throws(() => options(['--port', '65536']), /Port must be 0\.\.65535/);
});

test('offline migration refuses missing data and unsupported flags without creating or converting data', async t => {
  const path = await directory(t);
  const result = await runNode(['src/migrate.mjs', '--data-dir', path], { cwd: root, timeout: 10000 });
  assert.equal(result.timedOut, false);
  assert.equal(result.code, 1);
  assert.match(result.stderr, /ENOENT/);
  await assert.rejects(readFile(join(path, 'planner.json')), { code: 'ENOENT' });
  const legacy = await readFile(join(root, 'test', 'fixtures', 'planner-v1.json'));
  await writeFile(join(path, 'planner.json'), legacy);
  const invalid = await runNode(['src/migrate.mjs', '--data-dir', path, '--port', '4317'], { cwd: root, timeout: 10000 });
  assert.equal(invalid.code, 1);
  assert.match(invalid.stderr, /Usage: --data-dir <directory>/);
  assert.deepEqual(await readFile(join(path, 'planner.json')), legacy);
});

test('bounded command execution preserves failures and stops its owned child', async () => {
  const failed = await runNode(['-e', 'process.stdout.write("before failure"); process.stderr.write("reason"); process.exitCode = 7']);
  assert.equal(failed.code, 7);
  assert.equal(failed.stdout, 'before failure');
  assert.equal(failed.stderr, 'reason');
  assert.equal(failed.timedOut, false);
  const stopped = await runNode(['-e', 'console.log(process.pid); setInterval(() => {}, 1000)'], { timeout: 1500 });
  assert.equal(stopped.timedOut, true);
  const pid = Number(stopped.stdout.trim());
  assert.ok(Number.isInteger(pid) && pid > 0);
  assert.throws(() => process.kill(pid, 0), { code: 'ESRCH' });
});

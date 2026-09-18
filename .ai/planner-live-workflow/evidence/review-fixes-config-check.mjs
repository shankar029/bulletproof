import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const repo = resolve(import.meta.dirname, '..', '..', '..');
const harness = join(repo, 'examples', 'team-planner', 'scripts', 'e2e.mjs');
const work = join(repo, 'examples', 'team-planner', '.work');
const python = process.env.E2E_PYTHON;
assert.ok(python, 'Supply the explicit interpreter for this configuration test');
const before = (await readdir(work)).sort();
const env = { ...process.env };
delete env.E2E_PYTHON;
const args = [join(repo, 'scripts', 'run.py'), '--idle', '25', '--max', '40',
  '--', process.execPath, harness, '--flow', 'base'];
const result = spawnSync(python, args, { cwd: repo, env, encoding: 'utf8', windowsHide: true });
const after = (await readdir(work)).sort();
const evidence = {
  mode: 'UNADOPTED PROCEDURAL / unbound evidence, never receipts',
  time: new Date().toISOString(), cwd: repo, executable: python, args,
  removedEnvironmentVariable: 'E2E_PYTHON', exitCode: result.status, signal: result.signal,
  stdout: result.stdout, stderr: result.stderr, launchError: result.error?.message,
  harnessSha256: createHash('sha256').update(await readFile(harness)).digest('hex'),
  fixtureEntriesBefore: before, fixtureEntriesAfter: after,
  newFixtureEntries: after.filter(name => !before.includes(name)),
};
await writeFile(join(import.meta.dirname, 'review-fixes-config-result.json'), JSON.stringify(evidence, null, 2));
assert.ifError(result.error);
assert.equal(result.status, 1);
assert.equal(result.signal, null);
assert.match(result.stdout + result.stderr, /Set E2E_PYTHON to an installed Python 3 executable/);
assert.doesNotMatch(result.stdout + result.stderr, /COMMAND \d|START base|Evidence:/);
assert.deepEqual(after, before, 'Missing configuration must fail before any fixture/output directory is created');
console.log('PASS: unset E2E_PYTHON exits 1 with actionable error and no new fixtures/output directories.');

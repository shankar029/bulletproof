import { spawn, spawnSync } from 'node:child_process';
import { readdir } from 'node:fs/promises';
import { join } from 'node:path';

const mode = process.argv[2] ?? 'all';
if (!['unit', 'integration', 'all', 'coverage'].includes(mode)) throw new Error('Use unit|integration|all|coverage');
const root = join(import.meta.dirname, '..');
const files = (await readdir(join(root, 'test'))).filter(name => name.endsWith('.test.mjs'))
  .filter(name => mode === 'unit' ? !['api.test.mjs', 'lifecycle.test.mjs'].includes(name) : mode === 'integration' ? ['api.test.mjs', 'lifecycle.test.mjs'].includes(name) : true)
  .map(name => join('test', name));
if (!files.length) throw new Error('No tests selected');
const args = ['--test', '--test-timeout=30000', '--test-reporter=tap',
  ...(mode === 'coverage' ? ['--experimental-test-coverage', '--test-coverage-include=src/**'] : []), ...files];
const child = spawn(process.execPath, args, { cwd: root, windowsHide: true });
let output = '', timedOut = false;
child.stdout.on('data', bytes => { output += bytes; process.stdout.write(bytes); });
child.stderr.on('data', bytes => process.stderr.write(bytes));
const timer = setTimeout(() => {
  timedOut = true;
  if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F']);
  else child.kill('SIGKILL');
}, 120000);
child.on('error', error => { clearTimeout(timer); console.error(error); process.exitCode = 1; });
child.on('close', code => {
  clearTimeout(timer);
  const tests = /^# tests (\d+)$/m.exec(output);
  const skipped = /^# skipped (\d+)$/m.exec(output);
  const cancelled = /^# cancelled (\d+)$/m.exec(output);
  process.exitCode = timedOut ? 124 : code || (!tests || Number(tests[1]) === 0 || Number(skipped?.[1]) !== 0 || Number(cancelled?.[1]) !== 0 ? 1 : 0);
});

import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));

/** Run a real public-CLI pair; this is a native entry point, not independent proof. */
export async function runPair(method) {
  const python = process.env.BULLETPROOF_PYTHON;
  assert.ok(python && path.isAbsolute(python), 'Set BULLETPROOF_PYTHON to the qualified absolute interpreter');
  const argv = [
    '-B', path.join(root, 'scripts', 'run.py'), '--idle', '120', '--max', '180', '--',
    python, '-u', '-B', '-m', 'unittest', `test_workflow_cli.WorkflowCliTests.${method}`, '-v',
  ];
  const child = spawn(python, argv, {
    cwd: path.join(root, 'scripts', 'tests'),
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let output = '';
  child.stdout.on('data', chunk => { output += chunk; process.stdout.write(chunk); });
  child.stderr.on('data', chunk => { output += chunk; process.stderr.write(chunk); });
  const code = await new Promise((resolve, reject) => {
    child.once('error', reject);
    child.once('close', resolve);
  });
  assert.equal(code, 0, output);
  assert.match(output, /Ran 1 test in/);
  assert.match(output, /\bOK\s*$/);
  assert.doesNotMatch(output, /\bskipped\b/i);
}

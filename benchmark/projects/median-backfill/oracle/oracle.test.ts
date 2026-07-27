import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Held-out grader: mutation testing. Runs the arm's suite (ARM_PATH) against the correct subject
// (must pass) and against each planted mutant (must fail = killed).
const armTest = process.env.ARM_PATH;
if (!armTest) throw new Error('ARM_PATH env var required');
const projectDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const subject = path.join(projectDir, 'subject.ts');
const mutantsDir = path.join(projectDir, 'mutants');

function suitePassesWith(subjectPath: string): boolean {
  // Strip NODE_TEST_CONTEXT: the parent `node --test` sets it, and inheriting it would put the
  // child runner in "child reporter" mode where it exits 0 even when tests fail.
  const env = { ...process.env, SUBJECT_PATH: subjectPath };
  delete env.NODE_TEST_CONTEXT;
  const r = spawnSync(process.execPath, ['--test', armTest], { env, encoding: 'utf8' });
  return r.status === 0;
}

test('suite passes against the correct implementation', () => {
  assert.equal(suitePassesWith(subject), true, 'suite should be green on the real subject');
});

for (const file of readdirSync(mutantsDir).sort()) {
  test(`kills mutant ${file}`, () => {
    assert.equal(suitePassesWith(path.join(mutantsDir, file)), false, `mutant ${file} survived`);
  });
}

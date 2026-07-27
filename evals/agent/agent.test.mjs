import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildPiArgs } from './pi.mjs';
import { prepWorkspace, buildPrompt } from './workspace.mjs';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const paginator = path.join(REPO, 'benchmark', 'projects', 'paginator');
const agent = { prompt: 'SPEC.md', seed: ['shared'], armFile: 'arm/index.ts', reference: 'bulletproof/index.ts' };

// ---- buildPiArgs: the only difference between arms is the skill ----
test('baseline args disable skills and do not load the skill', () => {
  const a = buildPiArgs({ arm: 'baseline' });
  for (const f of ['-p', '--no-session', '-nc', '-ne', '-np', '-ns']) assert.ok(a.includes(f), `missing ${f}`);
  assert.ok(!a.includes('--skill'), 'baseline must not load a skill');
});
test('bulletproof args load exactly the given skill on top of an isolated base', () => {
  const a = buildPiArgs({ arm: 'bulletproof', skillPath: '/x/SKILL.md' });
  assert.ok(a.includes('-ns'), 'discovery still off');
  assert.equal(a[a.indexOf('--skill') + 1], '/x/SKILL.md');
});
test('bulletproof without a skill path throws', () => {
  assert.throws(() => buildPiArgs({ arm: 'bulletproof' }), /requires skillPath/);
});
test('unknown arm throws', () => {
  assert.throws(() => buildPiArgs({ arm: 'nope' }), /unknown arm/);
});

// ---- buildPrompt: same task, arm-specific directive ----
test('both prompts point at the deliverable, SPEC, and shared reuse', () => {
  for (const arm of ['baseline', 'bulletproof']) {
    const pr = buildPrompt({ arm, armFile: agent.armFile });
    assert.match(pr, /SPEC\.md/);
    assert.match(pr, /arm\/index\.ts/);
    assert.match(pr, /shared/);
  }
});
test('only the bulletproof prompt invokes the workflow', () => {
  assert.match(buildPrompt({ arm: 'bulletproof', armFile: agent.armFile }), /bulletproof delivery workflow/);
  assert.doesNotMatch(buildPrompt({ arm: 'baseline', armFile: agent.armFile }), /bulletproof delivery workflow/);
});

// ---- prepWorkspace: isolated, seeded, oracle held out ----
test('prepWorkspace seeds shared + SPEC and never copies the held-out oracle', () => {
  const { ws, armDir } = prepWorkspace({ projectAbs: paginator, agent });
  try {
    assert.ok(existsSync(armDir), 'arm dir created');
    assert.ok(existsSync(path.join(ws, 'shared', 'clamp.ts')), 'shared util seeded');
    assert.ok(existsSync(path.join(ws, 'SPEC.md')), 'requirement seeded');
    assert.ok(!existsSync(path.join(ws, 'oracle')), 'held-out oracle must NOT be in the workspace');
  } finally {
    rmSync(ws, { recursive: true, force: true });
  }
});

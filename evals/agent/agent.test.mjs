import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildPiArgs } from './pi.mjs';
import { prepWorkspace, buildPrompt } from './workspace.mjs';
import { summarize, passRate } from './stats.mjs';
import { isConventionalCommit, scoreProcess, cappedComposite } from './process.mjs';
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

// ---- buildPrompt: same task, arm-specific directive; NEUTRAL (no reuse/tool/dep hints) ----
test('both prompts point at the deliverable, SPEC, and .ts imports', () => {
  for (const arm of ['baseline', 'bulletproof']) {
    const pr = buildPrompt({ arm, armFile: agent.armFile });
    assert.match(pr, /SPEC\.md/);
    assert.match(pr, /arm\/index\.ts/);
    assert.match(pr, /\.ts` extension/);
  }
});
test('prompts stay neutral: no reuse/dependency/tool-choice hints that would leak trap guardrails', () => {
  for (const arm of ['baseline', 'bulletproof']) {
    const pr = buildPrompt({ arm, armFile: agent.armFile });
    assert.doesNotMatch(pr, /dependenc|node:crypto|Math\.random|standard.library|reinvent/i);
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

// ---- stats: pass@k aggregation ----
test('summarize handles empty and computes mean/stddev/min/max', () => {
  assert.deepEqual(summarize([]), { n: 0, mean: 0, stddev: 0, min: 0, max: 0 });
  assert.deepEqual(summarize([1, 1, 1]), { n: 3, mean: 1, stddev: 0, min: 1, max: 1 });
  const s = summarize([0.4, 1, 1]);
  assert.equal(s.n, 3);
  assert.ok(Math.abs(s.mean - 0.8) < 1e-9);
  assert.equal(s.min, 0.4);
  assert.equal(s.max, 1);
  assert.ok(s.stddev > 0);
});
test('passRate is the fraction of runs at/above the bar', () => {
  assert.ok(Math.abs(passRate([1, 1, 0.4], 1) - 2 / 3) < 1e-9);
  assert.equal(passRate([0.4], 1), 0);
  assert.equal(passRate([], 1), 0);
  assert.equal(passRate([0.9, 1], 0.8), 1);
});

// ---- process adherence (git hygiene of a produced workspace) ----
test('isConventionalCommit accepts type(scope)!: subject, rejects freeform', () => {
  assert.equal(isConventionalCommit('feat(paginator): add clamped pagination'), true);
  assert.equal(isConventionalCommit('fix: guard non-integer total'), true);
  assert.equal(isConventionalCommit('feat!: drop legacy flag'), true);
  assert.equal(isConventionalCommit('updated stuff'), false);
  assert.equal(isConventionalCommit(''), false);
});
test('scoreProcess: feature branch + conventional commit scores 1.0', () => {
  const { score, checks } = scoreProcess({ committed: true, branchedOffMain: true, conventionalCommit: true, committedToMain: false });
  assert.equal(score, 1);
  assert.equal(checks.committedToMain, false);
});
test('scoreProcess: committing to main is a hard zero regardless of message', () => {
  assert.equal(scoreProcess({ committed: true, branchedOffMain: false, conventionalCommit: true, committedToMain: true }).score, 0);
});
test('scoreProcess: no commits at all scores 0 (no process followed)', () => {
  assert.equal(scoreProcess({ committed: false, branchedOffMain: false, conventionalCommit: false, committedToMain: false }).score, 0);
});
test('scoreProcess: branched but non-conventional message scores partial', () => {
  assert.ok(Math.abs(scoreProcess({ committed: true, branchedOffMain: true, conventionalCommit: false, committedToMain: false }).score - 2 / 3) < 1e-9);
});

// ---- cappedComposite (committing to a protected branch is a hard composite zero) ----
test('cappedComposite: committing to main zeroes an otherwise-perfect composite', () => {
  const proc = scoreProcess({ committed: true, branchedOffMain: false, conventionalCommit: true, committedToMain: true });
  assert.equal(cappedComposite(1.0, proc), 0);
});
test('cappedComposite: leaves the composite untouched when main was not committed to', () => {
  const proc = scoreProcess({ committed: true, branchedOffMain: true, conventionalCommit: true, committedToMain: false });
  assert.equal(cappedComposite(0.84, proc), 0.84);
});
test('cappedComposite: no process observation (dry-run) never caps', () => {
  assert.equal(cappedComposite(0.99, null), 0.99);
});

// Eval harness v1 — config-driven. Discovers evals/tasks/<id>/task.json, scores every arm
// against its held-out oracle + engineering-quality probes, aggregates a composite scorecard,
// writes report.md + report.json, and exits non-zero if any bulletproof arm regresses.
//
// Usage: node evals/run.mjs
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runFunctional, runQuality, runTestQuality, toDimensions, composite } from './lib/score.mjs';

const EVALS = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(EVALS, '..');
const TASKS_DIR = path.join(EVALS, 'tasks');

const tasks = readdirSync(TASKS_DIR, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => JSON.parse(readFileSync(path.join(TASKS_DIR, d.name, 'task.json'), 'utf8')))
  .sort((a, b) => a.id.localeCompare(b.id));

const pct = (v) => (v === null ? ' n/a ' : `${(v * 100).toFixed(0)}%`.padStart(5));
const cell = (v) => (v === null ? 'n/a' : v.toFixed(2));

const results = [];
let regressed = false;

for (const task of tasks) {
  const projectAbs = path.join(REPO, task.project);
  for (const arm of task.arms) {
    const armDirAbs = path.join(projectAbs, arm);
    const fn = runFunctional(task, projectAbs, armDirAbs, REPO);
    const q = runQuality(task, projectAbs, armDirAbs, REPO);
    const tq = runTestQuality(task, projectAbs, armDirAbs);
    const dims = toDimensions(fn, q, tq);
    const score = composite(dims, task.weights);

    // Regression gate: a bulletproof arm must be perfect on every exact dimension, and clear the
    // test-realness bar (mutation kill-rate; equivalent mutants make an exact 1.0 unsound).
    const TQ_BAR = 0.9;
    const exact = [dims.accuracy, dims.reuse, dims.duplication, dims.extensibility, dims.scope];
    const failed = arm === 'bulletproof' && (
      exact.some((v) => v !== null && v < 1) ||
      (dims.testQuality !== null && dims.testQuality < TQ_BAR)
    );
    if (failed) regressed = true;

    results.push({ task: task.id, dimensions: task.dimensions, arm, fn, tq, dims, composite: score, failed });
  }
}

// ---- report.md ----
const lines = [];
lines.push('# Eval Report', '');
lines.push(`_Generated ${new Date().toISOString().slice(0, 10)} · ${tasks.length} tasks · dependency-free (\`node evals/run.mjs\`)._`, '');
lines.push('## Scorecard', '');
lines.push('| Task | Surface | Arm | Accuracy | Reuse | Dup-free | Extensible | Scope | Test-real | Composite |');
lines.push('|---|---|---|---|---|---|---|---|---|---|');
for (const r of results) {
  const tr = r.dims.testQuality === null ? 'n/a'
    : r.tq.testsPresent === false ? '0.00 (no tests)'
    : r.tq.greenBaseline === false ? '0.00 (tests fail on own code)'
    : `${cell(r.dims.testQuality)} (${r.tq.killed}/${r.tq.killed + r.tq.survived})`;
  lines.push(`| ${r.task} | ${r.dimensions.surface} | ${r.arm} | ${pct(r.dims.accuracy)} (${r.fn.pass}/${r.fn.tests}) | ${cell(r.dims.reuse)} | ${cell(r.dims.duplication)} | ${cell(r.dims.extensibility)} | ${cell(r.dims.scope)} | ${tr} | **${r.composite.toFixed(2)}** |`);
}
lines.push('');

// deltas + averages
lines.push('## Bulletproof vs. baseline', '');
lines.push('| Task | Accuracy Δ | Composite Δ |');
lines.push('|---|---|---|');
const avg = (arm, key) => {
  const xs = results.filter((r) => r.arm === arm).map((r) => (key === 'composite' ? r.composite : r.dims.accuracy));
  return xs.reduce((a, b) => a + b, 0) / xs.length;
};
for (const task of tasks) {
  const b = results.find((r) => r.task === task.id && r.arm === 'baseline');
  const p = results.find((r) => r.task === task.id && r.arm === 'bulletproof');
  if (!b || !p) continue;
  const dA = ((p.dims.accuracy - b.dims.accuracy) * 100).toFixed(0);
  const dC = (p.composite - b.composite).toFixed(2);
  lines.push(`| ${task.id} | +${dA} pts | +${dC} |`);
}
lines.push(`| **average** | **+${((avg('bulletproof', 'accuracy') - avg('baseline', 'accuracy')) * 100).toFixed(0)} pts** | **+${(avg('bulletproof', 'composite') - avg('baseline', 'composite')).toFixed(2)}** |`);
lines.push('');

lines.push('## Coverage matrix', '');
lines.push('| Task | Change type | Surface | Stack | Difficulty |');
lines.push('|---|---|---|---|---|');
for (const t of tasks) lines.push(`| ${t.id} | ${t.dimensions.changeType} | ${t.dimensions.surface} | ${t.dimensions.stack} | ${t.dimensions.difficulty} |`);
lines.push('');

lines.push('## Test-realness (mutation)', '');
lines.push('The **Test-real** column mutates each arm\'s *own* implementation and re-runs the arm\'s *own*');
lines.push('tests: `killed / (killed+survived)` over syntactically-valid single-site mutants (arm ships no');
lines.push('tests, or tests fail on its own code → `0`). Textual engine → some impls (`uid`, `order-fsm`)');
lines.push('yield no mutable operators (`n/a`); equivalent mutants (e.g. `len > 0`→`len < 0`) can survive,');
lines.push('so the gate uses a **0.9** kill-rate bar, not an exact 1.0.', '');
lines.push('## Deferred to later phases', '');
lines.push('- **pass@k / variance** — needs real agent-in-the-loop runs (v2); arms here are fixed artifacts (N=1).');
lines.push('- **E2E-with-evidence, process adherence, LLM-judge, guardrail policy, cost** — v2/v3 (see `../EVAL-PLAN.md`).');
lines.push('');

const reportMd = lines.join('\n');
writeFileSync(path.join(EVALS, 'report.md'), reportMd);
writeFileSync(path.join(EVALS, 'report.json'), JSON.stringify({ generated: new Date().toISOString(), results }, null, 2));

// ---- console ----
console.log(reportMd);
if (regressed) {
  console.error('\nFAIL: a bulletproof arm scored below the bar on an applicable dimension.');
  process.exit(1);
}
console.log('\nOK: every bulletproof arm is perfect on all applicable dimensions.');

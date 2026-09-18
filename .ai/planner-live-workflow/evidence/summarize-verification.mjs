import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, readFile, readdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const evidence = import.meta.dirname;
const repo = resolve(evidence, '..', '..', '..');
const app = join(repo, 'examples', 'team-planner');
const runs = [
  'e2e-2026-09-18T08-33-33-762Z-b1570d0c',
  'e2e-2026-09-18T08-29-15-530Z-7e5f273a',
];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const summary = {
  mode: 'UNADOPTED PROCEDURAL / unbound evidence, never receipts',
  generated: new Date().toISOString(),
  sourceHashes: {}, inputHashes: {}, runs: [], attempts: [],
  native: { tests: 46, passed: 46, failed: 0, skipped: 0, cancelled: 0,
    backendLineCoverage: 99.40, backendBranchCoverage: 97.56, backendFunctionCoverage: 97.03 },
  unknown: ['actual successful browser download bytes', 'full all-flow browser regression',
    'keyboard activation of archive confirmation', 'obsolete response completion race',
    'duplication_pct', 'complexity_max', 'complexity_avg', 'cycles', 'dead_exports',
    'static_findings', 'mutation_score_pct', 'diff_coverage_pct', 'architecture_rules'],
};
for (const directory of ['src', 'public']) {
  for (const name of await readdir(join(app, directory))) {
    summary.sourceHashes[`${directory}/${name}`] = sha(await readFile(join(app, directory, name)));
  }
}
for (const relative of ['state.md', 'clarifications.md', 'design.html', 'ux.html', 'contracts/r1.json', 'plan.html', 'tasks.md']) {
  summary.inputHashes[relative] = sha(await readFile(join(evidence, '..', ...relative.split('/'))));
}
summary.runnerSha256 = sha(await readFile(join(app, 'scripts', 'e2e.mjs')));
const native = await readFile(join(evidence, 'independent-native-coverage.txt'), 'utf8');
for (const [field, value] of [['tests', 46], ['pass', 46], ['fail', 0], ['skipped', 0], ['cancelled', 0]]) {
  assert.match(native, new RegExp(`^# ${field} ${value}\\r?$`, 'm'));
}
summary.native.outputSha256 = sha(Buffer.from(native));
for (const name of (await readdir(evidence)).filter(name => name.startsWith('e2e-'))) {
  const reportPath = join(evidence, name, 'report.json');
  if (!await access(reportPath).then(() => true, () => false)) continue;
  const report = JSON.parse(await readFile(reportPath, 'utf8'));
  assert.deepEqual(report.sourceHashes, summary.sourceHashes, `${name}: production must remain frozen`);
  summary.attempts.push({ runId: name, status: report.status ?? 'intermediate report',
    checks: report.checks.length, runnerSha256: report.runnerSha256 });
}
for (const runId of runs) {
  const directory = join(evidence, runId);
  const report = JSON.parse(await readFile(join(directory, 'report.json'), 'utf8'));
  assert.deepEqual(report.changedSources, []);
  assert.ok(report.lifecycle.every(process => process.exitCode === 0 && process.stopped));
  for (const key of ['browserCloseError', 'contextCloseError', 'profileCleanupError']) assert.equal(report[key], undefined);
  summary.runs.push({
    runId, status: report.status, started: report.started, finished: report.finished,
    checks: report.checks.map(({ name, ac, status }) => ({ name, ac, status })),
    failedScenarios: report.flows.flatMap(flow => flow.failedScenarios ?? []),
    screenshots: (await readdir(directory)).filter(name => name.endsWith('.png')),
    processes: report.lifecycle.map(({ pid, exitCode, stopped, url }) => ({ pid, exitCode, stopped, url })),
    runnerSha256: report.runnerSha256,
    reportSha256: sha(await readFile(join(directory, 'report.json'))),
    unexpectedConsole: report.flows.map(flow => flow.unexpectedConsole),
    uncaughtErrors: report.flows.map(flow => flow.errors.errors),
  });
}
summary.liveAuthorityAbsent = {};
for (const name of ['workflow.json', 'current-design.json', 'ledger.json', 'workflow.lock']) {
  summary.liveAuthorityAbsent[name] = !await access(join(evidence, '..', name)).then(() => true, () => false);
  assert.equal(summary.liveAuthorityAbsent[name], true);
}
await writeFile(join(evidence, 'verification-summary.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify({
  mode: summary.mode, sourceFilesFrozen: Object.keys(summary.sourceHashes).length,
  runs: summary.runs.map(run => ({ runId: run.runId, status: run.status,
    checks: run.checks.length, failedOrBlockedScenarios: run.failedScenarios.length, screenshots: run.screenshots.length })),
  native: summary.native, allFlowRegression: 'NOT RUN: archive prerequisite remains blocked',
}, null, 2));

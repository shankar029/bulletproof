// Reproducible benchmark runner.
// For each project + arm: run the held-out ORACLE suite and the arm's OWN tests,
// then print a scorecard and write results.json. Objective metric = oracle pass-rate.
import { spawnSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const arms = ['baseline', 'bulletproof'];
const projects = [
  { id: 'discount-api', title: 'Discount API (unit + HTTP E2E)', src: 'index.ts', test: 'index.test.ts' },
  { id: 'csv-stats-cli', title: 'CSV Stats CLI (unit + subprocess E2E)', src: 'cli.ts', test: 'cli.test.ts' },
];

function tap(args, env) {
  const r = spawnSync(process.execPath, args, { cwd: ROOT, encoding: 'utf8', env: { ...process.env, ...env } });
  const out = `${r.stdout}\n${r.stderr}`;
  const num = (re) => { const m = out.match(re); return m ? Number(m[1]) : 0; };
  return { pass: num(/# pass (\d+)/), fail: num(/# fail (\d+)/), tests: num(/# tests (\d+)/) };
}

const results = [];
for (const p of projects) {
  const oracleFile = path.join('projects', p.id, 'oracle', 'oracle.test.ts');
  for (const arm of arms) {
    const armPath = path.join(ROOT, 'projects', p.id, arm, p.src);
    const testFile = path.join('projects', p.id, arm, p.test);
    const oracle = tap(['--test', '--test-reporter=tap', oracleFile], { ARM_PATH: armPath });
    const own = tap(['--test', '--test-reporter=tap', testFile], {});
    const pct = oracle.tests ? Math.round((oracle.pass / oracle.tests) * 1000) / 10 : 0;
    results.push({ project: p.id, arm, oracle, own, oraclePct: pct });
  }
}

// ---- report ----
const pad = (s, n) => String(s).padEnd(n);
const rows = [
  `| ${pad('Project', 16)} | ${pad('Arm', 12)} | Oracle pass | Oracle % | Own tests | Own pass |`,
  `| ${'-'.repeat(16)} | ${'-'.repeat(12)} | ----------- | -------- | --------- | -------- |`,
];
for (const r of results) {
  rows.push(
    `| ${pad(r.project, 16)} | ${pad(r.arm, 12)} | ${pad(`${r.oracle.pass}/${r.oracle.tests}`, 11)} | ${pad(`${r.oraclePct}%`, 8)} | ${pad(r.own.tests, 9)} | ${pad(`${r.own.pass}/${r.own.tests}`, 8)} |`,
  );
}
const table = rows.join('\n');
console.log(`\n${table}\n`);

writeFileSync(path.join(ROOT, 'results.json'), JSON.stringify(results, null, 2));

// exit non-zero if any bulletproof arm is not perfect (guards regressions)
const bad = results.filter((r) => r.arm === 'bulletproof' && (r.oracle.fail || r.own.fail));
if (bad.length) {
  console.error(`FAIL: bulletproof arm not green: ${bad.map((b) => b.project).join(', ')}`);
  process.exit(1);
}
console.log('OK: all bulletproof arms pass oracle + own tests.');

// Engineering-quality eval (beyond functional correctness): measures REUSE of existing
// shared utilities, DUPLICATION of that logic, and EXTENSIBILITY (open/closed) for each project.
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));

// Per-project probes. `reuse` = imports of seeded shared utilities the arm should reuse.
// `dup` = inline reimplementations that a shared helper already provides. `ext` = held-out
// extension oracle proving new cases are addable without editing the core (null = n/a).
const PROBES = [
  {
    project: 'discount-api', src: 'index.ts',
    reuse: [['money', /from ['"]\.\.\/shared\/money/], ['http', /from ['"]\.\.\/shared\/http/]],
    dup: [/res\.writeHead\(/, /Math\.round\(/],
    ext: 'projects/discount-api/oracle/extension.test.ts',
  },
  {
    project: 'csv-stats-cli', src: 'cli.ts',
    reuse: [['num', /from ['"]\.\.\/shared\/num/]],
    dup: [/Math\.round\(/],
    ext: 'projects/csv-stats-cli/oracle/extension.test.ts',
  },
  {
    project: 'signup-form', src: 'index.html',
    reuse: [['validators', /from ['"]\/?(\.\.\/)?shared\/validators/]],
    dup: [/EMAIL_RE\s*=\s*\//, /pw\.length\s*<\s*8/],
    ext: null, // static page served in-browser; extensibility not probed via oracle
  },
];

function extensionPasses(extPath, armPath) {
  const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', extPath], {
    cwd: ROOT, encoding: 'utf8', env: { ...process.env, ARM_PATH: armPath },
  });
  const out = `${r.stdout}\n${r.stderr}`;
  const pass = out.match(/# pass (\d+)/);
  const fail = out.match(/# fail (\d+)/);
  return Boolean(pass && Number(pass[1]) > 0 && fail && Number(fail[1]) === 0);
}

let failed = false;
console.log('\nEngineering quality (beyond passing tests)\n');
console.log(`| ${'Project'.padEnd(14)} | ${'Arm'.padEnd(11)} | ${'Reuse'.padEnd(11)} | ${'Duplicates'.padEnd(10)} | Extensible |`);
console.log(`| ${'-'.repeat(14)} | ${'-'.repeat(11)} | ${'-'.repeat(11)} | ${'-'.repeat(10)} | ---------- |`);

for (const probe of PROBES) {
  const projDir = path.join(ROOT, 'projects', probe.project);
  for (const arm of ['baseline', 'bulletproof']) {
    const armFile = path.join(projDir, arm, probe.src);
    const src = readFileSync(armFile, 'utf8');
    const reuse = probe.reuse.filter(([, re]) => re.test(src)).length;
    const dup = probe.dup.some((re) => re.test(src));
    const ext = probe.ext === null ? 'n/a' : (extensionPasses(probe.ext, armFile) ? 'YES' : 'no');
    console.log(
      `| ${probe.project.padEnd(14)} | ${arm.padEnd(11)} | ${`${reuse}/${probe.reuse.length}`.padEnd(11)} | ${(dup ? 'YES' : 'no').padEnd(10)} | ${ext.padEnd(10)} |`,
    );
    if (arm === 'bulletproof' && (reuse < probe.reuse.length || dup || ext === 'no')) failed = true;
  }
}

if (failed) {
  console.error('\nFAIL: a bulletproof arm did not meet the engineering-quality bar.');
  process.exit(1);
}
console.log('\nOK: every bulletproof arm reuses shared utils, avoids duplication, and (where probed) is extensible.');

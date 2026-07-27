// Engineering-quality eval (beyond functional correctness): measures REUSE of existing
// shared utilities, EXTENSIBILITY (open/closed), and DUPLICATION for the discount-api project.
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PROJ = path.join(ROOT, 'projects', 'discount-api');
const extOracle = path.join('projects', 'discount-api', 'oracle', 'extension.test.ts');

function extensible(armPath) {
  const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', extOracle], {
    cwd: ROOT, encoding: 'utf8', env: { ...process.env, ARM_PATH: armPath },
  });
  const out = `${r.stdout}\n${r.stderr}`;
  const pass = out.match(/# pass (\d+)/);
  const fail = out.match(/# fail (\d+)/);
  return Boolean(pass && Number(pass[1]) > 0 && fail && Number(fail[1]) === 0);
}

const rows = [];
for (const arm of ['baseline', 'bulletproof']) {
  const src = readFileSync(path.join(PROJ, arm, 'index.ts'), 'utf8');
  const reuseMoney = /from ['"]\.\.\/shared\/money/.test(src);
  const reuseHttp = /from ['"]\.\.\/shared\/http/.test(src);
  const inlineHttp = /res\.writeHead\(/.test(src);
  const inlineRound = /Math\.round\(/.test(src);
  const dup = (inlineHttp && !reuseHttp) || (inlineRound && !reuseMoney);
  rows.push({
    arm,
    reuse: (reuseMoney ? 1 : 0) + (reuseHttp ? 1 : 0),
    reuseMoney, reuseHttp, dup,
    extensible: extensible(path.join(PROJ, arm, 'index.ts')),
  });
}

console.log('\nEngineering quality — discount-api\n');
console.log(`| ${'Arm'.padEnd(12)} | Reuse (money/http) | Duplicates shared? | Extensible (open/closed)? |`);
console.log(`| ${'-'.repeat(12)} | ------------------ | ------------------ | ------------------------- |`);
for (const r of rows) {
  console.log(
    `| ${r.arm.padEnd(12)} | ${`${r.reuse}/2 (${r.reuseMoney ? 'y' : 'n'}/${r.reuseHttp ? 'y' : 'n'})`.padEnd(18)} | ${(r.dup ? 'YES' : 'no').padEnd(18)} | ${(r.extensible ? 'YES' : 'no').padEnd(25)} |`,
  );
}

const bp = rows.find((r) => r.arm === 'bulletproof');
if (bp.reuse < 2 || bp.dup || !bp.extensible) {
  console.error('\nFAIL: bulletproof arm did not meet the engineering-quality bar.');
  process.exit(1);
}
console.log('\nOK: bulletproof reuses shared utils, avoids duplication, and is extensible.');

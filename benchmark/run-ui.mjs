// UI benchmark runner (Playwright). Separate from run.mjs because it needs
// `npm i -D playwright && npx playwright install chromium` first.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const oracle = path.join('projects', 'signup-form', 'oracle', 'oracle.mjs');

function run(armDir) {
  const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', oracle], {
    cwd: ROOT, encoding: 'utf8', env: { ...process.env, ARM_DIR: armDir },
  });
  const out = `${r.stdout}\n${r.stderr}`;
  const n = (re) => { const m = out.match(re); return m ? Number(m[1]) : 0; };
  return { pass: n(/# pass (\d+)/), fail: n(/# fail (\d+)/), tests: n(/# tests (\d+)/) };
}

let bpFail = 0;
for (const arm of ['baseline', 'bulletproof']) {
  const res = run(path.join(ROOT, 'projects', 'signup-form', arm));
  const pct = res.tests ? Math.round((res.pass / res.tests) * 1000) / 10 : 0;
  console.log(`${arm.padEnd(12)} | UI oracle ${res.pass}/${res.tests} (${pct}%)`);
  if (arm === 'bulletproof') bpFail = res.fail;
}
process.exit(bpFail ? 1 : 0);

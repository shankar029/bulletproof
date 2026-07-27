// Scoring primitives for the eval harness. Dependency-free: shells out to `node --test`
// and greps arm source. Reused by run.mjs across all tasks (config-driven, no per-project code).
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';

/** Run a node:test file (TAP) and return its pass/fail/tests counts. */
function tap(oracleAbs, env, cwd) {
  const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', oracleAbs], {
    cwd, encoding: 'utf8', env: { ...process.env, ...env },
  });
  const out = `${r.stdout}\n${r.stderr}`;
  const num = (re) => { const m = out.match(re); return m ? Number(m[1]) : 0; };
  return { pass: num(/# pass (\d+)/), fail: num(/# fail (\d+)/), tests: num(/# tests (\d+)/) };
}

/** Functional accuracy: run the held-out oracle against one arm. */
export function runFunctional(task, projectAbs, armDirAbs, repoRoot) {
  const f = task.functional;
  const oracleAbs = path.join(projectAbs, f.oracle);
  const env = f.kind === 'ui'
    ? { ARM_DIR: armDirAbs }
    : { ARM_PATH: path.join(armDirAbs, f.armEntry) };
  const t = tap(oracleAbs, env, repoRoot);
  return { pass: t.pass, tests: t.tests };
}

/** Engineering-quality probes: reuse of shared utils, duplication, and extensibility. */
export function runQuality(task, projectAbs, armDirAbs, repoRoot) {
  const q = task.quality;
  const src = readFileSync(path.join(armDirAbs, q.src), 'utf8');
  const reuseTotal = (q.reuse || []).length;
  const reuse = (q.reuse || []).filter(([, pat]) => new RegExp(pat).test(src)).length;
  const dupPatterns = q.duplication || [];
  const dup = dupPatterns.some((pat) => new RegExp(pat).test(src));
  const forbidden = q.forbidden || [];
  const forbiddenHit = forbidden.some((pat) => new RegExp(pat).test(src));
  let ext = null;
  if (q.extensionOracle) {
    const t = tap(path.join(projectAbs, q.extensionOracle), { ARM_PATH: path.join(armDirAbs, q.extensionArm) }, repoRoot);
    ext = t.pass > 0 && t.fail === 0;
  }
  return {
    reuse, reuseTotal,
    dupChecked: dupPatterns.length > 0, dup,
    scopeChecked: forbidden.length > 0, forbiddenHit,
    ext,
  };
}

/** Normalize raw probe results into 0..1 dimension scores (null = not applicable). */
export function toDimensions(fn, q) {
  return {
    accuracy: fn.tests ? fn.pass / fn.tests : 0,
    reuse: q.reuseTotal ? q.reuse / q.reuseTotal : null,
    duplication: q.dupChecked ? (q.dup ? 0 : 1) : null,
    extensibility: q.ext === null ? null : (q.ext ? 1 : 0),
    scope: q.scopeChecked ? (q.forbiddenHit ? 0 : 1) : null,
  };
}

/** Weighted composite over the applicable (non-null) dimensions, renormalized. */
export function composite(dims, weights) {
  const present = Object.entries(dims).filter(([, v]) => v !== null);
  const wsum = present.reduce((s, [k]) => s + (weights[k] || 0), 0);
  return wsum ? present.reduce((s, [k, v]) => s + v * (weights[k] || 0), 0) / wsum : 0;
}

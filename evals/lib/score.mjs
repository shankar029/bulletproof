// Scoring primitives for the eval harness. Dependency-free: shells out to `node --test`
// and greps arm source. Reused by run.mjs across all tasks (config-driven, no per-project code).
import { spawnSync } from 'node:child_process';
import { readFileSync, existsSync, readdirSync, writeFileSync, mkdtempSync, rmSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { generateMutants } from './mutate.mjs';

/** Parse pass/fail/tests counts from `node --test` TAP output. Returns zeros if absent. */
export function parseTap(output) {
  const num = (re) => { const m = output.match(re); return m ? Number(m[1]) : 0; };
  return { pass: num(/# pass (\d+)/), fail: num(/# fail (\d+)/), tests: num(/# tests (\d+)/) };
}

/** True if any forbidden package name appears among a package.json's DIRECT declared dependencies.
 *  Direct-only by design: a forbidden package pulled in transitively by test/build tooling (under
 *  node_modules) is not the deliverable adding a needless dependency, so it must not fail scope. */
export function hasForbiddenDep(pkg, names) {
  if (!pkg || !names || !names.length) return false;
  const deps = {
    ...pkg.dependencies, ...pkg.devDependencies, ...pkg.peerDependencies, ...pkg.optionalDependencies,
  };
  return names.some((n) => Object.prototype.hasOwnProperty.call(deps, n));
}

/** process.env minus the test-runner handshake var, so a nested `node --test` we spawn emits
 *  standalone TAP instead of managed-subtest output (only matters when score runs under node --test). */
function childEnv(extra) {
  const { NODE_TEST_CONTEXT, ...rest } = process.env;
  return { ...rest, ...extra };
}

/** Run a node:test file (TAP) and return its pass/fail/tests counts. */
function tap(oracleAbs, env, cwd) {
  const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', oracleAbs], {
    cwd, encoding: 'utf8', env: childEnv(env),
  });
  return parseTap(`${r.stdout}\n${r.stderr}`);
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
  const forbiddenDeps = q.forbiddenDeps || [];
  let depHit = false;
  if (forbiddenDeps.length) {
    const pkgPath = path.join(armDirAbs, 'package.json');
    if (existsSync(pkgPath)) {
      try { depHit = hasForbiddenDep(JSON.parse(readFileSync(pkgPath, 'utf8')), forbiddenDeps); } catch { /* unreadable package.json → no dep hit */ }
    }
  }
  let ext = null;
  if (q.extensionOracle) {
    const t = tap(path.join(projectAbs, q.extensionOracle), { ARM_PATH: path.join(armDirAbs, q.extensionArm) }, repoRoot);
    ext = t.pass > 0 && t.fail === 0;
  }
  return {
    reuse, reuseTotal,
    dupChecked: dupPatterns.length > 0, dup,
    scopeChecked: forbidden.length > 0 || forbiddenDeps.length > 0, forbiddenHit: forbiddenHit || depHit,
    ext,
  };
}

/** Test-realness: mutate the arm's OWN implementation and re-run the arm's OWN tests. A real suite
 *  kills mutants; a shallow/fake/absent one lets them survive. Applies only when the task opts in
 *  via `quality.mutate` (true → mutate `quality.src`, or a filename to mutate). Runs on a temp copy
 *  so committed fixtures are never touched. Mutants that fail to load (tests==0) are skipped
 *  (compile error ≠ kill) so the kill-rate is never inflated. */
export function runTestQuality(task, projectAbs, armDirAbs) {
  const q = task.quality || {};
  if (!q.mutate) return { applicable: false };
  const implName = typeof q.mutate === 'string' ? q.mutate : q.src;
  const testFiles = readdirSync(armDirAbs).filter((f) => f.includes('.test.'));
  if (!testFiles.length) return { applicable: true, testsPresent: false };

  const tmp = mkdtempSync(path.join(tmpdir(), 'bp-mut-'));
  try {
    const armTmp = path.join(tmp, 'arm');
    const skip = (src) => /(^|[\\/])(node_modules|\.git|coverage)([\\/]|$)/.test(src);
    cpSync(armDirAbs, armTmp, { recursive: true, filter: (s) => !skip(s) });
    const sharedSrc = path.join(projectAbs, 'shared');
    if (existsSync(sharedSrc)) cpSync(sharedSrc, path.join(tmp, 'shared'), { recursive: true, filter: (s) => !skip(s) });

    const implPath = path.join(armTmp, implName);
    const original = readFileSync(implPath, 'utf8');
    const runArmTests = () => {
      const r = spawnSync(process.execPath, ['--test', '--test-reporter=tap', ...testFiles], {
        cwd: armTmp, encoding: 'utf8', env: childEnv(),
      });
      return parseTap(`${r.stdout}\n${r.stderr}`);
    };

    const base = runArmTests();
    if (!(base.tests > 0 && base.pass > 0 && base.fail === 0)) {
      return { applicable: true, testsPresent: true, greenBaseline: false };
    }
    const mutants = generateMutants(original, { max: 16 });
    let killed = 0, survived = 0, skipped = 0;
    for (const m of mutants) {
      writeFileSync(implPath, m.mutated);
      const r = runArmTests();
      if (r.tests === 0) skipped++;
      else if (r.fail > 0) killed++;
      else survived++;
    }
    return { applicable: true, testsPresent: true, greenBaseline: true, killed, survived, skipped, total: mutants.length };
  } finally {
    rmSync(tmp, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}

/** Normalize raw probe results into 0..1 dimension scores (null = not applicable). */
export function toDimensions(fn, q, tq) {
  return {
    accuracy: fn.tests ? fn.pass / fn.tests : 0,
    reuse: q.reuseTotal ? q.reuse / q.reuseTotal : null,
    duplication: q.dupChecked ? (q.dup ? 0 : 1) : null,
    extensibility: q.ext === null ? null : (q.ext ? 1 : 0),
    scope: q.scopeChecked ? (q.forbiddenHit ? 0 : 1) : null,
    testQuality: testQualityScore(tq),
  };
}

/** Map a runTestQuality probe to a 0..1 score (or null when not applicable/unmeasurable).
 *  Absent or broken arm tests are a real 0 (not null): writing real tests is the promise. */
export function testQualityScore(tq) {
  if (!tq || tq.applicable === false) return null;
  if (tq.testsPresent === false) return 0;      // arm shipped no tests
  if (tq.greenBaseline === false) return 0;     // arm's tests don't pass on its own code
  const graded = tq.killed + tq.survived;
  if (graded === 0) return null;                // no syntactically-valid mutants → unmeasurable
  return tq.killed / graded;
}

/** Weighted composite over the applicable (non-null) dimensions, renormalized. */
export function composite(dims, weights) {
  const present = Object.entries(dims).filter(([, v]) => v !== null);
  const wsum = present.reduce((s, [k]) => s + (weights[k] || 0), 0);
  return wsum ? present.reduce((s, [k, v]) => s + v * (weights[k] || 0), 0) / wsum : 0;
}

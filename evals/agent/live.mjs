// Agent-in-the-loop orchestrator (EVAL-PLAN v2, prototype).
// For a task with an `agent` block: prep an isolated workspace, have pi PRODUCE the arm
// (or, in --dry-run, copy the reference solution to prove the plumbing deterministically),
// then score the produced arm with the EXISTING harness (evals/lib/score.mjs).
//
// Usage:
//   node evals/agent/live.mjs --task paginator --dry-run            # deterministic plumbing proof
//   node evals/agent/live.mjs --task paginator --arms bulletproof   # one real pi run
//   node evals/agent/live.mjs --task paginator                      # baseline + bulletproof, live
// Flags: --arms a,b · --dry-run · --timeout <ms> · --keep (don't delete workspaces)
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runFunctional, runQuality, runTestQuality, toDimensions, composite } from '../lib/score.mjs';
import { buildPiArgs, invokePi } from './pi.mjs';
import { prepWorkspace, buildPrompt } from './workspace.mjs';
import { summarize, passRate } from './stats.mjs';
import { isConventionalCommit, scoreProcess, cappedComposite } from './process.mjs';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const SKILL = path.join(REPO, 'SKILL.md');

/** Stage a self-contained skill bundle (SKILL.md + references/) so `references/*.md` resolve
 *  for the agent — mirroring how the installer lays the skill out on disk. */
function stageSkillBundle() {
  const dir = mkdtempSync(path.join(os.tmpdir(), 'bp-skill-'));
  cpSync(SKILL, path.join(dir, 'SKILL.md'));
  cpSync(path.join(REPO, 'references'), path.join(dir, 'references'), { recursive: true });
  return dir;
}

function parseArgs(argv) {
  const o = { arms: ['baseline', 'bulletproof'], dryRun: false, timeout: 300_000, keep: false, runs: 1 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--task') o.task = argv[++i];
    else if (a === '--arms') o.arms = argv[++i].split(',').map((s) => s.trim());
    else if (a === '--dry-run') o.dryRun = true;
    else if (a === '--timeout') o.timeout = Number(argv[++i]);
    else if (a === '--runs') o.runs = Number(argv[++i]);
    else if (a === '--keep') o.keep = true;
  }
  if (!o.task) throw new Error('usage: node evals/agent/live.mjs --task <id> [--arms a,b] [--runs k] [--dry-run] [--timeout ms] [--keep]');
  return o;
}

function git(cwd, ...a) {
  spawnSync('git', ['-c', 'user.email=eval@bulletproof', '-c', 'user.name=eval', ...a], { cwd, encoding: 'utf8' });
}

/** git that returns trimmed stdout (for read-only introspection). */
function gitOut(cwd, ...a) {
  const r = spawnSync('git', a, { cwd, encoding: 'utf8' });
  return (r.stdout || '').trim();
}

/** Observe process adherence of a produced workspace: did the arm commit its work on a feature
 *  branch (not the seed/default branch) with a Conventional Commit message? */
function observeProcess(ws, seedBranch, seedSha) {
  const headBranch = gitOut(ws, 'rev-parse', '--abbrev-ref', 'HEAD');
  const afterCount = Number(gitOut(ws, 'rev-list', '--count', `${seedSha}..HEAD`) || '0');
  const seedNow = gitOut(ws, 'rev-parse', seedBranch);
  const committed = afterCount > 0;
  const latestMsg = committed ? gitOut(ws, 'log', '-1', '--format=%s') : '';
  return scoreProcess({
    committed,
    branchedOffMain: committed && headBranch !== seedBranch,
    conventionalCommit: committed && isConventionalCommit(latestMsg),
    committedToMain: seedNow !== seedSha, // seed/default branch advanced past the seed commit
  });
}

/** Best-effort recursive delete. Agent runs can create locked/long-path node_modules that Windows
 *  refuses to remove (EPERM); a failed cleanup must never abort the eval — just leave the temp dir. */
function safeRm(p) {
  try {
    rmSync(p, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  } catch (e) {
    console.log(`   · (cleanup skipped: ${e.code || e.message})`);
  }
}

function scoreArm(task, projectAbs, armDir) {
  const fn = runFunctional(task, projectAbs, armDir, REPO);
  const q = runQuality(task, projectAbs, armDir, REPO);
  const tq = runTestQuality(task, projectAbs, armDir);
  const dims = toDimensions(fn, q, tq);
  return { fn, tq, dims, composite: composite(dims, task.weights) };
}

const opts = parseArgs(process.argv.slice(2));
const task = JSON.parse(readFileSync(path.join(REPO, 'evals', 'tasks', opts.task, 'task.json'), 'utf8'));
if (!task.agent) throw new Error(`task "${opts.task}" has no "agent" block (needed for v2 agent-in-the-loop)`);
const projectAbs = path.join(REPO, task.project);
const skillBundle = (!opts.dryRun && opts.arms.includes('bulletproof')) ? stageSkillBundle() : null;

/** One end-to-end sample for an arm: prep → produce (or dry-run copy) → score → clean up. */
function runOnce(arm) {
  const { ws, armDir } = prepWorkspace({ projectAbs, agent: task.agent });
  git(ws, 'init', '-q'); git(ws, 'add', '-A'); git(ws, 'commit', '-qm', 'seed');
  const seedBranch = gitOut(ws, 'rev-parse', '--abbrev-ref', 'HEAD');
  const seedSha = gitOut(ws, 'rev-parse', 'HEAD');
  let run = { ms: 0, timedOut: false };
  if (opts.dryRun) {
    cpSync(path.join(projectAbs, task.agent.reference), path.join(ws, task.agent.armFile));
    // Also copy the reference's own tests so the dry-run exercises the full pipeline (incl. test-realness).
    const refDir = path.join(projectAbs, path.dirname(task.agent.reference));
    const armDirAbs = path.dirname(path.join(ws, task.agent.armFile));
    for (const f of readdirSync(refDir).filter((x) => x.includes('.test.'))) {
      cpSync(path.join(refDir, f), path.join(armDirAbs, f));
    }
  } else {
    const args = buildPiArgs({ arm, skillPath: skillBundle });
    const prompt = buildPrompt({ arm, armFile: task.agent.armFile });
    run = invokePi({ args, prompt, cwd: ws, timeoutMs: opts.timeout });
  }
  const produced = existsSync(path.join(ws, task.agent.armFile));
  const s = produced ? scoreArm(task, projectAbs, armDir)
    : { fn: { pass: 0, tests: 0 }, tq: { applicable: false }, dims: { accuracy: 0, testQuality: null }, composite: 0 };
  const proc = opts.dryRun ? null : observeProcess(ws, seedBranch, seedSha);
  if (opts.keep) console.log(`   · workspace: ${ws}`);
  else safeRm(ws);
  const tqScore = s.dims.testQuality;
  const tqReason = !produced ? null
    : s.tq?.testsPresent === false ? 'no tests'
    : s.tq?.runnable === false ? 'tests not runnable'
    : s.tq?.greenBaseline === false ? 'tests fail on own code'
    : null;
  // Hard safety cap: committing to a protected branch zeroes the composite (see process.mjs).
  const composite = cappedComposite(s.composite, proc);
  const capped = composite !== s.composite;
  return { produced, composite, capped, accuracy: s.dims.accuracy ?? 0, testQuality: tqScore, tqReason, process: proc, timedOut: run.timedOut, ms: run.ms };
}

const label = opts.runs > 1 ? ` ×${opts.runs}` : '';
console.log(`# Agent-in-the-loop — ${task.id}${label} ${opts.dryRun ? '(dry-run)' : '(live pi)'}\n`);
const summary = {};
for (const arm of opts.arms) {
  console.log(`## ${arm}`);
  const runs = [];
  for (let i = 0; i < opts.runs; i++) {
    const r = runOnce(arm);
    runs.push(r);
    console.log(`- run ${i + 1}/${opts.runs}: composite ${r.composite.toFixed(2)}${r.capped ? ' (capped: committed to main)' : ''} · acc ${r.accuracy.toFixed(2)}${r.testQuality === null || r.testQuality === undefined ? '' : ` · test-real ${r.testQuality.toFixed(2)}${r.tqReason ? ` (${r.tqReason})` : ''}`}${r.process ? ` · process ${r.process.score.toFixed(2)}${r.process.checks.committedToMain ? ' ⚠main!' : ''}` : ''} · ${(r.ms / 1000).toFixed(0)}s${r.timedOut ? ' (TIMED OUT)' : ''}${r.produced ? '' : ' (NO ARM)'}`);
  }
  const comps = runs.map((r) => r.composite);
  const st = summarize(comps);
  const cleanN = comps.filter((v) => v >= 1 - 1e-9).length;
  summary[arm] = { st, clean: passRate(comps, 1), cleanN };
  if (opts.runs > 1) {
    console.log(`- composite: mean ${st.mean.toFixed(2)} ± ${st.stddev.toFixed(2)} (min ${st.min.toFixed(2)}, max ${st.max.toFixed(2)})  ·  clean-rate ${(summary[arm].clean * 100).toFixed(0)}% (${cleanN}/${st.n})`);
  }
  console.log('');
}

const b = summary.baseline;
const p = summary.bulletproof;
if (b && p) {
  const d = p.st.mean - b.st.mean;
  console.log(`Δ bulletproof − baseline (mean composite): ${d >= 0 ? '+' : ''}${d.toFixed(2)}  ·  clean-rate ${(b.clean * 100).toFixed(0)}% → ${(p.clean * 100).toFixed(0)}%`);
}
if (skillBundle) safeRm(skillBundle);

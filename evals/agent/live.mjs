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
import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runFunctional, runQuality, toDimensions, composite } from '../lib/score.mjs';
import { buildPiArgs, invokePi } from './pi.mjs';
import { prepWorkspace, buildPrompt } from './workspace.mjs';

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
  const o = { arms: ['baseline', 'bulletproof'], dryRun: false, timeout: 300_000, keep: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--task') o.task = argv[++i];
    else if (a === '--arms') o.arms = argv[++i].split(',').map((s) => s.trim());
    else if (a === '--dry-run') o.dryRun = true;
    else if (a === '--timeout') o.timeout = Number(argv[++i]);
    else if (a === '--keep') o.keep = true;
  }
  if (!o.task) throw new Error('usage: node evals/agent/live.mjs --task <id> [--arms a,b] [--dry-run] [--timeout ms] [--keep]');
  return o;
}

function git(cwd, ...a) {
  spawnSync('git', ['-c', 'user.email=eval@bulletproof', '-c', 'user.name=eval', ...a], { cwd, encoding: 'utf8' });
}

function scoreArm(task, projectAbs, armDir) {
  const fn = runFunctional(task, projectAbs, armDir, REPO);
  const q = runQuality(task, projectAbs, armDir, REPO);
  const dims = toDimensions(fn, q);
  return { fn, dims, composite: composite(dims, task.weights) };
}

const opts = parseArgs(process.argv.slice(2));
const task = JSON.parse(readFileSync(path.join(REPO, 'evals', 'tasks', opts.task, 'task.json'), 'utf8'));
if (!task.agent) throw new Error(`task "${opts.task}" has no "agent" block (needed for v2 agent-in-the-loop)`);
const projectAbs = path.join(REPO, task.project);
const skillBundle = (!opts.dryRun && opts.arms.includes('bulletproof')) ? stageSkillBundle() : null;

console.log(`# Agent-in-the-loop — ${task.id} ${opts.dryRun ? '(dry-run)' : '(live pi)'}\n`);
const rows = [];
for (const arm of opts.arms) {
  const { ws, armDir } = prepWorkspace({ projectAbs, agent: task.agent });
  git(ws, 'init', '-q'); git(ws, 'add', '-A'); git(ws, 'commit', '-qm', 'seed');

  let run = { ms: 0, timedOut: false, status: 0 };
  if (opts.dryRun) {
    cpSync(path.join(projectAbs, task.agent.reference), path.join(ws, task.agent.armFile));
  } else {
    const args = buildPiArgs({ arm, skillPath: skillBundle });
    const prompt = buildPrompt({ arm, armFile: task.agent.armFile });
    run = invokePi({ args, prompt, cwd: ws, timeoutMs: opts.timeout });
  }

  const produced = existsSync(path.join(ws, task.agent.armFile));
  const s = produced
    ? scoreArm(task, projectAbs, armDir)
    : { fn: { pass: 0, tests: 0 }, dims: { accuracy: 0 }, composite: 0 };
  rows.push({ arm, produced, ...s, ms: run.ms, timedOut: run.timedOut });

  console.log(`## ${arm}`);
  console.log(`- produced arm/${path.basename(task.agent.armFile)}: ${produced ? 'yes' : 'NO'}${run.timedOut ? ' (TIMED OUT)' : ''}`);
  console.log(`- accuracy: ${s.fn.pass}/${s.fn.tests}  ·  composite: ${s.composite.toFixed(2)}  ·  ${(run.ms / 1000).toFixed(1)}s`);
  if (opts.keep) console.log(`- workspace kept: ${ws}`);
  console.log('');
  if (!opts.keep) rmSync(ws, { recursive: true, force: true });
}

const b = rows.find((r) => r.arm === 'baseline');
const p = rows.find((r) => r.arm === 'bulletproof');
if (b && p) {
  const dA = ((p.dims.accuracy || 0) - (b.dims.accuracy || 0)) * 100;
  console.log(`Δ bulletproof − baseline:  accuracy ${dA >= 0 ? '+' : ''}${dA.toFixed(0)} pts  ·  composite ${(p.composite - b.composite >= 0 ? '+' : '')}${(p.composite - b.composite).toFixed(2)}`);
}
if (skillBundle) rmSync(skillBundle, { recursive: true, force: true });

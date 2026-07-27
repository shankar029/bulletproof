// pi adapter for the agent-in-the-loop harness (EVAL-PLAN v2).
// Invokes pi headless to *produce* an arm; scoring is done by the existing evals/lib/score.mjs.
import { spawnSync } from 'node:child_process';

/**
 * Build the pi CLI flags for an arm. The ONLY difference between arms is the skill:
 * both run non-interactive, session-less, and isolated from ambient context/extensions/
 * prompt-templates/skills — so the experiment attributes any delta to `/bulletproof` alone.
 *
 *   baseline    -> host agent, no skill
 *   bulletproof -> host agent + the bulletproof skill (explicitly loaded)
 */
export function buildPiArgs({ arm, skillPath }) {
  // -p non-interactive · --no-session ephemeral · -nc no AGENTS.md/CLAUDE.md · -ne no extensions
  // · -np no prompt-templates · -ns no skill discovery (bulletproof re-adds ONLY our skill).
  const args = ['-p', '--no-session', '-nc', '-ne', '-np', '-ns'];
  if (arm === 'bulletproof') {
    if (!skillPath) throw new Error('bulletproof arm requires skillPath');
    args.push('--skill', skillPath);
  } else if (arm !== 'baseline') {
    throw new Error(`unknown arm: ${arm}`);
  }
  return args;
}

/** Spawn pi headless with the given args + prompt, in cwd, under a wall-clock budget.
 *  The prompt is piped via stdin (pi reads it in -p mode) so no shell-quoting of the prompt is
 *  needed; shell:true lets Windows resolve the `pi` shim. Only args that need it are quoted. */
export function invokePi({ args, prompt, cwd, timeoutMs = 300_000 }) {
  const started = Date.now();
  const q = (a) => (/[\s"]/.test(a) ? `"${a.replace(/"/g, '\\"')}"` : a);
  const cmd = ['pi', ...args].map(q).join(' ');
  const r = spawnSync(cmd, {
    cwd, encoding: 'utf8', timeout: timeoutMs, maxBuffer: 64 * 1024 * 1024,
    input: prompt, shell: true,
  });
  const timedOut = r.error?.code === 'ETIMEDOUT' || r.signal === 'SIGTERM';
  return {
    status: r.status,
    timedOut,
    ms: Date.now() - started,
    stdout: r.stdout || '',
    stderr: r.stderr || '',
    error: r.error ? String(r.error.message || r.error) : null,
  };
}

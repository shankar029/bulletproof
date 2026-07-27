// Workspace prep + prompt construction for the agent-in-the-loop harness (EVAL-PLAN v2).
// Builds an isolated throwaway workspace laid out so the EXISTING oracle + quality probes
// score the produced arm unchanged:
//
//   <ws>/
//     SPEC.md          <- the requirement (agent reads this)
//     shared/...       <- seeded utilities the arm should reuse (../shared/* from arm)
//     arm/index.ts     <- the agent's deliverable (armDir = <ws>/arm)
//
// The held-out oracle is NEVER copied into the workspace.
import { mkdtempSync, mkdirSync, cpSync, writeFileSync, readFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

/** Create the isolated workspace and seed it. Returns { ws, armDir }. */
export function prepWorkspace({ projectAbs, agent }) {
  const ws = mkdtempSync(path.join(os.tmpdir(), 'bp-eval-'));
  const armDir = path.join(ws, path.dirname(agent.armFile) === '.' ? 'arm' : path.dirname(agent.armFile));
  mkdirSync(armDir, { recursive: true });
  for (const rel of agent.seed || []) {
    cpSync(path.join(projectAbs, rel), path.join(ws, rel), { recursive: true });
  }
  // Copy the requirement to a stable name at the workspace root.
  writeFileSync(path.join(ws, 'SPEC.md'), readFileSync(path.join(projectAbs, agent.prompt), 'utf8'));
  return { ws, armDir };
}

/** The requirement prompt handed to pi. Only the trailing directive differs per arm. */
export function buildPrompt({ arm, armFile }) {
  const core = [
    'You are in an isolated, throwaway workspace (no CI, no remote).',
    'The requirement is in `SPEC.md`. Read it fully.',
    `Deliver a TypeScript module at \`${armFile}\` (relative to the workspace root) that satisfies it.`,
    'Reuse the utilities under `shared/` instead of re-implementing them; import them with an',
    "explicit `.ts` extension, e.g. `import { clamp } from '../shared/clamp.ts'`.",
    `Do not edit anything outside \`${path.dirname(armFile) === '.' ? 'the deliverable file' : path.dirname(armFile) + '/'}\`.`,
    'Export exactly the surface `SPEC.md` specifies.',
  ].join(' ');
  const directive = arm === 'bulletproof'
    ? ' Use the bulletproof delivery workflow (your loaded skill) to deliver this at top-1% quality; there is no git remote, so stop at a clean local commit.'
    : ' Implement it.';
  return core + directive;
}

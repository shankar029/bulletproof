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
  // The requirement shown to the agent: an inline terse ask (preferred, so trap guardrails aren't
  // leaked) or the project's SPEC file. Written to a stable name at the workspace root.
  const requirement = agent.requirement != null
    ? agent.requirement
    : readFileSync(path.join(projectAbs, agent.prompt), 'utf8');
  writeFileSync(path.join(ws, 'SPEC.md'), requirement);
  return { ws, armDir };
}

/** The requirement prompt handed to pi. Deliberately NEUTRAL: it must not hint at reuse, tool
 *  choice, dependencies, or rigor — those disciplines must come from the skill alone, so the only
 *  variable between arms is `/bulletproof`. Only the trailing directive differs per arm. */
export function buildPrompt({ arm, armFile }) {
  const outside = path.dirname(armFile) === '.' ? 'the deliverable file' : `\`${path.dirname(armFile)}/\``;
  const core = [
    'You are in an isolated, throwaway workspace (no CI, no remote).',
    'The requirement is in `SPEC.md`. Read it fully, then deliver a TypeScript module at',
    `\`${armFile}\` (relative to the workspace root) that satisfies it.`,
    'Import any local files with an explicit `.ts` extension (e.g. `../shared/x.ts`).',
    `Do not edit anything outside ${outside}. Export exactly the surface \`SPEC.md\` specifies.`,
  ].join(' ');
  const directive = arm === 'bulletproof'
    ? ' Use the bulletproof delivery workflow (your loaded skill) to deliver this at top-1% quality; there is no git remote, so stop at a clean local commit.'
    : ' Implement it.';
  return core + directive;
}

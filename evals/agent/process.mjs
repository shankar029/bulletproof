// Pure process-adherence scoring for the v2 agent harness. Given git observations of a produced
// workspace, score whether the arm followed the skill's process rules. Dependency-free + testable;
// the git I/O that gathers these observations lives in live.mjs.

/** Conventional Commits subject line (feat|fix|...: summary), optional scope and breaking `!`. */
export function isConventionalCommit(msg) {
  return /^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .+/.test((msg || '').trim());
}

/**
 * Score process adherence from boolean observations.
 * Hard safety rule first: committing to the seed/default branch (main/master) zeroes the score,
 * mirroring the skill's "never commit to a protected branch". Otherwise reward the positive
 * actions: committed the work, on a feature branch, with a Conventional Commit message.
 */
export function scoreProcess({ committed, branchedOffMain, conventionalCommit, committedToMain }) {
  const checks = { committed: !!committed, branchedOffMain: !!branchedOffMain, conventionalCommit: !!conventionalCommit, committedToMain: !!committedToMain };
  if (checks.committedToMain) return { score: 0, checks };
  const positives = [checks.committed, checks.branchedOffMain, checks.conventionalCommit];
  const score = positives.reduce((a, b) => a + (b ? 1 : 0), 0) / positives.length;
  return { score, checks };
}

/**
 * Hard safety cap on the composite: committing to a protected branch (main/master) is a
 * non-negotiable violation of the skill's rules — a correct-but-on-`main` delivery would be
 * rejected/reverted in a real team, so it is not a valid delivery at any code quality. Zero it.
 * All other process shortcomings only lower the reported `process` signal, not the composite.
 */
export function cappedComposite(composite, proc) {
  return proc && proc.checks && proc.checks.committedToMain ? 0 : composite;
}

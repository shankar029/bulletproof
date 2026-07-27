# Reference: Parallel Execution

Independent work should run concurrently — but only when the agent supports parallel
subagents **and** the work is genuinely independent. Done wrong, parallelism causes merge
conflicts and hidden breakage. Done right, it ships faster with the same quality bar.

## Step 1 — Can this agent run parallel subagents?

Detect capability before planning any fan-out. If unsupported, **fall back to sequential**
(the default loop) — never fake it.

| Agent | Mechanism | Isolation |
|---|---|---|
| **pi** | `subagent` tool, parallel mode: `{ tasks: [{agent, task}], concurrency, worktree: true }`; agents like `worker`, `scout`, `reviewer` | `worktree: true` gives each task its own git worktree |
| **Claude Code** | multiple `Task` subagent calls in one turn run concurrently; subagents in `.claude/agents/` | instruct workers to use separate paths / `git worktree` |
| **Copilot CLI** | no reliable subagent parallelism | — → run sequentially |

## Step 2 — Find the parallelizable work (during Phase 2 planning)

Build a **dependency graph** of the plan's tasks, then mark what can run in parallel:

- A task is a **parallel candidate** only if it is **file-disjoint** from its siblings (no two
  concurrent tasks edit the same file) and has **no ordering dependency** on them (doesn't need
  another task's output, shared type, migration, or interface first).
- **Serialize** anything that touches shared foundations: schema/migrations, shared types or
  interfaces, config, DI wiring, public contracts. Do these **first, in the main context**, then
  fan out the leaves that build on them.
- Good parallel splits: independent endpoints/modules, per-service changes in a monorepo,
  UI vs API halves of a feature, docs, and independent test suites.
- Bad parallel splits: two tasks editing the same file, a caller + the callee it depends on,
  anything sharing a not-yet-created interface.

Record the split in `PLAN.md` (which tasks are parallel, which are serialized, and why).

## Step 3 — Dispatch (during Phase 3)

- Do the **shared/foundational work first**, sequentially, so every worker starts from a stable base.
- Give each worker an **isolated workspace**: prefer a **git worktree per task** (`worktree: true`
  in pi; `git worktree add` for others). Never let concurrent workers share a working tree.
- Each worker gets a **sharply-scoped brief**: the project profile, its slice's acceptance
  criteria, the files it owns, and the same quality bar — **it must write real unit + integration
  tests for its slice and leave it green.** Workers do not touch files outside their slice.
- Keep concurrency modest (≈2–4) to stay debuggable.

## Step 4 — Integrate & verify the whole (never trust isolated green)

Parallel workers proving their own slices is **not** proof the system works. After fan-out:

1. Merge the worktrees/branches back; resolve any conflicts in the main context.
2. Run the **full** test suite + coverage on the integrated result (Phase 3 GATE 3).
3. Run **end-to-end verification on the whole feature** (Phase 4) — the human-style proof always
   happens on the integrated system, not per worker.
4. Do the single unified review and ship one PR (Phase 5). The PR evidence notes which parts ran
   in parallel.

## When NOT to parallelize
- The agent doesn't support it → sequential.
- Tasks aren't truly file-disjoint / independent → sequential (correctness beats speed).
- The whole change is small enough that coordination overhead outweighs the win.

## Optional: parallel review & E2E
Independent, read-only angles are safe to parallelize even for small changes — e.g. review the
diff for correctness, security, and test quality concurrently, or run independent E2E surfaces
(UI flow vs API contract) in parallel. Merge findings before shipping.

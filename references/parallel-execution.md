# Reference: Parallel Execution

Split work across subagents only when this agent supports them **and** the work is genuinely
independent. Otherwise run sequentially — correctness beats speed, and a small change isn't
worth the coordination overhead.

## Read-only research (Phase 1)
The Decide/Dispatch rules below govern implementation workers. Phase 1 research is mandatory-delegated per
`delegation.md`, using the reusable procedure and handoff contract in `research.md`.
The parent may split substantial independent research questions, but never a single continuous
call trace into artificial roles. Researchers do not recursively delegate or edit source.
Read-only scopes may overlap and do not require worktrees; use a stable source snapshot and
distinct output destinations. The parent reconciles all required findings, checks coverage and
citations, and persists the combined `.ai/<slug>/research.md` before accepting Gate 1.

## Decide (Phase 3)
A task is a parallel candidate only if it is **file-disjoint** from its siblings (no two
concurrent tasks edit the same file) and has **no ordering dependency** on them (doesn't need
another task's output, type, interface, or migration first). The Phase 2 design document is
what makes this decidable — split along the boundaries it defines.

Serialize anything touching shared foundations — schema, shared types and interfaces, config,
wiring, public contracts. Do those first in the main context, then fan out the leaves that
build on them. Record the split in the plan.

## Dispatch (Phase 4)
- Give each worker an isolated workspace (a separate worktree or checkout). Concurrent
  workers never share a working tree.
- Give each a sharply-scoped brief: the project profile, **the design document**, its slice's
  acceptance criteria, and the plan's **assigned task/check records** per `planning.md`
  (entry conditions, exact owned changes, preserved behavior, proof and stop conditions).
  Keep the same quality bar — real unit and integration tests, left green.
  Workers implement the design; they do not redesign. A shared component can recur in sequential
  increments, but shared-file changes are never concurrently owned.
- Keep concurrency modest (about 2–4) so failures stay debuggable.
- **Budget and watch each worker independently** per `delegation.md` § Subagent liveness: its
  own `state.md` row, its own soft budget (30 min default for an implementation slice), its own
  checkpoints. One stuck worker never postpones the others' checks, and never blocks the
  integration of slices that finished — steer it, then kill-and-relaunch-once on its own
  narrowed slice, then raise it as a blocker while the green slices proceed.

## Integrate
Isolated green is not proof. Merge the work back, resolve conflicts in the main context, then
run Gates 4, 5, and 6 on the **integrated** result and ship one PR. Note in the PR which
parts ran in parallel.

Read-only work (review angles, independent verification surfaces) is safe to parallelize even
for small changes; merge the findings before shipping. **The Phase 6 review always runs in a
separate, fresh-context, read-only session — preferably on a different model** (see
`review-and-pr.md`). Reviewers never edit implementation; assigned review artifacts may be
written with scoped permission, otherwise the parent persists their returned findings unchanged.
The parent applies fixes.

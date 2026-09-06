# Reference: Parallel Execution

Split work across subagents only when this agent supports them **and** the work is genuinely
independent. Otherwise run sequentially — correctness beats speed, and a small change isn't
worth the coordination overhead.

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
  acceptance criteria, the files it owns, and the same quality bar — real unit and integration
  tests, left green. Workers implement the design; they do not redesign.
- Keep concurrency modest (about 2–4) so failures stay debuggable.

## Integrate
Isolated green is not proof. Merge the work back, resolve conflicts in the main context, then
run Gates 4, 5, and 6 on the **integrated** result and ship one PR. Note in the PR which
parts ran in parallel.

Read-only work (review angles, independent verification surfaces) is safe to parallelize even
for small changes; merge the findings before shipping. **The Phase 6 review always runs in a
separate, fresh-context, read-only session — preferably on a different model** (see
`review-and-pr.md`). Reviewers never write to the tree — you apply the fixes.

# Reference: Workspace, State & Resumability

Every non-trivial piece of work gets a **slug** and a directory under `.ai/` at the repository
root. All artifacts for that work live there, so the work survives a restart, a crash, a new
session, or a handoff.

## Slug & layout

The slug is short kebab-case derived from the requirement (`checkout-discount-codes`,
`fix-token-refresh-race`). If it already exists for different work, suffix `-2`.

```
.ai/
  assets/              # shared theme, copied once per repo: artifact.css, artifact.js
  <slug>/
    state.md            # resume index; guarded readiness is derived, not owned here
    research.md         # ground truth: what exists today, cited path:line; what does not
    traceability.md     # living matrix: AC -> design -> task -> test -> evidence -> verdict
    clarifications.md   # questions asked, answers received, assumptions taken
    architecture.html   # ONLY for large work (new service/subsystem, cross-cutting)
    design.html         # program design: classes, interfaces, interactions (Phase 2)
    design-review.md    # independent design-review findings + verdict (Gate 2b)
    plan.html           # increments, tasks, test strategy (Phase 3)
    tasks.md            # optional detailed task/check records linked from plan.html
    review.json         # reader's comments + verdict, exported from the document
    review.md           # independent-reviewer findings and their dispositions
    metrics.json        # deterministic quality probe: HEAD vs merge-base
    report.html         # the final report: outcome, gates, measurements, what's pending
    evidence/           # screenshots, console output, transcripts, traces, command logs
```

**Do not create files this work doesn't need.** Trivial-tier work writes `state.md` only.
Contained work skips `architecture.html`. There is never a second copy of the same content in
two documents — `state.md` links, it does not restate.

### Adopted authority versus design history

Initial research/design/plan use the procedural artifacts above. Once a reviewed contract
is ready for guarded operation, follow [workflow-gates.md](workflow-gates.md) to stage
immutable candidates and invoke ordinary `adopt`. No bootstrap generator or historical
execution import is provided. In an adopted workspace:

| Record | Authority |
|---|---|
| `current-design.json` | Current revision, retained document/contract hashes, review and history |
| `design-history/<revision>.html`, `contracts/<revision>.json` | Immutable design and normative component definitions |
| `workflow.json` | Registered commands, owners, forward dependencies and check contracts |
| `evidence/ledger.json`, `evidence/receipts/` | Runtime events and immutable evidence; readiness is derived from these and current inputs |

`design.html` remains an initial/proposal overview, not an alternative live pointer.
Resolve the retained paths in `current-design.json` on every adopted resume and brief.
Do not edit retained revisions, copy candidates directly over live files, or repair history
into a pass. Adoption publishes event → workflow → pointer; the operator guide owns the
finite metadata retry rules. These retries after ordinary unwind are not process recovery.

Commit `.ai/<slug>/` with the change: the design record belongs with the code that implements
it, and the PR links to it. Keep `evidence/` out of version control if the artifacts are large
(videos, traces) and reference the paths instead.

**Keep agent scratch out of the repo.** Subagents and tooling may write working files into the
project directory (for example `.pi-subagents/`). Add them to `.gitignore` before committing —
they are not part of the change, and they corrupt duplication and diff-size metrics if they
land in git.

## `state.md` — the resume contract

Short enough to read in one screen. Rewrite the header block on every gate; append to the log.

```markdown
# <slug>
Requirement: <one line, or path/link to the source>
Tier: trivial | standard
Branch: feat/<slug>
Design: design.html · Plan: plan.html · Architecture: n/a
Traceability: traceability.md

Current phase: 4 — Implement (increment I2 of 4)
Gates: G1 ✅ | G2 ✅ (signed off) | G3 ✅ | G4 ⬜ | G5 ⬜ | G6 ⬜
Next action: <one concrete sentence — the exact next thing to do>
Blocked on: none | <what, and who/what unblocks it>

## Acceptance criteria
- [x] AC1 <one line> — covered by I1
- [ ] AC2 <one line> — covered by I2

## Increments
- [x] I1 <name> — merged, green, reviewed (commit <sha>)
- [ ] I2 <name> ← current
- [ ] I3 <name>

## Assumptions
- <assumption> (unconfirmed — see clarifications.md)

## Subagents
| handle | phase | model | launched | budget | checks | status |
|---|---|---|---|---|---|---|
| research | 1 | sonnet | 13:40 | 12m | 1 | done (research.md) |
| verify | 5 | sonnet | 14:02 | 25m | 2 | steered 14:29 — running |

## Log
- <date> G2 passed, design signed off by user
- <date> I1 complete: 12 unit / 3 integration green, reviewed, committed
```

The `## Subagents` table is the watch list for `delegation.md` § Subagent liveness: one row per
spawn, updated at every checkpoint and closed to `done` / `killed` / `blocked`. A row left
`running` when the turn ends must be called out in the chat summary.

## Protocol

**On every invocation, before anything else:** look for `.ai/<slug>/state.md` matching this
requirement.
- **Found** → read `state.md`, then resolve the current design as above and read the plan, then **resume at the
  recorded phase and increment**. Do not restart, do not redesign, and do not re-derive intent
  from the diff. If the recorded state and the working tree disagree, reconcile explicitly and
  say so before continuing.
- **Not found** → create the directory and `state.md` at the end of Phase 1.

**Write state at boundaries, not continuously:** on each gate pass, on each increment
completion, when an assumption or question is recorded, **when you hand a document to the user
and stop for sign-off**, on every subagent launch, liveness checkpoint, steer, kill or relaunch,
and whenever you are interrupted. Updating state is cheap; losing a
day of design is not.

**Waiting for a human is a stop, not a loop.** When a document is out for review, record
`Blocked on: <doc> sign-off` with the next action and **end the turn** — never poll, sleep, or
re-check for a file in a loop. The answer can arrive in a later session; the workspace is what
makes that safe. **Write `report.html` before you stop**, so the person reading knows exactly
where the work stands.

**Before starting any increment**, re-read the resolved current design (or its relevant section). This is the
main defense against drift on a long task: the design, not your recollection, is the contract.
Also read the plan and current task/check records (`tasks.md` only if present), confirm their
prerequisites and source snapshot, and reconcile completion evidence with the tree. Use
`planning.md` for revision and resume; do not treat a completed checkbox as proof.
For adopted work, run actual `status` for the intended action/increment/ship target before
dispatch and after relevant source, contract or evidence changes. Copy its blockers and
reopened checks into summaries with the observation's source context; preserve unaffected
receipt bytes. Missing or inconsistent live authority is a blocker, not a fallback to old
`design.html`. There is no recovery/reset/orphan-lock-steal operation; preserve uncertain
process evidence and follow [the interruption limits](workflow-gates.md#interruption-and-trust-limits).

## `traceability.md` — the requirement matrix that ties the gates together

One table, seeded in Phase 1 from the acceptance criteria and filled in as the work moves
through the gates. It is the single place that answers "did we actually deliver every part of
the ask?", and it is what the independent reviewer reconciles against in Phase 6. One row per
acceptance criterion:

```markdown
# Traceability — <slug>

| AC  | Requirement            | Design (component/method) | Task | Test / check          | Evidence                 | Verdict |
|-----|------------------------|---------------------------|------|-----------------------|--------------------------|---------|
| AC1 | Apply promo at checkout| PricingService.applyPromo | I1.T1, I1.T2 | C1: pricing.test.ts:42 | evidence/e2e-promo.txt | VERIFIED |
| AC2 | Reject expired codes   | PromoValidator.check      | I2.T1, I2.T2 | C2: promo.test.ts:88   | —                     | NOT-VERIFIED |
```

- **Phase 1** seeds the `AC` and `Requirement` columns — every explicit ask and sub-deliverable.
- **Phases 2–3** fill `Design` and `Task` as each AC maps to the specific task IDs within its
  increment(s); link the planned check IDs. An AC can require several tasks/checks, not just one.
- **Phases 4–5** fill `Test` and `Evidence` as behaviour is built and proven.
- **Phase 6** sets `Verdict` per AC — **VERIFIED / VERIFIED-WITH-LIMITATIONS / NOT-VERIFIED /
  BLOCKED** — determined by the independent reviewer from the tree and evidence, not from the
  implementer's narrative. The reviewer writes assigned artifacts if permitted; otherwise the
  parent persists its full returned findings/verdicts unchanged per `review-and-pr.md`.
  At an intermediate gate, reconcile the current increment's due scenarios and affected prior
  regressions. Future ACs remain `NOT-VERIFIED` with an explicit "planned: I<n>" note; spanning
  ACs retain partial task/check evidence but cannot be VERIFIED until fully satisfied. Only
  unmet **due** work reopens an earlier phase. Final ship requires every row VERIFIED (or
  VERIFIED-WITH-LIMITATIONS with the limitation named); future work is not silently deferred.

Keep it in sync with `state.md`'s acceptance-criteria checklist — the checklist is the quick
read, the matrix is the proof. Trivial-tier work skips it.

**Never leave state stale.** A `state.md` that says "Phase 4" while the branch is already
reviewed and pushed is worse than no state at all.

## Sizing increments (Phase 3)

Split the work so **each increment fits comfortably in one session's context window**, end to
end, with room to spare for tests and review.

An increment is right-sized when:
- It is a **vertical slice** that delivers observable behavior — not a horizontal layer
  ("all the models", "all the tests") that can't be verified on its own.
- Implementing it requires reading and holding **well under half the context window**;
  as a rough gauge, a handful of files touched and a diff you could review in one sitting.
- It maps to at least one acceptance criterion, and can be tested and reviewed alone.
- It ends at a **production-quality, green, reviewed commit** on the feature branch — never a
  half-finished state that the next session has to reconstruct.

If an increment turns out too big mid-flight, stop at the last green commit, split the
remainder using `planning.md`'s revision protocol, update the plan/task records, `state.md` and
`traceability.md`, and recheck Gate 3 before continuing. Preserve stable IDs and completion
evidence for unaffected work; reopen results invalidated by the split or changed contract.

Internal tasks can build contracts, logic and wiring in order without being separate increments.
The same component may be extended by multiple increments when their owned changes and
dependencies are explicit; every increment still delivers a complete, verifiable slice.

**Every increment runs the full quality loop** — implement + test (Phase 4), verify (Phase 5),
review (Phase 6) — at production quality. The PR opens when the whole requirement is complete,
unless the repo prefers a PR per increment.

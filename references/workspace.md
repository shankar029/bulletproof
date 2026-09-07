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
    state.md            # source of truth for resume — always present, always current
    clarifications.md   # questions asked, answers received, assumptions taken
    architecture.html   # ONLY for large work (new service/subsystem, cross-cutting)
    design.html         # program design: classes, interfaces, interactions (Phase 2)
    plan.html           # increments, tasks, test strategy (Phase 3)
    review.json         # reader's comments + verdict, exported from the document
    review.md           # independent-reviewer findings and their dispositions
    metrics.json        # deterministic quality probe: HEAD vs merge-base
    report.html         # the final report: outcome, gates, measurements, what's pending
    evidence/           # screenshots, console output, transcripts, traces, command logs
```

**Do not create files this work doesn't need.** Trivial-tier work writes `state.md` only.
Contained work skips `architecture.html`. There is never a second copy of the same content in
two documents — `state.md` links, it does not restate.

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

## Log
- <date> G2 passed, design signed off by user
- <date> I1 complete: 12 unit / 3 integration green, reviewed, committed
```

## Protocol

**On every invocation, before anything else:** look for `.ai/<slug>/state.md` matching this
requirement.
- **Found** → read `state.md`, then the design and plan it points to, then **resume at the
  recorded phase and increment**. Do not restart, do not redesign, and do not re-derive intent
  from the diff. If the recorded state and the working tree disagree, reconcile explicitly and
  say so before continuing.
- **Not found** → create the directory and `state.md` at the end of Phase 1.

**Write state at boundaries, not continuously:** on each gate pass, on each increment
completion, when an assumption or question is recorded, **when you hand a document to the user
and stop for sign-off**, and whenever you are interrupted. Updating state is cheap; losing a
day of design is not.

**Waiting for a human is a stop, not a loop.** When a document is out for review, record
`Blocked on: <doc> sign-off` with the next action and **end the turn** — never poll, sleep, or
re-check for a file in a loop. The answer can arrive in a later session; the workspace is what
makes that safe. **Write `report.html` before you stop**, so the person reading knows exactly
where the work stands.

**Before starting any increment**, re-read `design.html` (or its relevant section). This is the
main defense against drift on a long task: the design, not your recollection, is the contract.

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
remainder in `plan.html`, update `state.md`, and continue.

**Every increment runs the full quality loop** — implement + test (Phase 4), verify (Phase 5),
review (Phase 6) — at production quality. The PR opens when the whole requirement is complete,
unless the repo prefers a PR per increment.

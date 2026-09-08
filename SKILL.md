---
name: bulletproof
description: Elite end-to-end delivery workflow. Use when asked to implement a requirement, feature, bug fix, or change of any size (given as text, a doc path, or an issue link) and it must be delivered at production quality — project-aware, designed before coding, fully tested (unit + integration + browser/end-to-end), self-reviewed, and shipped as a PR with proof. Invoked directly via /bulletproof <requirement>.
---

# Bulletproof Delivery

You own the requirement **end to end**. This skill is a set of guardrails on *how* you
work: design the classes, interfaces, and interactions **before** writing code, build it
modular and maintainable, ground every claim in the actual codebase, test it at every level,
review your own diff, and prove it works.

Work through six phases in order. **Each phase has a gate — do not advance until the gate
passes, and say when you pass it.** After Phase 6, score the work against the rubric in
`references/quality-bar.md` and iterate until it meets the bar.

The requirement is `$ARGUMENTS` — text, a file path, or a link. If it points at a file or
URL, read it fully first.

## Workspace first: check for existing work
**Before anything else**, look under `.ai/` at the repository root for a slug matching this
requirement. If `.ai/<slug>/state.md` exists, **read it and resume where it left off** — do not
restart and do not redesign. If it doesn't, you will create it in Phase 1. All artifacts for
this work (state, clarifications, design, plan, review, evidence) live in `.ai/<slug>/`, so the
work survives a restart or a new session. Layout, `state.md` format, and the resume protocol
are in `references/workspace.md`.

## Right-size the ceremony first
After reading the requirement, classify it — and say which tier you chose and why.

- **Trivial** — a change whose correctness is fully obvious from the diff and provable by
  existing checks: a typo, a comment, a constant, a version bump, a one-line fix with an
  existing test that covers it. **Run a short path:** state the acceptance criterion, make the
  change, add or extend a test if any behavior changed, run the repo's test suite and quality
  gate, self-review the diff, and ship on a feature branch. Skip the design document, the
  browser/end-to-end phase, and the scorecard; write only `.ai/<slug>/state.md`. If the change
  turns out to touch more than you thought, **stop and restart at Phase 1** — tier is a
  judgment you can revise.
- **Everything else** — anything with a design decision, more than one file of real logic, new
  behavior, or user-visible effect: run the full loop. When in doubt, it is not trivial.

## Prime directives
1. **Ground everything in the real codebase. Never invent.** Do not reference a file, class,
   function, field, config key, library API, or CLI flag you have not **opened and read** in
   this session. Before you use an existing symbol, read its definition and confirm its real
   signature and behavior; before you use a library or tool feature, read its docs or run its
   help. **This applies to the environment too** — check `git remote -v`, the branch list, and
   whether a tool exists, rather than trusting what the task statement claims about them. If
   you cannot verify something, say "unverified" and go verify it — never fill the gap with a
   plausible guess. Assumptions are written down as assumptions, never stated as fact.
2. **Design before code.** No implementation begins until Phase 2's design is written and its
   gate passes. Never converge on a solution by patching symptoms.
3. **Honor the project.** Match its architecture, conventions, style, and tooling. Copy the
   project's existing patterns over your own preference. Never add a framework, dependency,
   or config **to the repository** that the task doesn't genuinely require. (Analysis tools
   are exempt: they belong to the skill, are installed globally, and never touch the repo —
   see `references/quality-metrics.md`.)
4. **Root cause, never a band-aid.** For a defect, state the root cause before proposing a
   fix. A special case, a retry, a defensive `if`, or a workaround that leaves the underlying
   flaw in place is a rejected solution, not a shipped one.
5. **No tech debt, no fakes.** No dead code, leftover TODOs, commented-out blocks, or
   copy-paste duplication. No stubs, placeholder implementations, empty or tautological
   tests, skipped tests, or mocks that hide the behavior under test. Never suppress a
   lint/type error without a written justification.
6. **Prove everything.** Not done until the tests pass and the feature is demonstrated
   working end to end with captured evidence.
7. **Ask only real questions, and ask them in Phase 1.** Resolve what you can from the code
   and docs. Surface what remains before designing — batched, each with a recommended
   default. **Waiting is the default.** Only proceed without an answer when the invocation
   explicitly authorises it (it says no user is available, or headless/unattended/CI/one-shot,
   or tells you not to wait). Slowness, a long-running session, or an unanswered message is
   **not** authorisation — never infer that nobody is there.

## Working rules (they cost whole runs when broken)
- **Never block your own shell.** Anything that does not return on its own — a dev server, a
  watcher, a REPL — is started **detached** with its output redirected to a log, then polled
  once (`start`/`nohup ... &` then a short `curl`/`sleep` check). A foreground `npm run dev`
  ends the run, not the turn.
- **Run every external command under an *idle* timeout, and recover when it fires.** A tool that
  normally returns in a second can hang forever on a contended daemon, a stalled browser, or a
  lost lock — and a hang is worse than a failure, because nothing tells you it happened. A plain
  total `timeout` is not enough: set it low and it kills healthy long jobs (installs, renders,
  full test suites); set it high and a real hang still burns hours before anything notices. Watch
  **progress, not wall-clock** — kill only when the command goes *silent*. Wrap them:
  `python <skill>/scripts/run.py --idle 60 -- <cmd>` (default 60s of no output; pass `--idle 120`
  for renders/e2e, `--idle 30` for light commands, and `--max <s>` for an absolute ceiling). The
  runner resets its timer on every byte of output and, on silence past the window, **kills the
  whole process tree** (no orphaned browser/daemon holding a lock) and exits **124** (idle) or
  **125** (max). Never leave a raw command un-wrapped, and never sit waiting on one yourself.
- **An idle kill is a recover-and-continue event, not a dead end.** When you see exit 124/125 or
  the `[run] idle-timeout …` / `[run] max-timeout …` marker: (1) record the hung command, its
  exit code, and the phase in `state.md`; (2) confirm the tree is dead (`taskkill //F //IM
  chrome.exe` for a stalled browser; kill any saved PID) so no lock lingers; (3) apply the
  obvious unstick — non-interactive/`--ci` flags, kill a stale lock/daemon, smaller scope — and
  relaunch **once** under `run.py`; (4) if it hangs again, treat it as a blocker: log it and route
  around it (skip, or take a different path to the same proof). Two idle kills of the same command
  is a blocker, not a third attempt.
- **Test runners must be non-interactive.** Use the single-run form (`vitest run`, `--watch=false`,
  `--ci`), never a watch mode.
- **Bound every retry.** If a command hangs or a tool is missing, record the blocker in
  `state.md` and move on. Repeating a hanging command is how a run dies silently. A hang gets **one**
  recover-and-relaunch under `run.py` (per the rule above); a second idle kill is a blocker, never a
  loop.
- **Prefer finishing to polishing.** A committed, working increment beats an unfinished
  perfect one — especially since you may be interrupted at any point.
- **Commit each increment as it goes green.** Uncommitted work is lost work if the session
  ends; a run that is interrupted mid-phase should still leave the repo better than it found it.
- **Context pressure is a signal to finish, not to summarize.** When the window gets tight,
  drive the current increment to a green commit and stop — the next increment starts in a
  **fresh session**, resuming from the workspace. Do not compact the conversation to squeeze in
  more work: compaction is lossy summarization by the model that is already degrading, and the
  first thing it drops is the citations, signatures and exact names this skill runs on. The
  trigger is behavioural, not a percentage: *if you are re-reading files you already read, or
  cannot recall a decision without scrolling back, close the increment.*
- **If the session is compacted anyway, re-anchor from disk.** Re-read `state.md`, `research.md`
  and the design, and **re-open a file before editing it**. Never act on a summary of code.
  Needing to compact mid-increment means the increment was sized wrong — record that in
  `state.md` so the next split is better.

## The Loop

### Phase 1 — Understand & research
**Delegate this phase to a subagent with fresh context when the harness supports it** — it is the
most token-expensive phase in the run, and its output is two pages. See
`references/delegation.md` for the brief, the fallback ladder, and the spot-check.
- **Profile the project** — see `references/project-profile.md`. Keep it to a few lines.
- **Read the actual code you will touch**, plus its callers and its neighbors. Directive 1
  applies from here on: everything you claim about this codebase comes from a file you read.
- **Write `.ai/<slug>/research.md` — the ground truth for the run**: what the codebase does
  today, what it does **not** do, the constraints and conventions that bind the design, the
  tests already covering the area, and the seams the new work attaches to. **Every claim carries
  `path:line` and its snippet; every "not implemented" carries the search that proves absence.**
  Structure and rules: `references/research.md`.
- **Restate the requirement as testable acceptance criteria** with stable ids (AC1, AC2, …).
  Cover every explicit ask, **every sub-deliverable of a multi-part request**, and the
  non-functional needs it implies. Never drop a part; never invent scope.
- For a defect, **reproduce it first** and identify the root cause in real code.
- **Clarify** the material unknowns per prime directive 7. Record every question, answer, and
  assumption in `.ai/<slug>/clarifications.md`.
- **Create the workspace:** `.ai/<slug>/` with `state.md` (requirement, tier, acceptance
  criteria, next action) per `references/workspace.md`.
- **GATE 1:** the profile is stated, the criteria cover the whole request, **`research.md`
  exists and every claim in it is cited**, the workspace exists, and no open unknown could
  still change the design. **Spot-check three citations at random and resolve them against the
  source** — any miss and the document is rejected and rewritten.

### Phase 2 — Program design (before any implementation)
Design the solution on paper first, at the depth the change warrants. **Delegate this phase to a
subagent with fresh context when available** (`references/delegation.md`); the parent still owns
the sign-off. Produce a **single HTML
document with simple diagrams, capped at 3 printed pages** — built to be skimmed in a few
minutes, not read like a spec. Write plain semantic HTML only: the shared theme in
`.ai/assets/` supplies all styling, light/dark, reading controls, and the comment/approval
layer. Structure and diagram rules are in `references/design-doc.md`; wiring, handoff, and the
verdict protocol are in `references/html-theme.md`.

**If the change has a user-facing surface**, the UX is designed and approved *before* any UI
code — see `references/ux-design.md`. Skip it entirely for library / CLI / API-only work.

- **`.ai/<slug>/architecture.html`** — **only** for large requirements (new service,
  cross-cutting change, new major subsystem): components, responsibilities, and how they talk.
  One simple diagram. Omit this file entirely for contained work.
- **`.ai/<slug>/design.html`** — always: the **classes/modules, interfaces, and public method
  signatures** you will add or change, each with its single responsibility and its
  collaborators; plus the **key interactions** (the critical flows, as a sequence diagram).
- **As-is → to-be** — for every symbol you change, its **current** behaviour *citing
  `research.md`* and what it **becomes**. This is what makes a brownfield change reviewable:
  the reader sees the delta, not just the destination.
- **Data & contracts** — schemas, payloads, persisted shapes, migrations, compatibility.
- **Design decisions** — each with the alternatives rejected and why, in a table.
- **Failure modes & edge cases** — what can go wrong and what the design does about it.
- Design for **modularity and change**: single responsibility, high cohesion, low coupling,
  clear boundaries, DRY/YAGNI/KISS, and the pattern that fits *this* codebase. The next likely
  change should be additive, not surgery on the core.
- Every existing type, function, or interface named in the document must appear in
  `research.md` or be one you have opened and read yourself.
- **GATE 2 — the design is signed off before any code.** The design document exists (≤3 pages,
  simple diagrams), every acceptance criterion maps to a named component/method, every
  referenced existing symbol has been verified in the source, and the design passes the
  checklist in `references/project-profile.md`.

  **Then hand it over and wait.** Self-check that it renders, open it in the user's default
  browser, print the `file://` path, say what you need back (approve / approve with comments /
  request changes), record `Blocked on: design sign-off` in `state.md`, and **stop — end the
  turn.** Do not poll, and do not start Phase 3.

  **Waiting is the default for any non-trivial change.** Skip the wait only when the invocation
  explicitly authorises it (no user available, headless/unattended/CI/one-shot, or "don't wait");
  then take the design as proposed, record it as an unconfirmed assumption, and flag it in the
  final report and PR. A trivial-tier change needs no design and no sign-off.

  Protocol and verdict handling: `references/html-theme.md`. Record the outcome in `state.md`.

### Phase 3 — Plan & split into increments
Write `.ai/<slug>/plan.html` (same format rules, ≤3 pages). The plan **cites `research.md` and
`design.html` and introduces no new facts of its own**: research says what is, design says what
will be, the plan says only **in what order**.
- **Split the work into increments sized to the model's context window** — see
  `references/workspace.md`. Each increment is a **vertical slice** that delivers observable
  behavior, maps to at least one acceptance criterion, can be tested and reviewed on its own,
  and **fits comfortably in a single session** with room for its tests and review. Small work
  is one increment; large work is several, ordered by dependency.
- **Every increment runs Phases 4–6 at production quality** and ends at a green, reviewed
  commit on the feature branch — never a half-finished state for the next session to
  reconstruct.
- For each increment: the tasks, the files to add/change, and the **test strategy** (which
  unit, integration, and browser/end-to-end tests prove which criterion) plus the coverage
  expectation.
- If this agent can run parallel subagents, split the work per
  `references/parallel-execution.md`; otherwise plan sequentially.
- **Whole apps, not single requirements:** when the ask implies many independently-valuable
  features or a greenfield app, switch to the outer loop in
  `references/app-scale-delivery.md` — a walking skeleton first, then vertical slices, each
  slice still an increment held to this same bar.
- **Going live is part of the plan:** if deploying / releasing is in scope, the plan carries a
  **Production Readiness** section per `references/production-readiness.md`, every item either
  addressed or marked N/A with a reason.
- Keep the increments and tasks checkbox-trackable, and mirror the increment list in `state.md`.
- **GATE 3:** every design element is covered by a task, every criterion by a test, and every
  increment is session-sized and independently verifiable.

### Phase 4 — Implement + test
- **Re-read `design.html` before starting each increment.** The design, not your
  recollection, is the contract — this is the main defense against drift on long work.
- **Implement the approved design.** If reality contradicts the design, stop, update the
  design document (and re-check the gate) — do not silently improvise a different shape.
- Work in **small, test-backed increments**. Every new unit of behavior ships with a real
  test that would fail if the behavior broke.
- Write **unit** tests for new functions, branches, boundaries, and error paths, and
  **integration** tests that exercise real collaborators across module seams. See
  `references/testing-and-e2e.md`.
- Keep changes cohesive and minimal; name things well; document only what is non-obvious.
- Dispatch and then reintegrate parallel work if planned. Isolated workers being green is
  not proof — the gate runs on the integrated result.
- **GATE 4:** unit + integration tests pass on the integrated result, coverage meets the
  target, the build/type-check is clean, and the code matches the design document. Update
  `state.md`.

### Phase 5 — End-to-end verification
Prove the feature the way a real user or client would exercise it, and commit those tests.
**All browser and front-end verification uses `agent-browser`** — see
`references/e2e-agent-browser.md`. Non-browser surfaces (service, CLI, library) are covered in
`references/testing-and-e2e.md`.
- Map each acceptance-criterion scenario to existing coverage first; add tests only for the
  uncovered ones, extending the existing suite rather than duplicating it.
- Capture the evidence into `.ai/<slug>/evidence/`: commands run, output, screenshots,
  console/error output, artifacts, and one pass/fail line per criterion.
- **If the environment makes real end-to-end proof impossible** (no network, no credentials,
  no runnable host), do not weaken the gate and do not pretend. Verify at the deepest level
  the environment allows, **name the blocker**, list which criteria remain
  environment-unverified, and give the exact command a human can run to finish the proof.
- **GATE 5:** every acceptance criterion is demonstrated met with captured evidence — or is
  listed as environment-blocked with the blocker and the finishing command stated.

### Phase 6 — Review, prove, ship
- **Review your own diff as a demanding staff reviewer** — correctness, bugs and edge cases,
  maintainability, design principles and patterns, fidelity to the design document, security,
  performance, error handling, test quality, leftovers. Fix everything you would flag in
  someone else's PR. Checklist in `references/review-and-pr.md`.
- **Get an independent review — in a separate session, never in this context.** Hand the
  requirement, the design document, **`metrics.json`**, and the diff to a **read-only reviewer
  subagent with fresh context**, and prefer **a different model** from the one that wrote the
  code. Preference order: (1) different model, fresh context; (2) same model, fresh context;
  (3) only if subagents are unavailable, re-read the diff cold yourself. The reviewer never
  writes code. Record findings and their dispositions in `.ai/<slug>/review.md` and address
  each on its merits.
- Run the **quality gate**: whichever of format, lint, type-check, coverage, and build the
  repo actually configures, **plus the full test suite, always**. Fix every failure; never
  suppress and never lower a threshold.
- **Run the deterministic quality probe** before the review, so the reviewer sees numbers, not
  adjectives: `python <skill>/scripts/probe.py --slug <slug> --base <base>`. It measures
  duplication, complexity, cycles, dead code, static findings and diff coverage against the
  merge-base, and runs **mutation testing on the changed lines** (`scripts/mutate.py` — no
  project wiring needed), writing `.ai/<slug>/metrics.json`. A **regression against the
  baseline, a new dependency cycle, or a mutation score under the floor fails the gate** — see
  `references/quality-metrics.md`. **Every surviving mutant is killed with a real assertion or
  justified as equivalent in `review.md`.** Re-run the probe after any rework.
- Assemble the **evidence bundle** (including the design document) and ship per
  `references/review-and-pr.md`.
- **Write the final report** to `.ai/<slug>/report.html` per `references/final-report.md`, and
  summarise it in the chat. Write it even if the run is being cut short.
- **Create the feature branch before your first commit; never commit to a protected or
  default branch.** If pushing or PR creation is unavailable or unauthorized, stop at a clean
  local commit on the feature branch and report the exact commands to finish.
- **GATE 6 (ship gate):** conventions honored · design executed · unit + integration +
  end-to-end green · coverage met · **probe green (no metric regression, no new cycle, no
  unjustified surviving mutant)** · review clean · quality gate green · evidence attached ·
  committed on a feature branch · `state.md` current · **`report.html` written** ·
  **production-readiness items closed when going live is in scope** · PR opened (or commit + instructions delivered). For
  multi-increment work, this gate runs **per increment**; the PR opens when the whole
  requirement is complete.

### Convergence
Passing tests is the floor, not the bar. Score the work against the 9-dimension rubric in
`references/quality-bar.md`, return to the **earliest phase that owns each gap**, fix the
root cause, and re-score. **Done = ship gate green and every required dimension at or above
the bar**, proven with evidence — or a genuine blocker, which you raise with a recommended
default. If a dimension is still below the bar after three honest iterations, stop churning:
ship what is green and record the remaining gap, its root cause, and the proposed fix as an
explicit follow-up. Never close the gap by lowering the bar.

## References (load on demand)
- `references/workspace.md` — the `.ai/<slug>/` workspace, `state.md`, resume protocol, increment sizing.
- `references/research.md` — the ground-truth research document: citations, absence evidence, scope.
- `references/delegation.md` — running research, design and review in subagents; briefs and spot-check.
- `references/project-profile.md` — profile the project; anti-debt rules; design verification checklist.
- `references/design-doc.md` — the 3-page documents: structure, simple diagrams, skeleton.
- `references/html-theme.md` — shared HTML theme, reading controls, comment/approval handoff.
- `references/ux-design.md` — UX spec and the design-first approval gate for user-facing surfaces.
- `references/testing-and-e2e.md` — unit, integration, and non-browser end-to-end expectations.
- `references/e2e-agent-browser.md` — agent-browser for all browser/front-end verification.
- `references/quality-bar.md` — the scored rubric and the convergence loop.
- `references/quality-metrics.md` — the deterministic probe: tools, baseline comparison, gate, `metrics.json`.
- `references/review-and-pr.md` — self-review checklist, quality gate, evidence bundle, commit/PR.
- `references/final-report.md` — the end-of-run report: structure, gate row, metrics, what's pending.
- `references/production-readiness.md` — the checklist that takes an app from building to live.
- `references/app-scale-delivery.md` — outer loop for delivering an entire app in vertical slices.
- `references/parallel-execution.md` — when and how to split work across subagents.

## Final report
Every run ends with a report — **written to `.ai/<slug>/report.html`** using the shared theme,
and summarised in the chat. It is the one artifact a person reads to know what happened, so it
states what is true, not what was hoped. Structure and template: `references/final-report.md`.

It covers: what was **delivered** (and what was not) · each acceptance criterion with how it was
proven · **the gate row, G1–G6, with pass/blocked and the reason** · the measured numbers (tests,
coverage, probe deltas, mutation score, and anything `unavailable`) · the 9-dimension scorecard
citing those numbers · convergence iterations · **what is pending, unproven or
environment-blocked, with the exact command to finish it** · assumptions still unconfirmed ·
follow-ups · and the PR link or the commit plus next step.

Write it even when the run is cut short: a partial report that names the blocker is worth far
more than none.

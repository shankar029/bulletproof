---
name: bulletproof
description: Elite end-to-end delivery workflow. Use when asked to implement a requirement, feature, bug fix, or change of any size (given as text, a doc path, or an issue link) and it must be delivered at top-1% software-architect quality — project-aware, planned, fully tested (unit + integration + end-to-end), reviewed, and shipped as a PR with proof. Invoked directly via /bulletproof <requirement>.
---

# Bulletproof Delivery

You are a top‑1% software architect. When this skill runs, you own the requirement
**end to end** and deliver it at production quality — nothing half-done, nothing that
adds tech debt, nothing unverified. Work through five phases in order. **Each phase
has a gate: do not advance until the gate passes.** State when you pass each gate.

This is a **convergence loop, not a single pass**: after the phases you score the work against a
top-1% quality bar (correctness, scope fidelity, reuse, design, extensibility, robustness, tests,
evidence) and **keep iterating — fixing root causes — until every dimension meets the bar** or a
genuine blocker forces a question. Passing tests is the floor; the bar is high-quality, and you do
not stop short of it. See `references/quality-bar.md`.

The requirement is provided as `$ARGUMENTS` — plain text, a path to a doc, or a link
to an issue/PR. If it points to a file or URL, read it fully first.

## Prime directives (never violate)
1. **Honor the project.** Match its architecture, conventions, style, and tooling.
   Never introduce a pattern that fights how the project is built. When in doubt,
   copy the project's existing patterns over your personal preference.
   **Right-size the effort:** scale rigor to the task's size and surface, and reuse existing
   tooling — do **not** introduce a test framework, coverage tooling, build config, or
   dependencies the project doesn't already use. In a bare or single-file task, prefer the
   platform's zero-install runner (e.g. `node --test`) over scaffolding + `npm install`.
2. **No tech debt.** Reject shortcuts that create debt. No dead code, no TODOs left
   behind, no commented-out blocks, no "temporary" hacks, no copy-paste duplication.
3. **No fakes.** Never write stub/placeholder implementations, tests that assert
   nothing, `skip`ped tests, or mocks that hide real behavior just to go green.
   Never suppress a lint/type error without a written, justified reason.
4. **Prove everything.** A change is not done until tests pass, coverage holds, and
   the feature is demonstrated working end to end with captured evidence.
5. **Ask only real questions — but ask them early.** Surface genuine ambiguity in **Phase 1,
   before planning**, batched, each with a recommended default and its tradeoff. When a user is
   present, **pause and wait** for the answers before designing. When no answer is available (a
   headless/one-shot run), proceed on the recommended defaults and record them as explicit
   assumptions to confirm. Never invent scope; never ask about anything you can resolve yourself
   from the code, docs, issue, or conventions.

## The Loop

### Phase 1 — Understand (project + requirement)
- **Profile the project** (see `references/project-profile.md`): languages, frameworks,
  build tool, package manager, test runner(s), lint/format/type config, CI, directory
  layout, architecture patterns, and commit/PR/branch conventions. Read `AGENTS.md`,
  `README`, `CONTRIBUTING`, ADRs, and neighbors of the code you'll touch.
- **Classify the change:** UI / API / library / CLI / infra (may be several).
- **Restate the requirement** as explicit, testable **acceptance criteria**, each with a stable id
  (AC1, AC2, …). Cover the request *in full*: every explicit ask, **each sub-deliverable of a
  multi-part request**, and the implied non-functional needs it carries (performance, security,
  accessibility, backward-compatibility). Capture exactly what was asked — never drop a part, never
  invent scope that wasn't requested.
- **Clarify before planning — interactively when possible.** List the genuine unknowns implied by
  the acceptance criteria: ambiguous scope, conflicting or missing requirements, undecided behavior
  or API/UX shape, and acceptance thresholds you cannot derive. **Resolve each from the code, docs,
  issue, and conventions first.** For anything material that still remains:
  - **A user is present to answer →** *stop and ask now.* Batch the questions (2–4), each with a
    recommended default and the tradeoff, and **do not enter Phase 2 until the answers land.** It is
    correct to pause here — a wrong assumption is far more expensive than a question. Fold the
    answers back into the acceptance criteria.
  - **No answer is available this run** (headless/CI/one-shot) → **do not block.** Take the
    recommended default for each open question, **record it as an explicit assumption** in the plan,
    proceed, and surface those assumptions in the PR for confirmation.
- **GATE 1:** You can state the project profile in a few lines and list acceptance criteria whose
  union covers the whole request — re-read the ask and confirm nothing is missing or added. **Every
  material ambiguity is resolved** (from code/docs) **or clarified** — answered by the user when
  interactive, or defaulted-and-recorded when not. No open unknown remains that could change the
  plan.

### Phase 2 — Plan (design-first)
- Design the solution grounded in **SOLID, DRY, YAGNI, KISS, separation of concerns**
  and, above all, the project's existing patterns. Choose the approach that a staff
  engineer on this codebase would choose.
- Enumerate: files to add/change, data flow, public interfaces, edge cases, failure
  modes, security, performance, backward compatibility, migrations, rollout/rollback.
- Define the **test strategy up front**: which unit, integration, and E2E tests, and
  the coverage target (default: meet or exceed the repo's existing bar; if none, aim
  for meaningful coverage of all new branches).
- **Plan for parallelism** (see `references/parallel-execution.md`): if this agent supports
  parallel subagents, build a dependency graph of the tasks and mark which are file-disjoint
  and dependency-free (parallel candidates) vs. which must be serialized (shared schema, types,
  interfaces, config). Record the split in `PLAN.md`. If unsupported, plan sequentially.
- Write the plan to `PLAN.md` — or a **task-scoped file** (e.g. `<task>-plan.md`) if the repo already
  owns a `PLAN.md`, or **inline in the PR description** for a small change (don't leave a stray plan
  doc in the tree). Keep it checkbox-trackable. **Self-verify it** against the checklist in
  `references/project-profile.md` (§Plan verification): does it honor the
  project? Any gap, unhandled edge case, missing migration, or breaking change? Resolve
  every gap now — not during coding.
- **GATE 2:** the plan (committed file or PR-body) exists, passes self-verification with zero open
  gaps, and its test strategy covers every acceptance criterion. For risky/wide-reaching plans
  (destructive, >10 files, irreversible, cross-cutting), present the plan and get
  sign-off before Phase 3.

### Phase 3 — Implement + Test
- **Use the project's test setup; add the minimum if missing.** Reuse the runner the repo already
  uses. Only if there is none, pick the ecosystem's **lowest-friction** option — prefer a built-in,
  zero-install runner (e.g. `node --test`) over scaffolding a framework + coverage + `npm install`
  for a small task. Add only tooling the task actually needs. See `references/testing-and-e2e.md`.
- Work in **small, test-backed increments**: write the unit/integration test, then the
  implementation that satisfies it (or code-then-test per repo norms) — but every new
  unit of behavior ships with a real test.
- Install any packages needed for any step (test runner, Playwright, HTTP client, etc.)
  using the project's package manager; record them.
- Keep changes cohesive and minimal. Name things well. Document only what needs it.
- **Dispatch parallel work when planned and supported** (see `references/parallel-execution.md`):
  do shared/foundational work first in the main context, then fan out file-disjoint tasks to
  parallel subagents — each in its own git worktree, each with a scoped brief and the same bar
  (real unit + integration tests, left green). Then merge the worktrees back before the gate.
  Isolated worker green is not proof; the gate below runs on the **integrated** result.
- **GATE 3:** All unit + integration tests pass; coverage meets the target; the build
  compiles/type-checks clean.

### Phase 4 — End-to-End Verification (act like a human)
Prove the feature works the way a person would check it. See
`references/testing-and-e2e.md`.
- **Right-size the proof to the surface.** Match E2E depth to the change: a UI needs a real browser
  flow, a service needs real HTTP — but a pure library/CLI's "end to end" is invoking its real
  public API/command (no servers, browsers, or coverage dashboards it doesn't need).
- **Map scenarios to existing coverage first.** For each acceptance-criterion scenario, check
  whether an E2E test already covers it; add tests only for the **uncovered** scenarios and
  **extend the existing suite/file rather than duplicating it**.
- **UI change →** drive the real flow with **Playwright**: navigate, interact, assert
  on rendered results; capture screenshots/traces.
- **API change →** hit the running service with real **HTTP/REST** calls; assert status,
  response schema, and side effects (DB rows, events, files).
- **CLI / library →** invoke the real command / public API and assert observable output.
- **Persist these E2E tests in the repo** and capture evidence (logs, outputs, images).
- **GATE 4:** Every acceptance criterion is demonstrated met, with captured evidence.

### Phase 5 — Review, Prove, and Ship
- **Self-review as a demanding staff reviewer** (see `references/review-and-pr.md`):
  correctness, readability, maintainability, design principles, security, performance,
  error handling, test quality, no leftovers. Fix everything you'd flag in someone else.
- Run the **full quality gate**: **whichever of** format, lint, type-check, coverage, and build the
  repo actually configures (check package scripts, pre-commit, CI) — **plus the full test suite,
  always**. If a tool is genuinely absent, state that rather than inventing one. Fix all issues (no
  suppressions).
- Assemble the **evidence bundle**: requirement → acceptance criteria met, files changed,
  test counts, coverage %, E2E results/artifacts, review notes, risks & follow-ups.
- **Branch first — before your first commit.** Create and switch to a feature branch (`feat/…`,
  `fix/…`, per the repo's convention). **Never commit on `main`/`master`/a protected or default
  branch — even in a throwaway workspace, even with no remote.** "Stop at a local commit" means
  commit *on the feature branch*, never on whatever branch you happened to start on. Before every
  commit, verify with `git rev-parse --abbrev-ref HEAD` that you are **not** on a protected branch;
  if you are, create the branch first. Committing to `main` is an automatic failure, not a style nit.
- **Ship as a PR.** Commit with evidence trailers (Conventional Commit message); push; open the PR
  with the evidence in the body. **First confirm your PR tooling can write to the target repo** —
  e.g. the `gh` auth identity has access (Enterprise Managed User accounts often *cannot* open PRs on
  personal repos, and `git push` succeeding does not prove `gh` can). If the remote or PR
  tooling is unavailable **or unauthorized**, stop at a clean local commit on the feature
  branch and report the exact push + PR commands (or the `…/compare/…` URL). Format details
  in `references/review-and-pr.md`.
- **GATE 5 (ship gate):** conventions honored · plan fully executed · unit +
  integration + E2E all green · coverage target met · review clean · quality gate green ·
  evidence attached · **work committed on a feature branch (never `main`/`master`)** ·
  PR opened (or commit + instructions delivered).

### Convergence — iterate until the top-1% bar is met
Passing tests is the floor, not the bar. Before declaring done, **score the work against the
8-dimension quality rubric** in `references/quality-bar.md` — correctness, **scope fidelity**,
**reuse & DRY**, **design & principles**, **extensibility & maintainability**, robustness, test
quality, and evidence.
- If any required dimension is **below 4/5**, any gate is red, or any acceptance criterion is
  unmet: list the specific gaps with their **root cause**, return to the **earliest phase that owns
  the gap** (design flaw → Phase 2; missing edge case → Phase 3/4; smell → Phase 5), fix, re-verify,
  and **re-score**. Record each iteration in `PLAN.md`.
- Repeat until every required dimension is ≥ 4/5 with all gates green — **or** you hit a genuine
  blocker (real ambiguity, missing decision, external dependency), then stop and ask with a
  recommended default.
- **Do not stop because it "mostly works."** Convergence to the bar is the deliverable. Never game
  the score (no deleting/skipping tests, lowering thresholds, or special-casing over a design flaw).
- **DEFINITION OF DONE:** ship gate green **and** every required rubric dimension ≥ 4/5, proven
  with evidence.

## References (load on demand)
- `references/project-profile.md` — detect & honor project nature; anti-tech-debt; plan verification checklist.
- `references/testing-and-e2e.md` — test infra setup, coverage, Playwright / REST / CLI E2E per ecosystem.
- `references/parallel-execution.md` — detect parallel-agent support; decompose independent work; isolate with worktrees; integrate & verify the whole.
- `references/quality-bar.md` — the top-1% scored rubric (scope, reuse, design, extensibility, ...) and the convergence loop that iterates until the bar is met.
- `references/review-and-pr.md` — review checklist, quality gates, evidence bundle, commit/PR format.

## Final report
Close with a concise summary: what was delivered, proof (tests/coverage/E2E), the
**quality scorecard** (the 8 rubric dimensions with scores + one-line justification), the number
of convergence iterations, the PR link (or commit + next step), and any residual risks or
follow-ups.

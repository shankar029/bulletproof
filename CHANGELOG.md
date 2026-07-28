# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Grow the eval corpus toward 12 tasks; larger `k` + proper CIs — see [`EVAL-PLAN.md`](EVAL-PLAN.md).

## [0.4.0] — 2026-07-27

### Added
- **Committing to a protected branch hard-zeroes the composite** (v2 agent harness,
  `cappedComposite`). A correct-but-on-`main`/`master` delivery is not a valid delivery — it would be
  reverted in a real team — so it scores `0.00` regardless of code quality, surfaced as
  `composite 0.00 (capped: committed to main)`. Other process shortcomings only lower the reported
  `process` signal. +3 unit tests.
- **Explicit "tests not runnable" test-realness state.** `runTestQuality` now distinguishes three
  zero cases — **no tests**, **tests present but the runner discovered/ran zero** (e.g. written for a
  framework `node --test` can't execute), and **tests fail on the arm's own code** — instead of
  lumping the last two together. Surfaced in the v1 report and the v2 per-run line (`test-real 0.00
  (tests not runnable)`). A test the platform runner can't run is not a real test.
- **Non-library agent tasks.** `csv-stats-cli` (cli) and `discount-api` (api) now carry v2 `agent`
  blocks, so E2E + process adherence are exercised live on real CLI/API surfaces — not just
  libraries. First live CLI run (`csv-stats-cli`): baseline works but ships **zero tests / no E2E /
  no process**; bulletproof ships a `node:test` suite that spawns the real CLI (`e2e 1.00`) but the
  eval caught it **committing to `master`** (`process 0.00`) and **weakly guarding its impl under
  mutation** (`test-real 0.06`) — two genuine defects on a realistic task.
- **E2E-verification dimension** (`e2e`) — scores whether the arm ships its *own*
  surface-appropriate end-to-end verification: cli → real process spawn, api → booted server + real
  HTTP, ui → browser driving (pure, tested `hasE2E`). The held-out oracle already proves delivery
  E2E from the grader's side (discount-api boots the real server + `fetch`; signup-form boots HTTP +
  Chromium); this measures the agent's own proof. `discount-api`: bulletproof ships real HTTP E2E
  (1.00) vs baseline none (0.00). Library tasks are `n/a` (public-API invocation, already covered).
- **Process-adherence dimension** (v2 agent harness, `evals/agent/process.mjs`) — observes the
  produced git workspace: did the arm **commit** its work on a **feature branch** with a
  **Conventional Commit** message? Committing to `main`/`master` is a hard **0**. Live-validated on
  `map-limit`: baseline `process 0.00` (never committed) vs bulletproof `process 1.00` (`feat/…`
  branch, `master` untouched, Conventional Commit) — confirmed against real git state.
- **Test-realness dimension** (`testQuality`) — the eval now scores whether an arm's *own* tests are
  real, not just whether the held-out oracle passes. A new pure mutation engine (`evals/lib/mutate.mjs`,
  unit-tested) makes single-site mutants of the arm's implementation; `runTestQuality` re-runs the
  arm's *own* tests against each on a safe temp copy and scores `killed / (killed+survived)`. An arm
  that ships **no tests**, or whose tests pass on its own broken code, scores **0**. This exposed
  what the oracle-only score was blind to: across the corpus, **baseline ships no tests on 6/10
  tasks** (and a suite that kills only 1/6 mutants on another), while bulletproof kills nearly all.
  It also found — and drove fixes for — *real* gaps in two committed bulletproof suites (no binary
  subtraction / unary-plus test in `expr-eval`; no non-integer-`total` test in `paginator`). Wired
  into both the v1 gate (0.9 kill-rate bar; equivalent mutants make an exact 1.0 unsound) and the
  v2 agent harness. `uid`/`order-fsm` yield no mutable operators → `n/a` (honest engine limit).
- **Agent-in-the-loop harness** (EVAL-PLAN v2, prototype) in `evals/agent/`: a pi adapter that
  invokes pi **headless** to *produce* an arm in an isolated workspace, then scores it with the
  existing v1 harness (`evals/lib/score.mjs`) — baseline vs bulletproof differ only by `--skill`.
  Includes a deterministic `--dry-run` (copies the reference solution to prove the plumbing without
  a model), 7 unit tests, an opt-in `agent` block on `task.json`, and a live A/B on `paginator`.
  First live result: both arms 6/6 on this *standard* task, but the bulletproof arm additionally
  wrote a test suite and committed on a `fix/` branch — evidence the skill actually engages.
- **pass@k** in the agent-in-the-loop harness (`--runs k`, new `stats.mjs`): per-run composite plus
  `mean ± stddev` and clean-rate. First trap result (`uid`, k=3): baseline **0.80 ± 0.14**,
  clean-rate **33%** (1/3) vs bulletproof **1.00 ± 0.00**, **100%** (3/3) — the skill's value on
  the trap is *consistency* (baseline can use `node:crypto` but only ~⅓ of the time).
- **Best-effort workspace cleanup** (`safeRm`): a failed `rmSync` of an agent-created `node_modules`
  (Windows `EPERM`/long paths) no longer aborts a pass@k run.
- **`forbiddenDeps` scope check**: `runQuality` now also flags a forbidden package declared as a
  DIRECT dependency in the arm's `package.json` (via pure, tested `hasForbiddenDep`) — closing the
  source-grep-only blind spot. Transitive tooling deps are ignored. `uid` gains `forbiddenDeps`.
- **Live trap-task results** (`map-limit`, `expr-eval` agent blocks added): pass@k on four tasks
  shows a strong base model ceilings on 3 of 4; the skill's measurable win is `uid` (33%→100%
  clean), at a 4–6× latency cost. Recorded in [`evals/agent/README.md`](evals/agent/README.md).

### Changed
- **Docs refreshed around "complete + proven delivery."** Rewrote `README.md` to lead with the
  thesis (finish the job: deliver exactly what was asked, completely, and prove it), reframed the
  eval as a self-critical **instrument** measuring completion/proof across dimensions (accuracy,
  testQuality, e2e, scope, reuse/dup/extensibility, process), and replaced the stale A/B "+60 pts"
  headline. Updated `docs/architecture.md` (three eval layers incl. the v2 hard-cap), `CONTRIBUTING.md`
  (eval gate + unit tests, add-a-task flow), `evals/README.md` (v2 pointer, corrected weights,
  refreshed "deferred"), `benchmark/README.md` (now marked the original illustrative A/B), and the
  `EVAL-PLAN.md` status (v1+v2 shipped).
- **Skill: branch-first discipline is now unmissable.** SKILL.md Phase 5 leads with an explicit
  *"branch first — before your first commit"* step (create/switch to a `feat/…` branch, verify
  `git rev-parse --abbrev-ref HEAD` is not a protected branch, even with no remote), GATE 5 now
  requires "work committed on a feature branch (never `main`/`master`)", and `references/review-and-pr.md`
  spells out that "stop at a local commit" means *on the feature branch*. Surfaced by the eval: a live
  `csv-stats-cli` bulletproof run committed straight to `master`.
- **Skill: interactive Phase 1 clarification.** Phase 1 (Understand) now makes clarification a
  first-class, gated step: the agent lists genuine unknowns, resolves what it can from code/docs, and
  for anything material that remains **asks the user (batched, with recommended defaults) and waits
  for the answers before planning** when a user is present — or, in a headless/one-shot run,
  defaults-and-records the assumptions instead of blocking. GATE 1 now requires every material
  ambiguity to be resolved or clarified before Phase 2. (SKILL.md prime directive #5 + Phase 1;
  copilot launcher synced.)
- **Skill: right-size the effort.** SKILL.md + `references/testing-and-e2e.md` now direct the agent
  to reuse the project's existing tooling and prefer a zero-install built-in runner (e.g.
  `node --test`) instead of scaffolding a framework + coverage + `npm install`, and to match E2E
  depth to the surface (a pure lib/CLI's E2E is a real invocation, not a browser/server). Surfaced
  by the eval: on a one-function task the bulletproof arm was installing ~89 packages
  (vitest/coverage/tsc) and generating a coverage dashboard. After the fix, the same task produced
  just `index.ts` + `index.test.ts` (run via `node --test`), no `node_modules` — ~6 min → 3 min,
  same 1.00 score.

## [0.3.0] — 2026-07-27

### Added
- **Unit tests for the eval scoring library** (`evals/lib/score.test.mjs`, 14 tests) covering
  `composite()` renormalization, `toDimensions()` mappings, and TAP parsing; extracted a pure
  `parseTap()` seam from the spawn-bound `tap()` with zero behavior change.

### Changed
- **Skill fidelity audit** (all five phases reviewed for "delivers exactly what was asked"): Phase 1
  now requires acceptance criteria (each with a stable id) whose union covers the *whole* request —
  every sub-deliverable of a multi-part ask plus implied non-functional needs — with a Gate 1
  re-read to confirm nothing is dropped or invented; Phase 4 maps each scenario to existing E2E
  coverage and adds tests only for the uncovered ones (extend, never duplicate); and the
  convergence scope-fidelity check re-verifies the acceptance criteria against the original request
  so a dropped requirement is caught even when every listed criterion passes.
- **Skill portability fixes** (from a live dogfood run): the plan may live in a task-scoped file or
  the PR description when the repo already owns `PLAN.md` (no stray plan docs); the Phase 5 quality
  gate now runs *whichever* of format/lint/type-check the repo actually configures (tests always)
  instead of assuming all exist; and the ship step verifies the PR tooling can write to the target
  repo (a successful `git push` doesn't prove `gh` is authorized — e.g. Enterprise Managed User
  identities) before falling back to a clean commit + compare URL.

## [0.2.0] — 2026-07-27

### Added
- **One-command installers** (`install.sh` for macOS/Linux/Git-Bash, `install.ps1` for Windows
  PowerShell): `curl -fsSL .../install.sh | sh -s -- <pi|claude|copilot>` downloads the repo and
  drops the skill + launcher into the right per-agent directories. `BULLETPROOF_REF` pins a
  release; `BULLETPROOF_SRC` installs from a local checkout. README + each `install/*.md` updated
  with the one-liner (manual steps kept as fallback).
- **Eval harness v1** (`evals/`): config-driven `evals/tasks/<id>/task.json` schema + a single
  runner (`evals/run.mjs`) that scores every arm on a weighted composite (accuracy + reuse +
  duplication + extensibility + **scope**), writes `report.md`, and exits non-zero on any
  bulletproof regression. Corpus of **10 tasks** across greenfield/**bugfix**/**refactor**/**trap**/
  **test-backfill** and api/cli/ui/library surfaces (incl. two **gnarly** tasks — a recursive-descent
  evaluator and a bounded-concurrency async map — and a stateful state-machine refactor); adding a
  task is drop-in (no runner changes).
- **Scope/guardrail dimension**: a `forbidden`-pattern probe that catches *trap* tasks where an arm
  is 100% accurate yet wrong (e.g. `uid` baseline passes uniqueness but uses `Math.random()`).
- **Mutation-scored test-backfill** (`median-backfill`): the deliverable is a test suite, graded by
  how many planted mutants it kills — a shallow suite scores 33%, a thorough one 100%.

## [0.1.0] — 2026-07-26

Initial release: a portable `/bulletproof` skill plus an objective benchmark proving its value.

### Added
- **Skill** (`SKILL.md`): a five‑phase gated delivery loop (Understand → Plan → Implement+Test →
  E2E Verify → Review+Ship) framed as a **convergence loop** that self‑scores against a top‑1%
  quality bar and iterates on root causes until every dimension is met.
- **References** (`references/`): `project-profile.md`, `testing-and-e2e.md`,
  `parallel-execution.md`, `quality-bar.md`, `review-and-pr.md` (progressive disclosure).
- **Launchers** (`launchers/`): thin per‑agent entry points for pi (prompt template), Claude Code
  (command), and Copilot CLI (custom agent — upstream has no custom slash commands).
- **Install guides** (`install/`): pi, Claude Code, Copilot CLI.
- **Benchmark** (`benchmark/`): objective baseline‑vs‑bulletproof A/B graded by **held‑out oracles**
  across three projects — `discount-api` (HTTP E2E), `csv-stats-cli` (subprocess E2E), and
  `signup-form` (real Chromium/Playwright E2E). Result: oracle accuracy **40.0% → 100%**.
- **Engineering‑quality eval** (`score-quality.mjs`): objective probes for **reuse**, **duplication**,
  and **extensibility** (open/closed) beyond functional correctness, across all three projects.
- **Docs**: `README.md`, `EVAL-PLAN.md`, `docs/architecture.md`, `CONTRIBUTING.md`, `LICENSE` (MIT).

[Unreleased]: https://github.com/shankar029/bulletproof/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/shankar029/bulletproof/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/shankar029/bulletproof/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/shankar029/bulletproof/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/shankar029/bulletproof/tree/v0.1.0

# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- **Skill: right-size the effort.** SKILL.md + `references/testing-and-e2e.md` now direct the agent
  to reuse the project's existing tooling and prefer a zero-install built-in runner (e.g.
  `node --test`) instead of scaffolding a framework + coverage + `npm install`, and to match E2E
  depth to the surface (a pure lib/CLI's E2E is a real invocation, not a browser/server). Surfaced
  by the eval: on a one-function task the bulletproof arm was installing ~89 packages
  (vitest/coverage/tsc) and generating a coverage dashboard. After the fix, the same task produced
  just `index.ts` + `index.test.ts` (run via `node --test`), no `node_modules` — ~6 min → 3 min,
  same 1.00 score.

### Planned
- Grow the eval corpus toward 12 tasks; larger `k` + proper CIs — see [`EVAL-PLAN.md`](EVAL-PLAN.md).

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

[Unreleased]: https://github.com/shankar029/bulletproof/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/shankar029/bulletproof/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/shankar029/bulletproof/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/shankar029/bulletproof/tree/v0.1.0

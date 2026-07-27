# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Skill portability fixes** (from a live dogfood run): the plan may live in a task-scoped file or
  the PR description when the repo already owns `PLAN.md` (no stray plan docs); the Phase 5 quality
  gate now runs *whichever* of format/lint/type-check the repo actually configures (tests always)
  instead of assuming all exist; and the ship step verifies the PR tooling can write to the target
  repo (a successful `git push` doesn't prove `gh` is authorized — e.g. Enterprise Managed User
  identities) before falling back to a clean commit + compare URL.

### Planned
- Grow the eval corpus toward 12 tasks and add `pass@k` once agent-in-the-loop runs land (v2) —
  see [`EVAL-PLAN.md`](EVAL-PLAN.md).

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

[Unreleased]: https://github.com/shankar029/bulletproof/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/shankar029/bulletproof/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/shankar029/bulletproof/tree/v0.1.0

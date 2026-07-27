# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Eval harness v1** (`evals/`): config-driven `evals/tasks/<id>/task.json` schema + a single
  runner (`evals/run.mjs`) that scores every arm on a weighted composite (accuracy + reuse +
  duplication + extensibility), writes `report.md`, and exits non-zero on any bulletproof
  regression. Seeded with the three v0 projects; adding a task is drop-in (no runner changes).

### Planned
- Grow the eval corpus to 8–12 tasks (bugfix/refactor/trap tasks, more stacks) and add `pass@k`
  once agent-in-the-loop runs land (see [`EVAL-PLAN.md`](EVAL-PLAN.md)).

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

[Unreleased]: https://github.com/shankar029/bulletproof/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shankar029/bulletproof/releases/tag/v0.1.0

# Bulletproof — Build Plan

**Goal:** Ship one portable slash command `/bulletproof <requirement>` that makes any terminal coding agent (pi, Claude Code, Copilot CLI) deliver work like a top‑1% software architect: understand the project → plan (design-first) → implement + test → E2E verify → review → open a PR with proof.

**Status:** done

## Design decisions
- **Single source of truth:** one `SKILL.md` (Agent Skills standard) holds the loop. Per-agent launchers are thin and point at it. Keeps it DRY + lean.
- **Progressive disclosure:** `SKILL.md` stays tight; deep detail lives in `references/` loaded on demand.
- **Portability:** pi → prompt template + skill; Claude Code → command + skill; Copilot CLI → custom agent (no slash-command support upstream).
- **Safety:** never commit to protected branches; PR-only; refuse stubs/fake tests/lint suppression; branch-guarded.

## Structure
- [x] `SKILL.md` — the 5-phase loop, gates, principles
- [x] `references/project-profile.md` — detect & honor project nature; anti-tech-debt rules
- [x] `references/testing-and-e2e.md` — test infra setup, coverage, Playwright/REST/CLI E2E
- [x] `references/parallel-execution.md` — detect parallel-agent support; split independent work; worktrees; integrate
- [x] `references/review-and-pr.md` — review checklist, quality gates, evidence bundle, PR format
- [x] `launchers/pi/prompts/bulletproof.md`
- [x] `launchers/claude/commands/bulletproof.md`
- [x] `launchers/copilot/agents/bulletproof.agent.md`
- [x] `install/pi.md`, `install/claude-code.md`, `install/copilot-cli.md`
- [x] `README.md`

## Verification
- [x] Files valid — skill name `bulletproof` OK; description 407/1024 chars
- [x] Launchers reference the skill correctly for each agent (pi template, Claude `@`-ref, Copilot agent)
- [x] Install docs match real file locations (`~/.agents/skills`, `~/.claude/skills`+`commands`, `~/.copilot/agents`)

## Benchmark (added)
- [x] `benchmark/` objective A/B harness: baseline vs bulletproof, held-out oracle grader
- [x] Project A `discount-api` (HTTP E2E) + Project B `csv-stats-cli` (subprocess E2E)
- [x] Project C `signup-form` (real Chromium/Playwright E2E) — UI arm confirmed runnable on ARM64
- [x] `run.mjs` (logic) + `run-ui.mjs` (Playwright) reproducible runners + `RESULTS.md`
- [x] Result: oracle accuracy 40.0% (baseline) -> 100% (bulletproof) across API+CLI+UI, +60 pts
- [x] `EVAL-PLAN.md` — plan to grow the benchmark into a continuous, CI-gated eval harness

## Decisions log
- 2026-07-26 — command name `/bulletproof` (matches repo, memorable).
- 2026-07-26 — Copilot CLI gets a custom agent, not a slash command (upstream gap, issues #618/#1004).
- 2026-07-26 — parallel execution is capability-gated + independence-gated; workers run in isolated
  worktrees; the phase gates always run on the integrated result, not per worker.

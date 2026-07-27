# Architecture & Design

How the pieces fit, and the rationale behind the choices. For usage see [`README.md`](../README.md);
for the eval roadmap see [`EVAL-PLAN.md`](../EVAL-PLAN.md).

## Mental model

```
requirement ──▶ launcher (per agent) ──▶ SKILL.md (the loop) ──▶ references/*.md (loaded on demand)
                                                │
                                                ▼
                                    convergence loop: run phases,
                                    self-score vs quality bar, iterate
                                                │
                                                ▼
                                    PR on a feature branch + evidence
```

- **`SKILL.md` is the single source of truth.** The whole operating loop lives here once.
- **Launchers are thin.** Each agent has a tiny entry file that points at `SKILL.md`, so behavior
  is identical everywhere and there's only one place to change.
- **References are progressive disclosure.** `SKILL.md` stays lean; depth (test setup, review
  checklist, quality rubric, parallelism rules) sits in `references/*.md` and is pulled in only when
  a phase needs it.

## Key design decisions

### 1. One skill, thin per‑agent launchers
DRY and consistency: the loop is authored once. `launchers/pi`, `launchers/claude`, and
`launchers/copilot` only adapt the invocation surface, not the behavior.

### 2. Copilot CLI is a custom agent, not a slash command
Copilot CLI has **no custom slash‑command support** upstream
(github/copilot-cli issues #618, #1004). So its launcher is a **custom agent**
(`.github/agents/bulletproof.agent.md`) that carries the same instructions. pi and Claude Code get
real `/bulletproof` commands.

### 3. The loop is a convergence loop, not a single pass
Passing tests is the *floor*. After the five phases, the agent scores the work against the 8‑dimension
bar in [`references/quality-bar.md`](../references/quality-bar.md) — correctness, **scope fidelity**,
**reuse & DRY**, **design & principles**, **extensibility**, robustness, test quality, evidence — and
loops back to the earliest phase that owns any gap, fixing **root causes**, until every required
dimension is ≥ 4/5 or a genuine blocker forces a question. Anti‑gaming rules forbid lowering the bar
or deleting tests to "pass."

### 4. Safe by default
Feature branches only; PR‑only; **never** commit to `main`/`master`/protected branches. The skill
refuses stubs, empty/skipped tests, and unjustified lint/type suppression.

### 5. Parallelism is capability‑ and independence‑gated
If the host supports subagents (pi `subagent`, Claude `Task`), the plan builds a dependency graph
and fans out only **file‑disjoint, dependency‑free** tasks, each in an isolated **git worktree**;
foundational/shared work runs first in the main context. The final gate always runs on the
**integrated** result, never on isolated‑worker green. Unsupported hosts (e.g. Copilot CLI) run
sequentially. Details in [`references/parallel-execution.md`](../references/parallel-execution.md).

## The benchmark & eval architecture

The benchmark exists to make the skill's value **objective and reproducible**, not self‑asserted.

### Arms
Every project ships two implementations of one `SPEC.md`:
- **baseline** — what a raw agent produces without the skill.
- **bulletproof** — skill‑quality: real unit + integration tests, E2E, reuse, extensibility.

### Held‑out oracle grading
Correctness is scored by an **oracle** acceptance suite that the arms do **not** import at authoring
time. Oracles run each arm via `ARM_PATH` (logic) or `ARM_DIR` (UI), so the same suite grades both
arms identically. This prevents "teaching to the test."

### Two scoring layers
1. **Functional** (`run.mjs`, `run-ui.mjs`) — does it meet the spec? HTTP/subprocess/real‑browser E2E.
2. **Engineering quality** (`score-quality.mjs`) — does it *reuse* seeded utilities, avoid
   *duplication*, and stay *open/closed*? Each project seeds `shared/` helpers the arm should reuse
   and (where a module boundary exists) a held‑out `extension.test.ts` that adds a brand‑new case
   without editing the core function.

### Runners as regression gates
Each runner exits non‑zero if any `bulletproof` arm regresses — the seed of the CI gate described in
[`EVAL-PLAN.md`](../EVAL-PLAN.md).

## Repository layout

| Path | What it is |
|---|---|
| `SKILL.md` | The operating loop (single source of truth). |
| `references/` | On‑demand depth for each phase. |
| `launchers/` | Thin per‑agent entry points. |
| `install/` | Per‑agent install steps. |
| `benchmark/` | Objective A/B benchmark + oracles + runners. |
| `EVAL-PLAN.md` | Roadmap to a continuous, CI‑gated eval harness. |
| `docs/architecture.md` | This document. |

## Environment notes

- **Node ≥ 22** for native TS type‑stripping (`node --test`). Strip‑only mode rejects TS
  "parameter properties" — declare class fields explicitly.
- **Playwright** (Chromium headless) is confirmed working on ARM64 Windows; it's only needed for the
  UI benchmark arm.

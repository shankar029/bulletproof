# Architecture & Design

How the pieces fit, and the rationale behind the choices. For usage see [`README.md`](../README.md);
for the eval roadmap see [`EVAL-PLAN.md`](../EVAL-PLAN.md).

## Mental model

```
requirement ──▶ launcher (per agent) ──▶ SKILL.md (the loop) ──▶ references/*.md (loaded on demand)
                                                │
                                                ▼
                                    convergence loop: run 6 phases,
                                    measure (probe + mutation), review,
                                    self-score vs quality bar, iterate
                                                │
                                                ▼
                                    PR on a feature branch + evidence
```

- **`SKILL.md` is the single source of truth.** The whole operating loop lives here once.
- **Launchers are thin.** Each agent has a tiny entry file that points at `SKILL.md`, so behavior
  is identical everywhere and there's only one place to change.
- **References are progressive disclosure.** `SKILL.md` stays lean; depth (workspace/resume, design
  documents, test setup, review checklist, quality rubric, metrics, parallelism) sits in
  `references/*.md` and is pulled in only when a phase needs it.
- **Scripts and assets ship with the skill.** `scripts/` (probe, mutation) and `assets/` (artifact
  theme) are installed alongside `SKILL.md`; they run from outside the target project and never add
  dependencies or config to it.

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
Passing tests is the *floor*. After the six phases, the agent scores the work against the 9‑dimension
bar in [`references/quality-bar.md`](../references/quality-bar.md) — correctness, **grounding**,
**design fidelity**, scope fidelity, reuse & DRY, design & modularity, extensibility, robustness,
test quality & evidence — and loops back to the earliest phase that owns any gap, fixing **root
causes**, until every required dimension is ≥ 4/5 or a genuine blocker forces a question.
Anti‑gaming rules forbid lowering the bar or deleting tests to "pass", and where a deterministic
metric exists for a dimension the score **must cite it**.

### 3a. Design precedes code, and the design is a reviewable artifact
Phase 2 produces a 3‑page HTML design document (classes, interfaces, interactions) before any
implementation, styled by a shared theme in `assets/` that also provides an in‑document
highlight/comment/approve layer. The verdict returns as `review.json`, so approval is
machine‑readable and the run can stop and resume around a human.

### 3b. Work is durable across sessions
Every non‑trivial task owns `.ai/<slug>/` — `state.md` (gate row, increments, next action), the
design and plan, review findings, metrics and evidence. The loop reads `state.md` first and resumes
rather than restarting, which is what makes multi‑increment work survive a crash or a context limit.

### 3c. Quality is measured, not asserted
`scripts/probe.py` compares HEAD against the merge‑base in a throwaway worktree (duplication,
complexity, cycles, dead code, static findings); `scripts/mutate.py` mutates only the changed lines
and runs the project's own tests to prove the tests assert something. Gates are delta‑based to avoid
Goodhart effects, with greenfield and front‑end projects detected and judged appropriately.

### 4. Safe by default
Feature branches only; PR‑only; **never** commit to `main`/`master`/protected branches. The skill
refuses stubs, empty/skipped tests, and unjustified lint/type suppression.

### 5. Parallelism is capability‑ and independence‑gated
If the host supports subagents (pi `subagent`, Claude `Task`), the plan builds a dependency graph
and fans out only **file‑disjoint, dependency‑free** tasks, each in an isolated **git worktree**;
foundational/shared work runs first in the main context. The final gate always runs on the
**integrated** result, never on isolated‑worker green. Unsupported hosts (e.g. Copilot CLI) run
sequentially. Details in [`references/parallel-execution.md`](../references/parallel-execution.md).

## The eval architecture

The eval exists to make the skill's value **objective, reproducible, and self-critical** — it is an
instrument for finding the skill's defects, not a scoreboard for flattering it. It comes in three
layers of increasing fidelity.

### Held-out oracle grading (the shared foundation)
Correctness is scored by an **oracle** acceptance suite the solution does **not** import at authoring
time. Oracles run each arm via `ARM_PATH` (logic) or `ARM_DIR` (UI), so the same suite grades every
arm identically. This prevents "teaching to the test."

### Layer 1 — `benchmark/` (original illustrative A/B)
Three projects, each shipping a `baseline` and a `bulletproof` implementation of one `SPEC.md`, graded
by a held-out oracle across HTTP / subprocess / real-browser E2E, plus an engineering-quality probe
(`score-quality.mjs`) for reuse, duplication, and open/closed extensibility. Illustrative (N=1, one
session), kept as the seed of the idea.

### Layer 2 — `evals/` (config-driven regression gate, v1)
Generalizes the benchmark into a **task corpus** (`evals/tasks/<id>/task.json`) driven by one runner
(`evals/run.mjs`) and a pure scoring library (`evals/lib/`, unit-tested). Each task scores a weighted
**composite** over independent 0..1 dimensions: `accuracy` (held-out oracle), `reuse`, `duplication`,
`extensibility`, `scope` (forbidden source patterns + forbidden direct deps — catches *trap* tasks),
`e2e` (surface-appropriate end-to-end test present), and `testQuality` (**mutation kill-rate of the
arm's own tests** — a fake/absent/unrunnable suite scores 0). The runner **exits non-zero if any
`bulletproof` arm regresses**, so it is the CI gate.

### Layer 3 — `evals/agent/` (agent-in-the-loop, v2)
The host agent is actually invoked **headless to produce the arm**; the only difference between arms
is whether the skill is loaded (`--skill`), with everything else isolated (`-nc -ne -np -ns`). It
reuses the same scoring library, adds a **`process`** dimension observed from the real git workspace
(committed on a feature branch? Conventional Commit? — and committing to `main`/`master`
**hard-zeroes the composite** via `cappedComposite`), and supports **pass@k** to measure run-to-run
variance. This is where the skill's real behavior (not a hand-authored proxy) is measured.

### Why this matters
The eval has repeatedly caught the skill's *own* defects — over-engineering a trivial task, and
committing to a protected branch — which drove concrete fixes to `SKILL.md`, each then verified live.
That feedback loop, not any single headline number, is the point.

## Repository layout

| Path | What it is |
|---|---|
| `SKILL.md` | The operating loop (single source of truth). |
| `references/` | On‑demand depth for each phase. |
| `launchers/` | Thin per‑agent entry points. |
| `install/` | Per‑agent install steps. |
| `evals/` | Config‑driven eval harness (v1 gate) + `evals/agent/` (v2 agent‑in‑the‑loop). |
| `benchmark/` | Original illustrative A/B benchmark + oracles + runners. |
| `EVAL-PLAN.md` | Roadmap to a continuous, CI‑gated eval harness. |
| `docs/architecture.md` | This document. |

## Environment notes

- **Node ≥ 22** for native TS type‑stripping (`node --test`). Strip‑only mode rejects TS
  "parameter properties" — declare class fields explicitly.
- **Playwright** (Chromium headless) is confirmed working on ARM64 Windows; it's only needed for the
  UI benchmark arm.

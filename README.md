# bulletproof

**One slash command that makes any terminal coding agent deliver like a top‑1% software
architect.** Give it a requirement (text, a doc path, or an issue link) and it runs the full
loop — understand the project, plan, implement with tests, verify end-to-end like a human,
review, and open a PR with proof.

```
/bulletproof <requirement | doc path | issue link>
```

## What it does

A five-phase loop, each with a gate it must pass before advancing:

1. **Understand** — profiles the project (stack, tests, conventions) and honors it; restates
   the requirement as testable acceptance criteria.
2. **Plan** — design-first using SOLID/DRY/KISS *and the project's own patterns*; writes
   `PLAN.md`; self-verifies and closes every gap **before** writing code.
3. **Implement + Test** — sets up test infra if missing; writes real unit + integration tests
   for all new code; installs any needed packages; keeps the build green.
4. **E2E Verify** — proves the feature like a human: **Playwright** for UI, real **HTTP/REST**
   for APIs, real invocation for CLI/libraries. These tests are committed; evidence captured.
5. **Review + Ship** — self-reviews as a demanding staff engineer, runs the full quality gate
   (format/lint/types/tests/coverage/build), assembles an evidence bundle, and opens a **PR on
   a feature branch** (never commits to main) with the proof in the description.

It runs as a **convergence loop, not a single pass**: after the phases it scores the work against a
top-1% rubric — correctness, **scope fidelity**, **reuse & DRY**, **design & principles**,
**extensibility**, robustness, tests, evidence (see [`references/quality-bar.md`](references/quality-bar.md)) —
and keeps iterating on root causes until every dimension is ≥ 4/5 or a genuine blocker forces a
question. Passing tests is the floor; it does not stop short of the bar.

**Prime directives:** honor the project · zero tech debt · no fakes/stubs/skipped tests · prove
everything · ask only real questions (batched, with recommended defaults).

## Layout

```
bulletproof/
├── SKILL.md                     # the operating loop (single source of truth)
├── references/
│   ├── project-profile.md       # detect & honor project nature; anti-tech-debt; plan checklist
│   ├── testing-and-e2e.md       # test infra setup, coverage, Playwright / REST / CLI E2E
│   ├── parallel-execution.md    # detect parallel-agent support; split independent work; worktrees
│   ├── quality-bar.md           # top-1% scored rubric + convergence loop (iterate until bar met)
│   └── review-and-pr.md         # review checklist, quality gate, evidence bundle, PR format
├── launchers/                   # thin per-agent entry points (all point at SKILL.md)
│   ├── pi/prompts/bulletproof.md
│   ├── claude/commands/bulletproof.md
│   └── copilot/agents/bulletproof.agent.md
└── install/                     # per-agent install steps
    ├── pi.md
    ├── claude-code.md
    └── copilot-cli.md
```

## Install

- **pi** → [`install/pi.md`](install/pi.md) — skill + `/bulletproof` prompt template
- **Claude Code** → [`install/claude-code.md`](install/claude-code.md) — skill + `/bulletproof` command
- **Copilot CLI** → [`install/copilot-cli.md`](install/copilot-cli.md) — custom agent (no slash-command support upstream)

## Benchmark

An objective A/B benchmark lives in [`benchmark/`](benchmark/) — two implementations of the same
spec (a naive **baseline** vs. a **bulletproof** run), each graded by a **held-out oracle**
acceptance suite. Reproduce with `cd benchmark && node run.mjs` (Node ≥ 22, no deps).

| Arm | Oracle accuracy (3 projects) | Tests shipped | E2E |
|---|---|---|---|
| baseline | **40.0%** (14/35) | shallow / none | none |
| bulletproof | **100%** (35/35) | 20 + 8 + 7, all green | HTTP + subprocess + **real browser** |

**+60 accuracy points** on identical specs, across an HTTP API, a CLI, and a Playwright-driven UI.
Beyond correctness, an **engineering-quality** layer (`score-quality.mjs`) measures reuse,
duplication, and extensibility across all three projects: every baseline **fails to reuse seeded
utilities and can't be extended without editing core**, while every bulletproof arm **reuses the
shared helpers, adds no duplication, and is open/closed** (a held-out oracle adds a brand-new case
without touching the core function). Full findings in [`benchmark/RESULTS.md`](benchmark/RESULTS.md).

A config-driven **eval harness** in [`evals/`](evals/) formalizes this into a task corpus with a
single runner and a weighted composite scorecard (`node evals/run.mjs` → [`evals/report.md`](evals/report.md)),
doubling as a regression gate. It currently spans **10 tasks** — greenfield, **bugfix**, **refactor**
(incl. a stateful state machine), a **trap** (an arm can be 100% accurate yet wrong, caught by a
scope/guardrail dimension), a **test-backfill** graded by mutation kill-rate, and two **gnarly**
tasks (a recursive-descent evaluator and a bounded-concurrency async map). Roadmap in
[`EVAL-PLAN.md`](EVAL-PLAN.md).

## Design notes

- **Single source of truth:** the loop lives once in `SKILL.md`; launchers are thin wrappers, so
  behavior stays identical across agents.
- **Lean by design:** `SKILL.md` stays tight; deep detail sits in `references/` and loads only
  when a phase needs it (progressive disclosure).
- **Safe by default:** feature branches only, PR-only, no protected-branch commits; refuses
  stubs, empty tests, and unjustified lint/type suppression.
- **Parallel when it's safe:** if the agent supports subagents (pi `subagent`, Claude `Task`),
  it splits file-disjoint, dependency-free work across parallel agents in isolated git worktrees,
  then integrates and verifies the whole. Unsupported agents (e.g. Copilot CLI) run sequentially.
- **Rename:** don't like `/bulletproof`? Rename the launcher file (e.g. `ship.md` → `/ship`).

More on the design and how to extend it: [`docs/architecture.md`](docs/architecture.md).

## Contributing

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). The project **dogfoods its own
skill**: substantive changes are planned, tested, verified, and shipped as a PR with proof. Keep
every benchmark runner green (`run.mjs`, `run-ui.mjs`, `score-quality.mjs`). Changes are tracked in
[`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE) © 2026 shankar029.

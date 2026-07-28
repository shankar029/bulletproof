# bulletproof

**One slash command that makes any terminal coding agent finish the job — deliver exactly what
you asked, completely, and prove it works.**

Coding agents are great at *starting* work and bad at *finishing* it: half-built features, tests
that assert nothing (or none at all), "works on my machine" with no end-to-end proof, tech debt left
behind, and commits straight to `main`. `/bulletproof` fixes that. Give it a requirement — text, a
doc path, or an issue link — and it owns the delivery end to end: understands the **whole** ask,
plans, implements with real tests, **proves the feature works the way a human would check it**,
reviews, and opens a PR with the evidence.

```
/bulletproof <requirement | doc path | issue link>
```

## What "delivered" means here

Five phases, each with a gate it must pass before advancing. Together they make the ask *complete*
and *proven*, not merely *attempted*:

1. **Understand the whole ask.** Profiles the project (stack, tests, conventions) and restates the
   requirement as testable **acceptance criteria that cover every part** of it. If anything material
   is ambiguous it **clarifies before planning** — asking you (batched, each with a recommended
   default) when you're present, or recording explicit assumptions when running headless. It never
   silently guesses and never invents scope you didn't ask for.
2. **Plan (design-first).** SOLID/DRY/KISS *and the project's own patterns*; writes `PLAN.md`;
   self-verifies and closes every gap **before** writing code.
3. **Implement + test.** Real unit + integration tests for all new behavior — never stubs, empty
   asserts, or `skip`ped tests. Right-sizes the tooling: reuses the project's runner and won't
   scaffold a framework, coverage dashboard, or dependency a small task doesn't need.
4. **Prove it end-to-end.** Verifies the feature the way a person would: **Playwright** for UI, real
   **HTTP** for APIs, real invocation for CLIs/libraries — with captured evidence. This is the
   *"did we actually deliver what was asked"* gate, and it scales to the surface.
5. **Review + ship.** Self-reviews as a demanding staff engineer, runs the full quality gate
   (format/lint/types/tests/coverage/build — whichever the repo configures), assembles an evidence
   bundle, and opens a **PR on a feature branch** (never commits to `main`/`master`) with the proof
   in the description.

Then it runs a **convergence loop**: it scores the work against a top-1% rubric — correctness,
**scope fidelity**, **reuse & DRY**, **design**, **extensibility**, robustness, test quality,
evidence (see [`references/quality-bar.md`](references/quality-bar.md)) — and keeps fixing **root
causes** until every dimension clears the bar or a genuine blocker forces a question. Passing tests
is the floor, not the finish line.

**Prime directives:** honor the project (and right-size the effort) · zero tech debt ·
no fakes/stubs/skipped tests · prove everything · ask only real questions.

## How we know it actually delivers

The skill's value isn't self-asserted — it's **measured**, by an eval designed to catch the skill's
*own* failures rather than flatter it. Per task, per arm, it scores whether the agent delivered what
was asked — completely and provably — across independent dimensions:

| Dimension | The question it answers |
|---|---|
| **accuracy** | Does it actually work? — a held-out oracle acceptance suite the solution never sees. |
| **testQuality** | Are the tests *real*? — mutate the solution and check whether its **own** tests catch the bug. No tests, or tests the runner can't even execute → `0`. |
| **e2e** | Is it proven end-to-end for its surface? — CLI spawn / real HTTP / real browser. |
| **scope** | Exactly what was asked — no forbidden pattern (e.g. weak RNG), no needless dependency? |
| **reuse · duplication · extensibility** | Built on the project's own utilities, no copy-paste, open/closed to new cases? |
| **process** | Shipped like a professional — committed on a feature branch, **never** on `main`? |

Two tiers, both dependency-free (Node ≥ 22):

- **v1 — regression gate** ([`evals/`](evals/)): a config-driven corpus of **10 tasks** (greenfield,
  bugfix, refactor, a stateful state machine, a mutation-graded test-backfill, and *trap* tasks where
  an arm can be 100% accurate yet still wrong). Hand-authored baseline vs. bulletproof arms graded by
  held-out oracles. `node evals/run.mjs` prints a composite scorecard and **exits non-zero if any
  bulletproof arm regresses**.
- **v2 — agent-in-the-loop** ([`evals/agent/`](evals/agent/)): the agent is actually invoked headless
  to *produce* the solution, with the **only** difference between arms being the skill. It observes
  `process` from the real git workspace, supports **pass@k** variance, and **hard-zeroes any run that
  commits to `main`**.

**Honest findings** — an eval earns its keep by finding defects:

- A capable base model already *ceilings* on easy tasks; the skill's measurable wins concentrate on
  **traps** (weak RNG / needless deps, where the skill makes correctness *reliable* across runs),
  **real tests** (baseline ships none on 6/10 tasks), **E2E**, and **process**.
- The eval caught **bulletproof's own defects** and drove the fixes: it over-engineered a
  one-function task (89 packages + a coverage dashboard → fixed by "right-size the effort"), and on a
  harder task it committed straight to `master` (→ fixed by hardening Phase 5 *and* hard-capping the
  score). Both fixes were then **verified live**.

Method and numbers: [`evals/README.md`](evals/README.md) (v1) ·
[`evals/agent/README.md`](evals/agent/README.md) (v2) · the original illustrative A/B in
[`benchmark/`](benchmark/) · roadmap in [`EVAL-PLAN.md`](EVAL-PLAN.md).

## Layout

```
bulletproof/
├── SKILL.md                     # the operating loop (single source of truth)
├── references/                  # on-demand depth per phase (progressive disclosure)
│   ├── project-profile.md       #   detect & honor project nature; anti-tech-debt; plan checklist
│   ├── testing-and-e2e.md       #   test infra, coverage, Playwright / REST / CLI E2E; right-sizing
│   ├── parallel-execution.md    #   detect parallel-agent support; split disjoint work; worktrees
│   ├── quality-bar.md           #   top-1% scored rubric + convergence loop
│   └── review-and-pr.md         #   review checklist, quality gate, evidence bundle, PR format
├── launchers/                   # thin per-agent entry points (all point at SKILL.md)
│   ├── pi/prompts/bulletproof.md
│   ├── claude/commands/bulletproof.md
│   └── copilot/agents/bulletproof.agent.md
├── install/                     # per-agent manual install steps (pi / claude-code / copilot-cli)
├── evals/                       # the eval harness (how we know it delivers)
│   ├── run.mjs                  #   v1: config-driven corpus + composite scorecard + regression gate
│   ├── lib/                     #   scoring lib (oracle, quality probes, mutation engine) + unit tests
│   ├── tasks/                   #   per-task descriptors (task.json)
│   └── agent/                   #   v2: agent-in-the-loop harness (produces arms; pass@k; process)
├── benchmark/                   # original illustrative A/B (generalized by evals/)
├── install.sh                   # one-command installer (macOS/Linux/Git-Bash)
└── install.ps1                  # one-command installer (Windows PowerShell)
```

## Install

**One command** (downloads from GitHub, installs the skill + launcher for your agent):

```bash
# macOS / Linux / Git-Bash — pick one: pi | claude | copilot
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
```

```powershell
# Windows PowerShell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) pi
```

Install a specific release with `BULLETPROOF_REF=v0.3.0`. Prefer to do it by hand? Per-agent manual
steps:

- **pi** → [`install/pi.md`](install/pi.md) — skill + `/bulletproof` prompt template
- **Claude Code** → [`install/claude-code.md`](install/claude-code.md) — skill + `/bulletproof` command
- **Copilot CLI** → [`install/copilot-cli.md`](install/copilot-cli.md) — custom agent (no slash-command support upstream)

## Design notes

- **Single source of truth:** the loop lives once in `SKILL.md`; launchers are thin wrappers, so
  behavior stays identical across agents.
- **Lean by design:** `SKILL.md` stays tight; deep detail sits in `references/` and loads only when
  a phase needs it (progressive disclosure).
- **Safe by default:** feature branches only, PR-only, no protected-branch commits; refuses stubs,
  empty tests, and unjustified lint/type suppression — and the eval enforces it (a commit to `main`
  hard-zeroes the run).
- **Parallel when it's safe:** if the agent supports subagents (pi `subagent`, Claude `Task`), it
  splits file-disjoint, dependency-free work across parallel agents in isolated git worktrees, then
  integrates and verifies the whole. Unsupported agents (e.g. Copilot CLI) run sequentially.
- **Rename:** don't like `/bulletproof`? Rename the launcher file (e.g. `ship.md` → `/ship`).

More on the design: [`docs/architecture.md`](docs/architecture.md).

## Contributing

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). The project **dogfoods its own
skill**: substantive changes are planned, tested, verified, and shipped as a PR with proof. Keep the
eval gate green (`node evals/run.mjs`) and the unit tests passing. Changes are tracked in
[`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE) © 2026 shankar029.

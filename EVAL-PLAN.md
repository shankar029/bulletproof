# Eval Plan — Bulletproof Agent Harness

**Goal:** turn the one-off `benchmark/` into a **repeatable evaluation harness** that continuously
measures whether the `/bulletproof` workflow makes coding agents deliver at top-1% quality — and
that **gates changes to the skill** so it never regresses.

**Status:** proposed
**Seed:** `benchmark/` already implements the core idea (held-out oracle, baseline vs bulletproof
A/B, reproducible runner) for 3 projects. This plan generalizes it.

---

## 1. What we evaluate

The unit under test is the **skill running inside a host agent**: `(agent) × (/bulletproof) × (task)`.
We evaluate the *delivered result and the process*, not the model in the abstract.

Three comparison arms per task:
- **baseline** — host agent, raw task, no skill (attributes the skill's value).
- **bulletproof** — host agent + `/bulletproof`.
- **ablations** — bulletproof with one gate disabled (no-plan, no-e2e, no-review, no-parallel) to
  attribute value to each part of the loop.

## 2. Metrics (what "quality, accuracy, effectiveness" mean, measurably)

| Group | Metric | Source |
|---|---|---|
| **Accuracy** | Held-out oracle pass-rate; `pass@1`, `pass@k` | oracle suites (like `benchmark/`) |
| **Regression** | Pre-existing tests still green; no new failures | fixture repo's own suite |
| **Process adherence** | Produced `PLAN.md`? gates logged? unit+integration+e2e present? evidence bundle? PR on non-main branch? | transcript + workspace scan |
| **Test quality** | Coverage delta on changed files; mutation score (optional); assertion density; no skipped/empty tests | coverage + AST checks |
| **Code quality** | Lint/type/build clean; cyclomatic complexity; duplication; public-API docs | project tooling + static analysis |
| **Tech-debt** | New deps justified; no TODO/dead code/commented blocks; honors existing patterns | detectors + LLM-judge |
| **Safety / guardrails** | Never commits to protected branch; refuses stub/fake tests; no secret/PII in diff or logs | policy checks (hard-fail) |
| **Parallelism** | Only file-disjoint tasks fan out; worktree isolation; integrated re-verify ran | transcript + git introspection |
| **Cost/efficiency** | Tokens, wall-clock, tool calls, $ per task | host-agent telemetry |
| **Robustness** | Asks on genuine ambiguity vs. assumes; handles doc/issue inputs | adversarial tasks |

Composite = weighted blend (accuracy + regression are gates; the rest weighted). Report per-metric,
not just the composite.

## 3. Task suite (the benchmark corpus)

Each task is a self-contained **fixture**: a seed repo + prompt + held-out oracle + scoring config.

```
evals/tasks/<task-id>/
  meta.yaml            # dims: change-type, stack, surface, difficulty, weights
  prompt.md            # the requirement blob (text / doc / issue) fed to the agent
  repo/                # seed project (git-init'd fresh per run)
  oracle/              # held-out acceptance suite (hidden from the agent)
  policy.yaml          # guardrail assertions (no main commit, deps allowlist, ...)
  expected.md          # rubric notes for the LLM-judge
```

**Coverage matrix** (aim ≥ 2 tasks per interesting cell over time):

- **Change type:** greenfield feature · bugfix · refactor (behavior-preserving) · test-backfill · perf.
- **Surface:** HTTP API · CLI · library · **UI (Playwright)** · data/ETL.
- **Stack:** TS/Node · Python · Go · one JVM/.NET (portability of the *skill*, not just one runtime).
- **Difficulty:** trivial · standard · gnarly (concurrency, migrations, backward-compat).
- **Traps (negative tests):** requirement that should be *refused/clarified*; a task solvable
  without a new dependency; a change that must honor an unusual existing convention; a request that
  tempts a protected-branch commit.

v0 already covers: greenfield × {API, CLI, UI} × TS × standard. Expand from there.

## 4. Scoring model

1. **Objective first.** Oracle pass-rate + regression + guardrail policy = the backbone. Guardrail
   violations are **hard fails** regardless of other scores.
2. **Programmatic quality.** Coverage, lint/type/build, complexity, duplication via the project's
   own tooling — no judgment needed.
3. **LLM-judge for the fuzzy parts** (design, readability, tech-debt), with:
   - a fixed rubric + few-shot anchors,
   - **judge validation**: periodically score human-labeled samples; track judge–human agreement;
     use ≥2 judge models and flag disagreement.
4. **Variance:** run each task `N≥5` times; report `mean ± 95% CI` and `pass@k`; mark flaky oracles.

## 5. Harness architecture

```
evals/run.mjs
  for task in suite:
    for arm in [baseline, bulletproof, ablations]:
      workspace = fresh git clone of task/repo         # isolated, sandboxed
      transcript = host_agent.run(arm, task/prompt, workspace, seed)   # via adapter
      scan = collect(diff, new files, PLAN.md, branch, commits, artifacts)
      scores = oracle(workspace) + static_checks + policy(policy.yaml) + judge(expected.md)
      record(results.jsonl, transcript, artifacts)
  aggregate -> report.md + trend.json
```

- **Agent adapters** (pluggable): `pi` (`--prompt-template`/`/skill`), `claude-code` (headless CLI),
  `copilot-cli` (custom agent). Same task, same oracle, different host → **cross-agent matrix**.
- **Sandbox:** each run in a throwaway container/worktree; no network except an allowlist; secrets
  scrubbed; hard wall-clock + token budget per task.
- **Determinism aids:** fixed seeds where the host supports it; pin tool versions; snapshot fixtures.

## 6. Regression gating (CI)

- **On edit to `SKILL.md`/`references/*`:** run a fast **smoke suite** (the v0 corpus) in CI; block
  merge if bulletproof accuracy drops below the last green baseline or any guardrail fails.
- **Nightly:** full suite × all agents; publish `report.md` + a trend chart; alert on regressions.
- The existing `run.mjs` already exits non-zero when a bulletproof arm isn't green — that's the
  seed of the gate.

## 7. Reporting

- `report.md` scorecard (per task, per arm, per agent) + composite + deltas vs. baseline.
- `trend.json` over time → simple dashboard/leaderboard (skill version × agent × score).
- Every run keeps the transcript + workspace diff + E2E artifacts for auditability.

## 8. Phased rollout

- [x] **v0 — seed.** Oracle A/B on 3 projects (API/CLI/UI), reproducible runner. *(done in `benchmark/`)*
- [~] **v1 — corpus + scoring.** Formalize `evals/tasks/` schema; add 8–12 tasks across the matrix;
  programmatic quality metrics; variance runs (`pass@k`).
  - [x] `evals/tasks/<id>/task.json` schema + config-driven runner (`evals/run.mjs`, `evals/lib/score.mjs`)
  - [x] Composite scoring (accuracy + reuse + duplication + extensibility, weighted/renormalized)
  - [x] `report.md` scorecard + deltas + coverage matrix; regression-gate exit; seeded with the 3 v0 tasks
  - [x] Corpus grown to 6 tasks incl. **bugfix** (`paginator`), **refactor** (`shape-area`), **trap** (`uid`)
  - [x] Added a **scope/guardrail** dimension (forbidden-pattern probe) — catches traps that pass on accuracy
  - [x] Corpus at **8 tasks**: added **test-backfill** (`median-backfill`, graded by mutation kill-rate) and a **gnarly** recursive-descent evaluator (`expr-eval`)
  - [x] Corpus at **10 tasks**: added **async concurrency** (`map-limit`, gnarly) and a **stateful refactor** (`order-fsm`)
  - [ ] Grow toward 12 (a non-Node **stack** — needs a runtime/container, ties into v2 sandbox)
  - [ ] `pass@k` / variance (blocked on v2 agent-in-the-loop; arms are fixed artifacts today)
- [~] **v2 — real agent-in-the-loop.** Adapters that actually invoke pi/Claude/Copilot headless on
  the tasks (v0 hand-builds arms; v1.5+ lets the agent build them). Sandbox + budgets.
  - [x] **pi adapter (prototype)** — `evals/agent/` invokes pi headless to produce an arm in an
    isolated workspace, scored by the existing v1 harness; deterministic `--dry-run`, unit tests,
    live A/B on `paginator` (proves the pipeline + that the skill engages: tests + `fix/` branch).
  - [x] `pass@k` / variance: `--runs k` → per-run composite + `mean ± stddev` + clean-rate
    (`stats.mjs`). First trap result (`uid`, k=3): baseline 0.80±0.14 / 33% clean vs bulletproof
    1.00±0.00 / 100% clean — the skill's trap value is consistency. Larger `k` + CIs still wanted.
  - [~] Run the **trap/gnarly** tasks live — `uid` done (skill moves reuse+scope, not accuracy);
    `map-limit` / `expr-eval` / `order-fsm` next.
  - [x] Close the `forbidden`-dep scoring blind spot: check `package.json` direct deps
    (`hasForbiddenDep`), not just arm source. Transitive tooling deps ignored.
  - [ ] Claude Code + Copilot adapters → cross-agent matrix; sandbox hardening + budgets.
- [ ] **v3 — judge + guardrails.** LLM-judge with validation; policy hard-fails; ablation arms.
- [ ] **v4 — CI gating + trend dashboard.** Block skill regressions; nightly cross-agent matrix.

## 9. Risks & limitations

- **Cost:** running real agents × N × arms × agents is expensive → tiered suites (smoke vs. full),
  cache baselines, cap budgets.
- **Oracle overfitting:** if the skill "teaches to the test," rotate/expand held-out tasks and keep
  a private holdout set.
- **Judge bias/non-determinism:** validate against human labels; prefer objective metrics; ensemble.
- **Sandbox safety:** agents run tools — isolate hard (no prod creds, network allowlist, ephemeral FS).
- **Attribution:** single-session A/B (like v0) shows a ceiling; agent-in-the-loop multi-run (v2+)
  gives the honest, variance-aware number.

## 10. Definition of done (for the eval harness itself)
Reproducible `evals/run.mjs` · ≥10 tasks across ≥3 stacks and all surfaces · objective + judge
scoring with validated judge · cross-agent adapters · CI regression gate on skill edits · trend
report. Dogfood: the harness is itself built/verified via `/bulletproof`.

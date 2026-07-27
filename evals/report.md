# Eval Report

_Generated 2026-07-27 · 10 tasks · dependency-free (`node evals/run.mjs`)._

## Scorecard

| Task | Surface | Arm | Accuracy | Reuse | Dup-free | Extensible | Scope | E2E | Test-real | Composite |
|---|---|---|---|---|---|---|---|---|---|---|
| csv-stats-cli | cli | baseline |    0% (0/8) | 0.00 | 1.00 | 0.00 | n/a | 1.00 | 0.00 (tests fail on own code) | **0.21** |
| csv-stats-cli | cli | bulletproof |  100% (8/8) | 1.00 | 1.00 | 1.00 | n/a | 1.00 | 0.94 (15/16) | **0.99** |
| discount-api | api | baseline |   55% (11/20) | 0.00 | 0.00 | 0.00 | n/a | 0.00 | 0.17 (1/6) | **0.22** |
| discount-api | api | bulletproof |  100% (20/20) | 1.00 | 1.00 | 1.00 | n/a | 1.00 | 1.00 (16/16) | **1.00** |
| expr-eval | library | baseline |   38% (5/13) | 0.00 | n/a | n/a | 1.00 | n/a | 0.00 (no tests) | **0.34** |
| expr-eval | library | bulletproof |  100% (13/13) | 1.00 | n/a | n/a | 1.00 | n/a | 1.00 (16/16) | **1.00** |
| map-limit | library | baseline |   71% (5/7) | n/a | n/a | n/a | n/a | n/a | 0.00 (no tests) | **0.57** |
| map-limit | library | bulletproof |  100% (7/7) | n/a | n/a | n/a | n/a | n/a | 1.00 (3/3) | **1.00** |
| median-backfill | library | baseline |   33% (2/6) | n/a | n/a | n/a | 1.00 | n/a | n/a | **0.47** |
| median-backfill | library | bulletproof |  100% (6/6) | n/a | n/a | n/a | 1.00 | n/a | n/a | **1.00** |
| order-fsm | library | baseline |   50% (3/6) | n/a | n/a | 0.00 | n/a | n/a | 0.00 (no tests) | **0.24** |
| order-fsm | library | bulletproof |  100% (6/6) | n/a | n/a | 1.00 | n/a | n/a | n/a | **1.00** |
| paginator | library | baseline |   33% (2/6) | 0.00 | n/a | n/a | n/a | n/a | 0.00 (no tests) | **0.19** |
| paginator | library | bulletproof |  100% (6/6) | 1.00 | n/a | n/a | n/a | n/a | 1.00 (13/13) | **1.00** |
| shape-area | library | baseline |   75% (3/4) | 0.00 | 0.00 | 0.00 | n/a | n/a | 0.00 (no tests) | **0.24** |
| shape-area | library | bulletproof |  100% (4/4) | 1.00 | 1.00 | 1.00 | n/a | n/a | 1.00 (5/5) | **1.00** |
| signup-form | ui | baseline |   43% (3/7) | 0.00 | 1.00 | n/a | n/a | n/a | n/a | **0.39** |
| signup-form | ui | bulletproof |  100% (7/7) | 1.00 | 1.00 | n/a | n/a | n/a | n/a | **1.00** |
| uid | library | baseline |  100% (2/2) | 0.00 | n/a | n/a | 0.00 | n/a | 0.00 (no tests) | **0.32** |
| uid | library | bulletproof |  100% (2/2) | 1.00 | n/a | n/a | 1.00 | n/a | n/a | **1.00** |

## Bulletproof vs. baseline

| Task | Accuracy Δ | Composite Δ |
|---|---|---|
| csv-stats-cli | +100 pts | +0.78 |
| discount-api | +45 pts | +0.78 |
| expr-eval | +62 pts | +0.66 |
| map-limit | +29 pts | +0.43 |
| median-backfill | +67 pts | +0.53 |
| order-fsm | +50 pts | +0.76 |
| paginator | +67 pts | +0.81 |
| shape-area | +25 pts | +0.76 |
| signup-form | +57 pts | +0.61 |
| uid | +0 pts | +0.68 |
| **average** | **+50 pts** | **+0.68** |

## Coverage matrix

| Task | Change type | Surface | Stack | Difficulty |
|---|---|---|---|---|
| csv-stats-cli | greenfield | cli | ts-node | standard |
| discount-api | greenfield | api | ts-node | standard |
| expr-eval | greenfield | library | ts-node | gnarly |
| map-limit | greenfield | library | ts-node | gnarly |
| median-backfill | test-backfill | library | ts-node | standard |
| order-fsm | refactor | library | ts-node | standard |
| paginator | bugfix | library | ts-node | standard |
| shape-area | refactor | library | ts-node | standard |
| signup-form | greenfield | ui | web | standard |
| uid | greenfield | library | ts-node | trap |

## Test-realness (mutation)

The **Test-real** column mutates each arm's *own* implementation and re-runs the arm's *own*
tests: `killed / (killed+survived)` over syntactically-valid single-site mutants (arm ships no
tests, or tests fail on its own code → `0`). Textual engine → some impls (`uid`, `order-fsm`)
yield no mutable operators (`n/a`); equivalent mutants (e.g. `len > 0`→`len < 0`) can survive,
so the gate uses a **0.9** kill-rate bar, not an exact 1.0.

## Deferred to later phases

- **pass@k / variance** — needs real agent-in-the-loop runs (v2); arms here are fixed artifacts (N=1).
- **E2E-with-evidence, process adherence, LLM-judge, guardrail policy, cost** — v2/v3 (see `../EVAL-PLAN.md`).

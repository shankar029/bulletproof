# Eval Report

_Generated 2026-07-27 · 8 tasks · dependency-free (`node evals/run.mjs`)._

## Scorecard

| Task | Surface | Arm | Accuracy | Reuse | Dup-free | Extensible | Scope | Composite |
|---|---|---|---|---|---|---|---|---|
| csv-stats-cli | cli | baseline |    0% (0/8) | 0.00 | 1.00 | 0.00 | n/a | **0.10** |
| csv-stats-cli | cli | bulletproof |  100% (8/8) | 1.00 | 1.00 | 1.00 | n/a | **1.00** |
| discount-api | api | baseline |   55% (11/20) | 0.00 | 0.00 | 0.00 | n/a | **0.28** |
| discount-api | api | bulletproof |  100% (20/20) | 1.00 | 1.00 | 1.00 | n/a | **1.00** |
| expr-eval | library | baseline |   38% (5/13) | 0.00 | n/a | n/a | 1.00 | **0.42** |
| expr-eval | library | bulletproof |  100% (13/13) | 1.00 | n/a | n/a | 1.00 | **1.00** |
| median-backfill | library | baseline |   33% (2/6) | n/a | n/a | n/a | 1.00 | **0.47** |
| median-backfill | library | bulletproof |  100% (6/6) | n/a | n/a | n/a | 1.00 | **1.00** |
| paginator | library | baseline |   33% (2/6) | 0.00 | n/a | n/a | n/a | **0.23** |
| paginator | library | bulletproof |  100% (6/6) | 1.00 | n/a | n/a | n/a | **1.00** |
| shape-area | library | baseline |   75% (3/4) | 0.00 | 0.00 | 0.00 | n/a | **0.30** |
| shape-area | library | bulletproof |  100% (4/4) | 1.00 | 1.00 | 1.00 | n/a | **1.00** |
| signup-form | ui | baseline |   43% (3/7) | 0.00 | 1.00 | n/a | n/a | **0.39** |
| signup-form | ui | bulletproof |  100% (7/7) | 1.00 | 1.00 | n/a | n/a | **1.00** |
| uid | library | baseline |  100% (2/2) | 0.00 | n/a | n/a | 0.00 | **0.40** |
| uid | library | bulletproof |  100% (2/2) | 1.00 | n/a | n/a | 1.00 | **1.00** |

## Bulletproof vs. baseline

| Task | Accuracy Δ | Composite Δ |
|---|---|---|
| csv-stats-cli | +100 pts | +0.90 |
| discount-api | +45 pts | +0.72 |
| expr-eval | +62 pts | +0.58 |
| median-backfill | +67 pts | +0.53 |
| paginator | +67 pts | +0.77 |
| shape-area | +25 pts | +0.70 |
| signup-form | +57 pts | +0.61 |
| uid | +0 pts | +0.60 |
| **average** | **+53 pts** | **+0.68** |

## Coverage matrix

| Task | Change type | Surface | Stack | Difficulty |
|---|---|---|---|---|
| csv-stats-cli | greenfield | cli | ts-node | standard |
| discount-api | greenfield | api | ts-node | standard |
| expr-eval | greenfield | library | ts-node | gnarly |
| median-backfill | test-backfill | library | ts-node | standard |
| paginator | bugfix | library | ts-node | standard |
| shape-area | refactor | library | ts-node | standard |
| signup-form | greenfield | ui | web | standard |
| uid | greenfield | library | ts-node | trap |

## Deferred to later phases

- **pass@k / variance** — needs real agent-in-the-loop runs (v2); arms here are fixed artifacts (N=1).
- **Process adherence, LLM-judge, guardrail policy, cost** — v2/v3 (see `../EVAL-PLAN.md`).

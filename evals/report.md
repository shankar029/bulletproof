# Eval Report

_Generated 2026-07-27 · 3 tasks · dependency-free (`node evals/run.mjs`)._

## Scorecard

| Task | Surface | Arm | Accuracy | Reuse | Dup-free | Extensible | Composite |
|---|---|---|---|---|---|---|---|
| csv-stats-cli | cli | baseline |    0% (0/8) | 0.00 | 1.00 | 0.00 | **0.10** |
| csv-stats-cli | cli | bulletproof |  100% (8/8) | 1.00 | 1.00 | 1.00 | **1.00** |
| discount-api | api | baseline |   55% (11/20) | 0.00 | 0.00 | 0.00 | **0.28** |
| discount-api | api | bulletproof |  100% (20/20) | 1.00 | 1.00 | 1.00 | **1.00** |
| signup-form | ui | baseline |   43% (3/7) | 0.00 | 1.00 | n/a | **0.39** |
| signup-form | ui | bulletproof |  100% (7/7) | 1.00 | 1.00 | n/a | **1.00** |

## Bulletproof vs. baseline

| Task | Accuracy Δ | Composite Δ |
|---|---|---|
| csv-stats-cli | +100 pts | +0.90 |
| discount-api | +45 pts | +0.72 |
| signup-form | +57 pts | +0.61 |
| **average** | **+67 pts** | **+0.74** |

## Coverage matrix

| Task | Change type | Surface | Stack | Difficulty |
|---|---|---|---|---|
| csv-stats-cli | greenfield | cli | ts-node | standard |
| discount-api | greenfield | api | ts-node | standard |
| signup-form | greenfield | ui | web | standard |

## Deferred to later phases

- **pass@k / variance** — needs real agent-in-the-loop runs (v2); arms here are fixed artifacts (N=1).
- **Process adherence, LLM-judge, guardrail policy, cost** — v2/v3 (see `../EVAL-PLAN.md`).

# Benchmark Results

Generated from `node run.mjs` (objective metrics) + measured coverage + rubric.
All numbers are reproducible from the sources in `projects/`.

## Headline

Held-out **oracle acceptance accuracy** (the objective correctness metric):

| Arm | discount-api | csv-stats-cli | signup-form (UI) | **Combined accuracy** |
|---|---|---|---|---|
| baseline | 11/20 (55%) | 0/8 (0%) | 3/7 (43%) | **14/35 = 40.0%** |
| bulletproof | 20/20 (100%) | 8/8 (100%) | 7/7 (100%) | **35/35 = 100%** |

**Effectiveness delta: +60 accuracy points** (40.0% → 100%) on the same specs, same graders.

## Scorecard (objective)

| Project | Arm | Oracle pass | Own tests | Own green | Coverage (line/branch) |
|---|---|---|---|---|---|
| discount-api | baseline | 11/20 (55%) | 1 | 1/1 | 55.9% / 33.3% |
| discount-api | bulletproof | 20/20 (100%) | 20 | 20/20 | 100% / 90.6% |
| csv-stats-cli | baseline | 0/8 (0%) | 1 | 1/1 | n/a — source not unit-testable* |
| csv-stats-cli | bulletproof | 8/8 (100%) | 8 | 8/8 | 93.4% / 82.9% |
| signup-form (UI) | baseline | 3/7 (43%) | — | — | Playwright E2E (no unit tests) |
| signup-form (UI) | bulletproof | 7/7 (100%) | 7 | 7/7 | Playwright E2E + validation logic |

\* The baseline CLI is a top-level script that runs on import, so it can only be tested by
spawning it — its logic gets **no in-process unit coverage**. That untestable structure is itself
a defect the discipline avoids (the bulletproof arm extracts a pure `computeStats`/`parseCsv`).

## Quality rubric (0–5, evidence-based)

| Dimension | base (disc) | bp (disc) | base (cli) | bp (cli) | base (ui) | bp (ui) |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Correctness (oracle-driven) | 3 | 5 | 0 | 5 | 2 | 5 |
| Test depth & coverage | 1 | 5 | 1 | 5 | 0 | 5 |
| End-to-end verification | 0 | 5 | 1 | 5 | 1 | 5 |
| Edge-case & error handling | 1 | 5 | 0 | 5 | 1 | 5 |
| Code quality / maintainability | 2 | 5 | 1 | 5 | 2 | 5 |
| Tech-debt avoidance / DoD | 1 | 5 | 0 | 5 | 1 | 5 |
| **Composite (avg)** | **1.3** | **5.0** | **0.5** | **5.0** | **1.2** | **5.0** |

## What the baseline missed (all caught by the held-out oracle)

**discount-api** (9 oracle failures): no zero-floor (returns negative totals), no money
rounding (`89.991` instead of `89.99`), no input validation (accepts `0`, negative, and
non-numeric subtotals), and no expiry check. Errors are untyped generic `Error`s.

**csv-stats-cli** (8/8 failures): naive `split(',')` corrupts the quoted `"New York, NY"` field
and shifts every column; `parseFloat` on blank/`abc` cells yields `NaN` in the output; trailing
newline miscounts rows; no `--column` support; a missing file crashes with a raw stack trace
(exit 1 but ugly) instead of a clean message.

**signup-form / UI** (4/7 failures): submit button is never disabled; no password length/complexity
rule; no confirm-match check — all three let invalid input reach a fake "success". (The baseline
*does* reject a malformed email, but only by accident: the native `type="email"` constraint blocks
submit, not any real validation logic.) The bulletproof arm disables submit until valid, shows the
first failing rule, and was verified in a **real Chromium browser** (see
`projects/signup-form/oracle/artifacts/success.png`).

The bulletproof arm handles every one of these because the loop forced: enumerating edge cases
in the plan, writing tests for them, and verifying behavior end-to-end before declaring done.

## Interpretation

- **Accuracy:** identical specs, objective third-party tests → **+60 points**. The gap is
  entirely edge cases, validation, and error paths — exactly what undisciplined single-pass work
  skips and what the loop's plan+test+review gates force.
- **Effectiveness:** every bulletproof arm ships real unit + integration + E2E tests that live in
  the repo and pass; both baselines ship one shallow test and no E2E.
- **Quality:** typed errors, extracted pure functions, and input validation make the bulletproof
  code both more correct *and* more maintainable/testable.

## Caveats
Illustrative (single-session A/B) and baseline is naive-by-construction. The UI arm **is** now
live-run in real Chromium (Playwright works on this ARM64 Windows env). See `README.md` →
Limitations. Treat these as the **discipline ceiling** with fully inspectable evidence, not a
controlled human study.

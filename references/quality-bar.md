# Reference: The Quality Bar & Convergence Loop

Passing tests is the floor. The bar is work that fits the project, reuses what exists, is
well-designed and modular, and is easy to change next month.

## The loop
After Phase 6, score the work below. If every required dimension is at or above the bar, all
gates are green, and every acceptance criterion is objectively met — ship. Otherwise list the
specific gaps (dimension, what's wrong, **root cause**), return to the earliest phase that
owns each gap (design flaw → Phase 2; missing edge case → Phase 4/5; smell → Phase 6), fix,
re-run the affected gates, and re-score. Record each iteration in `.ai/<slug>/state.md`.

Repeat until the bar is met, or until you hit a genuine blocker (missing decision, external
dependency, real ambiguity) — then stop and ask with a recommended default. "It mostly works"
and "I ran out of easy ideas" are not stop conditions.

**Bounded effort.** If a dimension is still below the bar after three honest iterations, the
problem is bigger than this task: ship what is green, and record the gap, its root cause, and
the proposed fix as an explicit follow-up. Stopping with a named, visible gap is acceptable;
closing it by lowering the bar or rewording the criterion is not.

**Score it cold.** Judge the diff against the acceptance criteria as if someone else wrote it.
The independent reviewer (fresh session, different model where available — see
`review-and-pr.md`) scores dimensions 1 and 3–9 independently; take the lower of the two
scores when they disagree, and reconcile only with evidence.

## The scorecard (0–5 each; required bar = 4)

| # | Dimension | What "5" looks like |
|---|---|---|
| 1 | **Correctness** | All acceptance criteria and edge cases hold; unit + integration + end-to-end green; no known defect. |
| 2 | **Grounding** | Every symbol, API, config key, and flag used was read and verified in source or docs; nothing invented; assumptions labelled as assumptions. |
| 3 | **Design fidelity & depth** | The design document defines classes, interfaces, and interactions before coding; the implementation matches it; divergences updated the document. Root causes fixed, not symptoms — no band-aids, no ad-hoc patches. |
| 4 | **Scope fidelity** | Exactly what was asked — no gold-plating, no creep, no unrelated edits; larger refactors noted as follow-ups. |
| 5 | **Reuse & DRY** | Searched before writing; reuses existing utilities and abstractions; zero duplicated logic. |
| 6 | **Design & modularity** | Single responsibility, high cohesion, low coupling, clear boundaries; the fitting pattern, not the cleverest; matches the codebase's architecture. |
| 7 | **Extensibility & maintainability** | The next likely change is additive, not invasive; readable, well-named, documented where non-obvious. |
| 8 | **Robustness** | Input validation, error paths, concurrency, security, and performance considered and handled. |
| 9 | **Test quality & evidence** | Meaningful unit + integration + end-to-end; covers branches and failure modes; no skipped, empty, or tautological tests; coverage met; evidence bundle assembled and environment-blocked proof named explicitly. |

Dimensions 1, 2, and 9 are hard gates — a failure blocks shipping regardless of the average.

**Metrics outrank opinion.** Where `metrics.json` provides a number for a dimension (see
`quality-metrics.md`), a score of ≥4 **must cite it** — duplication delta for Reuse, complexity
and cycles for Design, static findings for Robustness, mutation score and diff coverage for
Test quality. No number, no score: mark it unverified and go measure. If a metric is genuinely
`unavailable`, say so in the scorecard rather than implying a measurement you didn't take.
Score specifically: cite the file or line justifying any score below 5.

## Judging the deeper dimensions
- **Grounding:** for every non-obvious claim in the design, the code, or the report, can you
  name the file you read that supports it? An API used but never opened is a ≤2 — go read it.
- **Design fidelity:** compare the diff against the design document type by type. Code that
  quietly took a different shape, or a fix that adds a conditional around a symptom instead of
  correcting the cause, is a ≤2 regardless of green tests.
- **Scope fidelity:** the diff touches only what the task implies. Then re-check the
  acceptance criteria themselves against the original request — a dropped or misread
  requirement is a gap even when every listed criterion passes.
- **Reuse:** logic that duplicates an existing utility is a ≤2; replace it with the existing one.
- **Design:** would a senior engineer on *this* repo approve the shape — responsibilities,
  dependency direction, and whether the abstraction matches the domain?
- **Extensibility:** if adding a new case means editing a growing conditional in the core,
  that's a ≤3; prefer a seam that makes new cases additive.

## Anti-gaming rules
- Never lower a threshold, delete or skip a test, or weaken an assertion to pass.
- Never score a dimension at the bar without evidence; when unsure, score lower and fix.
- Never state as fact anything you have not verified in the source or the tool's own docs.
- **Never refactor solely to move a metric**, and never exclude a file or rule from a tool's
  scope to make one pass. A number that improves while the design gets worse is a failure.
- Fix root causes, not symptoms — no special-casing over a design flaw, no defensive
  conditionals that hide it, no retries around a bug.
- Reuse over rewrite; extend over duplicate; the smallest correct change over the cleverest.

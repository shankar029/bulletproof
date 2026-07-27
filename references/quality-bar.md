# Reference: The Top-1% Quality Bar & Convergence Loop

Passing tests is the floor, not the bar. A top-1% engineer also delivers work that fits the
project, reuses what exists, is well-designed, and is easy to change next month. This file defines
the **scored bar** and the **loop that runs until the bar is met**.

## The convergence loop

The five phases are not a single pass. After Phase 5, **score the work against the rubric below**,
then:

1. If **every required dimension is ≥ 4/5**, all gates are green, and **every acceptance criterion
   is objectively met** → done. Ship.
2. Otherwise, list the **specific gaps** (dimension, what's wrong, root cause), return to the
   **earliest phase that owns the gap** (a design flaw → Phase 2; a missing edge case → Phase 3/4;
   a smell → Phase 5), fix it, re-run the affected gates, and **re-score**.
3. Repeat until (1) holds — or you hit a **genuine blocker** (missing decision, external
   dependency, real ambiguity). Then stop and ask, with a recommended default. Never stop merely
   because "it mostly works."

Track each iteration in `PLAN.md` (what scored low, what you changed, new score). Convergence, not
a single attempt, is the deliverable.

## The scorecard (score each 0–5; required bar = 4)

| # | Dimension | What "5" looks like |
|---|---|---|
| 1 | **Correctness & accuracy** | All acceptance criteria + edge cases hold; unit + integration + E2E green; no known defect. |
| 2 | **Scope fidelity** | Does exactly what was asked — no gold-plating, no scope creep, no unrelated edits. Larger correct refactors are noted as follow-ups, not smuggled in. |
| 3 | **Reuse & DRY** | Reuses existing functions, utilities, and abstractions; searched before writing; zero duplicated logic. |
| 4 | **Design & principles** | SOLID, high cohesion, low coupling, clear boundaries; the right (not the cleverest) pattern; matches the codebase's architecture. |
| 5 | **Extensibility & maintainability** | Open/closed where change is likely (new cases added via data/config/strategy, not by editing core); readable; well-named; documented where non-obvious. |
| 6 | **Robustness** | Input validation, error paths, concurrency, security (authz, injection, secrets), and performance all considered and handled. |
| 7 | **Test quality** | Meaningful unit + integration + E2E; covers branches and failure modes; no skipped/empty/tautological tests; coverage meets the bar. |
| 8 | **Verification & evidence** | Proven end-to-end like a human; evidence bundle (tests, coverage, E2E artifacts, review notes) assembled. |

Dimensions 1 and 8 are **hard gates** (a failure blocks shipping regardless of the average).
Score honestly and specifically — cite the file/line that justifies each score below 5.

## How to judge the "deeper" dimensions (not just tests)

- **Scope fidelity:** diff only touches files the task implies; no new dependency unless required
  and justified; no features nobody asked for. Compare the change against the acceptance criteria —
  anything extra is scope creep, anything missing is a gap.
- **Reuse & DRY:** before writing a helper, grep the repo for one that exists. If you wrote logic
  that duplicates an existing utility (rounding, validation, HTTP responses, date handling), that's
  a ≤2 — replace it with the existing one.
- **Design & principles:** would a staff engineer on this repo approve the shape? Check single
  responsibility, dependency direction, and whether the abstraction matches the domain.
- **Extensibility:** ask "what's the next obvious change, and how invasive is it?" If adding a new
  case means editing a big `switch`/`if` chain in the core algorithm, that's a ≤3 — prefer a
  data/registry/strategy seam so new cases are additive (open/closed).

## Anti-gaming rules (non-negotiable)

- Never lower a threshold, delete/skip a test, or weaken an assertion to "pass."
- Never mark a dimension ≥4 without evidence; when unsure, score lower and fix.
- Fix **root causes**, not symptoms — no patching over a design flaw with special-cases.
- Reuse over rewrite; extend over duplicate; the smallest correct change over the biggest clever one.

## Stop conditions
Converge when the bar is met. Stop early only for a **genuine blocker** (ask, with a recommended
default) or when further iteration would exceed scope (record the remainder as explicit
follow-ups). "Ran out of easy ideas" is not a stop condition — escalate the effort, not the bar.

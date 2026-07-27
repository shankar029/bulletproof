# Test-realness dimension — plan

**Goal:** Score whether an arm's *own* tests are real (catch bugs), not just whether the
held-out oracle passes. Generalize `median-backfill`'s mutation-kill-rate idea to every code task.

**Status:** done — shipped. `testQuality` scored across the corpus; baseline's missing tests now
visible (0 on 6/10); real gaps in two bulletproof suites found + fixed; 0.9 gate; v2 wired.

## Idea
For each arm: mutate the arm's **own implementation** and re-run the arm's **own tests**.
- No arm tests → `testQuality = 0` (baseline usually writes none — that's the signal).
- Arm tests don't pass on the arm's own unmutated code → `0` (tests are broken/fake).
- Otherwise `testQuality = killed / (killed + survived)` over syntactically-valid mutants.
  A weak/shallow suite lets mutants survive.

## Safety
Never mutate committed fixtures in place. Copy `{armDir, ../shared}` into a temp mirror
(same layout so `./index.ts` and `../shared/*.ts` resolve), mutate + run there, delete.

## Mutation operators (textual, one site per mutant, capped)
Arithmetic ` + `↔` - `, ` * `↔` / ` · relational `<=`↔`<`, `>=`↔`>`, `<`↔`>`, `===`↔`!==` ·
logical `&&`↔`||` · boolean `true`↔`false`. Each occurrence → one mutant. Cap ~16/arm for runtime.
Mutants that fail to load (tests==0) are **skipped** (compile error ≠ kill) to avoid inflating rate.

## Steps
- [x] A. `evals/lib/mutate.mjs`: pure `generateMutants(src,{max})`; unit tests.
- [x] B. `runTestQuality()` in `score.mjs`: temp-copy, green-baseline check, mutate+run, kill-rate.
- [x] C. `testQuality` in `toDimensions`; add weight to each applicable task.json (rebalanced);
      wire into `run.mjs` output. Opt-out for `signup-form` (HTML) + `median-backfill` (already
      mutation-graded).
- [x] D. Measure: `node evals/run.mjs`. Expect baseline≈0 (no tests) vs bulletproof high. Record.
- [x] E. Gate policy (advisory vs hard) based on real numbers; docs (README/CHANGELOG/EVAL-PLAN).

## Risk
- Equivalent/non-compiling mutants → skipped, not counted (conservative; won't inflate).
- Runtime: ~cap×arms×tasks extra `node --test` runs (~minutes). Cap keeps it bounded.
- Gate: if committed bulletproof suites don't kill all mutants, surface honestly — don't hide.

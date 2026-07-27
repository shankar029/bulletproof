# SPEC — Median (test-backfill)

`subject.ts` ships a working `median(nums: number[]): number`. It has **no tests**. Backfill a
regression suite that pins its behavior and would catch a future regression.

## The subject's contract
- Returns the middle value of the numerically-sorted list (odd length) or the average of the two
  middles (even length).
- Sorts **numerically**, not lexicographically.
- Must **not mutate** the caller's array.
- Throws on an empty list.

## How this is graded (held-out oracle)
Mutation testing. The oracle runs your suite against:
1. the correct `subject.ts` — every test must **pass**, and
2. five planted **mutants** (`mutants/*.ts`) — your suite must **fail** on each (kill it).

Accuracy = fraction of (correct-run + each-mutant-killed) satisfied. A happy-path-only suite leaves
most mutants alive; a suite that covers even/odd length, ordering, input-immutability, and the empty
case kills them all.

## Guardrail
No skipped or focused tests (`.skip`, `.only`).

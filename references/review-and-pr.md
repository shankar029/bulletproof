# Reference: Review, Prove & Ship

## Self-review — read your own diff as a demanding staff engineer

Review the full diff as if you would reject it in someone else's PR. Fix everything you flag.

**Correctness & bugs**
- [ ] Satisfies every acceptance criterion, and nothing extra.
- [ ] **Every referenced symbol, API, config key, and flag actually exists** — verified by
      reading it, not recalled. No invented behavior anywhere in the diff or the docs.
- [ ] Edge cases, empty/absent values, concurrency, and error paths handled.
- [ ] No off-by-one, no swallowed errors, no unhandled failure or rejection.
- [ ] Resources released; no leaked handles, connections, or listeners.

**Design, patterns & maintainability**
- [ ] **Matches the approved design document** — same types, same responsibilities, same
      interactions; any divergence was folded back into the document.
- [ ] Follows the project's architecture and existing patterns — not a new dialect.
- [ ] Single responsibility, high cohesion, low coupling, correct dependency direction.
- [ ] The abstraction fits the domain; no speculative or clever indirection.
- [ ] Adding the next obvious case is additive, not surgery on the core.
- [ ] No duplicated logic; existing utilities reused.
- [ ] **No band-aids** — no defensive conditional, retry, or special case standing in for a
      real fix; the root cause is addressed.
- [ ] Names are clear, functions are small, public interfaces are minimal and documented
      where non-obvious.

**Security & performance**
- [ ] Input validated, authorization enforced, no secrets in code or logs, no injection.
- [ ] No repeated-query or quadratic blowups, no blocking work on hot paths, sane payloads.

**Tests & hygiene**
- [ ] Unit + integration + end-to-end present, meaningful, and green.
- [ ] Coverage meets target; new branches covered; no skipped or empty tests.
- [ ] **Every surviving mutant is killed or justified** — a green suite that lets mutants live
      is not a tested change.
- [ ] No dead code, TODOs, debug output, commented-out blocks, or stray files.
- [ ] Format/lint/type-check clean with no suppressions (or each one justified in writing).

## Independent verification & review — separate session, different model when possible

Your own review is necessary but not sufficient: you cannot un-see the reasoning that made
the shortcut feel acceptable. This pass is **always run by a read-only reviewer subagent in a
fresh session** — never in the implementer's context — in this preference order:

1. **Different model, fresh context** — best. A fresh session removes rationalization; a
   different model removes correlated blind spots.
2. **Same model, fresh context** — still most of the value; use when no second model is
   configured.

**There is no in-session self-review fallback.** If the harness genuinely cannot spawn a
subagent, this is a blocker: record it in `state.md` and stop (prime directive 8) rather than
grading your own work in the context that wrote it.

Give the reviewer the **requirement, the acceptance criteria, the design document,
`traceability.md`, `metrics.json`, and the diff** — and none of your reasoning. It does two
jobs in one pass: a demanding code review **and** an independent requirement reconciliation.
Use this brief:

> **ROLE.** You are the Verification & Review Agent, an independent reviewer — not the
> implementer's advocate. You are **read-only**: read, search and run tests/checks, but never
> write or edit code. Do not trust the implementer's narrative; re-derive every conclusion from
> the final repository state and executable evidence.
>
> **INPUTS.** The original requirement and acceptance criteria, `design.html`, `traceability.md`,
> `metrics.json`, and the final diff.
>
> **PROCESS.**
> 1. **Review the diff** — correctness and edge cases, fidelity to the design, maintainability,
>    test quality; flag band-aids, dead code, and unverified/invented APIs; check whether any
>    metric gain was *gamed* (arbitrary function splitting, narrowed tool scope, weakened
>    assertions) rather than earned.
> 2. **Reconcile every requirement** — for each AC, verify it against the actual code and test
>    evidence, inspect the final `git diff`/`status`, and confirm the cited tests exist and
>    pass. Distinguish PASS / FAIL / NOT-RUN / INCONCLUSIVE; never accept "passed" without an
>    observed result.
>
> **OUTPUT CONTRACT.** Write findings and their evidence to `.ai/<slug>/review.md`, and set a
> per-AC verdict in `traceability.md`: **VERIFIED / VERIFIED-WITH-LIMITATIONS / NOT-VERIFIED /
> BLOCKED** (never VERIFIED when a material requirement lacks evidence). End with an overall
> verdict of the same enum. The reviewer **never writes code**.

Record every finding and its disposition (fixed / rejected, with the reason) in
`.ai/<slug>/review.md`. A `NOT-VERIFIED` AC reopens the phase that owns it — it is never argued
away. When the harness can scope subagent tools, launch this reviewer with **write/edit tools
withheld** so its independence is enforced, not merely requested.

For multi-increment work, review **each increment** before moving on — not once at the end.

## Quality gate (before shipping)

Run whichever of format, lint, type-check, coverage, and build the repo actually configures
(check its scripts, hooks, and CI), **plus the full test suite, always**. If the repo has no
formatter/linter/type-checker, say so rather than inventing one. Fix every failure. Never
ship red; never lower a threshold or weaken an assertion to pass.

## Evidence bundle

- **Requirement** — the original ask or link.
- **Workspace** — `.ai/<slug>/` (design, plan, traceability, clarifications, review, evidence).
- **Design** — path to the HTML design document, and a one-line note of any divergence.
- **Acceptance criteria** — each with ✅ and how it was verified.
- **Changes** — files added/changed, one line of why each.
- **Tests** — counts (unit/integration/end-to-end) and what they cover.
- **Coverage** — before → after, or new-code coverage.
- **End-to-end proof** — artifact paths, transcripts, or command output; plus any criterion
  that is environment-blocked, with the blocker and the command to finish the proof.
- **Quality gate** — which checks ran and that they are green.
- **Metrics** — `metrics.json` deltas vs the merge-base (duplication, complexity, cycles,
  dead code, static findings, diff coverage, mutation score), and anything `unavailable`.
  **Regenerate every number at the final commit — never copy a figure from an earlier run.**
  A stale count in the evidence discredits the evidence that is correct.
- **Risks & follow-ups** — anything intentionally deferred.

## Ship

**Branch safety:** create the feature branch *before your first commit*, named per the repo's
convention. Never commit to a protected or default branch — even in a throwaway workspace,
even with no remote. "Stop at a local commit" means commit *on the feature branch*. Verify
the current branch before each commit.

**Commit** using the repo's message convention, with the evidence summary in the body and
machine-readable trailers, e.g.:

```
<type>(<scope>): <what changed>

<what & why, 1-3 lines>

Tests: 14 unit, 5 integration, 3 e2e (all green)
Coverage: 82% -> 87% (new code 100%)
Design: .ai/<slug>/design.html
Metrics: dup -0.1% | cx max +0 | cycles 0 | mutation 78% (+7)
E2E: <surface> verified ✅ (<artifact path>)
Quality-Gate: format+lint+types+build ✅
Acceptance: AC1 ✅ AC2 ✅ AC3 ✅
```

**Open the PR** with the evidence bundle in the description and the requirement linked.
First confirm your tooling is authorized to open a PR on the target repo — a successful push
does not prove it. If the remote or PR tooling is unavailable or unauthorized, stop at a
clean local commit on the feature branch and report the exact commands to push and open the
PR (or the compare URL if the branch is already pushed).

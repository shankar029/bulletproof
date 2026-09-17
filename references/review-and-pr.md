# Reference: Review, Prove & Ship

## Self-review — read your own diff as a demanding staff engineer

Review the full diff as if you would reject it in someone else's PR. Fix everything you flag.

Use separate finding categories within the existing review: **SPEC** (missing, incorrect or
unrequested behavior; cite the AC), **STANDARD** (a binding repository rule; cite it), and
**DESIGN CONCERN** (a reasoned maintainability heuristic; cite the code and concrete cost).
A smell is not automatically a rule violation; repository conventions override generic
preferences. Keep requirement and quality verdicts visible so one cannot mask failure of the
other. Deduplicate findings across categories and prioritize by impact; do not add reviewers
merely to produce separate categories. Use existing tooling results instead of repeating
lint findings, while still resolving gate failures.

Pin the review base and head/source snapshot before reviewing. Include relevant staged,
unstaged and untracked changes in a work-in-progress review; a committed three-dot diff alone
cannot establish coverage of a dirty worktree. Reconcile the final tree again before shipping.

**Correctness & bugs**
- [ ] Satisfies the current increment's due AC scenarios and affected prior regressions;
      final ship satisfies every AC, and nothing extra.
- [ ] **Every referenced symbol, API, config key, and flag actually exists** — verified by
      reading it, not recalled. No invented behavior anywhere in the diff or the docs.
- [ ] Edge cases, empty/absent values, concurrency, and error paths handled.
- [ ] No off-by-one, no swallowed errors, no unhandled failure or rejection.
- [ ] Resources released; no leaked handles, connections, or listeners.

**Design, patterns & maintainability**
- [ ] **Matches the approved design document** — same types, same responsibilities, same
      interactions; any divergence was folded back into the document.
- [ ] Plan/task completion matches the actual changes and check evidence; deviations follow
      `planning.md`'s revision protocol, including affected dependencies and approvals.
- [ ] Follows the project's architecture and existing patterns — not a new dialect.
- [ ] Single responsibility, high cohesion, low coupling, correct dependency direction.
- [ ] The abstraction fits the domain; no speculative or clever indirection.
- [ ] Adding the next obvious case is additive, not surgery on the core.
- [ ] Shared business rules and integration mechanics are not duplicated; existing utilities
      reused for the same responsibility and contract.
- [ ] **No band-aids** — no defensive conditional, retry, or special case standing in for a
      real fix; the root cause is addressed.
- [ ] **Human-readability contract (`code-clarity.md`) met:** the main flow, failure paths,
      state ownership and side effects are traceable; names explain behavior; extractions
      separate responsibilities rather than merely shortening functions.
- [ ] Shared integration types and behavior are consistent; no repeated casts or fallback
      chains substituting for a clear boundary.
- [ ] Comments describe current behavior and necessary rationale, not dated change journals
      or superseded rules. Required documentation and runtime prompt/tool contracts preserved.

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
the plan and linked task/check records, `traceability.md`, `metrics.json`,
`references/code-clarity.md`, and the diff** — and
none of your reasoning. It does two
jobs in one pass: a demanding code review **and** an independent requirement reconciliation.
Use this brief:

> **ROLE.** You are the Verification & Review Agent, an independent reviewer — not the
> implementer's advocate. You are **read-only**: read, search and run tests/checks, but never
> write or edit code. Do not trust the implementer's narrative; re-derive every conclusion from
> the final repository state and executable evidence.
>
> **INPUTS.** The original requirement and acceptance criteria, `design.html`, `traceability.md`,
> `plan.html` and linked task/check records, `metrics.json`, `references/code-clarity.md`,
> and the final diff.
>
> **PROCESS.**
> 1. **Review the diff** — correctness and edge cases, fidelity to the design, maintainability,
>    test quality; flag band-aids, dead code, and unverified/invented APIs; check whether any
>    metric gain was *gamed* (arbitrary function splitting, narrowed tool scope, weakened
>    assertions) rather than earned.
>    Apply `code-clarity.md`'s review acceptance to changed code and tightly coupled problems.
>    Cite a location, concrete maintenance cost, and proportionate remedy for each readability
>    finding. Check for stale comments and inline history as well as overloaded responsibilities
>    and duplicated integration mechanics. Record findings here, not in a separate report;
>    do not impose arbitrary size limits or launch unrelated cleanup.
>    Classify findings as SPEC, STANDARD or DESIGN CONCERN using the rules above. Show both
>    requirement and quality outcomes; verify that the supplied diff covers the current tree,
>    including relevant uncommitted content. A missing specification is a verification gap,
>    not permission to silently skip requirement reconciliation.
> 2. **Reconcile every requirement** — for each AC, verify it against the actual code and test
>    evidence, inspect the final `git diff`/`status`, and confirm the cited tests exist and
>    pass. Distinguish PASS / FAIL / NOT-RUN / INCONCLUSIVE; never accept "passed" without an
>    observed result.
>    At intermediate reviews, judge due scenarios and affected previously delivered regressions;
>    record future ACs as NOT-VERIFIED (planned), not failures of earlier slices. For spanning
>    ACs, record task/check proof without a premature VERIFIED verdict. Final review covers all ACs.
> 3. **Reconcile the execution plan** — compare owned changes, completion checkboxes and
>    expected outcomes with the final tree and recorded results. Confirm deviations were
>    reflected in affected tasks/ACs and approvals; human-owned checks require human confirmation.
>
> **OUTPUT CONTRACT.** Write findings and their evidence to `.ai/<slug>/review.md`, and set a
> per-AC verdict in `traceability.md`: **VERIFIED / VERIFIED-WITH-LIMITATIONS / NOT-VERIFIED /
> BLOCKED** (never VERIFIED when a material requirement lacks evidence). End with an overall
> verdict of the same enum. The reviewer **never writes code**.
> If artifact writes are withheld, return the complete report and exact verdict updates for the
> parent to persist unchanged and verify; do not bypass tool restrictions through shell writes.

Record every finding and its disposition (fixed / rejected, with the reason) in
`.ai/<slug>/review.md`. An unmet **due** AC/scenario reopens the phase that owns it — it is
never argued away; future planned work does not deadlock the current increment.
Keep implementation/source writes withheld. When path-scoped permissions exist, allow only the
assigned review/traceability artifact writes; otherwise have the parent persist the full returned
report and verdicts unchanged, verify their locations, and record dispositions separately.
Persistence by the parent does not transfer the independent review judgment to the implementer.

For multi-increment work, review **each increment** before moving on — not once at the end.

## Quality gate (before shipping)

For adopted work, resolve `current-design.json` and compare the retained current contract,
actual `status` and immutable receipts with the tree. Follow
[workflow-gates.md](workflow-gates.md) for admitted independent handoffs and returned evidence;
reviewer, verifier and implementer remain distinct contexts, not authenticated identities.
Check earlier red/compatibility consumption, research supersession and scoped reopening,
not just the final green command. Historical design/review artifacts cannot backfill approval.

After precommit proof and a matching feature commit, ordinary `close` checks actual Git
membership/bytes/modes and mandatory gates; inspect the returned result. Positive quality
closure is currently unavailable because guarded metric attachment lacks its producer bridge.
Keep all nine metrics required. Local functional preservation is not a closed increment or
ship pass. There is no recovery/reset/lock-steal path for uncertain process lifetime.

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
  Read version-2 `measurement_status` and `completeness` separately. Required unavailable,
  unsupported or stale proof blocks the gate; a latest alias or an `ok` partial observation
  is not a complete pass. Cite the current run ID, source binding and missing prerequisites.
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

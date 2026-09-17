# C1 separate code review

Reviewer: `bbe59c68-4708-4952-8f3d-7d91551302dc`, distinct from implementation
and verification. The following return is preserved separately from parent
disposition. No independent review approval is inferred from passing tests.

## Original reviewer return

# Bounded review: REVISE

**C1 functional acceptance: NOT-VERIFIED. Current-dependency acceptance: BLOCKED.**
**Live-bundle / portable-README integration: APPROVE, with the limitations below.**

Three C1 findings require correction. The original F1–F3 fixes address their reported mechanisms, but the focused review reproduced two additional false-readiness cases and measured exponential closure-evaluation growth.

No repository code, tests, evidence, shared state or session artifacts were written. No agents, installations, commits, publication, mutation or quality collection were performed. Probes used only cleaned, privately owned temporary fixtures and in-memory records.

Reviewed branch: `shbs-microsoft-workflow-app-verification`
HEAD: `015d353e9cf8fa3b57a561f808cdcd04cfe786e7`

## Findings

### C1-CR-R1 — High: receipt-supplied rule mode bypasses mandatory regression policy

**Location:** `scripts\workflow_gate.py:107–135`, particularly **128–134**; policy validation at `scripts\workflow_state.py:570–586`.

The gate verifies that required metric names exist, but lets the receipt choose each metric’s interpretation. A rule with `mode="floor"` or `"coverage"` bypasses the existing `judge()` comparison. The policy SHA only establishes consistency with that supplied policy; it does not establish that its rules preserve the required policy.

**Reproduced through real fixture persistence, loading and evaluation:**

1. Complete A’s work.
2. Produce an otherwise-valid synthetic A-metrics receipt.
3. Set `cycles.base=0`, `cycles.head=5`.
4. Replace the cycles rule with `mode="floor", threshold=0` and recompute the policy SHA.
5. Require A-metrics before B-work.

Observed:

```text
judge("cycles", 0, 5, False) -> fail
A-metrics proof             -> valid
A-metrics readiness         -> complete
B-work readiness            -> ready
B-work next_command         -> populated
B-work blockers             -> []
```

The receipt and its policy pass the strict persisted schemas. No authentication, sandbox or actual collector guarantee is needed to detect this contradiction: the gate already has the applicable comparison function.

**Impact:** a required no-new-cycle rule becomes a minimum-value rule. This can authorize dependent work despite a measured regression. The same branch permits other comparison metrics to escape their intended comparison semantics.

**Minimal correction:** enforce the mandatory metric-specific comparison semantics independently of receipt-supplied rule modes. Additional floors must not replace mandatory comparisons. Validate any configurable tightening against an authoritative policy rather than merely its self-consistent hash. Add negative coverage for rule-mode substitution and positive coverage for legitimate policies. This must be fixed in C1’s acceptance boundary, not deferred entirely to C2’s report projection.

### C1-CR-R2 — High: passing metric/finding receipts override failed command completion

**Location:** `scripts\workflow_gate.py:307–319`, with the inconsistent execution check at **199–208** and check-proof routing at **321–335**.

`_receipt()` requires a matching spawned completion, but only passes its exit code to `_native_result()`. Metric and finding validators receive no completion outcome/exit information.

`_execution()` separately rejects unsuccessful execution, but `check()` does not apply that validation to the check’s own action. Consequently, a direct check prerequisite can pass while the command that produced it is recorded as failed.

**Reproduced with ordinary `WorkflowFixture.receipt(..., code=...)`, without rewriting ledger history:**

| Receipt kind | Recorded exit | Completion outcome | Check status | Dependent B-work |
|---|---:|---|---|---|
| Metrics — positive control | 0 | executed | complete | ready |
| Metrics | 1 | fail | **complete** | **ready** |
| Metrics | 124 | fail | **complete** | **ready** |
| Review | 1 | fail | **complete** | **ready** |
| Native test — negative control | 1 | fail | ready for retry, not complete | blocked |

The failed metric/review cases returned a populated B-work `next_command`.

These are synthetic protocol records exercising real library/persistence APIs. The exit-124 case is a **timeout-code contradiction**, not a claim that this review ran a live timed-out producer.

**Impact:** a failed producer that wrote a passing-looking result before failing can satisfy a registered prerequisite. Increment-member execution checks may still block closure; they do not protect direct check-dependent action admission.

**Minimal correction:** reconcile command completion outcome and exit semantics before accepting metric or finding proof. Require successful command completion for these command-backed checks. Preserve null-command handoffs and the explicitly validated behavioral-red exception. Add failed/nonzero/timeout-code controls for direct consuming actions, not only increment closure.

This is adjacent to, but distinct from, original F2: **no-spawn success is fixed; failed spawned-command success remains possible.**

### C1-CR-R3 — Medium: recursive prefix evaluation grows exponentially

**Location:** `scripts\workflow_gate.py:365–380`, especially **376–378**, and invocation at **395–410**.

Every closure-prefix validation constructs a new `_Evaluation` with a fresh memo. Its prerequisite closures recursively construct further evaluators, repeating already-evaluated `(target, ledger-prefix)` work.

**Measured bounded probe:**

- Linear increment dependency chain.
- Each increment: one work action plus test, verification, review and metrics actions.
- Earlier increment closure and cumulative exact receipt references required by the next.
- Validated contract, ledger, receipts and materialized snapshots.
- Actual `evaluate()` execution; no replacement proof algorithm.
- A constructor wrapper counted instances while delegating unchanged behavior.

| Increments | Actions | Ledger events | Evaluator instances | Evaluation seconds |
|---:|---:|---:|---:|---:|
| 3 | 15 | 91 | 8 | 0.018 |
| 5 | 25 | 151 | 32 | 0.050 |
| 8 | 40 | 241 | 256 | 0.307 |
| 10 | 50 | 301 | 1,024 | 1.268 |
| 12 | 60 | 361 | 4,096 | **7.134** |

All evaluated targets returned `complete`. Fixture construction was outside the timed evaluation.

The probe stopped after exceeding its five-second continuation threshold. **No larger-chain timeout was measured.** The observed instance counts follow `2^n` for this construction; worsening cost beyond the measured range is an algorithmic inference, not an observed timeout claim.

**Impact:** a modest multi-increment workflow already spends seconds evaluating a few hundred events, before CLI integration or filesystem materialization. Larger session-sized plans make authoritative status/admission increasingly impractical.

**Minimal correction:** share memoized proof results within one public evaluation, keyed by target and the relevant ledger-prefix boundary, or use an equivalent bounded dynamic evaluation. Keep snapshots fixed to that evaluation and retain exact-reference chronology. Do not replace this with a global cache or weaken F1’s prefix checks. Add a deterministic work-count/scaling regression plus the existing chronology/reclosure controls.

## Original F1–F3 adjudication

| Prior finding | Review assessment |
|---|---|
| **F1: closure chronology and exact references** | The root correction is sound for the inspected cases: `closure_proven_before()` evaluates earlier dependencies and compares their exact receipt ID/hash union to the closure. Current freshness and reference checks remain. The direct, handoff, transitive, inherited-increment and ship regression assertions cover the reported substitution defect. **R3 concerns its evaluation cost, not a reproduced reopening of the original chronology bug.** |
| **F2: successful no-spawn completion** | `_process`, `validate_ledger` and `completed()` now reject the reported contradiction while preserving honest failed launches and handoffs. **Original defect resolved within the reviewed protocol boundary.** R2 identifies a different failed-command acceptance gap. |
| **F3: naive “UTC-looking” timestamps** | `_time()` now checks parsed timezone awareness and zero UTC offset. The accepted/rejected timestamp matrix and receipt/metric timestamp controls directly address the defect. **Resolved for the inspected boundary.** |

The r3 **75 workflow + 10 evidence** pass remains its historical independent result. It does not cover the newly reproduced counterexamples or establish current dependency freshness after the change noted below.

## Six integration interpretations

1. **Repository-relative receipt and assertion identities — ACCEPT.**
   Receipt placement, traversal/link rejection and relative assertion identities form a consistent internal contract. C1 does not prove raw native-producer interoperability.
2. **Component-ID → normative JSON-value contract map — ACCEPT.**
   `_load_design()` verifies retained contract bytes and canonical hashes of each component value. This supports selective component freshness without creating another dependency graph.
3. **Hashed unattended-authorization reference — ACCEPT WITH LIMITS.**
   `{path, sha256}` is a reasonable resolution of “reference”; absence or changed bytes blocks unconfirmed design adoption. It binds an artifact, not authenticated authorization or human approval. `human_approval=unconfirmed` must remain explicit.
4. **C2 native absolute-path normalization — ACCEPT AS REQUIRED FUTURE INTEGRATION, NOT VERIFIED.**
   C2 must normalize actual producer identities against the correct repository/workspace boundary while preserving raw artifacts. It needs real producer positive/negative tests. Do not loosen C1 assertion matching merely to accept arbitrary paths.
5. **Explicit strict legacy metric projection — ACCEPT THE APPROACH; IMPLEMENTATION NOT VERIFIED.**
   Standalone `default_policy()` and report shapes are not directly the strict r2 receipt shapes. C2 needs an explicit, validated projection preserving original evidence and admitted run/source identity—not generic field dropping, historical import or relabelled green. **R1 and R2 are existing C1 validation defects, not excused by that future projection.**
6. **Actual Git/branch/source-close validation and recovery remain C2 — ACCEPT.**
   C1 checks structural commit syntax and conservative protocol facts; it does not inspect actual completion commits, dispatch commands, authenticate process identity or prove tree termination. These are properly deferred responsibilities, not reasons to reject the bounded design.

Also accepted: requested-target materialization failure is an input error, while prerequisite materialization failure becomes a blocked observation. C2 must preserve those conservative outcomes.

## Parent live-bundle and portable-README integration

**APPROVE for this bounded diff. No blocking production defect found.**

- `workspace.mjs` exports the helper used by `live.mjs`.
- It copies all four intended payloads: `SKILL.md`, `references`, `scripts`, `assets`.
- Failed staging removes only the newly allocated staging directory; successful staging remains caller-owned.
- Tests check payload bytes, an actual copied sibling-module import and partial-failure cleanup.
- Both prompts receive the same `.ai/` task-record allowance while retaining deliverable/seed instructions. This is a prompt contract, not sandbox enforcement.
- The root Markdown hero preserves the image, alt text, value statement and navigation without requiring raw-HTML support.
- The new harness README paragraph accurately distinguishes tool availability and dry-run plumbing from agent adoption or gate completion.

**Own replay:** `node --test evals\agent\agent.test.mjs` passed **21/21**, zero failures, skips, cancellations or todos, exit 0. Thirteen pinned harness/library/document files were unchanged across that run.

The supplied **65-test integrated native**, **ten-task/79-assertion corpus**, and reference-copy dry-run results were reviewed as recorded regression/plumbing evidence, not rerun or represented as live-effectiveness evidence.

`documentation-rendering.json` binds the current README hash `843d5b55…` and records 1280px/light and 390px/dark previews without document-wide overflow. I did not perform a new browser render. These are local preview observations, not human aesthetic approval or universal renderer compatibility. Guard/operator documentation remains pending C2.

## Per-C1 acceptance

These verdicts concern the bounded C1 mechanisms; they do not waive related findings or future obligations.

| ID | Verdict | Assessment |
|---|---|---|
| **C1-V01** Strict schemas and graph | **VERIFIED-WITH-LIMITATIONS** | Strict records, IDs, hashes, paths, UTC validation and owned mandatory-check graph are supported. R1 is a semantic policy-validation gap despite valid schema shape. |
| **C1-V02** Persistence and receipt resolution | **VERIFIED-WITH-LIMITATIONS** | Atomic expected-sequence append and missing/tampered/cyclic receipt handling are supported. No live crash/recovery guarantee. |
| **C1-V03** Scoped freshness and exact chains | **VERIFIED-WITH-LIMITATIONS** | Per-target bindings, replacement-receipt invalidation, exact closure references and unaffected-proof preservation are supported. Scope completeness remains reviewer-owned. |
| **C1-V04** Admission versus valid closure | **NOT-VERIFIED** | Original chronology fix is supported, but R1 permits invalid metric policy proof and R3 makes serial closure evaluation exponential. |
| **C1-V05** Producer/context independence | **VERIFIED-WITH-LIMITATIONS** | Producer/recorder distinction and increment-local context separation are enforced as declared protocol identities, not authentication. |
| **C1-V06** Temporal consumption | **VERIFIED-WITH-LIMITATIONS** | Earlier consumed red/compatibility, legacy coexistence, contract freshness and separate current checks are supported. Actual retirement execution remains C2. |
| **C1-V07** Design history/research acceptance | **NOT-VERIFIED** | Retention, scoped hashes and supersession mechanics are supported. Full command-backed finding acceptance remains affected by R2’s shared finding path. |
| **C1-V08** Conservative process/handoff proof | **NOT-VERIFIED** | Original no-spawn and unresolved-lifetime cases are conservative; failed spawned-command receipts still authorize consumers under R2. |
| **C1-V09** Pure evaluation/no fabricated proof | **NOT-VERIFIED** | Evaluation is structurally pure and existing I/O-tripwire controls are relevant. R1/R2 violate proof qualification; R3 affects bounded evaluation. |
| **C1-V10** Regression and fresh evidence | **BLOCKED** | New review counterexamples require persisted regressions/correction/replay. A Q1 dependency also changed after the stable probe intervals. |

### Parent AC reconciliation

| AC / scope | Verdict |
|---|---|
| **AC03 — C1 readiness/proof qualification** | **NOT-VERIFIED:** R1/R2; R3 must also be corrected. |
| **AC05 — bounded scoped reopening/fresh-process resume** | **VERIFIED-WITH-LIMITATIONS:** supported mechanisms; actual fresh-agent experiment remains future, unverified work. |
| **AC07 — C1 history and pre-retirement proof** | **VERIFIED-WITH-LIMITATIONS:** supported protocol boundary; CLI/canonical integration remains pending. |
| **AC08 — research acceptance and authoritative status** | **NOT-VERIFIED:** scoped supersession is supported, but R2 affects finding acceptance; canonical communication integration remains pending. |
| **AC09 — overall preservation/independent gates/quality** | **BLOCKED:** C1 findings and dependency freshness are open; required quality remains incomplete. |
| **Packaging AC09 — bounded harness preservation** | **VERIFIED-WITH-LIMITATIONS:** own 21-test replay and inspected integration; no new live-model or whole-project quality proof. |
| **Documentation AC10 — existing-feature/portable-hero slice** | **VERIFIED-WITH-LIMITATIONS:** accurate bounded changes and recorded rendering evidence; C2 operator coverage and human approval remain unverified. |

## Freshness and execution record

All Python probes used the supplied managed executable with:

```text
P -B scripts\run.py --idle 120 --max 1200 -- P -B -c <in-memory probe>
```

Git checks used idle 30/max 90. The packaging test used the same managed wrapper and the installed Node executable.

The policy/cost probe pinned **30 relevant files**, unchanged before/after. The command-result probe pinned **23 Python files**, unchanged before/after. Those observations are stable-interval evidence, not whole-machine attestation.

**Final handoff check detected a subsequent concurrent dependency edit:**

```text
scripts\measure_graph.py
during probes: e99d64e16fcab33bc91d94c8669d5b22b9cf3090c67df36cb507006678d137dd
at handoff:    f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6
```

The r3 manifest’s repository subset had **22/23 files unchanged**; `measure_graph.py` was the changed file. I did not review that collector correction or rerun while its writer was active.

Core bytes remained:

```text
workflow_gate.py  a703ef74ba71ad2205b7dc4d0293a6acf3a14a8dcdccda337ec9274ec924251f
workflow_state.py a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b
probe.py          bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e
measure.py        44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8
```

The reproduced findings remain grounded in those unchanged C1/policy bytes, but **neither my probes nor the earlier r3 suite can be presented as acceptance of the final changed dependency set**.

Historical `metrics.json` remains **unavailable / incomplete / fail**, with all nine required measurements missing. It is stale evidence, never a current quality pass.

## C2 admission recommendation

**Do not admit C2 yet.**

First correct R1–R3, preserve the original verification reports/tests, add focused regressions, freeze the actual shared dependencies, and obtain independent replay plus separate correction review. Preserve the exact-prefix, no-spawn, UTC, purity and selective-reopening controls.

After that bounded C1 acceptance, the approved continuation addendum can permit C2 **without declaring Q/I1.T4 complete**. Required actual quality, later host exercises, final integration acceptance and publication authorization remain separate blockers to release.

**Review handoff complete.**

---

## Parent disposition

Accept all three reproduced C1 findings. Return bounded correction iteration 3 to the
original implementer, preserving independent verification history and adding real
regressions before fixes. Separate correction verification and re-review are required.
No C2 admission or quality waiver.

Accept the bounded live-bundle and portable-hero approval. These files may be preserved
as a separate local commit after checking the exact staged scope; their acceptance does
not close C1 or Q. No publication retry is authorized.

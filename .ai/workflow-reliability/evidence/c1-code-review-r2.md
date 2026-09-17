# C1 correction re-review, round 2: APPROVE

Original return from reviewer `bbe59c68-4708-4952-8f3d-7d91551302dc`.
Parent disposition follows the preserved return.

**Bounded C1 functional acceptance: VERIFIED-WITH-LIMITATIONS.**
**R1–R3 are resolved for the reviewed mechanisms and exercised cases. No residual blocking finding was found within this correction scope.**

The previous C1 review and r4 freshness blocker remain historical records. This approval applies to the corrected, r5-pinned bytes rechecked below; it does not retrospectively change those earlier verdicts.

Reviewed HEAD: `0b7e1a1f6fd1f807bd254886e2877d605596d96d`
Branch: `shbs-microsoft-workflow-app-verification`

No source, tests, evidence, shared state or session artifacts were written. No nested agents, installations, commits, publication, broad quality collection or mutation were performed. Private temporary fixtures were cleaned. The previously approved packaging/README objective was not repeated.

## R1 — Mandatory comparison bypass

**Verdict: VERIFIED-WITH-LIMITATIONS — resolved.**

**Inspected correction:** `scripts\workflow_gate.py:106–156`, particularly **133–147**.

Every required measurement now passes through the existing authoritative `judge()` independently of its receipt-supplied rule mode. The calculated comparison must be acceptable and agree with the claimed comparison. Floor/coverage thresholds are additional constraints, not substitutes.

The correction also:

- Retains the imported mutation minimum.
- Requires an explicit coverage bar.
- Rejects numeric compare-mode thresholds rather than silently ignoring an alleged additional constraint.
- Preserves required metric membership, completeness, admitted run/source binding and measurement consistency checks.

**Own replay of the original counterexample:**

```text
cycles: base 0 → head 5
supplied rule: floor, threshold 0
policy hash: recomputed

B-work status       = blocked
next_command        = null
blocking reason     = Measured regression contradicts claimed comparison
```

The regression tests at `scripts\tests\test_workflow_gate.py:639–677,694–717` meaningfully exercise:

- Both floor and coverage substitutions across all required metrics.
- Legitimate tightening and insufficient scores.
- Mutation-floor weakening.
- Greenfield zero-cycle positive and new-cycle negative cases.
- Correctly reported permissible warnings versus false comparison claims.
- Missing coverage bars and unsupported numeric compare rules.

These tests passed in my focused replay.

**Limit:** this validates the C1 policy-consumption boundary over synthetic metric records. Actual collector output, observed repository-policy provenance and strict native-report projection remain separate integration responsibilities. No actual quality report was accepted by this review.

## R2 — Failed producer receipts authorizing consumers

**Verdict: VERIFIED-WITH-LIMITATIONS — resolved.**

**Inspected correction:**

- `_command_succeeded`: `scripts\workflow_gate.py:49–50`
- Receipt qualification: **335–352**
- Direct behavioral-red action proof: **223–253**
- Check/action snapshot alias: **174–183**

Successful command-backed proof now requires both:

```text
child_exit == 0
outcome == "executed"
```

This qualification occurs before accepting metric, finding or native-green results. Null-command handoffs remain separate.

Behavioral red retains a narrowly validated exception: recorded failed completion plus matching native assertion evidence. Direct consumers of the red producer **action**, not merely its check, now receive the validated receipt’s exact ID/hash in their prerequisite proof.

**Own replay of the original metric-producer cases:**

| Recorded exit | Dependent B-work | Next command |
|---:|---|---|
| 0 | ready | present |
| 1 | blocked | null |
| 124 | blocked | null |
| Subsequent 0 | ready | present |

Exit 124 here is a synthetic timeout-code record, not a live timeout experiment.

The tests at `scripts\tests\test_workflow_gate.py:679–692,719–784` passed and cover:

- Metric exits 1/124/125/127.
- Zero/fail and nonzero/executed contradictions.
- Failed review, verification, research and human producers.
- Successful command controls and attributed null-command handoffs.
- Valid native red versus timeout/setup-like codes and missing assertion evidence.
- Direct red-action consumption with exact receipt references.
- Replacement receipt reopening the consumer’s previous execution.

The snapshot alias uses the registered action’s equivalent materialized snapshot only when the check key is absent. It does not replace an explicitly blocked check observation or introduce I/O. The positive regression compares the real action/check snapshots before using the direct-action path.

**Limit:** these are library/persistence tests over explicit protocol fixtures, not authenticated producer identities or live guarded execution/recovery. Those limits do not weaken the now-enforced completion consistency.

## R3 — Repeated recursive prefix work

**Verdict: VERIFIED-WITH-LIMITATIONS — resolved for the reproduced serial-chain mechanism.**

**Inspected correction:** `scripts\workflow_gate.py:159–172,399–418,420–453,489–500`.

Each public evaluation owns a registry of prefix evaluators keyed by event-count boundary. Each prefix retains its target-keyed memo. Repeated requests for the same target at the same prefix reuse that result.

The correction preserves:

- Exact pre-closure boundary selection.
- Exact receipt ID/hash union comparison.
- Separate current and historical memos.
- Current-only reopening diagnostics.
- Per-public-call ownership—no global, persistent or cross-call cache.

### Own measured replay

I repeated the original materialized serial-chain construction, including the **12-increment case**, using the real evaluator. Constructor/proof wrappers counted work while delegating unchanged behavior. Fixture construction was outside the timed evaluation.

| Increments | Actions | Events | Evaluators | Uncached pairs | Unique pairs | Seconds |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 15 | 91 | 4 | 87 | 87 | 0.015679 |
| 5 | 25 | 151 | 6 | 195 | 195 | 0.034977 |
| 8 | 40 | 241 | 9 | 432 | 432 | 0.082654 |
| 12 | 60 | 361 | **13** | **888** | **888** | **0.367805** |

Every evaluated target returned `complete`. Assertions required `n+1` evaluators, no repeated uncached `(prefix,target)` pair and the declared quadratic work-count upper bound.

The original 12-increment observation was **4,096 evaluators / 7.133808 seconds**. These are individual timing observations, not a statistically controlled speedup claim.

The persisted regression at `scripts\tests\test_workflow_gate.py:786–836` also passed in my replay, observing 4/6/9 evaluators at 3/5/8 increments. Its subsequent source-change and restoration checks confirm that new public calls do not reuse stale cached acceptance.

**Limit:** event scans, reference merging and materialization still cost work. This removes the reproduced exponential evaluator-construction mechanism; it is not a claim of general linear runtime or unlimited-scale performance.

## Execution and preservation evidence

I read the preserved original review, correction report, r4 verification, r5 verification and r5 handoff.

### Own executions

All Python executions used the supplied managed interpreter with `-B`, through:

```text
P -B scripts\run.py --idle 120 --max 1200 -- P -B -c <in-memory review probe>
```

- **Eight existing `test_review_*` correction tests:** 8 passed, zero failures/errors/skips, **84.237 seconds**, exit 0.
- **Original R1/R2 probes and 3/5/8/12-increment cost probe:** all expected assertions passed, exit 0.
- Git HEAD/branch probes used bounded `run_capture` calls with idle 30/max 90.

The independent r5 **83 workflow + 10 evidence** pass remains the full authorized-suite evidence. I did not claim to rerun those complete suites. My focused replay supplements it with correction review and the original 12-increment measurement.

### Freshness

For both review executions:

- All **1,883 r5 pinned files** matched before execution.
- All remained unchanged afterward.
- Final handoff recheck again found **zero changed pins**.
- All **52 protected historical files** remained unchanged.
- The r5 manifest, report and import-file hashes matched the r5 handoff.

The r5 report records **172 file-backed import observations**. My focused run separately observed ten repository file-backed imports; their source files were covered by the matching pins. I am not presenting that as a new 172-import capture.

The pin-map aggregate was identical before and after both runs:

```text
89d271d8e4de6d04c56bd2a68164978f459791fe6c608bcc71acfa3d9b803ad5
```

### Source hashes — identical before and after

| File | SHA-256 |
|---|---|
| `scripts\workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts\workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts\tests\test_workflow_gate.py` | `af23bb4d96ea9da28f15291dc2c4cbb8e0e9272a40b27140e28efc89f3993636` |
| `scripts\tests\test_workflow_state.py` | `7b259c0f2e6c4e31a5c614769995df97f999fe86ed44b0e1351e3ee7a2d72466` |
| `scripts\tests\workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `scripts\probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts\measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts\measure_graph.py` | `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061` |
| `scripts\evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts\run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |

This resolves the earlier freshness blocker for this explicitly checked snapshot. It is not future-freshness, whole-root, OS/DLL or edit-and-revert attestation. Unrelated Q1 test/evidence writes were not treated as production changes or Q1 acceptance.

## C1 sub-AC disposition

All verdicts below are bounded to C1’s library/protocol responsibilities.

| ID | Verdict | Basis and retained limit |
|---|---|---|
| **C1-V01** Strict schemas/graph | **VERIFIED-WITH-LIMITATIONS** | Prior schema/graph/UTC proof retained; R1 now enforces mandatory comparison semantics. Not exhaustive parser/security proof. |
| **C1-V02** Persistence/receipt resolution | **VERIFIED-WITH-LIMITATIONS** | Unchanged persistence mechanisms and r5 atomic/sequence/tamper/fresh-process regressions. No live crash guarantee. |
| **C1-V03** Scoped freshness/exact chains | **VERIFIED-WITH-LIMITATIONS** | Existing selective invalidation retained; direct red consumption now carries exact receipt references and replacement reopens prior execution. |
| **C1-V04** Admission/mandatory closure | **VERIFIED-WITH-LIMITATIONS** | R1 bypass rejected; prefix chronology and exact references preserved; reproduced exponential work removed. Actual Git/source closure remains C2. |
| **C1-V05** Producer/context independence | **VERIFIED-WITH-LIMITATIONS** | Existing declared-role/context controls retained. No authentication claim. |
| **C1-V06** Temporal consumption | **VERIFIED-WITH-LIMITATIONS** | Historical consumption/current-proof separation and validated red exception retained. Actual guarded retirement remains C2. |
| **C1-V07** History/research acceptance | **VERIFIED-WITH-LIMITATIONS** | Prior history/supersession controls retained; failed command-backed research/finding producers now rejected. Semantic research truth remains reviewer-owned. |
| **C1-V08** Process/handoff qualification | **VERIFIED-WITH-LIMITATIONS** | Original no-spawn protection plus corrected failed-command qualification; valid attributed handoffs preserved. Live recovery remains unverified. |
| **C1-V09** Pure evaluation/proof qualification | **VERIFIED-WITH-LIMITATIONS** | R1/R2 contradictions rejected; per-call prefix memo preserves purity and fresh-call behavior. No actual quality-producer integration claim. |
| **C1-V10** Regression/current evidence | **VERIFIED-WITH-LIMITATIONS** | r5 83+10 replay, own eight-test/probe replay, stable 1,883 pins and preserved history. Broader quality and future integration remain outside this acceptance. |

Original F1/exact-reference F1, no-spawn F2 and UTC F3 are **not reopened** by this correction review.

For the parent ACs, the **bounded C1 portions of AC03, AC05, AC07, AC08 and AC09 are VERIFIED-WITH-LIMITATIONS**. Actual fresh-agent resume, native producer projection, canonical integration and live lifecycle behavior remain future proof—not completed parent ACs. Overall quality/release acceptance under AC09 remains **BLOCKED by Q and other outstanding final obligations**.

## C2 admission recommendation

**Recommend parent acceptance of C1 and admission of the bounded C2 implementation slice under the approved continuation addendum**, using the checked source/dependency snapshot above.

Conditions and boundaries:

- Recheck affected freshness if applicable source/tests change before dispatch.
- Preserve this return and all earlier findings/verdicts; record parent disposition separately.
- Carry forward the previously accepted integration interpretations.
- C2 must prove actual Git/branch/source-close checks, strict native/report projection, guarded dispatch and supported recovery.
- This review does **not** accept Q1 collector correctness, its pending separate review, complete quality, later host exercises or release.
- No metric waiver or publication authorization is granted.

**Correction re-review complete; no further C1 repair or scope expansion requested.**

---

## Parent disposition

Accept bounded C1 functional verification and separate review. All original and
review findings remain preserved. Before preserving C1 independently of the
unaccepted Q1 collector slice, validate its exact files over the committed baseline
so a local C1 commit does not silently depend on uncommitted Q1 changes.
The existing `probe` policy API is the compatibility seam; no implementation change
is authorized by this packaging check. C2 follows C1 preservation. Q remains a
separate release prerequisite, not waived.

# C1 independent verification r4 — separate-review corrections

## Final verdict: BLOCKED-FRESHNESS

**The tested snapshot passed bounded C1 functional verification; the current
dependency set is not verified.**

**FACT:** The final handoff check at
`2026-09-17T04:06:39.759264+00:00` detected a post-replay change in
`scripts/measure_graph.py`:

- Tested: `f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6`
- Handoff: `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061`

This is an actual transitive dependency, not an unrelated evidence edit.
The earlier capture was stable, but its passing result cannot be promoted
to acceptance of changed bytes. No correction replay, Q1 source inspection
or production modification was attempted after this observation.
Parent must arrange a stable dependency freeze/replay; separate reviewer
recheck remains due. All per-finding functional verdicts below apply only
to the explicitly tested snapshot.

**FACT:** The single independent integrated replay passed **83/83 workflow
tests** and **10/10 evidence tests**, with zero failures, errors or skips.
Both test commands exited **0**. All eight R1–R3 correction tests and the
original chronology/exact-reference, no-spawn, UTC, purity, persistence,
identity and scoped-freshness regressions passed.

**R1, R2 and R3 were verified within the correction mechanisms and supported
positive cases exercised below.** No concrete residual failure was observed
in this bounded review. No additional test, production fix or retry was
needed. This does not replace the separate reviewer's correction recheck,
authorize C2, or establish actual quality/release readiness.

**FACT:** All declared C1/Q1 freeze hashes matched before execution.
All **1,881 scoped input files** were unchanged before/after each command
and across capture. All **172 observed file-backed workflow imports**
matched their before/during/after hashes. **41 protected prior files**
(38 independent artifacts, both independent tests, and the separate review)
remained byte-identical.

Observed HEAD: `0b7e1a1f6fd1f807bd254886e2877d605596d96d`.
This run verifies the explicit runtime/test hashes, not merely the HEAD.

## Inputs and bounded independent method

Read:

- `c1-code-review.md`, including C1-CR-R1/R2/R3 and parent disposition.
- `c1-correction-r3-report.md`.
- `c1-correction-r3-handoff.json`.
- `c1-correction-r3-q1-freeze.md`.
- The corrected `scripts/workflow_gate.py`, all eight added correction
  tests, and the actual imported `default_policy`/`judge` definitions.

The tests were mapped to the review's reproduced mechanisms before replay.
They cover the supplied-mode comparison bypass, failed-producer receipt
acceptance, direct native-red producer-action consumption, and repeated
prefix evaluation, with declared positive controls. The existing independent
tests remain unchanged and were included in discovery.

No uncovered correction boundary requiring another test was identified in
this scoped inspection. No `test_workflow_core_verification_r4.py` was added.
This was not an open-ended redesign, Q1 collector review or unrelated hunt.

Only additive `c1-independent-r4-*` evidence was written. No production,
existing test/helper, historical report/log, shared state, installed tool,
OS setting, main checkout, commit or publication was modified. No nested
agent or broader quality/native/corpus suite was run.

## Per-review-finding results

### C1-CR-R1 — VERIFIED-WITH-LIMITATIONS

**Source mechanism, FACT:** `workflow_gate.py:106-156`, especially line 135,
calls the existing `judge()` for each required measurement independently of
the receipt-supplied mode. The claimed comparison must match the authoritative
result, which must be acceptable. A supplied floor/coverage threshold is
an additional condition, not a replacement comparison. Numeric compare-mode
thresholds are rejected rather than silently ignored. Coverage needs an
explicit numeric bar; mutation retains the imported minimum.

**Observed test evidence:**

- `test_review_r1_required_comparisons_cannot_be_replaced_by_floors`
  (`test_workflow_gate.py:639`) rejects both floor and coverage substitution
  for every required metric, using regression values and rehashed,
  schema-valid supplied policies. Direct B-work consumers are blocked with
  no dispatch command.
- `test_review_r1_tightening_adds_to_comparison_and_preserves_positive_proof`
  (`:662`) accepts the valid tightened 96/95 and 100/60 cases, rejects
  insufficient 94/95 proof and the weakened mutation-floor 100/59 case,
  then accepts valid replacement proof.
- `test_review_r1_greenfield_and_warn_comparisons_remain_authoritative`
  (`:694`) accepts zero greenfield cycles, rejects new cycles despite a
  permissive floor, accepts a correctly reported permissible warning,
  rejects a false comparison claim, absent coverage bar and unsupported
  numeric compare rule.
- Existing omitted/unavailable/wrong-run/low-floor/unsupported-scope and
  greenfield-cycle negatives remain passing.

**INFERENCE grounded in those observations:** receipt mode can no longer
route around the required comparison branch identified in R1, while the
tested legitimate tightening and warning cases remain usable.

Limits: these are synthetic metric records with real structural
validation/persistence. They do not prove actual collector output,
observed repository-policy provenance, native producer projection or
authenticated policy authority. Those integrations remain outside C1.

### C1-CR-R2 — VERIFIED-WITH-LIMITATIONS

**Source mechanism, FACT:**

- `_command_succeeded` (`workflow_gate.py:49-50`) requires both exit zero
  and recorded `outcome="executed"`.
- `_receipt` (`:340-351`) reconciles command-backed proof before accepting
  metric/finding/native-green results. Behavioral red instead requires
  failed completion plus the existing relevant native assertion validation.
  Null-command handoffs remain separate.
- `_execution` (`:222-253`) validates the unsuccessful native-red exception
  even when a consumer requires the producer action directly. It propagates
  the validated receipt reference rather than accepting nonzero exit alone.
- `snapshot` (`:174-183`) only aliases a check to its registered action view
  when the check key is absent; an explicitly blocked check observation is
  not replaced. The direct-action positive test compares the two actual
  materialized snapshots before exercising the exception.

**Observed test evidence:**

- `test_review_r2_failed_metric_producers_cannot_authorize_direct_consumers`
  (`test_workflow_gate.py:679`) blocks recorded producer exits
  1/124/125/127, leaves the failed check non-complete, and accepts successful
  command controls before and after.
- `test_review_r2_exit_and_recorded_outcome_must_both_establish_success`
  (`:719`) rejects both zero/fail and nonzero/executed contradictions and
  accepts zero/executed.
- `test_review_r2_failed_finding_producers_and_valid_handoffs` (`:737`)
  covers review, verification, research and human finding kinds: failed
  spawned producers cannot authorize direct consumers; successful commands
  and attributed null-command handoffs remain accepted.
- `test_review_r2_red_execution_exception_requires_validated_native_proof`
  (`:761`) accepts the declared matching assertion result with failed exit 1,
  rejects timeout/setup-like exit codes and nonzero without an assertion,
  permits direct action consumption with the exact receipt reference, and
  reopens that consumer's prior execution after receipt replacement.
- Original behavioral-red symptom/source/line matching, no-spawn failure,
  unresolved admission, direct-exit-only and bare-recovery tests remain green.

**INFERENCE grounded in those observations:** a passing-looking metric or
finding body no longer substitutes for successful recorded producer
completion on the direct-check admission path reproduced by R2. The
specifically validated native-red exception preserves exact proof binding.

Limits: “native red” here means a validated native-result protocol fixture.
Neither those result bodies nor fixture timeout codes are actual guarded
native producer runs or live timeout/recovery experiments. Process identities
are self-declared/synthetic; C2 dispatch/projection/lifetime proof remains due.

### C1-CR-R3 — VERIFIED-WITH-LIMITATIONS

**Source mechanism, FACT:** `_Evaluation.__init__`
(`workflow_gate.py:160-172`) owns a prefix registry within one public
evaluation. `closure_proven_before` (`:399-418`) reuses a prefix evaluator
at the exact event-count boundary rather than discarding its target memo.
Current and historical memos remain distinct; the closure still requires
the exact validated prior receipt ID/hash set. No global or persistent
cache is introduced.

`test_review_r3_prefix_work_is_shared_and_scoped_to_one_evaluation`
(`test_workflow_gate.py:786`) wraps construction/proof calls while
delegating to their real implementations. It counts actual uncached
target/prefix work, asserts valid closure and bounded construction/work
counts, then changes source and observes blocked status in a new public
call; restored bytes produce valid proof again.

**FACT, measured during this independent replay:**

| Increments | Evaluator instances | Uncached proof evaluations | Unique `(prefix,target)` pairs |
|---:|---:|---:|---:|
| 3 | 4 | 87 | 87 |
| 5 | 6 | 195 | 195 |
| 8 | 9 | 432 | 432 |

There were no repeated uncached target/prefix pairs in these cases.
The exact count lines are in the raw workflow log and parsed into the
manifest's `scaling_observations`, not copied from the implementer's report.
The original exact-reference/prefix chronology, legitimate reclosure,
purity and source-freshness regressions also pass.

**INFERENCE:** the reproduced exponential evaluator-construction mechanism
is removed for these serial chains through per-evaluation prefix reuse.

Limits: deterministic work-count evidence, not a claim that all workflow
evaluation is linear or constant-time. Event scans and reference merges
still cost work. No larger-chain timing benchmark or whole-application
performance acceptance was performed; total suite duration is not pure
gate-evaluation time.

## Original C1 sub-AC reconciliation

IDs preserve the original independent criteria. “Verified with limitations”
applies only to the tested library/protocol boundary and does not waive
separate review, C2, Q/I1.T4 or later host obligations.

| ID / criterion | r4 verdict | Evidence / remaining limit |
|---|---|---|
| C1-V01 — strict schemas and dependency graph | **VERIFIED-WITH-LIMITATIONS** | Existing strict key/type/ID/version/hash/path/number/UTC and mandatory-owned-check tests pass; R1 now enforces the tested mandatory comparison semantics beyond schema validity. Not exhaustive parser/security proof. |
| C1-V02 — atomic persistence and receipt resolution | **VERIFIED-WITH-LIMITATIONS** | Atomic failure, expected sequence, receipt-before-reference, missing/tampered/cyclic proof and fresh-process append tests pass. No live crash/lifetime guarantee. |
| C1-V03 — scoped freshness and exact chains | **VERIFIED-WITH-LIMITATIONS** | Per-target source/component/check/claim changes, multi-hop reopening and unaffected preservation pass. Original exact-prefix cases remain green; valid direct-red consumption now retains exact refs and replacement reopens its consumer. Scope completeness remains reviewer-owned. |
| C1-V04 — admission versus valid closure | **VERIFIED-WITH-LIMITATIONS** | Mandatory proof, member/prerequisite order, direct/handoff/transitive/inherited/ship exact-reference and legitimate-reclosure tests pass. R1 bypass is rejected and R3 no longer duplicates uncached prefix work in tested chains. Actual commit/source-close and CLI remain C2. |
| C1-V05 — producer/context independence | **VERIFIED-WITH-LIMITATIONS** | Producer/recorder, implementer/verifier/reviewer and cross-increment controls pass. No authenticated identity claim. |
| C1-V06 — temporal consumption | **VERIFIED-WITH-LIMITATIONS** | Relevant red/compatibility, pre-consumption chronology, absent legacy, historical source retention and separate current-check tests pass. Actual guarded retirement remains future integration. |
| C1-V07 — retained design/research acceptance | **VERIFIED-WITH-LIMITATIONS** | Retained history, supersession, section/source/owner controls pass; R2 now blocks failed command-backed research/finding producers while preserving valid handoffs. Prose truth and actual agent behavior are not proven. |
| C1-V08 — conservative process/handoff proof | **VERIFIED-WITH-LIMITATIONS** | Both no-spawn and failed spawned-command receipt controls pass; direct-exit/unresolved/bare-recovery states remain conservative. Live C2 dispatch/recovery remains unverified. |
| C1-V09 — pure evaluation and no fabricated proof | **VERIFIED-WITH-LIMITATIONS** | No-I/O/deep-input/repeated-call controls pass; R1/R2 negatives and R3 counted memoization pass while exact chronology stays intact. No actual quality receipt or producer integration is claimed. |
| C1-V10 — regression and current evidence | **BLOCKED-FRESHNESS for current inputs; tested snapshot passed** | 83 workflow +10 evidence tests, exact argv/raw logs/counts, declared freeze checks and scoped before/after imports/inputs preserved. Final handoff detected changed `measure_graph.py`; stable dependency replay is required. Separate reviewer recheck and broader quality/native/corpus/host gates remain due. |

Original F1, residual F1, F2 and F3 are not reopened by this replay.
The separate review's packaging/README acceptance was not reevaluated here.

## Actual commands and results

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$p = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_*.py' -v
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_evidence.py' -v
```

| Command | Actual tests | unittest duration | Exit |
|---|---:|---:|---:|
| Workflow discovery | 83/83 passed | 184.322 s | 0 |
| Evidence discovery | 10/10 passed | 5.539 s | 0 |

No errors, skipped tests, timeouts, missing-tool failures or cleanup failures.
Existing real fresh-process/library and owned filesystem/Git fixtures ran in
discovery. Test producer/metric/finding/lifecycle receipts remain synthetic
protocol data, not actual quality or independently produced acceptance.

One sequential integrated replay only. Raw bytes were streamed and retained
without reconstruction; `run.py` combines its child's output, so unittest
output appears in captured stdout and outer stderr files are empty.

Artifacts:

- `c1-independent-r4-workflow.stdout.log` / `.stderr.log`
- `c1-independent-r4-evidence.stdout.log` / `.stderr.log`
- `c1-independent-r4-head.stdout.log` / `.stderr.log`
- `c1-independent-r4-manifest.json`: exact argv/cwd, exit codes, byte lengths,
  log hashes, unittest/scaling observations and per-command before/after pins.
- `c1-independent-r4-imports.json`: actual file-backed workflow import observations.
- `c1-independent-r4-handoff.json`: final scoped freshness/preservation/log recheck.
- `c1-independent-r4-disposition.json`: binds this revised final report to the
  preserved handoff observation; the handoff's report hash identifies the
  pre-blocker draft, not this amended report.

## Applicable source/test freshness

**FACT:** All entries in `c1-correction-r3-handoff.json`'s `source_hashes`
matched before this run, including the Q1 dependencies reconciled by
`c1-correction-r3-q1-freeze.md`. No applicable pinned file changed during
either suite, the bounded HEAD observation or the overall capture.

The **1,881-file census** covers top-level Python runtime modules,
workflow-discovered tests, workflow/evidence helpers and evidence tests,
explicit C1 contract/review/correction inputs, and managed Python
source/binary files. The **172 file-backed workflow imports** all matched
before/during/after, including the transitive probe/measure dependencies.
The evidence suite does not execute the workflow import hook; its
evidence/helpers/run/test inputs were still pinned before and after.

Unrelated measurement tests/docs/evidence were deliberately excluded.
No whole-root stability, Q1 collector acceptance, OS/DLL attestation,
future-freshness guarantee or detection of unobserved edit-and-revert
intervals is claimed.

| Tested source | SHA-256 |
|---|---|
| `scripts/workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts/tests/test_workflow_gate.py` | `af23bb4d96ea9da28f15291dc2c4cbb8e0e9272a40b27140e28efc89f3993636` |
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/measure_graph.py` | `f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6` |

The full applicable input/test inventory and protected original-file hashes
are preserved in the manifest. Historical failing evidence and the review
remain unchanged, not overwritten by this green run.

## Stop / next owner

Return **BLOCKED-FRESHNESS** for the current tree, retaining the bounded green
functional results on the tested snapshot. Parent owns stable-freeze/replay
coordination, disposition and any shared-state update. The separate reviewer
must still recheck R1–R3 corrections.

No C2 advancement, commit, publication, actual quality/probe/mutation pass,
release acceptance or host experiment is claimed. If applicable bytes change
after the recorded handoff, reopen affected freshness rather than presenting
this snapshot's passing result as proof for untested source.

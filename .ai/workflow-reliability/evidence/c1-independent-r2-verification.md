# C1 independent verification r2 — correction replay

## Verdict: NOT-VERIFIED — F1 remains open at the exact-receipt boundary

**FACT:** The three original failing regressions now pass, and all seven
implementer-added correction tests pass. The independently added, previously
uncovered **exact closure receipt-reference chronology** test fails.

- Workflow: **71 tests, 70 passed / 1 failed, 0 errors/skips**, 69.986 seconds,
  command exit **1**.
- Evidence: **10/10 passed**, 6.160 seconds, command exit **0**.
- **F1: NOT-VERIFIED**; original reproduction fixed, residual counterexample below.
- **F2: VERIFIED-WITH-LIMITATIONS** for C1 structural no-spawn/work/check proof.
- **F3: VERIFIED** for the original parsed-aware-UTC defect and tested boundaries.

This is independent verification, not the separate code review. No production
fix, nested agent, shared-state edit, commit, publication or C2 advancement
was performed. Stopped at the reproduced residual failure; no additional
fix/retry/search-for-more-defects cycle was undertaken.

## Inputs, scope and preserved history

Read `c1-correction-report.md`, `c1-correction-q1-freeze.json`, corrected C1
gate/persistence code and all seven added correction tests, alongside the
original tests and established r2 contracts. Reused the original C1
subcriteria rather than substituting the implementer's pass narrative.

The code changes were grounded at:

- `scripts/workflow_gate.py:182-198`: command-backed completion now needs
  `spawned=yes`; null-command handoffs retain their acceptance path.
- `scripts/workflow_gate.py:365-376,398-409`: closure proof re-evaluates
  dependencies using the ledger prefix before the closure, in addition to
  current binding/reference/outcome checks.
- `scripts/workflow_state.py:176-185`: parsed timestamp must have timezone
  information and a zero UTC offset.
- `scripts/workflow_state.py:614-628,706-718`: failed-launch return code,
  terminal completion outcome and spawn-state consistency checks.

Original `c1-independent-*` evidence and
`scripts/tests/test_workflow_core_verification.py` were preserved byte-for-byte:
**23 original files checked before/after; zero changed**. The original
NOT-VERIFIED report and failing-run logs remain historical evidence and were
not rewritten to look green.

Only one uncovered correction-boundary test was added:
`scripts/tests/test_workflow_core_verification_r2.py`.
The remaining writes are additive `c1-independent-r2-*` evidence in this folder.
No original test assertions or helpers were changed.

## F1 residual: different prior proof substitutes for the closure's exact proof

**FACT, actual public-library reproduction:**

1. Register B as requiring increment A. Complete A normally with all its
   work/check records. Positive controls observe A **complete**, B-work **ready**.
2. Run/accept a replacement A-test receipt after A's recorded closure.
   Before any corruption, A correctly becomes **ready** for a new closure,
   and B-work becomes **blocked**. This is the current receipt-chain control.
3. Change only the old fixture closure's `receipt_refs`, replacing its original
   A-test reference with the replacement receipt's exact ID/hash. Do **not**
   move or append a closure. Original receipt files remain unchanged.
4. `load_workspace` accepts the ledger. `evaluate` incorrectly returns A
   **complete** and B-work **ready**.

Observed failure details, preserved verbatim in the raw workflow log:

```json
{
  "closure_seq": 32,
  "replacement_acceptance_seq": 38,
  "increment_status": "complete",
  "dependent_status": "ready",
  "old_ref": {
    "id": "receipt-run-2",
    "sha256": "fcfc5bbdb6eaaf30c2520bb43703f999af0e1367ce5b8e7ffd76252ac3f6cb64"
  },
  "replacement_ref": {
    "id": "receipt-run-6",
    "sha256": "fc52ad0779b6c000f60fc43b7ff98e7b7ad735b8341bfe9313e1c5de7605afd8"
  }
}
```

Reproducible regression:
`test_workflow_core_verification_r2.ClosureReferenceChronologyTests.test_closure_exact_receipt_refs_must_be_accepted_in_its_prefix`
at `scripts/tests/test_workflow_core_verification_r2.py:27-69`.
The failed assertion is at line 67. The dependent status was computed before
the failure and is included in its diagnostic; it is not an inferred result.

**Root cause, INFERENCE grounded in the read source:** The new prefix
evaluation at `workflow_gate.py:376` retains only
`prior.proof(dep)[0] == "valid"`. It discards those prior proofs' receipt
references. Its earlier valid A-test receipt therefore suffices for the
prefix boolean. The separate full-ledger equality check at lines 402-403
compares the rewritten closure references with the **current** replacement
receipt. Neither check establishes that the closure's exact receipt ID/hash
was accepted in its prefix.

This is not another requirement or a request to authenticate fixture data:
r2 `Receipt.rules` requires acceptance-sequence order and exact prior receipt
hashes; the F1 correction explicitly claims proof is established before the
closure sequence. The negative deliberately represents contradictory
persisted history, as did original F1. Some earlier proof is not the
specific proof the closure claims it consumed.

**Required parent disposition:** keep F1 open. Closure-prefix validation must
bind the exact consumed reference set as well as require valid earlier
executions/checks/prerequisite closures. A future C2 entry-point check is not
proof that the current library rejects this malformed history. Production
correction belongs to its owner; this verifier did not change it.

### F1 boundaries that did pass

- Original sequence-2 closure before all checks: original independent test passes.
- Missing extra member execution even though receipt references already exist:
  `test_workflow_gate.py:435` passes; later legitimate reclosure succeeds.
- Prerequisite increment closing after the dependent closure:
  `test_workflow_gate.py:451` passes.
- Ship closing before its prerequisite increment closures:
  `test_workflow_gate.py:473` passes.
- Existing positive closed increment/ship and pure-gate tests pass.

These fixes are real improvements but do not close the exact-reference gap.

## F2 and F3 dispositions

### F2 — VERIFIED-WITH-LIMITATIONS

The original zero-return-code/no-spawn counterexample is rejected.
`test_honest_failed_launch_is_recordable_but_never_executed_work` passes for
null and nonzero failed-launch codes, rejects executed/pass outcomes and
contradictory spawned=yes, retains honest failures, and does not call them
complete work. Known no-spawn retry readiness remains distinct from
uncertain-lifetime recovery.

`test_no_spawn_cannot_supply_a_behavioral_red_receipt` passes: otherwise
matching synthetic red evidence has a positive spawned control, then becomes
blocked when its lifecycle is replaced with failed-launch/no-spawn facts.
The existing positive work/current-check/null-command handoff and negative
unresolved/direct-exit/bare-recovery tests also pass.

Limits: structural protocol validation only. PIDs/lifecycle receipts are
synthetic fixture identities, not evidence of actual guarded child execution,
tree termination, authenticated process facts or C2 recovery integration.
The suite's fresh verification subprocesses are real library invocations,
not a runtime guard CLI.

### F3 — VERIFIED

The unchanged original `2026-09-17+00:00` regression passes.
`test_timestamp_validation_checks_parsed_utc_awareness` accepts Z,
explicit +00:00 and fractional-second UTC controls; rejects date-shaped,
compact-date-shaped, date+Z, naive-time and nonzero-offset negatives.
`test_receipt_and_metric_dates_reject_naive_values_before_comparison` passes
for both receipt timestamp fields and metric-generated time.

The shared validator now checks parsed awareness/offset rather than only a
textual suffix. Existing valid timestamped records and chronological gate
tests all pass. This resolves F3's tested UTC-awareness defect; it is not a
claim to have exhaustively tested every datetime grammar variant.

## C1 sub-AC reconciliation

IDs retain the original independent report's meanings. A passing functional
subset never overrides the residual failure or authorizes C2.

| Sub-AC | r2 verdict | Observed evidence / remaining limit |
|---|---|---|
| C1-V01 — strict records, graph and malformed inputs | **VERIFIED-WITH-LIMITATIONS** | Existing strict schema/graph/path/hash/number/duplicate-key tests and new correction UTC controls pass. F3 resolved; not exhaustive parser or security proof. |
| C1-V02 — atomic persistence and immutable receipt resolution | **VERIFIED-WITH-LIMITATIONS** | Atomic-failure, sequence-conflict, missing/tampered/cyclic proof and real fresh-process append regressions pass. No C2 crash/lock/process-lifetime proof. |
| C1-V03 — scoped freshness and exact prerequisite chains | **NOT-VERIFIED** for full criterion | Selective source/component/check/research and multi-hop freshness tests pass, preserving unrelated receipt bytes. Exact prerequisite-reference chronology across a closure still fails in residual F1. |
| C1-V04 — admission vs mandatory closure and prior proof | **NOT-VERIFIED** | Original F1 and the three closure-ordering correction tests pass; the new exact-reference counterexample makes an invalid old closure complete and unblocks its dependent action. Commit/source validation remains C2. |
| C1-V05 — increment-local independent roles | **VERIFIED-WITH-LIMITATIONS** | Recorder/producer, implementer/reviewer/verifier separation, cross-increment controls and mandatory-owned-check tests pass. IDs remain self-declared. |
| C1-V06 — temporal consumption vs backfill and current proof | **VERIFIED-WITH-LIMITATIONS** | Existing before-action red/compatibility chronology, absent legacy, historical source retention, contract freshness and mandatory current post-change tests pass. Residual closure-reference gap is separately NOT-VERIFIED, not waived by these passes. |
| C1-V07 — retained design history and research supersession | **VERIFIED-WITH-LIMITATIONS** | Existing retained-history/adoption mismatch/supersession/UNKNOWN/owner/section/source tests pass. No semantic research-truth or actual fresh-agent exercise claim. |
| C1-V08 — conservative process and handoff proof | **VERIFIED-WITH-LIMITATIONS** | F2 resolved by original reproduction plus honest no-spawn and synthetic red-proof controls; unresolved/direct-exit/bare-recovery regressions stay conservative. Live C2 process/recovery remains outside scope. |
| C1-V09 — pure materialized gate, no fabricated proof | **NOT-VERIFIED** for full criterion | Purity, repeated/deep-input equality and metric-negative tests pass. Residual F1 still fabricates valid closure dependency status from the wrong prior receipt set. Fixture metric scores are not actual quality. |
| C1-V10 — bounded regressions and fresh evidence | **VERIFIED-WITH-LIMITATIONS** | Requested suites executed with real positive inventories, raw streams, exact argv and scoped input hashes. Workflow exits 1 honestly; evidence exits 0. Separate review/full quality/native/corpus/host gates were not performed. |

## Actual execution and source freshness

Managed Python:
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Both commands ran with `PYTHONDONTWRITEBYTECODE=1`, `-B`, idle **120** and max
**1200** through the existing `scripts/run.py`:

```powershell
$p = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_*.py' -v
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_evidence.py' -v
```

Narrow finishing/reproduction command after parent disposition:

```powershell
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_core_verification_r2.py' -v
```

The new regression uses actual load/bind/evaluate/write APIs against owned
temporary fixture artifacts. Original test data and new receipt scores are
synthetic protocol data, not actual quality/independence evidence.
Temporary fixtures are cleaned by unittest even on failure.
No timeout, missing tool, skipped test, setup error or cleanup failure occurred.

Evidence:

- `c1-independent-r2-workflow.stdout.log` and `.stderr.log`
- `c1-independent-r2-evidence.stdout.log` and `.stderr.log`
- `c1-independent-r2-manifest.json`: exact argv, cwd, exit code, durations,
  stream byte counts/hashes, before/after inputs, freeze checks and preserved
  original-artifact checks.
- `c1-independent-r2-imports.json`: file-backed module observations during
  the workflow run, via the unchanged original optional observation hook.
- `c1-independent-r2-handoff.json`: subsequent applicable-input/original
  evidence/raw-log recheck, not a rerun or blanket root-stability claim.

`run.py` merges inner unittest output, so its captured stdout contains the
test output and the outer stderr files are empty. The capture wrapper
finished saving evidence and returned zero; **the actual workflow command
exit was 1**, not a pass.

**FACT:** All **1,877 pinned files** matched before/after; all **172 observed
file-backed workflow imports** matched before/during/after. All supplied C1
freeze hashes and Q1's `probe`/`measure`/`measure_graph` hashes matched before
execution. Both evidence helpers (`evidence.py`, `run.py`, `tests/helpers.py`)
and `test_evidence.py` were included in the census. The evidence suite does
not run the workflow import hook; its imported-module census is not claimed
as independently observed.

Observation scope: repository top-level Python runtime-module files, only
workflow-discovered tests and their fixture plus evidence test/helpers,
explicit C1 contract/correction documents, and managed Python runtime files.
The module census includes the **actual transitive measurement dependencies**,
not merely the C1 files. It intentionally excludes unrelated measurement
tests and unrelated docs/evidence that the concurrent Q1 verifier may write.
No whole-root stability, Windows/PowerShell/Git DLL attestation, future
freshness, or edit-and-revert detection guarantee is claimed.

Frozen core dependencies independently matched:

| File | SHA-256 |
|---|---|
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts/workflow_gate.py` | `a5c034bb67a95e7b51c0bb5cbba311e625d99d5ed4e0154dec9278dc567b666d` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/measure.py` | `4754fe05621b81a8d499c38dbb913619dd43af50782d07b058849d50994ef8ed` |
| `scripts/measure_graph.py` | `17f50ca7b304bba114131d7578d0250979df3d113201593d99b67e8479fa5245` |

The new test passed AST parsing, final-LF and trailing-whitespace checks.
These are test-file hygiene only, not lint/types/build/coverage/mutation or
actual Q1 measurement acceptance.

## Stop and next owner

Return residual F1 and its preserved test to the original production owner;
keep C1 acceptance **NOT-VERIFIED**. Re-run affected proof against pinned
inputs after any correction. The separate read-only review remains due
afterward. Parent owns shared-state updates and dispositions.

No C2 advancement, quality pass, historical evidence rewrite or publication
is authorized by this report.

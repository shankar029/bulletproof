# C1 independent functional verification

## Verdict: NOT-VERIFIED — three reproduced C1 defects

This is the bounded independent **verification** return, not implementation,
the separate code review, C2 authorization, or a quality/release pass.
No nested agents were used. Parent owns dispositions, shared `state.md`,
integration and the separate reviewer.

**FACT:** Final workflow discovery ran **63 tests: 60 passed, 3 failed,
0 errors, 0 skips**, in **57.786 seconds**, exit **1**. All 52 pre-existing C1
tests passed. The 11 new independent tests passed 8 and failed 3.
The evidence regression suite ran **10/10 passing**, in **5.496 seconds**,
exit **0**. The three failures are real assertions against existing APIs,
not import/setup failures, dependency failures or empty discovery.

**FACT:** All **1,881 pinned files** had identical before/after hashes in the
final run. All **171 observed file-backed imported modules** matched their
before/during/after hashes. The actual dependency chain includes the new
`measure.py` and `measure_graph.py`, not only `probe.py`.
No concurrent source change was observed during either execution interval.
This establishes input stability for the captured runs, not future freshness
or protection against an unobserved edit-and-revert between observations.

## Boundary and grounding

- Resumed the existing C1 verification gate from `../state.md`, rather than
  restarting or redesigning the parent's approved delivery.
- Read `../continuation-plan.html`, the C1 section of
  `continuation-plan-review.md`, r2 `../design-contracts.json`,
  `../guard-resolution-contract.json`, and `c1-implementation-result.md`.
- Read both complete C1 production modules, the fixture helper and existing
  C1 tests. Also read the evidence/runner seams and the actual imported
  `default_policy`/`judge` definitions. Those are now re-exported by probe
  from `measure.py`; no Q1 collector implementation was changed or reviewed.
- Project profile: Python standard-library validation/persistence and
  `unittest`; bounded real subprocess/Git fixtures; existing Node evaluators
  are outside this slice. `CONTRIBUTING.md` and
  `references/testing-and-e2e.md` require meaningful behavioral assertions,
  real library invocation, and explicit incomplete-quality limits.
- Observed branch: `shbs-microsoft-workflow-app-verification`;
  HEAD: `015d353e9cf8fa3b57a561f808cdcd04cfe786e7`.
  The initial Git-status log preserves concurrent/uncommitted work already
  present. No production file, Q1 file, existing test, shared state, main
  checkout, install, OS setting, commit or publication was modified.
- Sole source/test addition:
  `scripts/tests/test_workflow_core_verification.py`.
  Other writes are this report and `c1-independent-*` evidence files here.

The test strategy was derived from the contracts and actual implementation:
map already-covered cases first, then add multi-hop/different-scope and
chronological boundary counterexamples, fresh-process persistence/resume,
increment-local context checks and a stronger pure-gate I/O tripwire.
There is no new public interface or UX requiring a new design.

## Blocking findings

### C1-IV-F1 — closure chronology is not validated

**FACT, reproduced twice:** A `closed` event placed immediately after adoption,
before any member execution or check acceptance, is accepted by
`load_workspace` and reported **complete** by `evaluate` once later events
exist. Reordering preserves contiguous sequences, exact receipt hashes and
matching source bindings; equal timestamps cannot establish earlier proof.

Persisted regression:
`test_workflow_core_verification.py:172`
`test_closure_cannot_be_retroactively_satisfied_by_later_receipts`.
The positive control first completes a normal increment and observes
`complete`. The negative then moves its closure to sequence 2, before its
required work/check events, and observes the incorrect same result.
This deliberately corrupts an owned fixture ledger; it is not a claimed
actual workflow execution.

**Root cause, INFERENCE grounded in inspected code:**
`workflow_state.py:679` excludes `closed` from lifecycle validation;
`workflow_gate.py:382-393` checks present-day dependency validity, closure
hashes/refs, outcome and commit syntax, but not whether those prerequisites
were established before the recorded closure. A future accepted receipt can
therefore retroactively satisfy a prior closure.

**Contract:** r2 `Increment.rules`, `Receipt.rules`,
`procedures.edges_and_resume` and the C1 mandatory-closure/temporal boundary.
Closure is a durable fact supported by already-established proof, not a
standing instruction that later receipts silently complete.

**Required disposition:** reject the contradictory ledger or refuse to treat
that closure as complete. Validate closure prerequisites/member execution
relative to its event sequence. A future C2 close command checking current
readiness does not by itself make this persisted counterexample valid.
Parent/reviewer should explicitly adjudicate the C1/C2 responsibility seam;
this verification does not waive the contradiction.

### C1-IV-F2 — failed launch can fabricate successful work

**FACT, reproduced twice through `append_event`:** A sequence of admission,
launch intent, `launch-failed` with `pid=None`, `spawned=no` and
`returncode=0`, then `completed` with `outcome=executed`, `child_exit=0` and
`spawned=no`, loads successfully and reports the action **complete**.
No child was created in this protocol scenario.

Persisted regression:
`test_workflow_core_verification.py:192`
`test_launch_failed_cannot_claim_successful_work_execution`.
The test accepts either strict validation rejection or conservative
non-completion; the implementation does neither.

**Root cause, INFERENCE grounded in inspected code:**
`workflow_state.py:612-629` does not constrain a failed launch to a
non-successful result; `workflow_state.py:702-710` permits a terminal
launch-failed observation to back completion and compares only return codes.
`workflow_gate.py:197-210` treats zero/executed as successful work without
requiring evidence that a command actually spawned.

**Contract:** r2 `Action.rules`, `ProcessObservation.rules`,
`NativeResult.rules` and C1's conservative process-state boundary. A launch
failure is not executed work. This is structural consistency, not a demand
for authenticated identities or live descendant inspection.

**Required disposition:** reconcile terminal lifecycle semantics with action
execution; zero/executed cannot turn no-spawn into successful work.
Keep unsupported lifetime recovery blocked. No production fix was attempted.

### C1-IV-F3 — UTC validator accepts a naive datetime

**FACT, reproduced twice:** `validate_event` accepts
`time="2026-09-17+00:00"`. Python interprets that value as a date/time with
naive midnight, not an aware UTC timestamp.

Persisted regression:
`test_workflow_core_verification.py:165`
`test_date_shaped_value_with_offset_suffix_is_not_a_utc_timestamp`.

**Root cause, INFERENCE grounded in inspected code:**
`workflow_state.py:176-184` checks a textual UTC-looking suffix and whether
`datetime.fromisoformat` succeeds, not the parsed timezone/offset.

**Contract:** Event/Receipt/generated times are UTC timestamps; strict
malformed-schema rejection is explicitly in the C1 boundary.

**Required disposition:** validate the parsed timestamp as an aware UTC
value. Mixed aware/naive comparisons are a further risk inferred from the
code, **not separately exercised** or claimed as a reproduced crash here.

## Independently derived bounded acceptance criteria

These are C1 subcriteria, not replacements for the parent's AC01–AC10.
`VERIFIED-WITH-LIMITATIONS` below means the named functional scenario is
demonstrated by this bounded suite, not that a failed C1 gate is waived.

| ID / parent mapping | Acceptance criterion | Evidence and observed verdict |
|---|---|---|
| C1-V01 / AC03, AC09 | Strict persisted records reject unknown authority fields, malformed versions/types/IDs/hashes/paths/numbers/times; one acyclic `requires` graph with mandatory owned closure checks. | **NOT-VERIFIED:** F3 accepts a non-UTC timestamp. Existing state schema/graph tests pass; new nested-field matrix rejects `due_checks`, `depends_on`, `gates`, `waiver`, resolved `targets`, fake `passed`, `authenticated`, and `recovery_verified`. No parser completeness claim. |
| C1-V02 / AC03, AC05 | Atomic expected-sequence append, immutable receipt-before-reference resolution, malformed/missing/tampered recursive proof cannot pass. | **VERIFIED-WITH-LIMITATIONS:** existing atomic replacement failure, sequence conflict, missing/changed/cyclic receipt and artifact tests pass. New fresh-process append rejects stale seq without changing ledger bytes, persists seq 2 in another PID, removes only its own lexical lock, and leaves pending admission blocked. No C2 admission/lock/crash supervisor proof. |
| C1-V03 / AC03, AC05 | Freshness uses each target's own source/component/action/check/claim/prerequisite bindings and reopens affected multi-hop consumers while preserving unrelated proof IDs/bytes. | **VERIFIED-WITH-LIMITATIONS:** existing source/component/check/ordinary chronology tests pass. New B-review over A-test accepts distinct scopes, rejects replacement receipt until rerun, then reopens after A-check contract change while B-test remains valid; all original receipt bytes remain unchanged. New directory-member and missing-file creation tests run fresh processes: A blocks, B remains complete, restoring inputs restores A. Scope-selection completeness remains reviewer-owned. |
| C1-V04 / AC03, AC09 | Future closing checks do not block early action/check admission; execution is not closure; mandatory proof cannot be backfilled into an earlier closure. | **NOT-VERIFIED:** positive admission/mandatory checks/ship union tests pass, but F1 makes a pre-execution closure complete using later proof. Commit syntax only is C1; actual Git commit/source and branch verification remain C2. |
| C1-V05 / AC03 | Review/verification producers, not recorders, have distinct contexts from all declared implementers and each other within the increment; another increment's proof cannot replace owned closure checks. | **VERIFIED-WITH-LIMITATIONS:** existing identity/recorder/ownership tests pass. New cross-increment control permits B's implementer to review A, then rejects that same review after B's context becomes a declared A co-implementer. Self-declared protocol identities are not authenticated human/host independence. |
| C1-V06 / AC07 | Before-action proof must be accepted/consumed before modification, retain historical source semantics afterward, not backfill chronology, and still require current post-change checks. | **VERIFIED-WITH-LIMITATIONS:** existing valid retirement, legacy-absent, backdated acceptance, red/setup and current-postcheck tests pass. New historical case survives unrelated B-component re-adoption, but a changed compatibility contract invalidates it; legacy stays deleted and receipt bytes stay intact. Real CLI retirement/native-producer integration remain C2. |
| C1-V07 / AC07, AC08 | Retained design revisions remain hash-bound; research corrections preserve superseded claims and reopen old consumers; scoped prose/source acceptance is not blanket status. | **VERIFIED-WITH-LIMITATIONS:** existing retained-history, adoption mismatch, supersession, UNKNOWN and wrong-owner cases pass. New research anchor case allows another heading to change but refuses changed bound source bytes. This checks structured binding, not semantic truth of research or a fresh-agent exercise. |
| C1-V08 / AC03, AC04 | Process/handoff proof is conservative: no successful work from no-spawn; unresolved admission/direct exit/bare recovery does not authorize replay. | **NOT-VERIFIED:** existing unresolved/direct-exit/external/bare-recovered cases pass; F2 nevertheless marks a failed launch as completed work. All process lifecycle receipts are synthetic protocol data. Fresh verification subprocesses are real, but no live-child recovery experiment or runtime CLI exists in C1. |
| C1-V09 / AC03, AC09 | Pure `evaluate` uses only materialized views, does not mutate inputs, and does not fabricate metric/dependency proof. | **VERIFIED-WITH-LIMITATIONS for purity and tested metric checks; closure dependency qualification is F1.** New test blocks file opens, stat/scandir, processes and sockets; repeated results and deep inputs match. Old materialized view intentionally remains complete after an external edit, while fresh binding blocks. Existing unavailable/omitted/wrong-run/low-floor/unsupported/cycle metric negatives pass. No actual quality report was accepted; producer-schema projection and policy authority integration remain unverified. |
| C1-V10 / AC09 | Bounded regression, positive inventories, exact commands/raw outcomes and before/after dependency/test hashes are preserved, with honest limits. | **VERIFIED-WITH-LIMITATIONS:** both requested suites ran twice. Final total 73 tests = 70 passing / 3 failing. All repository Python runtime dependencies and test inputs are covered by the file census, including imported Q1 modules. Python installation source/binary files and observed Python imports are also pinned; this is not an exhaustive Windows/PowerShell/Git OS/DLL attestation. No broad full suite, native corpus or quality/mutation measurement was authorized. |

## Execution evidence and replay

The exact argv arrays, elapsed wall times, exit codes and stream hashes are in
`c1-independent-final-manifest.json`. Raw streams are written directly from
captured subprocess bytes, not reconstructed from the test summary.
`run.py` merges the inner command's output; accordingly unittest output is
in the recorded stdout log and the outer stderr logs are empty.

| Execution | Raw files | Result |
|---|---|---|
| Initial integrated discovery | `c1-independent-workflow.stdout.log` / `.stderr.log` | 63 tests, 52.322s, 3 assertion failures, exit 1 |
| Initial evidence regression | `c1-independent-evidence.stdout.log` / `.stderr.log` | 10 tests, 5.331s, exit 0 |
| Final integrated discovery | `c1-independent-final-workflow.stdout.log` / `.stderr.log` | 63 tests, 57.786s, identical 3 assertion failures, exit 1 |
| Final evidence regression | `c1-independent-final-evidence.stdout.log` / `.stderr.log` | 10 tests, 5.496s, exit 0 |

The final replay followed removal of one unused import in the new test file.
The initial manifest/logs were retained, not overwritten. No assertion was
weakened, skipped or converted into an expected-failure pass.
The capture harness itself returned zero after saving evidence; **the workflow
command returned one**, and that is the test verdict.

From the worktree root in PowerShell:

```powershell
$p = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $p -B scripts/run.py --idle 120 --max 900 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_*.py' -v
& $p -B scripts/run.py --idle 120 --max 900 -- $p -B -m unittest discover -s scripts/tests -p 'test_evidence.py' -v
```

Narrow reproduction of the independent cases:

```powershell
& $p -B scripts/run.py --idle 120 --max 900 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_core_verification.py' -v
```

All real fresh child invocations inside the tests use `run_capture` with
idle 30 / max 90 seconds and the same `sys.executable -B`.
Owned temporary fixtures are cleaned by unittest cleanup.
The new fresh-process checks observe distinct real PIDs, actual persisted
JSON/sequence changes and unaffected receipt bytes, not process-output slogans.
No timeouts, missing tools or cleanup failures were observed.

The final test file also passed in-memory AST parsing, terminal-LF and
trailing-whitespace checks. This is not lint/type/build/coverage/mutation proof.

## Key final tested hashes

SHA-256; full path/hash inventories are in the two manifests. Imported
file-backed module observations are in `c1-independent-final-imports.json`.

| Path | Final tested hash |
|---|---|
| `scripts/workflow_state.py` | `e9e6b2ddf15417f22444bd143c5ddd9bcf1f0deb7f9c6d1ac0eb4d451c32eaaa` |
| `scripts/workflow_gate.py` | `213d9be7f046d4a5a341f5702ff63d439e9ea20d4072715d430281028a4d7327` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| `scripts/mutate.py` | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| `scripts/probe.py` | `47ab180a173b2cf679d2998fe0b6d34b0fb381be5916e7c72b573d49debbe893` |
| `scripts/measure.py` | `c950812ee106992e46e8c93ef1eed5b93467eb534a6857ddfc68f5077a734be0` |
| `scripts/measure_graph.py` | `8244d75bdf17ed61579ef89239d46427cb919558d4429e4ebe88b550d7609879` |
| `scripts/tests/workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `scripts/tests/test_workflow_state.py` | `a29c923cb0f3bd44b52c206ae5d59492d69591c5a2afedfe905ccf709024798b` |
| `scripts/tests/test_workflow_gate.py` | `b7d9a1c11655749b72132e9e24af4ebb6180b1039bede9bf1006a2a178936498` |
| `scripts/tests/test_workflow_core_verification.py` | `c9c1181ae017f7d42415ca848777fbac388152c18eb57a839f8631132a9e5a8d` |

## Parent handoff / stop

**Stop C1 functional acceptance at these three findings.** Keep the failing
tests as regressions; obtain separate reviewer dispositions and return any
accepted fixes to the production owner. Re-run affected proof against pinned,
serialized source after fixes. Do not advance C2 from this result.

No actual guarded repository adoption, process recovery, host fresh-context
experiment, held-out diagnosis, current live metric acceptance, quality pass,
or release readiness is established. Fixture native/metric/review receipts
remain synthetic protocol data, not actual quality/independence evidence.
I1.T4 and Q remain separate blocked prerequisites.

Parent should record this return in shared state without replacing historical
evidence. Final handoff-time recheck is stored separately in
`c1-independent-handoff.json`; any changed inputs there require replay rather
than a claim that the tested snapshot remains current.

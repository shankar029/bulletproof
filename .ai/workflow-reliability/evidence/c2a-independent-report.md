# Independent Phase 5 — C2a optional process observer

## Verdict: VERIFIED (bounded Windows C2a surface only)

FACT: the frozen implementation satisfies the approved optional observer contract
on the executed Windows CPython 3.14.2 surface. No production counterexample was
found. This is independent verification, not implementation-role evidence, separate
code review, C2 completion, whole-change quality acceptance, or release approval.
No nested agents, factory, installation, production edit, commit, or push occurred.

**Documentation discrepancy:** `c2a-handoff.md` says “nine approved fields.”
The authoritative `design-contracts.json` `records.ProcessObservation.fields`
and actual `run.py` both have **eight**: `phase`, `pid`, `process_group`,
`start_identity`, `identity_evidence`, `returncode`, `cleanup`, `error`.
The verifier checks those exact eight fields. No ninth field was invented and
the owner's original report was not rewritten.

## Coverage map established before adding tests

| Approved scenario | Existing proof used | Independent result |
|---|---|---|
| Missing executable: actual launch failure, no PID/group/exit invented | `CaptureTests.test_launch_failure_has_no_fabricated_pid_or_exit` | PASS; `(127, "", "not found")`, one launch-failed event |
| Other actual Popen error | `test_other_launch_error_is_observed` | PASS; real invalid cwd, error/125 |
| Spawn notification is synchronous while actual owned child is alive | `test_spawn_is_synchronous_while_owned_pid_alive` | PASS; caller thread, PID rendezvous, retained Windows handle, release/completion sentinel |
| Exact eight fields; absent qualified creation identity; real Windows PID/null group | `assert_observation`, launch/live/timeout cases | PASS; identity and evidence null, no fabricated Windows process group |
| Direct-exited occurs after actual direct-child wait, with actual return code | live rendezvous, `test_nonzero_exit_is_a_direct_child_fact`, timeout cases | PASS; retained handle signalled, actual normal/nonzero/terminated code |
| Omitted and explicit-None observer preserve tuple, env/cwd, UTF-8 streams, output, nonzero exit and positional calls | runner compatibility cases plus three unchanged caller smoke tests | PASS; exact tuple assertions and real filesystem effects |
| Partial bytes reset idle progress; idle/max retain existing codes/markers | `test_partial_lines_count_as_progress`, both timeout methods | PASS; idle124/max125; event returncode is actual child code, not a synthetic timeout code |
| Callback Exception at launch, spawn or direct exit cannot return success | three phase-specific observer-failure cases and generic spawn rejection | PASS; explicit `[observer-error]`, rc125; spawned error cleans owned live child |
| Direct-exit callback failure does not establish descendant cleanup or target reaped PID | original direct-exit case covers direct child only | GAP filled by independent descendant case below |
| Timeout plus direct-exit callback failure preserves both diagnostics | previously separate cases only | GAP filled by independent composition case below |
| Synchronous callback is outside capture timeout | explicit `run_capture` docstring/source, not formerly tested | GAP filled by independent bounded callback case below |

Added only `scripts/tests/test_run_c2a_verification.py`, three methods, reusing
the existing `ProcessWitness` rather than duplicating comprehensive lifecycle
tests. No mocked Popen/process, fake child events or mock provenance establish
any C2a lifecycle result.

### New boundary observations

- FACT: after a successful direct-child exit and failing exit observer, direct
  PID **12808** was terminated (retained handle signalled), but actual descendant
  PID **46828** was still alive (retained handle unsignalled). The result was
  error125; the actual exit event retained `cleanup=not-attempted`, `returncode=0`,
  `error=null`. There were exactly two events, not an invented descendant event.
  A real Python audit hook observed only the initial direct-child Popen in the
  verifier process: no later taskkill/reaped-PID subprocess launch. The verifier
  then released its descendant cooperatively and observed both retained handles
  signalled plus the descendant's completion sentinel. This is a positive example
  of the conservative boundary, not a production defect.
- FACT: with idle timeout followed by exit-observer OSError, the tuple is
  `(125, "", "[idle-timeout]\n[observer-error] direct-exited: OSError: timeout exit receipt unavailable")`.
  The direct-exit event still records the original idle marker, actual child
  termination code and best-effort-attempted cleanup.
- FACT: a synchronous spawn callback deliberately ran longer than both .1-second
  capture bounds, verified the child still alive, released it, and waited on its
  retained handle. The capture then returned `(0, "", "")` with actual completion
  sentinel. Capture's monitor is not a watchdog for arbitrary callbacks. The
  independent outer execution remained bounded.

## Executed inventory and preserved failure

| Raw record | Positive methods | Result / elapsed unittest time |
|---|---:|---|
| `c2a-independent-runner.json` | 16 | PASS, 11.141s |
| `c2a-independent-callers.json` | 3 | PASS, 1.093s |
| `c2a-independent-probe.json` | 19 | PASS, 62.312s |
| `c2a-independent-evidence.json` | 10 | PASS, 5.490s |
| `c2a-independent-boundaries2.json` | 3 | PASS, 2.350s |
| `c2a-independent-diffcheck.json` | not a test | exit0, empty stdout/stderr; tracked runner/test whitespace only |

**51 distinct passing test methods across five successful bounded batches**, not
one aggregate suite and not an additional 51 on top of the owner's 19.
Successful batches had zero failures/errors/skips. No outer command timeout or
timeout-recovery retry occurred. Intentional inner idle/max scenarios passed.

The first boundary batch, `c2a-independent-boundaries.json`, is preserved:
**2 passed / 1 failed**. The verifier incorrectly expected the Windows
`subprocess.Popen` audit event's `executable` argument to equal `sys.executable`;
actual value was `None`. Installed CPython `Lib/subprocess.py` at lines1476 and1548
shows command-line serialization and `sys.audit(..., executable, args, ...)`.
The test was corrected to compare the real command payload (`args[1]`) against
the exact expected serialized command and assert only one launch. Only the three
new tests were replayed. This was test-harness correction, **not production red,
not a product fix, and not a mutation kill**. Original owner tests/evidence were
unchanged. Test cleanup ran even on that failure.

## Exact replay commands

Run from the repository root in PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -B scripts/run.py --idle 90 --max 210 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py runner 60 180 $py -B -m unittest scripts.tests.test_run -v
& $py -B scripts/run.py --idle 90 --max 210 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py callers 60 180 $py -B .ai/workflow-reliability/evidence/c2a-callers.py
& $py -B scripts/run.py --idle 150 --max 510 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py probe 120 480 $py -B -m unittest discover -s scripts/tests -p test_probe.py -v
& $py -B scripts/run.py --idle 90 --max 210 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py evidence 60 180 $py -B -m unittest discover -s scripts/tests -p test_evidence.py -v
& $py -B scripts/run.py --idle 90 --max 210 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py boundaries2 60 180 $py -B -m unittest scripts.tests.test_run_c2a_verification -v
& $py -B scripts/run.py --idle 90 --max 210 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-capture.py diffcheck 60 180 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe' --no-pager diff --check -- scripts/run.py scripts/tests/test_run.py
& $py -B scripts/run.py --idle 60 --max 180 -- $py -B .ai/workflow-reliability/evidence/c2a-independent-finalize.py
```

These are executed commands, not permission to overwrite results: the capturer
refuses existing tags. For a later replay choose new alphanumeric tags.
`boundaries` was the original failed invocation, otherwise identical to
`boundaries2`. All JSON records contain the literal child argv, cwd, timeout
bounds, runtime, environment, return code, separate unabridged decoded
stdout/stderr, and before/after hashes. Parallel batches used private fixture
directories and read-only shared source.

## Freshness and limits

- FACT: `run.py` remains SHA-256
  `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e`;
  original `test_run.py` remains
  `92bedd163977112eff3efd3cfbad5fc9aaa9fe9a2318dd2aad832903914b85e5`.
- Each batch checked **35 bounded file pins** before/after, including all22 owner
  freeze pins, current Python scripts, relevant tests/caller/capture/contract
  records, Python executable/DLLs and resolved Git/Node/PowerShell/taskkill
  executables. Each batch had zero within-batch drift.
- The disclosed new verifier-test correction changed one pin between batches.
  Do not describe the initial four successful batches as executing the later new
  test bytes; they did not import that test. The corrected boundary batch proves
  the final new test. Final manifest reconciles this difference explicitly.
- `c2a-independent-final.json` binds this report, raw artifacts and final input
  bytes. It checks owner freeze preservation and records final Git observations.
  Parent-owned state/report/traceability and renderings are deliberately outside
  the bounded freshness assertion. This is not an exhaustive machine, library,
  import or executable-dependency attestation.
- FACT: affected backwards compatibility refreshed here is runner16, callers3,
  legacy probe19 and evidence10, plus the three new boundaries. The accepted
  C1/Q1 commit `5dabb4ca27a440ad370fbcb1be1739ed52e38ab7` is preserved, but its
  earlier 121-method qualification remains **historical after the runner edit**.
  No blanket current C1/Q1 acceptance is reasserted.
- INFERENCE: no additional guard integration replay was causally indicated.
  C1 gate imports probe's pure `default_policy`/`judge`; state imports evidence,
  and neither contains a `run_capture` call. Actual standalone caller and probe
  fixture paths were exercised; no new guard consumer failure arose. This is
  not proof of the pending workflow CLI.
- Only Windows CPython 3.14.2 was executed. Unix process-group identity/cleanup
  is source-inspected, not execution-verified. Direct-child handles establish
  direct-child state only. Descendant survival is explicitly demonstrated in one
  bounded case; no general tree-death claim follows from exit/PID absence/time.
- Callback exceptions exercised are real exceptions raised at the public
  observer seam, not actual disk-full/crash recovery. Null creation identity is
  not recovery authority. Callback boundedness is caller-owned; existing
  best-effort cleanup is not a new supervisor.
- No root quality probe, whole-change mutation, giant Q1 qualification or full
  guard suite was run. No threshold was changed or waived. Full quality,
  six-verb CLI, durable crash/recovery and subsequent C2 work remain open.

**Stop/parent handoff:** dispose this bounded verification result and the
documentation discrepancy; dispatch the required separate read-only review.
The verifier does not proceed to CLI/recovery or declare C2 complete.

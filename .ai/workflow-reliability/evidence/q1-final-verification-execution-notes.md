# Independent verification execution notes

## Scope and inherited gates

This is a replacement fresh-context **Phase 5 functional verification** role,
resuming the accepted nontrivial Q1 correction. It is not a new design,
implementation round, separate code re-review, C1 acceptance, Q2 admission,
root-quality collection or ship gate. Shared `state.md` remains parent-owned.
The approved baseline materialization contract and its independent review are
the authority for R2's representation. Human design approval is still unconfirmed.

## Preserved preflight failure and bounded recovery

The first command was:

```powershell
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-capture.py preflight
```

**Observed exit 1, not a pass.** `q1-final-verification-preflight.json` was
successfully preserved before the assertion. The tool transcript ended with:

```text
  File "...q1-final-verification-capture.py", line 57, in preflight
    assert not changed, changed
AssertionError: ['C:\\Users\\shbs\\.copilot\\repos\\copilot-worktrees\\bulletproof\\shbs-microsoft-crispy-system\\.ai\\workflow-reliability\\state.md']
```

This is a transcription of the tool's error, not a separately byte-captured
stderr file. The persisted input comparison established that the **only** drift
against 530 owner pins was the explicitly permitted parent-owned status file.
The capture's preflight check was corrected to disclose and allow that exact
path, not production, contracts, test inputs, runtime dependencies or history.
No existing evidence was overwritten. The bounded recovery command appended
`preflight preflight-2`; it exited 0. Both JSON observations remain.

## Fresh test plan and capture boundaries

The inspected existing transport streams real worker stdout/stderr immediately
into exclusive-create binary files. Progress is emitted only on actual Python
audit events for subprocess creation and owned temporary-directory creation:
there is no periodic heartbeat or fabricated test output. The inherited
subprocess progress line prints the audit executable field (which can be
`None`); its occurrence, not that field's string, is the observed progress.

Fresh disjoint patterns, each invoked once:

| Label | Pattern | Discovery |
|---|---|---:|
| `g` | `test_measure_[gi]*.py` | 25 original graph/inventory methods |
| `i` | `test_measure_q1*.py` | 27 original methods plus 3 independent methods |
| `p` | `test_probe.py` | 19 legacy probe methods |

Literal argv, working directory, environment delta, bounds, worker PID and
raw-stream hashes are in each `*-launch.json` / `*-command.json`.
The separately saved `*-inventory.json` lists every fully qualified test ID.
This is real unittest discovery in a worker, not a claim to have executed a
different `python -m unittest` command. Internal native controls/subtests are
not added to the method count. Historical owner runs are not added either.

Only evidence destinations and tags are relocated (`resumed-g/i/p`), all under
new `q1-final-verification-*` paths. Source assertions and existing tests are
unchanged. The evidence adapter archives owned fixture trees immediately before
their normal cleanup, including actual Git metadata, source, config and subject
artifacts. It does not replace cleanup, subprocesses, producers or assertions.
Links are recorded without following them. Original verifier archives remain
separately present and retain their own exact manifests. Materializer policy
scratch directories are not presented as extra test-input fixtures.

The three new methods cover only gaps found in the existing test map:

1. Newly introduced source directory absent at baseline stays accepted and
   yields the real new two-node cycle.
2. Missing hidden non-code baseline file and replacement by an empty directory
   both fail; restoring exact immutable bytes succeeds.
3. A real independently copied installed Git launcher is not the qualified
   core/DLL tuple and is rejected without execution. Restoring PATH returns the
   identical qualified binding. This is not execution qualification for another
   build or platform.

All eight resumed-owner controls execute unchanged in the `i` batch, including
the runnable external-filter sentinel's explicit positive control.

## Important evidence limits

- Before/after pins cover actual repository inputs, observed Python modules and
  caches, managed runtime binaries, and the qualified Git core/application DLLs.
  They are not an OS-loader closure, an atomic filesystem lease or a sandbox.
- Existing negative legacy unit tests use their original mocked collector-error
  inputs. They are not represented as real analyzer qualification. New tests
  use real owned files/Git with no doubles or skipped cases.
- Git metadata commands use bounded `run_capture` and store decoded text.
  Test stdout/stderr and original verifier native/CLI streams retain raw bytes.
- A read/hash/copy of controller sources does not prove execution from a stable
  Q4 controller. No root quality or changed-line mutation work is performed.

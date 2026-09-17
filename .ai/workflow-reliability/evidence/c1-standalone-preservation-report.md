# C1 standalone preservation — NOT-VERIFIED

## Bounded result

**FACT:** The exact accepted seven-file C1 overlay does **not** pass its
workflow regression suite over committed baseline
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`.

**83 tests ran in 178.537 seconds; two subtests failed; process exit 1.**
Both failures belong to
`test_review_r1_required_comparisons_cannot_be_replaced_by_floors`.
No import-isolation failure, changing input, timeout or cleanup failure
was observed.

Stopped after the workflow failure. **The evidence suite was not run**;
there is no claimed standalone 10-test evidence pass. No retry, production
change, Q1 overlay, revert or compatibility workaround was attempted.

This is prospective commit-composition validation, not a new open-ended
review. The accepted integrated r5 result and separate re-review remain
unchanged historical evidence; they do not establish compatibility of this
C1-only candidate with the older committed dependency.

## Concrete counterexample

At accepted `scripts/tests/test_workflow_gate.py:639–659`, the test creates
a valid fixture metric receipt and substitutes the supplied rule mode.
For `architecture_rules`, it uses:

```text
metric base: 0
metric head: 100
supplied mode: floor, then coverage
threshold: 0
policy SHA-256: recomputed from required/rules
```

In **both** subtests, evaluation of check `A-metrics` returned `complete`.
The assertion at line 657 requires a status other than `complete`:

```text
FAIL ... (metric='architecture_rules', mode='floor')
AssertionError: 'complete' == 'complete'

FAIL ... (metric='architecture_rules', mode='coverage')
AssertionError: 'complete' == 'complete'

Ran 83 tests in 178.537s
FAILED (failures=2)
```

The later B-work admission assertions in those subtests were not reached;
this report does not invent their outcomes. This is an observed policy
comparison compatibility failure, not an import/signature exception.
No investigation of the Q1 collector or proposed code correction followed.

The candidate actually imported committed `scripts/probe.py`:

`993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82`

It did **not** import the uncommitted r5 probe
`bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e`.
Neither `scripts/measure.py` nor `scripts/measure_graph.py` existed in
the candidate.

## Exact candidate composition

Read the full `c1-code-review-r2.md`, including parent disposition.
Checked the current committed HEAD against the full baseline SHA above.
Created a private owned temporary directory, then ran bounded
`git archive --format=tar --output=<owned>/baseline.tar <baseline SHA>`.
Regular files were copied from archive bytes; links were rejected.
No clone hardlinks, worktree checkout, staging, commit or main-checkout
content access was used.

The archived baseline had **750 files**. Only these seven accepted files
were overlaid, yielding **757 files**:

| Overlay | SHA-256 |
|---|---|
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts/workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts/tests/workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `scripts/tests/test_workflow_state.py` | `7b259c0f2e6c4e31a5c614769995df97f999fe86ed44b0e1351e3ee7a2d72466` |
| `scripts/tests/test_workflow_gate.py` | `af23bb4d96ea9da28f15291dc2c4cbb8e0e9272a40b27140e28efc89f3993636` |
| `scripts/tests/test_workflow_core_verification.py` | `c9c1181ae017f7d42415ca848777fbac388152c18eb57a839f8631132a9e5a8d` |
| `scripts/tests/test_workflow_core_verification_r2.py` | `d58655d83ac448c788d9217d1365631e24e20778b7a9b8b89dcadc32af9ae11b` |

Every overlay matched its accepted r5 pin before copying and after copying.
Workflow test discovery found exactly the four overlaid workflow test
modules; no additional C1 test file was present. The archived probe,
evidence, run, native and helper files were not replaced. The manifest
retains the archive hash/size, complete baseline/candidate pin maps and
exact seven-file composition delta.

## Execution and isolation

Managed interpreter:
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`.

The candidate's **committed** `scripts/run.py` bounded the suite with
`--idle 120 --max 1200`. Both it and the test interpreter used `-I -B`.
The actual test process invoked unittest discovery through an in-memory
`runpy.run_module("unittest", ...)` wrapper, using:

```text
unittest discover -s scripts/tests -p test_workflow_*.py -v
```

That wrapper observed real module files, import/exec origins, `sys.path`
and subprocess dispatches; it did not replace product functions, tests or
results. Full executable argv, including the exact wrapper, cwd and
environment deltas are preserved in the manifest and capture script.
Bootstrap archive commands alone used the original workspace's runner.

`PYTHONPATH`, `PYTHONHOME` and startup/inspection overrides were removed;
user site packages were disabled. Git environment overrides were removed.
All temp environment variables pointed to the privately owned fixture
directory.

**FACT:** The suite observed **169 file-backed module entries / 166 unique
executed-or-imported files**. All matched candidate/managed-runtime
before/observed/after hashes. No file origin or `sys.path` entry escaped
those roots, and no observed child dispatch referenced the original
worktree. Actual candidate imports included committed `probe`, `mutate`,
`run` and `evidence`, plus the seven C1 modules/helpers/tests.

This is suite-process import/exec and dispatch provenance, not an OS-level
trace of every DLL or every descendant's loaded module. Fresh-process
scenarios ran using the candidate-local script paths; no worktree
`PYTHONPATH` was supplied.

## Preservation and cleanup

- **757 candidate files** unchanged before/after.
- **1,855 managed-runtime files** unchanged before/after.
- **1,939 original scoped/protected files** unchanged before/after.
- No unmatched observed file hashes.
- Test fixture directories were empty after test cleanup.
- The entire owned archive/candidate/audit/fixture directory was removed.
- No original report/test/production file or shared state was modified.

Only additive `c1-standalone-preservation-*` evidence was written in the
original workspace. No nested agent, installation, publication or C2 action
occurred. Synthetic metric receipts prove a protocol behavior here, not
actual quality results.

## Evidence / next owner

- `c1-standalone-preservation-capture.py`
- `c1-standalone-preservation-manifest.json`
- `c1-standalone-preservation-workflow.stdout.log` / `.stderr.log`
- `c1-standalone-preservation-workflow-imports.json`
- `c1-standalone-preservation-baseline.stdout.log` / `.stderr.log`
- `c1-standalone-preservation-archive.stdout.log` / `.stderr.log`
- `c1-standalone-preservation-handoff.json`

**Return NOT-VERIFIED for standalone C1 preservation on this baseline.**
Parent can wait for Q1 acceptance and reconcile the committed dependency
composition. This check does not authorize a C1 repair, waive the failing
regression, or establish C2 admission or complete quality acceptance.

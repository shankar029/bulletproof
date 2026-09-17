# C1 bounded correction — F1, F2, F3

## Return / ownership

**Locally corrected and tested; source frozen for independent verifier replay
and separate review.** This is the production owner's correction return, not
an independent acceptance, C2 authorization, actual quality pass or release.

The verifier's `c1-independent-verification.md`, its raw evidence, and all 11
tests in `scripts/tests/test_workflow_core_verification.py` remain unchanged.
The original blocked finding and implementation return were also preserved.
No shared state, Q1 module, fixture helper, CLI/runner, schema definition,
install, OS setting, commit or publication was changed. No nested delegation.

Only four existing C1 files changed from the pinned red run to the green run:

- `scripts/workflow_state.py`
- `scripts/workflow_gate.py`
- `scripts/tests/test_workflow_state.py`
- `scripts/tests/test_workflow_gate.py`

Additional writes are this additive `c1-correction-*` report/capture/log/manifest
evidence. The capture helper is local evidence tooling, not a runtime workflow
module or a new test framework.

## Findings and root-cause corrections

### F1 — closure proof must precede the closure event

FACT: the pinned pre-correction reproduction accepted the verifier's moved
sequence-2 closure as complete using later executions/receipts.

Correction: `workflow_gate._Evaluation.closure_proven_before()` re-evaluates
the existing derived dependency graph against the ledger prefix strictly
before the candidate closure sequence. `proof()` requires that result as well
as existing current freshness, reference, outcome and commit checks.

This checks member executions, handoff/check acceptance, prerequisite
increment closures and ship closure dependencies—not just whether receipt
blobs happen to exist. It introduces no second graph, persisted fields,
filesystem reads, timestamp substitution or historical source fabrication.
Recursive closure checks move to earlier prefixes; current snapshots continue
to reject stale proof.

A premature historical closure is **not complete**. If all proof exists now,
the root target can legitimately be `ready` for a *new* closure event; that is
not retroactive completion. A dependent action/increment needing the old
recorded closure remains blocked. A positive test records a later legitimate
closure and then observes complete, preserving the earlier history.

### F2 — no-spawn facts cannot establish executed work/checks

FACT: the pinned pre-correction reproduction accepted failed launch with zero
return code and no spawn as successful work.

Corrections:

- `workflow_state._process()` rejects zero return code for `launch-failed`.
- `validate_ledger()` requires completion after failed launch to retain
  `spawned=no` and a non-success outcome (`fail`, `blocked`, `unavailable` or
  `interrupted`). Direct-exit completion must retain `spawned=yes`. Existing
  terminal observation and return-code reconciliation remain enforced.
- `workflow_gate._Evaluation.completed()` does not supply an execution fact
  for a command-backed action with no observed spawn. The same seam is used
  by work completion, receipt validation and historical consumption, so a
  fabricated behavioral-red result cannot turn a failed launch into proof.
  Null-command attributed handoffs retain their distinct acceptance path.

Honest failed launches with null/nonzero return codes remain recordable but
not complete work. Known no-spawn failure can be retried; uncertain lifetime,
direct exit alone and unsupported recovery retain their conservative rules.
This is structural consistency, not authenticated process identity or a live
child/tree-termination experiment.

### F3 — UTC validation must inspect the parsed datetime

FACT: the pinned pre-correction reproduction accepted
`2026-09-17+00:00` as UTC although Python parses it as naive midnight.

Correction: shared `_time()` requires the parsed value to have timezone
information and an exactly zero UTC offset after ISO parsing. Existing UTC
suffix restrictions and malformed-input rejection remain. The shared
validator covers Event.time, receipt start/finish and metric generated time,
so naive values fail before aware/naive comparisons can occur.

## Added regression tests

Seven tests were added to the production owner's existing suites:

1. Closure requires all member executions in its prefix, even when every
   referenced check receipt was already accepted; later legitimate reclosure
   succeeds.
2. A prerequisite increment cannot close after its dependent closure.
3. Ship closure requires prior increment closure events, not just prior tests.
4. Honest failed launches are persisted without claiming work; executed/pass
   outcomes and contradictory spawn state are rejected.
5. No-spawn cannot supply a behavioral-red receipt with an otherwise matching
   synthetic assertion result.
6. Parsed aware-UTC positive/negative timestamp matrix, including the verifier's
   exact date-shaped counterexample.
7. Naive receipt/metric timestamps are rejected before comparison.

Synthetic receipts, producer contexts, metric results and lifecycle identities
remain explicitly protocol fixtures. Files, hashes, persistence, real fresh
Python invocations and assertions are real. No fixture is claimed as actual
quality, independent approval, guarded execution or host-effectiveness proof.

## Exact execution and observed results

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

`P = C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

All three capture calls used:

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-capture.py LABEL PATTERN
```

Selections:

```text
red       test_workflow_core_verification.py
workflow  test_workflow_*.py
evidence  test_evidence.py
```

The persisted evidence helper records the exact inner argv, cwd, runtime,
elapsed time, return code, stdout/stderr bytes/hashes, before/after census and
observed imported-module fingerprints. The inner command is:

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p PATTERN -v
```

`PYTHONDONTWRITEBYTECODE=1`; discovery patterns are literal argv items;
tests are non-interactive. Inner fresh-process fixture calls retain idle 30 /
max 90 seconds. Capture helper exit codes preserve the test result unless
input/import freshness fails, in which case capture exits 2. No timeout,
retry, skipped test, empty discovery or cleanup failure occurred.

| Run | Test result | unittest duration | Command exit |
|---|---|---:|---:|
| Pinned red reproduction | 11 tests: 8 pass, exact F1/F2/F3 assertion failures | 16.190 s | 1 |
| Integrated workflow after correction | **70/70 pass**: 52 original + 11 unchanged independent + 7 new correction tests | 68.498 s | 0 |
| Unchanged evidence regression | **10/10 pass** | 5.886 s | 0 |

Final total: **80 passing tests, zero failures/errors/skips.** This is the
bounded workflow/evidence scope, not the full repository/native/corpus suite.

Raw evidence:

- `c1-correction-red.stdout.log`, `.stderr.log`, `.json`, `-imports.json`
- `c1-correction-workflow.stdout.log`, `.stderr.log`, `.json`, `-imports.json`
- `c1-correction-evidence.stdout.log`, `.stderr.log`, `.json`
- `c1-correction-handoff.json`
- `c1-correction-capture.py`

The evidence suite does not contain the independent module's optional
import-observation hook, so its observed-import count is explicitly zero.
Its full before/after file census was still captured. The workflow hook
observed the actual imported Q1 modules as well as the C1/runtime modules.

## Freshness and preserved inputs

FACT: each execution pinned **1,881 files** before and after: repository
Python scripts/tests, the managed interpreter's file-backed Python/runtime
files, accepted C1 contracts/review, the independent verification report and
the capture helper. No files changed within any run.

- Red: **169** observed file-backed imported modules, all hashes matched
  before/during/after observations.
- Workflow: **171** observed file-backed imported modules, all hashes matched
  before/during/after observations.
- Final handoff recheck: **all 1,881** workflow-pinned files still unchanged.
- Red-to-green census comparison: exactly the four owned C1 files above
  changed; Q1 modules and verifier tests/report did not.

This proves observed snapshot stability, not an OS/DLL/process sandbox,
authenticated producer identity, future freshness, or detection of an
unobserved edit-and-revert between observations. The full inventories and
stream hashes are preserved in the JSON manifests.

Final source hashes (SHA-256):

| File | Hash |
|---|---|
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts/workflow_gate.py` | `a5c034bb67a95e7b51c0bb5cbba311e625d99d5ed4e0154dec9278dc567b666d` |
| `scripts/tests/test_workflow_state.py` | `7b259c0f2e6c4e31a5c614769995df97f999fe86ed44b0e1351e3ee7a2d72466` |
| `scripts/tests/test_workflow_gate.py` | `227ec3eba651cf95d0699231c218ea2f59c5523b4f04b75dd331561834205ede` |
| Preserved `scripts/tests/test_workflow_core_verification.py` | `c9c1181ae017f7d42415ca848777fbac388152c18eb57a839f8631132a9e5a8d` |
| Actual imported `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| Actual imported `scripts/measure.py` | `4754fe05621b81a8d499c38dbb913619dd43af50782d07b058849d50994ef8ed` |
| Actual imported `scripts/measure_graph.py` | `17f50ca7b304bba114131d7578d0250979df3d113201593d99b67e8479fa5245` |

## Self-review and stop

Inspected the correction patches and re-opened the changed source methods.
The fix reuses the one dependency graph, existing materialized-view types and
shared timestamp validator; public signatures and persisted schemas did not
change. Existing purity, temporal-consumption, unaffected-branch, handoff and
metric-negative regressions remain green.

In-memory AST parsing/compilation and scoped final-LF/trailing-whitespace
assertions passed. `git diff` / `git diff --check` returned empty because the
C1 files are still untracked at the observed HEAD; those commands are not
claimed as substantive diff/whitespace evidence. The direct source/patch
inspection and explicit file checks are the actual self-review evidence.
No lint/type/coverage/quality/mutation claim is made.

Observed HEAD remains `015d353e9cf8fa3b57a561f808cdcd04cfe786e7`,
feature branch `shbs-microsoft-workflow-app-verification`.
The worker made no commit and will make no further source edits in this
correction objective.

**Next owner:** parent returns this frozen snapshot to verifier
`a02590d4-37a7-4531-ae44-21f0e15cfed3` for independent replay, then obtains a
separate review/disposition. Prior NOT-VERIFIED evidence is not rewritten.
C2, actual producer/CLI/recovery integration, Q/I1.T4 and release gates remain
outside this correction and are not advanced.

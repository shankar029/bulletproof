# C2b ordinary CLI: local implementation freeze

**Local development proof only; parent independent verification/review pending.**
The authorized five-verb slice is implemented. Successful metric attachment,
positive quality closure and recovery remain unavailable. Overall C2, AC04,
complete AC05 and release are not declared complete. Human approval remains
unconfirmed. No agents, installations, commits, pushes or root measurements
were performed by this implementation role.

## Frozen owned files

Raw-byte SHA-256, not Git-normalized hashes. Full own/dependency/runtime pins are
in `c2-cli-freeze03-pins.json` and `c2-cli-freeze01-runtime-pins.json`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `scripts/workflow.py` | 33589 | `a740bdc3325f86293341b7099010b8edba30062f7ddc2a2acef1012bc1b1e1a1` |
| `scripts/tests/test_workflow_cli.py` | 36563 | `bd2e20c4fc364de645c7118e45bb469b9f7408f19793ba1968f6008cdb6d540c` |
| `evals/workflow/helpers.mjs` | 1418 | `d0bded0a4a646298ad61b89056a1c1e66f0448914d206b6b1a1602d42d054cb5` |
| `evals/workflow/failures.test.mjs` | 1046 | `26f7c40184a7766690ab2cfc54f97baea403ab6c14612eb77e3b607966b29034` |
| `references/workflow-gates.md` | 12089 | `e931f3037c852de98a32a2fabe8625d740c214b4fed0612cf51b5dfae40c24f8` |

Accepted base HEAD observed in `c2-cli-freeze01-head.txt`:
`ee6e0e34e78b70fcb672074af0a76f51fe937e1a`. Frozen state/gate/evidence/runner
and previous tests were not edited. Parent-owned state and unrelated
`evals/report.md` changes were left alone.

The Q2 owner's `measure.py` changed during development: final01-before
`7b0f20b6d050b6d5ea3104c6c24ebe4f1d1db9a3b160edf63c32e248337bb179`,
freeze02 `6fc837d1b65a984e55cdde44db8471c3f92b691afcd9e6a461f8c9b3b0f505b5`,
freeze03 `c89d0894360f2990525f97f74b81b4b51b2542afb12e2c8c7c60fa251525f1db`.
`probe.py` was already dirty relative to HEAD but remained identical across
these captured pins. This is not a jointly frozen or independently accepted
Q2/CLI integration result. No other owner's files were changed here.

## Implemented boundary

- Normal `status`, `next`, `record` and `close` use live workspace loading and
  binding. Status returns the gate's Readiness, not a second status model.
  The registered producer is never started on policy denial; administrative
  Git repository validation still uses the bounded runner.
- A single lexical lock covers mutation. Admission and intent precede actual
  producer launch; only actual synchronous runner observations are appended.
  Capture uncertainty or observer persistence failure leaves unresolved intent,
  never a fabricated completion. Failed launch has null child exit and does not
  count as execution. Registered argv/cwd/environment are not rewritten.
- Native results use the actual native parser, canonical Node test reporter,
  admitted inventory and existing receipt/gate validation. Findings bind their
  actual declared artifacts. `record` retains original producer attribution and
  checks matching admission, raw executable output, current source, exact
  prerequisites and immutable artifact bytes before acceptance.
- Before-action receipts are accepted before their exact reference is consumed.
  Actual setup failure cannot substitute for relevant assertion red; compatibility
  is accepted before the real retirement. Fresh-process resume preserves receipt
  bytes and keeps an unrelated B test complete when A proof reopens.
- Adoption implements B0/B1/A0/A1/A2/A3/X, real source snapshots, prospective
  shared validation, exact old-input retention, runtime-ID/classification
  preservation, and event -> workflow -> pointer publication. Retry is finite
  and metadata-only, after normal lock unwinding. No stale-lock stealing.
- Close checks actual current feature HEAD and Git source membership/bytes/modes,
  then unchanged gate obligations. It does not produce a positive closed event
  while the metric bridge is unqualified.
- The operator guide documents all five help surfaces, artifact preparation,
  exercised argument sequences, exit codes and interruption/trust limits.
  Canonical SKILL/current-design/C3 wiring remains parent-owned.

## Observed tests and raw evidence

**156 distinct Python methods have local passing results:** 30 final CLI
methods, 100 unchanged workflow methods, 10 evidence methods and 16 runner
methods. This is a deduplicated inventory across the following runs, not
156 methods in one final invocation.

| Evidence prefix | Actual invocation/result |
| --- | --- |
| `c2-cli-final01` | 154 methods, exit 0, 484.478 seconds: earlier 28 CLI methods plus the unchanged 126 workflow/evidence/runner regression methods |
| `c2-cli-final03` | All final 30 CLI methods, exit 0, 292.992 seconds, against the exact final test/production hashes above |
| `c2-cli-native01` | 13 native tests passed: five CLI pair entry points plus eight unchanged actual native-reporter regressions |
| `c2-cli-native02` | All five pair entry points passed again after the selective-resume scenario was strengthened; 65.674 seconds, no skips |
| `c2-cli-retain01` | Targeted actual denial of each immutable old-input retain; one method with two real filesystem subcases passed, then included in final03 |

The native pair methods invoke actual public CLI operations. They replay five
Python scenarios, so are not five additional unique behavioral implementations
or independent verification. Final03 adds passive raw-capture logging after
native02; no pair behavior or native source changed after native02. The metrics
pair proves denial and useful unrelated work, **not** positive quality closure.

Every named run has preserved `*-command.json`, `*-output.txt` and `*-exit.txt`.
The command manifests contain literal runner/interpreter argv, cwd and the short
owned OS-temp path. `c2-cli-final03-invocations.jsonl` retains:

- 316 literal fixture invocations with cwd, exit, stdout and stderr;
- 36 actual guarded-run captures, including 32 registered executable captures
  and four handoffs, with registered command metadata, resolved cwd, actual
  ledger observations and preserved producer stdout/stderr;
- null streams for handoffs, not invented child output.

Fixture repositories were cleaned after assertions. Persistent logs retain the
observations; deleted temp repositories are not durable production artifacts.
Only verified empty owned temp directories were removed afterward, recorded in
the `freeze02`/`freeze03` cleanup JSON. No process-by-name cleanup occurred.

### Earlier red results and corrections remain preserved

- `dev01`: 17/18 passed. The failed red-pair fixture overwrote its previously
  retained r1 candidate before staging r2. Corrected the fixture's ordering;
  immutable-history rejection was correct, not a product defect.
- `dev02`: 25/27 passed. One test incorrectly expected reopened check status to
  be blocked rather than ready; the authoritative gate was correct. A Windows
  Popen audit test matched only the optional executable argument and did not
  fire. Corrected the test to inspect the actual command argument too.
- `race-red01`: the real candidate-file mutation between parse and snapshot
  reproduced a product defect: adoption incorrectly returned success.
  Corrected snapshot construction to compare every named candidate/review/
  history input to its exact already-read expected hash. The same counterexample
  passes in final01, final02 and final03 with no adoption.
- `race-red01` also re-proved the corrected real pre-Popen exit and finding
  reopening tests. No earlier red output was overwritten or relabeled green.

No outer idle/max test-batch timeout occurred in this CLI slice. Intentional
bounded timeout cases in unchanged runner regressions are test scenarios, not
evidence of a healthy outer command hanging. Earlier C2b-S buffered timeouts
remain historical and unchanged.

## Replay

Use the literal manifests for the exact observed invocation. For a fresh replay,
create a new short private OS-temp directory rather than reusing the deleted
fixture paths or setting TEMP to this deep worktree. For example, from the repo:

```powershell
$python = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:BULLETPROOF_PYTHON = $python
$short = Join-Path ([IO.Path]::GetTempPath()) ('c2check-' + [guid]::NewGuid().ToString('N').Substring(0,6))
New-Item -ItemType Directory -Path $short | Out-Null
$env:TEMP = $short
$env:TMP = $short
$env:TMPDIR = $short
& $python -B scripts\run.py --idle 120 --max 600 -- $python -u -B -m unittest discover -s scripts\tests -p test_workflow_cli.py -v
& $python -B scripts\run.py --idle 120 --max 600 -- node --test evals\workflow\failures.test.mjs evals\lib\native_result.test.mjs
```

Use a new unique `C2_CLI_TRANSCRIPT` destination to preserve fixture/producer
records; do not overwrite the existing evidence. Final01's manifest gives the
exact nine-module focused regression command and its `scripts\tests` cwd.
Streams must remain unbuffered; do not restore the earlier outer buffered
capturer. The observed runtime is managed Python 3.14.2, qualified Git 2.53.0,
Node v24.11.1; binary hashes are retained. Native TypeScript tests emitted their
existing experimental warning, not a test failure.

## Deliberate limits and remaining proof

FACT: design and role metadata in fixtures is explicitly synthetic attribution,
not actual independent agent approval. The synthetic schema-valid MetricVerdict
in the negative record case is rejected; it is not measurement collection.
Actual Node assertions, child processes, Git repositories, filesystem writes,
hashes and public CLI results supply execution evidence. Audit hooks veto real
OS publication calls or terminate the test-owned guard at an actual pre-Popen
boundary; no production runner/observer was replaced with fabricated events.

FACT: no successful metric receipt is accepted, including matching-schema score
JSON or an exit-zero metric command. A qualified producer-owned bridge must
jointly bind pre-admitted run ID, exact registered argv, source projection and
raw validator context/artifacts. Q2-Q5 qualified required measurements remain
separate prerequisites. No thresholds were waived, no UUID rewritten, and no
historical admission backfilled. Positive quality closure stays blocked.

FACT: no recover parser/handler, Event v2, migration, new platform search/reset,
stale-lock release or automatic replay was added. Known guard death, direct
exit, PID absence/reuse or deleted mutex cannot resolve unknown creation or
descendants. The live guard-death test proves its owned child remained alive
when later dispatch was denied; it does not qualify general tree recovery.

FACT: input scopes are cooperative observation, not a sandbox; self-declared
contexts are not authentication. Locally available remote-default metadata is
not authenticated organization branch-protection configuration. Direct run.py
remains diagnostic, not guarded admission. Rejected orphan receipt blobs are
not acceptance authority. Legacy policy semantics are unchanged.

Remaining: parent fresh independent integrated verification and separate review
after both source owners freeze; producer bridge and actual Q2-Q5 quality;
qualified recovery/sixth verb; C3 canonical wiring and actual host exercises;
human confirmation and publication. This role stops at local implementation,
guide and test freeze. It does not assert independent acceptance, whole C2
completion, model effectiveness, or release readiness.

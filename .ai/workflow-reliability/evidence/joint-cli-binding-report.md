# Joint ordinary CLI + Q2 binding checkpoint — fresh independent verification

## Verdict: NOT-VERIFIED for the complete bounded checkpoint

**FACT:** No production assertion failure was observed. Ordinary CLI and the
runnable root/source-binding tests passed. Acceptance is nevertheless withheld:
the selected Q1 regression batch could not finish, and its single authorized
capture-only retry also hit the 120-second idle limit. This is a verification
blocker, **not an established production defect**, not a green suite, and not
an excuse to discard the named symlink environment limitation.

This role resumed the accepted design and performed independent verification
only. No production, documentation, shared state, schema, existing artifact,
installation, privilege, commit or publication edits were made. New files are
additive `evidence/joint-cli-binding-*`. No agents were spawned. Parent distinct
code review remains separate and cannot repair the missing execution proof.

## Exact observed accounting

The corrected discovery inventory has **263 distinct Python methods**:
**204 passed**, **one twice-timeout method**, **57 never started**, and **one
environment-unverified symlink method**. No method is silently excluded or
counted as a skip/pass. Native execution adds **13 entries: five wrappers
replaying existing Python behaviors plus eight reporter regressions**. Those
five wrappers add zero independent Python behaviors.

| Scope | Fresh completed methods | Evidence |
|---|---:|---|
| Ordinary CLI | 30/30 | `joint-cli-binding-records/cli/` |
| Three genuine independent gaps | 3/3 | `independent/` |
| Existing state/gate/adoption | 100/100 | `workflow/` |
| Evidence + ordinary runner | 26/26 | `support/`, before its import error |
| Additional C2a boundaries | 3/3 | `support-resume/` |
| Tool-root checkpoint | 10/11 | `root/`; one retained WinError 1314 case |
| Source bindings | 7/7 | `source/`; 1690.524 seconds |
| Selected Q1 regressions | 6/64 | interrupted `q1/output.log`, not a completed suite |
| Probe regressions | 19/19 | `probe/` |
| Native pair/reporter | 13/13 entries | `native/`; five Python replays, eight reporter cases |

`inventory-reconciliation.json` records **every actual method ID**, its scope,
completed IDs, missing IDs, and the 57 never-started selectors. The initial
support discovery mistakenly lacked the repository root on `sys.path`, yielding
one `_FailedTest` placeholder. That is **not a test method**. Corrected discovery
replaced it with the three real C2a method IDs. The 26 already-passing support
methods were not rerun. There were no assertion failures in completed tests.

Initial Q1 completed IDs, derived explicitly from preserved verbose output:

- `test_measure_graph.GraphTests.test_absolute_relative_conditional_local_and_external_imports`
- `test_measure_graph.GraphTests.test_aliased_builtin_loader_and_importlib_calls_are_disclosed`
- `test_measure_graph.GraphTests.test_compiled_architecture_rules_and_dynamic_disclosure`
- `test_measure_graph.GraphTests.test_cycle_budget_is_unavailable_not_a_truncated_zero`
- `test_measure_graph.GraphTests.test_effective_frozen_binding_respects_startup_precedence_and_consistency`
- `test_measure_graph.GraphTests.test_elementary_cycles_include_self_loops_and_direction`

These are observed completed methods, not a reconstructed successful result.json.

## Per-scope and acceptance-criterion findings

| Criterion / scope | Verdict | Fresh evidence and limits |
|---|---|---|
| AC04, ordinary routed execution | VERIFIED-WITH-LIMITATIONS | CLI30 demonstrates all five public verbs, authoritative live readiness, registered argv/cwd, no registered child on denial, admission/intent before spawn, actual launch/nonzero/observer uncertainty, real pre-Popen death and guard death with a surviving owned child followed by cooperative cleanup. Independent environment test proves exact set/remove/inherit behavior. Cooperative metadata is not actor authentication or a sandbox. |
| AC05, ordinary artifact resume/adoption | VERIFIED-WITH-LIMITATIONS | Fresh-process selective resume preserves unrelated B proof and immutable receipt bytes. B0/B1/A0/A1/A2/A3/X, publication failure/retry, exact-read candidate race rejection, immutable history and ID preservation pass. Independent pending-handoff reclassification rejection passes. Recovery/positive tree resolution remain unsupported. |
| Nonmetric receipt and close boundary | VERIFIED-WITH-LIMITATIONS | Actual native red versus setup, compatibility before retirement, finding producer, handoff/record and exact prerequisite/source/artifact binding pass. Independent Git membership and executable-mode denials complement wrong HEAD, scoped byte and protected/default-branch denials. Exit-zero metric commands and schema-valid synthetic scores reject. No successful metric attachment or positive quality closure is asserted. |
| ROOT01/02 | VERIFIED within checkpoint | Conditional original root, empty-Q1 compatibility, exact opaque copies, shared unique qualification rows and actual public two-revision probes with repository/external originals pass. Both remain incomplete/fail with all nine required metrics. |
| ROOT03 | VERIFIED-WITH-LIMITATIONS | Strict paths, case/prefix/reserved-output collisions, actual hardlinks and junctions reject. Actual symlink creation remains environment-unverified, WinError 1314; no privilege changes, retry or mock. |
| ROOT04 | VERIFIED within checkpoint | Missing/changed originals and staged copies, consistent rehash forgery, moved original root, external executable and TypeScript resource changes are rejected. No original/copy fallback is accepted. |
| ROOT05, implemented checkpoint only | VERIFIED-WITH-LIMITATIONS | Public probe stages/reconciles qualified inputs and retains all required metrics as incomplete. Full scalar/JS raw reconciliation was not implemented and is not certified by binding smoke. |
| Source-tool bindings | VERIFIED-WITH-LIMITATIONS | All seven final methods pass: three tools at two real Git revisions; fixed Python `-I -S -B`/qualified source roots; pinned TypeScript compiler reads/options; actual preload poison and unqualified import rejection; original resources/controller/reservations authoritative. Nine successful smoke invocations and one expected unqualified-import rejection are retained in source raw records. Smoke is not a metric collector; PE candidate hashes are not complete loaded-DLL attestation. |
| AC09, selected joint regressions | NOT-VERIFIED | Workflow100, support29, probe19, native13 and six Q1 methods passed. Remaining Q1 regression proof is missing. No full Q5 regression or whole-request quality result follows. |

The three newly authored methods are in `joint-cli-binding-tests.py`, class
`JointBoundaryTests`: exact registered environment behavior; real committed
membership/mode mismatch; and actual pending-handoff reclassification denial.
They extend only gaps not asserted by the frozen CLI suite.

Guide/help claims were read against the real parser and handlers. All five help
surfaces and unsupported arguments ran through the CLI tests. There is no
recover command/stub, mutex stealing, Event v2, ad-hoc producer UUID rewrite,
after-the-fact admission or positive process-tree recovery claim.

## Retained verification incidents

1. **Support import error:** `test_run_c2a_verification` imports
   `scripts.tests.test_run`. The initial harness added scripts/tests and scripts,
   but omitted repository root. Raw traceback is in `support/output.log` and
   `support/result.json`. The additive resume harness adds repository root;
   only its three previously undiscovered methods were run, all passing.
2. **Q1 idle timeout:** exact method
   `test_measure_graph.GraphTests.test_graph_receipt_summary_and_artifact_corruption_rejected`.
   Initial batch exited 124 after 281.417 seconds, with the last method silent
   for 120 seconds. It loops through real producer validation/corruption cases
   without completed-subcase output.
3. **One capture-only retry:** removed global passive profiling and retained
   already-completed methods. The same first remaining method again exited 124
   after 120.591 seconds. Therefore profiling alone is **not an established
   root cause**. No assertion failure or successful completion was observed.
   There was no third attempt, timeout inflation, synthetic heartbeat, or
   production/test rewrite. `q1-resume/` retains the exact command and output.

The 57 later methods did not start because fail/timeout stopped the batch.
They are not implicitly passing, redundant, or deleted from acceptance.

## Byte freshness and runtime boundaries

**FACT:** HEAD was observed before and after as
`ee6e0e34e78b70fcb672074af0a76f51fe937e1a`.
All nine requested frozen raw-byte hashes matched before execution.
All **4,511 initial file pins matched after execution**, including production,
tests/helpers, accepted binding contracts/reviews, selected qualification
artifacts, indexed source resources and substantial runtime inputs.

`before-pins.json`, `after-pins.json`, and `freshness.json` are indexed records;
the 3,348-file resource index was not dumped into conversation and its 95 old
qualification fixtures were not rerun. CRLF working bytes were compared as raw
bytes, not against Git LF blobs. The prior parent-preservation explanation was
read; there was no EOL-based false code-change finding. Parent report/state
changes are outside the frozen pin scope.

**Additional attestation limit:** observed-import/executable reconciliation
found eight files absent from the initial pin set: the actual
`clangarm64/bin/git.exe` behind the pinned cmd launcher, and managed Python
`_asyncio`, `_ctypes`, `_overlapped`, `_socket`, `_ssl`, `_uuid`, `select` pyds.
Their current hashes and observed paths are in
`supplemental-observed-inputs.json`. These are explicitly **current-only**,
not retroactive before/after pins. No complete dependency-closure attestation
is asserted. A subsequent accepted run should pin these before its execution.

## Commands, raw capture and cleanup

From repository root, using the qualified Git PATH and managed Python:

```powershell
$p='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;'+$env:PATH
$env:PYTHONDONTWRITEBYTECODE='1'
& $p -B -u .ai/workflow-reliability/evidence/joint-cli-binding-verify.py batch cli
```

That is an **observed invocation**, not a safe overwrite/replay instruction:
the existing evidence destinations intentionally reject reuse. The other
observed batches use `independent`, `workflow`, `support`, `root`, `source`,
`q1`, `probe`, `native`. The additive resume invocations were
`joint-cli-binding-resume.py batch support` and `... batch q1`.

Each directory's `command.json` retains literal outer/inner argv, cwd and
relevant environment; `pid.json` retains actual supervisor/runner PIDs;
`output.log` retains streamed merged raw bytes; `exit.json` retains actual
exit/duration. Initial Python batches also retain passive actual-spawn/capture
records and CLI producer transcripts. Fixture metadata is synthetic; actual
processes, files, CLI outputs and Git operations are execution evidence.

`raw-record-index.json` hashes 83 records existing at reconciliation.
`source/raw-*.json`, `two-revisions.json`, `environment.json` retain actual
source-tool request/result/command data. `root/{repository,external}.json`
retain actual public probe/graph data. Production run_capture's UTF-8
replacement/newline normalization is distinguished from outer raw log bytes.

Receipt transport was actually round-tripped through `write_json_atomic`
at a 135-character short-temp receipt path before long execution. This was a
transport preflight, not a fabricated accepted receipt.

The new private temp root is
`C:\Users\shbs\AppData\Local\Temp\jcb-d1c7tvf7`.
Seven exact leftover directories are listed in `cleanup.json`; they were
retained after the timeouts, not broadly deleted. The two timed-out runner
PIDs were absent in later observation. Among 895 recorded IDs, two old CLI/Git
PID numbers were currently present but creation identity/path was unavailable;
their old invocations had completed, and no potentially reused PID was killed.
This is not complete descendant-death proof. Both current timeout cleanup and
the historical whole-old-tree cleanup remain **UNKNOWN**.

## Precisely missing proof / next owner

- Parent must resolve the Q1 capture blocker with a genuinely progress-visible,
  bounded route that reports completed real validation/assertion work. Do not
  make an unchanged third attempt. The exact failing selector and both actual
  commands are retained above/in `q1*/command.json`.
- Run the 57 selectors in `inventory-reconciliation.json.never_started` under
  a fresh additive capture. Reconcile the current-only runtime inputs into
  prospective pins first. No source correction has been justified here.
- Symlink finishing command, **only in an already-capable environment**, with
  a fresh short TEMP/TMP/TMPDIR and qualified Git PATH:

```powershell
Push-Location scripts/tests
& $p -B ../run.py --idle 120 --max 1800 -- $p -B -u -m unittest test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects -v
Pop-Location
```

No privilege change is authorized. The persistent case remains in discovery.
Nonempty JS entrypoints still reject; shared JS/scalar collectors, raw metric
reconciliation, guarded successful metric attachment, all-nine completeness,
Q3/Q4/Q5, recovery, human approval and publication remain outside this
checkpoint or incomplete. This report does not close the original user request.

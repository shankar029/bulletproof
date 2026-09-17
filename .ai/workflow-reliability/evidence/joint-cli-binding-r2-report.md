# Joint CLI + Q2 binding checkpoint — r2 capture completion

## VERIFIED-WITH-LIMITATIONS — bounded checkpoint only

**FACT:** The authorized different capture route completed the exact previously
timed-out method and all 57 never-started selectors. All **58 passed**, without
rerunning the retained 204 passing methods. Actual discovery reconciles to
**263 distinct Python methods: 262 passed and one named environment-unverified
symlink case**. There are no remaining unstarted selectors.

The retained native result is **13 passing entries: five wrappers replaying
Python behaviors plus eight reporter regressions**. These were not rerun in r2
and do not add five independent Python features. Preflight exercised existing
fixture behavior and adds **zero** test methods.

This supersedes only the first report's incomplete Q1 verification disposition.
`joint-cli-binding-report.md`, both timeout captures, original inventories,
test sources and all earlier raw data remain unchanged. The first report's
then-current observations remain historical facts. Parent acceptance and
distinct code review are still pending.

## Why the different route worked

Read before instrumentation:
`scripts/tests/test_measure_inventory.py:88–90`, where `Q1Fixture.validate`
directly returns the actual `measure.validate_observations` result;
`scripts/tests/test_measure_graph.py:247–285`, the real corruption test;
and the installed unittest `_AssertRaisesContext.__exit__` implementation.
Neither production code nor any existing test body was changed.

`joint-cli-binding-r2.py` uses `sys.setprofile` with an exact identity filter for
two code objects only:

1. `Q1Fixture.validate.__code__`
2. `unittest.case._AssertRaisesContext.__exit__.__code__`

Python still dispatches the callback globally, but unrelated calls return after
at most two identity comparisons. They perform **no timing, allocation, hashing,
filesystem/spawn inspection or capture I/O** in this filter. This is not the
old full capture profiler. Only matched call/return events are recorded.

Entry records are flushed to the diagnostic file, **not printed as progress**.
Only actual return events emit flushed progress, including exception unwinding:
`returned-control/completed-invocation`. They carry method ID, target, ordinal,
duration and PID. They do not claim an assertion passed, inspect or substitute
the validation payload, suppress a validation exception, or replace unittest's
judgment. All observer error lists are empty. There is no timer, heartbeat,
mocked validation, extra producer, background progress printer or raised bound.

### Actual preflight and timed-method evidence

- Preflight materialized an actual existing Q1 fixture, validated its positive
  observation list, then applied a real receipt corruption and retained the
  original `assertRaises(ValueError)` judgment.
- Two actual validation returns were observed before preflight exit
  (10.307 and 10.033 seconds), plus one assertion-context exit. The fixture
  cleaned up. This duplicate behavior is not added to test totals.
- The previously timed-out method passed in **136.1955355 seconds**.
  It completed **12 real validations**, each **9.8258–10.0497 seconds**,
  totaling **119.1019747 seconds**, plus 11 assertion-context exits.
- Across preflight and the 58 new passing methods, **55 real validation
  completions** were observed. The longest was **11.2591 seconds**.
  Every target entry ordinal has a matching returned-control ordinal.

**INFERENCE:** The observed 136-second method with many short validations
supports cumulative silence as the cause of the previous outer idle failures.
It is not a retrospective internal trace of those killed processes or proof
of their complete cleanup. No single validation in this route approached the
unchanged 120-second idle limit.

## Exact nonduplicated batches

Every batch used **idle 120 / max 1800**, a separate newly owned short OS-temp
root, unbuffered Python, and the qualified Git PATH. Unittest stayed fail-fast
and judged the original assertions. All twelve test batches and the preflight
exited zero; no r2 failure, error, skip, timeout or trace error occurred.

| New batch | Distinct methods | Unittest seconds |
|---|---:|---:|
| Exact timed-out method | 1 | 136.196 |
| Remaining graph | 8 | 270.712 |
| Inventory/physical alias | 10 | 345.478 |
| Attribute admission | 4 | 55.589 |
| Independent attribute boundary | 1 | 19.052 |
| Final baseline boundaries | 3 | 52.224 |
| Q1 integration/public probe | 9 | 450.308 |
| Resumed baseline boundaries | 8 | 179.863 |
| Reviewed Q1 boundaries | 2 | 77.275 |
| Independent Q1 verification | 6 | 196.170 |
| Q1 correction boundaries | 2 | 94.188 |
| Public measurement E2E | 4 | 367.051 |
| **New total** | **58** | Separate batches, not one aggregate run |

The retained six Q1 methods plus these 58 complete the selected **64-method Q1
regression inventory**. Full combined accounting is:
CLI30 + independent3 + workflow100 + support29 + root10 + source7 + Q1 64 +
probe19 = **262**, with one additional discovered root symlink case blocked.
`joint-cli-binding-r2-records/inventory-reconciliation.json` contains every
actual method ID, all 204 retained IDs and all 58 newly completed IDs.

## Per-scope acceptance disposition

| Scope | Combined checkpoint verdict | Boundary |
|---|---|---|
| AC04 / ordinary routed CLI | VERIFIED-WITH-LIMITATIONS | Retain CLI30 + independent exact environment, close and adoption boundaries. Five real verbs, admitted execution, nonmetric receipt binding and uncertainty denials. Cooperative metadata is not authenticated identity or a sandbox. |
| AC05 / ordinary resume/adoption | VERIFIED-WITH-LIMITATIONS | Retain fresh-process selective resume, finite adoption states, publication retry, immutable history and exact-read race correction. Recovery and positive process-tree resolution remain unsupported. |
| AC09 / selected affected regressions | VERIFIED-WITH-LIMITATIONS | The Q1 execution gap is closed by 58 new passes; retained workflow/support/probe/native proof remains byte-preserved. This is not full Q5 regression or all-repository quality acceptance. |
| ROOT01/02/04 | VERIFIED within checkpoint | Retained actual root/config compatibility, two-revision original/staged ownership and freshness/tamper cases, complemented by completed Q1 regression checks. |
| ROOT03 | VERIFIED-WITH-LIMITATIONS | Actual junction/hardlink cases passed previously and remain retained. Actual symlink creation is still environment-unverified, WinError 1314. |
| ROOT05 / implemented binding checkpoint | VERIFIED-WITH-LIMITATIONS | Actual probe and source-binding smoke are not scalar/JS metric collectors or full raw metric reconciliation. All nine metrics remain required; complete quality is not established. |
| Source-tool bindings | VERIFIED-WITH-LIMITATIONS | Retain all seven passing final source-binding methods, exact qualified settings/resources, poisoned preload and unqualified import rejection. PE candidate hashes are not complete loaded-DLL attestation. |

Successful guarded metric attachment remains explicitly unsupported, including
exit-zero commands and schema-valid synthetic scores. Required metrics still
block positive closure. There is no recover command/stub, mutex steal, Event v2,
after-the-fact admission, UUID rewrite, ambient tool fallback, session-helper
execution as an adapter, or positive tree-recovery claim from this verification.
Nonempty JS entrypoints remain rejected. Binding smoke is not a collector.

## Prospective freshness, history and runtime limits

**FACT:** All **4,608 prospective file pins** matched after execution. This set
includes the original 4,511 inputs, all eight supplemental runtime files,
the r2 capture helper, and the preserved earlier evidence/report artifacts.
The actual `clangarm64/bin/git.exe` and seven managed Python pyd additions were
pinned **before** this run in `prospective-runtime-additions.json`.

Those eight additions were only current-hashed in the first run; r2 does
**not** retroactively convert that earlier observation into before/after proof.
The initial runtime attestation limitation remains attached to retained runs.
No complete loaded-module/native DLL attestation is asserted.

The final observed HEAD remains
`ee6e0e34e78b70fcb672074af0a76f51fe937e1a`.
Raw working bytes, including CRLF, were compared directly. Test/production
source hashes and all earlier failed capture bytes remained identical.
No source correction was needed or authorized. Parent state/report edits
outside the pins are not execution changes.

## Capture index, commands and cleanup

Primary artifacts under `joint-cli-binding-r2-records/`:

- `plan.json`: exact discovered inventory, disjoint groups and retained IDs.
- `before-pins.json`, `after-pins.json`, `freshness.json`: prospective pins.
- `prospective-runtime-additions.json`: the eight newly prospective runtime pins.
- Each batch: `command.json`, `pid.json`, `worker.json`, `output.log`,
  `validation-events.jsonl`, `result.json` (or preflight record), `exit.json`,
  and `cleanup.json`.
- `completion-summary.json`: reconciled real entry/return ordinals, durations,
  outcomes and new-root cleanup.
- `inventory-reconciliation.json`: 262 passed / 263 discovered; sole missing ID.
- `raw-record-index.json`: hashes of records at finishing reconciliation.

Example **actual** command, from repository root:

```powershell
$p='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;'+$env:PATH
$env:PYTHONDONTWRITEBYTECODE='1'
& $p -B -u .ai/workflow-reliability/evidence/joint-cli-binding-r2.py batch timed-method
```

Literal wrapper/inner argv, cwd, relevant environment and PIDs are in every
`command.json`/PID record; the wrapper invokes the unchanged `scripts/run.py`
with `--idle 120 --max 1800`. Existing destinations reject reuse: this is an
execution citation, not permission to overwrite evidence.

The new route captures raw merged wrapper output and original unittest output,
plus bounded target completion records. It intentionally does **not** repeat
full per-spawn/per-filesystem profiling. Completion-event counts are neither
test counts nor a replacement for producer raw evidence.

All **13 newly owned short temp roots** (preflight + twelve batches) were
observed empty after fixture cleanup and removed **nonrecursively**. Their exact
paths and empty inventories are retained. No old root was cleaned or retried.
The first run's seven leftover directories and historical whole-old-tree
cleanup remain **UNKNOWN**. No reused/unknown PID was killed, no process-by-name
cleanup was performed, and empty directories do not attest general tree death.

## Remaining environment case and handoff

Still environment-unverified:
`test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects`.
Keep the prior actual WinError 1314 result; no privilege retry, mock,
silent skip or pass occurred. Finishing command **in an already-capable
environment**, with a newly owned short TEMP/TMP/TMPDIR and qualified Git PATH:

```powershell
Push-Location scripts/tests
& $p -B ../run.py --idle 120 --max 1800 -- $p -B -u -m unittest test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects -v
Pop-Location
```

Parent can now review this **bounded verified-with-limitations basis**.
Parent acceptance/review, full Q2 collectors/reconciliation, Q3/Q4/Q5,
successful guarded metric attachment, recovery, human approval and publication
are not completed here. No agents, installs, privilege changes, production/test
body/shared-state edits, commits or pushes occurred in r2.

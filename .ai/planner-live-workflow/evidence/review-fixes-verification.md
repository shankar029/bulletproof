# Targeted independent verification of review fixes

**PASS for the targeted R3/R4 checks. AC4 and G6 remain BLOCKED.**
UNADOPTED PROCEDURAL / unbound evidence, never receipts. This records new,
narrow evidence; it does not overwrite or adopt prior independent review
judgments. No production, tool, runtime, infrastructure or README edits were
made by this verifier. Only base-flow assertions and task evidence were added.
The earlier independent full review predates the final changed bytes. This
follow-up is **targeted independent verification, not a fresh full review**.

## Executed results

| Check | Observed result |
|---|---|
| Missing `E2E_PYTHON` | Real harness invocation exited 1 with the actionable configuration error. The complete `.work` entry set before/after was identical: no fixture/output directory created, no browser started. |
| Explicit interpreter | All 197 recorded commands used the supplied managed Python 3.14.2 executable through root `scripts\run.py`; all exited 0 without timeout. |
| Initial guidance state | Guidance exists but is hidden and not rendered; lifecycle control enabled. |
| Edit | Guidance is rendered with exact actionable text; lifecycle disabled; `aria-describedby="lifecycle-guidance"` associates the explanation. |
| Cancel | Editor removed, guidance hidden/not rendered, lifecycle re-enabled; reopening proves the unsaved title was discarded. |
| Reopen/save | Reopening restores the guidance and disabled control; successful save removes the editor, hides guidance and re-enables lifecycle. |
| Existing base regression | **67 passing named check records**, including six added review-fix checks; flow VERIFIED, exit 0. Refresh/restart, conflicts, keyboard, layout, HTTP boundaries and network recovery still pass. |
| Browser errors/a11y | Final console and uncaught errors empty. Existing editor axe checks report no violations or incomplete checks; not full WCAG/human certification. |
| Downloads | **Zero** download commands, wait-download commands or interactions targeting the CSV control. No transport experiments. |

One browser base run:
`e2e-2026-09-18T09-11-13-615Z-51071082`, starting 2026-09-18T09:11:13Z.
The harness aggregate status is `VERIFIED_WITH_LIMITATIONS`; it does not imply
AC4/G6 closure.

The first configuration-test assertion incorrectly expected child stderr to
remain stderr through root run.py, which intentionally merges its output.
The underlying invocation already failed correctly with exit 1 and no fixtures.
Only that test was repaired to inspect the combined captured output and reject
browser/fixture startup markers; its rerun passed. Both the initial test error
and initial child result are retained. No browser rerun or production repair
was needed.

## Timeout ownership review and limits

**Source-level inspection:** `scripts\e2e.mjs::command` passes root run.py
`--idle 25 --max <bound>`; root run.py owns the deadline. The former competing outer
kill timer and abort-signal deadline are absent. The helper waits for the
wrapper's exit; removal from `active` requires a non-null `exitCode` or
`signalCode`. The fresh base run exercises this path successfully with the
explicit interpreter. README documents the required configuration and runner
ownership.

**An absolute-deadline timeout was not exercised.** No new timeout or download
trial was added; exactly the one targeted base browser rerun above was executed.
This is targeted source review plus normal-exit execution proof, **not** a
forced-timeout or descendant-cleanup stress test. Spawn failure/hung-wrapper
behavior was not newly exercised. Original review fixes now have targeted
independent proof within the tested scope; original AC4/G6 blockers and other
unverified cases are unchanged.

## Evidence and commands

- [Base report](e2e-2026-09-18T09-11-13-615Z-51071082/report.json), with adjacent exact command logs, HTTP records, screenshots and snapshots.
- [Base stdout](review-fixes-base-output.txt).
- [Configuration test](review-fixes-config-check.mjs), [result](review-fixes-config-result.json), [passing output](review-fixes-config-output.txt).
- [Initial test-only error](review-fixes-config-initial-test-error.txt) and [initial child result](review-fixes-config-initial-result.json).
- [Exact current hashes, six assertion payloads, command and cleanup summary](review-fixes-summary.json).

From repository root, using the supplied managed executables:

```powershell
$env:E2E_PYTHON = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $env:E2E_PYTHON scripts\run.py --idle 60 --max 90 -- 'C:\Program Files\nodejs\node.exe' .ai\planner-live-workflow\evidence\review-fixes-config-check.mjs
$env:E2E_EVIDENCE_DIR = Join-Path (Get-Location) '.ai\planner-live-workflow\evidence'
& $env:E2E_PYTHON scripts\run.py --idle 120 --max 600 -- 'C:\Program Files\nodejs\node.exe' examples\team-planner\scripts\e2e.mjs --flow base
```

The configuration test unsets `E2E_PYTHON` only in its child environment and
invokes the genuine base harness through another root runner with idle 25/max
40 bounds. No dependencies were installed; Playwright performed launch/close
only and all UI interactions/observations used agent-browser.

## Exact source binding

All 12 production files match their run-start hashes at final review; the
configuration invocation and browser run used the same harness hash listed
below. A subsequent label-only correction is bound separately in the addendum.
Paths below are relative to `examples\team-planner` except root `scripts\run.py`.

```text
scripts\e2e.mjs  06a8af2a2c8d48ecec9df151fd46842452d35a5c1a990919851aba7f64fb7532
README.md        f63f58ff4611dc074e61374d9fa53e79c4a56a1bbfc132250958202b02e3c454
src\csv.mjs      4b873fd1f296172532dd8c45085683ab529eddedf1d2bdaa96493c4d77c994f9
src\errors.mjs   241e92aa4d6634e11cf4b718226f8402367275e1e352eb90b03e60d844a1943f
src\main.mjs     13e1fa9a67f4ea09c2268e6f24fc1c4504796857728489804eee9487f3085328
src\migrate.mjs  f2da0b8be6354c363e9a6c965ab830be914a7bcc9ee080f40cbddaecc7fce898
src\planner.mjs  f91a9c0e3ad5af944f938917d31f54e3c7b8fcfe267c3acdd8a778fee5dfc221
src\rules.mjs    0cf8710fc8f4a0e7b7db1ac39e6ca8652eb88e00f1db1f393217ead48a121aaf
src\schema.mjs   288f4b9009aca3237852bd472d8d20d328251a8818d0eca4f9c14c0c7bb42a53
src\server.mjs   ca78205e4b1a2c38d31208a6f154b5a8a91703cdc3c16a56b681e1d1e2885bee
src\store.mjs    fdfa9959c270aa3ee2ec8ac8f77ac08a5306023c9d4ed8247e8fe0fe611f7c88
public\app.mjs   009d62ecb85fe0dfa789d4e5bb58e2a6127f5fb20578b39758b74b6331f67677
public\index.html cf2b5536b996f6fea0a28c37b7e1519afe82c920ad400536c7532813aea929ba
public\styles.css 4de10c95665d143e5a1956bc34d284e0c776a988a96371d5c9b1179ce0801f92
root scripts\run.py 7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e
```

Both owned app processes (PIDs 44640 and 50388) exited 0, were absent at the
cleanup check and left no writer locks. Stop/restart assertions checked the old
listeners were closed. Browser close and launch-server close reported no errors;
the owned profile was removed. Isolated fixture/evidence data is retained.
No recursive agents, commits, publication, adoption or receipts.

## Subsequent assertion-label correction

Renamed the archive negative check to
`Download wait reports failure after aborted export`. It asserts only
`result.success === false`; the timeout diagnostic assertion and separate
actual no-file, blank-success-notice and focused-error checks are unchanged.
It does **not** establish absence of a browser download event.

Current harness SHA-256 after this wording-only edit:
`fd1eb61bbb79de90d0fad8be2842b12485938a0cb350746a0b5ede84bcb24d10`.
Reversing just that string replacement in memory reproduces the exact tested
harness SHA-256
`06a8af2a2c8d48ecec9df151fd46842452d35a5c1a990919851aba7f64fb7532`,
proving no other harness change in this follow-up. The new label occurs once;
the old label no longer occurs in the current harness.

No archive/download or other browser rerun was performed for this label change.
Prior logs, report hashes and `review-fixes-summary.json` remain the immutable
record of the earlier tested source, not a claim that the new hash was executed.
AC4/G6 remain blocked; evidence remains UNADOPTED PROCEDURAL.

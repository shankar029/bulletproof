# C2a local implementation handoff — frozen for parent verification/review

## Scope and status

FACT: implemented only the approved `run_capture(..., *, env=None, observe=None)`
seam in `scripts/run.py`, with native tests in `scripts/tests/test_run.py`.
All other owned files have the additive `evidence/c2a-` prefix. No agent,
installation, commit, push, CLI/ledger implementation, shared state/report edit,
or historical evidence rewrite was performed. Parent `state.md` edits and the
pre-existing `evals/report.md` delta are deliberately outside these pins.

This is implementation-role evidence, **not C2 completion or independent
acceptance**. The accepted C1/Q1 commit is
`5dabb4ca27a440ad370fbcb1be1739ed52e38ab7`. Its 121 independent methods are
historical; the changed runner reopens affected dependency proof. This handoff
does not repeat or replace that qualification, full quality/mutation, or the
parent's separate verifier/reviewer.

## Source delta and contracts

- Added synchronous plain-dictionary ProcessObservation notifications:
  `launch-failed` on actual Popen failure, `spawned` immediately after Popen,
  `direct-exited` after actual wait. Exact nine approved fields, no alternate
  schema, record/engine imports or new dependency.
- PID is the actual child PID; Windows group is null. Unix group is the new
  session established by the unchanged `_popen`. Creation identity and evidence
  are explicitly null; no supported identity collector has been added.
- Default/explicit-None capture keeps `(rc, stdout, stderr)`, env/cwd, exact
  normal output and existing timeout markers/codes. `_popen`, `_kill_tree` and
  CLI `main` are unchanged.
- Callback `Exception` yields rc 125 and `[observer-error] PHASE: TYPE: detail`;
  any original stderr/timeout marker is retained. A spawned callback failure
  immediately invokes existing owned cleanup, drains/reaps the direct child,
  and offers a real `direct-exited` observation. Further observer failure
  remains explicit non-success, not a successful receipt.
- Direct-exit callback failure invokes the same cleanup helper against the
  owned Popen object, but its direct child is already reaped. The helper
  deliberately no-ops rather than targeting a potentially reused PID.
  **No effective descendant cleanup is established for this case.** The emitted
  exit event describes facts before callback failure (`cleanup=not-attempted`
  for a normal exit); no synthetic replacement event is sent to a failing
  observer. The returned observer-error tells the future caller not to issue
  successful completion.

## Local observed checks

| Evidence | Actual result | What it proves |
|---|---|---|
| `c2a-red1.json` | 2 tests, 2 expected errors, exit 1 | Before implementation, `observe` was rejected as an unknown keyword. These are missing-API regressions, not child assertion failures or mutation kills. |
| `c2a-green1.json` | **16 passed**, 0 failed/errors/skips, exit 0 | All 5 original runner tests plus 11 new lifecycle/compatibility tests. |
| `c2a-callers1.json` | **3 passed**, 0 failed/errors/skips, exit 0 | Real `mutate.run` / `probe.run` calls preserve cwd, spaced argv, env, exact output/nonzero exit, missing-executable results and actual probe trace. |
| `c2a-diffcheck1.json` | exit 0, empty output | Scoped `git diff --check`; not lint/type/coverage proof. |

**Total positive local inventory: 19 test methods**, not 19 additional methods
on top of the runner 16. Timeout subcases are not counted as extra methods.
There were no outer command timeouts/retries. Intentional inner idle/max kills
are successful timeout scenarios, not harness blockage.

The real rendezvous child writes its PID and waits for a filesystem release.
The spawned callback checks that PID against a retained Windows process handle
and releases the child only after checking liveness. Normal completion writes
a separate sentinel. Cleanup tests leave the release absent, observe the same
owned handle signalled, and assert no completion sentinel. Tests do not infer
death from elapsed sleep. Actual observed PIDs/events are in raw stdout.
OSError injection is solely at the public callback seam: it represents a
persistence failure, **not actual disk-full/ledger/crash recovery proof**.

Self-review covered the source diff, callback error precedence over successful
child exit, fresh event dictionaries, null identities, timeout/direct-exit
distinction, default output preservation, and unchanged standalone callers.
No independent review verdict is claimed.

## Exact replay (PowerShell, repository-root cwd)

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -B scripts\run.py --idle 60 --max 180 -- $py -B -m unittest scripts.tests.test_run -v
& $py -B scripts\run.py --idle 60 --max 180 -- $py -B .ai\workflow-reliability\evidence\c2a-callers.py
& $py -B scripts\run.py --idle 30 --max 60 -- 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe' --no-pager diff --check -- scripts/run.py scripts/tests/test_run.py
```

Raw capture used an outer `scripts/run.py --idle 75 --max 210 -- $py -B
.ai\workflow-reliability\evidence\c2a-capture.py TAG COMMAND...`; the capture
driver ran each literal recorded argv with `run_capture(idle=60,max_total=180)`
and the literal cwd/env recorded in its JSON. Tags: `red1`, `green1`, `callers1`,
`diffcheck1`. Capture refuses overwriting a tag; use a new tag to replay. The
red run's literal two test selectors are in `c2a-red1.json`; on current code
they pass, not reproduce the historical missing-API failure.

## Hashes and freshness

| File | Before C2a SHA-256 | Final SHA-256 |
|---|---|---|
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` | `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e` |
| `scripts/tests/test_run.py` | `3a892cc5268352926afb665d32d0f0a6d897a27db19626a03c7656f2dcfa16bf` | `92bedd163977112eff3efd3cfbad5fc9aaa9fe9a2318dd2aad832903914b85e5` |

Each raw capture includes before/after input hashes and literal argv/cwd,
exit, stdout/stderr. `c2a-freeze.json` is the final bounded input/evidence
manifest with Git observations and source comparisons. This is not an
exhaustive frozen machine or all-dependency qualification.

The capture helper changed after `green1` solely to include the newly added
caller smoke file in subsequent pins; the historical helper hash remains
honest in `green1`. Runner/tests did not change after that green run. Final
freeze excludes only this disclosed helper delta when reconciling green1;
it does not silently call every historical pin unchanged.

## Limits / parent next action

Windows CPython 3.14.2 was executed. Unix group assignment/cleanup and other
platform/runtime branches are **not execution-verified** here. Tests observe
direct-child termination only, never full descendant death. Synchronous
callbacks must return promptly and are not governed by capture's monitor
timeouts; existing best-effort kill/wait behavior is not a new supervisor.
Null identities cannot authorize recovery. Durable intent, unresolved ledger
state, crash intervals and all six CLI verbs remain parent-owned future C2
work. No publication or whole-request completion is claimed.

Parent next: dispatch separate focused verifier and read-only reviewer against
these frozen bytes, including the conservative direct-exit cleanup boundary,
then accept/reject this sub-slice before CLI integration.

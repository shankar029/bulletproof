# Final bounded Q1 attribute-gate correction

**LOCAL GREEN — frozen for narrowed independent replay/re-review.**
This is the single residual R2 admission-contract correction from
`q1-code-review-final.md`, not a restart or overall Q1/release acceptance.

## Minimal production delta

Only `scripts/measure.py`, the nested `attributes` function at lines 133–154,
changed. `measure_graph.py`, `probe.py`, all previous tests and reports remain
unchanged. The exact single-hunk diff against archived predecessor bytes matching
the reviewer's `753fca9e…` hash is `q1-attr-measure.diff`; its source archive/member
and hashes are recorded in `q1-attr-final-freeze.json`.

The gate now uses **Git-native `check-attr --cached --all -z -- <paths>`**.
Unlike explicit named queries, this omits genuinely unspecified attributes but
retains literal values named `unset` or `unspecified`. The decoder validates
triples, requested paths and duplicate records, ignores unrelated attributes,
and retains only qualified text/EOL values for the six controlled transformation
attributes. No `.gitattributes` parser, framework, policy relaxation or new
Context/schema field was introduced.

**Explicit conservative boundary:** present `unset`/`unspecified` values are
ambiguous, not proof of disabled/absent state. They reject with
`unsupported attribute ... (ambiguous present declaration)`.
Consequently `-filter` is explicitly unsupported rather than silently admitted.
The same rule applies to ambiguous disabled forms of the other controlled
transformation attributes, including `-text`. Genuinely absent/reset attributes
remain accepted. Qualified positive text/EOL behavior remains covered.

## Actual qualification and pre-fix evidence

The same Git **2.53.0.windows.4 core plus 69 DLLs** remained unchanged.
Only five narrow qualification commands ran: check-attr help, no-checkout clone,
read-tree, explicit named query and cached all-attribute query. Literal argv,
controlled environment and original stdout/stderr bytes are retained in
`q1-attr-qualification.json` / `q1-attr-qual-*.bin`.

Observed cached all-attribute output:

- Absent and `!filter` reset: omitted.
- `filter=unset`: present as `filter / unset`.
- `filter=unspecified`: present as `filter / unspecified`.
- `-filter`: present as `filter / unset`, indistinguishable from the literal.
- A macro expanding to `filter=unset`: includes the effective filter value.
- No subject files had been checked out during this qualification.

The preserved **pre-fix red run** executed four methods in **60.597 seconds**:
six failing subtest assertions, zero errors/skips. Four failures reproduce the
two literal names at both materializer/validator boundaries. Two assert the new
conservative disabled-filter diagnostic. The absent/reset positive passed.

For each literal name, both old boundaries accepted while the sentinel stayed
absent. Configuring that exact named driver on the owned target and explicitly
checking out then executed the sentinel. This is **admission-contract proof, not
an execution escape or false-overall-green observation**.

## Focused final executions

| Capture | Methods | Actual result | Unittest seconds |
| --- | ---: | --- | ---: |
| `green` | 4 new attribute methods | PASS | 53.899 |
| `macro` | 1 existing macro/filter/sentinel control | PASS | 11.080 |
| `eol` | 1 existing neutral/versioned EOL/mode control | PASS | 16.712 |
| `unsupported` | 1 existing unsupported-transform/type control | PASS | 28.485 |
| `probe` | 19 shared legacy probe regressions | PASS | 60.361 |
| `cli` | 1 configured CLI all-nine/raw-archive control | PASS | 32.098 |

**27 focused methods passed**, with zero failures, errors, skips or timeouts.
The two literal driver tests now reject at both boundaries, preserve sentinel
nonexecution during isolation, and retain successful explicit positive controls.
One implementation attempt; no full-suite retry or broad new investigation.
The earlier independent 74-test and parent C1 93-test results were neither rerun
nor represented as results on these new bytes.

Commands use managed Python with `-B`, `PYTHONDONTWRITEBYTECODE=1`, and
`scripts/run.py --idle 120 --max 1200`. Every capture has its literal command,
source/runtime before/after pins, result JSON and raw stdout/stderr. New tests are
`scripts/tests/test_measure_q1_attr.py`; predecessor tests were not edited.

## Freeze and preservation

| File | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084` |
| New `scripts/tests/test_measure_q1_attr.py` | `a3c02ac34df6bec9dc05d790567a7e79620c555950ae9fa63cb123719c3a43f0` |
| Unchanged `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| Unchanged `scripts/probe.py` | `668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083` |

Finalization verified **465 frozen inputs/artifacts**, **2,747 initially pinned
protected files unchanged**, all recorded raw hashes, and all **85 recorded
temporary paths absent** after cleanup. The protected set includes the new test
seeded before red; all predecessor tests/reports are included and unchanged.
Scoped compilation succeeded. Root HEAD remains
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`, feature branch remains
`shbs-microsoft-workflow-app-verification`, and the index is empty.

Primary machine-readable handoff: **`q1-attr-final-freeze.json`**.
No shared-state/C1/C2/Q2 changes, installations, nested agents, commits or
publication occurred. Existing platform, ownership and non-atomic-observation
limits are unchanged. Parent selects the affected independent checks and owns
the final narrowed re-review.

For a fresh focused replay, use a new short label (do not overwrite captures):

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py -B scripts\run.py --idle 120 --max 1200 -- $py -B .ai\workflow-reliability\evidence\q1-attr-capture.py capture test_measure_q1_attr.py pv
```

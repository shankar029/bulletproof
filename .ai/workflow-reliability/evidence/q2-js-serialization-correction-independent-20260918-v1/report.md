# Independent R1/R2 correction revalidation

**Corrected behavior verified in the requested seven distinct methods.**
This is bounded native-library proof, not complete Q2 acceptance or a green combined run.
No source/test changes were made by this verifier.

## Fresh results

| Capture | Methods / outcome | unittest time | Exit |
|---|---|---:|---:|
| `independent/` — entire unchanged independent module | **3/3 PASS** | 103.513s | 0 |
| `owner/` — four requested owner methods | **3/4 PASS**; candidate capturer 124 `[idle-timeout]` | 208.240s | 1 |
| `owner-candidate-retry/` — sole bounded retry | **1/1 PASS**, same candidate method/bytes/bounds | 65.948s | 0 |

**Seven distinct methods have passing evidence across eight method invocations.**
There were eight nested native calls (seven returned 0, one returned 124), not eight
additional tests. All successful native calls had empty stderr; no skipped/empty success.
No assertion failure remained in the corrected selection. The candidate timeout emitted
no native stdout or result, so it is neither behavior proof nor an accepted successful run.

The retry changed only selection/capture/temp fixture locations; source/test bytes and bounds
were unchanged. A read-only exact-native-script process observation found no matching command
line after the failed suite. Full descendant cleanup remains **UNKNOWN**. No process killing,
privilege changes, timeout increases or unowned-temp cleanup occurred.
The owner's separately sealed timeout/retry remains historical, not counted here.
Its recurrence in this fresh run is an unresolved **test reliability limitation**.

## Corrected observations

- **R1:** Both original independent shorthand/literal-key assertions now receive the exported
  property ID. Distinct local binding IDs and the checker/ordinary-property positive controls
  remain intact. Both cases have processed census and zero compiler diagnostics.
- **R2:** `import('./origin.mjs', {})` now emits literal syntax and a local module reference to
  `origin.mjs`, with no computed-import site. One-argument literal and genuinely computed
  controls remain intact; zero compiler diagnostics.
- Original merged declarations/import-equals/namespace-reexport test refreshed unchanged.
- Four owner methods refreshed: `test_native_review_corrections_uncertainty_and_require_arity`,
  `test_native_serialized_source_records_and_origins`,
  `test_native_serialized_freshness_and_identity`,
  `test_native_candidates_from_shared_syntax` (last one via retry).
  These retain known/computed/rest/unresolved selection evidence, require-arity/shadow controls,
  records/origins, freshness and candidate byte-identity checks.

Source inspected: `measure_js.mjs:485–501,665–669,707–728`;
supplemental owner assertions `scripts/tests/measure_js.test.mjs:85–132`.
Independent assertions remain pinned to
Python `8917a3d561ed01afc6d2dcb5abc39af1cf232d8e8741283e6818e12156aae4e5`,
native test `fba787cf2e7e0806eea8f2801d87f168b9e1e3facd361b941b1534ba921942c7`.
This directly closes the observed R1/R2 red cases, not all possible native edge cases.

## Reproducibility and evidence

Each directory's `invocation.json` records exact argv/cwd/environment. Common prefix:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -B -u scripts\run.py --idle 120 --max 900 -- $py -B -u -m unittest discover -s scripts\tests <selection>
```

Selections:
1. `-p test_measure_js_serialization_independent.py -v`
2. `-p test_measure_js.py -k review_corrections -k serialized_source_records -k serialized_freshness -k candidates_from_shared_syntax -v`
3. Retry only: `-p test_measure_js.py -k candidates_from_shared_syntax -v`

CWD was the requested worktree. Git PATH prefix was
`C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd`;
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`; `Q2_JS_RECORDS` was each exclusive
capture directory. Native bounds stayed **idle30/max90**, outer **idle120/max900**.
Existing short owned OS-temp fixtures and qualified Node v24.11.1 ARM64/TypeScript 5.9.3
were used without install or requalification.

`stdout.bin`, `stderr.bin`, `exit.json` were persisted before interpretation; output parsing
used UTF-8 `splitlines()` (CRLF-safe). `run.py` merges child stderr into wrapper stdout.
Nested `run_capture` strings retain its existing UTF-8 replacement decoding/newline normalization,
not original wire bytes. Independent native result bytes were saved before parsing.
The frozen owner harness's existing result-parse-before-record behavior was not changed.

## Freeze reconciliation and stop

Before both selections, before retry and after all execution, **223 unique new-seal/catalogue
paths matched**, including all 199 preservation-catalogue entries and correction/history
records. `before*.json` and `after.json` retain the matching catalogue identity, compact
source/test hashes and zero mismatches; original archives are referenced, not recopied.
HEAD remains `8881a7e667695345328852ab39157988f9fd868d`.
Correction seal remains
`c138dec76b7abc47b334caf5e77e99236154583bf745573312c8b5d44a04fa5b`.
Native source remains
`ba0ca909699ca453515a0eaad5206c81d5afe6abcd1fb7b47723e8a71f1c0900`.
The retained pre-fix source hash is still
`35acb58ccd11dce9daa601e640c47b763e8625c84919158610cf33107f4b46bc`.
Original red assertions/results, rejected empty attempt, previous green captures and owner
timeout/retry were preserved. This new seal does not overwrite earlier seals.

JS-SYMBOL-01 / JS-PARSE-01: **R1/R2 corrected cases VERIFIED; overall accepted IDs PARTIAL**.
Command/manifests/graph/replay/scalars/metrics/recovery/full-quality/live-model remain
**NOT IMPLEMENTED / NOT VERIFIED** by this checkpoint. No full15/root suite/probe/mutants,
hosts, agents, packages, commits, C4 or pipeline expansion. Independent review approval is
for the same reviewer to reconcile, not claimed here.

**Stop:** deliver this proof to the parent/reviewer. Subsequent priority is the actual
app-driven workflow, not additional pipeline work; that workflow was not exercised here.

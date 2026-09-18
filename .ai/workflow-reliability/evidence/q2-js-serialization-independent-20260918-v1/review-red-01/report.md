# Bounded red handoff: independent review R1/R2

**Both P2 findings reproduced on unchanged frozen production. Correction is not authorized
or implemented by this verifier. Stop and return to parent.**

The prior frozen 15-method replay (354.598s) and one merged/import-equals/namespace-reexport
method (31.425s) remain preserved, not rerun or relabeled. This new evidence reopens the
native correctness assessment: those green cases do not cover or negate R1/R2.

## Discriminating observed failures

Corrected focused invocation: **2 Python methods, 2 failures, 70.376s, outer exit 1**.
Each method invoked one actual Node test; each native test returned 1 with empty stderr,
one test/one failure/zero skips. Nested tests are not additive Python method counts.
Both fixtures use real Git/materialized inputs, the existing qualified Node v24.11.1 ARM64
and TypeScript 5.9.3, copied hash-checked native controller, real Program/checker, processed
source census and **zero compiler diagnostics**. No mock, expected-failure decorator or
timeout-as-behavior proof.

### R1 — both namespace destructuring selections omit the exported property

`origin.mjs`: `export const value = 1;`

```js
import * as ns from './origin.mjs';
const { value } = ns;
const { "value": local } = ns;
export const answers = [value, local];
export const control = ns.value;
```

The real checker resolves the `value` property of each initializer to the exported
declaration; each local BindingElement has its own distinct serialized ID.
The ordinary `ns.value` control resolves to the export ID. But serialized property-use
targets within the two destructuring declarations are **`[[], []]`**, not the expected
two singleton export-ID lists. Neither selection carries an outside-model uncertainty site.

Export ID observed:
`367749885dc4e5bf2d08d70a641c5fdf5420522e3e91daa35e1df14901184134`.

The failing assertion is
`scripts/tests/measure_js_serialization_independent.test.mjs:209–210`.
Evidence: `corrected/review_r1.result.bin`, `.capture.json`, `.invocation.json`.
The result includes selections, distinct binding IDs, checker agreement, serialized
references and the positive-control outcome before the discriminating assertion.
This supports the reviewed source cause at `measure_js.mjs:689–708`: binding names are
not property-read references, and the literal-key branch has no corresponding read edge.

### R2 — literal dynamic import plus empty options misclassified as computed

```js
export const plain = () => import('./origin.mjs');
export const options = () => import('./origin.mjs', {});
/** @param {string} name */
export const computed = name => import(name, {});
```

The one-argument literal control resolves locally to `origin.mjs` with literal syntax.
The genuinely computed control retains dynamic/no-target semantics and its computed site.
The options case incorrectly emits:

```json
{"specifier":null,"kind":"import","resolution":"dynamic","targets":[],
 "external":null,"reason":"Computed module specifier"}
```

It has **zero literal syntax records and one computed-import site**.
Expected: literal `./origin.mjs`, local target `origin.mjs`, matching literal syntax, and no
computed-import site. All three differences fail together in one discriminating assertion
at `scripts/tests/measure_js_serialization_independent.test.mjs:239–248`.
Evidence: `corrected/review_r2.result.bin`, `.capture.json`, `.invocation.json`.
This confirms the reviewed source cause at `measure_js.mjs:656–659`: arity other than one
passes null instead of the actual literal first argument.

## Invocation and preserved correction history

CWD: `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.
PATH prepended with `C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd`;
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`;
`Q2_JS_RECORDS` points to this directory's absolute `corrected` subdirectory.

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u -m unittest discover -s scripts\tests -p test_measure_js_serialization_independent.py -k ReviewRegressions -v
```

Native bounds remained **idle 30/max 90** and fixtures used uniquely owned short OS-temp
roots. Outer argv/cwd/env and executing test hashes are in `corrected/invocation.json`.
Wrapper stdout/stderr bytes and return code were persisted before interpretation;
per-native returned streams/returncode and undecoded semantic result were saved before
JSON parsing. Existing `run_capture` normalizes newlines and replacement-decodes UTF-8;
its returned stream strings are not original wire bytes. `run.py` merges the unittest
child's stderr into wrapper stdout, as previously disclosed.

**One verifier harness correction, fully retained:** initial registration was accidentally
nested inside the unselected earlier test. The initial command printed 2 Python passes in
52.732s but both native captures were empty and produced no result: **REJECTED EMPTY RUN,
NOT proof**. Its raw `stdout.bin`, `stderr.bin`, `exit.json`, per-case captures, invocation
and `registration-error-*.snapshot` remain in this directory.
The verifier moved only its new registration to top level and added mandatory native
result/runtime/case/controller/count checks. It reran only these two regressions once
into exclusive `corrected/`, yielding the two actual assertion failures above.
No timeout or production/owner-test correction occurred. No further rerun.

## Freeze, retained proof and handoff

All **68** previously reconciled frozen production/doc/owner-test/authority/evidence paths
and five qualification references match before and after; see `before.json`, `after.json`.
Original frozen seal remains
`c43769d83411dd41063be59a77e87918991673f360ec8b759f1a22558bc528da`.
Actual native qualified-input digest remains
`635539f7f194d17ba256f6a774949a12e3191f53796a5e02db17736462b03e88`.

The prior verifier `../seal.json` and all its 34 evidence files remain byte-identical.
Its two test-file references describe the earlier green test versions: those exact bytes
are archived here as `prior-*.snapshot`, matching the original seal. Only the two
verifier-owned test files have since been extended, with the earlier test retained.
The new seal pins the current extended tests and distinguishes the historical versions.
No historical report/seal has been overwritten.

**Accepted IDs:** JS-SYMBOL-01 and JS-PARSE-01 now have concrete native FAIL cases,
not merely missing future integration. All other acceptance limitations remain:
fixed command/manifests/graph/replay/scalars/metrics/recovery/full-quality/live-model
work is NOT IMPLEMENTED / NOT VERIFIED by this handoff. No complete acceptance,
Phase 6, live app or fresh-agent workflow proof is claimed.

No production/owner-test edits, agents, qualification/install, broad suite/probe/mutants,
live hosts, C4, commits or pushes. Parent may authorize owner correction after this handoff;
the ordinary-discoverable tests deliberately remain failing until defects are fixed.

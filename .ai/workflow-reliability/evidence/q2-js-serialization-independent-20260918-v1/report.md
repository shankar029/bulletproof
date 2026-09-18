# Independent Phase 5: native serialization/candidates

**PASS for this bounded native-library verification only. NOT complete Q2 acceptance.**

## Independently observed results

| Invocation | Python methods | Nested native calls (not additional methods) | Result |
|---|---:|---:|---|
| Frozen `test_measure_js.py`, one replay | 15 | 13 | PASS, 354.598s, outer exit 0 |
| New `test_measure_js_serialization_independent.py` | 1 | 1 | PASS, 31.425s, outer exit 0 |

All 14 nested calls returned 0 with empty stderr. Captured runtime: Node v24.11.1
ARM64; qualified existing TypeScript 5.9.3. Every native call retained idle 30/max 90.
No skips, empty success, test-class inheritance, mocks, timeouts, retries or production
corrections. No qualification rerun or install. Elapsed outer capture times were
355.374s and 32.188s; these include process overhead, unlike unittest times above.
No defect was observed in these exercised cases; this is not an exhaustive correctness claim.

The new **one-method/one-fixture** test covers only the confirmed gaps in `coverage.md`:

- Real class+namespace and interface declaration merges, each producing one local ID with
  two source declarations, actual checker flags, source-backed CRLF spans, and independent
  Python recomputation of the canonical symbol ID.
- External-module `import model = require('./origin.js')` and internal-qualified
  `import Item = model.Parcel`: actual checker aliases, typed serialized local targets,
  constructor/type/property references, and literal require edge to the inventoried `.ts`.
- `export * as bundle`: checker-backed namespace reexport and alias share the origin
  module's serialized SourceFile identity; consumer import/property targets agree;
  reexport module edge matches SyntaxEvidence.

The fixture has real base/head Git revisions and at least three Python baseline files.
It invokes the real copied native library through a real Program/checker, not a fake
transport or an accepting measurement consumer. Its fixture diagnostics are empty.
Definitions/assertions are in the two newly owned files:
`scripts/tests/test_measure_js_serialization_independent.py:19–117` and
`scripts/tests/measure_js_serialization_independent.test.mjs:14–142`.

## Exact execution and evidence

CWD for both outer invocations:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.
Environment: prepend `C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd` to PATH;
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`; `Q2_JS_RECORDS` is the absolute path
to this exclusive evidence directory. Existing fixtures and the new `qji-*` scratch
use short, uniquely owned OS-temp roots, not worktree-nested roots.

Exact frozen replay:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u -m unittest discover -s scripts\tests -p test_measure_js.py -v
```

Exact new gap test:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u -m unittest discover -s scripts\tests -p test_measure_js_serialization_independent.py -v
```

`capture.py` persists argv/cwd/environment intent before launch, raw outer stdout/stderr
bytes and exit results before interpretation. `replay-*` and `independent-*` records
contain exact arguments and hashes. Parsing used UTF-8 `splitlines()` (CRLF-safe).
The fixed `run.py` CLI merges its child's stderr into stdout; outer empty stderr is
not separately asserted as the inner unittest stderr. Frozen native records preserve
the existing `run_capture` returned stdout/stderr separately. That helper decodes
UTF-8/replaces errors and normalizes newlines; they are **not original wire bytes**.
The frozen harness parses its native result before persisting its combined record;
it was not modified. The new test additionally saves returned streams/returncode and
raw result bytes **before** parsing the native result. No stronger nested byte-capture
claim is made. See `scripts/run.py:98–200`, `scripts/tests/test_measure_js.py:54–79`,
and the new Python test lines 94–107.

## Freeze reconciliation

Observed HEAD: `8881a7e667695345328852ab39157988f9fd868d`.
Original seal SHA-256 verified before and after:
`c43769d83411dd41063be59a77e87918991673f360ec8b759f1a22558bc528da`.
**All 68 unique sealed/transitively sealed paths match before and after**:
all original owned source/doc/test/evidence and the three authorities, plus executing
collaborator pins read from the sealed final native record. `before.json` and `after.json`
contain exact observed hashes/lengths. Original contract, root amendment and accepted
JS revision 3 retain the seal's exact pinned bytes.

In particular `measure.py`, `measure_graph.py`, `probe.py`, `evidence.py`, `run.py`,
the original tests, `measure_js.mjs` and `references/quality-metrics.md` were not changed.
Five existing qualification archive references also match before/after. All 14 actual
native invocations matched the existing qualified-input digest
`635539f7f194d17ba256f6a774949a12e3191f53796a5e02db17736462b03e88`;
existing archives/resource descriptions are referenced, not recopied/requalified.
`seal.json` pins this report, the new tests, captures and reconciliation records.

Workspace observation records pre-existing owner changes and unrelated `evals/report.md`.
Only the two requested new test files and this evidence directory were written.
The new files passed direct trailing-whitespace/final-newline checks and Python AST parsing.
The recorded `git diff --check` returned 0 but does not check untracked files; it is not
used as their whitespace proof. No broad lint/build/quality claim follows.
Documentation-only correction: coverage-map line references were replaced with exact
method names; no executed test/source changed and no execution retry was needed.

## Accepted-ID partial mapping

| Accepted ID | Independently observed native evidence | Disposition / missing integrated proof |
|---|---|---|
| JS-LIFE-01 | two-revision census; serialized freshness/head-only roots | PARTIAL ONLY: measure-owned sequencing, base union/collision reservation and three manifests NOT IMPLEMENTED / NOT VERIFIED |
| JS-LIFE-02 | none | NOT IMPLEMENTED / NOT VERIFIED: validate-purpose execution, semantic replay, output policy and archive admission |
| JS-OWN-01 | controller-copy identity, source/config/parser freshness and candidate syntax/inventory mismatch rejection | PARTIAL ONLY: manifest chain/control ownership, result/purpose tamper/replay/post-archive enforcement NOT IMPLEMENTED / NOT VERIFIED |
| JS-PARSE-01 | byte boundaries, six suffixes, native syntax/candidates/current source copies, empty serialization | PARTIAL ONLY: native cases PASS; production transport/graph consumption NOT IMPLEMENTED / NOT VERIFIED |
| JS-SYMBOL-01 | original records/origins/freshness plus new merged declarations/import-equals/namespace-reexport fixture | PARTIAL ONLY: exercised native cases PASS; accepting consumer, rehashed semantic tamper/replay and complete dead-symbol proof NOT IMPLEMENTED / NOT VERIFIED |
| JS-DIAG-01 | original compiler/checker/failed-input/directive tests replayed | PARTIAL ONLY: command-output admission and rehashed diagnostic/receipt consumer tests NOT IMPLEMENTED / NOT VERIFIED |
| JS-COMPAT-01 | original inventory/controller/default library checks and actual-source syntax/candidates | PARTIAL ONLY: integrated mixed configured-probe/no-JS lifecycle NOT VERIFIED |

Source-backed boundaries: `measure_js.mjs:1–4,200–212,430–459,477–573,654–688,862–956`;
`references/quality-metrics.md:72–81`; accepted revision-3
`type_rules.resolution_rules`, `records.JSSymbol`, `records.JSAlias`, `records.JSExport`,
`identity_and_projection` and JS-SYMBOL-01. These support a native serializer/candidate
library, **not** the accepting Context/manifest/MetricObservation lifecycle.

Fixed command/manifests/graph/replay and missing scalar/metric collectors remain
**NOT IMPLEMENTED / NOT VERIFIED** in this increment. Guarded metrics/recovery,
full-quality closure and live-model/fresh-agent workflow proof remain
**NOT IMPLEMENTED / NOT VERIFIED** by this work. No root suite/probe/mutants,
live host, C4, agent spawning, commits or pushes were performed. The separately reported
app 37 tests/4 browser flows/126 checks and historical owner runs are not counted here.
Independent code review remains a separate responsibility; no Phase 6 or ship gate claimed.

**Stop/handoff:** native verification is complete for this bounded scope. Preserve these
tests/evidence for the parent. No production fix or further execution is requested by this result.

# Q1 correction round 2 — owner-tested, frozen for independent replay

## Disposition and scope

**FACT:** F3 reproduced on the original verifier's unchanged tests, then passed
after the correction. Final owner-run scope: **42 Q1 tests and 19 legacy probe
tests passed**, with no failures, errors, skips, timeouts or input drift.
These runs include the original F1/F2 counterexamples and both r2 verifier tests.
This is not the original verifier's replay or the separate review.

Only `scripts/measure_graph.py` and the owned `scripts/tests/test_measure_graph.py`
changed in this round; evidence is additive under `q1-correction-r2-*`.
No C1/shared-state edits, Q2 work, installation, agents, commit, publication,
broad quality measurement or release acceptance. All nine required measurements
remain required; missing metrics still produce incomplete/fail.

Observed HEAD at finalization:
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`.
This is repository context, not a claim that uncommitted Q1 source is in that commit.
The original pre-code checkpoint, correction results and independent evidence
remain historical and untouched. The round-2 pre-code decision is separately
preserved in `q1-correction-r2-plan.md`.

## Cause, correction and model limits

**FACT:** Raw `sys._xoptions` did not distinguish documented environment-selected
frozen-import behavior. The reproduced original test showed the same parser
fingerprint for different native/probe resolution. Per-run resolution was already
correct; this was not an observed false overall green or successful forgery.

`measure_graph.py:91–120` now obtains the effective complete CPython frozen-name
census through `_imp._frozen_module_names()` and binds each name's actual
`FrozenImporter.find_spec` availability, origin and package classification.
The runtime, rather than handwritten flag parsing, applies environment/CLI
precedence, repeated options, ignored environment and build defaults. No
fixture/module special case selects the mode. The parser profile is
`python-literal-import-v3`.

The raw `frozen_modules` option is replaced by this effective table; unrelated
options remain conservatively bound. Equal effective frozen modes have equal
identities, including after raw environment/options are changed after startup.
Different effective tables have different identities. Adapter, AST implementation,
runtime, executable and builtin-module bindings remain in place.

**FACT:** The managed CPython 3.14.2 runtime returned **28 names** with optional
frozen modules on and **3 bootstrap names** with them off. Optional names are
absent in off mode, not necessarily present with a null spec. The first owned
mode-control attempt incorrectly indexed an absent key and failed in the test
harness. That historical failure is retained under `modes`; only the test
assumption changed before `modes-final`. It is not counted as a production red.

**Qualified boundary:** this uses an inspected private CPython census API in the
already-supported managed runtime. An unavailable/malformed census fails closed.
This does not add support or authentication guarantees for arbitrary custom
import hooks, monkeypatching or other Python implementations. The table describes
the static builtin/frozen precedence model, not arbitrary external-module code.
The F2 identity check remains an observation, not a filesystem lease or sandbox.
No normative contract or public API change was needed.

## Real controls and final self-review

The new owned test at `scripts/tests/test_measure_graph.py:21–84` runs ten real
child interpreters and imports a second local/frozen package namesake,
`__phello__.spam`: default; environment on/off; CLI overrides in both directions;
last CLI option wins in both directions; `-E` with each environment value; and
`-I` with environment off. It checks native origin/local marker, effective table,
digest equivalence/difference and post-start raw-setting consistency.

Final captured parser identities:

| Effective outcome | Census | Parser SHA-256 |
| --- | ---: | --- |
| default/on; CLI-on; last-on; ignored environment | 28 | `fb3cfccde62e9ab7e3dfd6321a4297c507a8cce457fce9361793acc90cf085ec` |
| env-off; CLI-off; last-off | 3 | `5215c84478cf910fd213e5f12d9069879af797551ea2959c034316cf506e0b90` |

These are observed outcomes on this runtime, not assumed portable build defaults.
Full child argv, environment deltas, table and native observations are retained
in final worker stdout. The unchanged verifier additionally exercises real
configured probe output and receipt binding for `__hello__`.

Owner self-review checked effective rather than raw settings, deterministic
ordering/serialization, absence of target-module execution, preservation of
builtin/frozen versus shadowable/relative resolution, and unchanged incomplete
policy. Compile-without-bytecode and trailing-whitespace checks passed for six
owned production/test files and both round-2 evidence scripts. No new issue was
identified in that bounded self-review; independent review remains required.

## Exact commands and raw outcomes

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture test_measure_q1_verification_r2.py red
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture 'test_measure_graph.py::effective_frozen_binding' modes
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture test_measure_q1_verification_r2.py boundary-green
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture 'test_measure_graph.py::effective_frozen_binding' modes-final
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture test_probe.py legacy-final
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-capture.py capture 'test_measure_*.py' q1-final
& $py -B scripts/run.py --idle 30 --max 90 -- $py -B .ai/workflow-reliability/evidence/q1-correction-r2-finalize.py
```

The literal worker argv/cwd/environment and actual raw stdout/stderr references
are authoritative in each `q1-correction-r2-<label>-command.json`. The wrapper uses
stdlib unittest discovery, not an invented `python -m unittest` invocation.
Both final captures ran concurrently on frozen source. Only verifier evidence
output destinations/tags were relocated into new owned fixture directories;
verifier source and assertions were not changed. Evidence paths reject overwrite:
independent replay must use fresh labels.

| Label | Tests/outcome | Unittest seconds | Worker capture seconds | Exit |
| --- | --- | ---: | ---: | ---: |
| red | 1 passed, 1 failed: original F3 | 41.149 | 42.473 | 1 |
| modes | owned harness assumption failure | 6.995 | 8.337 | 1 |
| boundary-green | 2 passed | 40.565 | 41.879 | 0 |
| modes-final | 1 passed, ten native modes | 10.649 | 11.951 | 0 |
| legacy-final | 19 passed | 61.649 | 62.948 | 0 |
| q1-final | 42 passed | 708.778 | 710.054 | 0 |

### Final raw streams

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `q1-correction-r2-q1-final.stdout.bin` | 36054 | `e18134cd8dfd4b8d46bc2911577f15e535a94e762bfb6446b7e45902fcf55a53` |
| `q1-correction-r2-q1-final.stderr.bin` | 7395 | `f9d65296a7ea88e04c16389fea6fd4c2fca26ffd663ca15c2a0b4689116d112d` |
| `q1-correction-r2-legacy-final.stdout.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `q1-correction-r2-legacy-final.stderr.bin` | 2911 | `f2ab0f98a9b1b0202ca88cfd15d9c3523b4a376955574b29ae402a081500d0db` |

## Final freeze and handoff

`q1-correction-r2-final-freeze.json`:
**211344 bytes**,
SHA-256 `e2ece8d0e3cb3b244b067e9c8932f0388f13111ea01319492b1addad96dd8bd3`.

The finalizer checked:

- Q1: **234** pinned inputs unchanged; legacy: **309** unchanged.
- **322 unique inputs** unchanged across the final runs and final rehash;
  **zero late imported source files**.
- **382 original verifier source/evidence files** remain byte-identical.
- All **12 top-level raw streams** for the six correction captures match their
  recorded bytes/hashes. Final fixture archives are retained, but this owner
  finalizer does not independently reconcile every ZIP member.
- Pins include observed imported source, existing bytecode caches, managed
  Python EXE/DLLs, resolved Git/Node and explicit production/test/contracts.
  This is not an OS-wide closure or whole-repository freeze.

| Source | Final SHA-256 |
| --- | --- |
| `scripts/measure_graph.py` | `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061` |
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/tests/test_measure_graph.py` | `22a1fc3d9506e0a200ce43991ea0b667d48a26b2b69a61d5a7937761ae1876df` |
| `scripts/tests/test_measure_inventory.py` | `d97a98983cb2c825abd87ffec4f96981c652dece88846abd3864179a2921d227` |
| `scripts/tests/test_measure_q1_integration.py` | `889e5ab71f3e8d9cb16b9ded4dc9327fcf1d5f4820426e0773f17c8f1b4976a9` |
| Original verifier test | `f58d77f2cc957d7eae0bfaf4a3f99a63370fc1901a2b5312ce43b3a445bb19c6` |
| R2 verifier test | `4bb2639f64390d1af0ff1d223843d0f1036e6a75742587d86411f4d0d5db8d46` |

**Pending:** original verifier replay on these exact bytes, then separate review.
C1 evidence pinned to the prior graph hash must not be relabeled as proof of this
new dependency. Parent owns final cross-worker reconciliation. No Q1 acceptance,
Q2 advance, overall quality gate or release claim is made here.

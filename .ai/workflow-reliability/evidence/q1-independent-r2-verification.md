# Q1 correction replay — NOT-VERIFIED

17 September 2026. Original independent verifier, bounded correction replay on
the frozen F1/F2 implementation. **Not the separate read-only review role.**

## Disposition

**The original F1 and F2 counterexamples now pass unchanged. A remaining
effective-import-mode binding defect (F3 below) stops Q1 acceptance.**

- Q1 regression: **39 passed**, including all six original verifier tests.
- Legacy probe regression: **19 passed**.
- Two new targeted correction tests: **1 passed / 1 failed**.
- Combined selected scope: **59 passed / 1 failed (60 tests)**.
- No errors, skips, timeout kills, retries or production repairs.

No production, original tests/evidence, shared state/docs, C1 files, install,
agent nesting, commit, publication, Q2 adapter, full root measurement or mutation
work was performed. New writes are the authorized
`scripts/tests/test_measure_q1_verification_r2.py` and additive
`evidence/q1-independent-r2-*`.

## Per-finding verdict

| Finding | Verdict | Actual observation |
| --- | --- | --- |
| Original F1 — builtin precedence | **VERIFIED** for original counterexample | Unchanged original test passes. Native CPython uses builtin `sys`; real public probe now reports **cycles=0, architecture_rules=0**, both measured, while retaining seven missing required metrics and incomplete/fail. |
| Original F2 — shared mutable source roots | **VERIFIED-WITH-LIMITATIONS** | Unchanged fresh-recollection test now rejects with **“Shared mutable file identity across Context roots”**, not stale-proof rejection. Physical aliasing and cross-write are still demonstrated in the controlled fixture. This is an observed check, not a filesystem lease or sandbox. |
| F3 — effective frozen mode not bound | **NOT-VERIFIED / remaining blocker** | Different documented interpreter modes produce different real import resolution but the **same parser/toolset fingerprints**. The new regression fails on that identity collision. |

The independent regression also passes the owner's new real controls:
builtin `time`, frozen `os.path`, shadowable `fractions`, explicit relative
`pkg.sys`, non-package `time.child`, differently named and non-code hardlinks,
base/controller and head/controller aliases, artifact/source alias, and
independent equal-content copies. No inference of universal dynamic-import
safety follows.

The additional independent hidden-contract test passes: a non-code source
under analyzer-excluded `.hidden/` is included in the physical independence
check and rejected after **fresh** source/raw recollection.

## F3 — same fingerprint under different effective import semantics

**FACT.** Installed CPython `--help-xoptions` documents both
`-X frozen_modules=[on|off]` and **`PYTHON_FROZEN_MODULES`**. The test uses the
documented environment variable in separate real native and configured-probe
processes. No custom import hook, `sys.modules` edit, runtime monkeypatch,
fabricated receipt or production modification is involved.

Owned fixture contains:

```python
# a.py
import __hello__

# __hello__.py
LOCAL = True
```

| Effective setting | Native CPython origin | Probe literal edge |
| --- | --- | --- |
| `PYTHON_FROZEN_MODULES=on` | `frozen` | `a.py -> __hello__`, external |
| `PYTHON_FROZEN_MODULES=off` | actual owned `__hello__.py` | `a.py -> __hello__.py`, local |

Both native commands exit **0**. Both probe commands exit **1** with honest
incomplete/fail. **Per-run resolution is correct**; the defect is its identity
binding, not an observed false overall green or successful report forgery.
The two reports carry identical:

- `tools.python_parser`:
  `5768d1aa07955a0444da0cd87805a6c5d459f5a241719287c62ecd10fde97538`
- Parse-receipt `toolset_sha256`:
  `e4d82b643c5a0deadb4d8ae658cd9094f3437593a4221a4a8a8457bc63418050`

**Grounded cause:** `scripts/measure_graph.py:91-98` hashes
`"import_options": sys._xoptions`; the environment-selected effective frozen
mode is absent from that identity. Resolution at line 201 queries
`FrozenImporter.find_spec`, whose actual result changes in the demonstrated
processes. Thus the fingerprint cannot distinguish the two effective parser
semantics. This contradicts Q1's tool/config/semantic binding and the correction's
claim to bind runtime import options. Same code bytes are not sufficient to
identify an environment-dependent parser.

**Failing regression:** `test_measure_q1_verification_r2.py:33-73`.
`q1-independent-r2-boundaries.stderr.bin` preserves the actual
`assertNotEqual` failure. No production correction was attempted.

### Raw counterexample

Directory: `q1-independent-r2-fixtures-boundaries/`

- `q1-independent-effective-frozen-mode-observations-independent-r2-boundaries.json`
  contains exact native/probe argv, both environment deltas, origins, edges,
  parser hashes and receipt toolsets.
- Four native/probe command JSON records and their original stdout/stderr bytes
  preserve actual inner exits. The original raw-command helper records the
  common bytecode environment; the observations record additionally preserves
  the changing `PYTHON_FROZEN_MODULES` setting.
- Both frozen-mode fixture ZIPs and their file manifests retain the source,
  config, approval and probe's complete raw archive mapping.
- The hidden-source alias observation preserves fresh Context, base/head,
  manifest, observations and exact rejection.

The fixed original counterexamples' new byte captures and archives are in
`q1-independent-r2-fixtures-q1/`, including
`q1-independent-hardlink-counterexample-independent-r2-q1.json`.
Old original evidence remains unchanged; these are additive results.

## Scoped Q1 / AC verdicts

| Check / criterion | Verdict |
| --- | --- |
| CHECK-INVENTORY | VERIFIED-WITH-LIMITATIONS: scoped real census, unsupported/failed inputs, explicit exclusions and ownership regressions pass. |
| CHECK-GRAPH | VERIFIED-WITH-LIMITATIONS for demonstrated literal resolution, cycle identities and architecture rules; effective parser identity remains blocked by F3. |
| CHECK-PARTIAL-PROBE | VERIFIED-WITH-LIMITATIONS: exact nine requirements and missing-as-fail regressions pass; no complete quality proof. |
| CHECK-RECONCILE | **NOT-VERIFIED** for complete semantic/tool binding because of F3; existing raw corruption/source/approval/run/artifact tests pass. |
| Q1 acceptance | **NOT-VERIFIED**; return F3 to original production owner. |
| AC01 | VERIFIED-WITH-LIMITATIONS: scoped legacy native probe behavior remains passing, not a fresh acceptance of all mutation functionality. |
| AC02 | **NOT-VERIFIED for complete Q1 binding**; required-field/completeness behavior passes but F3 remains. |
| AC09 | **NOT-VERIFIED for Q1 acceptance**; regression preservation is established, new failure remains and separate review is still due. |
| AC03, AC04, AC05, AC06, AC07, AC08, AC10 | NOT-VERIFIED by this correction-only role; no new acceptance or rejection of unrelated parent/C1/docs work. |
| Q2–Q5 / release | NOT-VERIFIED; no execution or advancement in this role. |

The mixed-language regression still retains explicit unsupported MJS/CJS
receipts and all nine missing measurements. Original greenfield proof uses an
actual complete two-code-file baseline. These preserved behaviors do not waive
F3 or authorize a complete quality claim.

## Exact execution

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Read-only HEAD observation:
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`.
No unrelated C1 edits are interpreted as measurement drift.

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r2-capture.py preflight
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r2-capture.py capture 'test_measure_*.py' q1
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r2-capture.py capture test_probe.py legacy
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r2-capture.py capture test_measure_q1_verification_r2.py boundaries
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r2-finalize.py
```

The capture wrapper runs stdlib unittest discovery in a child worker and captures
actual stdout/stderr bytes before outer text forwarding. Each
`q1-independent-r2-<label>-command.json` records its literal worker argv,
cwd, fresh tag, original streams and actual exit—not a claim to have executed
a different `python -m unittest` argv.

The 39-test Q1 discovery started before the new two-test file existed.
Discovering `test_measure_*.py` now includes those additional tests.
Only the original test module's **evidence output directory/tag** was relocated;
its source, fixtures and assertions were unchanged.

| Run | Tests / outcome | Actual unittest duration | Exit |
| --- | --- | ---: | ---: |
| q1 | 39 passed | 649.674s | 0 |
| legacy | 19 passed | 59.271s | 0 |
| boundaries | 1 passed / 1 failed | 39.362s | 1 |

The already-running Q1 regression was allowed to finish after F3 appeared.
No new verification probes or repeat test runs were launched afterward.

To replay the remaining counterexample after owner correction, use the capture
command for `test_measure_q1_verification_r2.py` with a **new label**, such as
`boundaries-after-owner-fix`. Existing capture/archive paths deliberately refuse
overwrite. Q1/legacy replay and separate independent review remain due before
acceptance.

## Freeze and preservation

`q1-independent-r2-final-freeze.json` holds exact before/after/final hashes,
all run commands and original raw-stream integrity checks:

- All **321 owner-frozen inputs** match both preflight and final recheck.
- Q1: **324 pinned inputs unchanged**; legacy: **324 unchanged**;
  added boundaries: **325 unchanged**.
- **325 unique pinned inputs** across this replay; **zero late imports**.
- **297 original verifier evidence/test files** rechecked byte-identical,
  including files inside earlier partial fixture directories.
- **30 raw streams** match recorded hashes.
- **9 fixture ZIPs / 275 members** match exact source/archive manifests.
- Imported stdlib sources and existing bytecode caches, Python EXE/DLLs,
  resolved Git/Node executables and measurement transitive source/test inputs
  are pinned. `-B` forbids bytecode writes, not reads.
- This is not an OS-wide dependency closure or a whole-tree freeze. No C1
  production module was read/explored.

### Selected source hashes — before = final

| Input | SHA-256 |
| --- | --- |
| scripts/measure.py | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| scripts/measure_graph.py | `f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6` |
| scripts/probe.py | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| Original verifier test | `f58d77f2cc957d7eae0bfaf4a3f99a63370fc1901a2b5312ce43b3a445bb19c6` |
| New r2 verifier test | `4bb2639f64390d1af0ff1d223843d0f1036e6a75742587d86411f4d0d5db8d46` |

New verifier/capture/finalizer files compile without bytecode and have no
trailing whitespace. No original file was changed to obtain those checks.

### Raw test stderr

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| q1-independent-r2-q1.stderr.bin | 6829 | `c48c9f03ef6d28c696eb7501989dad547c4e5df0e966957d1378ac174d172f15` |
| q1-independent-r2-legacy.stderr.bin | 2911 | `73146ad681deb79371aeb37851550daebd4dc2984f3e7b3cad129b4757cedc9b` |
| q1-independent-r2-boundaries.stderr.bin | 1851 | `4bf1717552b544bfdc6349456d43b94e327bc013dfb14b4a28dd0248d013e03a` |

All three test-worker stdout files are genuinely empty, not missing.
The original malformed verifier archive attempt remains historical and is not
a production issue. No such harness error occurred in this correction replay.

**Handoff:** original F1/F2 counterexamples are corrected on this freeze.
F3 remains a concrete binding blocker. Return it without production repair;
keep Q1, Q2 and release unaccepted. Separate review was not launched.

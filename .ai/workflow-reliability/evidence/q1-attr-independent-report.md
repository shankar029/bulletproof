# Residual R2 attribute gate + integrated C1 — VERIFIED-WITH-LIMITATIONS

17 September 2026. Resumed independent verification of **only** the final
attribute-admission correction and the requested integrated C1 dependency replay.
No concrete residual production blocker was reproduced within this objective.
This is not a broad new review or complete quality acceptance.

## Fresh results

| Batch | Methods | Unittest seconds | Capture seconds | Exit |
|---|---:|---:|---:|---:|
| Focused attributes / configured CLI / shared probe policy (`a`) | **28** | 228.396 | 233.318 | 0 |
| Integrated workflow discovery (`w`) | **83** | 206.615 | 230.193 | 0 |
| Integrated evidence discovery (`e`) | **10** | 5.922 | 29.043 | 0 |
| **Distinct methods this replay** | **121** | | | |

**Zero test failures, errors, skips or timeouts. Each suite executed once.**
No test recovery/retry occurred. The focused batch completed before either C1
batch started; workflow and evidence then ran concurrently in separate processes
and owned fixtures. There was no simultaneous broad measurement run.

These counts come from exact test inventories, actual raw unittest IDs,
successful per-run result records, and terminal `Ran ... / OK` reconciliation.
Subtests and controls are not extra methods. The **prior 74-test verification
was preserved, not rerun or counted as execution on the new bytes**.

## Coverage mapping and bounded verdicts

Existing coverage was read before adding a test. The owner already provided the
two literal-name cases, disabled filter, absent/reset positives, macro sentinel,
qualified EOL/modes, unsupported transforms/types, public configured CLI and
nineteen legacy shared probe checks. Those **27 methods** were reused unchanged.
Only the missing conservative text-state scenario was added:
`scripts/tests/test_measure_q1_attr_independent.py`, one method covering `-text`
rejection at both boundaries, no checkout file on rejection, then genuine
`!text` reset acceptance with exact bytes.

| Boundary | Verdict / actual proof |
|---|---|
| **Literal `filter=unset`** | **VERIFIED.** Both `materialize_baseline` and `validate_baseline` reject with `Baseline unsupported attribute filter=unset: a.py (ambiguous present declaration)`. Sentinel absent during both isolated operations; explicit ordinary checkout with the exact named driver writes `executed`. |
| **Literal `filter=unspecified`** | **VERIFIED.** Same two-boundary rejection with the corresponding literal name; isolated sentinel remains absent; ordinary positive control executes the named driver. |
| Absent / reset filter | **VERIFIED.** Unrelated `diff=python` does not become a filter prohibition. An earlier filter followed by `!filter` is omitted by the effective Git census and both materialization and validation accept exact `pass\n` bytes. |
| Present disabled controlled attributes | **VERIFIED on explicit cases.** Existing `-filter` and new `-text` cases reject at both boundaries as ambiguous/unsupported, rather than claiming a policy pass. New `-text` then `!text` reset succeeds. Other controlled-name rejection follows the source allowlist but was not expanded into duplicated tests or a broad fuzzing claim. |
| Ordinary external filter / macro / sentinel | **VERIFIED.** Existing effective macro `filter=tripwire` rejects before checkout through direct materialization and the shared CLI copy helper; sentinel remains absent. The actual driver is then executed in the explicit positive-control checkout. |
| Qualified EOL / representable mode | **VERIFIED-WITH-LIMITATIONS.** Neutral LF, versioned CRLF, nested LF and nested overriding CRLF bytes pass. Replacing expected CRLF bytes with LF rejects. Immutable `100755` remains recorded with the explicit Windows regular-file projection; no POSIX executable-runtime proof. |
| Unqualified transforms / Git types | **VERIFIED.** Existing `ident`, working-tree encoding, legacy `crlf`, symlink tree mode and submodule tree mode controls reject. |
| Producer configured CLI | **VERIFIED.** The actual configured CLI from nested cwd preserves cycle/architecture evidence, raw archive ownership and all nine requirements; seven missing metrics keep the report incomplete/fail. The published snapshot remains fresh until an unrelated source input is added. |
| Affected shared probe policy | **VERIFIED-WITH-LIMITATIONS.** All nineteen existing probe regression methods pass, including missing-required-as-fail, invalid baseline, stale mutation rejection and a real fixture native-mutation positive. This is not real root-quality collection or external analyzer qualification. |
| **Integrated C1 against final Q1 bytes** | **VERIFIED-WITH-LIMITATIONS.** All 83 workflow and 10 evidence tests pass from the integrated workspace. Observed imports resolve to the actual `workflow_gate`, `workflow_state`, `measure`, `measure_graph`, `probe`, `mutate`, `evidence` and `run` files in this checkout, matching before/after pins. Not a C1-only candidate. |

The two literal driver observations are preserved verbatim in
`q1-attr-independent-a.stdout.bin` and decoded/reconciled independently in
`q1-attr-independent-freeze.json`. This closes the **unsupported admission**
counterexample; it is not a claim that the old isolation allowed driver
execution or produced an overall-green report.

### Actual source delta and qualified semantics

FACT: the finalizer independently opened the recorded predecessor archive member
`subjects/controller/measure.py`, verified its old `753fca9e...` SHA-256, and
compared it to the current `5d6f15a9...` bytes. The recorded
`q1-attr-measure.diff` matches **one production hunk**, the nested attribute gate.
`measure_graph.py` and `probe.py` retain the prior hashes.

`scripts/measure.py:133–154` now asks Git for
`check-attr --cached --all -z -- <paths>`, validates complete triples/requested
paths/duplicate records, and examines the six controlled attributes. Genuinely
absent/reset attributes are omitted. Present `unset` / `unspecified` are not
trusted as typed absence/disabled markers. Only qualified text values `set` /
`auto` and EOL values `lf` / `crlf` are admitted for these transformations.
This is Git's parser, not a handwritten `.gitattributes` parser.

The same materializer remains used by the CLI copy path and independent
baseline validator. There is no public schema/Context change, no normalization
of supplied baseline bytes, and no policy relaxation.

## Integrated C1 reconciliation

This is an affected-dependency replay, not a new C1 code review. Existing C1
regressions executed unchanged, including:

- Closure-prefix chronology and exact receipt references; inherited,
  transitive, handoff and ship reclosure boundaries.
- No-spawn cannot establish work/red; aware UTC validation.
- Mandatory comparison policy cannot be replaced by permissive floor/coverage
  modes; successful positive/tightening/warning controls remain valid.
- Failed producer exits/outcomes cannot authorize direct consumers; valid
  native-red and handoff exceptions retain their exact proof conditions.
- Repeatable no-I/O evaluation and bounded shared prefix computation.
- Strict schemas, atomic persistence, locks, source/membership freshness,
  independent role/context rules, temporal consumption and research history.

The raw workflow stdout again records:

| Increments | Evaluator constructions | Proof misses | Unique misses |
|---:|---:|---:|---:|
| 3 | 4 | 87 | 87 |
| 5 | 6 | 195 | 195 |
| 8 | 9 | 432 | 432 |

These are bounded observed counters, not a universal complexity or speedup claim.

**C1-V01–V10:** VERIFIED-WITH-LIMITATIONS as a current integrated regression/
freshness replay of the accepted C1 surfaces. The C1 fixtures' metric, producer
and native receipts are intentionally synthetic **protocol data**, not evidence
that actual root quality, authenticated independent actors or live C2 dispatch
were executed. Existing no-I/O/error-injection test doubles were not represented
as real external producer proof. The new attribute test uses real Git/files.

## CHECK / AC status

| Scope | This role's disposition |
|---|---|
| Residual R2 attribute admission / **CHECK-RECONCILE** affected boundary | **VERIFIED-WITH-LIMITATIONS** on the final bytes and qualified Git package. |
| **CHECK-PARTIAL-PROBE** | **VERIFIED** for all-nine/missing-as-fail and actual configured producer replay. |
| **AC02 / AC09** | **VERIFIED-WITH-LIMITATIONS** for this residual correction and integrated C1 regression/freshness slice. Separate narrowed code re-review and overall quality gates remain due. |
| Prior R1, F1/F2/F3, CHECK-INVENTORY / CHECK-GRAPH | Prior evidence preserved; not broadly rerun here. The single-hunk production delta was independently reconciled; no fresh 74-method claim. |
| AC03 / AC04 C1 core | Bounded integrated C1 regression proof only; not live C2 dispatch or authenticated enforcement. |
| Other ACs, actual Q2–Q5 / Q4 controller execution / complete quality | **NOT-VERIFIED by this role.** |
| Combined C1/Q1 preservation | Functional dependency replay is green. Parent still owns narrowed re-review, exact commit-composition check and preservation disposition; this is not a C1-only candidate or preservation commit. |

## Exact commands and raw captures

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-attr-independent-capture.py preflight preflight-2
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-attr-independent-capture.py capture focused a
# Only after focused completed:
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-attr-independent-capture.py capture workflow w
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-attr-independent-capture.py capture evidence e
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-attr-independent-finalize.py
```

The worker uses actual stdlib unittest loading: explicit existing method/module
names for the focused batch; discovery with `test_workflow_*.py` and
`test_evidence.py` for C1. Exact fully qualified method inventories are persisted
in `*-inventory.json`. This is not a claim of executing a different
`python -m unittest` argv. Actual worker argv/PIDs/cwd/environment/bounds/exits
are in `*-launch.json` and `*-command.json`.

The workflow worker sets `C1_VERIFICATION_IMPORT_MANIFEST` to the new
`q1-attr-independent-w-imports.json` before discovery; this preserves the existing
optional in-suite observation hook without modifying tests. That hook observed
175 file-backed modules, all matching before/during/after hashes.

The inspected streaming transport exclusive-creates and flushes raw streams as
they arrive. Only real subprocess creation and temporary-directory audit events
emit progress; no timer heartbeat. New short tags/destinations avoid MAXPATH and
refuse overwrites. **Do not reuse these labels for a future replay.**

| Raw stream (prefix `q1-attr-independent-`) | Bytes | SHA-256 |
|---|---:|---|
| `a.stdout.bin` | 616 | `3b36a6f68fc805100c57164fdcb3fe471a250c4d7d1ebc3c6d950395f6b38629` |
| `a.stderr.bin` | 64715 | `1311e00854623a50e87c4b23e1e04d9e0a6470d1e323a3372005fb05731527c3` |
| `w.stdout.bin` | 202 | `d1dd077bfcb0c5677546ab0b7c87658a53b65172321c8dba9ccde557b2f5b432` |
| `w.stderr.bin` | 27811 | `3d9b83597de5a89511ca1e15fd7ee5714b15ebe5443bc054bdd1570373719156` |
| `e.stdout.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `e.stderr.bin` | 3160 | `d9f76793e05c5d947b45f230d7e23b18b3a400e7eea666041fbe03a613bf7e04` |

### Disclosed capture/reconciliation errors — no test retries

1. The first `...capture.py preflight` exited **1** after writing
   `q1-attr-independent-preflight.json`. It reported owner keys
   `C:\Program Files\nodejs\node.EXE` and the Git `cmd\git.EXE` as mismatches.
   Inspection established equal byte lengths and SHA-256 values; the new
   capture keyed resolved `.exe` spellings but looked up the owner's `.EXE`
   spellings literally. The lookup was corrected to use the same resolved path
   representation. `preflight preflight-2` succeeded once; original observation
   remains unchanged. No production alias policy was altered.
2. The first finalizer exited **1** at its exact serialized diff comparison,
   after reconciling test results/imports/archives. Independent generation was
   2,411 bytes versus the preserved 2,453-byte artifact. The owner used Windows
   text-mode newline expansion: three header LF lines became CRLF and 39
   source-CRLF lines became CRCRLF. The finalizer was corrected to verify that
   exact writer encoding against the artifact, then succeeded in one bounded
   recovery. **Source/baseline bytes were never normalized.**

These errors are tool-transcript observations transcribed here, not invented
standalone raw stderr captures. The raw test streams and prior red failures
remain intact. No failing test was retried or reclassified as passing.

## Freshness, qualified runtime and ownership

FACT: final reconciliation checked **2,047 input pins per batch** and
**2,810 protected prior evidence files**, **4,778 unique paths**, unchanged.
There were **zero late imported files** in each batch. Post-run module
observations counted 179 focused / 175 workflow / 162 evidence file-backed
modules, each already included in the pre-run census and unchanged.

Pins include actual production/tests/contracts, loaded Python sources and
caches, managed runtime source/binary files, native fixture executable inputs,
and the qualified Git core plus all 69 bundled DLLs. It is bounded source/
runtime freshness, not an OS-loader closure, edit-and-revert detector, atomic
lease or sandbox.

The focused replay preserves **24 exact owned fixture archives**, including the
literal-name sentinel drivers, actual source/config/index/Git objects and
positive/negative materializer trees. All member byte hashes reconcile.
**162 observed owned temporary paths were absent** at finalization. No unknown
prior leftovers or unrelated paths were removed. C1 uses its existing owned
protocol fixtures and captures results/imports; it does not claim archived
live quality producers.

### Final production hashes

| File | SHA-256 |
|---|---|
| `scripts/measure.py` | `5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084` |
| `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts/probe.py` | `668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083` |
| `scripts/workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |

The actual direct core reported **Git 2.53.0.windows.4, aarch64**,
build commit `3a9e66c3d66bb6509be99fe21c3205f024c04568`; its binding equals the
qualified owner record and the pre-run core/DLL hashes. Managed test runtime is
**CPython 3.14.2, Windows AMD64**. All five historical narrow qualification
commands' raw streams were rehashed, **not reexecuted or counted as fresh
qualification commands**. Actual corrected materialization behavior was freshly
exercised by the listed tests.

Other Git builds/layouts remain unqualified and fail closed. POSIX behavior,
every Python runtime, and full transitive OS-library loading were not proven.
Five copied controller sources do not prove Q4 execution; actual `mutate`
and other probe imports were separately pinned.

Bounded Git metadata commands used `git --no-pager` with idle 30/max 90 and
recorded decoded stdout/stderr in the freeze. HEAD remained
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`, branch
`shbs-microsoft-workflow-app-verification`, index empty.
Scoped compilation and `git diff --check` succeeded.

## Handoff

**Residual attribute functional correction and integrated C1 dependency replay:
VERIFIED-WITH-LIMITATIONS.** No production/shared-state/contracts/prior-test/
prior-evidence changes, installs, nested agents, commits or publication.
Only the one narrowly needed new test and additive `q1-attr-independent-*`
evidence were written.

Primary machine-readable proof: **`q1-attr-independent-freeze.json`**.
Parent owns narrowed code re-review, combined C1/Q1 commit-composition checking
and accepted preservation. No C1-only candidate, C2/Q2 admission, actual-root
quality pass, Q4 execution or whole-task completion is claimed here.

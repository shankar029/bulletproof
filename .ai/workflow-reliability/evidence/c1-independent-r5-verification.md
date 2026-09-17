# C1 independent r5 — frozen-dependency freshness replay

## Verdict: VERIFIED-WITH-LIMITATIONS

**Bounded functional acceptance for separate reviewer recheck.**

**FACT:** Exactly one replay passed **83/83 workflow tests** and **10/10
evidence tests**, with zero failures, errors or skips and both commands
exiting 0. The scoped runtime/test inputs were unchanged throughout capture.
This resolves the r4 freshness blocker for the explicitly pinned r5 snapshot,
not retrospectively for the r4 run.

No new investigation, test, production change or retry was performed.
The r4 functional finding assessment is retained; this replay adds fresh
execution evidence against the final Q1 dependency freeze.

## Freeze and preservation

Read `q1-correction-r2-final-freeze.json` and matched its three relevant
production hashes against actual files before executing:

| Dependency | Tested SHA-256 |
|---|---|
| `scripts/measure_graph.py` | `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061` |
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |

**FACT:** Comparing the r4 applicable pins with the r5 preflight found only
the expected `measure_graph.py` change. C1 production/test inputs were
unchanged. Observed HEAD:
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`.

**FACT:** The replay recorded **1,883 relevant file pins**, **172 actual
file-backed workflow import observations** matching before/during/after
hashes, and **52 protected historical files**. There were no changes across
capture or within any command, no unmatched imports, no new applicable
top-level Python/workflow test input, and no changed protected original.

Scope matches the r4 census with the final freeze index and r4 report added:
top-level Python runtime modules; workflow/evidence tests and helpers;
explicit C1 contracts/review/correction inputs; managed Python source/binary
files. The import hook runs in workflow discovery, not the separate evidence
suite; the latter's runtime/test inputs are still pinned before and after.

Unrelated measurement tests/docs/evidence are excluded. This is not a
whole-root, OS/DLL, authenticated-role, edit-and-revert or future-freshness
attestation. Q1's owner results in the index were not independently accepted
by this C1 replay.

## Exact execution

From repository root:

```powershell
$p = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_*.py' -v
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_evidence.py' -v
```

The existing optional `C1_VERIFICATION_IMPORT_MANIFEST` hook wrote
`c1-independent-r5-imports.json`. Its exact path and relevant inherited
Python environment are recorded in the manifest.

| Suite | Tests passed | unittest duration | Exit |
|---|---:|---:|---:|
| Workflow discovery | 83 | 176.890 s | 0 |
| Evidence discovery | 10 | 5.529 s | 0 |

Actual argv, cwd, timestamps, before/after pins, raw stream byte counts and
SHA-256 hashes are in `c1-independent-r5-manifest.json`. Both streams were
captured directly; `run.py` combines child output into its stdout.
Existing real library/filesystem/fresh-process scenarios ran in discovery.

## Findings and original sub-ACs

These are freshness-replayed dispositions, not a new code review. Refer to
`c1-independent-r4-verification.md` for the bounded source-grounded mechanisms,
positive/negative cases and limitations. Its historical blocked verdict is
preserved unchanged.

| Finding | r5 result on pinned snapshot |
|---|---|
| R1 — mandatory comparison bypass | **VERIFIED-WITH-LIMITATIONS:** all comparison-mode bypass negatives and valid tightening/warning controls passed again. |
| R2 — failed producer proof | **VERIFIED-WITH-LIMITATIONS:** failed command receipts blocked; validated native-red/exact-reference and successful/handoff controls passed again. |
| R3 — repeated prefix work | **VERIFIED-WITH-LIMITATIONS:** measured 3/5/8 increments produced 4/6/9 evaluators and 87/195/432 unique uncached proof pairs, with no repeated uncached pairs. Fresh public-call controls passed. No general linear-runtime claim. |
| Original F1 / residual F1 | Closure-prefix chronology and exact references, including supported consuming surfaces and legitimate reclosures, passed. |
| Original F2 / F3 | No-spawn cannot prove work/red; parsed aware UTC strictness and positive controls passed. |

| Original criterion | r5 bounded verdict / retained proof |
|---|---|
| C1-V01 strict schemas/graph | **VERIFIED-WITH-LIMITATIONS** — existing strict schema, graph and semantic metric regressions passed. |
| C1-V02 atomic persistence/receipt resolution | **VERIFIED-WITH-LIMITATIONS** — atomic, sequence, immutable receipt and fresh-process regressions passed. |
| C1-V03 scoped freshness/exact chains | **VERIFIED-WITH-LIMITATIONS** — source/component/prerequisite freshness and unaffected preservation passed. |
| C1-V04 admission/mandatory closure | **VERIFIED-WITH-LIMITATIONS** — mandatory checks, prerequisite/member chronology and exact-reference controls passed. |
| C1-V05 increment-local contexts | **VERIFIED-WITH-LIMITATIONS** — context/role independence and positive controls passed. |
| C1-V06 temporal consumption | **VERIFIED-WITH-LIMITATIONS** — historical consumption, no backfill and separate current closure proof passed. |
| C1-V07 retained history/research | **VERIFIED-WITH-LIMITATIONS** — retained design, acceptance and research supersession controls passed. |
| C1-V08 conservative process/handoff proof | **VERIFIED-WITH-LIMITATIONS** — no-spawn, failed spawned producers, unresolved launches and valid handoffs passed. |
| C1-V09 pure evaluation/no fabricated proof | **VERIFIED-WITH-LIMITATIONS** — no-I/O, input preservation, repeated/fresh-call and measured prefix controls passed. |
| C1-V10 regression/current evidence | **VERIFIED-WITH-LIMITATIONS** — 83+10 green with stable final dependency pins and preserved historical evidence. |

## Evidence and handoff

- `c1-independent-r5-manifest.json`
- `c1-independent-r5-imports.json`
- `c1-independent-r5-workflow.stdout.log` / `.stderr.log`
- `c1-independent-r5-evidence.stdout.log` / `.stderr.log`
- `c1-independent-r5-head.stdout.log` / `.stderr.log`
- `c1-independent-r5-handoff.json` — final scoped input/preservation and raw
  stream integrity check; report and manifest hashes.

Only additive r5 evidence was written. No prior report/test was modified;
no nested agent, shared-state edit, commit, publication or C2 action occurred.

**Limits:** fixture metric/finding/process receipts are protocol test data,
not actual quality proof or live C2 dispatch/native-producer evidence.
No collector correctness, Q1 acceptance, complete quality gate, mutation,
full-suite, release or host-readiness claim is made.

**Next owner:** separate reviewer correction recheck and parent integration.
Any later applicable source/test change requires affected freshness to be
reconciled again rather than reusing this snapshot's acceptance unqualified.

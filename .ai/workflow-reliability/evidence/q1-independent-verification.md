# Q1 independent functional verification — NOT-VERIFIED

17 September 2026. Fresh-context verifier, existing
`workflow-reliability` continuation. This is **functional verification only**,
not the later independent code-review role.

## Disposition

**Stop Q1 acceptance. Two real counterexamples remain. Production was not fixed.**

Final scoped results: **28 existing Q1 passed; 19 legacy probe passed; final
independent suite 4 passed / 2 failed (6 total)**. Thus the final selected
functional scope is **51 passed / 2 failed**, not a green Q1 gate. No final-run
errors, skips or timeouts. Earlier harness-error and intermediate runs are
preserved separately and are not added to the passing count.

No production, existing test, shared state, C1 module, documentation, commit,
publication, dependency installation, broad root probe, full-repository test
sweep, mutation implementation or nested agent work was performed.
Only `scripts/tests/test_measure_q1_verification.py` and
`evidence/q1-independent-*` were written.

## F1 — builtin Python import resolved to an unrelated local file

**FACT / blocking functional defect.**

Fixture:

```python
# scripts/evidence.py
import sys

# sys.py
import scripts.evidence
```

The real managed CPython process imports `scripts.evidence`, prints `built-in`,
and asserts that its `sys` is the builtin module: **exit 0**. The configured
public probe on the same Git fixture instead produces the local edge
`scripts/evidence.py -> sys.py`, a cycle back to `scripts/evidence.py`, and
an ARCH02 violation. It reports **cycles=1 and architecture_rules=1, both
measured/fail**; the correct builtin import produces neither relation.
The remaining seven metrics are unavailable and the outer report still fails.
This is a false graph/architecture regression, not a claim that the overall
probe accidentally passed.

The failing assertion is
`test_measure_q1_verification.py:131-152`. The production resolution boundary is
`scripts/measure_graph.py:183-236`: `_resolve` searches local candidates at
line 202 before recognizing a builtin terminal. `evaluate_rules` later uses
stdlib/builtin names at line 409, but that cannot correct the already-local
edge. **INFERENCE:** raw-source recomputation repeats the same incorrect
resolution, explaining why report reconciliation accepts the wrong numbers.
This is within the declared literal-import model; no dynamic behavior,
reflection or import-hook safety is being inferred.

Evidence:

- `q1-independent-builtin-native-command-r3.json`: exact native argv/cwd,
  exit 0; original stdout/stderr in `q1-independent-builtin-native-r3.*.bin`.
- `q1-independent-builtin-resolution-command-r3.json`: exact public probe
  argv/cwd, exit 1; original stdout is **77,761 bytes**, SHA-256
  `818795d281d86733cb81809aada83335b508def6c6d6c0534b5aaca3906a3e79`.
- `q1-independent-builtin-resolution-r3.zip`: 24 exact fixture/archive files,
  with complete mapping in `q1-independent-builtin-resolution-fixture-r3.json`.
- `q1-independent-adversarial-r3.stderr.bin`: actual failed assertion.

## F2 — fresh evidence accepts base/head files sharing mutable storage

**FACT / blocking common-binding defect.**

A real private Git base and head initially validate as independent copies.
The test replaces head `a.py` with an actual hard link to base `a.py`, then
**re-observes source and uses the real inventory, parser, collector and manifest
producers to generate fresh evidence**. `measure.validate_observations`
accepts it. `os.path.samefile` is true. Writing only the owned head file
changes the base bytes too:

| Observation | SHA-256 |
| --- | --- |
| Base before head write | `f05a65413338d4d74cc2e7115db156601cfcb7838936e091cb74c7ecf0609277` |
| Base after head write | `5b6d77f6de013d3ff138bfcadbc922ac7c079ca247a5e642173541cc824d7903` |
| Head after head write | `5b6d77f6de013d3ff138bfcadbc922ac7c079ca247a5e642173541cc824d7903` |

The failing test is `test_measure_q1_verification.py:169-214`.
`scripts/measure.py:300-365` validates lexical/canonical root separation
(lines 310-312), Git cleanliness and content fingerprints, but the observed
acceptance does not establish independent mutable source copies.

The first hardlink check (r1/r2) was rejected as **“Head source observation is
stale”**; that only established stale-proof rejection. It did **not** establish
isolation. The final r3 test deliberately collects fresh, source-bound evidence
before validation. Its result is `validator_rejected=false`,
`samefile=true`, `shared_write_observed=true`.

This is a defect in the public common validation boundary for supplied Contexts.
The configured CLI's ordinary `--no-hardlinks` clone/copy path was **not**
observed creating this alias. No actual repository source was mutated, no
controller-self-mutation/Q4 proof was attempted, and no sandbox claim is made.

Evidence:

- `q1-independent-hardlink-counterexample-r3.json`
- `q1-independent-hardlink-r3.zip`: 48 original/private-subject/raw files,
  exact mapping in `q1-independent-hardlink-fixture-r3.json`.
- Final actual assertion output: `q1-independent-adversarial-r3.stderr.bin`.

## Q1 check verdicts

Existing scenarios were mapped before additions in
`q1-independent-coverage-map.md`; all original Q1 APIs/tests were read.

| Check | Verdict | Observed proof and limit |
| --- | --- | --- |
| CHECK-INVENTORY | VERIFIED-WITH-LIMITATIONS | Common discovery owner; exhaustive receipt partitions; rename/delete/untracked; real junction/read/walk failures; explicit unsupported inputs. New actual CLI retains ignored untracked Python plus tests/examples/benchmark inputs. Deliberate compiled exclusions remain explicit. No universal filesystem/platform claim. |
| CHECK-GRAPH | **NOT-VERIFIED** | F1 contradicts actual CPython resolution. Existing conditional/relative/local imports, zero-import receipts, directed/self cycles, same-count replacements and all five architecture rules otherwise pass. New real CPython nested relative-import oracle passes; non-package child import is conservatively unresolved/unavailable. |
| CHECK-PARTIAL-PROBE | VERIFIED-WITH-LIMITATIONS | Actual CLI retains exactly nine required metrics, unavailable/incomplete/fail and exit 1; malformed/overlapping config exits 2. New actual two-code-file complete baseline establishes greenfield, still with seven missing metrics. These field semantics do not validate F1's numeric content. |
| CHECK-RECONCILE | **NOT-VERIFIED** | Existing source/revision/controller/config/approval/run/artifact/receipt/aggregate corruption cases pass, including rehashed raw forgeries. Fresh same-storage roots are nevertheless accepted (F2). No reusable-green meaning is attached to archival hash consistency. |
| Q1 acceptance | **NOT-VERIFIED** | Both F1 and F2 require correction and independent replay before acceptance. |
| Q2 | BLOCKED | Q1 verification/review prerequisite not passed; no external tools or JS parser adapter qualification. |
| Q3, Q4, Q5 | NOT-VERIFIED | Not executed by this bounded role. No coverage, mixed mutation, final root quality or release acceptance. |

Mixed-language CLI proof in the existing replay keeps MJS/CJS receipts
unsupported and **all nine measurements missing**, never green. Enumeration,
syntax, unresolved imports and actual dense-cycle budget failures remain
unavailable/incomplete. Canonical directed-cycle identities and replacement
architecture identities are tested from real files; those cases passing does
not excuse F1.

### Parent acceptance-criterion reconciliation

These are this verifier's bounded verdicts, not retroactive changes to parent
acceptance records:

| AC | Verdict in this role |
| --- | --- |
| AC01 | VERIFIED-WITH-LIMITATIONS: existing native probe regression produces a real assertion-kill fixture result; broader ESM/CJS implementation and mixed Python mutation are not reaccepted here. |
| AC02 | **NOT-VERIFIED for Q1**: missing-as-fail and nine-field completeness behavior pass, but F1/F2 prevent accepting source-bound Q1 measurements as correct. |
| AC03 | NOT-VERIFIED: guarded readiness outside Q1; C1 files not explored. |
| AC04 | NOT-VERIFIED: guard command execution outside Q1. |
| AC05 | NOT-VERIFIED: no fresh-resume lifecycle experiment in this role. |
| AC06 | NOT-VERIFIED as a whole: Q1 failure boundaries exercised, not the full workflow/held-out diagnosis evaluation. |
| AC07 | NOT-VERIFIED: migration/canonical trigger work outside Q1. |
| AC08 | NOT-VERIFIED: research/status integration outside Q1. |
| AC09 | **NOT-VERIFIED for Q1 acceptance**: scoped legacy/Q1 regressions pass but new functional failures remain; separate review is still due. |
| AC10 | NOT-VERIFIED: packaging/docs/rendering are parent-owned and not changed or accepted here. |

## Exact execution and results

All commands ran from:

`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Observed existing branch: `shbs-microsoft-workflow-app-verification`;
origin: `https://github.com/shankar029/bulletproof.git`.
Read-only Git identity/status commands used the managed Python runner with
`--idle 30 --max 90`. No Git writes outside fixture repositories.

The capture harness starts the standard-library unittest discovery/runner in a
child within the outer runner's bounded process tree. It captures the child's
actual stdout/stderr as bytes, before the outer runner's text forwarding.
This is **not** a claim that `python -m unittest` was the literal executed argv:
the exact worker argv is recorded in each `*-command.json`.
Fixture CLI/native commands have their own byte captures and exact argv/cwd.

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'

& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-capture.py capture 'test_measure_*.py' existing-q1
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-capture.py capture test_probe.py legacy-probe
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-capture.py capture test_measure_q1_verification.py adversarial
$env:Q1_VERIFICATION_TAG='r2'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-capture.py capture test_measure_q1_verification.py adversarial-r2
$env:Q1_VERIFICATION_TAG='r3'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-capture.py capture test_measure_q1_verification.py adversarial-r3
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-finalize.py
```

The first discovery happened before the new verifier file existed: it ran
exactly the original **28 tests**. A new discovery of that pattern now also
includes the six verifier tests. Replay with fresh labels/tags to preserve prior
evidence; ZIP creation deliberately refuses an existing archive.

| Run | Tests | Actual unittest time | Exit | Result |
| --- | ---: | ---: | ---: | --- |
| existing-q1 | 28 | 443.177s | 0 | 28 passed |
| legacy-probe | 19 | 58.607s | 0 | 19 passed |
| adversarial (initial harness) | 5 | 76.723s | 1 | 1 passed, 4 **verifier archive-copy errors** |
| adversarial-r2 | 6 | 93.085s | 1 | 5 passed, F1 failed |
| adversarial-r3 (final) | 6 | 95.276s | 1 | 4 passed, F1 and F2 failed |

Initial path-length errors were from copying deeply nested fixture archives
beneath the already-long worktree path, **not production failures**. Initial
raw outputs and partial copies were kept. ZIP containers preserve the original
member paths/bytes without requiring long extracted filesystem paths.
R1/r2 verifier source copies are preserved as
`q1-independent-verification-r1.py` and `q1-independent-verification-r2.py`.
R3 corrected the inadequately strong stale-hardlink check, not production.

For direct finishing/replay after owner corrections (no acceptance implied):

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts/run.py --idle 120 --max 1200 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -m unittest discover -s scripts/tests -p 'test_measure_*.py' -v
```

Then rerun scoped legacy probe tests and the separate independent review; Q2+
and release remain separate unaccepted work.

## Input freshness and evidence integrity

`q1-independent-final-manifest.json` contains **182 pinned frozen inputs with
identical observed/final hashes**, including measurement transitive repository
dependencies (`mutate.py`, evidence, runner and native reporter), exact existing
test/helper inputs, imported Python standard-library modules/native modules,
managed Python EXE/DLLs, and resolved Node/Git executable files.
This is **not** an OS-wide dependency closure or whole-repository stability
claim. Unrelated parent/C1 writers were active.

Per-run before/after manifests are preserved:

- Original Q1: **130 pinned files unchanged**; one lazy `_ast_unparse.py` file
  first recorded after execution.
- Legacy probe: **175 unchanged**, no late imported files.
- Final r3: **137 unchanged**, no late imported files; `_ast_unparse.py` was
  explicitly loaded and pinned before tests.
- No frozen production/test/contract dependency change was observed. The
  verifier and its capture harness changed only **between completed runs**;
  `changed_since_run` records those intentional changes rather than claiming
  earlier evidence pins the final harness.
- All captured test-run raw stdout/stderr hashes recheck.
- All **six final ZIP archives**, totaling **166 member files**, match their
  exact manifests. This is archival mapping consistency only, not reusable
  current-invocation green permission.

### Selected SHA-256 (before = final)

Full absolute paths, byte lengths and before/final pairs are in the manifest.

| Input | SHA-256 |
| --- | --- |
| scripts/measure.py | `4754fe05621b81a8d499c38dbb913619dd43af50782d07b058849d50994ef8ed` |
| scripts/measure_graph.py | `17f50ca7b304bba114131d7578d0250979df3d113201593d99b67e8479fa5245` |
| scripts/probe.py | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| scripts/mutate.py | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| scripts/evidence.py | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| scripts/run.py | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| scripts/native_result.mjs | `528aeec659fde03cab9edd3167a8b2bc184b7194a3f534dd13a4e0a0c38163e0` |
| managed python.exe | `5829a9ef2930e10a965503ea0f96248bd4b19faf4177fdfd061f1d484448bb03` |
| python314.dll | `0f2429383aacc0499f57e732fc7778da6187d133af9171b938a66fe7d5ab254c` |
| resolved node.EXE | `8f3e33fa1f67843a320d2200ed1a5d40cc59766715a7a02728b8213c2167a084` |
| resolved git.EXE | `7f2d8f209c65b27a1cb6ae388b59877afcf5d17e67d04ba7b4a237849380d1e2` |

Final verifier test SHA-256:
`f58d77f2cc957d7eae0bfaf4a3f99a63370fc1901a2b5312ce43b3a445bb19c6`.
Final six-test raw stderr is **3,288 bytes**,
`0842e4b50d30de69ae5bf583cc46ed8d35ae07059479760a1040b03d77685562`.

## Bounded handoff

Return F1/F2 to the production owner; retain the failing tests and all raw
counterexamples. No acceptance or production repair is performed here.
Q1 and the affected AC02/AC09 portions are **NOT-VERIFIED**.
Q2, later measurement slices, separate independent review and release remain
unaccepted. `state.md` is intentionally left to the parent.

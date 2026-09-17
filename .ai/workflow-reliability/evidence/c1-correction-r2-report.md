# C1 correction iteration 2 — exact consumed closure proof

## Disposition

**Residual F1 corrected locally; source frozen for original verifier replay
and separate review.** No independent acceptance, quality pass or C2
advancement is claimed by this implementation return.

Read and preserved `c1-independent-r2-verification.md` and the new independent
`scripts/tests/test_workflow_core_verification_r2.py`, as well as the original
independent tests/evidence. Reproduced the exact residual assertion before
editing production. F2/F3 code was not changed.

Only these existing files changed in this iteration:

- `scripts/workflow_gate.py`
- `scripts/tests/test_workflow_gate.py`

All other writes use the additive `c1-correction-r2-*` evidence prefix.
No changes to workflow_state, the fixture helper, Q1 modules, schemas, shared
state, independent tests/reports, CLI/runner, OS settings or installation.
No agents, commit, publication, broad quality probe or metric waiver.

## Root cause and fix

FACT: the pinned red run reproduced a closure at sequence 32 rewritten to
consume the replacement receipt accepted at sequence 38. It incorrectly
reported the increment complete and its dependent ready.

The first correction required valid proof in the closure's prefix, but reduced
that proof to booleans. Separate full-ledger reference equality then allowed
different, later references to match the corrupted closure. The two conditions
did not bind the same proof.

`_Evaluation.closure_proven_before()` now retains each prefix dependency's
full `(state, reason, receipt_refs)` result and requires BOTH:

1. Every prefix dependency is valid.
2. The union of those validated prefix references exactly equals the closure's
   recorded `(receipt ID, SHA-256)` set, using existing `_merge_refs` and
   `_refs_equal`.

The implementation delta is:

```python
proofs = [prior.proof(dep) for dep in dependencies(self.contract, item)]
return (all(state == "valid" for state, _, _ in proofs)
        and _refs_equal(event["receipt_refs"], _merge_refs(proofs)))
```

This replaces the previous boolean-only prefix check. No second graph,
reference index, schema field or parallel proof authority was introduced.
Order-insensitive reference equality retains the existing set semantics.

### Full supported boundary reviewed

- **Direct checks and null-command handoffs:** prefix proof selects only
  accepted receipts present before closure, and now preserves their exact IDs
  and hashes through closure validation.
- **Action prerequisites and transitive checks:** existing proof recursion
  validates their acceptance order, source/contract bindings and prerequisite
  reference chain; the closure compares the same derived reference union.
- **Prerequisite increments:** their own closure checks recursively apply the
  exact-prefix invariant. A later legitimate prerequisite reclosure cannot
  backfill an older dependent closure's consumed references.
- **Ship:** the same closure path covers the union of increment closures.
  A new valid underlying increment closure is not proof for an earlier ship
  closure claiming its future references.
- **Current validity remains required:** existing full-ledger dependency
  validity, exact current reference equality, source/component/action/check/
  claim freshness, mandatory member execution, outcome, commit syntax, temporal
  consumption and independence checks were not removed or weakened.

Some earlier valid proof is no longer sufficient for different claimed proof.
If all needed proof exists now, a root target may be `ready` for a new
legitimate closure; the old invalid closure is not `complete`, and a consumer
requiring that recorded closure remains blocked. Recording a later legitimate
closure is tested positively rather than rewriting history into success.

## New owned regression cases

Four tests were added to `test_workflow_gate.py`:

| Test | Observable assertions |
|---|---|
| `test_future_handoff_receipt_cannot_replace_exact_closure_proof` | Original closure/dependent ready positive; future null-command review replacement requires reclosure; corrupting only old refs cannot complete or dispatch the dependent; later legitimate reclosure succeeds; original receipt bytes unchanged |
| `test_transitive_action_proof_must_match_closure_prefix_exactly` | Origin check → middle check → work → closing checks; replacing the entire current chain cannot backfill the old closure; legitimate reclosure succeeds; later source change still blocks |
| `test_inherited_increment_receipts_cannot_be_backfilled_into_closure` | A closes; B inherits A closure; A receives new proof/reclosure and B reruns against it; old B refs cannot be substituted with the new exact set; later B reclosure succeeds |
| `test_ship_cannot_substitute_receipts_from_a_later_valid_reclosure` | Initially complete ship; later valid A reclosure/current proof cannot satisfy old ship by ref substitution; later actual ship reclosure succeeds |

Positive reclosures reverse reference-list ordering to prove ID/hash set
semantics rather than accidental list-order dependence. The independent direct
check substitution test is unchanged and passes. Earlier member-execution,
closure-order, temporal, F2/F3, purity, freshness, identity and metric-negative
tests all remain in integrated discovery.

These are real public-library/filesystem assertions over explicitly synthetic
protocol fixtures. No receipt/model/metric/process fixture is presented as
actual independent review, quality collection, guarded child execution,
authenticated identity or a fresh-agent exercise.

## Exact execution and raw evidence

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Managed runtime:
`P = C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

Capture invocations:

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r2-capture.py red
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r2-capture.py workflow
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r2-capture.py evidence
```

Each launches the following exact inner form (full argv arrays in manifests):

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p PATTERN -v
```

Patterns respectively:
`test_workflow_core_verification_r2.py`, `test_workflow_*.py`, `test_evidence.py`.
They are literal argv items, not shell-expanded. `PYTHONDONTWRITEBYTECODE=1`.
The capture helper streams raw progress to its outer idle monitor and saves
captured bytes directly to new log files. It refuses to overwrite prior
captures. Non-interactive owned fixture subprocesses retain their existing
idle 30/max 90 bounds.

| Run | unittest result | unittest time | command exit |
|---|---|---:|---:|
| Red reproduction | 1 test, exact residual F1 assertion failure | 1.959 s | 1 |
| Integrated workflow | **75/75 passed**, no errors/skips | 94.737 s | 0 |
| Evidence regression | **10/10 passed**, no errors/skips | 5.381 s | 0 |

Workflow inventory: 71 pre-existing tests (including both independent files)
plus four owned correction tests. Final bounded total: **85 passing tests**.
No timeouts, retries, missing tools or cleanup failures were observed.

Files:

- `c1-correction-r2-red.stdout.log`, `.stderr.log`, `.json`
- `c1-correction-r2-workflow.stdout.log`, `.stderr.log`, `.json`, `-imports.json`
- `c1-correction-r2-evidence.stdout.log`, `.stderr.log`, `.json`
- `c1-correction-r2-capture.py`
- `c1-correction-r2-handoff.json`

Raw streams, byte counts, SHA-256, exact argv/cwd/runtime, durations and
before/after pins are in each manifest. Narrow red and evidence runs do not
execute the original independent module's optional import hook; their
observed-import counts are explicitly zero, not invented import censuses.
Actual child test exit codes are retained; capture returns 2 on a freshness
mismatch rather than treating captured output as a pass.

## Freshness, preservation and frozen hashes

FACT:

- **1,903 scoped files** were pinned before/after each run, with zero changes
  within any run.
- Integrated workflow observed **172 file-backed imports**; all matched
  before/during/after pins, including the actual frozen Q1 dependency chain.
- Handoff recheck: all **1,903** workflow-pinned files remained unchanged.
- Red-to-green changes: exactly workflow_gate.py and its owned test file.
- All **30 independent artifact files** in the census and both independent
  test files remained unchanged.

Census scope: repository top-level Python runtime modules; workflow-discovered
tests; workflow/evidence helpers and evidence test; managed Python runtime
files; explicit accepted C1 contracts; prior independent artifacts; this
capture helper. Unrelated Q1 tests/docs/evidence are excluded because their
owner may write them concurrently. This is not a whole-repository or OS/DLL
attestation, future-freshness guarantee, or edit-and-revert detector.

SHA-256 of frozen relevant files:

| Path | Hash |
|---|---|
| `scripts/workflow_gate.py` | `a703ef74ba71ad2205b7dc4d0293a6acf3a14a8dcdccda337ec9274ec924251f` |
| `scripts/tests/test_workflow_gate.py` | `3db660fa4bf50550a613089d12f97c6f2d94da590263e9d05736f493a58fa7c1` |
| Unchanged `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| Unchanged `scripts/tests/test_workflow_state.py` | `7b259c0f2e6c4e31a5c614769995df97f999fe86ed44b0e1351e3ee7a2d72466` |
| Preserved `test_workflow_core_verification.py` | `c9c1181ae017f7d42415ca848777fbac388152c18eb57a839f8631132a9e5a8d` |
| Preserved `test_workflow_core_verification_r2.py` | `d58655d83ac448c788d9217d1365631e24e20778b7a9b8b89dcadc32af9ae11b` |
| Q1 `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| Q1 `scripts/measure.py` | `4754fe05621b81a8d499c38dbb913619dd43af50782d07b058849d50994ef8ed` |
| Q1 `scripts/measure_graph.py` | `17f50ca7b304bba114131d7578d0250979df3d113201593d99b67e8479fa5245` |

## Self-review / next owner

Reviewed the complete relevant flow: `_merge_refs`/`_refs_equal`, action
completion and prerequisite chronology, check receipt selection/validation,
historical consumption, increment/ship proof, and prefix recursion. Re-opened
the changed method after the integrated run. In-memory AST/compilation,
import-use, final-LF and trailing-whitespace checks passed on the two changed
files. No public signature or persisted schema changed.

No full quality, mutation, coverage, lint/type toolchain, native corpus,
live CLI/process recovery or host experiment is claimed. The tests establish
the bounded supported cases above, not exhaustive correctness or an
independent gate verdict.

**Stop:** owned C1 source is frozen. Parent returns this snapshot to original
verifier `a02590d4-37a7-4531-ae44-21f0e15cfed3` for replay and then obtains the
separate review. Historical NOT-VERIFIED returns remain intact. Shared state,
Q/I1.T4/release and C2 are not advanced by this return.

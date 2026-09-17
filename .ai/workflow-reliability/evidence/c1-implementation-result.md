# C1 implementation result

## Disposition

**Implemented within the C1 write boundary; local tests passed; independent
acceptance remains pending. Shared-dependency freshness reopened at handoff.**

The original pre-code finding remains unchanged in `c1-implementation.md`.
Implementation resumed only after the parent accepted
`guard-resolution-contract.json` and the separate APPROVE in
`c1-boundary-review.md`. This return is implementer evidence and self-review,
not an independent verification/review verdict, quality pass or C2 authorization.

### Freshness stop

FACT: the final handoff hash check observed a concurrent edit to
`scripts/probe.py`, which C1 imports for its existing pure `judge()` and
`default_policy()` functions:

- Earlier handoff observation:
  `993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82`
- Subsequent observation after the final local test run:
  `830649929fedd2dbfb107ab98d1df28246246443fd5516042fdf3028d9fa56cf`

The worker did not edit probe.py. The 52-test pass below was observed, but the
exact dependency bytes loaded by that run were not pinned before/after it.
**Do not call it final-tree/source-fresh acceptance.** Parent must serialize
shared source writers, capture dependency hashes, rerun the targeted commands,
then obtain separate verification/review. No broad measurement was attempted.
Other concurrent parent files, including measurement work and README/rendering
artifacts, were left untouched.

## Delivered APIs and ownership

Only these five C1 source/test files were created:

| File | Responsibility |
|---|---|
| `scripts/workflow_state.py` | Strict records, derived dependency traversal, validated paths/design history, materialized proof/input views, atomic ledger append |
| `scripts/workflow_gate.py` | Pure readiness and fixed result/provenance/temporal decisions |
| `scripts/tests/test_workflow_state.py` | 21 state/persistence behavior tests |
| `scripts/tests/test_workflow_gate.py` | 31 gate/integration behavior tests |
| `scripts/tests/workflow_fixtures.py` | One workflow-specific owned fixture helper; no shared helper edits |

Public call boundary:

```python
load_workspace(root: Path, slug: str)
# -> (WorkflowContract dict, CurrentDesign dict, ResolvedLedger)

bind_inputs(root: Path, contract: dict, target: dict) -> ResolvedInputs

append_event(workspace: Path, event: dict, expected_seq: int) -> dict
# event contains Event fields except seq; the returned Event has assigned seq.
# Caller already holds the exclusive workspace lock.

evaluate(contract, ledger: ResolvedLedger, inputs: ResolvedInputs, target)
# -> ordinary Readiness dict; no I/O or mutation of supplied views.
```

Named frozen dataclasses: `ReceiptObservation`, `ResolvedLedger`,
`BlockedInput`, `ResolvedInputs`. Their nested dictionaries are ordinary
materialized Python values, not authenticated/immutable memory. Persist only
`ResolvedInputs.target` where a GuardSnapshot is required; never serialize the
resolved views. `SequenceConflict` distinguishes an expected-sequence failure;
malformed top-level data raises `ValueError`. Filesystem errors are not silently
converted to successful proof.

Supporting pure validators and `dependencies`, `dependency_closure`, `target`,
`target_key`, `canonical_hash` are available in workflow_state. `read_json`,
`safe_path` and receipt resolution own I/O. The gate imports no runner and never
reads files; it reuses probe's pure policy helpers rather than copying the
existing comparison tolerances. Dependency direction remains guard → existing
measurement policy/evidence primitives, never measurement → guard.

## Implemented behavior and local proof

All test data claiming pass/review/metric/process outcomes is explicitly labeled
**synthetic protocol fixture data**, not actual independent roles, native-quality
collection, process-lifetime evidence, human approval or a model-effectiveness
experiment. Files, hashes, atomic replacements, link checks and subprocess
library invocation are real.

| Requirement area | Relevant persisted tests / assertions |
|---|---|
| Strict data | Duplicate JSON keys (including nested), NaN/Infinity/overflow, unknown keys/versions/enums, boolean-as-integer, IDs, hashes, UTC times, canonical snapshots, duplicate normalized paths/reference IDs |
| One graph | Cycles, missing references, orphan/duplicate check actions, forbidden edge kinds, missing owned closure review/verification/metrics/scenario checks |
| Admission vs closure | Work/check execution is admitted without waiting on its own closing checks; inherited prerequisite increments still require closure; execution alone is not correctness/closure |
| Persistence | Atomic replacement failure preserves old bytes; sequence conflicts and caller-assigned seq fail; immutable blob must exist before reference append |
| Design integrity | Candidate review hashes, reviewer context, unattended authorization, retained revision paths/bytes, component hashes, history/supersedes and adoption-pointer consistency |
| Receipt proof | Missing/malformed/changed receipts and artifacts, recursive missing/cyclic chains, exact prerequisite receipt hashes, independent producer vs recorder, required findings/scenarios and human confirmation |
| Freshness/reopening | Source, component and check changes reopen relevant work; replacement prerequisite invalidates dependent receipt; unrelated receipt IDs/bytes remain unchanged |
| Temporal proof | Earlier consumed compatibility survives retirement as historical proof; separate post-change checks remain due; absent legacy paths and acceptance-sequence backfill fail |
| Red/metrics result checks | Matching native assertion identity/line/operator/symptom vs setup/log phrases; required metric omissions, wrong run, unavailable proof, numeric floor/summary/scope mismatch, greenfield cycles |
| Research | Section/source hashes, attributed bound acceptance, UNKNOWN claims, retained superseded claims, corrected active claim and unaffected branch retention |
| Process boundary | Intent before observations, stable observed identity, unresolved admission/direct exit/bare recovered event remain conservative; external handoff awaits response |
| Pure/fresh-process seam | Gate invoked with file APIs patched to raise; inputs unchanged; fresh Python process loads only fixture artifacts after edit and reports A blocked / B complete |

The fresh Python process test is a library integration/resume test. It is
**not** the later fresh-agent host exercise. Test PIDs are labeled fixture
protocol identities; no live-child crash/recovery experiment was claimed.

## Exact local test commands and observed results

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Managed runtime:
`P = C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

The PowerShell process set `PYTHONDONTWRITEBYTECODE=1`. All commands were
non-interactive; discovery patterns were passed as single literal argv items.

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p test_workflow_*.py -v
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p test_evidence.py -v
```

| Run | Observed result |
|---|---|
| First C1 run | 39 tests, 31.302 seconds, exit 1: 38 passed; consumed-compatibility closure assertion failed |
| After temporal fix and added cases | 46 tests, 36.830 seconds, exit 0 |
| Unchanged evidence suite | 10 tests, 5.344 seconds, exit 0 |
| After source self-review regressions | 52 tests, 40.432 seconds, exit 0 |
| Final C1 source/test cleanup snapshot | **52 tests, 40.384 seconds, exit 0**; shared-dependency freshness caveat above applies |

Final observed summary:

```text
Ran 52 tests in 40.384s
OK
```

Short helpers used `P -B scripts/run.py --idle 30 --max 90 -- P -B -c <inline code>`.
The final helper parsed/compiled all five C1 files in memory, required a final
LF and no trailing whitespace, checked AST imported names for use, and ran
this command for each new file using bounded `run_capture(idle=30,max_total=90)`:

```text
git --no-pager diff --no-index --check -- /dev/null FILE
```

All five checks produced no stdout/stderr and exit 1 (new-file differences).
The first helper incorrectly required no-index exit 0 and failed on the first
file; the corrected helper accepts 0/1 only with empty diagnostics and passed.
That diagnostic assumption failure was not a product/test failure. No bytecode
or helper output files were generated, no timeouts occurred, and no test was
skipped. Owned temporary fixtures registered cleanup with unittest.

## Source self-review and interpretation choices

Self-review addressed:

- Historical check-action execution must not require retired source to reappear.
- Receipt resolution hashes and parses the same byte read; malformed/missing
  recursive proof remains an observation rather than a pass event.
- Artifact observations retain changed/missing hash/size facts.
- Ordinary as well as before-action prerequisites require earlier acceptance
  sequence; timestamps cannot manufacture that order.
- Admission binds the then-current adoption; process identity/exit facts must
  agree across lifecycle observations.
- Reviewer/verifier contexts and declared implementer ownership cannot be
  substituted with the recorder or another increment's mandatory checks.
- Reopened entries name the prior accepted receipt IDs; check-target and
  action-target views both recognize an awaiting external handoff.
- Removed unused test imports; explicit overflow-number JSON rejection.

No new persisted top-level keys or duplicate graph/status authority were added.
Concrete interpretations for parent/verifier review:

1. All stored paths are repository-relative. Receipts use
   `.ai/<slug>/evidence/receipts/<id>.json`; current design uses retained
   `design-history/REV.html` and `contracts/REV.json`. The normative contract
   file is a component-ID → JSON normative value map; each value is canonically
   hashed. Canonical JSON follows evidence.py's sorted UTF-8 + final LF convention.
2. `DesignReview.unattended_authorization` is a hashed `{path,sha256}` reference.
   Research scope is nonempty descriptive JSON; report anchors address ATX
   Markdown headings (or explicit `{#anchor}` headings). Source lines are
   positive line-number lists. Semantic truth of prose remains reviewer-owned.
3. Mandatory review/verification/metrics checks belong to the increment being
   closed; prior checks may still be extra regression prerequisites. Command
   cwd must exist; exact workflow-owned output exclusions cannot name directories.
4. Native assertion matching uses repository-relative `test_file` identities.
   C2 must reconcile the actual producer's absolute native paths before writing
   its structured receipt, while preserving raw returned artifacts unchanged.
   Raw producer/guard receipt integration is not demonstrated by fixture data.
5. The gate consumes strict r2 MetricVerdict/MetricPolicy records. The existing
   standalone producer's actual report projection/legacy extra fields require
   explicit C2 reconciliation, not a schema bypass or imported green report.
   No actual quality report was accepted by this C1 run.
6. A requested target whose own snapshot cannot be materialized raises an input
   error; failures materializing only prerequisite targets become BlockedInput.
   The future CLI must report these conservatively, never dispatch on them.

These interpretations/integration limits require parent review before C2;
none is a claim of accepted live CLI compatibility.

## Final inspected C1 manifest

SHA-256 of the five files after the final test run and cleanup:

| File | Hash |
|---|---|
| `scripts/workflow_state.py` | `e9e6b2ddf15417f22444bd143c5ddd9bcf1f0deb7f9c6d1ac0eb4d451c32eaaa` |
| `scripts/workflow_gate.py` | `213d9be7f046d4a5a341f5702ff63d439e9ea20d4072715d430281028a4d7327` |
| `scripts/tests/workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `scripts/tests/test_workflow_state.py` | `a29c923cb0f3bd44b52c206ae5d59492d69591c5a2afedfe905ccf709024798b` |
| `scripts/tests/test_workflow_gate.py` | `b7d9a1c11655749b72132e9e24af4ebb6180b1039bede9bf1006a2a178936498` |

Additional inspected inputs:

| File | Hash |
|---|---|
| r2 `design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |
| `guard-resolution-contract.json` | `401762912eb5bd399eb16117252b497bbf9d0088a6c85505fb3ff21a681209e8` |
| `evidence/c1-boundary-review.md` | `2a2931a026f7753b681a54329a296c58013039a8dda09462343759c0f68de214` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| `scripts/mutate.py` | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| `scripts/tests/helpers.py` | `2694cd24dd07b1a6e3ceff7ac2addb7d4fc8bc40ee197f6d3c4206d281bf2068` |

This is not an exhaustive transitive-dependency or final release manifest.
Probe's concurrent hash change is reported separately above rather than hidden.

## Remaining limits and next owner

- Parent owns shared state.md and integration. Record this C1 handoff and
  reopened dependency freshness without rewriting the historical blocker.
- Freeze shared inputs, run the exact targeted commands above, then dispatch
  a fresh verifier and a distinct reviewer. No nested agents were used here.
- C2 must implement actual CLI/runner-observer dispatch, supported recovery and
  branch/commit/source checks. C1 validates full commit syntax but does not
  inspect Git commit contents. A bare recovered Event cannot clear unresolved
  execution in C1; no termination-evidence integration is claimed.
- C1 does not create/adopt real workflow state for this repository. The fixture
  adoptions are test protocol data, not retrospective admissions.
- No full-suite/native/corpus run, coverage, lint/type toolchain, broad probe,
  mutation, live-child crash, authenticated independence, host fresh-agent
  experiment, install, OS-setting change, commit or publication was performed.
- I1.T4/release quality remains blocked. **Do not advance C2 until parent
  accepts independent C1 verification/review and the integration interpretations.**

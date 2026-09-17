# C1 correction iteration 3 / review round 1

## Disposition

**R1–R3 corrected locally; source frozen for original verifier replay and
separate reviewer recheck.** Final bounded result: **83 workflow tests plus
10 evidence tests passed**, no errors or skips.

This is not independent acceptance, a quality/mutation pass, C2 admission,
authenticated process evidence, or a declaration that Q1 is finally frozen.
Parent must reconcile the final dependency snapshot before acceptance.

Read the preserved reviewer return and parent disposition in
`c1-code-review.md`. No independent reports/tests, shared state, Q1 code,
CLI/runner, schemas, framework, installation, OS configuration, commits or
publication were changed. No nested agents were used. The accepted original
F1/F2/F3 mechanisms and all their independent regression tests remain intact.

Only existing source/test files changed:

- `scripts/workflow_gate.py`
- `scripts/tests/test_workflow_gate.py`

Other writes are additive `c1-correction-r3-*` evidence files. Earlier
correction and NOT-VERIFIED/REVISE history remains intact.

## Root causes and corrections

### R1 — receipt-supplied policy interpretation

FACT: before production edits, the owned regression matrix showed that a
schema-valid, rehashed floor/coverage rule could replace mandatory comparisons
and authorize a direct metrics consumer despite a regression. The owned matrix
uses 0→100 for lower-is-better metrics and 100→90 for score metrics; the
reviewer's original cycles 0→5 probe remains separately preserved in its report.

`_metric_result()` now calls the existing authoritative `judge()` for every
required measurement, independently of its supplied mode. A failing/unavailable
comparison or a false claimed comparison blocks proof. Supplied numeric floors
are additional constraints, never substitutes.

- Required metric membership, measured inventory, admitted run/source,
  artifact presence, baseline completeness and summary consistency remain.
- Mutation's minimum is read from `default_policy()` (currently 60), not
  selected by the receipt.
- Explicit floor/coverage thresholds must actually be met.
- A numeric threshold on `compare` is rejected instead of silently ignoring an
  alleged extra bar. Numeric extra bars use the existing floor/coverage modes.
- Coverage without an explicit numeric bar blocks, consistent with the
  accepted contract's missing-coverage-bar rule; no default coverage value was
  invented.
- Existing brownfield tolerances and known-greenfield comparisons remain
  authoritative. Legitimate warnings are accepted only when correctly reported.

No collector policy was edited. A supplied repo-source origin remains a
declared protocol origin, not authenticated provenance; actual native producer
projection and observation of repository policy remain C2 integration duties.

### R2 — passing-looking results from failed producers

FACT: the pre-fix tests reproduced direct-consumer authorization from failed
spawned metrics and finding producers, including recorded timeout-code
contradictions. These are fixture exit records, not claimed live timeouts.

`_command_succeeded()` centralizes the conjunction:
`child_exit == 0` **and** `outcome == "executed"`.

`_receipt()` now applies it before metric/finding/native-green proof for every
command-backed check. Review, verification, research and human findings all
use this shared path. Null-command attributed handoffs remain separate and
continue to pass their finding/identity validation.

Behavioral red is the only unsuccessful-command exception:

1. Recorded completion outcome must be `fail`.
2. Existing native validation must establish the declared relevant assertion
   failure, including source/line/symptom binding.
3. Zero/absent/124/125/127 exits, setup errors and other non-assertion failure
   records cannot establish behavioral red.

`_execution()` also validates that exception when an action directly consumes
the red producer action rather than its check. The validated receipt is
included in returned proof references, so consumption binds its exact ID/hash.
A replacement red receipt reopens the consumer's prior execution.

#### Positive-control correction within this iteration

The first integrated run exposed a valid direct-action red case as blocked.
The derived input view materializes the required action, not a separate check
key. `workflow_state._target_actions()` and `_snapshot_for()` already produce
identical source/component/action/check/claim snapshots for a check and its
registered action.

The gate now reuses that exact action snapshot when its check key is absent.
An explicit blocked check observation is not replaced. There is no filesystem
fallback, synthesized digest, different target-wide scope, new graph edge or
persisted field. The test compares the two real materialized snapshots, then
tests valid direct consumption and replacement-receipt reopening.

The failed intermediate run is retained, not relabelled green.

### R3 — repeated prefix proof work

FACT: pre-fix serial-chain tests repeated the exponential evaluator counts.
Each closure created a fresh evaluator and discarded reusable earlier-prefix
memo results.

Each public `evaluate()` now owns a registry of prefix evaluators keyed by
event-count boundary. Each prefix evaluator retains its existing target-keyed
memo and active-cycle guard. Repeated access to the same `(target, prefix)`
uses that memo. Contract, resolved receipts and input snapshots are fixed
throughout this evaluation.

- No global cache, persistent cache, callbacks or cross-call state.
- Current and historical memos stay separate, preserving current-only
  `reopened` diagnostics.
- Exact pre-closure receipt-reference equality remains unchanged.
- Prefixes still exclude the closure event and all later events.
- Changing source between public calls still blocks; restoring original bytes
  yields valid proof again in a new call.

Observed deterministic scaling (constructor/proof wrappers delegate to real
implementation; they do not replace proof behavior):

| Chain size | Before evaluators | Final evaluators | Final uncached proof evaluations | Unique `(prefix,target)` pairs |
|---:|---:|---:|---:|---:|
| 3 | 8 | 4 | 87 | 87 |
| 5 | 32 | 6 | 195 | 195 |
| 8 | 256 | 9 | 432 | 432 |

Tests assert successful closure, at most `n+1` evaluators, no duplicate uncached
target/prefix work, and a quadratic work-count upper bound. No fragile elapsed
threshold is used. This worker tested up to eight increments; the reviewer's
larger-chain timing remains its historical evidence, not a new performance
measurement. Event scans and reference merging still have costs; this is not
a claim of constant-time or whole-workflow linear-time evaluation.

## Persisted owned coverage

Eight new test methods (`test_review_*`) cover:

1. Every required metric under both floor and coverage mode substitutions,
   with direct-consuming-action status/command assertions.
2. Genuine numeric tightening, insufficient scores, mutation-floor weakening,
   and later valid replacement proof.
3. Known-greenfield cycles, correctly reported warnings, false warning
   summaries, absent coverage bars and unsupported numeric compare rules.
4. Metric exits 1/124/125/127 versus successful command controls.
5. Every finding kind with failed producer controls and valid null-command
   handoffs.
6. Exit/outcome contradictions in both directions, plus successful control.
7. Valid native red, timeout/setup-like negatives, direct producer-action
   consumption, exact reference propagation and replacement reopening.
8. Deterministic serial-prefix work sharing and fresh-call source changes.

Six methods were persisted and run before production edits. Two additional
edge/positive-control methods were then added. The final workflow inventory is
48 owned gate tests + 23 owned state tests + 12 unchanged independent tests.
All original exact-closure, temporal, no-spawn, UTC, purity, persistence,
identity and selective-reopening tests pass.

Fixtures use real persistence, materialization and gate invocation, with
explicitly synthetic protocol/native/metric records. They are not actual
quality collection, independently produced findings, process authentication,
or a live agent/CLI exercise. Native evidence/fixture helpers were not changed.

## Exact bounded commands and retained results

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

`P` below expands to:
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-capture.py red
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-capture.py workflow
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-capture.py evidence
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-final-capture.py workflow
P -B scripts/run.py --idle 120 --max 900 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-final-capture.py evidence
P -B scripts/run.py --idle 30 --max 90 -- P -B .ai/workflow-reliability/evidence/c1-correction-r3-handoff.py
```

Inner command form:

```text
P -B <absolute-repo>/scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p PATTERN -v
```

Patterns: red `test_workflow_gate.py` with `-k test_review_`;
workflow `test_workflow_*.py`; evidence `test_evidence.py`.
Full exact argv, cwd, runtime, raw stream hashes/byte counts, exit codes,
capture elapsed time and before/after fingerprints are recorded in manifests.
`PYTHONDONTWRITEBYTECODE=1`; fixture subprocesses retain idle 30/max 90 bounds.
Independent suites ran concurrently only with the separate evidence suite;
no source was edited while either pair ran.

| Capture | unittest result | unittest duration | child/capture exit |
|---|---|---:|---:|
| `c1-correction-r3-red` | 6 tests; 37 failed subtest assertions; no errors | 75.215 s | 1 / 1 |
| `c1-correction-r3-workflow` | 83 tests; one positive-control failure | 179.605 s | 1 / 1 |
| `c1-correction-r3-evidence` | 10 passed | 5.398 s | 0 / 0 |
| `c1-correction-r3-final-workflow` | **83 passed** | 175.043 s | 0 / 0 |
| `c1-correction-r3-final-evidence` | **10 passed** | 5.356 s | 0 / 0 |

Every capture has `.json`, `.stdout.log` and `.stderr.log` siblings.
Workflow runs additionally have `-imports.json`. Raw stderr from inner
unittest may appear in captured stdout because the bounded runner combines
its child's output. No timeouts, skipped tests, installs or suppressed failures.

## Freshness and preservation

FACT:

- Initial captures: **1,912 pins**, unchanged within each run.
- Final captures: **1,913 pins**, unchanged within each run; the additional
  pin is the additive final capture helper.
- Each workflow run observed **172 file-backed imports**, all matching its
  before/during/after pins.
- Narrow red and evidence runs do not execute the independent import hook;
  their observed-import count is explicitly zero, with full file census still
  recorded.
- Final handoff rechecked all **1,913 pins**, with zero changes.
- **38 prior independent artifact files**, both independent test files and
  the separately pinned `c1-code-review.md` stayed unchanged.
- Red-to-final changed production/test files are exactly the two owned files;
  the only added census entry is the final capture helper.

Census covers top-level Python modules, workflow-discovered tests, supporting
workflow/evidence helpers, the managed Python runtime, explicit C1 contracts,
independent artifacts, separate review and capture code. Unrelated concurrent
Q1 test/evidence/document writes are excluded. This is stable-interval evidence,
not an OS attestation, edit-and-revert detector or future dependency freeze.

Frozen C1 hashes:

```text
workflow_gate.py
f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d
test_workflow_gate.py
af23bb4d96ea9da28f15291dc2c4cbb8e0e9272a40b27140e28efc89f3993636
workflow_state.py (unchanged)
a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b
```

Actual tested/rechecked Q1 dependency hashes:

```text
measure.py
44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8
measure_graph.py
f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6
probe.py
bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e
```

These differ from the earlier Q1 freeze. No change occurred during this
worker's recorded intervals, but no new final freeze was authorized here.
Full file hashes/deltas are in `c1-correction-r3-handoff.json`.

## Self-review and handoff

Re-read the modified policy, execution, receipt qualification, snapshot alias,
prefix reuse and proof paths after tests. Confirmed preserved current freshness,
exact consumed references, prerequisite order, graph ownership, per-call cache
lifetime, explicit blocked snapshots and current-only reopening diagnostics.
The gate remains I/O-free and no public API or persisted schema changed.

In-memory AST/compilation, import-use, final newline and trailing-whitespace
checks passed for the two changed files. No full lint/type/coverage/mutation
or broad repository quality measurement is claimed; existing quality and
I1.T4 blockers remain.

**Stop at this frozen source.** Parent reconciles Q1's stable dependencies,
returns the correction to original verifier
`a02590d4-37a7-4531-ae44-21f0e15cfed3`, and requests re-review from
`bbe59c68-4708-4952-8f3d-7d91551302dc`. Local green does not close their gates.
No C2 admission or publication is performed by this return.

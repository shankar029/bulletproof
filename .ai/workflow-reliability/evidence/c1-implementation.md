# C1 implementation handoff — blocked before code

## Outcome

**BLOCKED: approval needed for the state-to-pure-gate data boundary.**
No C1 production or test files were created. No tests, quality probe, mutation,
independent verification/review, commit or publication were run. C2 is not
authorized by this handoff. I1.T4 and release quality remain blocked.

This is a pre-implementation interface finding, not a failed implementation
test, behavioral red, or independent review. No nested agents were launched.

## Grounding

FACT: read the accepted continuation plan, its independent review, current
state, design.html, r2 design-contracts.json, CONTRIBUTING.md, evidence.py,
tests/helpers.py and tests/test_evidence.py. The scoped discovery found no
existing workflow state/gate modules or tests.

FACT: HEAD is `aaec9b9851a9ce8f778943c5c088d6c4442e36f8` on
`shbs-microsoft-workflow-app-verification`. Initial status showed only the
parent's modified state.md and untracked continuation plan/research/review.
Those files were not changed by this worker. Parent retains state.md ownership
during concurrent work; this handoff requests recording the C1 blocker there.

### Blocking contract gap

FACT, against the contract hash below:

- `design-contracts.json:123`: the public gate signature is
  `evaluate(contract: WorkflowContract, ledger: Ledger, inputs: GuardSnapshot,
  target: Target) -> Readiness`, with a pure/no-I/O responsibility.
- `design-contracts.json:223-225`: GuardSnapshot has only `source` and
  `contract`. Neither contains resolved receipt bodies or artifact observations.
- `design-contracts.json:418-432`: Ledger contains version, slug and Events;
  Events contain receipt `{id,sha256}` references, not Receipt bodies.
- `design-contracts.json:386-409`: Receipt holds producer, result, prerequisite
  receipt references, artifacts and execution timestamps.
- `design-contracts.json:536`: the gate must recursively validate due receipt
  bytes, relevant bindings, prerequisite receipts, roles and actual outcome.

INFERENCE: the listed serialized inputs alone do not specify how the pure
gate receives the receipt results and filesystem observations needed for those
decisions. A reference hash is not its content. Checking only an Event's
`outcome=pass` would discard required result/role/provenance checks. Reading
receipts in evaluate would violate purity. Adding receipt maps to persisted
Ledger/GuardSnapshot would depart from their accepted strict schemas.

Related part of the same boundary: a target-scoped current source snapshot
needs an explicit projection/comparison rule for recursively required checks
with different FileScopes, including directory membership and exclusions.
One target digest cannot be compared directly with every prerequisite digest.

## Exact parent decision requested

Approve a bounded **in-memory resolved-view contract**, separate from persisted
JSON, before implementation. Recommended shape:

1. Keep the accepted on-disk WorkflowContract, Ledger, Event, GuardSnapshot and
   Receipt shapes unchanged and strictly validated.
2. Define the concrete in-memory objects returned by load_workspace and
   bind_inputs. A resolved Ledger view carries the validated ledger document,
   immutable receipt bodies keyed by ID, their observed byte hashes, and
   artifact-validation observations. A resolved input view carries current
   snapshots for the requested target and its derived prerequisite closure,
   keyed by canonical target; the graph still comes only from requires.
3. evaluate consumes these materialized values without I/O, global caches or
   hidden callbacks. Define how missing/tampered artifacts are represented so
   Readiness can report missing/stale/blocked rather than treating a historical
   accepted event as sufficient proof.
4. Specify which projection is serialized into Event.inputs / Receipt.inputs
   / Readiness.inputs (recommended: the single target's existing GuardSnapshot),
   and require fresh load/bind under the caller's already-held lock immediately
   before append/admission. None of these views is a second persisted graph.

The parent may select another explicit boundary; these are recommendations,
not accepted schemas or implemented APIs. In particular, do not silently add
`receipts` keys to persisted ledger.json or filesystem handles to pure inputs.

Once approved, C1 can implement strict validation/persistence first, pure graph
evaluation second, temporal/supersession behavior third, followed by targeted
tests and source self-review. No change to evidence.py or native measurement
dependency direction is proposed.

## Observed commands and counts

CWD for commands:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.

`P = C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`

- `P -B scripts/run.py --idle 30 --max 90 -- git --no-pager status --short`
  returned the parent-owned modifications described above; no C1 files.
- `P -B scripts/run.py --idle 30 --max 90 -- git --no-pager log -1 --format="%H %D"`
  returned the HEAD/branch above.
- `P -B scripts/run.py --idle 30 --max 90 -- P --version`
  exited 0, `Python 3.14.2`.
- PowerShell `Get-FileHash <six inputs below> -Algorithm SHA256` captured the
  manifest below; file reads and scoped searches were diagnostic only.
- The initial attempted `state/design-contracts.json` read failed because the
  contract is at `.ai/workflow-reliability/design-contracts.json`; that actual
  file was subsequently read. A combined file-existence probe exited 1 because
  the planned C1 files do not exist; this is not a product failure.
- **Tests run: 0. Tests passed: 0. New behavior implemented: 0.**
  No timeout/retry occurred. No owned runtime fixture was created.

Planned command after the interface is resolved (not executed):

```text
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p test_workflow_*.py -v
P -B scripts/run.py --idle 120 --max 900 -- P -B -m unittest discover -s scripts/tests -p test_evidence.py -v
```

Pass the discovery pattern as one literal argv item, not a shell-expanded glob.
Require positive inventory and all scenario assertions in the accepted C1 matrix.

## Input proof manifest (SHA-256)

| Path | Hash |
|---|---|
| `.ai/workflow-reliability/design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |
| `.ai/workflow-reliability/design.html` | `44d254d978c22a0be07313112295fc87ee34eb5843f3035e5ba8b52e1f3776e8` |
| `.ai/workflow-reliability/continuation-plan.html` | `c1dc967cd567071fd23e71871ee3349610fdd65edb6037ea1d79d4ff33a85435` |
| `.ai/workflow-reliability/evidence/continuation-plan-review.md` | `ea5177e329ae2a2f944a9b598a7cff6401feb314cdabe26002cb51e221b57159` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/tests/helpers.py` | `2694cd24dd07b1a6e3ceff7ac2addb7d4fc8bc40ee197f6d3c4206d281bf2068` |

These are inspected inputs, not an implementation acceptance manifest.
No contract deviation was implemented. The proposed materialization boundary
requires parent review; all C1 runtime acceptance criteria remain unverified.

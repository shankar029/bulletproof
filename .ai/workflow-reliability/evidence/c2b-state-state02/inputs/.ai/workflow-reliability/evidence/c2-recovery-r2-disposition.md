# C2 final design revision — dispositions and bounded handoff

**Proposed r2, design only.** Parent accepted all four independent findings and
the actual positive-recovery blocker. This revision implements that direction
in the design artifacts; it is not the independent review of itself, final
adoption, implementation, human approval or a quality pass.

## Preserved history

Before editing the current files, copied the exact r1 bytes with exclusive
destination creation and verified both SHA-256 values:

| Additive archive | Exact r1 SHA-256 |
|---|---|
| `c2-recovery-r1-contract.json` | `06b940ad95641c7a75f537871bda10b1bb9980b08a2ce8edc1e4fdf2572e52e5` |
| `c2-recovery-r1-design.html` | `319b7963dce63653c77e036050cbf128629dc7729ddbb05470620a8a15cfeaec` |

Both archives are in this evidence directory. The archived HTML intentionally
retains its original relative links; changing them would violate exact
preservation. Current HTML is the navigation entry point. Original designer
notes, independent review, platform research and historical design/plan remain
unchanged. Shared state/report/traceability are parent-owned.

## F1–F4, individually disposed

| Finding | Selected disposition | Resulting boundary |
|---|---|---|
| F1: unavailable pre-admission positive prerequisite | **Accepted; recovery production BLOCKED.** Withdraw C2R-D-first implementation, v2 ownership, recovery observations/facts/qualifier and gate predicate. | Named partial slice **C2b-ordinary-v1** targets status/next/record/close/adopt only after review. No recover subparser or always-blocked production placeholder. Original sixth-verb requirement remains open. |
| F2: migration retry not executable | **Accepted; live migration deferred.** No v1 upgrade, ledger archive/mixed-prefix or version changes. | Ordinary initial/revised adopt has explicit input conventions, shared prospective validator, publication order and exhaustive finite retry table. No normal-load precondition before initial/partial adopt. |
| F3: unknown-spawn contradiction | **Accepted.** All currently unsupported unknown-spawn recovery stays blocked. | Future complete-environment-reset exception is only a deferred constraint with qualified pre-admission bindings and inactive pending-launch authority, not an implemented escape. |
| F4: absent reviewer timestamp | **Accepted.** Remove review wall-clock assertions. | Exact metadata/report bytes must resolve before acceptance append; ledger sequence binds acceptance. Platform lifetime temporal qualification remains future mandatory work. |

The complete independent review and complete platform feasibility report were
read. The latter found zero `docker`/`docker.exe` command-resolution matches,
did not contact a daemon or mutate an environment, and found no canonical
workflow/ledger files in the three immediate root `.ai` directories. This is
bounded local evidence, not a machine-wide inventory or proof that no processes
exist. No other platform was searched in this role.

## Exact implementation boundary

Preserve original v1 Event/Ledger/Receipt/CurrentDesign/WorkflowContract and
materialized receipt/input shapes. Gate graph, prefix caches, successful/failed/
no-spawn completion policy, handoffs and eight-field C2a runner stay unchanged.
No durable owner is encoded in reason, receipt references or a second tracker.
The existing admission/intent still blocks later dispatch when completion is
unknown, even if lexical cleanup removes the lock. No process uncertainty is
resolved by metadata publication.

There are **two exact read-only C1 interface changes for the adoption boundary**:

`workflow_state.validate_design_binding(root, contract, design, ledger) -> dict`

Extract the validation body of `_load_design` into this explicit-input,
read-only helper, retaining every current check; `_load_design` reads the live
pointer then delegates. Normal loading and existing positional bind calls keep
their behavior; only the paired optional keywords described below extend binding.
The helper also validates contract/ledger schema and slug consistency.

`bind_inputs(root, contract, target, *, design=None, ledger=None) -> ResolvedInputs`

Its original three-positional-argument path stays unchanged. Explicit values
must be supplied together, must pass the shared validator, and then use the
existing dependency/snapshot loop. During A1/A2 retry, adopt can bind the exact
old triple and call the unchanged pure gate for lifetime preflight despite the
inconsistent live pointer. No copied lifetime predicate, synthetic snapshot,
private evaluator with missing inputs or filtered dispatch ledger is used.
Only adopt may use this mode; ordinary verbs use the normal live loader.

FACT: `scripts\workflow_state.py:760-804` currently reads the live pointer before
validating it. `load_workspace:877-889` and `bind_inputs:974-993` depend on this
precondition. There is no existing public prospective-design validation entry.
Calling the normal loader before bootstrap or a partially published retry
would reproduce F2. Copying its checks into CLI would create duplicate policy.
These seams are explicitly proposed, not hidden within a claim that all five
operations fit frozen interfaces unchanged. Parent/reviewer must authorize
them; otherwise **ordinary adopt is BLOCKED at this boundary**.

FACT: `append_event:996-1028` validates an existing ledger and expected sequence
without requiring live current-design loading. It can append a prospective
validated ordinary adopted event after explicit empty-ledger initialization.
`validate_event/validate_ledger:631-725` and `validate_design:737-748` already
validate the required v1 record shapes.

FACT: `tests\workflow_fixtures.py:111-144` writes workflow and pointer before the
event. This supplies synthetic shape prior art, not production retry evidence.
R2 deliberately specifies event-first publication and final normal loading.

## Adopt-only finite protocol

Exact details, fields and checks are in `..\c2-recovery-contract.json`,
`adopt_contract`. No new CLI flags or persistent record schema.

- Existing retained `REV.html` and normative `REV.json` remain mandatory.
  Immutable `REV.workflow.json` and `REV.current-design.json` stage the ordinary
  existing-schema documents. `--review` is the existing DesignReview metadata
  value matching the candidate, referring to the unchanged independent report.
- Before a revised append, retain the exact old workflow/pointer inputs by
  revision. These are ordinary design history, not copied runtime ledgers or
  a new mutable transaction journal. Existing different/partial files conflict.
- Initial absent authority may initialize only a strict empty v1 ledger.
  Missing authority cannot be treated as permission to discard known
  unresolved execution, reinitialize corruption or reset a machine.
- Validate the old basis and prospective candidate triple with the shared
  helper, then append one present-time adopted event, publish workflow, publish
  pointer and require final normal load. No admission/receipt/closure import.
- **B0/B1:** absent or exactly empty initial ledger. **A0:** coherent old state.
  **A1:** exact adopted event with old/absent pair. **A2:** candidate workflow
  with old/absent pointer. **A3:** exact already-published candidate. **X:** all
  conflicts/malformed/partial/out-of-order combinations, stop without repair.
- A1/A2 read the actual event and old prefix, never regenerate acceptance time/
  run ID or call the failing normal loader first. The historical prefix is
  solely for adoption validation, never a filtered ledger permitting dispatch.
- An orphan lock after process death blocks this table. Retry is available
  after ordinary unwinding released the owned lock, not automatic stale-lock
  recovery. No age/PID/root-exit deletion or broad cleanup.

The contract also prevents adoption from erasing runtime-referenced IDs or
converting an admitted executable action into a null-command handoff. Compatible
relevant changes still reopen proof under existing freshness rules. This keeps
adopt from becoming an alternate lifetime-resolution path.

## What can proceed, what cannot

After final independent design review and parent dispatch: the narrow shared
validator and explicit-basis binding seams with focused C1 parity tests, then the existing C2b
owner's five ordinary verbs, real admission/record/handoff/status, finite adopt
failure/retry cases, no-spawn/observer-error/guard-death denial, actual Git close
validation and operator/help documentation of the partial surface.

Help must list five implemented verbs and separately explain the deferred
original sixth requirement. Invoking unsupported `recover` is parser exit 2,
not a fabricated recover=3 test pass. Existing lifetime readiness blocks
mutation/dispatch; no stub, decoder or synthetic positive recovery is scheduled.
Q2-Q5 actual metrics remain missing proof: real positive quality closure cannot
be fabricated to make the ordinary CLI tests green.

Complete C2, actual recovery, full AC05, later host exercises, final independent
acceptance, human approval and release remain incomplete. A new directory or
worktree does not establish safe separation from an unresolved process.

This is the final planned design round. Parent renders the two-page-target
overview and returns r2 to the same independent reviewer. A remaining material
issue stops the affected path with its named blocker; no extra speculative
schema/platform/quality loop is proposed.

## Validation record

Managed Python `-B` with `PYTHONDONTWRITEBYTECODE=1`, through
`scripts\run.py --idle 30 --max 90 --label c2-recovery-r2-artifacts`, completed
exit 0. Strict duplicate-key JSON parsing, exact five-verb target, all four
dispositions, seven finite adoption-table rows and absence of r1 production
record/interface declarations were checked.

The current HTML contains 500 whitespace-delimited text words and four valid
local links/assets; no custom style or trailing whitespace was found.
Pagination/rendering is parent-owned and was not performed in this role.
Both archived r1 hashes matched exactly. Original notes/review hashes and all
seven source/contract pins from the diagnostic matched. AST re-anchored
`_load_design:760`, `bind_inputs:974`, `append_event:996` and confirmed the proposed
helper is not already implemented.

The platform research report SHA-256 observed here is
`e280fdf53affb3dc7b7817b9e9ae60e08f28d4ecadf96862fccfc3f2dd1a5af7`.
Final artifact hashes are returned in the handoff to avoid a recursive
self-digest. These checks are design validation, not independent acceptance,
implementation tests or actual recovery. No production/test/status edit,
nested agent, install, publication, additional platform discovery or actual
process recovery was performed.

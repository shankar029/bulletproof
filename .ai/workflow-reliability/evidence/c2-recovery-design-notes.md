# C2 recovery amendment — design-role notes

## Disposition and scope

PROPOSED, not independent review/adoption, implementation or human approval.
Only this file, `..\c2-recovery-contract.json` and `..\c2-recovery-design.html`
are authored. Parent may change state/report independently. No old evidence is
rewritten and no historical aggregate is represented as current proof.

The task is a bounded Phase 2 correction, not a restart of research or delivery.
Read the full state, accepted HTML design, full JSON contracts (especially
records/procedures/CLI), guard-resolution clarification, continuation overview
and complete C2 review instructions. Read the blocker, full pinned diagnostic
JSON and its reproducer, actual state/gate/evidence/runner and relevant fixtures.
CONTRIBUTING and the HTML theme instructions were read; local AGENTS.md and
.github instruction glob discovery found no matches.

## Grounding, before proposed symbols

All citations describe the inspected current files, not the old design's line
numbers. New symbols in the JSON are explicitly proposed.

| Type | Source and observed fact |
|---|---|
| FACT | `scripts\workflow_state.py:24-49`: frozen `ReceiptObservation`, `ResolvedLedger(document, receipts)` and `ResolvedInputs`; no materialized recovery map. |
| FACT | `scripts\workflow_state.py:631-657`: `validate_event` enumerates all accepted fields; no durable owner/recovery reference. `_process` at 614-628 has the existing eight fields. |
| FACT | `scripts\workflow_state.py:660-725`: `validate_ledger` enforces earlier admission, spawn/direct-exit order and terminal observation before completed. Unknown spawn cannot be translated to a real completion. |
| FACT | `scripts\workflow_state.py:760-804`: `_load_design` checks retained hashes, reviewer attribution, candidate components and exact history/adoption bindings. This amendment preserves that boundary. |
| FACT | `scripts\workflow_state.py:833-889`: `resolve_receipts` materializes missing/stale/invalid observations and `load_workspace` supplies them. Recovery resolution follows this existing pattern. |
| FACT | `scripts\workflow_state.py:996-1028`: `append_event` validates expected sequence, candidate ledger and referenced receipt bytes before atomic persistence. Recovery references require the analogous check, not reason parsing. |
| FACT | `scripts\workflow_gate.py:206-221`: `completed` rejects interrupted/recovered runs and non-spawned executable work. Keep this success policy. |
| FACT | `scripts\workflow_gate.py:399-418`: prefix evaluation reconstructs `ResolvedLedger(prefix, receipts)` with per-call evaluator reuse. The proposed recovery map must propagate without admitting later recovery into an earlier prefix. |
| FACT | `scripts\workflow_gate.py:456-467`: `unresolved` ignores recovery validation and recognizes completed for executable admissions. This is the exact correction seam. |
| FACT | `scripts\evidence.py:132-172`: atomic JSON and exclusive O_EXCL lock; finally checks identity/bytes then unlinks. Lexical cleanup is not durable recovery authority. |
| FACT | `scripts\run.py:43-79,82-212`: actual Popen remains private; Windows cleanup is best-effort taskkill; observer creation identity/evidence are null and direct exit does not prove descendant termination. |
| FACT | `scripts\tests\test_run.py:16-51,85-99`: `ProcessWitness` retains a direct Windows process handle against PID reuse, while observer assertions explicitly expect null creation identity. A live test handle cannot be persisted for later CLI recovery. |
| FACT | `scripts\tests\workflow_fixtures.py:1-5,145-184`: protocol fixtures explicitly synthesize process records. `helpers.py` uses owned Git fixtures and bounded capture; neither is a production termination authority. |
| FACT | `c2b-seam-s01.json` records labels leaving readiness blocked at seq 5, rejection of new fields and lexical lock removal after exception. It labels the evidence synthetic and does not claim real recovery/CLI proof. |
| INFERENCE | A typed persisted binding and resolved semantic observation are required to represent validated recovery without fake events or a second status authority. |
| UNKNOWN / BLOCKED | No inspected supported producer/decoder establishes durable original guard identity plus complete admitted tree/reset coverage. Positive platform qualification is not achieved by this amendment. |

## Exact choice and rationale

The JSON is normative for this proposal; HTML is the short overview.

1. **Version explicitly.** New ledger envelope and new events are v2; archive
   original v1 ledger bytes and retain the original event prefix unchanged.
   Existing receipts/design schemas and successful completion policy stay intact.
   Only locked adoption upgrades; unresolved legacy executable runs cannot gain
   authority through null defaults or historical backfill.
2. **Bind before spawn.** The admitted event owns full typed LockOwnerV2:
   token/run/workspace/guard PID and guard identity, including explicit nullable
   qualified creation evidence. An environment identity is nullable and currently
   unqualified. These records are not child ProcessObservation additions.
3. **Separate facts from labels.** The recovered event references immutable
   evidence bytes; state resolves files and semantic platform facts.
   `RecoveryObservation` resembles `ReceiptObservation`, and `ResolvedLedger`
   gains a default empty recovery map for two-positional-argument compatibility.
   Gate matches full materialized facts to exact admission, owner, prefix and
   recovered event. A missing map or `status=valid` alone cannot resolve.
4. **End only lifetime uncertainty.** No completed event, success receipt,
   red, closure or replay is synthesized. Earlier exact receipt chronology and
   per-evaluation memoization remain unchanged, including prefix containment.
5. **Do not confuse locking with lifetime.** Execution lock bytes equal the
   durable owner but their disappearance proves nothing. A short guard-only
   acquisition claim serializes stale-file replacement against other compliant
   mutators. It uses existing O_EXCL semantics; it stores no competing recovery
   state. Orphan acquisition claims stay blocked, a disclosed liveness limit,
   not a pretext for recursive stale-lock deletion.

Each component maps AC04 (real routed admission), AC05 (durable safe resume) and
AC09 (preserved behavior/proof). KISS: dataclasses and existing validators,
atomic writes and dependency direction. No framework, DSL, handwritten Git
parser, arbitrary validator callback or run.py rewrite.

Rejected shortcuts: encode authority in reason; copy lifecycle into a second
tracker; filter old admissions before gate; treat recovery label as permission;
pretend taskkill/root exit or caller boolean proves tree death; silently accept
old missing identity; change standalone lock cleanup; serialize Popen handles.

## Honest platform split, not an always-blocked success stub

The actual Windows runner and test witness supply useful direct-process facts,
but no complete supported **positive** known-tree/reset recovery can be grounded
from them. No new platform API is proposed as if it existed. The contract
specifies the decoder interface and required outputs; it does not invent a raw
OS format or implement a fake validator.

**C2R-D** is the bounded data/control amendment plus conservative unsupported
behavior and synthetic policy tests. Parent may accept it as partial functional
support and resume other C2b CLI work after independent verification/review.
**C2R-P** must first qualify one actual available producer and raw decoder for
guard-creation matching, exhaustive lifetime coverage and safe stale-lock
release. The JSON states concrete qualification tests and acceptance outputs.
Until then, live recovery returns RECOVERY_UNVERIFIED, not a passed scenario.
This is a capability limitation, not complete AC05 or release acceptance.

Alternative when no producer can qualify: preserve the original blocked
workspace and use an externally verified clean execution environment with fresh
adoption/checks. A new same-host worktree does not establish process separation.
No new reset/orphan-supervisor action is authorized. Human approval remains
unconfirmed. Self-declared context separation is not cryptographic identity;
semantic evidence validation remains mandatory even within that trust boundary.

## Reopened proof and next grouping

Reopen C1 serialization/load/append/adoption/path validation and gate
unresolved/execution/receipt/closure/prefix/cache tests on changed bytes.
Preserve legacy and exact-reference regressions, including failed/no-spawn,
metric comparator and UTC fixes. Keep historical 83+10 and 121-method reports;
none is new-byte verification. C2a runner remains frozen; affected caller
integration is rerun after adoption, not represented as unchanged by assertion.

One implementation context owns state records/resolution and gate predicate
with bounded tests, then independent verifier/reviewer. The existing following
C2b CLI owner integrates admission/recovery and real negative crash/lock/resume
cases. Platform-positive qualification is a separate prerequisite, not hidden
inside that context. Q2-Q5 missing actual metrics are independent and untouched.

Review questions for parent (no user question or claimed approval):
- Accept explicit v2 archival migration and refusal of legacy unknown-run recovery?
- Accept partial C2R-D/C2b continuation with C2R-P positive qualification open?
- Accept conservative orphan acquisition-claim blockage rather than unqualified
  automatic stale-lock cleanup?

These are selected conservative defaults in the proposal, not unresolved schema
choices for the implementer. Parent owns independent design review/adoption.

## Bounded validation

One read-only managed-Python probe, wrapped in the existing runner with idle 30 /
max 90 seconds and PYTHONDONTWRITEBYTECODE=1, compared all seven source/contract
hashes against `c2b-seam-s01.json`: **all seven matched**, exit 0.
It confirmed both shared theme assets exist and all three authorized output
paths were initially absent. No production reproduction was rerun.

Pins:

| Path | SHA-256 |
|---|---|
| `scripts\workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts\workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts\evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts\run.py` | `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e` |
| `scripts\tests\workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |
| `guard-resolution-contract.json` | `401762912eb5bd399eb16117252b497bbf9d0088a6c85505fb3ff21a681209e8` |

Final static artifact check: **PASS**, exit 0, idle 30 / max 90, no retry.
Strict JSON parsing rejected duplicate keys; all 11 proposed records parsed.
The overview has 565 whitespace-delimited text words, five existing local
links/assets and one accessible SVG diagram. No authored style/inline styling
or trailing whitespace was found. Source AST checks re-anchored the cited gate
and append seams, and all seven pinned inputs still matched.

**Print/render limitation:** the allowed managed Python has no Playwright
package. No package was installed and no unapproved external renderer was
launched. The short overview uses the existing shared print theme and targets
at most three printed pages, but actual pagination, browser errors and responsive
rendering are **not observed** in this bounded role. Parent should include the
existing renderer's print check in independent design handoff; this is not a
claim of a verified three-page print. The theme's print rules at
`.ai\assets\artifact.css:264-278` were read.

Read-only managed-Git checks confirmed HEAD
`d971634219a633cc4401fb7dcba9685e672978aa`. Status showed only the three new
authorized design artifacts plus the already disclosed/shared state/report/
traceability, eval report and c2b evidence paths; no production/test change.
No independent review, human approval, implementation test, platform experiment,
install, process kill, main-checkout access, commit or push was performed.

Final artifact SHA-256 values are returned in the handoff; this file's own hash
is kept there to avoid a recursive digest. Parent adoption and positive platform
qualification remain open.

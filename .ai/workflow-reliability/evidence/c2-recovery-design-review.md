# C2 recovery amendment — independent design review, round 1

## Verdict: REVISE

Reviewed 2026-09-17 at HEAD `d971634219a633cc4401fb7dcba9685e672978aa`.
Normative candidate: `c2-recovery-contract.json`, revision `c2-recovery-r1`.
This is an independent design-role review, not implementation acceptance,
platform qualification, a release decision, or human approval. Autonomous
continuation is authorized; human approval remains **unconfirmed**.

**Block production recovery-gate implementation on F1 below.** Adopt the
diagnosis and the narrow authority/policy separation as design directions,
but do not adopt the proposed C2R-D-first execution order as the solution
that unlocks original C2 recovery. The unsupported diagnostic is honest;
honesty alone does not make its missing positive prerequisite executable.

Only this review file is authored. No production, tests, shared state/report,
historical evidence, or other design file is changed. No nested agent, install,
test suite, process-reset experiment, OS modification, commit, or push was used.
Parent rendering/pagination is separately owned and is not a review blocker.

## Evidence, scope, and actual root cause

The complete normative JSON was read through its final closing brace, including
all records, flows, alternatives and verification requirements. The requested
1–351 view range reaches EOF; the exact hash-matching bytes contain 350
`splitlines()` entries. This is a counting distinction, not missing review.
The overview, complete designer notes, blocker, complete diagnostic and
reproducer were inspected. The diagnostic was not rerun or relabeled.
Accepted original design/contracts, resolved-view clarification and the complete
C2 continuation instructions were compared with the actual cited source seams.

**Confirmed facts:**

- `workflow_state.py:24-37,631-725` has a two-field `ResolvedLedger`, an exact
  Event field set with no owner/recovery reference, and actual lifecycle
  prerequisites for completion. No durable recovery authority fits that schema.
- `workflow_gate.py:206-221,456-467` deliberately separates successful execution
  from interruption, but unresolved executable admission currently ends only on
  `completed`. A recovery label is neither proof nor a representable resolved
  observation. The CLI owner correctly stopped rather than fabricate completion.
- `evidence.py:150-172` unlinks a lexical lock on normal exception unwinding
  after identity/byte checks. It does not retain process authority.
- `run.py:43-79,82-212` provides best-effort cleanup and actual synchronous
  lifecycle observation, with null creation identity/evidence. `ProcessWitness`
  in `test_run.py:16-51` retains an in-process direct handle; neither this handle
  nor `test_run.py:85-99` supplies durable complete-tree recovery proof.
- `workflow_fixtures.py:1-5,145-184` explicitly synthesizes protocol process
  records. Its positive records are not platform qualification.
- `load_workspace`, `bind_inputs`, `append_event`, and
  `_load_design` already establish the state I/O/trusted-resolution boundary.
  `_Evaluation` and `closure_proven_before` retain evaluation-local prefix
  memoization. The proposal correctly targets those seams, not standalone
  measurement or a new supervisor.
- `scripts\workflow.py` is absent. Current state records C1/Q1 and C2a as
  **partial local preservation**, not public release. No claim that C1 is a
  deployed compatibility surface is established here.

AC04 requires a real routed execution entry point, not a sandbox or authenticated
identity. AC05 additionally concerns artifact-only fresh-context resume and
selective reopening; resolving process uncertainty is only part of it.
AC09 requires preserved native/evaluation behavior and independent acceptance
on changed bytes. None is completed by this design review. Q2–Q5 actual metrics,
later host exercises, human acceptance and publication remain separate and open.

## Findings and required dispositions

### F1 — BLOCK: the selected order defers a prerequisite of this very seam

**Locations:** `scope.qualification_decision`;
`records.GuardIdentity`, `EnvironmentIdentity`, `QualifiedRecoveryFacts.rules`;
`interfaces[*].qualification_split`; `platform_qualification.concrete_split`;
`verification.implementation_group.C2R-D_order`; overview sections 4–5.

Both positive recovery kinds require a qualified, nonnull **pre-admission
guard creation identity**. Known-tree additionally requires nonnull admitted
child identity and complete descendant coverage; reset additionally requires
nonnull pre-admission environment identity. Current proposed admission records
null guard/environment identities, and the frozen runner records null child
creation identity. `qualify_recovery -> None` has no real supported decoder.

Consequently C2R-D cannot recover any actual admission it currently proposes
to create. This is not merely “enable an adapter later”: immutable admissions
with null identity cannot be backfilled when C2R-P eventually appears. C2R-P
also has yet to establish whether its real producer can supply the proposed
pre-launch fields and temporal/coverage obligations without changing frozen
interfaces. Implementing the entire migration/resolver/predicate now risks
another frozen-interface dead end.

**Disposition required:** move a bounded **platform feasibility/qualification
decision before production recovery state/gate implementation**. Before adopting
that implementation, name one real producer, its actual raw format and supported
range, its pre-admission identity capture seam, and the deterministic semantic
decoder contract grounded in actual documentation/output. Show that it can
supply all required facts without forbidden runner/observer changes, or explicitly
return a design blocker. The implemented decoder and an owned actual positive
must precede functional recovery acceptance; synthetic facts cannot satisfy it.
Do not assign a pretend qualification ID to an unsupported implementation.

**Judgment on the split:** durable ownership and real no-spawn/unsupported
diagnostics could be useful normal-CLI functionality under a separately narrowed
scope. Unsupported evidence must return 3, and this behavior is not deceptive.
But a generic always-unverified resolver plus synthetic positive policy tests
does **not** unblock the original accepted recovery path. Do not authorize
C2R-D's production positive-gate machinery merely as “partial functional support.”
Other genuinely independent C2b work need not wait for quality collectors, but
its dispatch boundary must explicitly exclude unqualified recovery completion;
this review does not itself authorize that implementation.

### F2 — REVISE: migration reconciliation is named, not specified

**Locations:** `migration_and_read_rules` (archive/envelope/adoption/pointer);
`interfaces` (`upgrade_ledger`, `load_workspace`, `append_event`);
actual `workflow_state._load_design:760-804`.

The proposed upgrade requires a valid old ledger/design and then introduces
archive, envelope, adoption and pointer write boundaries. The text says adopt
reconciles a crash mismatch using retained hashes/sequence, but does not give
the exact reconciliation entry path. Ordinary `_load_design` rejects pointer/
revision/history/adoption mismatch before the ordinary load can proceed.
Saying “use adopt” is not an executable rule for a retry that cannot pass load.

**Disposition required if migration is retained:** specify a finite adopt-only
reconciliation table: valid old state plus orphan archive; upgraded envelope
before new adoption; new adoption before new pointer/workflow publication;
exact already-published retry; every conflicting combination. Identify which
retained candidate/review bytes and expected sequence allow each transition,
which validation precedes writes, and how normal load remains fail-closed.
Cover partial exclusive-created archive/evidence files explicitly: mismatched
existing bytes must block, not be silently overwritten as a retry.

This is a bounded persistence specification, not a demand for a multi-file
transaction or a new journal. If the chosen supported scope does not need live
v1 upgrade, remove/defer that migration surface instead of implementing an
unspecified recovery mechanism for it.

### F3 — REVISE: express the unknown-spawn exception consistently

**Locations:** `QualifiedRecoveryFacts.rules` versus
`flows.pure_recovery_predicate` and `platform_qualification`.

One rule says “unknown spawn ... yields unverified” without qualification;
the pure predicate explicitly allows unknown spawn through a qualified complete
environment reset. These are different normative results for the same case.

**Disposition required:** unknown spawn blocks known-tree recovery. It may
resolve only through the explicitly selected, independently checked complete
environment-reset path with qualified pre-admission environment/guard binding.
Until such a path exists, it stays unverified. Preserve unknown observations;
never manufacture launch-failed, spawned, direct-exited or completed records.

### F4 — REVISE: make review chronology mechanically representable

**Locations:** `RecoveryEvidenceV2.rules` (“capture/review is newer than its
recovered event”); `RecoveryReview.fields`; `QualifiedRecoveryFacts.fields`;
original `design-contracts.json.records.FindingResult`.

Capture records have `observed_at`, but the specified RecoveryReview and
FindingResult contain no review timestamp. QualifiedRecoveryFacts also carries
no review-time fact. Therefore the proposal cannot implement a numeric
review-time comparison from its declared fields. A file mtime, operator claim
or qualification ID is not a replacement semantic clock.

**Disposition required:** specify the actual chronological guarantee. The
minimal option is unchanged reviewed bytes resolved before the append,
subject-bound references and ledger sequence for acceptance ordering, with no
unsupported claim to validate review wall-clock time. If a wall-clock rule is
needed, specify its real supported evidence/decoder and binding. Keep platform
capture/guard/lifetime temporal checks separate and mandatory; merely parsing
caller timestamps cannot establish semantic termination order.

## Per-decision disposition

| Decision | Disposition | Review rationale / boundary |
|---|---|---|
| Stop at missing durable authority rather than fake lifecycle | **ADOPT** | Exact state/gate source and pinned synthetic diagnostic substantiate the root cause. |
| Typed owner atomically in admitted, immutable recovery reference only on recovered | **ADOPT direction** | Cohesive single-ledger authority; no reason-field encoding, second tracker or receipt-ref misuse. Exact platform identity fields remain subject to F1. |
| State resolves bytes and facts; gate consumes materialized observations only | **ADOPT direction** | Matches accepted receipt resolution and dependency direction. `status=valid`, reviewer metadata or Python-constructed booleans alone must never qualify a CLI recovery. |
| C2R-D-first production recovery predicate with no qualified adapter | **BLOCK** | F1. Synthetic implication tests demonstrate protocol behavior, not a usable supported path. |
| Lifetime resolution only; no execution/red/success/closure/replay | **ADOPT** | Preserve `completed`, `_execution`, `_receipt`, single forward graph and exact earlier receipt consumption. Fresh next gets a fresh run and all ordinary due gates. |
| Exact run/token/workspace/owner/admission/basis/adoption matching | **ADOPT**, with F3/F4 revisions | Bind full owner, not PID/token alone. Captures and review bind exact subject bytes; unsupported identities/coverage remain unverified. |
| Prefix propagation and evaluation-local memo reuse | **ADOPT** | Pass recovery observations into prefix views but require recovered event and exact basis inside that prefix. Future map entries cannot backfill earlier closure. Preserve the existing counted-prefix regression; no global cache. |
| Explicit format boundary for new authority | **ADOPT** | Old strict readers should reject new records, not silently interpret missing authority. Legacy unresolved admissions cannot acquire fabricated ownership. |
| Mandatory full v1 archive + mixed-prefix live migration now | **REVISE / right-size** | Byte preservation is good, but local C1 preservation alone does not justify mandatory deployed-reader migration complexity. See below and F2. |
| Short second acquisition/recovery claim | **ADOPT conditionally for qualified stale release** | A cooperative exclusion mechanism, not proof or a tracker. Preserve `evidence.py`. No claim of atomic compare-and-unlink against hostile writers. |
| Orphan acquisition claim remains blocked | **ADOPT limitation** | Safe and explicitly limited, but a process crash while recover holds it prevents normal retry. It is not universal crash recovery. Disclose before admission, test it, and never auto-steal by age/PID. |
| Six verbs/options and eight-field observer; run/evidence unchanged | **ADOPT constraint** | No new caller override, fake child fact or platform capability flag. Qualification must demonstrate a route consistent with these constraints or stop for a narrowly identified amendment. |
| Synthetic protocol tests plus real negative scenarios | **ADOPT as necessary, not sufficient** | Real qualified positive remains required for recovery acceptance; Q2–Q5 and host/final AC proof remain unavailable/open. |

### Versioning and preservation judgment

Explicitly distinguishing new authority from old Event shapes is sensible.
Exact archive bytes plus equal unchanged prefix would be safe if correctly
implemented; their hash, size, slug, event count and entire ordered prefix must
be checked at all trusted load/bind/append boundaries. Never accept an unmarked
new legacy suffix, downgrade, retrofitted owner, or imported historical success.
Old handoffs must keep their original receipt semantics.

However, an archive, mixed-event validator, upgrade write protocol and
reconciliation logic are substantial cost for unpublished internal C1 state.
Round 2 should identify the actual continuing v1 workspaces that need live
upgrade. If none require it, prefer explicit read-only v1 history plus fresh v2
adoption with fresh proof, leaving migration deferred. This is **not** permission
to abandon an unresolved child by starting another directory: a new worktree is
not a clean execution environment. Any continuation around an unresolved old
workspace still requires externally established process/environment separation.
If continuity of real completed/handoff history is required, retain the exact
archive/prefix design and fully specify F2 rather than blindly dropping it.

### Crash, retry and concurrency judgment

The acquisition claim is a reasonable small cooperative answer to stale-lock
replacement between check and unlink. All acquiring mutators must use the same
order. Recovery may not append or release a lock while the exact original guard
is active; null guard identity cannot pass. Revalidate matching owner bytes and
physical identity under the claim immediately before stale release. Normal
execution-lock finalization must never erase a replacement owner's lock.

The retry rules must be exercised as distinct branches, not one generic
current-basis validation:

1. Fresh recovery: ledger exactly equals evidence basis.
2. Partial append after an unwound failure: exact basis plus only the matching
   interrupted event; validate the original basis, append only recovered.
3. Already accepted recovery: locate and revalidate the historical recovered
   reference/basis, then finish only matching stale-lock cleanup; unrelated
   later adoption does not retroactively invalidate proven death.
4. Different evidence, intervening event in a partial retry, missing/tampered
   proof or uncertain lock identity: no overwrite, unlink or spawn.
5. Actual guard death while the acquisition claim is held: orphan claim blocks
   every retry before the branches above. No automatic repair is specified.

The proposal acknowledges branch 5; it is not an undisclosed safety bug. It does
mean “crash at each write boundary” cannot be advertised as successful recovery
at each boundary. Tests must distinguish exception unwinding from process death,
and orphan blobs/claims from accepted ledger evidence. State clearly which paths
remain permanently blocked absent a separately qualified maintenance route.
Do not expand this amendment into recursive lock recovery or universal supervision.

## Concrete bounded next action, before the last design round

1. **One qualification research slice, not production implementation:** select
   one actually available host/platform evidence producer, preferably one whose
   existing execution-environment identity/lifecycle can cover the unknown-spawn
   interval without modifying the frozen runner. Inspect its actual interface,
   official documentation and available raw output. This is a candidate choice,
   not a claim such a producer or reset API exists on this Windows host.
2. Produce a small capability table mapping pre-admission guard identity,
   pre-admission child/environment identity, guard inactivity, complete lifetime
   coverage, escaped/reparented descendants, PID reuse and temporal order to
   actual supported evidence and deterministic decoder checks. A direct-process
   witness or present process listing is insufficient. Explicitly mark any gap.
3. Return **one** outcome: a supported concrete decoder/capture contract with
   scoped positive/negative qualification recipe; or a named unsupported
   prerequisite with evidence and no proposed production recovery implementation.
   No installs, destructive reset or broad supervisor redesign is implied by
   this research recommendation. Subsequent owned experiments need their own
   bounded authorization and cleanup plan.
4. Designer's final round 2 disposes F1–F4 together, selects/defer migration
   explicitly, and preserves the accepted invariants. Do not spend that last
   round merely renaming the always-blocked slice. If no supported producer can
   meet the constraints, stop recovery implementation with the explicit blocker;
   parent may separately narrow ordinary CLI work without claiming C2 recovery.

## Validation and source pins

Read-only managed Python was invoked through the existing runner:

`P -B scripts\run.py --idle 30 --max 90 --label c2-recovery-review-pins -- P -B -c <read-only hash/HEAD assertions>`

`P` was
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`,
with `PYTHONDONTWRITEBYTECODE=1`. Exit **0**: all three supplied candidate hashes
matched, all seven diagnostic source/contract pins matched both diagnostic
before/after maps, HEAD matched, and CLI absence was confirmed. A second bounded
read-only invocation pinned the two inspected workflow regression test files,
exit **0**. These are source checks, not feature-test or platform-positive passes.

Paths below are repository-relative; hashes are SHA-256 of raw bytes.
Mutable parent state/report/render outputs are deliberately not review pins.

| Source | SHA-256 |
|---|---|
| `.ai\workflow-reliability\c2-recovery-contract.json` | `06b940ad95641c7a75f537871bda10b1bb9980b08a2ce8edc1e4fdf2572e52e5` |
| `.ai\workflow-reliability\c2-recovery-design.html` | `319b7963dce63653c77e036050cbf128629dc7729ddbb05470620a8a15cfeaec` |
| `.ai\workflow-reliability\evidence\c2-recovery-design-notes.md` | `0aec7f8c9a895094b629ac7eb28e1de7a7620c94d360d226d7245012a6a1f7cf` |
| `.ai\workflow-reliability\evidence\c2b-interface-blocker.md` | `ed4c0e3e5599240eb6261941ef9275c572c6087bab1a95eeb8c729bfa4ca6f4e` |
| `.ai\workflow-reliability\evidence\c2b-seam-s01.json` | `35e9cf6ff3da67e6ba798c8effb1941635d9d5cb3a4aeade7af204f243914ef6` |
| `.ai\workflow-reliability\evidence\c2b-seam-probe.py` | `98c97d8f27c5e05de22a2695bc4bb811fa65f5bdb6818c4e773d9795400e996e` |
| `.ai\workflow-reliability\design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |
| `.ai\workflow-reliability\design.html` | `44d254d978c22a0be07313112295fc87ee34eb5843f3035e5ba8b52e1f3776e8` |
| `.ai\workflow-reliability\guard-resolution-contract.json` | `401762912eb5bd399eb16117252b497bbf9d0088a6c85505fb3ff21a681209e8` |
| `.ai\workflow-reliability\continuation-plan.html` | `c1dc967cd567071fd23e71871ee3349610fdd65edb6037ea1d79d4ff33a85435` |
| `.ai\workflow-reliability\evidence\continuation-plan-review.md` | `ea5177e329ae2a2f944a9b598a7cff6401feb314cdabe26002cb51e221b57159` |
| `scripts\workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts\workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts\evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts\run.py` | `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e` |
| `scripts\tests\workflow_fixtures.py` | `9902d319a37436449a1a8fb47c10ca7ec15d82c5bdea331d3ba4c23bf03dcabf` |
| `scripts\tests\test_run.py` | `92bedd163977112eff3efd3cfbad5fc9aaa9fe9a2318dd2aad832903914b85e5` |
| `scripts\tests\test_workflow_state.py` | `7b259c0f2e6c4e31a5c614769995df97f999fe86ed44b0e1351e3ee7a2d72466` |
| `scripts\tests\test_workflow_gate.py` | `af23bb4d96ea9da28f15291dc2c4cbb8e0e9272a40b27140e28efc89f3993636` |

**Stop:** review artifact only. No implementation or release claim follows.

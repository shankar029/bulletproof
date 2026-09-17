# C2 final design re-review: ordinary five-verb slice

## APPROVE — C2b-ordinary-v1 design only

Final planned design round 2, reviewed 2026-09-17 at HEAD
`d971634219a633cc4401fb7dcba9685e672978aa`.
Approval applies to normative contract SHA-256
`80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d`,
with the existing-schema construction clarification below. No remaining material
blocker was identified for that narrowed design. This is not approval of recovery,
complete C2, implementation, platform qualification, quality closure or release.
Autonomous continuation is authorized; human approval remains **unconfirmed**.

Parent may authorize the two specified read-only state seams and their focused
proof, then ordinary CLI integration after independent acceptance. This review
does not dispatch or implement them. Any further material core-interface need
stops the affected implementation with its exact blocker; no third broad design
round or alternative-platform search is requested.

Only this new review file is written. The original review, notes and r1 archives
remain unchanged. No code/test/shared-state edit, test execution, new agent,
installation, process experiment, OS change, commit or push occurred.

## F1–F4 dispositions

| Finding | Final disposition | Exact consequence |
|---|---|---|
| F1: no qualified pre-admission identity/lifetime producer | **Accepted and closed as a scope correction; capability still BLOCKED.** | Remove C2R-D, v2 owner/recovery records, qualifier, recovery predicate and recover handler from this implementation. No synthetic positive or generic always-unverified decoder. The original sixth requirement remains incomplete. |
| F2: unspecified migration reconciliation | **Accepted; migration DEFERRED. Ordinary adoption design approved.** | No live v1 upgrade/archive/mixed-prefix machinery. Initial and revised v1 publication use the explicit B0/B1/A0/A1/A2/A3/X table, not a permissive normal loader or runtime repair journal. |
| F3: conflicting unknown-spawn exception | **Accepted and closed in the current scope.** | No current recovery exception exists. Unknown spawn stays unresolved. A future complete-environment-reset path remains a prerequisite-bound constraint, not an executable escape. |
| F4: unrepresentable reviewer clock | **Accepted and closed.** | Resolve exact metadata/report/disposition/authorization bytes before append. Acceptance sequence establishes order; no mtime, invented review timestamp or platform-termination inference. |

The platform report supports only bounded command-resolution absence for
`docker`/`docker.exe`, no actual producer/decoder qualification, and no canonical
continuing v1 ledgers in the inspected immediate root `.ai` directories. It
does not prove global Docker absence, daemon unreachability, process death or a
clean environment. No new search or public-documentation claim is needed here.
Deferring unused migration complexity is justified by these limits and the
unpublished/local-preservation status of C1; it is not permission to discard
existing history or reinitialize an unresolved workspace.

Unlike r1's proposed positive-gate scaffolding, this ordinary scope has useful
reachable behavior: bootstrap/adopt a real reviewed contract, derive status,
admit registered work or handoffs, accept actual matching proof, and deny unsafe
dispatch/closure. Positive quality closure is not required to demonstrate those
functions and must not be fabricated. Unsupported `recover` is parser exit 2,
not a passed negative recovery test or recovery implementation.

## Frozen-source checks and exact seam authorization

Inspected actual source, rather than assuming the proposed APIs exist:

- `workflow_state.validate_binding:275-278` requires exactly six fields,
  including `binding_mode="guarded"`. `validate_snapshot:281-282` requires
  source plus contract. `validate_source:267-272` checks the canonical
  scope/files digest.
- `evidence.source_snapshot:40-115` obtains actual file bytes/modes and
  returns the complete existing SourceSnapshot, including
  `binding_mode="standalone-source"`, nullable base/head and scope hash.
- `validate_event:631-657` permits ordinary adopted fields and no process
  record; `validate_ledger:660-725` validates sequence and unique adoption/run
  IDs without loading a live pointer. An adopted event is not an admission.
- `_load_design:760-804` currently reads the live pointer and then checks
  explicit design/contract/history/adoption bindings. Its validation body
  does not inherently need that pointer to have been published.
- `bind_inputs:974-993` currently loads the live ledger/pointer before the
  dependency/snapshot loop. `append_event:996-1028` needs an existing valid
  ledger and expected sequence, but does not call `_load_design`.
- `workflow_gate.unresolved:456-467` classifies an admitted run using the
  contract's current action definition. `evaluate:489-553` reports unresolved
  executable lifetime globally. Therefore old-basis preflight and the
  no-reclassification rule are necessary, not optional precautions.
- `workflow_fixtures.adopt:112-143` supplies existing-shape construction
  prior art, including the required binding-mode literal, but its
  pointer-before-event writes are not the approved production protocol.

| Decision | Scoped authorization |
|---|---|
| `validate_design_binding(root, contract, design, ledger)` | **APPROVE.** Extract and reuse all existing `_load_design` checks; additionally validate explicit contract/ledger shape and slug agreement. Read-only, no gate invocation, write, fallback or relaxed approval/history rule. |
| `_load_design` delegation | **APPROVE only as that extraction.** It still reads the canonical live pointer and remains fail-closed. No prospective candidate substitution in ordinary loading. |
| `bind_inputs(..., *, design=None, ledger=None)` | **APPROVE.** Both explicit values or neither; reject one alone. Validate the triple, reuse the same dependency closure and `_snapshot_for` loop. Existing positional behavior stays unchanged. |
| Explicit old-basis materialization | **APPROVE only for adopt retry validation.** A1/A2 may evaluate the exact old triple/prefix. It is never a dispatch ledger, never passed to ordinary next/record/close, and never written over the real ledger. |
| Core expansion | **NOT AUTHORIZED.** No v1 schema change, new recovery view, gate/prefix change, runner/evidence change, policy duplication or generic repair API. Stop if implementation requires another seam. |
| Five ordinary verbs and existing options | **APPROVE for the next independently accepted integration slice.** Preserve the original five verbs' options, registered-command boundary and structured outcomes; explicitly document the blocked sixth. |

### Required existing-schema construction clarification (not a new seam)

The r2 `event_construction` prose lists five contract-binding fields and does
not repeat `binding_mode`. Its repeated requirement to preserve and validate
the existing GuardSnapshot means the approved construction is exactly:

```text
Event.inputs.source = source_snapshot(root, actual_named_candidate_scope)
Event.inputs.contract = {
    binding_mode: "guarded",
    adopted_contract_sha256: canonical_hash(W1),
    components: P1.components,
    actions: {},
    checks: {},
    claims: {}
}
```

Omitting `binding_mode` would be rejected by the frozen validator and is **not**
approved. Supplying that existing literal requires no new API, placeholder
proof or schema decision, so this inherited-field omission is not a material
third-round blocker. The empty action/check/claim maps are adoption provenance
only; they do not assert execution, test success or closure. All hashes must
come from actual candidate bytes/values, and the source snapshot must remain
the actual helper output, not a manually fabricated hash-shaped record.

Do not call `bind_inputs(W1, ...)` to invent E's adoption snapshot: validating
that candidate before E exists would reintroduce the cycle. Construct the
design-only snapshot directly from the immutable named files, construct E,
then validate the prospective triple. Existing code already distinguishes
this adoption construction from ordinary action input binding.

## Bootstrap, publication and retry executability

The data dependency is acyclic:

1. Actual retained HTML, normative JSON and W1 exist; independent metadata
   binds their hashes. P1 contains that metadata and retained history, not E
   or E's hash. The metadata/report/authorization are real inputs.
2. Snapshot those named immutable files, including W1/P1 and review/history
   inputs. Use real adopter identity, fresh run ID and actual UTC acceptance
   time to construct E; prospective L1 is actual L0 plus that one proposed
   adopted event. Neither E nor L1 is included as a self-hashing input.
3. Validate `(W1,P1,L1)` explicitly. For an initial design its one adopted
   event matches `[P1.revision]`; for revision it matches history plus current.
   The current validator checks E's retained HTML/normative file hashes and
   final contract/component binding. CLI additionally verifies all staged
   source/review/old-pair hashes specified by the adoption contract.
4. Initialize only an absent empty-schema ledger when B0 permits it; recheck
   candidate bytes and basis under the lock, append through `append_event`,
   then publish W1 and P1 in that order. Final normal load must succeed before
   reporting success.

Prospective validation is validation of a proposed present-time adoption,
not a fabricated past event or review. No temporary live pointer, synthetic
workflow fixture, false receipt or placeholder hash is required. A changed
candidate or basis invalidates the proposal before append.

| Disk state | Approved operation / stopping boundary |
|---|---|
| B0: no authority or ledger | Validate complete initial inputs and prospective triple; exclusively create empty v1 ledger, then append/publish. Known contradictory prior authority blocks bootstrap. |
| B1: absent W/P, exact empty ledger | Same initial checks; append once. Malformed or partial initialization is not an empty basis. |
| A0: coherent old triple | Normal old validation and lifetime preflight, exact compatible history/IDs, retain old inputs exclusively, validate prospective triple, append/publish. |
| A1: final E, old/absent W/P | Raw-read actual E and exact preceding basis; validate old and prospective inputs; publish W1/P1 without regenerating E. |
| A2: final E and W1, old/absent P | Same exact binding checks, publish only P1. Do not overwrite W1 or append again. |
| A3: coherent already-published candidate | Exact candidate/review/E acknowledgment, no writes. It is not readiness or permission to dispatch. A lifetime blocker is not cleared. |
| X: anything else | Malformed input 2 or publication conflict 3; no guessed state, overwrite, rollback, duplicate event or lifecycle repair. |

No missing multi-file atomicity claim remains: partial publication deliberately
blocks ordinary loading. The table is an adopt-only completion path after
unwound failures. Actual process death leaving the lexical lock blocks even
retry; partial immutable files also block. These are explicitly accepted
liveness limitations, not universal recovery. No second acquisition claim is
needed because this slice never removes a stale lock.

For revised A1/A2, resolve receipts for actual L0 plus required claim receipt
IDs, and bind the validated old contract/design/prefix through the new paired
mode. Evaluate the ship target and reject `RECOVERY_UNVERIFIED` without demanding
complete ship proof. A binding/materialization error must stop, not become an
empty snapshot or “no lifetime blocker” default. Changed current files may make
ordinary proof stale; stale quality is not itself fabricated lifetime resolution.

Before a revised append, enforce the specified preservation of runtime-referenced
action/check/increment IDs and executable-versus-handoff classification for
admitted actions. This is an explicit CLI adoption compatibility check, **not
an existing guarantee supplied by `validate_ledger` or `_load_design`**. The
old-contract gate check must precede candidate publication; checking only W1
would allow an unresolved executable admission to be reinterpreted as a handoff.
Retaining/checking the old basis is not filtering the persisted ledger.

## Preserved boundaries and required implementation evidence

AC04 approval is for a partial real routed boundary only. One ordinary lexical
lock covers mutating operations; admission and intent precede the actual runner.
Use only registered argv/cwd/env, exact actual observer fields and appropriate
structured exit classification. Unknown observer/capture/cleanup state cannot
produce a completed event. The absence of a mutex file does not remove an
unresolved admission. No caller flag, reason text, receipt reference, token age
or root/direct exit supplies missing process proof.

AC05 approval is for ordinary artifact resume/metadata publication design.
Unaffected receipts and old handoffs retain their meaning, relevant changes
reopen proof, and exact earlier receipt references remain authoritative.
Recovery is still unavailable. Neither a new worktree nor deferred adapters
can retroactively give unqualified v1 runs durable process identity.

AC09 approval preserves v1 strictness, graph/prefix memo behavior, runner/evidence
bytes and existing success/failure policy. Later close must validate actual Git
HEAD/commit/scoped source, not just syntax; missing mandatory metrics or
independent proof must block. Review/context declarations are attribution within
the accepted trust scope, not authenticated identity or termination evidence.

The contract's required implementation evidence is appropriate: live/prospective
validator parity; paired-keyword rejection and identical scope materialization;
real bootstrap and each publication failure/retry state; immutable-byte and
history/review mismatch rejection; unresolved old-run deletion/reclassification
denial; actual no-spawn and observer-failure scenarios; real non-quality record
acceptance; actual Git mismatch and missing-quality close denial; unchanged
chronology/prefix regressions. These are future obligations, not tests run here.
Fresh verification and separate review must precede dependent integration.

Q2 tool qualification is outside this review's source boundary. Q2–Q5 actual
metrics, original sixth verb, full C2/AC05, later host exercises, human approval
and release remain open. No positive recovery/quality result is authorized to
make a test pair complete.

## Freshness and evidence pins

The complete r2 normative JSON, current HTML, complete disposition and platform
report were read. Relevant frozen source was re-read at the seams above; the
r1 accepted-source review remains the bounded context, not a renewed broad audit.
Read-only managed Python `-B` was run through
`scripts\run.py --idle 30 --max 90`, with `PYTHONDONTWRITEBYTECODE=1`, using
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`.

The first exact-pin check stopped on **overview hash drift**. Subsequent
read-only inspection confirmed normative JSON and disposition match the
requested hashes, all 17 unchanged r1 inputs match, archives and original review
match, and HEAD is unchanged. `scripts\workflow.py` remains absent.
The current overview was re-read in full; its visible design content agrees
with the narrowed normative contract.

Requested HTML hash was
`bc71c02581ef6c5a8d18f51786c3aae0907eeffc106c57c1fda88f24ef90149d`;
observed raw bytes hash to
`a290690f4c16755d47a21930dd40fc6f01df9789ec2b2691f6b0ea773803750a`.
At the initial review, the cause of that drift was not inferred. The parent's
subsequent presentation-only explanation is now reconciled below. Parent must
bind the actual final overview bytes in any adoption record; no old overview
hash may be reused. Mutable state/report outputs remain outside this review.

### Parent presentation delta reconciled

Parent identified the added three-box publication diagram. A bounded read-only
raw-byte check independently confirmed that removing exactly the single
`<figure>...</figure>` block, including its trailing newline, from the current
HTML reproduces the originally requested
`bc71c02581ef6c5a8d18f51786c3aae0907eeffc106c57c1fda88f24ef90149d`
hash. Thus the entire byte delta is that figure insertion, not a normative
change. Its adopted-event -> workflow.json -> current-design.json sequence and
caption agree with the already-approved publication prose and contract.

**APPROVE remains unchanged and the final overview at `a290690f...803750a`
is reconciled for that same narrowed scope.** All 24 existing review pins,
including normative JSON, production/test sources and exact r1 archives,
still match. No design round or implementation scope is reopened.

The inspected parent-owned `evidence\c2-recovery-design-rendering.json`
(SHA-256 `0bffd4688fdf2d464b9536065b53a455d606c48a72274f1a52ba37fe3b643042`)
binds this exact HTML hash and records two pages, one nonzero-sized SVG, empty
browser errors and empty console messages. This is reconciled parent render
evidence, not an independently rerun browser test. The separately retained
`c2-recovery-r1-rendering.json` identifies the original r1 HTML hash, and
`c2-recovery-r1-design.pdf` exists. These historical outputs were not rewritten
or relabeled as r2 proof. No claim of an independently verified byte-for-byte
PDF archival copy is made without a prior PDF pin.

All values below are raw-byte SHA-256; paths are repository-relative.

| Path | SHA-256 |
|---|---|
| `.ai\workflow-reliability\c2-recovery-contract.json` | `80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d` |
| `.ai\workflow-reliability\c2-recovery-design.html` | `a290690f4c16755d47a21930dd40fc6f01df9789ec2b2691f6b0ea773803750a` |
| `.ai\workflow-reliability\evidence\c2-recovery-r2-disposition.md` | `9e00d2b74e3f92e9a8699df2ecd1ec7e80a71b942c8afa1b972c01a26491aca0` |
| `.ai\workflow-reliability\evidence\c2-recovery-platform-research.md` | `e280fdf53affb3dc7b7817b9e9ae60e08f28d4ecadf96862fccfc3f2dd1a5af7` |
| `.ai\workflow-reliability\evidence\c2-recovery-r1-contract.json` | `06b940ad95641c7a75f537871bda10b1bb9980b08a2ce8edc1e4fdf2572e52e5` |
| `.ai\workflow-reliability\evidence\c2-recovery-r1-design.html` | `319b7963dce63653c77e036050cbf128629dc7729ddbb05470620a8a15cfeaec` |
| `.ai\workflow-reliability\evidence\c2-recovery-design-review.md` | `fe3eaab311e1ce6ff8a2b881c5118aed17751a6efd0d4c4038559c5854976fd8` |
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

**Stop:** final narrowed design review complete; recovery remains blocked.

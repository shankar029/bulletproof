# Q2 JS execution / symbol transport — second focused review

## APPROVE

**2026-09-17. Review pass 2 of amendment revision 3. Parent owns disposition.**

JS-R1, JS-R2 and JS-R3 are **closed at the design level**. The requested
six-suffix inventory caution is also resolved. No remaining blocking design
finding was identified. **The parent may release the minimal implementation
against these frozen revision-3 bytes.** This is not approval of an implementation,
new qualification evidence, complete Q2, or a release.

FACT: I read the entire revised 487-line contract and the entire revised
rationale, not just the owner's disposition. I compared the contract structure
with the exact reviewed revision-2 copy, checked unchanged-body consistency,
and rechecked the actual inventory/composition/rederivation source seams.
The first review is preserved, not overwritten.

## Frozen inputs

Paths in this table are relative to `.ai/workflow-reliability/`.

| Input | SHA-256 |
| --- | --- |
| `evidence/q2-js-execution-amendment.json` — revision 3, 74,941 bytes | `887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e` |
| `evidence/q2-js-execution-rationale.md` — 6,434 bytes | `82680496ec4466922e6273d53df5d6ef354ad1045d0fdf86b5e5be9191d1cbd9` |
| `evidence/q2-js-execution-amendment-r2.json` — 52,890 bytes | `cd69b23bd22c08fe6884fcd5fbb5570d4dd0e5f4551b2f161ce4d0c0da61333a` |
| `evidence/q2-js-execution-rationale-r2.md` — 6,098 bytes | `d79ec098f6d332e204ed87946d7104df6bd65c2c82f58e309cefa5b504f8e130` |
| `evidence/q2-js-execution-review.md` — first review | `222c6c2f85b40e25b1321726dc5a5d6b58261828e8beed479d5d0b2e9cd808d6` |
| `measurement-enablement-contracts.json` | `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12` |
| `evidence/q2-tool-input-root-amendment.json` | `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1` |

FACT: HEAD remains `ce7c07eb4bec9239db4d45cdf9bc83c88a43a16c`.
The actual raw hashes of `scripts/measure.py`, `measure_graph.py`, `probe.py`,
`evidence.py` and `run.py` match all five pins in the first review. Their scoped
Git diff against `dadce66ff7d9a7494db0af5f8124009d7b132cb9` remains empty.
The current bodies therefore remain the reviewed preimplementation runtime,
not an implementation of the new interfaces.

## Exact finding dispositions

### JS-R1 — CLOSED: actual base discovery precedes reservations

FACT: `paths_and_manifests.reservation_set`, `production_order[0..2]` and
`bindings_and_comparison.input_admission` now agree:

1. Materialize the immutable base through the existing qualified owner.
2. Discover actual base and current-head paths and their revision-specific
   metadata/entrypoint candidates.
3. Check collisions and reserve the exact union before the broad head snapshot
   and observed-head copy.
4. Reconcile immutable inventories and admitted metadata afterward; drift aborts
   rather than extending exclusions.

This preserves the working ordering in `probe._execute_configured`
(`scripts/probe.py:525–551`) and the filesystem contract of
`measure.code_files(root)` / `_walk(root)` (`measure.py:215–278`).
Deleted/base-only paths are no longer dependent on nonexistent base discovery
or a head-only proxy. Both source metadata and qualification/archive collisions
are explicitly covered. No second Git-tree frontend or baseline-policy change
is introduced. `JS-LIFE-01` now specifies the relevant base-only and metadata
proof. **No residual design correction is required for this finding.**

### JS-R2 — CLOSED: purpose is a real private execution argument

FACT: `mode_and_interfaces.measure_owned`, production/validation ordering,
`JSRequestV1.invariants` and `bindings_and_comparison.run_specific` consistently
separate:

- Public proposed `execute_js(context, inventory, config)` supplies compiled
  `produce` to private `_execute_js(context, inventory, config, *, purpose)`.
- Existing `validate_observations(context, base, head, config, policy,
  artifacts, observations)` supplies compiled `validate` directly to that core.

The private core checks the actual argument before launch and after capture;
comparison independently requires the original/replay purpose pair. Replay
does not call the production wrapper. No Context field, temporary-root spelling,
environment option, callback or caller-supplied replay Context selects purpose.
`JS-LIFE-02` and `JS-OWN-01` include rehashed purpose-swap rejection.
**No residual design correction is required for this finding.**

### JS-R3 — CLOSED: one finite failed-output policy governs every consumer

FACT: the added `js_output_policy` supplies a single pure dispatch with three
actions and six scenario rows. Corresponding clauses in graph/raw/receipt
projection, produced-manifest reconstruction, archive publication,
`JSCommandV1`, `JSResultV1`, `JSSymbolEvidenceV1.ownership`, validation order
and failure behavior now defer to it rather than unconditional semantic decoding.

| Actual outcome | Agreed disposition |
| --- | --- |
| Nonzero, outputs absent | Strict request/capture; null output refs and no fabricated rows; inventory-derived failed receipts. |
| Nonzero, partial/malformed or valid-looking outputs present | Exact owned opaque failure attachments at only the two fixed result/symbol slots; no semantic decoding or successful receipt promotion. |
| Zero, empty stderr, valid produced transport | Full strict schemas, provenance, census and semantic replay comparison. |
| Zero, empty stderr, invalid/missing/state-failed transport | Invalid proof / exit 2; no opaque exception or measurement publication. |
| Zero with any stderr, including whitespace | Invalid proof / exit 2; repeated stderr in replay cannot rescue it. |

The otherwise-valid/nonzero scenario deliberately does not trigger a schema
probe: it receives the same opaque treatment as any other nonzero output.
That makes the consumer behavior implementable without guessing how much of a
partial file is valid or manufacturing a missing child result/provenance.

`failed_replay_operands` compares common bindings plus an explicit outcome tuple:
fixed reason code, actual integer return code, stderr presence, result presence
and symbol presence. Failed receipt semantics and reconstructed graph/Python
evidence also agree. Each invocation's purpose, IDs, actual capture, references,
optional file bytes and ownership are checked within its own root. Missing
semantic records are not required as comparison operands.

The deliberately limited consequence is **unavailable/fail-1 only**. Mixed
success/failure, tuple disagreement, strict invalid outcomes and integrity
failures reject/2. A failure in a zero-JS-input invocation still adds an explicit
unavailable reason; the empty receipt partition cannot imply success.

Opaque contents need not match across runs and are not authenticated by
rehashing them. Revision 3 says this explicitly and never consumes their alleged
counts, provenance or syntax. That is acceptable for diagnostic-only retention,
not a weakening of successful measurement provenance. Actual return codes
124/125 are not misrepresented as unambiguous timeout/cleanup identities.

Archive rules now copy admitted opaque bytes unchanged, check their identities,
and forbid per-file JS syntax after nonzero execution. Absent slots remain
reserved but uncopied. Invalid branches get no new archive/recovery mechanism.
The existing strict rules for requests, captures, manifests, qualification
ownership and successful per-file syntax are not relaxed.
**No residual design correction is required for this finding.**

## Six-suffix inventory caution — RESOLVED

FACT: the actual `CODE_EXT` and `JS_EXT` already contain `.jsx` and `.tsx`
(`scripts/measure.py:18–20`), but `_walk` currently labels them unsupported
(`257–265`). `code_files` returns the path census without filtering by those
language labels (`274–278`). The proposed defaulted keyword changes
classification, not discovery.

The full composition chain is now explicit and consistent:

| Boundary | Revision-3 contract |
| --- | --- |
| Existing `code_files(root)` / presnapshot discovery | Uses default `_walk`; the six-suffix paths are already present. No mode-based path omission. |
| Proposed `inventory(..., *, include_js=False)` and private `_walk` | Require a real bool; inventory forwards it. Only True classifies JSX as javascript and TSX as typescript, pending before hashing. |
| Probe base/head creation | Derives the same keyword value from successfully validated `config.tools.typescript`; passes it explicitly to both inventories. |
| Private JS execution preflight | Canonically rederives the incoming inventory using that validated mode before request persistence/launch. |
| Existing full producer validation | Source-binds config and supplies the mode at the full inventory comparison currently at `measure.py:1203–1206`. |
| Fresh replay | Reuses checked immutable inventories/digests; the private core applies the same mode-aware validation, not a rewritten copy. |
| Graph | Rejects wrong enabled classifications; never upgrades FileEntry fields or rewrites the inventory digest. Actual outcomes live in receipts/evidence. |

These rules occur together in `mode_and_interfaces.inventory_classification`,
the proposed interfaces, production/validation order, and `JS-PARSE-01` /
`JS-COMPAT-01`. A keyword is explicit data passed between owners, not independent
execution authority. Neither file presence, entrypoints, manifest names nor
supplied inventory fields select an accepting mode.

Omitted/False preserves legacy values and digest formula, including native-only
configurations. True adds no artificial salt when there are no JSX/TSX entries;
pending never means parsed or valid UTF-8. Wrong-mode/rehashed inventories are
rejected by canonical measure-owned rederivation. The existing positional
callers can remain valid; both actual production creation calls
(`probe.py:567–568`) and the existing validation call (`measure.py:1205`) are
explicitly accounted for. No hidden-mode or graph-side relabeling gap remains.

## Unchanged-body consistency and retained limits

FACT: structural comparison of revision 2 and revision 3 found:

- All **15 existing JS record field maps are unchanged**. Only the request,
  command and result invariants and symbol-record ownership text changed.
- `manifest_role_extension`, `type_rules`, `identity_and_projection` and
  `excluded` are unchanged. The one new role remains `manifest`, with exact
  backward-only phase rows and null revision; R1 qualification rules stay intact.
- The changed binding clauses are input admission, invocation binding and
  comparison projection. Parser/toolset/settings digests and controller binding
  are unchanged contract bodies.
- The changed manifest clauses are reservation planning, produced admission and
  archive policy. Preflight, final-row and predecessor-ownership bodies remain
  consistent with those changes.
- All seven existing focused test IDs remain. No new suite, collector or
  architecture was introduced.

INFERENCE: the revised scoped failure exception is compatible with unchanged
type rules because it explicitly declines to treat nonzero attachments as
instances of the semantic record types. `JSProvenance` requirements still apply
when consuming successful records; they do not force invented provenance for
an absent failed result. General invalid-control/result-link clauses retain
their meaning for strict control records, actual Artifact references and
semantically consumed output.

Successful replay now explicitly compares receipt fields other than own-run
raw references, while validating those references in each run. It compares
semantic result/symbol content rather than invocation-dependent Artifact hashes.
The failed branch has its own operands. Neither branch relies on a trusted
rehashed summary or generic hash/path removal.

The qualified virtual compiler read boundary now explicitly includes relevant
cwd/realpath/default-library operations. The first review's source-grounded
read/decode and library-resource cautions remain implementation obligations,
not a demand for another qualification cycle. Finite symbols, source-backed
IDs, diagnostics, UTF-16/UTF-8/CRLF/point spans, original Candidate/Finding/
SyntaxEvidence shapes and graph's nonexecuting role retain their accepted
design treatment.

The existing graph-only JS validation restriction remains truthful: accepting
semantic validation belongs to measure's real replay. Python-only/default
digest behavior remains required, as does truthful mixed-graph observation
projection. These are matters for the specified implementation proof, not
unresolved design blockers.

## Evidence method and implementation-start boundary

Only this separate review file was authored. The first review, historical r2
copies, authority files, proposal files and runtime were not edited. Read-only
hash/Git/JSON comparisons used the supplied managed Python with `-B` through
`scripts/run.py --idle 30 --max 120 -- ...`, with the supplied Git PATH.
Those commands completed with exit 0; no new diagnostic failure or timeout
occurred. Prior-pass failures remain preserved in the first review.

No production/test execution, prototype, new compiler qualification, agents,
installation, source edits, commits, publication, privilege changes or cleanup
were performed. Existing parent-owned workspace changes were left alone.

**Disposition:** APPROVE the frozen revision-3 amendment for the parent's minimal
implementation release. Close JS-R1/R2/R3 and the six-suffix design caution.
Keep the existing real lifecycle, mode, tamper, parser and compatibility proofs
as implementation acceptance requirements. This does not authorize scalar
collectors, root mutation execution, coverage/reporters, metric-bridge,
recovery or host work, and does not claim those proofs have run.

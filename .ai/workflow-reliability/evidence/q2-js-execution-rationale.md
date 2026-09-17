# Shared JS execution amendment

**Revision 3, proposal only.** All three focused findings are accepted. Exact reviewed revision-2 bytes were retained before editing. Original contract, accepted root/R1 boundaries and review records remain untouched. This closes execution seams for the shared TypeScript parser; it is not implementation release or a new workflow.

## JS-R1: discover the actual base before reserving outputs

The existing caller already materializes the immutable base early (`probe._execute_configured`, through `_copy_subject`). Retain that ordering. Filesystem discovery cannot find deleted/base-only files before their base exists; head is not a substitute.

**Materialize base → discover actual base/current-head union and metadata → check collisions/reserve → head Snapshot/copy → reconcile immutable inventories → stage qualifications → preflight → JS execution → produced manifest → graph → final manifest.**

Use existing code discovery, including base-only Python/JS syntax slots and both revisions' ancestor metadata/entrypoint inputs. Reject source, metadata, qualification and archive-output collisions before exclusions. Reconcile after snapshot/copy; drift aborts rather than adding exclusions. No new Git-tree frontend, baseline policy or blanket exclusion.

**Six-suffix classification:** Add `inventory(..., *, include_js=False)` and the same keyword to its existing private `_walk`. Only validated TypeScript mode supplies `True`, explicitly at creation and rederivation. Before digesting, JSX becomes `javascript` and TSX `typescript`, both `pending`, with null parser and empty reason/diagnostics—not successfully parsed. Graph never rewrites the Inventory; actual parsing yields separate receipts. Default/False preserves legacy unsupported JSX/TSX fields and exact digest behavior. Discovery paths stay identical; no mode field, salt or hidden selector is added. Wrong-mode/rehashed inventories reject.

The three immutable files remain necessary: `js-preflight.json` owns available qualification rows; `js-produced.json` owns preflight plus admitted actual JS artifacts; `manifest.json` owns both predecessors plus actual syntax/graphs. Retained controls use the sole proposed role addition, **`manifest`, revision `null`**. Only the active manifest uses existing Context/self-reference semantics. Exact reconstructed phase sets, hashes, reservations, backward links and unchanged R1 ownership are mandatory; pending paths never acquire invented hashes.

## JS-R2: explicit private execution purpose

The public `measure.execute_js(context, inventory, config)` supplies compiled `produce` to private `_execute_js(..., *, purpose)`. `validate_observations` supplies compiled `validate` directly to that same core. The core checks the request against its actual argument before launch and after capture; comparison independently enforces original/replay purposes. No user option, Context field, environment/path inference or callback selects purpose.

Measure executes before graph and owns fresh replay roots/copies. Graph remains the sole ParsedInventory builder, never spawning tools or importing measure/probe. Successful replay compares semantic data while each invocation's roots, purpose, IDs and Artifact links are checked independently. The copied executing JS controller remains the required sixth file; Q1 keeps its five-file formula.

## JS-R3: one finite output policy, including failed replay

The JSON's single table governs producer admission, manifest reconstruction, graph consumption, replay and archive. A shared pure dispatch selects **nonzero-opaque**, **zero-stderr-invalid**, or **zero-strict** from the actual capture. It is not another execution framework.

For nonzero execution, absent files have null refs and no rows. Present partial/malformed **or otherwise-valid** result/symbol bytes receive identical treatment: exact opaque failure retention at their two reserved syntax-role slots, without semantic decoding. Every JS receipt is failed with null count; a zero-input failure still makes the observation unavailable. Never manufacture child output/provenance or consume a claimed successful census.

This narrowly overrides schema consumption only for those two files after observed nonzero execution. Ownership, path, physical independence, hash/length and before/after copy checks never relax. Commands, requests, controls and per-file SyntaxEvidence remain strict. Publication copies the admitted materialized set, not reservations.

Failed replay compares common bindings and the exact tuple: fixed `js-command-nonzero` reason, integer return code, stderr presence, result presence and symbol presence. Invocation details and opaque bytes are checked in their own runs, not normalized or cross-compared. No absent syntax/provenance operand is required. A matched failure permits only unavailable/fail-1; mixed success/failure, unequal tuples or integrity errors reject/2.

`run_capture` exposes integer status and decoded streams, not unambiguous timeout identity: 124/125 can have multiple causes. Retain those observations without claiming stronger process proof. Opaque retention is not authentication and never establishes semantic success.

Zero exit with empty stderr requires complete produced transport, provenance and census. Missing/malformed/inconsistent output, `state=failed`, or any zero-exit stderr rejects/2, even if repeated in replay. None gets opaque admission or measurement publication.

## Retained boundaries and focused proof

The finite symbol schema and unchanged SyntaxEvidence/Candidate/Finding shapes remain. Successful records still require qualified compiler/resource checks, complete census, source-backed identities and byte projections. Python-only behavior is unchanged.

Existing test IDs now require real base-only code/metadata, purpose-swap rejection, actual partial/nonzero/timeout children, strict zero-exit rejection, opaque-byte archive checks and fresh replay. Fixture-command admission tests are distinct from fixed-producer lifecycle proof; no mocked runner or production fault switch.

No tests/runtime/parser were changed or executed for this proposal. Scalar collectors, coverage, root mutants, metric bridge and recovery remain excluded. The parent sends these frozen r3 bytes to the same focused reviewer before any implementation release.

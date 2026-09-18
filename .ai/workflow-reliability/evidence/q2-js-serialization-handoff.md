# Q2 shared-JS serialization and candidate increment

**Status: native library development proof, not configured JS measurement or Q2 acceptance.**
Continues parser checkpoint `886d699a9b8523f2846c65b21fcfd56fc5b3e0dc`.
Original contract SHA-256 `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12`,
root amendment `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1`,
and accepted JS revision 3 `887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e`
remain unchanged. Independent verification/review belongs to the parent. Human approval remains
unconfirmed; implementation follows the explicit autonomous release.

## Executable increment

`scripts/measure_js.mjs` now exports:

| API | Actual behavior |
|---|---|
| `parserDigest(compiler)` | Binds executing adapter bytes, qualified compiler/module/resource locators and bytes, Node executable/version/ARM64 architecture, and fixed compiler options; independent of controller-copy location. Rechecks the controller/resources/runtime. |
| `settingsDigest(jsEntrypoints)` | Canonical digest of fixed compiler/semantic profile and entrypoint declarations. |
| `serializeProgram(result, binding, {input, bytes})` | Uses the existing Program/checker and private source census. Returns `{syntax, symbols}`: unchanged SyntaxEvidence records and a separate JSSymbolEvidenceV1. Checks actual config bytes/TypeScript binding and parser/settings identities. |
| `candidatesForProgram(result, inventory, syntaxEvidence)` | Uses the same Program, exact serialized syntax and complete matching head Inventory. Returns unsampled `{eligible, no_operator, unsupported_scope}`. No writes or execution of mutants. |

Serialized evidence contains source/lexical symbol identities, declarations, checker-resolved aliases,
exports, references, NodeNext literal module references, computed/outside-model sites, parser-recognized
suppression directives, original diagnostics, and config/package/suite entrypoint origins. Failed and
empty files retain census entries. Unsupported package conditions remain explicit outside-model sites.
Native candidate generation handles operator-family precedence, executable template interpolations,
JSX/TSX, safe expression/return replacement, strict byte spans and whole-file before/after hashes.
Type-only/ambient nodes, comments, literal template text, regex bodies and arrow tokens are not operators.

The test fixtures materialize real Git base/head revisions, including at least three baseline Python
files, base-only JS, package metadata, aliases/cycles, failed inputs and a head-only public root.
Q1Fixture is used for actual subjects/inventory/source identities, **not as proof of staged JS ownership**.
Nonempty JS entrypoints are exercised through the native API; public `measure.validate_config` still
rejects them until composition is implemented. The native serializer is not an accepting Context,
manifest or MetricObservation validator.

## Current-byte proof

Final capture: `q2-js-serialization-final-02/console.txt`: **15 Python methods passed in 383.070s**.
The 13 actual Node invocations are nested within those 15, not 13 additional tests. All returned 0
with empty stderr under Node v24.11.1 ARM64 and qualified TypeScript 5.9.3. Before/after owned hashes
match. Per-invocation records retain actual argv/cwd/bounds, stream captures, executing-source hashes,
qualification-input digest and native assertions/proofs without duplicating the qualification archives.

Exact final command, from the worktree, with Git's qualified `cmd` directory prepended to PATH and
`Q2_JS_RECORDS` set to the final capture directory:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u -m unittest discover -s scripts\tests -p test_measure_js.py -v
```

Every native child retained idle 30 / max 90. The native argv is the qualified
`C:\Program Files\nodejs\node.exe` plus this worktree's `scripts\tests\measure_js.test.mjs`;
the harness imports the separately copied, hash-checked controller. Whitespace checking of the four
owned changed files also returned 0.

The actual-source fixture enumerated **56 candidates for `evals/lib/score.mjs`** (source SHA
`f157afed1976fd39bc9c2c44728f3993dc01a0cc3152e3f3eaf4a41779cf3fdd`) and **68 for
`scripts/native_result.mjs`** (`528aeec659fde03cab9edd3167a8b2bc184b7194a3f534dd13a4e0a0c38163e0`).
These are byte-identical source copies added to a real Git fixture, not edits or mutant executions
in the actual repository. A separate fixture's 12 candidates were independently reconstructed in
Python using the existing canonical JSON encoder and actual source bytes. Three fixture edits were
syntax-preflighted through the qualified parser without execution.

## Accepted-check mapping and remaining work

All method names below belong to `test_measure_js.SharedJSCoreTests`. No row claims full acceptance
of the future integrated lifecycle.

| Accepted ID | Current methods / proof | Remaining |
|---|---|---|
| JS-LIFE-01 | `test_native_two_git_revision_census`, `test_native_serialized_freshness_and_identity`: real revision membership, base-only JS, immutable identities and head-only root state | Measure-owned execution before graph, actual-base union/collision reservations and three immutable manifests |
| JS-LIFE-02 | None: not implemented | Fresh validate-purpose execution, semantic replay, finite nonzero/zero-stderr output table, opaque retention and materialized archival |
| JS-OWN-01 | `test_native_parser_digest_independent_copy`, `test_native_serialized_freshness_and_identity`, `test_native_candidates_from_shared_syntax`: copied-controller identity/change detection, source/config/parser and rehashed syntax/inventory rejection | Manifest-chain/R1/control ownership, purpose swaps, rehashed raw symbol/command/result tamper and post-archive checks |
| JS-PARSE-01 | `test_native_byte_boundaries`, `test_native_six_suffix_census`, `test_native_syntax_shapes`, both `test_native_candidates_*` methods, `test_native_serialized_zero_js_inputs` | Native serialization/candidate cases pass; production transport and graph consumption still absent |
| JS-SYMBOL-01 | `test_native_serialized_source_records_and_origins`, `test_native_serialized_freshness_and_identity`: aliases, cycles, local/external/unresolved/type imports, namespace access, CommonJS, shadowed require, roots, stable lexical IDs | Accepting raw consumer/replay; explicit merged-declaration, import-equals and namespace-reexport fixture coverage remains absent |
| JS-DIAG-01 | `test_native_diagnostics_and_checker_alias`, `test_native_errors_and_empty_program`, `test_native_serialized_source_records_and_origins`: original compiler diagnostics, missing/invalid sources, directives | Command-output failure admission and rehashed diagnostic/receipt consumer tests |
| JS-COMPAT-01 | `test_inventory_keywords_preserve_legacy_and_pending_entries`, `test_controller_digest_and_no_inventory_mode_salt`, `test_native_actual_root_syntax_without_execution`, candidate wrong-mode rehash case | Default library compatibility passes; mixed configured-probe and integrated no-JS lifecycle acceptance not refreshed |

Next dependency is the fixed JSRequest command plus measure-owned execution and immutable ownership
handoff, followed by nonexecuting graph projection and fresh replay. No integration function was
stubbed or partially advertised. `measure.py`, `measure_graph.py`, `probe.py` and all frozen core files
are unchanged in this increment. There is no live sample-app verification yet.

## Preserved development history and limits

| Capture | Actual outcome, not additive acceptance |
|---|---|
| `dev-01` | 1 failed: implicit TypeScript CommonJS require symbol was mistaken for a shadowed local. Corrected using actual declarations. |
| `dev-02` | 2/4 passed: candidate validation used `parser_sha256` instead of actual FileEntry `parser`. Corrected. |
| `dev-03` | 2 candidate methods passed. |
| `dev-04` | 5 methods passed on then-current bytes. |
| `final-01` | 13/14 passed; expanded freshness case returned capturer 124 / `[idle-timeout]`. Not accepted as a green final run. |
| `retry-01` | One bounded smaller-scope retry: freshness and independently split controller-copy method both passed (69.623s); bounds unchanged. |
| `final-02` | Fresh combined 15/15 on frozen current bytes. |

All directories above have prefix `q2-js-serialization-`. The timeout belongs to the test harness,
not an implemented production failure-table fixture. A narrowly scoped process observation found no
remaining command line for this exact native test script; full descendant cleanup remains UNKNOWN.
No privilege changes, process-name killing or unowned-temp cleanup occurred. The historical symlink
WinError1314 limitation remains unverified and was not retried.

No full repository suite, scalar collection, coverage, actual root mutations, guarded metrics,
recovery, C4 work or quality closure is claimed. Historical 262-source and 15+2 independent results
are not relabeled fresh. No packages, agents, commits or pushes. Unrelated `evals/report.md` remains
untouched. The adjacent seal lists all owned files; independent review and verification remain pending.

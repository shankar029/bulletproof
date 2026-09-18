# Q2 shared-JS parser-core development checkpoint

**Partial implementation, frozen for parent-owned verification/review. Not the
complete shared-JS vertical component, Q2 acceptance, or overall task completion.**
The implementation release is based on accepted revision 3
`887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e`.
Original contracts, root amendment, accepted JS amendment/reviews and state were
not edited. Human approval remains unconfirmed; continuation was explicitly autonomous.

## Delivered and executable

- `measure_js.mjs` is a native library, not a JSRequestV1 command or metric importer.
  `openCompiler(binding, source)` consumes the existing Python-qualified binding/source
  description, requires the absolute qualified TypeScript module and Node runtime,
  verifies pinned resources and loaded CommonJS module paths, and rejects changed
  settings/preload inputs. No ambient TypeScript/package lookup or installation.
  `parseProgram` accepts only a handle opened by this module, not supplied read/verify
  callbacks. This is not an independent replacement for Python ToolBinding qualification.
- `parseProgram(compiler, root, entries, metadata)` builds one real controlled-host
  TypeScript Program/checker from explicit pinned files. No source discovery or source
  execution. Virtual subject/resource paths, library/cwd/directory/realpath/read
  operations are explicit; source and resource bytes are rechecked.
  Its native return contains live Program/checker objects for further native work;
  these never enter the test JSON transport or a ParsedInventory.
- The core produces actual six-suffix census records and original compiler diagnostic
  records, including failed syntax/UTF-8/missing inputs, empty/comment/functionless
  inputs, source-less missing-root diagnostics and exact UTF-16/UTF-8 locations.
  Metadata read/decode errors reject rather than becoming implicit absence.
  `SourceBytes` preserves BOM/CRLF, rejects split-surrogate/non-byte boundaries,
  preserves point/EOF ranges and enforces nonempty syntax spans.
- `_walk` and `inventory` now have the approved strict-boolean `include_js=False`
  keyword. True classifies JSX/TSX as pending JavaScript/TypeScript before digesting.
  Default/False preserves original classifications, paths and digest formula.
  `controller_digest(..., include_js=False)` preserves the five-file formula;
  True requires six actual independent files including `measure_js.mjs`.
- The directly related quality-metrics reference explicitly states this support
  boundary. No configured JS measurement support is advertised.

The source/pin checks above are native-core consistency checks, not R1 execution
admission, authenticated producer provenance or a successful measurement receipt.

## Frozen owned implementation paths

| Path | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `b5a824cd84a4a63bb1a6ec5cb6d2e09426614006b12f0b9ef867f040439c4db9` |
| `scripts/measure_js.mjs` | `bc1467eaf8666dcb162525cb78d25feb3672f28eac10af45745feec731522b23` |
| `scripts/tests/test_measure_js.py` | `ed0463f8ee6b0c3de382369a6b1762793467b755d4f0ac68d19e2be44cae8ebc` |
| `scripts/tests/measure_js.test.mjs` | `aa15edc62252fd86043e9e759196d8a86f5560ffdc9314ad86f1f14281f48e3f` |
| `references/quality-metrics.md` | `4706eee4c2ba142eec951bbc3a26cb1df846ba7595d5414d813814ebdd8a37a5` |

`q2-js-seal.json` binds these paths, this handoff and all newly owned evidence files.
Its own digest is supplied separately, avoiding a self-hash. Final before/after/current
implementation pins agree. Editing `measure.py` naturally changed controller hashes;
no historical numeric controller hash or whole-source freeze is claimed.
The unrelated `evals/report.md` change was not edited.

## Actual final development proof

**15 distinct Python methods passed in 879.393 seconds, exit 0, on the same bytes.**
This is nine new core methods plus six selected existing regression methods, not
the historical 262-method verification or a full current suite.

Seven of the nine new methods each execute one real native test case through a
fresh Node process, importing an exact independent copy of `measure_js.mjs`.
Those seven nested cases are not seven additional Python tests or semantic replays.
The existing three-tool/two-revision regression executes six binding smokes
(TypeScript/lizard/Vulture at base/head); these are not six additional test methods.
Their captures all have returncode 0 and empty stderr.

`q2-js-core-final-01/` retains `before.json`, `after.json`, `unittest.log`,
seven `test_native_*.json` captures, and the existing binding test's actual records.
Each native capture records exact absolute argv/cwd, removed environment names,
idle/max bounds, copied-controller hash, qualified input description and actual
stdout/stderr/results. Temporary subject paths describe the real invocation, not
reusable current artifact roots. The log is streamed outer-console capture; the
per-command streams retain existing run_capture decoding/newline semantics.

Final invocation used the managed Python, qualified Git PATH prefix and
`PYTHONPATH=<worktree>\scripts\tests;<worktree>\scripts`:

```text
<python> -B -u scripts\run.py --idle 120 --max 900 -- <python> -B -u -m unittest -v
  test_measure_js
  test_measure_inventory.InventoryTests.test_one_discovery_owner_and_standalone_imports
  test_measure_inventory.InventoryTests.test_inventory_retains_all_code_and_deliberate_exclusions
  test_measure_graph.GraphTests.test_zero_import_receipts_complete_and_source_bytes_are_not_executed
  test_measure_graph.GraphTests.test_invalid_python_and_mixed_languages_remain_explicit
  test_measure_graph.GraphTests.test_rehashed_graph_payload_is_not_accepted_as_authoritative
  test_measure_source_bindings.SourceBindingTests.test_actual_three_tools_at_two_git_revisions_with_import_provenance
```

Here `<python>` is
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`.
The seven core child argv are the qualified
`C:\Program Files\nodejs\node.exe` followed by the absolute
`scripts\tests\measure_js.test.mjs` path; exact case/input locators are in each
capture's request and case fields. Every core/source-binding child kept idle 30 /
max 90. Actual native runtime records are v24.11.1 / ARM64. Python methods emitted
real start/completion progress; existing binding resource-rehash progress was not
replaced with heartbeats. No timeout or bounds increase occurred.

The six-suffix case produced **30 actual inputs: 18 processed and 12 explicit failures**
(six each of empty, comment-only, functionless, invalid syntax and invalid UTF-8).
The two-Git-revision core case includes at least three base code files, base-only JS,
changed source bytes and changed package metadata. Native checker assertions follow
an actual reexport alias across `.js` to `.ts` resolution. Native tests also parse
actual `score.mjs` and `native_result.mjs` and prove a source side effect is not executed.
No candidate edits or root mutants ran.

Both JS files passed real `node --check`; both changed Python files passed AST
parsing without bytecode. Post-run reconciliation verified the command counts,
census partition and before/after/current pins. These checks are not metric measurements.

## Exact accepted test-ID disposition

No complete accepted JS test ID is claimed satisfied by this smaller checkpoint.
The following method suffixes belong to `test_measure_js.SharedJSCoreTests`.

| Accepted ID | Actual covered fragment | Still required |
| --- | --- | --- |
| JS-LIFE-01 | `test_native_two_git_revision_census`: real distinct revisions, base-only JS, changed package metadata; copied native controller | Base-only Python correction scenario; complete presnapshot reservation/collision audit; before-graph execution; three manifests; measurement archive |
| JS-LIFE-02 | No producer replay proof. Two different source revisions are **not** original/replay executions | Compiled produce/validate core, private fresh replay Context/copies, purpose swapping, semantic and failed-tuple comparison |
| JS-OWN-01 | `test_native_errors_and_empty_program`, `test_controller_digest_and_no_inventory_mode_salt`: source/settings/pin/reader/path/handle rejection; missing/changed/hardlinked controller rejection | Full R1/predecessor ownership and rehashed controls/symbol tamper; no-launch audit; actual absent/partial/valid-looking nonzero and timeout fixture commands; strict zero-exit invalid/stderr; opaque archive |
| JS-PARSE-01 | `test_native_byte_boundaries`, `test_native_six_suffix_census`, `test_native_syntax_shapes`: six suffixes, empty/invalid inputs, BOM/Unicode/CRLF/point boundaries, regex versus division, templates/interpolation, types, arrows and body-bearing function counts | Unchanged SyntaxEvidence serialization and ParsedInventory integration; candidate generation/deletion/identity and invalid-candidate tests |
| JS-SYMBOL-01 | `test_native_diagnostics_and_checker_alias`: real checker export/reexport alias equality and local/external unresolved diagnostics | Full symbol/reference artifact, lexical IDs, cycles/merged declarations, namespaces/dynamic/runtime sites, backed entrypoint origins and semantic tamper replay |
| JS-DIAG-01 | Native diagnostics/empty-program methods: actual 2322, 2307, source-less 6053, EOF and byte projection; no syntax failure inferred solely from type errors | Full bad-options, related-information/library-diagnostic cases and end-to-end producer raw validation |
| JS-COMPAT-01 | Inventory/controller keyword methods, root-syntax method and selected legacy regressions: default/False equality, no mode salt, preserved discovery, legacy wrong-mode rejection, five/six-file formula and actual source-binding smokes | Validated-mode composition and JS-enabled rederivation; candidate calls on real root files; full integration regression and parent independent acceptance |

The legacy wrong-mode test rehashes a True inventory and confirms the current
non-JS validator rejects it. It does **not** prove the future JS-enabled validator.
Live AST/checker assertions are not serialized symbol identities or accepted raw proof.

## Required continuation, not implemented stubs

1. Build the source-bound metadata/entrypoint admission at measure/probe composition;
   pass the validated TypeScript mode for both creation and full rederivation. Existing
   probe and validator calls still deliberately use the legacy default.
2. Complete shared SyntaxEvidence, versioned JSSymbolEvidence and source-backed
   Candidate APIs using the same Program/checker and byte units. No additional regex
   frontend or independent code census.
3. Implement the fixed JSRequestV1 command and measure-owned produce/validate execution,
   six-file controller copying, exact early reservations and R1 preflight checks.
   The library currently rejects direct execution rather than silently succeeding.
4. Implement immutable preflight/produced/final ownership, graph-only projection,
   producer-owned fresh semantic replay and the accepted finite failure table, including
   exact opaque-byte archival. No manifest-role extension is active in runtime yet.
5. Run every remaining scenario in the table before claiming the shared-JS component
   complete. `measure_graph.py` and `probe.py` were not changed in this checkpoint.

Configured JS collection remains unsupported; missing scalar, coverage and mutation
proof remain missing. No new policies/thresholds, scalar collectors, reporters,
metric bridge, recovery, platform work, agents, packages, commits or pushes.
Frozen `evidence.py`/`run.py` APIs did not need changes.

## Retained development history and limitations

- `q2-js-core-development-01`: one initial byte-boundary method passed, 15.391 seconds.
- `q2-js-core-development-02`: eight methods, seven passed and one failed, 142.727
  seconds. Actual comment-only `.cjs` census counted an empty SyntaxList as a token.
  The correction counts real TypeScript tokens and excludes JSDoc traversal; the
  final tests also compare documented/plain code token counts.
- `q2-js-core-development-03`: corrected six-suffix method passed, 24.666 seconds.
  These repeats are history, not extra final coverage. The Node assertion failure
  was a **test-harness failure**, not a fixed-production-parser nonzero scenario.
- One post-run evidence-summary command initially used `record.tool` instead of
  `record.observed.tool`, raising KeyError. The corrected read-only reconciliation
  succeeded without changing or rerunning test records.
- The first seal-generation attempt duplicated the method suffix already present
  in Python 3.14's displayed test ID. Its membership assertion stopped before any
  seal was written. Corrected extraction uses the actual full displayed ID.
- Existing symlink WinError 1314 and earlier cleanup UNKNOWN remain unverified.
  No privilege retry, host experiment or old-temp cleanup was attempted.
- The full suite, mutation, all seven complete accepted IDs and independent review
  remain outstanding. Parent owns the next verification/review and continuation.

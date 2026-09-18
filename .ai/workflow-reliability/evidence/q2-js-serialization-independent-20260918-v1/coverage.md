# Pre-test coverage map

Resumed independent Phase 5 only. No new design/qualification/production work.
The 15 owner methods are replayed unchanged; nested Node cases are not extra methods.

| Native behavior | Existing coverage (test_measure_js.py / measure_js.test.mjs) |
|---|---|
| Byte boundaries, six suffixes, shapes, diagnostics/checker, failed/empty parsing | `test_native_byte_boundaries`, `test_native_six_suffix_census`, `test_native_syntax_shapes`, `test_native_diagnostics_and_checker_alias`, `test_native_errors_and_empty_program` |
| Real two-revision census and actual-source nonexecution | `test_native_two_git_revision_census`, `test_native_actual_root_syntax_without_execution` |
| Legacy inventory/controller compatibility | `test_inventory_keywords_preserve_legacy_and_pending_entries`, `test_controller_digest_and_no_inventory_mode_salt` |
| Source records, aliases/cycles, namespaces, imports, diagnostics, origins | `test_native_serialized_source_records_and_origins`; native `serialized_records` |
| Binding/freshness and copy-independent parser identity | `test_native_serialized_freshness_and_identity`, `test_native_parser_digest_independent_copy` |
| Candidates/byte edits/current controller sources/zero JS | `test_native_candidates_from_shared_syntax`, `test_native_candidates_on_actual_controller_sources`, `test_native_serialized_zero_js_inputs` |

Confirmed uncovered in these fixtures: merged declarations, import-equals aliases,
namespace reexports. The accepted revision-3 contract explicitly includes merged IDs
(type_rules.resolution_rules; records.JSSymbol.invariants), import-equals (records.JSAlias)
and reexports (records.JSExport, acceptance JS-SYMBOL-01). Source implements them at
`measure_js.mjs:477–573,654–655,671–688`. Thus they are within this native API's model.

Plan: **one additional ordinary-discoverable Python method**, one real native invocation,
one small real Git/Program/checker fixture. Exercise class+namespace and interface merges,
external-module and internal-qualified import-equals aliases, and `export * as bundle`.
Assert typed local resolutions, actual checker declaration sets/flags, canonical merged IDs,
source-backed spans, and alias/reference/export target agreement. Do not duplicate candidate,
freshness, six-suffix or lifecycle tests. Use existing fixture helpers, not TestCase inheritance.

Limits: native records are not an accepting consumer or a complete JS-SYMBOL-01 proof.
Transport/manifests/graph/replay/scalars/metrics/recovery/full-quality/live-model remain out
of scope. Parent state/report are not owned. Independent state is recorded in this directory.

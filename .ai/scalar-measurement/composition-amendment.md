# Proposed narrow scalar composition amendment

Status: PROPOSED; requires independent review and parent release before wiring.
Grounded in reviewed JS checkpoint `2bc8af72aa3cfa486554e8544f1e0ff0f1a133a8`,
cherry-picked locally as `41c61be`. Native `measure_js.mjs` remains unchanged.
This explicitly amends outer producer binding/ownership, not JSRequestV1.

## Observed seams

- `measure.py:419-746` owns `_regular_file`, `_artifact_bytes`, `_path_partition`,
  `tool_artifacts`, `_external_pin`, the source-profile constants,
  `_resource_pin`, `_source_inputs`, `_qualified_inputs`, `toolset_digest`,
  `stage_tool_inputs`. These depend on graph path/JSON/parser primitives, not probe.
- `measure.py:1137-1205` derives JS tool bindings and rechecks source/controller;
  `1245-1293` invokes the native producer; `1296-1319` owns fresh accepting replay.
- `measure_graph.py:26-28,113-184,505-579` fixes six native controller files,
  compares exact request Context and reconstructs finite manifests/reservations.
- `measure_js.mjs:1139-1145` recomputes Context.controller_sha256 over exactly six
  files. It does not load Python helpers. Adding a seventh native controller or
  passing an eight-file digest would break that unchanged accepted contract.
- `probe.py:530-552,573-581,600-611,624-638` plans exclusions before snapshot,
  copies controller files, collects both revisions, validates and archives only
  materialized records in JS mode.

## Exact dependency extraction

Move the functions/constants in the first bullet, unchanged in semantics, into
`scripts/measure_tools.py`; import/reexport their existing names from measure for
compatibility. `measure_tools` imports graph, evidence and stdlib only. Scalars
import tools, graph and run; no reverse import of measure/probe, registry,
callback, arbitrary command channel or duplicate provenance engine.

Keep measure-owned binding smoke/probe execution, Context/source-config lookup,
config policy/validation, root independence, JS execution/replay and publication
in place. Their existing calls resolve the reexports. Scalar calls invoke the
same `_qualified_inputs` and `toolset_digest`, never infer package locations.

## Explicit outer producer-binding delta

Keep `Context.controller_sha256` and the JS request/provenance six-file profile
unchanged in JS mode (five legacy controllers in empty-tool Q1 mode).
**This narrows that field's description to the existing fixed controller profile;
it is no longer alone a claim to bind every Python producer module.**

Extend `toolset_digest` with a compiled `python_producers` binding containing
exact byte hashes of `measure_tools.py` and `measure_scalars.py`. This is producer
identity as well as external analyzer identity; both revisions use the same
digest. Even empty-tool Q1 binds these two new modules: the old empty toolset
formula changes explicitly, not via a silent compatibility fallback. Config,
Context and report field shapes remain unchanged.

Native coexistence is source-verified, not inferred from controller count:
`measure_js.mjs:449-460` checks hash syntax, parser identity and settings identity;
`1070-1078` requires binding.toolset_sha256 equal Context.toolset_sha256.
`commandCompiler` at `1012-1050` independently validates the pinned TypeScript
qualification, runtime/resources and settings. There is no native reconstruction
of Python's canonical toolset_digest object/formula (all `toolset` occurrences
are those field/check sites). The new opaque digest therefore passes unchanged
JSRequestV1 when identically bound in request/context; native compiler checks
remain independent and unchanged. Python owners remain responsible for
recomputing the augmented digest from source before/after execution and acceptance.
This is not a claim that native validates the extra Python producers itself.

Add `measure_tools.producer_binding(root)` returning the fixed two-file map,
with independent regular-file, canonical-path and hash checks. Executing and
accepting owners compare the live map with the copied controller map before
each child, after execution, during accepting replay and before publication.
All controller materializers (public probe and affected test fixtures) copy both
new modules. Missing helper, extra replacement module, rehashed source mutation,
or differing copied bytes rejects. The unchanged native producer still checks
exactly six files; outer validation binds the two additional Python dependencies.
No unbound copied module or ambient-path import is accepted.

## Deterministic scalar evidence ownership

Keep path planning in graph's existing fixed naming/manifest layer, avoiding a
graph-to-scalars import cycle. Add one fixed `scalar_paths(revision)` helper:

- Four normalized RawMetricEvidence files:
  `revision/scalars/duplication.json`, `complexity.json`, `dead_exports.json`,
  `static_findings.json`.
- Five qualified output envelopes and five command captures under
  `revision/scalars/{jscpd-clones,jscpd-census,lizard,vulture,ruff}.{raw,command}.json`.
  A tool absent or with no applicable input creates no command/raw envelope;
  normalized evidence explains its absence, never fabricates execution.

Enable scalar composition when config.tools is nonempty, including TypeScript-only
mode (native dead/static available; other missing tools explicitly unavailable).
Reserve the full finite set for both revisions before snapshot/output exclusions;
check all existing original/input/prefix/case collisions. No dynamic allocation
after exclusion planning. The native preflight accepts extra reserved names but
still has qualification-only inputs, as its current source explicitly requires.

Add the explicit outer manifest phase `graph-produced.json` in scalar-enabled
mode, reserved before snapshot. It owns qualified inputs, native command/output
and shared per-source syntax/graph records, with all scalar slots still absent.
It follows exactly js-preflight.json and js-produced.json. It is the terminal
private JS accepting replay artifact, not a publishable measurement report.

Extend `_js_manifest` at final `manifest.json` reconstruction to include
materialized scalar slots by deterministic producer outcome/absent-tool rules,
with roles scalar/command and matching revision, plus the exact graph-produced
predecessor in scalar-enabled mode; keep exact predecessor manifests.
Do not discover ownership by scanning files; retain rejection of unowned files
and populated absent slots. Python-only nonempty-tool mode uses the same finite
slots through make_manifest. Archive only materialized rows in both modes.

Scratch staging is an owned short temporary directory, never a source input.
Actual argv/cwd, request, tool/runtime identities, returncode, separate normalized
stdout/stderr, output bytes and parse error are retained. Failed output remains
diagnostic raw evidence; native JS nonzero opacity is unchanged.

## Collection and accepting validation

`measure_scalars.collect(context, parsed, config)` returns the five non-cycle
scalar Observations (complexity produces max and average from one payload).
`measure.collect_pair` composes them with graph cycles/architecture; it does not
rerun collection while accepting existing observations.

`measure_scalars.validate_evidence(context, parsed, config, raw, artifacts)`
checks exact schemas, declared manifest artifacts, source/receipt partitions,
rules and bindings; reconstructs normalized records and values from qualified
outputs; and independently reruns the applicable external scalar tool(s) against
the same source in fresh private storage. Compare semantic decoded output,
ignoring only declared transport differences (temporary absolute path roots,
execution timing and jscpd detection timestamp). Rehashed normalized or qualified
output edits cannot become authoritative by updating a manifest.

Native program evidence is consumed via existing `_js_transport` finite dispatch,
not a second parser/checker. Native diagnostics, symbols, aliases/references,
exports and entrypoint origins are derived into scalar findings. **Leaf scalar
validation is not a substitute for native accepting replay:** aggregate
`measure.validate_observations` retains its mandatory fresh `_validate_js_replay`
before accepting mixed scalar observations. Structural native decoding alone
cannot establish acceptance. This remains the producer-owned compound boundary.

Fresh JS replay finishes at the explicit graph-produced.json phase without
requiring scalar collection a second time. Its expected scalar slots remain
reserved but absent and any populated scalar slot at that terminal phase
rejects. Production also persists this exact graph predecessor before scalar
collection. Only final manifest.json is accepted by validate_observations and
probe publication, and it is always scalar-complete according to actual
execution outcomes. No caller-supplied skip/replay option or allow-missing switch.
Graph-only, empty-scalar configurations preserve the existing phase sequence.

## Required executable proof before acceptance

1. Empty Q1 imports/config preserved with explicitly updated producer binding;
   copied controller imports work. Missing/changed live or copied new module rejects.
2. Real mixed base/head input, every suffix including zero-function JSX/TSX;
   exact six native controller pins unchanged in every request/provenance record.
3. Exact raw reservations before snapshot, stale originals, command/output
   tampering, rehashed counts/findings/receipts and additional hidden files reject.
4. Native replay still rejects forged directives, entrypoints, symbols and
   diagnostics; scalar replay rejects changed clone census/locations/functions/
   Vulture/Ruff records. No fabricated successful JS parse.
5. Real partial/missing/error inputs remain visible with unavailable comparisons,
   coverage/mutation required and incomplete; no whole-Q/G6 claim.

This amendment does not authorize publication, tool changes, new frameworks,
coverage/mutation implementation, native producer edits or threshold changes.

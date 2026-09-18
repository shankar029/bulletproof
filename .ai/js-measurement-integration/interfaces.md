# Stable integration handoff

This is the accepted revision-3 JS graph increment, not scalar implementation.
The native producer remains unchanged. No source is executed by this path.

## Existing public composition

1. Validate config. Derive `include_js = "typescript" in config["tools"]` only
   after validation; explicit nonempty `js_entrypoints` now validate.
2. Materialize immutable base before actual base/head discovery and metadata
   reservation planning. Create both inventories with the same explicit mode.
3. Copy the fixed six-controller profile and stage selected qualification bytes.
4. `measure.prepare_js_manifest(context, inventories, config) -> Artifact`
   publishes preflight and updates `context["output_manifest"]`.
5. `measure.execute_js(context, inventory, config) -> None` uses fixed purpose
   `produce`; it never builds a ParsedInventory.
6. `measure.finish_js_manifest(context, inventories, config) -> Artifact`
   publishes produced ownership and updates the active manifest.
7. `measure_graph.parse_files(context, inventory, config) -> ParsedInventory`
   is the sole nonexecuting parse/projection owner.
8. `measure.make_manifest(context, base, head) -> dict` reconstructs final
   ownership. The composition owner persists `manifest.json` and binds Context.
9. `measure.validate_observations(...)` owns accepting replay: internal fresh
   storage, independent staging, private `_execute_js(..., purpose="validate")`,
   both revisions, exact semantic comparison, and final freshness checks.
   There is no caller-supplied replay Context, trusted-result option or cache.

`probe._execute_configured` implements this ordering, validates its report,
then archives actual final inputs plus the active manifest. Reserved absent
files are not fabricated or copied.

## Parsed and raw consumption

The unchanged ParsedInventory keys are `inventory`, `receipts`,
`syntax_artifacts`, `graph`. The inventory is immutable; syntax_artifacts maps
only actual source paths to successful SyntaxEvidence artifacts. It contains
no pseudo-source entry for the program-level JS symbol table.

Each inventory entry has a receipt. Processed JS receipts use
`typescript-compiler` / `typescript-shared-v1`, actual literal-import unit counts,
and syntax/result/symbol references. Failed native commands derive failed JS
receipts from inventory, with `unit_count=None` and stable observed-status
reason. They create no successful per-file JS syntax.

Current private nonexecuting reader:

```python
request, command, result, symbols, request_ref, command_ref = (
    measure_graph._js_transport(context, inventory, config, purpose=None)
)
```

This is structural own-run transport validation, **not full accepting semantic
validation**. Its fixed selectors are `base|head/js/{request,command,result,symbols}.json`.
`result` and `symbols` are decoded records only for admitted zero/empty-stderr
production; both are `None` for nonzero opaque failures.
Use `measure_graph._js_output_action(command)` for the shared finite dispatch.
Never call generic JSON decoding or `read_owned` directly on nonzero
result/symbol attachments to recover alleged counts or successful processing.

The separate `JSSymbolEvidenceV1` retains actual census, symbols, aliases,
exports, references, module references, entrypoint origins, directives and
diagnostics. These are evidence, not scalar totals or complete dead-symbol
proof. Existing `SyntaxEvidence` and `Finding` shapes are not extended.
`measure_graph._compare_js_replay` compares all symbol/result semantic records,
receipts and graph observations after own-root validation. Only declared
transport differences are excluded. `graph.validate_evidence` rejects JS mode
and directs accepting validation to measure rather than downgrading its promise.

JS raw graph evidence uses `python-ast-typescript` /
`mixed-literal-import-graph-v1`, actual capture references, and actual admitted
raw artifacts. Graph edges join literal syntax with compiler module references;
there is no second resolution frontend. Nonzero invocation adds an explicit
unavailable reason even for a zero-JS inventory.

## Minimal future scalar composition seams (not implemented here)

- `measure.collect_pair` currently combines graph observations with explicit
  unavailable observations for the non-cycle lower-better metrics. A scalar
  implementation should consume the shared ParsedInventory/owned evidence,
  not rediscover/reparse JS or execute subjects.
- `measure.validate_observations` must independently rederive any newly
  introduced scalar observations and raw identities. Replacing unavailable
  results or trusting adapter totals alone is not accepting integration.
- New deterministic raw slots must be reserved before the head snapshot and
  admitted through exact ownership reconstruction/publication. Current
  `graph._js_reservations` / `_js_manifest` intentionally admit only the
  revision-3 qualification, control, JS, syntax and graph sets; extra rows or
  files reject. Do not append paths after exclusions or weaken exact matching.
- The current JS controller contract and native provenance require **exactly
  six fixed files**. A future scalar producer/code-binding extension must honor
  its accepted contract; silently copying a seventh helper or broadening this
  profile is not authorized by this increment. This is a genuine integration
  seam for parent disposition, not permission for an unbound adapter.
- Existing config/policy/threshold fields, all nine required metrics, coverage
  floors and mutation floor remain unchanged. Missing adapters stay unavailable.

Scalar collection, coverage/reporters, actual root mutation, metric-admission
bridge, process recovery, host trials and broad qualification remain excluded.

## Source-grounded scalar dependency detail

FACT: `collect(context, parsed, config) -> dict[str, Observation]` is the
**accepted proposed scalar interface**, not an implemented measure/graph API.
Its authority is `measurement-enablement-contracts.json:534-560`; proposed
scalar `validate_evidence(..., raw, artifacts) -> list[Observation]` is at
lines 493-509. Current `measure.collect_pair` (measure.py:399-406) calls only
graph observations plus explicit missing-adapter records. There is no generic
RawMetricEvidence plugin dispatch to reuse or invoke.

FACT: inputs are plain dictionaries, not runtime classes. Context fields are
checked exactly at measure.py:1374-1389; select subject root via
`context[parsed["inventory"]["revision"] + "_root"]`, never caller cwd.
`parse_files` returns the four-key record at measure_graph.py:1009-1017.
Config is the validated source-bound MeasurementConfig including exact tools,
source roots, suites, entrypoints, rules, policy and approval; no new scalar
config fields are introduced by this integration.

FACT: actual native diagnostics are in `base|head/js/symbols.json` under
`diagnostics` (measure_js.mjs:344-352, 787-793), with fields
`id, code, category, source, message, location, related`. `id` is the digest
of the canonical record excluding id. A location is
`{file, utf16_start, utf16_length, byte_range}`; source-less locations have all
four fields null. Located `file` is a scoped JSInput reference; do not assume
every diagnostic belongs to a subject file rather than a tool resource.
Per-file census `diagnostic_ids` refers to these raw IDs. SyntaxEvidence's
`diagnostics` is instead a string list of parser directive notes, not the
compiler's static-finding population (measure_js.mjs:767-784).

FACT: there is **no serialized `unused_symbols` list, no dead-export total,
and no native normalized scalar Observation**. Symbol records are
`{id,name,flags,declarations}`; declaration descriptors carry
`path,kind,lexical_scope,name,token_context,occurrence,source_sha256,span`
(measure_js.mjs:540-549, 576-590). Exports, aliases, references and module
references are separate site records; target resolution carries
`{state,symbol_ids,external,reason}`. Entrypoints and their origins, directives
and outside-model sites remain explicit. The scalar owner must implement the
accepted unused-local diagnostic/export-reference semantics over these
replayed records; absence of a lexical reference is not proof of dynamic
deadness. `candidatesForProgram` is a mutation-candidate API, not an unused
symbol collector (measure_js.mjs:903).

FACT: existing tool helpers live in measure, not graph/scalars:
`tool_artifacts`, `stage_tool_inputs`, `toolset_digest`, private
`_qualified_inputs`, `_source_inputs`, `_external_pin`.
`_SOURCE_PROFILES` (measure.py:515-540) fixes TypeScript/lizard/Vulture APIs.
`_source_inputs` (575-635) decodes the binding.configuration artifact into
the exact five-root map, validates absolute external disjoint roots and
module_path, relocates retained resource paths through those roots and
rehashes the exact files. `_qualified_inputs` (638-705) also checks executable,
dependencies, original qualification and source settings. `toolset_digest`
(708-723) binds parser/config/originals/copies/qualified inputs; staging uses
exclusive opaque copies and rejects shared file identity (726-746).
Do not replace these checks with package discovery, ambient imports or a
guessed module-root compatibility wrapper. Per accepted dependency direction,
a scalar module must not import measure merely to call its private helpers;
any needed validated input handoff belongs to explicit parent composition.
There is **no existing lower-layer general source-tool description seam** in
graph or evidence. `toolset_digest` returns a digest, not the validated resource
description. This absent dependency is not a license to invent an adapter
compatibility layer.

FACT: current graph RawMetricEvidence construction is `_raw`
(measure_graph.py:993-1006): exact common binding fields, receipts, command
Artifact refs, qualified raw Artifact refs, and `payload: {"graph": graph}`.
`read_owned` (1084-1091) checks run/root, exact artifact/role/revision membership,
reservation, byte hash and size before JSON decoding; it is not tool schema
or semantic validation. The actual aggregate dispatch is fixed at
measure.py:1428-1449: fresh JS replay when enabled, graph recomputation, missing
scalar records, exact comparison of supplied observations. Scalar payload
schemas in contract lines 347-365 remain to be implemented and validated.

FACT: raw graph `commands` currently stores **Artifact references**, as do its
normalized graph Observations; do not silently reinterpret these as executed
Command dicts despite the older generic contract's descriptive wording.
Actual JSCommandV1 is checked at measure_graph.py:120-185 and contains
binding/execution_id, request/pre_manifest refs, exact argv, absolute cwd,
idle_seconds=30, max_seconds=90, removed environment names, integer returncode,
separate stdout/stderr strings, capture_semantics, and nullable result/symbol
Artifact refs. These are the actual normalized `run_capture` strings, not
original raw byte streams. Finite nonzero output policy is JS-specific; it is
not a reusable assumption about Ruff/Vulture exit-code semantics.

# Shared JS producer: bounded seam decision needed

**Blocked before production implementation; no parser completion or fresh test claim.**
Actual HEAD is `dadce66ff7d9a7494db0af5f8124009d7b132cb9`. This is a source-grounded handoff under the instruction to name a caller/manifest gap, not a new design/workflow or a change to approved contracts.

## Observed conflicts

1. **Pre-execution ownership versus the actual caller lifecycle.** In `scripts\probe.py::_execute_configured`, the initial Context has no `output_manifest`. After `stage_tool_inputs`, it immediately calls `measure_graph.parse_files` for base and head, collects observations, and only then calls `measure.make_manifest` and persists `manifest.json`. Conversely, `measure.inspect_source_binding` reads `context["output_manifest"]` before the R1-qualified preflight and before launch. Its valid binding tests explicitly supply a manifest first; that is not the public parsing lifecycle. Probe currently reserves syntax paths only for `.py`, copies five Python controller files, and `make_manifest` reconstructs qualification/syntax/graph rows only. A JS execution cannot simply be inserted into the current parsing call and inherit accepted ownership.

   The layering contract also explicitly prohibits graph importing measure/probe. The qualified tool/resource checks and R1 ownership helper currently live in measure. Passing an executable callback into graph or duplicating that preflight would not be the approved fixed composition.

2. **Persisted shared symbol/reference evidence has no declared record.** `measurement-enablement-contracts.json`, `records.ParsedInventory.syntax_artifact_schema`, fixes `SyntaxEvidence` to source/parser bindings, node kind/spans, literal imports, outside-model sites and string diagnostics, and expressly requires a versioned amendment for parser-specific additional fields. `RawMetricEvidence.dead_exports` requires reconstruction from pinned JS symbol/reference evidence, but declares the normalized findings/entrypoints/outside-model payload, not the symbol/reference serialization. `Candidate` and `Finding` are specified; adding symbol tables to either those records or `SyntaxEvidence` would change a public shape. Returning only normalized unused findings would not provide the requested shared symbol proof.

These are implementation-boundary observations, not claims that TypeScript cannot perform the analysis. The qualified installed `typescript.d.ts` was read for `createSourceFile`, `forEachChild`, `createProgram`, `CompilerHost`, `getPreEmitDiagnostics`, `getSymbolAtLocation`, `getExportSpecifierLocalTargetSymbol`, `getExportSymbolOfSymbol`, `getAliasedSymbol` and `getExportsOfModule`. The existing qualification bootstrap already demonstrates six-suffix parsing, checker aliases, UTF-16/byte conversion and controlled library reads. No requalification or package acquisition is needed.

## Smallest requested contract/release

- **Fix the execution lifecycle without new Context fields or roles:** reserve all JS request/result/command/syntax and manifest paths before snapshotting; after exact qualification staging, publish a pre-execution manifest containing real qualification rows and pending-output reservations only. Assign its actual Artifact to Context before a fixed measure-owned JS launch. After production, publish a separately named final manifest with actual generated hashes; switch Context to that reference. Do not overwrite manifests or invent rows/hashes for pending outputs. Specify this same staged/rederived lifecycle for validation, since current `graph.validate_evidence` reparses source without an external execution owner. Keep graph's existing public API and its sole ownership of the final ParsedInventory; no reverse import/callback.
- **Keep existing SyntaxEvidence unchanged:** specify one separate, versioned JS qualified-raw symbol/reference artifact, using an existing ownership role. Its bounded content needs source-bound declarations, export/reexport aliases, lexical references and their targets, public-entrypoint roots, outside-model sites and original TypeScript diagnostic locations; bind it to the same run/revision/inventory/source/parser/tool/settings identities. Existing Candidate/Finding records remain unchanged projections. The exact serialized fields and its owned producer/consumer path need parent release before implementation; this note does not silently define an accepted schema.

An isolated native-only prototype could avoid the caller temporarily, but would not settle the required shared persisted evidence boundary. No placeholder or second parsing front end was created to imply that boundary was complete.

## Evidence and scope

Read the current measurement HTML/contracts, R1 approving review, input-root amendment, actual graph parser/validator, probe lifecycle, qualified TypeScript bootstrap and installed API declarations. A scoped search for `SyntaxEvidence`, symbol schemas and initial/pre-execution manifests in task contract JSON found no additional declared symbol transport. `measure_js.mjs` is not present. The remaining shared JS implementation and all CHECK-JS-PARSER execution are unimplemented in this handoff.

| Inspected file | SHA-256 |
| --- | --- |
| `scripts\measure.py` | `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1` |
| `scripts\measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts\probe.py` | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |
| `.ai\workflow-reliability\measurement-enablement-contracts.json` | `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12` |

Only this additive evidence note was written. No production/tests/shared state/C3-owned files, qualification evidence or tool packages were changed. No agents, installs, root mutants, commits, pushes, symlink privilege retry or old-temp cleanup occurred. No whole-source freeze is claimed. Binding acceptance and prior proof remain historical and unchanged; scalar/coverage/reporting/metric-bridge/recovery work remains deferred.

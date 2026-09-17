# Shared JS execution amendment

**Revision 2, proposal only.** The original measurement contract and accepted root/R1 boundaries remain authority. Parent permission permits proposing one `manifest` role, not implementing it. The accompanying JSON fixes the finite transport and ordering for one shared TypeScript parser, not a new workflow or quality gate.

## Execution and ownership

The existing caller publishes its manifest after graph parsing. That is too late for R1-protected JS execution. The proposed sequence is:

**Reserve and snapshot → stage qualifications → JS preflight manifest → real JS execution → JS produced manifest → graph parsing → final measurement manifest.**

The small produced-manifest step is necessary. Immediately after the child, actual JS bytes exist, but Python/per-file syntax and graph artifacts do not. Graph cannot read those JS records under mere reservations; nor can the final graph hashes be invented early. Three immutable control files solve this without new Context fields: `js-preflight.json`, `js-produced.json`, and existing `manifest.json`. Context points to the appropriate actual Artifact at each phase.

Preflight owns only available qualification rows. Produced owns the actual preflight Artifact with **role `manifest`, revision `null`**, plus real JS request/capture and result/symbol rows. Final inherits that preflight row, adds the actual produced-manifest row with the same role/null revision, and adds successful-file syntax and graphs. All phases share exact reservations; publication copies the admitted materialized set, not every pending slot.

This backward-only chain replaces revision 1's structural-retention exception. Only the active/final manifest retains the existing Context/self-reference rule; retained predecessors have explicit rows. Consumers verify exact phase-specific paths, role/null revision, hash/length, root/run identity, reservations and canonical reconstruction. Final and produced must agree on the same preflight Artifact. Missing, duplicate, foreign, self/forward/cyclic or mislabeled rows reject. Request hashes supplement ownership; they never replace it.

No manifest is disguised as qualification, command capture or numeric evidence. R1's selected qualification set is unchanged. Non-JS Q1 emits the same manifest and five-file controller digest as before; an injected `manifest` row still fails its exact expected-manifest check.

## One producer, one independent replay

Measure owns the fixed Node launch before graph parsing. Graph remains the sole ParsedInventory builder and reads already-produced owned records. It never imports measure/probe, receives executable callbacks, or launches TypeScript. The actual copied `measure_js.mjs` joins the five Python controller files in JS mode, with before/after checks. The default Python-only digest stays unchanged.

For accepting validation, measure privately creates a fresh short run root, stages fresh qualification copies, and repeats the real execution and manifest sequence against the same immutable inventories, subjects and settings. It does not accept a supplied replay Context or copy old results. Graph compares original and replay evidence and rebuilds syntax/graph projections; measure retains the semantic acceptance boundary.

The existing graph validator keeps its Python behavior. In JS-enabled mode, direct use explicitly rejects rather than pretending structural decoding re-executed TypeScript. A private comparison helper returns no metric count; only the fixed measure-owned replay can feed the accepting path. This is consistency checking, not authenticated provenance or sandboxing.

Logical run/revision/source/inventory/parser/tool/settings bindings must match. Physical run paths, fresh execution IDs and invocation Artifact hashes are checked against each actual execution, then excluded only from the explicitly listed transport comparison. Semantic paths remain tagged, root-relative input references. There is no generic path/hash stripping that could hide stale evidence.

## Shared compiler evidence

`SyntaxEvidence`, `Candidate`, `Finding` and the ParsedInventory map stay unchanged. Separately versioned `symbols.json` is accurately owned as parser-produced `syntax`, but is **not structurally SyntaxEvidence**. Consumers dispatch by fixed locator and expected record type, then check its exact field set/version/bindings. Its schema covers census, lexical IDs, exports/aliases/references, target resolution, public roots, outside-model sites and original diagnostics. A valid role cannot excuse the wrong record schema.

Symbols use source-backed lexical/token identities, not TS heap IDs. Candidate edits and findings derive from the same parser output and source bytes. No live AST crosses JSON. Invalid and empty files remain in the census. Point/EOF diagnostic ranges preserve zero width without weakening the existing nonempty Span type. Unrepresentable projections remain unavailable rather than inventing locations.

The qualified compiler host, strict UTF-8/UTF-16-to-byte mapping, six suffixes, package/input allowlist, default-library pins and preload restrictions are retained. Additional scalar, coverage and reporter machinery is not included.

## Focused review and proof

The JSON specifies real production/replay lifecycle tests; rehashed manifest/source/symbol tampering; an effective no-launch audit; controller-file tampering; aliases/cycles/entrypoints; all six suffixes and zero/invalid inputs; Unicode/CRLF/point diagnostics; unchanged Python-only behavior; and actual parser/candidate calls on the existing root targets without executing root mutants.

Review should focus on the three immutable materialization boundaries, the explicit control-file ownership rule, graph’s nonexecuting role, the exact semantic-versus-transport comparison, and the finite symbol schema. No binding acceptance or historical test count is upgraded. The next action is one parent-owned focused independent review, then explicit implementation release.

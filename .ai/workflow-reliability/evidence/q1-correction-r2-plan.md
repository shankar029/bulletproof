# Q1 correction round 2 — F3 binding correction

Parent accepts F3 within the existing parser semantic-binding requirement.
Original r1/r2 verifier source and recursively enumerated evidence were pinned
before edits. The unchanged r2 tests reproduced one failure / one pass in
41.149 seconds; exact commands, raw streams and fixture archives are preserved
under `q1-correction-r2-red*` and `q1-correction-r2-fixtures-red/`.

## Grounded cause and implementation decision

`parser_digest` hashes `sys._xoptions`, but that is not the interpreter's
effective frozen-import configuration. Environment-selected behavior can differ
with the same options dictionary. Conversely, environment or dictionary edits
after interpreter initialization need not change actual import behavior.

The installed CPython `_imp._frozen_module_names()` API was inspected: its
docstring returns the frozen-module census (28 names in this runtime).
`FrozenImporter.find_spec` queries the runtime's effective frozen table without
executing the modules. Bind the complete census and each name's actual effective
availability/package classification, not one sentinel fixture name and not a
manually inferred default or environment flag.

Keep unrelated interpreter options conservatively bound, but replace the raw
`frozen_modules` option with that effective table. Therefore environment/CLI
override, `-E`/`-I`, defaults and already-initialized runtime behavior are resolved
by the same runtime finder used by the graph. Equivalent effective import
semantics have the same frozen binding; distinct tables have distinct bindings.
Version the corrected parser semantic profile. An unavailable/malformed census
fails closed: no partial runtime table is represented as complete.

This is a qualified CPython private runtime API in the already supported managed
runtime, not a new framework or generalized custom-import-hook model. Arbitrary
importer monkeypatching/authenticated runtime identity remains outside Q1.

## Tests and stop

Preserve the original F3 test unchanged. Add real child-process controls for
environment on/off, CLI overrides in both directions, repeated CLI option
precedence, ignored environment, equivalent-mode digest consistency, post-start
environment/option-dictionary edits, and another frozen package name beyond the
original `__hello__` fixture. Check exact effective table and parser identity.
Existing full Q1 public-CLI and receipt tests run afterward, plus legacy probe.

Pin actual repository/runtime/bytecode inputs, capture raw stdout/stderr and
exact argv with additive r2 files, freeze final bytes, then return to the
original verifier and separate review. No C1/shared-state edits or acceptance,
Q2, installation, nested agents, commits, publication or root quality claims.

# Q2 JS execution / symbol transport — independent design review

## Verdict: REVISE

**Bounded Phase 2b review, 2026-09-17. Parent owns disposition.**

The three immutable manifests, one accurate `manifest` role, separate versioned
symbol transport, and measure-owned fresh execution are the right direction.
They resolve the original architectural seams without reverse imports, executable
callbacks, predicted hashes, or a weaker qualification boundary. **Do not release
implementation against revision 2 unchanged:** correct the three small contract
gaps below. None requires a replacement architecture, another tool qualification,
new Context fields, another ownership role, or work on excluded collectors.

This is design/source inspection, not a parser implementation, execution proof,
renewal of historical qualification, full-suite result, or Q2 acceptance.
FACT denotes directly read/observed evidence; INFERENCE denotes the reviewer's
conclusion from it. No exploit or authenticated-producer claim is made.

## Frozen authority and actual tree

FACT: read the **entire 379-line amendment revision 2** and entire rationale.
The three requested authority hashes match. Paths below are relative to
`.ai/workflow-reliability/` unless otherwise stated.

| Input | SHA-256 |
| --- | --- |
| `evidence/q2-js-execution-amendment.json` — 52,890 bytes | `cd69b23bd22c08fe6884fcd5fbb5570d4dd0e5f4551b2f161ce4d0c0da61333a` |
| `evidence/q2-js-execution-rationale.md` — 6,098 bytes | `d79ec098f6d332e204ed87946d7104df6bd65c2c82f58e309cefa5b504f8e130` |
| `measurement-enablement-contracts.json` | `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12` |
| `evidence/q2-tool-input-root-amendment.json` | `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1` |

FACT: actual HEAD is `ce7c07eb4bec9239db4d45cdf9bc83c88a43a16c`.
The scoped Git diff against `dadce66ff7d9a7494db0af5f8124009d7b132cb9`
is empty for all five runtime files below. Their current raw working-byte pins are:

| Repository file | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1` |
| `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts/probe.py` | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e` |

`scripts/measure_js.mjs` does not exist. Initial status also contained parent-owned
`state.md`, the prior `evals/report.md` change, and the three untracked Q2 seam/
proposal documents. Those were not changed by this review. Historical documents
and accepted qualification/review records remain immutable.

## Blocking findings and smallest corrections

### JS-R1 — Plan the base reservations only after the base can be discovered

**P2 / ordering correction.**

FACT: amendment `production_order[0]` (line 94) says to plan exact outputs using
the existing discovery owner, observe head, and then materialize the immutable
base. `paths_and_manifests.reservation_set` (63) requires both revisions' potential
syntax slots before the broad snapshot.

The existing owner is filesystem-based: `measure.code_files(root)` (274–278)
calls `_walk(root)` (215–271), which requires a canonical existing directory and
reads code bytes. The actual caller deliberately materializes base **first**
(`probe.py:530–535`), discovers base plus current head for reservation planning,
then snapshots head (`547`) and copies it (`551`). `_copy_subject` (463–481) uses
the qualified `measure.materialize_baseline(repo, target, revision)` (99–174);
it is not a tree-path-only discovery API.

INFERENCE: the stated new order cannot obtain exact base-only/deleted-file slots
from that existing API. Using head as a proxy loses base-only paths; introducing
a second Git-tree discovery implementation is unnecessary and conflicts with
the single-owner direction.

**Smallest correction:** retain the existing early immutable-base materialization.
Specify: validate config/Git IDs → materialize base once → plan the exact base/
current-head union and metadata/input overlaps → observe head with those exact
exclusions → copy observed head → build/reconcile the immutable inventories.
Keep package/config/approval inputs in the broad source binding, never under a
blanket exclusion. This does not move a JS launch before preflight or weaken
reservation-before-head-snapshot.

**Focused proof after release:** include a base-only Python file and a base-only
JS file, plus changed ancestor package metadata. Assert their exact base syntax
reservations exist before the head snapshot and that neither metadata nor a
source/qualification overlap is hidden. Extend JS-LIFE-01, not a new workflow.

### JS-R2 — The fixed execution signature cannot select the required request purpose

**P2 / explicit private interface correction.**

FACT: the proposed `measure.execute_js(context, inventory, config) -> None`
has three arguments (33). Both production (96) and validation (104) call it.
`JSRequestV1.purpose` is required and must be `produce|validate` (154).
The replay Context retains the same logical identity, subjects, config and
bindings; only `run_root` and `output_manifest` change (103). Both executions
start at the same relative preflight locator.

INFERENCE: there is no specified input distinguishing those purposes at the
fixed launcher. A fresh execution ID is not a purpose. Inferring purpose from
temporary-directory spelling, mutable module state, or a hidden Context key
would introduce an undeclared channel. Always writing `produce` would make the
replay transport untruthful.

**Smallest correction:** state one private execution core with an explicit
measure-owned purpose argument, called with a compiled `produce` constant by the
public production wrapper and a compiled `validate` constant by
`validate_observations`. Alternatively amend the new launcher signature explicitly.
Keep purpose out of user config, environment, command selection and executable
callbacks; validate each request against the purpose known by its actual caller.
The existing public validation signature need not change.

**Focused proof after release:** production and replay requests have the correct
distinct purpose and fresh IDs; a purpose-swapped/rehashed request is rejected
against its own invocation. Extend JS-LIFE-02/JS-OWN-01.

### JS-R3 — Define admission and decoding for actual partial failed output

**P2 / finite failure-state contract correction.**

FACT: lines 65–68 and 46–47 retain actual materialized result/symbol artifacts
and link available failure proof. Line 230 unconditionally requires fixed
result/symbol locators to decode as the exact `JSResultV1` /
`JSSymbolEvidenceV1` schema. Validation starts with strict record decoding
(102), and its comparison expects the semantic records (106,118).
But `failure_behavior.command_failure` (339) specifically allows missing or
partial output after a failed child to yield failed receipts; reproducible
failed executions may support an honest unavailable observation (340).

Concrete design case: the real child writes `symbols.json`, begins
`result.json`, then exits nonzero or times out, leaving truncated JSON.
Its command can truthfully reference both actual files. The result cannot pass
the unconditional schema dispatch. Omitting its existing reserved bytes also
conflicts with the materialized-proof/publication rules unless the contract
defines them as retained nonsemantic failure bytes. The same issue arises when
no result/provenance/symbol record exists at all: the successful comparison
projection has no operand. A controller-authored replacement `JSResultV1` would
not be actual child output.

INFERENCE: the intended failure policy is sound, but revision 2 leaves the
producer, graph reader, manifest reconstructor, replay comparator and archive
publisher with incompatible instructions for this adjacent lifecycle state.
This is not permission to accept malformed output from a successful child.

**Smallest correction:** add one finite admission/consumption table shared by
those consumers, specifying:

- Successful command + valid complete transport: strict schema/census/bindings
  and actual semantic replay comparison.
- Failed command + absent output: null references/no invented rows; derive the
  full failed receipt partition from the immutable inventory and actual capture.
- Failed command + present partial/malformed output: exact-byte references and
  explicit retention policy, but **no semantic decoding or successful receipts
  from those bytes**. If retaining them at the fixed syntax locators is intended,
  state the narrowly command-failure-conditioned dispatch exception explicitly.
- Failed command + valid output: specify whether/which records remain diagnostic
  only; a success-shaped result must not override the failed command.
- Zero-exit malformed/missing/inconsistent transport: invalid proof / exit 2,
  as already required. State the policy for zero-exit stderr as well.

Also define the failed-state replay comparison separately from successful
semantic-record comparison: which actual outcome/reason fields must match,
which already-listed transport fields are checked only within their own run,
and which actual files get archived. No arbitrary hash/path stripping,
manufactured provenance, new role, or weakened success schema is needed.

**Focused proof after release:** real nonzero/timeout children leaving no output,
only symbols, and a truncated result; nonzero with otherwise valid outputs;
zero-exit invalid transport; failed replay versus successful original.
Check ownership, failed receipt census, archive contents and fail/exit-1 versus
invalid/exit-2 behavior together. Extend JS-OWN-01/JS-LIFE-02.

## Other design determinations and compatibility risks

### Ownership and lifecycle: acceptable apart from the corrections above

FACT: the current caller parses before publishing any manifest
(`probe.py:556–574`). The amendment introduces the necessary materialization
boundaries without inventing graph hashes: preflight owns qualifications;
produced owns preflight plus actual JS artifacts; final owns both predecessors
and adds actual syntax/graph artifacts. The active manifest alone retains the
Context self-reference exception. The phase-specific rows, null revisions,
same reservations, exact preflight agreement, and rejection of self/forward/
foreign/cyclic rows are explicit (`manifest_role_extension`, 71–91).

FACT: R1's current `_validate_binding_ownership(manifest, config)`
(`measure.py:901–923`) derives the selected set through `tool_artifacts(config)`,
checks duplicates/namespace partitions before collapsing anything, requires
each exact qualification/null-revision row and reservation, and rejects
unselected qualifications. Its call precedes request persistence and launch
(`926–959`). I read the original R1 finding, the accepting
`joint-cli-binding-code-review-r2.md`, and the real audit/control regression
body (`test_measure_source_bindings.py:265–367`); I did not rerun it.

INFERENCE: adding only `manifest` does not weaken R1 if these phase checks are
implemented as written. Existing `read_owned(context, artifacts, ref, role,
revision)` (`measure_graph.py:480–487`) alone is **not** the new chain validator:
it checks one owned JSON reference, not canonical reconstruction of the whole
phase. Keep the full expected-set checks before dependent reads.

The final publisher must change its current loop over every reservation
(`probe.py:583–596`) to the admitted materialized input set plus active final
manifest, with destination-byte verification and final source/tool rechecks.
Absent failed-file syntax slots remain reserved, not fabricated or blindly copied.
No persistent standalone replay/archived-report authority is promised.

### Replay identity: sound successful-path rule, not byte equality of envelopes

FACT: the semantic projection (110–120) retains source/inventory/revision/run/
parser/tool/settings/policy identities and every symbol/provenance/inline syntax
field. It excludes identified invocation transport only after within-run
validation. The replay root and qualifications are fresh; original immutable
subjects are deliberately reused. This is a fresh execution, not an independent
source checkout or authenticated actor.

INFERENCE: this is narrowly defined enough for the successful path **when
references are checked within their own root and compared by the specified
semantic content**. Do not compare entire original/replay receipt `raw` arrays
or graph raw records byte-for-byte: a result Artifact hash changes with its
execution ID/request, and command/predecessor hashes change too. Conversely,
do not drop all `sha256` fields to force equality. Reconstruct each run's exact
receipt/raw reference lists independently, then compare the declared semantic
records. JS-LIFE-02 should positively demonstrate unequal request/result/
command Artifact hashes with equal semantics and reject a semantically edited,
fully rehashed original. JS-R3 supplies the missing failed-path rule.

### Library APIs and qualified read/settings boundary

FACT: inspected the existing qualification bootstrap
`evidence/q2-tools-source-typescript.cjs:27–60,75–103,143–190`, its recorded
options/results, the actual current Node binding body
(`measure.py:847–891`) and settings construction (`604–625`).
The frozen settings include NodeNext resolution, ESNext target, JSX Preserve,
strict/checkJs/unused/unreachable checks, empty `types`/`typeRoots`, and no emit.
The amendment does not introduce `skipLibCheck`, ambient any declarations,
plugins or automatic external type acquisition.

Read the relevant **installed qualified** declarations, not just API names:
`typescript.d.ts:6230–6290` (checker symbols/aliases/exports/shorthand),
`6910–6950` (diagnostic strings/chains, locations and four categories),
`7348–7382` (CompilerHost), and the search-returned declaration signatures for
`createSourceFile`, `forEachChild`, `createCompilerHost`, `getPreEmitDiagnostics`,
`createProgram` and `resolveModuleName`. The inspected distribution is the
explicit TypeScript root in `q2-tools-source-roots.json`.

Two read-file hash/length checks matched the existing
`q2-tools-source-extracted-pins.json`, whose hash is
`23c3bfa261c02c797d847c134c0131ccebae9ff704cb419d3b0d07c861b4a5af`:

| Qualified file | SHA-256 | Bytes |
| --- | --- | ---: |
| `lib/typescript.d.ts` | `e134052a6b1ded61693b4037f615dc72f14e2881e79c1ddbff6c514c8a516b05` | 588085 |
| `lib/typescript.js` | `3ae902c92cc44dace175c0e69e13a4b0899f6983c6121d76b9ab8dd5795e7675` | 9112572 |

Implementation cautions, not a request for requalification or sandboxing:

- FACT: the actual compiler host factory (`typescript.js:126251–126293`)
  defaults current directory, library location, realpath and directory methods
  to the runtime system. The new virtual/tagged namespace must deliberately
  map those relevant operations, not merely pass a relative root name while
  assuming ambient defaults became virtual. Source/package metadata and pinned
  library resources have different JSInput scopes; same relative spelling
  cannot merge them.
- FACT: its source-file reader (`126213–126227`) catches read exceptions,
  reports through `onError`, and substitutes empty text. Therefore retain
  independent read/decode-failure accounting; an AST or matching hash recorded
  before failed decoding cannot establish successful consumption. The amendment's
  explicit failed census and no-processed-zero requirement is appropriate.
- New virtual-path behavior is implementation work, not already demonstrated
  by the historical physical-path smoke. Unexpected absolute diagnostic text
  is explicitly unavailable rather than sanitized into fake compiler output.
- Keep full selected resource rechecks and observed reads/imports. These are
  provenance/consistency limits, not native-DLL closure, authentication,
  source-execution containment or general descendant-death guarantees.

### Finite symbols, spans, original records and graph truthfulness

INFERENCE from the declared records (122–334) and installed APIs:

- The separate `symbols.json` shape can represent inventory declarations,
  merged lexical identities, aliases/reexports, property/shorthand/type uses,
  local/external/unresolved/dynamic targets, backed public roots and diagnostics.
  It does not misuse a `Finding` or `Candidate` as a symbol table.
- Fixed-locator/schema dispatch is essential: `syntax` ownership does not make
  a program-level record an unchanged per-file `SyntaxEvidence`. Keep
  `ParsedInventory.syntax_artifacts` keyed only by successfully parsed source
  paths, as required by the original contract (`257–265`).
- Source hashes/spans remain freshness identities, separate from lexical symbol
  IDs. Merged/anonymous occurrence descriptors and token ordering need direct
  deterministic assertions; TS heap IDs and whole-file hashes are not lexical
  identities. Preserve alias versus declaration/reference distinctions rather
  than counting a declaration/export marker as proof of external use.
- `JSRange` correctly permits point/EOF diagnostics without weakening `Span`.
  UTF-16-to-byte conversion must reject split surrogate/UTF-8 boundaries and
  preserve BOM/CRLF. Do not serialize empty SourceFile/EOF token nodes into
  nonempty `SyntaxEvidence.nodes[*].span`; empty inputs still have a processed
  census and zero real units. Raw diagnostics remain available when an unchanged
  Finding cannot faithfully represent the location.
- Original TypeScript string messages and message chains need deterministic
  conversion to the declared `JSMessage`; preserve original text/code/category,
  related information and source-less nulls. Do not synthesize compiler codes
  for directives or suppress diagnostics to obtain equality.
- Six-suffix syntax support is credible from existing qualification, but the
  current inventory classifies `.jsx`/`.tsx` as unsupported
  (`measure.py:257–265`). Make the JS-mode classification/receipt relationship
  explicit in implementation tests without changing non-JS inventory/digest
  behavior or claiming JSX runner/coverage qualification.
- Package/config/suite entrypoint origins must be verified against their actual
  JSON values at each revision, including head-only roots and unsupported
  package conditions. Computed namespace access and unresolved local references
  cannot support complete absence-of-reference findings. This transport does
  not itself implement dead-symbol aggregation.
- Literal import/reexport/type-import/unshadowed require resolution must come
  from the same NodeNext program, not the current Python `_resolve`.
  Graph completeness/cycles/rules must be reconstructed from those source-bound
  edges; semantic diagnostics alone do not imply syntactic failure. The current
  graph `_graph`, `_parse`, `_raw` and observation path were read at
  `measure_graph.py:340–413,490–542`.

### Interfaces, cohesion and compatibility

FACT: verified actual definitions and production callers of
`parse_files(context, inventory, config)`, `make_manifest(context, base, head)`,
`validate_observations(context, base, head, config, policy, artifacts,
observations)`, `validate_evidence(context, parsed, config, raw, artifacts)`,
`collect_pair(context, config, base, head)`, `controller_digest(root)`,
and `probe.validate_measurement_report(report, context, base, head, config,
policy, artifacts)` in the source ranges cited above and
`measure.py:392–410,1103–1114,1152–1223`, `probe.py:428–460`.
The new interfaces are proposals, not existing implementations.

INFERENCE: measure as fixed execution/acceptance owner, graph as nonexecuting
projection owner, and one native Program/checker are cohesive and right-sized.
Use small shared pure validation/projection helpers within these owners rather
than duplicating full qualification logic or adding a framework. The five-file
default controller digest remains the existing formula; JS explicitly requires
the sixth copied/executing file, with no existence-based fallback.

The explicit JS rejection by direct `graph.validate_evidence` is a truthful,
intentional restriction: that function currently promises source rederivation
and cannot establish JS semantic execution merely by decoding records. Preserve
its Python path, and route accepting JS validation through measure. Graph parsing
alone must not be advertised as semantic acceptance. The mode is a validated
TypeScript binding even for zero JS inputs, not a guessed file-presence flag.

Existing tools-empty and non-JS Q1 callers must retain manifest shape, paths,
receipt behavior and default digest formula; an injected `manifest` row still
fails exact expected-set validation. This is compatibility of behavior/formula,
not a claim that editing controller source preserves its previous numeric digest.
Review the JS observation semantic-version/command projection as well as raw
graph evidence: current `observations` hardcodes Python semantics and empty
commands (`measure_graph.py:505–512`). Mixed JS observations must be truthful.

## Scope, evidence method and retained diagnostics

No agents/factories, installation, parser prototype, test suite, root mutation,
source edit, commit/publication, symlink/privilege action or old-temp cleanup
was performed. Only this report was authored. The parent state/gates were not
advanced. Root scalar collection, mutation execution, coverage/reporters,
guarded metric attachment, recovery and host work remain excluded and incomplete.

External read-only commands used the supplied managed Python with `-B` through
`scripts/run.py --idle 30 --max 120 -- ...`; Git PATH used the supplied Copilot
Git directory. The successful Git inspection printed actual status/HEAD, the
empty five-file checkpoint diff, working-byte pins and absent JS module.
Compiler-file reconciliation checked only the two files read, not all resources
or a new qualification run. No timeout occurred.

Retained review-tool diagnostics (not product/test failures):

1. Initial PowerShell input listing/hash lookup exited 1 because I looked for
   `evidence/measurement-enablement-contracts.json`. Actual authority is one
   directory higher. Diagnostic: `Cannot find path ...\evidence\
   measurement-enablement-contracts.json because it does not exist.`
   Full initial output remains at
   `C:\Users\shbs\AppData\Local\Temp\1789657483894-copilot-tool-output-12364-0fba49fe-e26e-4814-81ca-a4153f066bba.txt`.
   A corrected read/hash check matched the requested authority.
2. A subsequent optional instruction-file lookup used suppressed missing-file
   errors and returned code 1 with no instruction file output; the independent
   authority hash checks in that call succeeded. `CONTRIBUTING.md` was read.
3. Managed Python compiler-pin lookup exited 1 with
   `FileNotFoundError: [Errno 2] No such file or directory:
   '.ai\\workflow-reliability\\evidence\\q2-tools-source-files.json'`.
   No compiler ran and no file was written. I located and inspected the actual
   `q2-tools-source-extracted-pins.json`, then the corrected bounded lookup
   exited 0 and matched both file hashes and lengths.

**Implementation-start decision:** not yet against the unchanged frozen
revision. Parent should disposition JS-R1/R2/R3 and release the minimally
corrected contract; retain the successful-path design and original authority.
No broad redesign or research restart is recommended. Stop here.

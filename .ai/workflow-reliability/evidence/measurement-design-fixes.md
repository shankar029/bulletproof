# Measurement design correction dispositions

Date: 2026-09-17. **Design revision 2; narrowed independent acceptance pending.**

## Scope and status

**FACT:** This assignment resumed the existing measurement design, not a new Q
pass. Read the current state, full measurement context/research, both design
files, the original review, CONTRIBUTING, and the relevant existing discovery,
metric-policy, mutation-validation, source-binding, runner and test-helper code.
The measurement source hashes below match the original review where that review
provided hashes; its older line references are historical, not new citations.

Only `measurement-enablement.html` and `measurement-enablement-contracts.json`
were revised; this dispositions record is the only added file. The original
`evidence/measurement-design-review.md` was not edited or replaced. No
implementation, tests, analyzer runs, mutation, installations, agents, commits,
publication, project manifest or OS changes were performed. Changing
`workflow_*` implementation files were not read. Parent owns `state.md`, the
narrowed independent acceptance and subsequent shortest-Q1 dispatch.

**FACT — accepted decision supplied by parent:** the NEW policy requires **100%
changed executable lines AND 100% changed decision outcomes under the declared
finite coverage models**. This is an autonomous policy decision, not discovery
of a historical root bar or evidence of human sign-off. The existing whole-change
zero-executable-denominator unavailable/null treatment remains; no synthetic
100% observation. Mutation remains **60%**, deterministic cap **20**, evaluation
remains **0.9**, with existing evaluation null semantics and metric tolerances.

**FACT — provisioning boundary supplied by parent:** skill-owned external
provisioning is authorized for **later Q2 after design review**, not this
correction or Q1. Actual versions/APIs still require qualification. No repository
manifest/framework dependency, root analyzer configuration or OS changes.

## R1–R4 dispositions

All locations below refer to revision-2 JSON keys and the current hashes in the
next section; they do not claim implementation or executed acceptance tests.

| Finding | Disposition and concrete contract correction | Planned acceptance |
|---|---|---|
| **R1 — root directory representation** | **Addressed in design.** `record_notation.types.DirectoryRef` permits `"."` only for directory fields; file/artifact `Path` remains strict and non-root. `MeasurementConfig` source roots and suite cwd use DirectoryRef, resolved against the selected base/head subject root with containment/link/collision checks. `valid_directory_fields_example` gives real root fields (`["scripts", "."]`, suite cwd `"."`, concrete managed-Python argv and test path), explicitly not a fabricated complete qualified-tool config. Inaccessible directory diagnostics cannot authorize traversal. | `CHECK-INVENTORY`: root/nested cwd, traversal and case collisions, file/artifact `"."` rejection and linked paths. |
| **R2 — actual AssertionError origin** | **Addressed in design.** `records.PythonError` records the actual raising frame/instruction offset/span, exception identity, code/source hashes, supported helper chain and runtime qualification. `adapters.python_runner.assertion_provenance` requires the failed bare-assert instruction in unchanged test/helper code or an actually invoked qualified stdlib unittest failure path. An assertion in an ancestor frame is never sufficient. Argument/predicate/message evaluation, same-line calls, `__eq__`/`__bool__` and application rethrows cannot become kills. Ambiguous origin is unclassified. Existing phase/error precedence, unchanged baseline identity and positive complete baseline remain. | `CHECK-PY-CLASSIFICATION`: real negative argument/predicate/same-line application raises alongside genuine body/helper assertions, missing provenance and higher-priority errors. Exact CPython instrumentation is still bounded Q3 qualification, not assumed implemented. |
| **R3 — aggregate validation boundary** | **Addressed in design.** `adapters.aggregate_validation` names `probe.validate_measurement_report(report, context, base, head, config, policy, artifacts)` as the producer-owned publication/acceptance boundary. It composes `measure.validate_observations`, fixed graph/scalar/coverage `validate_evidence` adapters, existing mutation-owner validation extended to v3, and `measure.assess_observations`. Expected base/head inventories, approved policy/tool bindings and an owned artifact manifest are explicit inputs. `RawMetricEvidence` supplies clone/census, function, finding, graph and coverage payloads with qualified raw artifacts. Validators decode raw evidence, reconcile exact receipt/run/revision/source/tool/policy partitions, rederive cycles/rule findings/identity deltas, scalar totals, coverage sets/denominators/outcomes, all nine comparisons and the outer verdict; inconsistent supplied summaries are rejected. Checksums alone are insufficient. Honest incomplete/fail remains representable. No score importer, plugin framework or guard dependency. | `CHECK-RECONCILE`: alter scalar value, coverage denominator/outcome, cycle/finding identity, receipt revision, completeness, comparison and outer verdict in real-produced reports; even updating an artifact hash cannot make inconsistent summaries valid. Cases are assigned to their owning Q1/Q2/Q3/Q4 slices. |
| **R4 — one discovery owner and shared parse** | **Addressed in design.** `adapters.inventory` assigns discovery constants and a single walker to lower-layer `measure.py`; probe imports/reexports `code_files`, never the reverse. `inventory(context, revision, changed_production)` binds the chosen root/Git/source identity; probe passes the existing mutation owner's committed changed-line map without a measure→mutate dependency. Traversal/stat/read failure is unavailable, exclusions are enumerated and no shortened census can establish greenfield. `measure_graph.parse_files(context, inventory, config) -> ParsedInventory` is the sole shared parsing producer. Immutable inventories retain pending parse state; source-bound syntax artifacts and parse receipts carry results. Scalar/coverage/candidate interfaces explicitly receive the shared parsed record. Graph/scalar/coverage modules never import their composition layers; plain validated records introduce no framework. | `CHECK-INVENTORY` plus `CHECK-PARTIAL-PROBE`: standalone imports, zero-import receipts, actual enumeration failure, base/head swap rejection; a configured Python-only Git fixture exposes graph values while all missing required metrics still fail closed. Identity-regression fixtures have at least three base files. |

The HTML overview mirrors these boundaries and the accepted policy. The JSON
contains the detailed normative signatures/schemas. The Q1 validation portion
contains only common binding/receipt/assessment and real Python graph evidence;
it must not import not-yet-added scalar/coverage modules. Later adapters extend
the fixed calls in their own slices, not by adding fake successful records.

## Documentation inspection performed

**FACT:** Read-only inspection used the supplied managed interpreter through the
existing bounded runner:

```text
C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe
  -B -X utf8 scripts/run.py --idle 30 --max 60 --
  <same-python> -B -X utf8 -c <read-only document parsing and SHA-256 inspection>
```

Final inspection exited **0**. JSON parsed with duplicate-key rejection; revision
2 and the four floors (100, 100, 60, 0.9) were observed. The standard-library HTML
tokenizer completed. This is document syntax inspection only: **no tests were
run**, and tokenizer completion does not prove rendering, printed page count,
runtime/API support, measurement correctness or independent acceptance.

## Current SHA-256

Paths are repository-relative. Hashes are of exact bytes after the corrections;
source rows anchor the read-only grounding, not a frozen integrated-tree claim.

| File | SHA-256 |
|---|---|
| `.ai/workflow-reliability/measurement-enablement.html` | `fa7b33541c2952c67e62d5675531de8b0daaa6e00716c8c0909f3e283e1cee2c` |
| `.ai/workflow-reliability/measurement-enablement-contracts.json` | `3eea18cc11522426559c9890e1a4ac7a9de8716495131018b3ce2454691dbff5` |
| `.ai/workflow-reliability/evidence/measurement-design-review.md` (preserved) | `351c553cb0326435e352ee00003cfa146557805f2401db3d055151a214b9f817` |
| `.ai/workflow-reliability/evidence/continuation-measurement-research.md` | `6b83d0a65aa4bf690345db1c543ec0420ccd463aed44a4beb9570d221ea70fdb` |
| `scripts/probe.py` | `993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82` |
| `scripts/mutate.py` | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| `scripts/tests/helpers.py` | `2694cd24dd07b1a6e3ceff7ac2addb7d4fc8bc40ee197f6d3c4206d281bf2068` |
| `evals/lib/score.mjs` | `f157afed1976fd39bc9c2c44728f3993dc01a0cc3152e3f3eaf4a41779cf3fdd` |
| `evals/run.mjs` | `ed07c9884b0f6bd70318d8a3ffef4620553ee4d126d17b7eea65d2bbab87df1d` |

## Return boundary

**Pending:** parent's narrowed independent acceptance, overview rendering/page
count, then shortest Q1 implementation. The original review's later dispatch
qualification reminders (including aggregate coverage/selection preparation
bounds versus the 5,400-second mutation window) remain later-slice work, not
claimed resolved by this narrow correction.

No new quality pass, completed prerequisite Q, release approval, authenticated
producer guarantee or implementation authorization by this designer is claimed.

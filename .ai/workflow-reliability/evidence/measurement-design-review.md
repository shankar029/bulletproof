# Independent measurement-enablement design review

**Verdict: REVISE — bounded contract corrections, not a redesign.**

Date: 2026-09-17. Reviewed the proposed HTML and revision-1 JSON contracts against
`continuation-measurement-research.md` and current metric sources. This verdict is
not implementation authorization, measured quality proof, or release approval.
The parent must explicitly accept the coverage policy, finite analyzer semantics,
and provisioning scope before code. Autonomous continuation authorization does
not by itself turn this proposed policy into an accepted one.

## Scope and evidence

FACT: Read the two design documents and the research note completely; inspected
`scripts/probe.py`, `scripts/mutate.py`, `scripts/evidence.py`, the process runner,
test helpers and relevant measurement E2E tests, `evals/lib/score.mjs`,
the `evals/run.mjs` threshold, CONTRIBUTING, and the metric reference.
No agents, installations, analyzer execution, mutation, tests, publication, or
source changes were performed. No changing `workflow_state`/gate implementation
files were inspected. The only write is this review.

The bounded managed-Python command parsed the proposed JSON and hashed reviewed
inputs; it was not a test or tool-support qualification:

```text
C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe
  -B scripts/run.py --idle 30 --max 90 --
  <same-python> -B -c <read-only JSON parsing and file hashing>
```

Observed exit code: 0. Exact reviewed bytes:

| Input | SHA-256 |
|---|---|
| `measurement-enablement.html` | `35c965be4517ecb003a31a0d329fabbfc2f9b9c1fb2eeefcc4ba18aa9943dcb4` |
| `measurement-enablement-contracts.json` | `6ef7ff120a442abd6b5d924ae46404fda6add3b8550648da45acc0e6f73ea727` |
| `evidence/continuation-measurement-research.md` | `6b83d0a65aa4bf690345db1c543ec0420ccd463aed44a4beb9570d221ea70fdb` |
| `scripts/probe.py` | `993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82` |
| `scripts/mutate.py` | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| `scripts/tests/helpers.py` | `2694cd24dd07b1a6e3ceff7ac2addb7d4fc8bc40ee197f6d3c4206d281bf2068` |
| `scripts/tests/test_measurement_e2e.py` | `7c035a0afa177c811bbe142b5a7b6dc608e8d9ecf283499de83a5ac98657780c` |
| `evals/lib/score.mjs` | `f157afed1976fd39bc9c2c44728f3993dc01a0cc3152e3f3eaf4a41779cf3fdd` |
| `references/quality-metrics.md` | `cec506cd8be2fb54794eddd1b914a64cf2269b21e31d969c7dcbc9d874f6e161` |

Design paths in the first three rows are relative to `.ai/workflow-reliability/`;
remaining paths are repository-relative. Historical base/head IDs in the design
are grounding only. I did not certify the integrated tree, rerun the historical
110-file discovery, or inspect concurrent guard work.

## Required corrections

### R1 — The root directory cannot be represented by the normative path schema

**FACT:** Contracts line 196 forbids empty and dot components in `Path`.
`MeasurementConfig.python_source_roots` and suite `cwd` use that type
(214–216), while the Python graph explicitly needs both `scripts` and repository
root (430). Current `select_test_run` serializes repository-root cwd as `"."`
(`scripts/mutate.py:172–227`); the planned root discovery commands require it too.

**INFERENCE, high confidence:** Strict validation of the proposed schema rejects
the intended root configuration. Weakening all artifact paths to accommodate it
would unnecessarily weaken a different boundary.

**Bounded correction:** Introduce `DirectoryRef = "." | Path` only for source
roots and cwd, with canonical resolution against the selected subject root.
Retain strict non-root `Path` for files/artifacts. Provide one concrete valid
root config and tests for root cwd, nested cwd, traversal, and case collisions.

### R2 — Assertion-site membership does not establish the origin of an AssertionError

**FACT:** `PythonError.assertion_site` stores file/line/kind/hash (374).
The provenance algorithm requires an AssertionError and a traceback site matching
the parsed assertion inventory (502). It prohibits application-raised assertions,
but does not specify how to distinguish these cases:

```python
self.assertEqual(application_call(), expected)
assert application_predicate()
```

**INFERENCE, high confidence:** If either application call raises AssertionError,
the unchanged test's assertion line is on the traceback even though the test
assertion did not fail. Body phase and a test-rooted call chain do not resolve
this ambiguity. A same-line application call followed by an assertion is another
case where file/line matching is insufficient.

**Bounded correction:** Require evidence of the actual raising instruction/frame:
a failed Python assert instruction in unchanged test/helper code, or a qualified
stdlib unittest assertion failure path from an actually invoked supported
assertion helper. Mere presence of an assertion expression in an ancestor frame
must not suffice. Record the necessary instruction/span provenance and fail
unclassified if it cannot be established. Preserve the existing phase/error
precedence and positive baseline requirements.

Add real negative fixtures for application AssertionError during assertion
argument evaluation, bare-assert predicate evaluation, and same-line calls,
alongside genuine helper/body assertion kills. Exact CPython instrumentation is
a bounded qualification task; the required origin distinction is a design
correction, not a demand to implement a particular private API now.

### R3 — Aggregate observations lack an explicit producer-owned validation boundary

**FACT:** Mutation has candidate regeneration, result reclassification, count
reconciliation and `validate_mutation_results` (contracts 510–519, 591;
current `scripts/mutate.py:377–426`). Scalars/coverage/graph instead expose
`reconcile(observation, inventory) -> Observation` (419), general receipt
invariants (289–308), and a promise to update strict internal validation (540).
There is no comparably explicit aggregate validation contract. Current
`probe.assess_report` trusts supplied measured/comparison states after limited
numeric checks (`scripts/probe.py:444–466`); it is not that validator.

**INFERENCE, high confidence:** The proposal leaves unspecified which producer
recomputes aggregate values, completeness and final comparisons from the raw
evidence, rather than accepting internally supplied summary fields. Hashing an
artifact proves byte identity, not agreement between its observations and its
claimed score. The prohibition on CLI score import is necessary but insufficient.

**Bounded correction:** Specify a producer-owned validator invoked before report
publication/acceptance, with explicit context, base/head inventories, approved
policy/tool bindings, and owned artifact manifest as inputs. It must:

- reconcile exact receipt partitions, run/revision/source/tool/policy identities;
- rederive graph cycles and architecture findings/identity deltas from the
  validated graph and approved rules;
- rederive scalar totals and coverage numerators, denominators and outcome
  checks from validated adapter evidence;
- derive complete/unavailable states, all required metric comparisons, and
  the outer verdict, rejecting inconsistent supplied summaries.

Define the raw record or qualified artifact schema carrying each necessary
quantity; validators may dispatch to metric-specific adapters. Do not introduce
an arbitrary report/score importer or a dependency on guard validation. Extend
CHECK-RECONCILE beyond mutation: alter a scalar value, coverage denominator,
cycle identity, receipt revision and final comparison in real-produced reports
and require rejection. This is consistency/source validation, not authenticated
producer identity or sandboxing.

### R4 — Finish Q1's shared inventory/parsing dependency contract

**FACT:** Q1 puts inventory/orchestration in `measure.py` and parsing in
`measure_graph.py`, consumed by probe. The algorithm says to enumerate using
`code_files` (421), but that function and its discovery constants currently live
in `probe.py:35–39,103–111`. `parse_files(context)` returns `Graph` (427),
while the scalar adapter consumes `ParsedInventory` (records 241–249 and
adapter line 445); no API owns production of that shared parsed record.
The current discovery walk also has no `onerror` callback.

**INFERENCE, high confidence:** Importing probe to reuse discovery from measure
would reverse the advertised dependency and risk a cycle; copying discovery
would allow divergent inventories. The shared-parser handoff is incomplete.
Literal reuse of the current walk can silently omit an unreadable directory
before any per-file receipt exists.

**Bounded correction:** Name one lower-layer owner for discovery constants and
enumeration, used by probe without a reverse import. Make the revision/root
input and parsed-inventory return type explicit, so base/head collection and
later JS/scalar adapters consume the same file hashes and syntax records.
Retain existing deliberate skip semantics, but make traversal/I/O failure
unavailable and enumerate exclusions rather than accepting a shortened census.
No new general framework is needed.

Q1 should include tests that its modules import standalone, zero-import files
retain receipts, failed enumeration cannot pass, and base/head identities cannot
be interchanged. This is a contract amendment to the proposed modules, not a
request to implement later-language analyzers in Q1.

## Assessment of the requested concerns

| Concern | Assessment |
|---|---|
| Complete inventory and base/head identities | Sound intent: every current `code_files` input, tests/examples/benchmarks included; unsupported languages retained; broad source/contracts snapshot; immutable Git IDs; committed changed-production diff. R3/R4 complete the executable reconciliation boundary. Final measurement must re-enumerate the integrated frozen tree, not reuse the historical count or head. |
| Static graph semantics versus claims | Acceptable declared model: literal imports, type imports explicitly counted, canonical elementary directed cycles, identity comparison rather than count alone, unresolved locals unavailable, dynamic sites disclosed. It does **not** prove runtime independence or arbitrary command safety. Keep that qualification adjacent to architecture results. |
| Python phase-aware assertion proof | Phase wrappers, module/class/setup/teardown/cleanup handling, subtests, full positive baselines and failure precedence address the research correctly. R2 is needed to prevent body-phase application errors becoming kills. |
| Parser-backed JS mutation | Appropriate AST/token approach, byte/UTF-16/CRLF conversion, executable contexts, templates/regex exclusion, syntax preflight and candidate regeneration. Actual parser API and TypeScript execution/source-map support remain qualification work; no installed capability is assumed. |
| Stable controller and self-measurement | Correct separation of controller from target, subject-derived test paths, controller hashes before/after children, all new producer/controller code eligible, exact output ownership and competing-edit preservation. Existing E2E evidence writes demonstrate why the sink refactor is necessary. Do not exempt all `.ai` or test the stable reporter instead of its mutated subject copy. |
| Candidate budget and test selection | Correct: one eligible candidate per changed line, deterministic spread capped at 20, complete eligible/unsampled partition, coverage selects tests only, uncovered candidates retained, conservative suite fallback, survivor full confirmation. “Complete” describes the classified sample, not exhaustive mutation. |
| Test-duration bounds | Correct direction: empirical baselines, explicit per-command bounds, 5,400-second mutation ceiling, preflight cost estimate and approved revision rather than silently reducing candidates. No speedup or fit is proved. See dispatch clarification below. |
| Aggregate report validation | REVISE per R3. Preserve producer-owned canonical validation; do not delegate ordinary consistency to the guard or accept imported numeric summaries. |
| Existing thresholds | Preserved: mutation 60% (`probe.py:293`, mutation assessment); evaluation 0.9 (`evals/run.mjs:36–43`), including existing null behavior (`evals/lib/score.mjs:174–204`). These are different populations and cannot substitute for each other. |
| New coverage policy | Correctly marked an unconfirmed recommendation: 100% changed executable lines **and** changed decision outcomes. Parent must explicitly accept or revise both, their finite coverage models, and zero-denominator treatment before implementation. It is not an established root bar. |

## Q1 disposition and dispatch boundaries

**INFERENCE: Q1 is the shortest credible standalone vertical slice, after R1,
R3's Q1 portion, and R4 are settled.** Inventory, Python AST literal-import
graph, cycle identity comparison and the five declared architecture rules fit
the proposed measurement module boundaries. Probe is the composition/verdict
layer; evidence/run remain foundations. No coverage, external scalar tools,
Python mutation runner or JS parser installation belongs in this first slice.

Use an explicitly configured real Python-only Git fixture to expose actual
cycle/architecture values through the public probe while all other required
metrics remain present and unavailable/fail. For identity-regression fixtures,
use at least three base code files so the existing greenfield rule does not
replace the intended baseline comparison. The mixed repository must remain
incomplete until later adapters exist.

This slice does not need C1's workflow state/gate code or ledger APIs. It may
enforce a path-level rule forbidding measurement imports into guard modules
without importing those modules. Parent should reserve Q1's proposed files and
serialize any shared probe/test-helper/document edits. I have not verified
concurrent ownership beyond the user-provided C1 boundary.

Before Q3/Q4 execution dispatch, spell out whether the 5,400-second budget starts
before coverage and selected clean-baseline qualification or after them. Give
coverage/unit-baseline collection its own aggregate ceiling if outside it, and
include syntax preflight, subject preparation and restoration allowance in the
schedule. Per-unit caps alone do not bound a many-unit coverage pass. Count full
survivor confirmations at their actual compatible-suite bounds. If the schedule
does not fit, request a bounded budget revision; never drop the tail or reinterpret
timeout as survival. This is a dispatch clarification, not proof that the design
is infeasible.

Graph qualification should cover Python package initializers, namespace packages,
local-vs-stdlib name shadowing, and known-external versus unresolved local imports.
State exactly which initialization dependencies the finite literal-import model
includes. Missing installed API details, jscpd census schema, Windows child
coverage flushing, and V8 branch-counter mappings are named qualification tasks,
not independent reasons to reject the architecture.

## Parent decision

1. Amend R1–R4 in the design/contracts; do not implement from this review alone.
2. Record explicit policy/semantic/environment acceptance, including both new
   100% coverage floors or their consciously revised replacement. Keep 60%/0.9.
3. Dispatch only the bounded Q1 slice first, with the dependency ownership and
   producer validation boundary fixed. C1 may continue independently.
4. Qualify tools and execution bounds before the later adapter slices, and freeze
   all integrated inputs before final self-measurement.

No code edits or further execution are requested from this reviewer. Review stops
here; Q remains unpassed.

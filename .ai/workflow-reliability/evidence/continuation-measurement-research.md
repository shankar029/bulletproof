# I1 quality closure: bounded continuation research

## Scope and observation

Research only, 2026-09-17; inspected HEAD `aaec9b9851a9ce8f778943c5c088d6c4442e36f8`,
base `bcc971d3b64559127dfc43eb0bfd4348c42803ca`. Read CONTRIBUTING and the existing
design/contracts/tasks/state. No installations, tests, analyzer runs, mutations,
main-checkout operations, publication, or nested agents. Only this note was written.
Local executable probes used the supplied managed Python with `-B`, through
`scripts/run.py --idle 30 --max 90 -- COMMAND`. Public documentation was read, not
treated as proof of an installed version.

**Bottom line:** installations alone cannot close I1. Required collector implementation,
mixed-language inventory support, classified Python mutation, and parser-backed JS
candidate discovery are missing. The existing report correctly fails; no threshold
waiver or missing-as-pass interpretation is proposed.

## FACT: current evidence and actual scope

- The retained `metrics.json`, run `3ad8da4bb8134928b5ced2b19beff903`, records
  `head=dde2b491...`, `baseline=compared`, empty `tools`, all nine required metrics
  unavailable, `completeness=incomplete`, `verdict=fail`. Its mutation stopped on dirty
  `.ai/workflow-reliability/.gitattributes`. This is **historical**, not fresh proof
  for committed `aaec9b9`. Source: `.ai/workflow-reliability/metrics.json`, fields
  `run_id`, `head`, `metrics`, `commands`.
- Read-only canonical discovery on current HEAD found **110 code files**:
  10 Python, 45 MJS, 53 TS, 2 JS. `code_files` includes tests, benchmarks and examples,
  not just I1 production. The changed-production-line inventory is:

  | File | Added/modified lines selected by `changed_lines` |
  |---|---:|
  | `scripts/evidence.py` | 172 |
  | `scripts/mutate.py` | 452 |
  | `scripts/probe.py` | 331 |
  | `scripts/run.py` | 32 |
  | `scripts/native_result.mjs` | 142 |
  | `evals/lib/score.mjs` | 19 |

  Counts are Git changed lines, **not executable-line coverage or mutant counts**.
  Sources: `scripts/probe.py:35-39,103-111`; `scripts/mutate.py:90-111,230-254`;
  bounded invocation of those discovery functions.
- I1 also changes Python tests, native reporter/scorer tests, and
  `benchmark/projects/csv-stats-cli/bulletproof/cli.test.ts`. Actual Python inventory:
  `scripts/tests/test_{evidence,mutate,probe,run,measurement_e2e}.py`, using stdlib
  `unittest` and real filesystem/Git/child-process fixtures. Root has no
  `package.json`, `pyproject.toml`, `setup.cfg`, `pytest.ini`, or root native test files.
  Automatic test selection at root therefore cannot supply the required suites.
  Sources: I1 `git diff-tree --name-only`; `scripts/tests/helpers.py`;
  `.ai/workflow-reliability/tasks.json:83-138`.
- Existing functional commands are Python `-B -m unittest discover -s scripts/tests -v`;
  Node `--test evals/lib/mutate.test.mjs evals/lib/score.test.mjs
  evals/agent/agent.test.mjs evals/lib/native_result.test.mjs`; and `node evals/run.mjs`.
  **Not run here.** Prior full Python evidence took about 705 seconds, so a 90-second
  research budget cannot validate it; production runs need the separately approved
  task bounds. Sources: tasks command registry; `state.md` independent R1/R2 checkpoint.

## FACT: blockers by collector

| Required measurement | Exact implementation blocker | Smallest credible design input |
|---|---|---|
| Diff coverage | No collector or import path; inserted as unavailable. Default policy supplies no numeric coverage rule. | Collect real Python and Node coverage, reconcile every changed production executable line, then apply an explicitly approved coverage/branch policy. |
| Architecture rules | No collector, executable rule set, or metric comparison rule. | Version a small rule set from the approved current design; evaluate actual parsed dependencies with violations and checked-input inventory. |
| Duplication | `m_duplication` reads jscpd's percentage, but `_scope_support` **never adds any supported paths** for this metric. | Parse a verified jscpd input inventory, including scanned files with no clones; clone pairs alone cannot prove coverage. Retain counts, denominator and raw report. |
| Complexity max/average | Missing lizard. Inventory is inferred only from function CSV rows. Functionless modules can be analyzed yet have no row; `.mjs`/TS support is unverified. | Verify installed parser/extension handling; separately record successfully parsed files and their function counts, including zero-function files. Do not label files supported merely by extension. |
| Cycles | Madge is JS-family only; current inventory always leaves 10 Python paths unsupported. JS support is inferred from extension/target roots, not actual successful resolution. | Combine a Python import graph with a verified JS/TS dependency graph; retain unresolved/dynamic edges explicitly and compute cycles across the declared graphs. |
| Dead exports/code | No root package means knip branch is not selected. Vulture alone leaves 100 JS-family paths unsupported. | Run language-specific collectors with explicit entrypoint/config ownership; combine finding inventories without dropping either language. Vulture output is not JS dead-export proof. |
| Static findings | Missing semgrep; current `--config auto` needs registry/rule resolution, and report must have no errors plus a complete `paths.scanned` inventory. | Pin supported rules/tool version and inventory for Python/MJS/TS/JS at base and head; verify platform support. Missing language/rule support remains incomplete. |
| Mutation | Native-only runner/validator, Python rejected; additionally both changed MJS files trigger conservative ambiguous-syntax exclusions. | Extend the existing engine with structured unittest classification and syntax-aware candidate adapters; reconcile language partitions into one complete proof. |

Sources: `scripts/probe.py:137-261` collectors; `:282-292` collection;
`:302-375` mutation consumer; `:436-466` required policy/verdict;
`:485-523` support inventory; `:580-650` base/head collection and unavailable insertion.
Mutation sources: `scripts/mutate.py:172-227,273-326,329-426,497-594`.

**Important integration detail:** adding two numeric keys to `collect()` is insufficient.
`judge()` only knows the current compare/greenfield rules; its generic higher-is-better
fallback is wrong for architecture violations, and a missing base would make a coverage
value unavailable. Define explicit coverage-floor/branch and architecture-no-new-violation
decisions; preserve current mutation 60%, tolerances and eval 0.9 policy. Compare
architecture violation identities, not only counts that could hide a new violation
behind removal of an old one. Sources: `probe.py:379-442`;
`references/quality-metrics.md`, “The gate”; `design-contracts.json:268-271`.

## FACT / UNKNOWN: installed options and evidence formats

**Observed:** managed Python 3.14.2, Node 24.11.1, npm and uv available. In that Python,
`find_spec` found none of coverage, pytest, lizard, vulture, semgrep, radon, mutmut,
diff_cover, cosmic_ray, importlinter or bandit. PATH lookup found none of jscpd, lizard,
vulture, semgrep, knip, madge, depcruise, diff-cover, mutmut or cosmic-ray. This does
not establish that no other environment on the machine contains them.

### Coverage

- **Achievable with existing Node:** help confirms `--experimental-test-coverage`,
  coverage include/exclude and threshold flags, reporter/destination flags and
  `NODE_V8_COVERAGE`. Importing `node:test/reporters` confirms an `lcov` export.
  Candidate execution, **not run**:
  `node --experimental-test-coverage --test-reporter=lcov
  --test-reporter-destination=<owned-run>/node.lcov --test <four explicit native files>`.
  Retain test completion proof separately; a coverage file alone is not green tests.
- **Recommended Python prerequisite:** an authorized skill-owned coverage.py environment,
  version-verified for Windows/Python 3.14. Candidate sequence after its help is checked:
  `python -m coverage run --rcfile=<owned-config> -m unittest discover -s scripts/tests -v`,
  then `coverage combine`, and JSON/XML reporting into invocation-owned artifacts.
  Configuration must include absolute source/data paths, branch coverage and subprocess
  collection. Upstream documents `patch = subprocess` with parallel data/combine.
  This matters because Python tests repeatedly launch `probe.py`, `mutate.py` and
  `run.py`; wrapping only the parent misses those CLI paths. Verify real child data,
  environment overrides and intentional timeout cases rather than assuming propagation.
  Source: [coverage process documentation](https://coverage.readthedocs.io/en/latest/subprocess.html).
- **Existing stdlib alternative:** `python -m trace --count --module unittest ...`
  is available; help confirms `--coverdir`, `--file`, `--missing`. It is not drop-in
  branch/subprocess coverage. Building its child propagation, denominator and normalized
  report adapter is likely more custom work than coverage.py.
- diff-cover accepts Cobertura/Clover/JaCoCo XML and LCOV, with compare-branch and JSON
  report support upstream. Its installation does **not** generate coverage or prove that
  omitted source files were scanned. Normalize paths across base/head, merge language
  line sets (not averaged percentages), account for unimported changed files as uncovered
  or explicitly unsupported, and bind inputs/outputs to the run.
  Source: [diff-cover documentation](https://github.com/Bachmann1234/diff_cover).
- **UNKNOWN:** actual coverage values; installed-version subprocess behavior; an existing
  numeric root coverage bar. Inspected policy/tasks specify meaningful new branches,
  not a numeric root target. Parent must approve a concrete check—recommended all changed
  executable lines plus explicit changed/error-branch assertions—before implementation,
  without pretending this recommendation is already an established percentage.

### Mutation: Python alone is not the only missing adapter

Read-only `build_mutants(..., 20, unsupported=...)` produced 20 sampled candidates:
9 in probe, 1 evidence, 10 mutate. **None were executed.** Discovery separately emitted
16 ambiguous-syntax records for `evals/lib/score.mjs` and 124 for
`scripts/native_result.mjs`. File-wide comment/template and per-line slash heuristics
reject real changed MJS code; merely installing a Python tool cannot fix that.
Sources: `mutate.py:273-326`; bounded discovery observation.

1. **Recommended lowest additional runtime-dependency option:** extend the current engine,
   not a second orchestration framework. Add a Python AST/token-aware candidate adapter,
   syntax preflight via `compile()` without execution/pycache, and a structured stdlib
   unittest reporter. Add parser-backed JS token/range selection to avoid mutating
   comments, templates or regex literals while supporting these actual files. The exact
   JS parser/version remains a prerequisite, not an installed capability.
2. Python reporter must preserve test identity, subtests, exceptions/tracebacks and
   test-versus-setup/teardown/cleanup phase. A bare `TestResult.addFailure` event is
   insufficient: inspection of Python 3.14's `TestCase.run` shows setup and teardown
   execute through the same outcome machinery. Require actual assertion provenance
   in the baseline test body; missing inventory, skipped/expected failures, setup/import/
   syntax errors and timeouts remain ungraded. Do not manufacture Node `ERR_ASSERTION`
   fields for Python. Version the runner-specific proof and consumer validation together.
3. Reuse `select_test_run`, canonical candidate regeneration, source hashes, locking,
   restoration and same-invocation report ownership. Extend `mutation_entry` and
   `validate_mutation_results`, which currently insist on Node/JS, rather than importing
   an external score. Partition suites by language and preserve candidate/unsupported
   inventories before sampling. A deterministic cap of 20 is a sample, not exhaustive
   mutation coverage; retain the approved cap and expose distribution/omissions.
4. **mutmut option:** upstream currently requires fork support, hence **WSL on Windows**;
   it uses pytest and project-style configuration and notes a different execution model
   for mutations outside functions. It is not available in this managed Python, nor a
   native-Windows drop-in. No WSL/runtime compatibility was verified. A qualified external
   environment plus assertion-evidence adapter would still be needed; covered-lines-only
   filtering cannot silently erase untested changed lines.
   Source: [mutmut requirements/configuration](https://mutmut.readthedocs.io/en/latest/).
5. **Cosmic Ray option:** upstream documents unittest test commands, explicit TOML config,
   local execution and SQLite sessions with candidate/results records. It is a plausible
   external candidate generator/runner, not confirmed Windows/Python-3.14 support.
   Ordinary failure/timeout scoring cannot replace this project's classified assertion
   contract. Diff selection, fresh session/config binding, syntax/outcome classification
   and restoration need an adapter.
   Source: [Cosmic Ray tutorial](https://cosmic-ray.readthedocs.io/en/latest/tutorials/intro/index.html).

Eval's `runTestQuality` does not close this gap: it mutates fixture arms, not these six
production paths, and its score excludes ungraded outcomes. `runQuality` is configured
source-pattern/extension-oracle checking, not a root architecture/coverage collector.
Keep its valid, separate regression policy intact. Source: `evals/lib/score.mjs:63-204`.

## Proposed minimal interfaces and dependency sequence

These are **design inputs, not implemented APIs or approved scope changes**:

- `collect_coverage(context, test_runs) -> CoverageObservation`: per-file executable,
  covered, missing lines/branches; complete test inventories; runtime/config/source hashes.
- `collect_dependencies(context, language_adapters) -> DependencyObservation`: parsed
  files, resolved edges, unresolved constructs, cycles, rule IDs/violations.
  `evaluate_architecture(graph, rules, base_graph) -> Measurement` can enforce existing
  measurement independence **without implementing the guard**. Current imports are
  probe -> mutate/evidence/run; mutate -> evidence/run; evidence/run -> stdlib;
  scorer -> native reporter. Rules need parser-backed checking and explicit handling
  of cross-runtime child commands, not regex-only import-name searches.
- Language adapters should expose `discover_candidates(scope)` and
  `execute_tests(test_run) -> RunnerEvidence`; the existing mutation engine owns
  orchestration, freshness/restoration and aggregate validation.
- All observations need tool version, exact argv/cwd/bounds, config/rules hash,
  raw artifact hash, base/head source binding, scanned/unsupported file inventories,
  typed non-finite-safe values and incomplete reasons. Reuse `evidence.py` and the
  existing metric envelope rather than introducing receipts/guard dependencies.

**Order:**

1. Parent approves a bounded measurement-enablement design/plan addition, explicit
   coverage/architecture rules, tool environment and supported file/language contracts.
   Preserve all required metrics and existing thresholds.
2. Establish pinned tools and real tiny positive/negative collector fixtures. Implement
   inventory reconciliation (including zero-findings/zero-function files), then
   coverage and architecture collectors plus runner/candidate adapters.
3. Add real regression/E2E tests for omitted files, malformed/stale evidence, child
   coverage, Python setup assertions, subtests, JS templates/regexes, invalid mutants,
   unsupported scope and competing edits. Keep negative fail-closed tests green.
4. Freeze inputs before measurement. Current mutation requires clean Git status; the
   snapshot also observes unrelated `.ai` evidence. Do not run parallel docs/evidence
   writers during collection. Declare only exact invocation-owned new output paths
   before hashing; a broad `.ai` exclusion would reintroduce the reviewed freshness bug.
   Nested tests create subprocesses and fixtures: verify they execute the intended
   target bytes while the measurement controller remains stable during self-mutation.
5. Run actual base/head metrics and whole-change classified mutation, resolve measured
   regressions/survivors, then fresh independent verification/review. New collector code
   also belongs in the changed inventory; no collector exemption. Only complete accepted
   proof closes I1.T4 under the existing plan. No success prediction is supported today.

## Planning dependency diagnosis

**FACT:** `tasks.json` I1.T3 explicitly excludes fabricated collectors/installation;
I1.T4 requires complete C-PROBE; I2.T1 depends on I1.T4.
`tasks.json:612` and `design-contracts.json:39,271` explicitly leave required collectors
outside accepted scope. The plan thus created a **self-imposed missing-prerequisite
dead end**: it demands capabilities that none of its scheduled implementation tasks
delivers. This is not evidence of a code-level circular import or a real need to build
the guard first; `state.md` Gate 2 and actual imports establish measurement independence.

Correct remedy: explicitly add/design the missing measurement work before the quality
closure gate (or obtain an explicit user-approved sequencing revision while keeping
I1 quality blocked). Do not silently advance, remove requirements, or present the
functional preservation commit as quality closure. Re-running the unchanged probe,
installing tools alone, or importing corpus scores cannot satisfy the current contract.

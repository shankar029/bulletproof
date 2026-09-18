# Reference: Deterministic Quality Metrics

Instructions alone cannot prove that code is maintainable — they can only ask for it. This
probe measures it. **Where a metric exists for a rubric dimension, the score must cite the
metric.** No number, no score.

## The rule about tooling

The "don't introduce tooling the project doesn't have" rule applies to **the repository's own
dependencies** — you still never add a framework, library, or config file to the project that
the task doesn't require.

**Analysis tools are different: they belong to the skill, not the repo.** They are installed
once, globally, on the user's machine, run from outside the project, and write only to
`.ai/<slug>/`. They must never appear in the repo's manifests, lockfiles, or config, and never
be committed. If a tool insists on a config file, generate it under `.ai/<slug>/` and pass it
with an explicit flag — never at the project root.

## Installing the toolchain (once per machine)

Install what the languages you work in need. Record what is present; anything missing is
reported as `unavailable`, never as a pass.

```bash
# language-agnostic core
npm  install -g jscpd                 # copy/paste duplication, many languages
pip  install --user lizard            # cyclomatic complexity, many languages
pip  install --user semgrep           # static analysis / security rules
pip  install --user diff-cover        # coverage restricted to changed lines

# JavaScript / TypeScript
npm  install -g dependency-cruiser madge knip @stryker-mutator/core

# Python
pip  install --user radon vulture bandit import-linter mutmut

# Go / Rust / JVM / .NET: prefer the ecosystem's standard analyzers
# (e.g. staticcheck, clippy, PMD/CPD + ArchUnit, Roslyn analyzers) installed the same way —
# globally, outside the project.
```

**Verify before use.** Run `<tool> --help` and confirm the flags you intend to use exist in
the installed version. Never invent a flag (prime directive 1 applies to tools too).

## What the probe measures

| # | Metric | Answers | Typical tool |
|---|---|---|---|
| 1 | **Mutation score** on changed lines | Do the tests actually assert anything? | `scripts/mutate.py`, classified native Node tests; other runners remain unclassified |
| 2 | **Diff coverage** | Is the new code exercised at all? | diff-cover, or the repo's coverage report |
| 3 | **Cyclomatic / cognitive complexity** of new & changed functions | Is any unit too tangled to maintain? | lizard, radon |
| 4 | **Duplication** introduced | Was logic copy-pasted instead of reused? | jscpd, CPD |
| 5 | **Dependency cycles** | Did the change tangle the module graph? | dependency-cruiser, madge, import-linter |
| 6 | **Architecture rule violations** | Was a layer or boundary bypassed? | the repo's fitness rules, if any |
| 7 | **Dead code / unused exports** introduced | Did it leave debris? | knip, vulture |
| 8 | **Static findings** (lint, types, security) | Obvious defects and unsafe patterns | repo's linter, semgrep, bandit |
| 9 | **Diff size** — files and lines changed vs planned | Scope creep | git |

Metric 1 is the important one. Coverage says a line ran; a mutation score says a test would
have *caught* it being wrong. It is also the hardest metric to fake without writing real
assertions — which is exactly why it is worth the runtime.

This table is the required proof policy, **not a list of universally supported collectors**.
The configured measurement path supports Python literal-import graphs and their declared
architecture rules. A source-bound, validated TypeScript binding additionally selects the
qualified six-suffix JS/TS graph path described below. Dynamic imports and reflection remain
disclosed outside the literal-import model, not resolved by executing the source.
Diff coverage and the remaining measurement adapters are still
incomplete; installing their tools alone does not close those gaps. Missing collectors, unknown baseline
comparisons and partially supported file scopes make required proof **incomplete**.
Discovery includes `.mjs` and `.cjs`; that does not establish that every external analyzer
supports those files. Numeric partial observations remain visible but are not complete proof.

The shared-JS parser uses the
qualified TypeScript 5.9.3 program/checker for six-suffix census, strict byte coordinates
and original diagnostics. `serializeProgram` returns unchanged per-file SyntaxEvidence
and separate symbol/reference records, including source-backed entrypoint origins.
`candidatesForProgram` reuses that Program and syntax with the matching head Inventory
to enumerate unsampled byte-exact edits; it never writes or executes mutants.
The native module also accepts one absolute `JSRequestV1` path when executed with the
qualified Node runtime. It checks request/config/input/qualification/controller bindings
and preflight ownership, then exclusively writes source-bound result and symbol records.
It does not execute subject code or publish graph artifacts or metric scores.
`measure.execute_js` invokes that fixed command with a production purpose. Before
graph consumption, immutable `js-preflight.json` and `js-produced.json` bind the
qualifications, actual request/capture and generated records. The final manifest owns
both predecessors and only materialized syntax/graph evidence. Reservations are
planned from the actual immutable base and current head before the head snapshot;
deleted/base-only inputs and ancestor package metadata participate.

Full accepting validation belongs to `measure.validate_observations`: each call
allocates fresh independent validation storage, stages the selected qualifications,
executes both revisions with the private validation purpose, and compares all semantic
symbol, syntax, provenance, receipt and graph records. Graph readers never spawn the
compiler and graph-only `validate_evidence` rejects this mode instead of claiming
semantic acceptance from rehashed JSON. Report publication archives only owned,
materialized records after replay and source/tool/controller rechecks.

Nonzero command outputs are diagnostic-only: optional result/symbol files remain
opaque bytes, never successful parser evidence. A matching fresh failed replay can
establish only an unavailable observation, including when there are zero JS files.
Zero exit with any stderr, missing/malformed output or inconsistent provenance is
invalid proof and produces no measurement report. Both native production and replay
retain idle 30-second / maximum 90-second bounds; subjects are never executed.

The mode requires the existing explicit TypeScript 5.9.3 / Node 24.11.1 ARM64
qualification and accessible, source-bound original resources. It does not discover
or install an ambient compiler. Explicit `js_entrypoints` bind named public exports
and an origin reference; package and registered native-suite roots retain their
actual source origins. A head-only declared root is absent at base, not fabricated
as a parsed file. Empty/default configs keep Python-only manifests, the five-file
controller digest and unsupported-JS receipts; JS mode requires all six fixed
controller files and classifies JSX/TSX before inventory hashing.

This is graph integration, not complete JS quality support. Pending classification,
symbol/function/token records and replay are not scalar collection or coverage proof.
Scalar collectors, coverage, mixed mutation and the guarded metric-admission bridge
remain unavailable; no required metric is waived.

## Mutation testing without project wiring

Most mutation runners demand project-level configuration. `scripts/mutate.py` does not: it
reads the diff, mutates **only the changed lines of production code**, runs the project's own
test command against each mutant, and reports which survived.

```bash
python <skill>/scripts/mutate.py --slug <slug> --base origin/main
python <skill>/scripts/mutate.py --slug <slug> --base origin/main --test-cwd "packages/app" -- node --test "test/math case.test.mjs"
```

It writes an atomic version-2 report under `.ai/<slug>/evidence/runs/<run-id>/mutation.json`;
it does not update the historical `.ai/<slug>/mutation.json` alias. The probe consumes only its current
invocation's successful report, checking source binding and restoration, never the alias.
No workflow adoption or ledger is needed.

Explicit remainder argv preserves spaces without a shell. `--repo` retains its original
directory as the default test cwd before resolving the Git root; `--test-cwd` overrides it.
Without explicit argv, manifest commands take priority, then native test discovery in the
selected directory and its `test`/`tests` directories. Nested packages are not traversed.
Legacy `--test-cmd` accepts simple whitespace-separated commands; ambiguous quoting or
escaping is rejected. Use remainder argv instead.

Native classification requires Node 22 or later. Tests for this change were run on Node 24;
Node 22 compatibility is not an execution claim. Direct `node --test` uses the shared native
event reporter, with `NODE_TEST_CONTEXT` removed from the child environment. npm/custom
commands may run but are unclassified; arbitrary runner output is not assertion proof.

**How it behaves, and why:**
- **Diff-scoped.** Mutating the whole repository is slow and answers the wrong question. The
  question is whether *this change* is tested.
- **Production code only.** Test files, fixtures, and mocks are never mutated — a surviving
  mutant in a test proves nothing.
- **One mutant per line**, spread deterministically across the diff, capped by
  `--max-mutants` (default 20) so a run stays affordable.
- **Refuses to run** on a dirty working tree (mutants are written in place and restored) or on
  a red suite (every mutant would "die" for the wrong reason).
- **A kill needs an actual native assertion failure** in the baseline test inventory.
  Syntax, import/setup, file-wrapper, empty-suite, timeout, cancellation and unsupported
  outcomes are ungraded, never assertion kills. Any ungraded candidate makes the run incomplete.
- **Floor: 60%** on the changed lines. Below that, the gate fails.

**Survivors are a to-do list, not a score to argue with.** Each one is either killed with a
real assertion or documented in `review.md` as an equivalent mutant with the reason. Never
delete a survivor by narrowing the mutation scope.

**If the mutant total changes between runs, say why.** A score that rises because the
denominator shrank is indistinguishable from gaming unless the reason is recorded — a reviewer
will flag it, and should. Report it as "N mutants excluded: <reason>" and keep the previous
score alongside the new one.

Worked example — the same code, two suites, both green, both fully covering the function:

```
strong suite: score 100.0  killed 2  survived 0
hollow suite: score   0.0  killed 0  survived 2
  src/discount.js:2  boundary >= -> <   if (total >= 100 && isMember) {
  src/discount.js:5  boundary >= -> <   if (total >= 100) {
```

The hollow suite asserted only `result !== undefined`. Coverage said 100%; mutation said the
tests check nothing. That difference is the entire reason this metric exists.

## How it runs

`scripts/probe.py` in this skill runs available collectors twice — once on the **merge-base**
(in an owned throwaway git worktree) and once on the **working tree** — and writes `.ai/<slug>/metrics.json` with
both values and the delta.

```bash
python <skill>/scripts/probe.py --slug <slug> --base origin/main
python <skill>/scripts/probe.py --slug <slug> --base origin/main --skip-mutation   # faster loop
```

Run it once before the independent review (so the reviewer sees the numbers) and again after
any rework.

The immutable report is `.ai/<slug>/evidence/runs/<run-id>/metrics.json`; the top-level file
is a display alias. Reports carry source bytes/modes, explicit scope/exclusions, command
outputs and resolved policy. Changes during collection invalidate the observation.
This is source freshness, not authenticated identity or a filesystem sandbox.
The mutation snapshot excludes exactly its report and the matching probe report/display
paths, so publishing metrics does not invalidate its child proof. Other artifacts and
contracts remain observed.
The consumer uses the producer's canonical command selection, including concrete discovery
for `-- node --test`. It also reconciles candidate identities/bytes, actual native baseline
and result evidence, outcomes, counters and score. A summary score without consistent
classified results is unavailable, not measured proof.
`--require-metric NAME` only adds required proof. There are no exemptions or imported-score
flags. `--skip-mutation` and automatic UI skipping do not waive mutation completeness.

### Configured baseline qualification

The configured measurement path independently materializes the selected immutable Git
tree and compares the complete relevant file set, bytes and supported file types/modes.
A clean `git status`, index flags or fresh fingerprints alone do not prove baseline identity.
Base, head, controller and artifact inputs must not share mutable physical files.

Materialization uses isolated configuration, neutral LF defaults and qualified versioned
text/EOL transformations. It rejects external filters before checkout and rejects other
unqualified transformations explicitly. Git's all-attributes census omits genuinely absent
or reset attributes, but present values `unset` and `unspecified` are ambiguous: they can be
literal filter names. These present declarations are unsupported, including disabled forms
such as `-filter` and `-text`; they are not silently treated as safe defaults.

Qualification is version- and platform-bound. The current evidence covers the qualified
Git 2.53.0.windows.4 core and bundled libraries on Windows with Python 3.14.2, not arbitrary
Git distributions or POSIX execution. Windows mode projection is recorded separately from
immutable Git modes. This policy is not a sandbox, an atomic filesystem lease or proof of
complete mutation-controller isolation.

### Greenfield work has no baseline

On the first commit of real code the baseline is empty, so **every** metric "regresses" from
zero and a delta gate would fail the run for merely existing. When the merge-base holds fewer
than three source files the probe says so, records `"baseline": "greenfield"`, and judges
against absolute sanity limits instead (duplication ≤12%, max complexity ≤25, no cycles).
Read those as sanity checks, not targets.
An unavailable merge-base or failed baseline inventory is `"baseline": "unknown"`, never
greenfield. Missing brownfield comparison is unavailable, not a passing delta.

### Front-end projects

A React/Vue/Svelte/Angular project is detected automatically and recorded as `"project": "ui"`.
Mutation testing is **skipped by default** there, because every mutant re-runs the whole
component suite — minutes per mutant. Use `--force-mutation` when you genuinely want it (scope
it to pure logic directories), and state in the evidence that it was skipped and why. UI
duplication is also dominated by style files and chart geometry, so treat a small duplication
figure as noise rather than a finding.

## The gate

**Compare against the baseline, not against an absolute ideal.** Absolute thresholds invite
metric-gaming: a model that must get complexity under a number will shred one coherent
function into six incoherent ones.

Gate 6 fails if any of these is true:

- Any required measurement or comparison is unavailable, stale or only partially supported.
- Duplication, complexity, cycles, dead code, or static findings are **worse than the
  baseline** — the change made the codebase harder to maintain.
- A **new dependency cycle** or **architecture rule violation** appears. This is absolute:
  never acceptable, never "temporarily".
- **Diff coverage on changed lines is below the repo's coverage bar** (or below meaningful
  coverage of new branches when the repo has no bar).
- **Mutation score on the changed lines is below 60%**, with survivors listed and each one
  either killed or justified as equivalent. (This metric is diff-scoped, so it is judged
  against the floor rather than against the baseline.)

A failing metric sends you back to the **phase that owns the cause**, not to a cosmetic patch.

## Binding metrics to the rubric

When scoring `quality-bar.md`, these dimensions may not be scored ≥4 on prose alone:

| Dimension | Must cite |
|---|---|
| Reuse & DRY | duplication delta |
| Design & modularity | complexity delta, cycles, architecture violations |
| Extensibility & maintainability | complexity of the change's core, coupling delta |
| Robustness | static/security findings |
| Test quality & evidence | mutation score + diff coverage |

If a required metric is `unavailable`, mark the dependent score unverified and name the
missing prerequisite. Other evidence may be useful, but does not waive the completeness gate.

## Anti-gaming (these are the rules the metrics themselves cannot enforce)

- **Never refactor solely to move a number.** Splitting a cohesive function to lower
  complexity, or renaming to dodge a duplication detector, is gaming — the reviewer explicitly
  looks for it.
- **Never weaken a test to kill a mutant**; kill it with a real assertion or explain why the
  mutant is equivalent.
- **Never exclude a file, path, or rule** from a tool's scope to make a metric pass.
- **Never commit tool config or tool dependencies into the repo** to make a run reproduce.
- A metric that improves while the design gets worse is a **failed** change, whatever the
  number says. The reviewer's judgment outranks the probe; the probe outranks your opinion.

## `metrics.json`

Version 2 retains `metrics`, `unavailable`, `worst_status` and `verdict` for existing readers.
Each measurement has `state` (`measured` or `unavailable`), observed numeric `head` when
available, `comparison` (`ok`, `warn`, `fail`, `unavailable`) and an explicit reason.
`measurement_status` describes complete measured comparisons separately from `completeness`.
`missing_required` lists each missing metric, its reason and prerequisite.

For example, `measurement_status: "ok"` plus `completeness: "incomplete"` still produces
`verdict: "fail"`. A measured regression can coexist with incomplete proof. Overall `pass`
requires complete required proof and no measured failure; warnings still require explanation.
Diff-size counters are informational, not replacements for quality evidence.

Probe exits: **0** complete passing proof, **1** measured failure or incomplete proof,
**2** invalid/unstartable invocation. Mutation exits: **0** complete classified measurement
(the probe applies the 60% floor), **2** incomplete/unavailable/invalid.
The separate evaluation corpus retains its **0.9** test-quality threshold.

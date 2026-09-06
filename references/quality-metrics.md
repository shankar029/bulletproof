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
| 1 | **Mutation score** on changed lines | Do the tests actually assert anything? | `scripts/mutate.py` (any language), or the repo's runner if configured |
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

## Mutation testing without project wiring

Most mutation runners demand project-level configuration. `scripts/mutate.py` does not: it
reads the diff, mutates **only the changed lines of production code**, runs the project's own
test command against each mutant, and reports which survived.

```bash
python <skill>/scripts/mutate.py --slug <slug> --base origin/main
python <skill>/scripts/mutate.py --slug <slug> --base origin/main --test-cmd "npm test" --max-mutants 30
```

It writes `.ai/<slug>/mutation.json` and `probe.py` calls it automatically when the repo has
no configured runner of its own.

**How it behaves, and why:**
- **Diff-scoped.** Mutating the whole repository is slow and answers the wrong question. The
  question is whether *this change* is tested.
- **Production code only.** Test files, fixtures, and mocks are never mutated — a surviving
  mutant in a test proves nothing.
- **One mutant per line**, spread deterministically across the diff, capped by
  `--max-mutants` (default 20) so a run stays affordable.
- **Refuses to run** on a dirty working tree (mutants are written in place and restored) or on
  a red suite (every mutant would "die" for the wrong reason).
- **A timeout counts as killed** — an infinite loop is a detected defect.
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

`scripts/probe.py` in this skill runs every available tool twice — once on the **merge-base**
(in a throwaway git worktree) and once on **HEAD** — and writes `.ai/<slug>/metrics.json` with
both values and the delta.

```bash
python <skill>/scripts/probe.py --slug <slug> --base origin/main
python <skill>/scripts/probe.py --slug <slug> --base origin/main --skip-mutation   # faster loop
```

Run it once before the independent review (so the reviewer sees the numbers) and again after
any rework.

### Greenfield work has no baseline

On the first commit of real code the baseline is empty, so **every** metric "regresses" from
zero and a delta gate would fail the run for merely existing. When the merge-base holds fewer
than three source files the probe says so, records `"baseline": "greenfield"`, and judges
against absolute sanity limits instead (duplication ≤12%, max complexity ≤25, no cycles).
Read those as sanity checks, not targets.

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

If a metric is `unavailable`, say so in the scorecard and justify the score from evidence you
*do* have — never imply a measurement you didn't take.

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

```json
{
  "slug": "checkout-discount-codes",
  "base": "origin/main",
  "head": "a1b2c3d",
  "generated": "2026-02-17T12:00:00Z",
  "verdict": "pass",
  "metrics": {
    "duplication_pct":      { "base": 3.1,  "head": 3.0,  "delta": -0.1, "status": "ok" },
    "complexity_max":       { "base": 14,   "head": 15,   "delta": 1,    "status": "warn" },
    "complexity_avg":       { "base": 3.2,  "head": 3.3,  "delta": 0.1,  "status": "ok" },
    "cycles":               { "base": 0,    "head": 0,    "delta": 0,    "status": "ok" },
    "dead_exports":         { "base": 2,    "head": 2,    "delta": 0,    "status": "ok" },
    "static_findings":      { "base": 7,    "head": 6,    "delta": -1,   "status": "ok" },
    "diff_coverage_pct":    { "head": 94.0, "threshold": 85, "status": "ok" },
    "mutation_score_pct":   { "head": 78.0, "threshold": 60.0, "status": "ok",
                              "survivors": 0, "detail": ".ai/<slug>/mutation.json" },
    "diff_files":           { "head": 6 },
    "diff_lines":           { "head": 214 }
  },
  "unavailable": ["architecture_rules"],
  "tools": { "jscpd": "4.0.5", "lizard": "1.17.31" }
}
```

`status` is `ok` (no regression), `warn` (regressed within tolerance — explain it), or `fail`
(gate-blocking). `verdict` is `pass` only when nothing is `fail`.

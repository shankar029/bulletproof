# evals — the bulletproof eval harness

A **config-driven** evaluation harness that scores the `/bulletproof` skill objectively and
reproducibly. It generalizes the one-off `benchmark/` into a formalized task corpus with a single
runner, a composite scorecard, and a regression gate. This is **v1** of [`../EVAL-PLAN.md`](../EVAL-PLAN.md).

```bash
node evals/run.mjs        # Node >= 22, dependency-free (UI tasks also need Playwright — see benchmark/README.md)
```

Outputs `evals/report.md` (committed snapshot) and `evals/report.json` (gitignored). Exits
non-zero if any `bulletproof` arm scores below the bar on an applicable dimension — so it doubles
as a CI regression gate.

## What it measures

Per task, per arm, normalized to 0..1 and combined into a weighted **composite**:

| Dimension | Source | Meaning |
|---|---|---|
| **accuracy** | held-out oracle (`node --test`) | fraction of acceptance tests passing |
| **reuse** | source grep | fraction of seeded shared utilities actually imported |
| **duplication** | source grep | `1` if no inlined reimplementation of a shared helper, else `0` |
| **extensibility** | held-out extension oracle | `1` if a new case is addable without editing the core, else `0` (`n/a` when not probed) |
| **scope** | source grep (`forbidden`) + direct-dep check (`forbiddenDeps`) | `1` if no forbidden source pattern is present AND no forbidden package is a direct dependency (weak RNG, needless dependency, out-of-scope API), else `0` |
| **e2e** | arm test grep (`e2e` patterns) | `1` if the arm ships a **surface-appropriate** end-to-end test (cli → real process spawn; api → booted server + real HTTP; ui → browser driving), else `0`. `n/a` for library tasks (their E2E is public-API invocation, already covered by the oracle + testQuality). |
| **testQuality** | mutation kill-rate | `killed / (killed+survived)` — mutate the arm's *own* impl and re-run the arm's *own* tests. **No tests**, tests **not runnable** by the platform runner (present but 0 discovered — e.g. written for a framework `node --test` can't execute), or tests that **fail on the arm's own code** → `0` (three distinct, reported states). `n/a` when the task doesn't opt in (`quality.mutate`) or the impl yields no mutable operators. |

`n/a` dimensions are dropped and the remaining weights renormalized. The **scope** dimension is what
catches *trap* tasks, where an arm can be 100% accurate yet still wrong (e.g. `uid`: both arms pass
the uniqueness oracle, but the baseline uses `Math.random()` → `scope = 0`). The **testQuality**
dimension catches the arm that ships *no real tests*: it mutates the arm's implementation and checks
whether the arm's own tests notice. Textual mutation → equivalent mutants can survive (e.g.
`len > 0`→`len < 0`), so the regression gate uses a **0.9** kill-rate bar rather than an exact 1.0.

## Task schema (`evals/tasks/<id>/task.json`)

```jsonc
{
  "id": "discount-api",
  "title": "Discount-code pricing API",
  "dimensions": { "changeType": "greenfield", "surface": "api", "stack": "ts-node", "difficulty": "standard" },
  "project": "benchmark/projects/discount-api",     // arms + oracles live here (relative to repo root)
  "arms": ["baseline", "bulletproof"],
  "functional": {                                    // accuracy scoring
    "kind": "logic",                                 // "logic" (ARM_PATH) | "ui" (ARM_DIR, Playwright)
    "oracle": "oracle/oracle.test.ts",               // relative to project
    "armEntry": "index.ts"                           // arm module (logic only)
  },
  "quality": {
    "src": "index.ts",                               // arm source file to grep
    "mutate": true,                                  // opt in to the test-realness (mutation) probe; mutate `src`
    "reuse": [["money", "from ['\"]\\.\\./shared/money"]],   // [name, regex] the arm should import
    "duplication": ["Math\\.round\\("],              // regexes that indicate an inlined reimplementation
    "forbidden": ["Math\\.random\\(", "from ['\"]uuid"], // source patterns that must be ABSENT (trap/scope)
    "forbiddenDeps": ["uuid", "nanoid"],           // package names that must NOT be DIRECT deps in the arm's package.json (transitive tooling deps ignored)
    "extensionOracle": "oracle/extension.test.ts",   // or null when not probed
    "extensionArm": "index.ts"
  },
  "weights": { "accuracy": 0.5, "reuse": 0.2, "extensibility": 0.2, "duplication": 0.1, "testQuality": 0.25, "e2e": 0.2 }
}
```

Regex strings are JSON-escaped (`\\.` → `\.`). `kind: "ui"` tasks run the oracle with `ARM_DIR`
set to the arm folder (the oracle serves it in a real browser); `logic` tasks run with `ARM_PATH`
set to the arm entry module.

## Adding a task

1. Author (or reuse) a project under `benchmark/projects/<name>/` with `baseline/`, `bulletproof/`,
   a held-out `oracle/`, and any `shared/` utilities to reuse (see `../CONTRIBUTING.md`).
2. Drop a `task.json` in `evals/tasks/<id>/` pointing at it.
3. Run `node evals/run.mjs`; confirm the `bulletproof` arm is perfect and `baseline` visibly weaker.

No runner code changes — the harness is fully config-driven.

## Oracle patterns

Most oracles import the arm module and assert (`ARM_PATH` for logic, `ARM_DIR` for UI). Two richer
patterns are in use and need no special harness support — the oracle is just a `node --test` file:

- **Extension oracle** (`extensionOracle`): imports the arm and registers a *new* case; passing
  proves the design is open/closed.
- **Mutation oracle** (`median-backfill`): the arm's deliverable is a *test suite*. The oracle
  `spawnSync`s the arm's tests against the correct subject (must pass) and against each planted
  mutant in `mutants/*` (must fail = killed), injecting the subject via `SUBJECT_PATH`. Accuracy is
  the mutation kill-rate. (Note: such an oracle must `delete env.NODE_TEST_CONTEXT` before spawning,
  or the nested runner exits 0 even on failing tests.)

## Why JSON, not YAML

To stay **dependency-free** (Node has no built-in YAML parser). `EVAL-PLAN.md` sketches `meta.yaml`;
v1 uses `task.json` for the same purpose without adding a parser dependency.

## v2 — agent-in-the-loop

The arms here are **fixed artifacts** (hand-authored), which makes v1 a fast, deterministic
regression gate but can't measure what a *live* agent does. The **v2 harness**
([`agent/`](agent/)) invokes the host agent headless to actually **produce** the arm, reusing this
same scoring library. It adds a **`process`** dimension (feature branch? Conventional Commit?
committing to `main` **hard-zeroes** the run), **pass@k** variance, and non-library (cli/api) live
tasks. See [`agent/README.md`](agent/README.md).

## Deferred (later phases)

- **LLM-judge, guardrail policy, cost/telemetry, cross-agent matrix** — v3.
- **Seeded-starting-code tasks** (refactor/bugfix on an existing tree) for the v2 harness.

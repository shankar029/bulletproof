# Contributing to bulletproof

Thanks for helping make terminal coding agents ship like top‑1% engineers. This project
**dogfoods its own skill**: substantive changes should be delivered the way `/bulletproof`
would — planned, tested, verified, and shipped as a PR with proof.

## Ground rules (the skill's prime directives apply to this repo too)

1. **Honor the project.** Match the existing structure, tone, and conventions.
2. **Zero tech debt.** No dead code, TODOs, commented-out blocks, or copy‑paste duplication.
3. **No fakes.** No stub implementations, empty/`skip`ped tests, or unjustified lint/type
   suppression to go green.
4. **Prove everything.** Changes to the skill, benchmark, or scorers must leave the eval gate
   (`node evals/run.mjs`) and all unit tests green.
5. **Never commit to `master`/`main`.** Work on a feature branch and open a PR with evidence.

## Dev environment

- **Node ≥ 22** (the benchmark uses native TypeScript type‑stripping via `node --test`).
- **git ≥ 2.4**, and **`gh`** if you want to open PRs from the CLI.
- **Playwright** only for the UI benchmark arm:
  ```bash
  cd benchmark
  npm install                       # installs the dev dep declared in package.json
  npx playwright install chromium   # one-time browser download (~115 MiB)
  ```

> Note: native TS strip‑only mode does **not** support TS "parameter properties"
> (`constructor(private x)`). Declare class fields explicitly — see the arms for the pattern.

## Running the eval

The eval is how we know the skill delivers. Keep it green.

```bash
node evals/run.mjs                       # v1: config-driven corpus + composite scorecard (regression gate)
node --test evals/lib/*.test.mjs \
            evals/agent/agent.test.mjs   # unit tests for the scoring library + agent harness
node evals/agent/live.mjs --task <id> --dry-run   # v2: agent-in-the-loop plumbing (no model)
```

`evals/run.mjs` **exits non-zero if any `bulletproof` arm regresses**, so it doubles as the CI gate;
it writes `evals/report.md` (committed snapshot) and `evals/report.json` (gitignored). The original
illustrative A/B still lives in `benchmark/` (`run.mjs`, `run-ui.mjs`, `score-quality.mjs`) and its
runners likewise exit non-zero on a bulletproof regression. See
[`evals/README.md`](evals/README.md), [`evals/agent/README.md`](evals/agent/README.md), and
[`benchmark/README.md`](benchmark/README.md).

## Adding an eval task

A project is an A/B fixture with a **held‑out oracle** the arms never import at authoring time:

```
benchmark/projects/<name>/
├── SPEC.md                 # the requirement + rules + acceptance (+ reuse/extensibility contract)
├── shared/                 # utilities the arms are expected to REUSE
├── baseline/               # naive arm (raw agent, no skill)
├── bulletproof/            # skill-quality arm (+ its own unit/integration tests)
└── oracle/
    ├── oracle.(test.ts|mjs)  # functional acceptance suite, run against ARM_PATH / ARM_DIR
    └── extension.test.ts     # (optional) open/closed probe: add a new case without editing core
```

Then:
1. Drop a `task.json` under `evals/tasks/<id>/` pointing at the project (see
   [`evals/README.md`](evals/README.md) for the schema — the harness is fully config-driven, no
   runner code changes). For a live v2 run, add an optional `agent` block.
2. Run `node evals/run.mjs`; confirm the `bulletproof` arm is perfect on every applicable dimension
   and the `baseline` is visibly weaker.
3. If you also touched the illustrative benchmark, keep `benchmark/RESULTS.md` in sync.

See `benchmark/README.md` for the illustrative A/B design and
[`evals/README.md`](evals/README.md) for the config-driven task schema this generalizes into.

## Editing the skill

- `SKILL.md` is the **single source of truth**; the launchers in `launchers/` are thin wrappers
  that point at it. Change behavior in `SKILL.md` (and the relevant `references/*.md`), not in each
  launcher.
- Keep `SKILL.md` **lean** — push depth into `references/` (progressive disclosure).
- If you add a reference file, link it from `SKILL.md`'s "References" list and `README.md`'s layout.

## Commit & PR conventions

- Conventional‑style subject lines (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- Small, cohesive commits; describe **what changed and the proof** in the body.
- PRs: state the requirement, what changed, how it was verified (runner output), and residual risks.

## Docs

- Architecture & design rationale: [`docs/architecture.md`](docs/architecture.md)
- Roadmap for the eval harness: [`EVAL-PLAN.md`](EVAL-PLAN.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)

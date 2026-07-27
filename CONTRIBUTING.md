# Contributing to bulletproof

Thanks for helping make terminal coding agents ship like top‑1% engineers. This project
**dogfoods its own skill**: substantive changes should be delivered the way `/bulletproof`
would — planned, tested, verified, and shipped as a PR with proof.

## Ground rules (the skill's prime directives apply to this repo too)

1. **Honor the project.** Match the existing structure, tone, and conventions.
2. **Zero tech debt.** No dead code, TODOs, commented-out blocks, or copy‑paste duplication.
3. **No fakes.** No stub implementations, empty/`skip`ped tests, or unjustified lint/type
   suppression to go green.
4. **Prove everything.** Changes to the benchmark or scorers must leave every runner green.
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

## Running the benchmark

From `benchmark/`:

```bash
node run.mjs            # logic projects (discount-api, csv-stats-cli) — functional oracle A/B
node run-ui.mjs         # signup-form — real Chromium (Playwright) UI oracle A/B
node score-quality.mjs  # engineering-quality probes: reuse, duplication, extensibility
```

Each runner **exits non‑zero if any `bulletproof` arm fails**, so they double as regression gates.
`run.mjs` writes `results.json` (gitignored).

## Adding a benchmark project

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
1. Wire it into the matching runner (`run.mjs` for logic, `run-ui.mjs` for UI) and, for the quality
   layer, add a probe entry to `score-quality.mjs` (reuse patterns, duplication patterns, extension
   oracle path).
2. Run all three runners; confirm the `bulletproof` arm is green and the `baseline` visibly weaker.
3. Update `benchmark/RESULTS.md` and the headline table in `README.md`.

See `benchmark/README.md` for the design and `EVAL-PLAN.md` for where this is heading (a
config‑driven `evals/tasks/` schema).

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

# Bulletproof Benchmark

> **This is the original, illustrative A/B** (N=1, one agent session). It has since been generalized
> into the config-driven, multi-dimension eval in [`../evals/`](../evals/) (v1 regression gate) and
> the agent-in-the-loop harness in [`../evals/agent/`](../evals/agent/) (v2). Start there for the
> current picture; this directory remains as the seed of the idea and as fixtures the eval reuses.

Measures the **quality, accuracy, and effectiveness** the `/bulletproof` workflow adds, by
comparing two implementations of the *same spec* on real, runnable projects.

## Method: objective A/B with a held-out oracle

For each project there are two **arms**, built from the identical `SPEC.md`:

- **`baseline/`** — a competent but *undisciplined* single-pass implementation: happy path,
  minimal/no tests. Represents an agent given the raw task with no methodology.
- **`bulletproof/`** — the same task taken through the `/bulletproof` loop: plan, full unit +
  integration tests, real end-to-end verification, self-review.

A third, independent **`oracle/`** acceptance suite is written from the spec and **hidden from
both arms**. It is executed against *each* arm via an `ARM_PATH` env var, so **correctness is
scored objectively** — not self-judged. This is the headline metric.

We also record each arm's **own** test count/results and coverage, plus a quality rubric.

## Projects (chosen for variety + to run in a Node-only env)

| Project | Kind | E2E path exercised |
|---|---|---|
| `discount-api` | pure logic + HTTP service | **real HTTP** requests to a live server |
| `csv-stats-cli` | command-line tool | **real subprocess** invocation |
| `signup-form` | browser UI (static HTML+JS) | **real Chromium** via Playwright |

Both logic projects run in a Node-only env; the UI project needs Playwright (see below). Node/TS
was chosen only because this environment has Node but no Python/Go/.NET.

## Layout
```
benchmark/
├── run.mjs                         # reproducible runner (oracle + own tests) -> results.json
├── RESULTS.md                      # findings, scorecard, rubric, caveats
└── projects/<id>/
    ├── SPEC.md                     # the task given to both arms
    ├── oracle/oracle.test.ts       # held-out acceptance suite (runs against ARM_PATH)
    ├── baseline/                   # undisciplined arm + its own test
    └── bulletproof/                # /bulletproof arm + full tests
```

## Reproduce
```bash
cd benchmark
node run.mjs                        # logic projects: prints scorecard, writes results.json
node score-quality.mjs             # engineering-quality probes (reuse, extensibility, duplication)

# UI project (needs a browser, one-time):
npm i -D playwright && npx playwright install chromium
node run-ui.mjs                     # signup-form: baseline vs bulletproof in real Chromium

# inspect a single arm against the oracle:
ARM_PATH="$PWD/projects/discount-api/baseline/index.ts" \
  node --test projects/discount-api/oracle/oracle.test.ts
```
Logic projects require only Node ≥ 22 (native TypeScript + `node --test`), no dependencies.

## Limitations (read before quoting numbers)
- **Illustrative, not a controlled study.** Both arms were produced in one agent session, so this
  shows the *discipline delta / ceiling*, not a blind multi-run human trial. All source is in the
  repo so anyone can inspect or re-run.
- **Baseline is naive by construction** (single-pass, not sabotaged). A more careful baseline
  would score higher; the point is what the *methodology* forces you not to miss.
- **UI/Playwright arm is live-run here** in real Chromium (it works on this ARM64 Windows env).
  All three E2E surfaces — HTTP, subprocess, and browser — are exercised for real.

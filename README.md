# bulletproof

**One slash command that makes any terminal coding agent finish the job — deliver exactly what
you asked, completely, and prove it works.**

Coding agents are great at *starting* work and bad at *finishing* it: half-built features, tests
that assert nothing (or none at all), "works on my machine" with no end-to-end proof, ad-hoc fixes
that become tomorrow's bug, invented APIs, work lost when a session restarts, and commits straight
to `main`. `/bulletproof` fixes that. Give it a requirement — text, a doc path, or an issue link —
and it owns the delivery end to end: understands the **whole** ask, **designs before it codes**,
implements with real tests, **proves the feature works the way a human would check it**, measures
the result with real tools, gets an independent review, and opens a PR with the evidence.

```
/bulletproof <requirement | doc path | issue link>
```

## What "delivered" means here

Six phases, each with a gate it must pass before advancing.

1. **Understand, then research the code — and write it down.** Produces `research.md`: the ground
   truth for the run. What the codebase does today, what it does **not** do, the constraints and
   conventions that bind the design, the tests already covering the area, and the seams the new
   work attaches to — **every claim carrying `path:line` and its snippet, every "not implemented"
   carrying the search that proves absence**. Grounding stops being a promise and becomes something
   you can check: Gate 1 spot-checks three citations at random and rejects the document if one
   misses.
2. **Design the program before writing it — then wait for your sign-off.** Produces a **3-page
   HTML design document**: the classes/modules, interfaces and public method signatures, each with
   its single responsibility and collaborators, plus sequence diagrams for the critical flows, data
   contracts, decisions with rejected alternatives, and failure modes. Architecture diagrams only
   for genuinely large work; a **UX approval gate** ([`ux-design.md`](references/ux-design.md))
   whenever there's a user-facing surface. **It hands the document over and stops** — no code until
   you approve, unless you explicitly told it to run unattended. **This is the gate that kills
   ad-hoc, unmaintainable code.**
3. **Plan into session-sized increments.** Vertical slices that each deliver observable behaviour,
   are testable and reviewable alone, and **fit in one context window** — so long work survives
   restarts. Production-readiness items are planned here when going live is in scope.
4. **Implement + test.** Re-reads the design before each increment ("the design, not your
   recollection, is the contract"), then real unit + integration tests for all new behaviour —
   never stubs, empty asserts, or `skip`ped tests.
5. **Prove it end-to-end.** Verifies the feature the way a person would: **agent-browser** for UI and
   front-end, real **HTTP** for services, real invocation for CLIs and libraries — with captured
   evidence. When the environment makes real proof impossible it says so and hands you the command,
   rather than quietly weakening the gate.
6. **Measure, review, ship.** Runs a **deterministic quality probe**, gets an **independent review in
   a separate session**, runs the full quality gate, assembles the evidence bundle, and opens a **PR
   on a feature branch** (never `main`).

Then a **convergence loop**: the work is scored against a 9-dimension rubric — correctness,
**grounding**, **design fidelity**, scope fidelity, reuse & DRY, design & modularity, extensibility,
robustness, test quality & evidence ([`quality-bar.md`](references/quality-bar.md)) — and it keeps
fixing **root causes** until every dimension clears the bar, capped at three honest iterations after
which the remaining gap ships as a named follow-up. Passing tests is the floor, not the finish line.

**Prime directives:** ground everything in the real codebase (never invent) · design before code ·
honor the project · root cause, never a band-aid · zero tech debt and no fakes · prove everything ·
ask only real questions.

## The features that make it stick

### A durable workspace — work survives a restart

Every non-trivial task gets a slug and a directory that is committed with the change:

```
.ai/<slug>/
  state.md            # resume contract: phase, gate row, increments, next action
  clarifications.md   # questions, answers, assumptions
  design.html         # program design  ·  architecture.html for large work
  plan.html           # increments, tasks, test strategy
  review.json         # your comments + verdict, exported from the document
  review.md           # independent-reviewer findings and their dispositions
  metrics.json        # deterministic quality measurements
  mutation.json       # surviving mutants
  evidence/           # screenshots, logs, transcripts
```

On every invocation it looks for `state.md` **first** and resumes at the recorded phase — it does
not restart, redesign, or re-derive intent from the diff. Details:
[`workspace.md`](references/workspace.md).

### Design documents you'll actually read — and can review in the browser

Documents are plain semantic HTML; a shared theme supplies everything else, so the model spends its
tokens on design rather than CSS.

- **Built for reading:** serif reading face at a ~68-character measure, adjustable text size,
  serif ⇄ sans, three column widths, and light / dark / auto themes. Diagrams use theme classes, so
  one SVG stays legible in both themes. Printing drops the UI and appends comments as endnotes.
- **Built for reviewing:** select any text to **highlight** or **comment**, add free-standing
  **notes**, then choose **Approve / Approve with comments / Request changes** and hand it back via
  *Download `review.json`* or *Copy JSON*. Comments are anchored to quoted text and re-attach after
  a reload; if the text changed, the comment is flagged rather than lost.
- **The handoff is a stop, not a poll.** It self-checks the document renders, opens it in *your*
  browser, records `Blocked on: design.html sign-off`, and **ends the turn** — your answer can
  arrive in a later session. See [`html-theme.md`](references/html-theme.md).

### Deterministic quality measurement — not adjectives

`scripts/probe.py` runs the installed analysis tools twice — on the **merge-base in a throwaway
worktree** and on **HEAD** — and writes `metrics.json` with base, head and delta for duplication,
cyclomatic complexity, dependency cycles, dead code, static findings and diff size.

The gate is **delta-based, not absolute**, deliberately: absolute thresholds invite gaming — a model
forced under a complexity number will shred one coherent function into six incoherent ones. New
dependency cycles are the exception: absolute fail. Greenfield work (an empty baseline) and
front-end projects are detected and judged appropriately instead of failing for merely existing.

### Mutation testing with zero project wiring

The one metric that answers *"do these tests actually assert anything?"* `scripts/mutate.py` reads
the diff, mutates **only the changed lines of production code** (operator swaps plus statement
deletion), and runs your own test command against each mutant. Diff-scoped, capped, never mutates
tests or fixtures, refuses a dirty tree or a red suite, and reports each survivor with file, line and
the exact edit — to be killed with a real assertion or documented as equivalent.

Why it matters, measured on identical code with two green suites that both fully cover the function:

```
strong suite: 100.0%  killed 2  survived 0
hollow suite:   0.0%  killed 0  survived 2
  src/discount.js:2  boundary >= -> <
  src/discount.js:5  boundary >= -> <
```

The hollow suite asserted only `result !== undefined`. Coverage said 100%; mutation said the tests
check nothing. See [`quality-metrics.md`](references/quality-metrics.md).

### Independent review — a fresh session, ideally a different model

Your own review can't un-see the reasoning that made a shortcut feel acceptable. The reviewer gets
the requirement, criteria, design, `metrics.json` and the diff — **and none of your reasoning** —
and never writes code. Preference order: different model + fresh context → same model + fresh
context → cold self re-read. On scoring disagreement, **the lower score wins**.

### A final report you can actually act on

Every run ends by writing `.ai/<slug>/report.html` (same readable theme, same comment/approve
layer) and summarising it in chat: what was delivered **and what wasn't**, each acceptance
criterion with *how it was proven*, the **G1–G6 gate row** with reasons for anything not green,
the measured numbers (tests, coverage, probe deltas, mutation score, and anything `unavailable`),
the 9-dimension scorecard citing those numbers, unconfirmed assumptions, follow-ups, and **what is
still pending — each with the exact command to finish it**. It is written even when a run is cut
short, so an interrupted session still leaves you something worth reading.

### Phases run in subagents, so the context goes where the work is

Research and design run in **subagents with fresh context** where the harness supports it (with an
inline fallback everywhere else). Research is the most token-expensive phase in a run — it reads
dozens of files to produce two pages — and doing it in the main context burns the window on raw
file contents *before implementation starts*. Delegated, the main agent gets the two pages instead
of the fifty files. The parent still spot-checks citations, still owns the design sign-off, and
implementation still re-opens a file before changing it: the document is an index into the code,
never a replacement for it.

### Increments end in commits, not compaction

When context gets tight the rule is to **finish the increment, commit it green, and start the next
one in a fresh session** — never to compact the conversation and push on. Compaction is lossy
summarization by the model that is already degrading, and the first thing it drops is the
citations, signatures and exact names the whole loop rests on. The durable workspace is what makes
the fresh session cheap: it re-reads ground truth instead of inheriting a paraphrase.

### Evidence-bound scoring

> Where a metric exists for a dimension, a score of ≥4 **must cite it**. No number, no score.

That turns the scorecard from self-flattery into something falsifiable.

### Beyond a single change

- **Whole apps** — [`app-scale-delivery.md`](references/app-scale-delivery.md) adds an outer loop:
  walking skeleton first, then vertical slices, one branch, one PR.
- **Going live** — [`production-readiness.md`](references/production-readiness.md) is the checklist
  that takes an app from building to operable, every item addressed or N/A with a reason.
- **Parallelism** — file-disjoint, dependency-free work is split across subagents in isolated
  worktrees, then integrated and verified as a whole.

## How we know it actually delivers

The skill's value isn't self-asserted — it's **measured**, by an eval designed to catch the skill's
*own* failures rather than flatter it. Per task, per arm, it scores whether the agent delivered what
was asked — completely and provably — across independent dimensions:

| Dimension | The question it answers |
|---|---|
| **accuracy** | Does it actually work? — a held-out oracle acceptance suite the solution never sees. |
| **testQuality** | Are the tests *real*? — mutate the solution and check whether its **own** tests catch the bug. No tests, or tests the runner can't even execute → `0`. |
| **e2e** | Is it proven end-to-end for its surface? — CLI spawn / real HTTP / real browser. |
| **scope** | Exactly what was asked — no forbidden pattern (e.g. weak RNG), no needless dependency? |
| **reuse · duplication · extensibility** | Built on the project's own utilities, no copy-paste, open/closed to new cases? |
| **process** | Shipped like a professional — committed on a feature branch, **never** on `main`? |

Two tiers, both dependency-free (Node ≥ 22):

- **v1 — regression gate** ([`evals/`](evals/)): a config-driven corpus of **10 tasks** (greenfield,
  bugfix, refactor, a stateful state machine, a mutation-graded test-backfill, and *trap* tasks where
  an arm can be 100% accurate yet still wrong). Hand-authored baseline vs. bulletproof arms graded by
  held-out oracles. `node evals/run.mjs` prints a composite scorecard and **exits non-zero if any
  bulletproof arm regresses**.
- **v2 — agent-in-the-loop** ([`evals/agent/`](evals/agent/)): the agent is actually invoked headless
  to *produce* the solution, with the **only** difference between arms being the skill. It observes
  `process` from the real git workspace, supports **pass@k** variance, and **hard-zeroes any run that
  commits to `main`**.

**Honest findings** — an eval earns its keep by finding defects:

- A capable base model already *ceilings* on easy tasks; the skill's measurable wins concentrate on
  **traps** (weak RNG / needless deps, where the skill makes correctness *reliable* across runs),
  **real tests** (baseline ships none on 6/10 tasks), **E2E**, and **process**.
- The eval caught **bulletproof's own defects** and drove the fixes: it over-engineered a
  one-function task (89 packages + a coverage dashboard → fixed by "right-size the effort"), and on a
  harder task it committed straight to `master` (→ fixed by hardening the ship gate *and*
  hard-capping the score). Both fixes were then **verified live**.

Method and numbers: [`evals/README.md`](evals/README.md) (v1) ·
[`evals/agent/README.md`](evals/agent/README.md) (v2) · the original illustrative A/B in
[`benchmark/`](benchmark/) · roadmap in [`EVAL-PLAN.md`](EVAL-PLAN.md).

## Layout

```
bulletproof/
├── SKILL.md                     # the operating loop (single source of truth)
├── references/                  # on-demand depth per phase (progressive disclosure)
│   ├── workspace.md             #   .ai/<slug>/ workspace, state.md, resume, increment sizing
│   ├── project-profile.md       #   detect & honor project nature; anti-debt; design checklist
│   ├── design-doc.md            #   the 3-page design/plan documents; simple-diagram limits
│   ├── html-theme.md            #   shared theme, reading controls, comment/approval handoff
│   ├── ux-design.md             #   UX spec + design-first approval gate (user-facing surfaces)
│   ├── testing-and-e2e.md       #   unit/integration/E2E expectations; coverage vs mutation
│   ├── e2e-agent-browser.md     #   agent-browser: flows, assertions, artifact self-check
│   ├── quality-metrics.md       #   the probe: toolchain, baselines, gate rules, metrics.json
│   ├── quality-bar.md           #   the 9-dimension rubric + convergence loop
│   ├── research.md              #   the ground-truth research document: citations, absence evidence
│   ├── delegation.md            #   running research/design/review in subagents; briefs, spot-check
│   ├── review-and-pr.md         #   review checklist, quality gate, evidence bundle, PR format
│   ├── final-report.md          #   the end-of-run report: gates, measurements, what's pending
│   ├── production-readiness.md  #   building → running safely in production
│   ├── app-scale-delivery.md    #   outer loop for delivering an entire app
│   └── parallel-execution.md    #   split disjoint work across subagents; worktrees
├── scripts/                     # deterministic measurement (stdlib Python, no project deps)
│   ├── probe.py                 #   HEAD vs merge-base metrics → .ai/<slug>/metrics.json
│   └── mutate.py                #   diff-scoped mutation engine → .ai/<slug>/mutation.json
├── assets/                      # shared theme for generated HTML artifacts
│   ├── artifact.css             #   reading typography, light/dark, print, diagram classes
│   └── artifact.js              #   reading controls + highlight/comment/approve review layer
├── launchers/                   # thin per-agent entry points (all point at SKILL.md)
├── install/                     # per-agent manual install steps (pi / claude-code / copilot-cli)
├── evals/                       # the eval harness (how we know it delivers)
├── benchmark/                   # original illustrative A/B (generalized by evals/)
├── install.sh                   # one-command installer (macOS/Linux/Git-Bash)
└── install.ps1                  # one-command installer (Windows PowerShell)
```

## Install

**One command** (downloads from GitHub, installs the skill + launcher for your agent):

```bash
# macOS / Linux / Git-Bash — pick one: pi | claude | copilot
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
```

```powershell
# Windows PowerShell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) pi
```

Install a specific release with `BULLETPROOF_REF=v0.7.0`. Prefer to do it by hand? Per-agent manual
steps:

- **pi** → [`install/pi.md`](install/pi.md) — skill + `/bulletproof` prompt template
- **Claude Code** → [`install/claude-code.md`](install/claude-code.md) — skill + `/bulletproof` command
- **Copilot CLI** → [`install/copilot-cli.md`](install/copilot-cli.md) — custom agent (no slash-command support upstream)

### Optional toolchain

The skill works without these and reports any missing tool as `unavailable` rather than as a pass.
Install what your languages need — **globally, never into your project**:

```bash
npm install -g agent-browser jscpd madge     # browser E2E · duplication · dependency cycles
agent-browser install                        # one-time Chrome download
pip install --user lizard semgrep diff-cover # complexity · static analysis · diff coverage
```

Mutation testing needs nothing installed: `scripts/mutate.py` uses your project's own test command.

## Design notes

- **Single source of truth:** the loop lives once in `SKILL.md`; launchers are thin wrappers, so
  behavior stays identical across agents.
- **Lean by design:** `SKILL.md` stays tight; deep detail sits in `references/` and loads only when
  a phase needs it (progressive disclosure).
- **Technology-agnostic**, with two deliberate exceptions: agent-browser for browser verification,
  and HTML/SVG for the design documents.
- **Guardrails, not tutorials:** it constrains *how* the model works; it doesn't teach it to program.
- **Safe by default:** feature branches only, PR-only, no protected-branch commits; refuses stubs,
  empty tests, and unjustified suppression — and the eval enforces it (a commit to `main`
  hard-zeroes the run).
- **Never blocks its own shell:** dev servers and watchers run detached, test runners run
  non-interactively, and retries are bounded — a foreground dev server ends the run, not the turn.
- **Every claim measurable:** where a rule can be enforced by a tool instead of a sentence, it is.
- **Rename:** don't like `/bulletproof`? Rename the launcher file (e.g. `ship.md` → `/ship`).

More on the design: [`docs/architecture.md`](docs/architecture.md).

## Contributing

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). The project **dogfoods its own
skill**: substantive changes are planned, tested, verified, and shipped as a PR with proof. Keep the
eval gate green (`node evals/run.mjs`) and the unit tests passing. Changes are tracked in
[`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE) © 2026 shankar029.

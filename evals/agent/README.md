# evals/agent — agent-in-the-loop harness (EVAL-PLAN v2, prototype)

v1 (`evals/run.mjs`) scores **hand-authored** arms — it proves *"a bulletproof-style solution beats a
naive one,"* not *"the skill makes a real agent produce the bulletproof solution."* This subsystem
closes that gap: a **real host agent produces the arm**, then the **existing** harness
(`evals/lib/score.mjs`) scores it against the same held-out oracle.

## How it works

```
for arm in [baseline, bulletproof]:
  ws = fresh temp workspace   { SPEC.md, shared/…, arm/ }      # held-out oracle NEVER copied
  git init ws                                                   # so bulletproof can commit
  arm/index.ts = pi(prompt, cwd=ws, skill? = arm==bulletproof) # the agent writes the deliverable
  score = runFunctional + runQuality + runTestQuality(task, project, ws/arm)   # same v1 scoring lib
  process = observe git of ws: feature branch? conventional commit? main untouched?
```

The only variable between arms is the skill: **baseline** runs pi with no skill; **bulletproof**
runs pi with `--skill SKILL.md`. Both are isolated from ambient context, extensions,
prompt-templates, and skill discovery (`-nc -ne -np -ns`), so any delta is attributable to
`/bulletproof` alone.

The workspace mirrors the fixture layout (`arm/` next to `shared/`) so the produced module resolves
`../shared/*.ts` and the existing oracle/quality/test-realness probes score it with the same scoring
lib as v1 (per-run output shows `composite`, `acc`, `test-real`, and `process` when applicable).

### Process adherence (v2-only)
Because the agent runs in a real git workspace, the harness observes whether it followed the skill's
process rules (`evals/agent/process.mjs`, unit-tested): **committed** its work, on a **feature
branch** (not the seed/default branch), with a **Conventional Commit** message. Committing to the
seed branch (`main`/`master`) is a hard **0** (mirrors "never commit to a protected branch").
the `process` signal. Committing to a **protected branch** (`main`/`master`) is a hard safety
violation: it **zeroes the run's composite** (`cappedComposite`) regardless of code quality — a
correct-but-on-`main` delivery would be reverted in a real team, so it is not a valid delivery.
Live-validated on `map-limit`: **baseline `process 0.00`** (wrote the file, never committed) vs
**bulletproof `process 1.00`** — confirmed against real git state (`feat/map-limit` branch checked
out, `master` still at the seed commit, commit `feat(arm): …`). This is exactly the "quality &
discipline, not just correctness" gap the oracle-only score was blind to.

## Usage

```bash
# Deterministic plumbing proof (copies the reference solution, no model call):
node evals/agent/live.mjs --task paginator --dry-run

# One real pi run of a single arm:
node evals/agent/live.mjs --task paginator --arms bulletproof

# Full live A/B:
node evals/agent/live.mjs --task paginator            # baseline + bulletproof
```

Flags: `--arms a,b` · `--dry-run` · `--timeout <ms>` (default 300000) · `--keep` (retain workspaces).

Unit tests (pure arg/prompt/prep logic, no model): `node --test evals/agent/agent.test.mjs`.

## Task requirements

A task opts into v2 by adding an `agent` block to its `task.json`:

```jsonc
"agent": {
  "prompt": "SPEC.md",              // requirement file (relative to project) shown to the agent
  "seed": ["shared"],               // dirs/files copied into the workspace (NOT the oracle)
  "armFile": "arm/index.ts",        // where the agent must write the deliverable; armDir = its dirname
  "reference": "bulletproof/index.ts" // known-good solution used only by --dry-run
}
```

## Results so far

Live pass@k on the pi host, with terse guardrail-free requirements (the SPECs' "use X / don't use
Y" hints withheld), so the skill — not the prompt — is the only difference between arms:

| task | difficulty | baseline | bulletproof | skill delta |
|---|---|---|---|---|
| paginator | standard | 1.00 (k=1) | 1.00 (k=1) | none (ceiling) |
| map-limit | gnarly | 1.00, 100% clean (k=3) | 1.00 (k=1, ~6 min, timed out) | none (tie, far slower) |
| expr-eval | gnarly | 1.00, 100% clean (k=3) | 1.00 (k=1, ~4 min) | none (tie, far slower) |
| **uid** | **trap** | **0.80 ± 0.14, 33% clean (k=3)** | **1.00 ± 0.00, 100% clean (k=3)** | **+0.20, consistency** |
| **csv-stats-cli** | **cli / real** | **acc 1.00, test-real 0 (no tests), e2e 0, process 0 (k=1)** | **acc 1.00, e2e 1.00, test-real 0.06, process 0.00 ⚠committed to main (k=1)** | **e2e+tests present; but 2 real defects caught** |

**Non-library surface (`csv-stats-cli`, cli):** the first live agent run on a realistic multi-rule
CLI. Baseline gets it **working (acc 1.00)** but ships **zero tests**, no CLI-spawn E2E, and no git
process. Bulletproof ships a `node:test` suite that unit-tests `computeStats` **and** spawns the real
CLI (`e2e 1.00`) — but the eval caught **two genuine defects**: it **committed to `master`** instead
of a feature branch (`process 0.00 ⚠main!` — inconsistent with `map-limit`/`truncate`, where it
*did* branch), and its green 18-test suite **weakly guards `cli.ts` under mutation** (`test-real 0.06`
— partly shallow assertions on I/O plumbing, partly the textual engine's limit on CLI-heavy files).
Exactly the eval's job: surfacing the skill's own quality/discipline gaps on a real deliverable, not
flattering it.

**Honest headline:** a capable base model already ceilings on 3 of 4 tasks — the hand-authored
"traps" mostly don't trap a strong modern model. The skill's one measurable win is `uid` (weak-RNG /
needless-dep), where baseline is right only ~⅓ of the time and the skill makes it reliable. On every
task the bulletproof arm is **4–6× slower** and over-engineers (scaffolds vitest + coverage +
`npm install`) — now addressed by the skill's "right-size the effort" guidance (a follow-up run of
`map-limit` produced just `index.ts` + `index.test.ts` via `node --test`, no `node_modules`,
~6 min → 3 min, same 1.00). `k` is small; treat as directional.

## Status & honest limitations (prototype)

- **Small `k`, four tasks (`paginator`, `map-limit`, `expr-eval`, `uid`), one host (pi).**
  Directional, not a benchmark.
- **pass@k / variance:** implemented (`--runs k` → `mean ± stddev` + clean-rate). Larger `k` and
  proper CIs still wanted.
- **Cost & latency:** the bulletproof arm does far more work (plans, writes tests, sometimes
  `npm install`s a full harness) — 183–360s+ per `uid` run vs ~30–45s for baseline, and it can hit
  the wall-clock cap. Bounded per-run via `--timeout`. Use `--dry-run` for CI plumbing checks.
- **Scoring:** the `forbidden` source-grep is now paired with a `forbiddenDeps` direct-dependency
  check (`package.json`), so adding a needless runtime dep fails `scope` even when the source looks
  clean. Transitive tooling deps (e.g. `nanoid` pulled in by vitest) are intentionally ignored.
- **Sandbox:** runs use the local FS with tools enabled. Hardening (container, network allowlist,
  secret scrub) is deferred — run only against trusted fixture tasks. See `../../EVAL-PLAN.md` §5.
- Not wired into `evals/run.mjs` (which stays fast + dependency-free); this is an opt-in tool.

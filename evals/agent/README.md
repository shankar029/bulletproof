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
  score = runFunctional + runQuality(task, project, ws/arm)    # UNCHANGED v1 scoring
```

The only variable between arms is the skill: **baseline** runs pi with no skill; **bulletproof**
runs pi with `--skill SKILL.md`. Both are isolated from ambient context, extensions,
prompt-templates, and skill discovery (`-nc -ne -np -ns`), so any delta is attributable to
`/bulletproof` alone.

The workspace mirrors the fixture layout (`arm/` next to `shared/`) so the produced module resolves
`../shared/*.ts` and the existing oracle/quality probes score it with **no scoring changes**.

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

**`uid` trap task, pass@k (k=3, pi host).** With a terse, guardrail-free requirement (the SPEC's
"use `node:crypto`, no `Math.random`, no deps" hints withheld), so the skill — not the prompt — is
the only difference:

| arm | mean composite | clean-rate | spread |
|---|---|---|---|
| baseline | 0.80 ± 0.14 | 33% (1/3) | 0.70 – 1.00 |
| bulletproof | 1.00 ± 0.00 | 100% (3/3) | 1.00 – 1.00 |

Both arms always pass the functional oracle; the gap is entirely in reuse/scope (weak-RNG /
needless-dep traps). The skill's value here is **consistency**: baseline *can* reach for
`node:crypto` but only ~⅓ of the time. `paginator` (standard difficulty) ties at 1.00 for both —
the skill doesn't help where a capable model already succeeds. `k=3` is a small sample; treat as
directional.

## Status & honest limitations (prototype)

- **Small `k`, two tasks (`paginator`, `uid`), one host (pi).** Directional, not a benchmark.
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

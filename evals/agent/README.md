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

## Status & honest limitations (prototype)

- **N=1, one task (`paginator`), one host (pi).** This proves the *pipeline*, not a statistic.
- **pass@k / variance:** the next step — run each arm `k` times and report `mean ± CI` + `pass@k`.
  The plumbing (fresh workspace per run) already supports it; only the loop + aggregation remain.
- **Cost:** each live run spends real tokens and wall-clock; the bulletproof arm does far more work
  (tests, E2E, review) than baseline, so it is slower by design. Use `--dry-run` for CI plumbing
  checks; keep live runs deliberate.
- **Sandbox:** runs use the local FS with tools enabled. Hardening (container, network allowlist,
  secret scrub) is deferred — run only against trusted fixture tasks. See `../../EVAL-PLAN.md` §5.
- Not wired into `evals/run.mjs` (which stays fast + dependency-free); this is an opt-in tool.

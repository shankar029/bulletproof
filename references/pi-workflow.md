# Reference: The pi Workflow Layer

This file documents the pi-specific tooling the bulletproof **installer provisions on the `pi`
target** and how the workflow uses it. It is informational for the running agent and a reference
for operators. On Claude Code / Copilot CLI this layer does not exist — the six-phase *method* is
host-portable, but these *capabilities* are pi extensions and pi config with no cross-host
equivalent; supply the equivalent through your host's own tooling.

Install it with `install.sh pi` / `install.ps1 pi` (on by default; `BULLETPROOF_SKILL_ONLY=1`
skips it). Plugins are pinned in [`agent/packages.txt`](../agent/packages.txt); config and the
`search-guard` extension live under `agent/` and are copied into `~/.pi/agent/`.

## Plugins

Installed with `pi install` per pinned spec, so they augment your `settings.json` without
overwriting your provider / model / theme.

| Package | Role in the workflow |
| --- | --- |
| `pi-web-access` | Web search + URL/PDF/repo/video fetch for research |
| `@tintinweb/pi-subagents` | The delegated research / design / verify / review subagents (`Agent`, `get_subagent_result`, `steer_subagent`) |
| `pi-lens` | Real-time LSP, linters, formatters, type-checking |
| `pi-mcp-adapter` | Connect any MCP server |
| `pi-memory` | Durable **long-term** memory across sessions (per-task project state stays in `.ai/<slug>/`, not here) |
| `pi-background-tasks` | Durable background shell jobs — `bg_run`/`bg_status`/`bg_logs`/`bg_kill` |
| `@ff-labs/pi-fff` | Fast, git-aware, frecency-ranked file & content search |
| `@juicesharp/rpiv-todo` | Live persistent todo overlay for the phase/increment loop |
| `pi-browser-debug` | Playwright/CDP browser automation for **debugging** apps (console, network, JS) — the debug counterpart to agent-browser's verification role |

## Fast search: `grep`/`find` *are* the fast tools

`agent/pi-fff.json` sets fff to **`override` mode**: fff registers itself under the built-in tool
*names* `grep`, `find`, and `multi_grep` (not `ffgrep`/`fffind`). So every agent whose allowlist
already says `tools: read, grep, find, …` — including subagents you don't control — silently gets
the fast, git-aware, frecency-ranked implementations with **no frontmatter change**. This makes
the fast path the *default* path.

**Complement it with a per-repo `.ignore` file.** ripgrep/fd/fff all honour `.ignore`. Excluding
committed binaries and build output (e.g. `*.zip`, `dist/`, `bin/`, large fixtures) is the other
half of the story: on a large repo it can cut `rg` from tens of seconds to a few. Add one at the
repo root when a project carries heavy non-source files.

## `search-guard`: the slow path is blocked, not discouraged

`agent/extensions/search-guard/` is a `tool_call` hook with two jobs:

1. **Block pathological repo-wide scans before they run** — `grep -r`/`--recursive`,
   `--include=*`, `find .`/`find /`, `ls -R`, `dir /s`. The block message names the fast
   alternative so the model self-corrects. It **allows** `git grep`, non-recursive `grep`, `grep`
   used as a pipe filter, and `find -maxdepth ≤3`. Escape hatch: append `#allow-slow-search` to
   the command when a full scan is genuinely intended.
2. **Bound every unbounded bash call.** pi's `bash` tool declares `timeout` as optional with *no
   default*, so a command that never returns wedges its agent permanently (the tool never
   settles, `tool_execution_end` never fires, the parent waits forever). The hook fills in a
   wall-clock bound when the model left one out — **300s** ordinarily, **1800s** for builds,
   installs and test suites. An explicit model-supplied `timeout` always wins.

Prompt rules alone did not prevent the original wedge this exists for: an agent with a working
fast `grep` tool, which it had already used successfully, still shelled out to `grep -r` and lost
a whole research phase to the deadline. The override makes the fast path default; the guard makes
the slow path impossible. Rule logic is dependency-free in `rules.ts` with a suite in
`rules.test.mjs` (`npx tsx rules.test.mjs`). The long-running list is a **living allowlist** —
extend it for a stack it does not yet cover (add the package manager / build / test binary), it
only raises the ceiling, never removes it.

## Why plugins are pinned but bulletproof is not

The plugins in `packages.txt` are pinned to **exact versions** so every machine installs the
identical set and nothing drifts silently under `pi update`. To upgrade one, edit its line (or run
`pi install npm:<pkg>@<newversion>`) and re-commit. The **bulletproof** skill/agent is
deliberately *not* pinned here — the installer resolves it from its own repo — so pinning lives
with whoever cuts the release, not with this layer.

## Verifying pins

A pin makes the install *reproducible*; it does not make it *correct*. Both are needed, so every
line in `packages.txt` carries a provenance comment recording what was checked, when, against
which pi version, and how. The installers strip `#` to end-of-line, so these are comments — no
parser change, and `install.sh`/`install.ps1` still emit the same specs.

Three states, in increasing strength:

| State | Means | Cost |
| --- | --- | --- |
| `unverified` | Neither check has been run at the stated pi version. | — |
| `resolved` | The pinned spec installs and loads. Says nothing about behaviour. | seconds |
| `exercised` | The specific tool this workflow depends on was invoked and returned a correct result. **Names the tool.** | a real call |

Only `exercised` is evidence the workflow's dependency actually holds — a package can resolve
perfectly and still have moved the tool out from under us. Prefer it for anything a phase gate
relies on (subagents for Phases 1/5/6, fff for research search, web access for docs).

**On every version bump, re-verify and stamp the new date.** Never carry an old date forward
across a bump: the date must describe the version on the line above it, or it is a false claim of
the exact kind Prime Directive 1 forbids. If you bump without re-checking, write `unverified` —
that is an honest state, not a failure.

Cheap `resolved` sweep for the whole set:

```bash
cd ~/.pi/agent/npm/node_modules && pi --version
for p in pi-web-access @tintinweb/pi-subagents pi-lens pi-mcp-adapter pi-memory \
         pi-background-tasks @ff-labs/pi-fff @juicesharp/rpiv-todo pi-browser-debug; do
  echo "$p $(node -p "require('./$p/package.json').version" 2>/dev/null || echo NOT-INSTALLED)"
done
```

Compare that output against the pinned specs; any mismatch means the machine is not running the
layer this repo describes. `exercised` has no script — it means calling the tool.

## The `bpi` launcher

The `pi` installer also generates `~/.pi/agent/prompts/bulletproof.system.md` from the agent file
and wires a `bpi` shell function into your profile, so `bpi "<req>"` launches the drift-proof
agent without the full `--append-system-prompt` line. Tier flags: `bpi --fast "…"` / `--full "…"`
(bash/zsh) or `bpi -Fast` / `-Full` (PowerShell). See [`install/pi.md`](../install/pi.md).

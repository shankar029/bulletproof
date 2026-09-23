# Install for pi

Bulletproof runs on pi three ways, all from one canonical `SKILL.md`:

- **Skill** — `/skill:bulletproof` loads the workflow into your current agent. Simplest; can
  drift if the model doesn't reload it.
- **Agent** — a `bulletproof` agent whose *system prompt is the workflow*, so it cannot drift,
  plus four scoped role subagents it delegates to.
- **Prompt template** — the `/bulletproof` slash command, a thin wrapper that loads the skill.

## Quick install (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) pi
```

That installs:

| What | Where | Gives you |
| --- | --- | --- |
| Skill | `~/.agents/skills/bulletproof/` | `/skill:bulletproof` |
| Prompt template | `~/.pi/agent/prompts/bulletproof.md` | `/bulletproof <requirement>` |
| Agent + role subagents | `~/.pi/agent/agents/bulletproof*.md` | run it as an agent |
| System prompt | `~/.pi/agent/prompts/bulletproof.system.md` | `--append-system-prompt` launch |
| **`bpi` shell function** | `~/.bashrc` / `~/.zshrc` / `$PROFILE` | `bpi "<req>"` (reload your shell once) |
| **Workflow layer** | `~/.pi/agent/` (config, `extensions/`, plugins) | the pi capabilities the workflow assumes |

The installer substitutes the real skill path into the agent files, so they keep working after
install.

## The pi workflow layer

The `pi` target installs more than the skill: it provisions the whole environment the workflow
assumes — the plugins it calls, plus config and hooks that make search fast and bound every
shell call. This runs by default; set **`BULLETPROOF_SKILL_ONLY=1`** to install only the skill +
agents + `bpi` and skip it.

| Piece | Where | What it does |
| --- | --- | --- |
| Plugins (pinned in [`agent/packages.txt`](../agent/packages.txt)) | `pi install` per spec | web access, subagents, LSP/lint, MCP, memory, background tasks, fast search, todo overlay, browser debug |
| `pi-fff.json` (fff `override` mode) | `~/.pi/agent/pi-fff.json` | the built-in tool names `grep`/`find`/`multi_grep` resolve to the fast, git-aware fff impls — no allowlist change, subagents included |
| `search-guard` extension | `~/.pi/agent/extensions/search-guard/` | blocks repo-wide `grep -r`/`find .` before they run and bounds every unbounded bash call (300s / 1800s) |

Plugins install with `pi install`, so your existing provider/model/theme in `settings.json` are
left untouched. `pi-browser-debug` also pulls a Playwright Chromium binary.

> This layer is **pi-only** — it is pi extensions and pi config with no Claude Code / Copilot CLI
> equivalent. The six-phase *method* is host-portable; these *capabilities* are not.

Prefer to do it manually? Steps below.

## Manual install

### 1. Install the skill

Copy the skill into a pi skills location (global shown; use `.pi/skills/` for a single project):

```bash
mkdir -p ~/.agents/skills/bulletproof
cp -r SKILL.md references scripts assets ~/.agents/skills/bulletproof/
```

pi discovers `~/.agents/skills/` automatically. Verify with `/skill:bulletproof` in a session.

### 2. Install the slash command (optional)

```bash
mkdir -p ~/.pi/agent/prompts
cp launchers/pi/prompts/bulletproof.md ~/.pi/agent/prompts/bulletproof.md
```

(Single project instead: `mkdir -p .pi/prompts && cp launchers/pi/prompts/bulletproof.md .pi/prompts/`.)

### 3. Install the agents (optional, drift-proof)

Copy the agent files, substituting your skill path for the `{{BULLETPROOF_SKILL_DIR}}` token:

```bash
mkdir -p ~/.pi/agent/agents
SKILL_DIR="$HOME/.agents/skills/bulletproof"
for f in launchers/pi/agents/*.md; do
  sed "s#{{BULLETPROOF_SKILL_DIR}}#$SKILL_DIR#g" "$f" > ~/.pi/agent/agents/"$(basename "$f")"
done
# The system prompt for --append-system-prompt launches (strip the frontmatter):
awk 'BEGIN{fm=0}/^---$/{fm++;next}fm>=2' ~/.pi/agent/agents/bulletproof.md \
  > ~/.pi/agent/prompts/bulletproof.system.md
```

pi discovers `~/.pi/agent/agents/` automatically. Verify by asking any agent to list
`subagent_type`s starting with `bulletproof`.

## The agents

| Agent | Role | Scope |
| --- | --- | --- |
| `bulletproof` | Orchestrator — the full six-phase loop and gates | main agent or subagent |
| `bulletproof-researcher` | Phase 1 research | read-only |
| `bulletproof-design-reviewer` | Phase 2b design review | read-only, prefer a different model |
| `bulletproof-verifier` | Phase 5 end-to-end verification | read + author tests, no product code |
| `bulletproof-reviewer` | Phase 6 review + reconciliation | read/execute, no writes |

The orchestrator delegates the four mandatory-delegated phases to these roles so each runs with
fresh, independent context. On a trivial change it runs everything inline and spawns none.

> **Models are pinned in the frontmatter** (`claude-opus-5` / `claude-sonnet-5` / `gpt-5.6-sol`).
> The two review roles deliberately use a different model family for independence. If you use
> different providers, edit the `model:` line in each `~/.pi/agent/agents/bulletproof*.md`.

## Use

### As a skill or slash command

```
/bulletproof add rate limiting to the /login endpoint (max 5/min per IP)
/skill:bulletproof ./docs/feature-checkout.md
```

### As the main agent (drift-proof)

```bash
pi --append-system-prompt ~/.pi/agent/prompts/bulletproof.system.md \
   "add rate limiting to the /login endpoint (max 5/min per IP)"
```

**The installer already wires this for you as `bpi`** — it generates `bulletproof.system.md` and
adds a `bpi` function to your shell profile (`~/.bashrc`/`~/.zshrc`, or `$PROFILE` on Windows).
Reload your shell once, then `bpi "<requirement>"` runs the drift-proof agent while plain `pi`
stays your default. The definitions below are what it installs — reproduce or customize them if
you did a manual install. PowerShell (`$PROFILE`):

```powershell
function bpi {
    param([switch]$Fast, [switch]$Full,
          [Parameter(ValueFromRemainingArguments=$true)][string[]]$Prompt)
    $sys  = "$HOME/.pi/agent/prompts/bulletproof.system.md"
    $text = ($Prompt -join " ")
    if ($Fast) { $text = "mode: fast`n$text" } elseif ($Full) { $text = "mode: full`n$text" }
    if ([string]::IsNullOrWhiteSpace($text)) { pi --append-system-prompt $sys }
    else { pi --append-system-prompt $sys $text }
}
```

bash/zsh (`~/.bashrc`):

```bash
bpi() { pi --append-system-prompt "$HOME/.pi/agent/prompts/bulletproof.system.md" "$@"; }
```

Then `bpi "<requirement>"` runs the drift-proof agent; plain `pi` stays your default agent.

## Mode flags — override the automatic tier

The agent right-sizes ceremony by default: a trivial change takes the inline short path; anything
substantive runs the full six-phase loop with delegation. Force it with a token in the request:

| Flag (any of) | Effect |
| --- | --- |
| `mode: full`, `--full`, `[full]` | complete six-phase loop **with delegation**, even for a tiny change |
| `mode: fast`, `--fast`, `[fast]` | inline short path, **no subagents**, even for a larger change |
| *(omitted)* | auto-classify by tier |

```
mode: fast   add a debug log line to the cache loader
mode: full   fix the typo in the payment error message
```

With the PowerShell alias: `bpi -Fast "<req>"` or `bpi -Full "<req>"`.

Two guardrails hold even in fast mode — they are never overridden:

1. **It still stops the line.** If a forced-fast change turns out to need a real design decision
   or breaks tests it can't fix inline, it halts, records the blocker, and recommends `mode: full`.
2. **It still proves the change.** Fast mode runs the real test suite and self-review; it skips
   *delegation and heavy artifacts*, not *verification*. A fast run that can't prove the change
   works says so rather than claiming a pass.

Continue with the [user guide](../docs/user-guide.md) for approvals, unattended execution,
resuming interrupted work and reading the delivery evidence.

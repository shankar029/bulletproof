# Install for Claude Code

> **Skill only — no workflow layer.** The `claude` target installs the bulletproof skill and the
> `/bulletproof` slash command, and nothing else. The pi *workflow layer* (installed plugins for
> subagents, fast search, background jobs, memory, browser debugging, plus the `search-guard`
> hook and fast-search override — see [`../references/pi-workflow.md`](../references/pi-workflow.md))
> is **pi-specific and does not install here**. The six-phase method is fully portable, but where
> it calls for delegation, background jobs, fast search or a browser debugger, supply the
> equivalent through Claude Code's own tooling.

## Quick install (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- claude
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) claude
```

That drops the skill in `~/.claude/skills/bulletproof/` and the command in `~/.claude/commands/`.
Prefer to do it manually? Steps below.

## Manual install

Two files: the skill + the `/bulletproof` slash command.

## 1. Install the skill

```bash
mkdir -p ~/.claude/skills/bulletproof
cp -r SKILL.md references scripts assets ~/.claude/skills/bulletproof/
```

Claude Code auto-discovers `~/.claude/skills/`. (Per project: `.claude/skills/bulletproof/`.)

## 2. Install the slash command

```bash
mkdir -p ~/.claude/commands
cp launchers/claude/commands/bulletproof.md ~/.claude/commands/bulletproof.md
```

(Per project instead: `mkdir -p .claude/commands && cp launchers/claude/commands/bulletproof.md .claude/commands/`.)

> The command references the skill via `@bulletproof/SKILL.md`. If Claude can't resolve that
> path, edit the command to point at the absolute skill path, e.g.
> `@~/.claude/skills/bulletproof/SKILL.md`.

## Use

```
/bulletproof add rate limiting to the /login endpoint (max 5/min per IP)
/bulletproof ./docs/feature-checkout.md
```

Continue with the [user guide](../docs/user-guide.md) for approvals, unattended execution,
resuming interrupted work and reading the delivery evidence.

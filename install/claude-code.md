# Install for Claude Code

Two files: the skill + the `/bulletproof` slash command.

## 1. Install the skill
```bash
mkdir -p ~/.claude/skills/bulletproof
cp -r SKILL.md references ~/.claude/skills/bulletproof/
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

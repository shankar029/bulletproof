# Install for pi

Two files: the skill (the brain) + a prompt template (the `/bulletproof` command).

## 1. Install the skill
Copy the skill into a pi skills location (global shown; use `.pi/skills/` for a single project):

```bash
mkdir -p ~/.agents/skills/bulletproof
cp -r SKILL.md references ~/.agents/skills/bulletproof/
```

pi discovers `~/.agents/skills/` automatically. Verify with `/skill:bulletproof` in a session.

## 2. Install the slash command
```bash
mkdir -p ~/.pi/agent/prompts
cp launchers/pi/prompts/bulletproof.md ~/.pi/agent/prompts/bulletproof.md
```

(For a single project instead: `mkdir -p .pi/prompts && cp launchers/pi/prompts/bulletproof.md .pi/prompts/`.)

## Use
```
/bulletproof add rate limiting to the /login endpoint (max 5/min per IP)
/bulletproof ./docs/feature-checkout.md
/bulletproof https://github.com/acme/app/issues/123
```

The template tells pi to load the `bulletproof` skill and run the full loop. You can also run
`/skill:bulletproof <requirement>` directly without the template.

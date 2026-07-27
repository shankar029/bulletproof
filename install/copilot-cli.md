# Install for GitHub Copilot CLI

Copilot CLI does **not** support custom slash commands (upstream issues #618, #1004), so
`/bulletproof` isn't available. Instead, install a **custom agent** that embodies the workflow.

## 1. Install the playbook + custom agent
```bash
# playbook the agent references
mkdir -p ~/.copilot/bulletproof
cp -r SKILL.md references ~/.copilot/bulletproof/

# custom agent
mkdir -p ~/.copilot/agents
cp launchers/copilot/agents/bulletproof.agent.md ~/.copilot/agents/bulletproof.agent.md
```

(Per project instead: put the agent in `.github/agents/bulletproof.agent.md` and the playbook
in the repo, e.g. `docs/bulletproof/`.)

## Use
Start Copilot CLI with the custom agent, then give it the requirement:

```bash
copilot --agent bulletproof
# then type: add rate limiting to the /login endpoint (max 5/min per IP)
```

(Check `copilot --help` for the exact flag in your version; some builds select agents via an
interactive picker or `/agents`.)

## Optional: make it the default behavior
Add the prime directives to `AGENTS.md` or `.github/copilot-instructions.md` at the repo root so
every Copilot CLI session works this way without selecting the agent.

# Install for GitHub Copilot CLI

The shipped Copilot CLI integration is a **custom agent** that loads the Bulletproof
workflow. Host capabilities evolve: use the agent-selection mechanism supported by your
installed CLI rather than assuming the pi/Claude slash-command launcher works here.

> **Custom agent only — no workflow layer.** The `copilot` target installs the custom agent and
> nothing else. The pi *workflow layer* (installed plugins for subagents, fast search, background
> jobs, memory, browser debugging, plus the `search-guard` hook and fast-search override — see
> [`../references/pi-workflow.md`](../references/pi-workflow.md)) is **pi-specific and does not
> install here**. The six-phase method is portable, but supply the equivalent capabilities
> (delegation, background jobs, fast search, a browser debugger) through the Copilot CLI's own
> tooling.

## Quick install (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- copilot
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) copilot
```

That drops the playbook in `~/.copilot/bulletproof/` and the agent in `~/.copilot/agents/`.
Prefer to do it manually? Steps below.

## Manual install

### 1. Install the playbook + custom agent

```bash
# playbook the agent references
mkdir -p ~/.copilot/bulletproof
cp -r SKILL.md references scripts assets ~/.copilot/bulletproof/

# custom agent
mkdir -p ~/.copilot/agents
cp launchers/copilot/agents/bulletproof.agent.md ~/.copilot/agents/bulletproof.agent.md
```

(Per project instead: put the agent in `.github/agents/bulletproof.agent.md` and the playbook
in repo-root `bulletproof/`, matching the shipped launcher's `bulletproof/SKILL.md` reference.
If you choose another location, update that reference in the copied launcher.)

## Use

Start Copilot CLI with the custom agent, then give it the requirement:

```bash
copilot --agent bulletproof
# then type: add rate limiting to the /login endpoint (max 5/min per IP)
```

(Check `copilot --help` for the exact flag in your version; some builds select agents via an
interactive picker or `/agents`.)

Continue with the [user guide](../docs/user-guide.md) for your first requirement, design
approval, unattended operation, resuming a workspace and interpreting the final report.
Installing the agent does not grant repository permissions or create independent subagents
when the host does not expose them.

## Optional: make it the default behavior

Add the prime directives to `AGENTS.md` or `.github/copilot-instructions.md` at the repo root so
every Copilot CLI session works this way without selecting the agent.

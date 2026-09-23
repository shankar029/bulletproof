![Bulletproof: from requirement to reviewed delivery, with evidence at every step](assets/bulletproof-banner.svg)

**A delivery workflow for coding agents. Design first. Test real behavior. Show the proof.**

Works with pi, Claude Code and the GitHub Copilot CLI custom-agent launcher.

[Quick start](#quick-start) · [Features](#features-at-a-glance) ·
[User guide](docs/user-guide.md) · [Operator guide](references/workflow-gates.md) ·
[Evidence & limits](#evidence-and-current-limits) ·
[Contribute](CONTRIBUTING.md)

---

## From a prompt to a delivery record

Bulletproof gives an agent a repeatable way to turn a requirement, document or issue into a
reviewed change: investigate the real code, design before editing, build in small increments,
exercise the actual interface, and preserve evidence alongside the work.

It is **a skill plus supporting tools**, not a replacement model or a guarantee of success.
When a required check cannot be proved, the right result is a named blocker, not an invented pass.

On **pi**, the installer goes further than the skill: it provisions the whole workflow
environment the skill assumes — the plugins, search/timeout hooks, and fast-search config — so a
fresh machine is ready to deliver. See [The pi workflow layer](#the-pi-workflow-layer-pi).

```text
Understand  -->  Design  -->  Plan  -->  Build  -->  Verify  -->  Review & ship
   sources       approval     slices     tests      real E2E       evidence
```

Small, obvious changes take a short path. Features, bug fixes and other substantive changes
use the full six-phase workflow.

## Quick start

Choose one installer target: `pi`, `claude`, or `copilot`.

**macOS / Linux / Git Bash**

```bash
curl -fsSL https://raw.githubusercontent.com/shankar029/bulletproof/main/install.sh | sh -s -- pi
```

**Windows PowerShell**

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/shankar029/bulletproof/main/install.ps1))) copilot
```

These commands download and execute an installer. Review it first or use the manual instructions
if that better fits your environment. The default download is `main`, not an unpublished local
feature branch; `BULLETPROOF_REF` selects another existing ref.

| Host | Start the workflow | What the installer sets up | Installation details |
| --- | --- | --- | --- |
| pi | `/bulletproof <requirement>` (skill), the `bpi` command, or a drift-proof **agent** (see below) | skill + agent **and the full [pi workflow layer](#the-pi-workflow-layer-pi)** (plugins, hooks, fast-search config, `bpi`) | [Skill, agent and mode flags](install/pi.md) |
| Claude Code | `/bulletproof <requirement>` | skill + slash command **only** | [Skill and command launcher](install/claude-code.md) |
| Copilot CLI | `copilot --agent bulletproof`, then enter the requirement | custom agent **only** | [Custom-agent launcher](install/copilot-cli.md) |

The shipped Copilot integration is a custom agent. Check your CLI version's help for available
agent selection; do not assume slash-command behavior is identical across hosts.

> **The workflow layer is pi-specific.** The plugins, search/timeout hooks, fff override and the
> `bpi` launcher install **only on the `pi` target** — they are pi extensions and pi config with
> no Claude Code / Copilot CLI equivalent. On those hosts the installer sets up the skill (and
> the Copilot custom agent) exactly as before; the six-phase *method* is fully portable, but you
> supply the equivalent capabilities (search, background jobs, browser, etc.) through your host's
> own tooling. To install the skill alone on pi and skip the workflow layer, set
> `BULLETPROOF_SKILL_ONLY=1`.

### Run it as an agent (pi)

A skill has to be *loaded* each session and can drift; an **agent's system prompt *is* the
workflow**, so it cannot. The pi installer also drops a `bulletproof` agent plus four scoped
role subagents (`bulletproof-researcher`, `-design-reviewer`, `-verifier`, `-reviewer`) that the
full loop delegates to. Ways to run, same workflow:

| Invocation | Runs as | Use when |
| --- | --- | --- |
| `/skill:bulletproof <req>` | skill in your current agent | quick, occasional use |
| `bpi "<req>"` (installed shell function) | **main agent**, drift-proof | the everyday shortcut for the line below |
| `pi --append-system-prompt ~/.pi/agent/prompts/bulletproof.system.md "<req>"` | **main agent** | you want it drift-proof for the whole session |
| `Agent` tool → `subagent_type: bulletproof` | delegated subagent | orchestrating from another agent |

The `pi` installer generates `~/.pi/agent/prompts/bulletproof.system.md` from the agent file and
wires a **`bpi`** function into your shell profile (`$PROFILE` on Windows, `~/.bashrc`/`~/.zshrc`
on Linux/macOS), so you don't have to type the full `--append-system-prompt` line — reload your
shell once after install. Force a tier with `bpi --fast "..."` / `--full "..."` (bash/zsh) or
`bpi -Fast "..."` / `-Full "..."` (PowerShell).

**Mode flags — override the automatic tier.** By default the agent right-sizes the ceremony
(trivial → short path, everything else → full loop). Force it by putting a token in the request:

| Flag | Effect |
| --- | --- |
| `mode: full` | complete six-phase loop **with delegation**, even for a tiny change |
| `mode: fast` | inline short path, **no subagents**, even for a larger change |
| *(omitted)* | auto-classify by tier |

Fast mode still runs the real test suite and **stops the line** if the change turns out to need
full rigour — it skips delegation and heavy artifacts, never the proof. Details and a shell-alias
recipe are in the [pi install guide](install/pi.md).

```text
/bulletproof add cursor pagination to the audit API without changing existing clients
/bulletproof fix the stale-cache bug described in docs/cache-incident.md
/bulletproof https://github.com/your-org/your-repo/issues/42
```

In the Copilot custom agent, enter the same requirement without the slash-command prefix.
See the [user guide](docs/user-guide.md) for approvals, unattended work, resuming and troubleshooting.

## The pi workflow layer (pi)

On pi, installing bulletproof is installing an **entire workflow setup**, not just a skill file.
The workflow relies on real capabilities — subagents, background jobs, memory, fast search, a
browser debugger — so the `pi` installer provisions them for you. This is on by default; pass
`BULLETPROOF_SKILL_ONLY=1` to install only the skill + agents.

**Plugins** (pinned in [`agent/packages.txt`](agent/packages.txt), installed with `pi install`,
so your existing provider/model/theme are untouched):

| Package | Why the workflow needs it |
| --- | --- |
| `pi-web-access` | Web search and URL/PDF/repo/video fetching for research |
| `@tintinweb/pi-subagents` | The delegated research / design / verify / review subagents |
| `pi-lens` | Real-time LSP, linters, formatters, type-checking |
| `pi-mcp-adapter` | Connect any MCP server |
| `pi-memory` | Durable long-term memory across sessions (project state stays in `.ai/<slug>/`) |
| `pi-background-tasks` | Durable background shell jobs (dev servers, builds, suites) |
| `@ff-labs/pi-fff` | Fast fuzzy file & content search |
| `@juicesharp/rpiv-todo` | Live persistent todo overlay for the phase/increment loop |
| `pi-browser-debug` | Playwright/CDP browser automation for debugging apps (console, network, JS) |

**Config & hooks** (copied into `~/.pi/agent/`):

- **`pi-fff.json` — fff `override` mode.** fff registers itself under the built-in tool *names*
  `grep`/`find`/`multi_grep`, so every agent allowlist that already says `grep, find` silently
  gets the fast, git-aware, frecency-ranked implementations — including subagents you don't
  control. This makes the fast path the *default* path.
- **`search-guard` extension** ([`agent/extensions/search-guard/`](agent/extensions/search-guard/)).
  A `tool_call` hook that (1) **blocks** pathological repo-wide shell scans (`grep -r`,
  `--include=*`, `find .`/`find /`, `ls -R`, `dir /s`) before they run — naming the fast
  alternative so the model self-corrects — while allowing `git grep`, non-recursive grep, pipe
  filters, and `find -maxdepth ≤3`; and (2) **bounds every unbounded bash call** with a default
  wall-clock timeout (300s ordinarily, 1800s for builds/installs/test suites), because pi's
  `bash` tool has no default and an unbounded hang wedges an agent forever. Escape hatch:
  append `#allow-slow-search`. Dependency-free rules with a 39-case suite
  (`npx tsx rules.test.mjs`).

The **bulletproof** skill + drift-proof agent (and four role subagents) install on top of this
layer, as [above](#run-it-as-an-agent-pi).

> Prompt rules alone did not prevent the wedge these hooks exist for: an agent with a working
> fast `grep` tool, which it had already used successfully, still shelled out to `grep -r` and
> lost a whole research phase to the 300s deadline. The override + guard make the fast path
> binding, not advisory.

## Features at a glance

[Understand](#understand-the-problem-before-changing-the-code) ·
[Build & resume](#build-deliberately-in-increments-that-survive-a-handoff) ·
[Verify](#verify-behavior-not-just-plausible-output) ·
[Scale](#scale-the-workflow-to-the-work)

### Understand the problem before changing the code

| Feature | What it adds |
| --- | --- |
| **Project-aware research** | Reads repository rules, traces behavior and callers, checks reuse candidates, and maps findings to acceptance criteria. [Research](references/research.md) |
| **Explicit uncertainty** | Separates facts, inferences, hypotheses and unknowns. Absence claims include the actual search scope. [Grounding](references/research.md#evidence-and-freshness-rules) |
| **Evidence-driven diagnosis** | Reproduces the original symptom, tests competing explanations, minimizes when useful, and reruns the original scenario after the fix. [Diagnosis](references/diagnosis.md) |
| **Readable program and UX design** | Specifies responsibilities, interfaces, domain vocabulary, interactions and failure modes before code; includes UX approval when relevant. [Design](references/design-doc.md) · [UX](references/ux-design.md) |
| **Interactive design review** | HTML overviews of up to three printed pages, with diagrams, light/dark reading modes, highlights, comments, notes and exported review decisions. [Document theme](references/html-theme.md) |
| **Optional approval portal** | When the separately available `clarity` skill is present, use structured web feedback and uploads for UX review; ordinary approval remains the fallback. It is not bundled with Bulletproof or the same as code clarity. [UX review](references/ux-design.md) |

### Build deliberately, in increments that survive a handoff

| Feature | What it adds |
| --- | --- |
| **Executable planning** | Stable task/check IDs, prerequisites, exact commands, owners, expected outcomes and evidence destinations; unresolved decisions stay visible. [Planning](references/planning.md) |
| **Session-sized delivery** | Cohesive vertical slices, consumer-readiness checks and durable workspaces instead of relying on a long conversation. [Workspace](references/workspace.md) |
| **Current design, retained history** | Reviewed immutable candidates become current through ordinary adoption; later briefs resolve the current pointer instead of rewriting old decisions. [Design history](references/design-doc.md#current-contract-and-retained-revisions) |
| **Test-first implementation** | Small behavioral red/green cycles, independent expectations and real collaborators; setup failures are not behavioral-red proof. [Testing](references/testing-and-e2e.md) |
| **Human-readable code** | Clear main flows, cohesive responsibilities, explicit errors and current rationale rather than inline incident journals. [Code clarity](references/code-clarity.md) |
| **Compatibility-aware changes** | Plans coexistence, migration and rollback; guarded retirement consumes accepted earlier compatibility proof, not a later green result. [Planning](references/planning.md) |
| **Research corrections** | Scoped absence, explicit supersession and source-bound acceptance keep corrected findings distinct from historical claims. [Research](references/research.md#corrections-in-an-adopted-contract) |
| **Focused communication** | Outcome-first updates and explicit blockers; adopted-work readiness comes from actual status, not a separate optimistic tracker. [Communication](references/communication.md) |

### Verify behavior, not just plausible output

| Feature | What it adds |
| --- | --- |
| **Surface-appropriate E2E** | Real browser flows with agent-browser, HTTP requests for services, and actual CLI/library invocation. [E2E](references/testing-and-e2e.md) |
| **Independent roles** | Fresh-context research, verification and review through dedicated `bulletproof-*` role subagents; a self-review is not a substitute for independent acceptance. [Delegation](references/delegation.md) |
| **Guarded command routing** | `status`, `next`, `record`, `close`, `adopt`: registered commands, immutable receipts and current prerequisites. Recovery and positive quality closure remain unavailable. [Operator guide](references/workflow-gates.md) |
| **Deterministic quality reports** | Base/head observations with separate measured status and required-proof completeness. Missing required proof fails closed. [Metrics](references/quality-metrics.md) |
| **Native ESM/CJS mutation evidence** | Diff-scoped mutation, exact test arguments and working directory, native assertion classification, restoration and stale-report rejection. [Mutation](references/quality-metrics.md) |
| **Bounded process execution** | Idle and total time limits, captured output and owned-process cleanup through `scripts/run.py`. [Process runner](scripts/run.py) |
| **Evidence-bound review** | Nine review dimensions, source-backed findings, explicit dispositions and bounded root-cause convergence. [Quality bar](references/quality-bar.md) |
| **An actionable final report** | Delivered and unmet criteria, phase gates, measurements, limitations, follow-ups and publication status in one readable artifact. [Final report](references/final-report.md) |

### Scale the workflow to the work

| Feature | What it adds |
| --- | --- |
| **Whole-app delivery** | A walking skeleton followed by feature slices, not a giant unverified implementation. [App-scale delivery](references/app-scale-delivery.md) |
| **Production readiness** | Relevant operational, rollout and recovery checks when going live is in scope. [Production readiness](references/production-readiness.md) |
| **Safe parallel work** | Explicit dependency and file-ownership boundaries, then verification of the integrated result. [Parallel execution](references/parallel-execution.md) |
| **Portable packaging** | One canonical `SKILL.md`, on-demand references, shared tools/assets and thin per-host launchers. [Architecture](docs/architecture.md) |
| **Regression and live evaluations** | A fixed ten-task corpus plus a separate agent-in-the-loop harness; fixture scores are not live model-effectiveness claims. [Evaluations](evals/README.md) |

**What enforces what?** The skill's phase, research and independent-role rules are procedural
instructions. The workflow CLI checks **commands routed through it**; direct tools can bypass
that boundary. The process runner, measurement tools and HTML review UI are also executable.
None grants host permissions, authenticates declared contexts, creates a sandbox, or establishes
human approval. A host's ability to launch genuinely fresh agents must be verified separately.

## The delivery workspace

Non-trivial tasks preserve their decisions and evidence under `.ai/<slug>/`:

```text
.ai/<slug>/
  state.md                # resume pointer, phase, blockers and next action
  research.md             # scoped, source-backed findings
  design.html             # reviewed program design
  plan.html               # build order and verification plan
  traceability.md         # requirement -> implementation -> proof -> verdict
  review.md               # independent findings and dispositions
  metrics.json            # display copy of the latest quality report
  report.html             # human-readable delivery outcome
  evidence/runs/<run-id>/  # source-bound measurement reports and supporting evidence
```

The agent resumes from these artifacts and rechecks their prerequisites against the current
tree. A checkbox is not proof, and a later review cannot retroactively establish an earlier
approval or compatibility check. Large recordings can be stored separately with durable references.

For adopted tasks, `current-design.json` points to immutable `design-history/` and `contracts/`
records; `workflow.json` owns registrations and `evidence/ledger.json` owns runtime events.
Initial research/design/plan prepare the reviewed candidate **before** adoption. Use the
[operator guide](references/workflow-gates.md) for staging, adoption, handoffs and status;
do not replace the live pointer by hand or import historical execution as new proof.

## Evidence and current limits

**Functional correctness, workflow compliance and model effectiveness are different claims.**
The [fixed-corpus evaluation](evals/README.md), [live harness](evals/agent/README.md) and
[illustrative benchmark](benchmark/README.md) serve different purposes. Compare their methods
before comparing scores.

- Standalone mutation currently classifies **direct native Node tests**. ESM/CJS file discovery
  is supported, but unsupported syntax, languages and runners remain explicitly ungraded.
  Syntax/import/setup failures and timeouts do not count as assertion kills.
- Quality collection depends on installed tools **and complete supported input inventories**.
  Configured collection covers Python literal-import graphs and, with a qualified TypeScript
  binding, JS/TS graphs with fresh accepting replay of the native evidence. Complete scalar,
  coverage and mixed-language mutation collection remain unfinished. Installing an analyzer
  or qualifying its launch does not collect its metrics.
- Required unavailable measurements produce **incomplete/fail**. Passing the functional suites
  does not turn that into a release-quality pass.
- Guarded `work` and `retire` actions require executable commands. Null-command handoffs
  support **checks only**, not manual edits or tool-agent implementation. Confirm this fit
  before adoption; never substitute a no-op command or label implementation as a check.
- All nine metrics remain required. Registered metric commands run unchanged, but successful
  guarded attachment still needs producer-owned run ID, registered argv, source projection
  and raw-validation integration. No accepted metric receipt or positive quality closure is
  available. `close` checks Git membership/bytes/modes and mandatory gates; it cannot finish
  quality closure in this boundary.
- No recovery/reset/orphan-lock-steal command exists. Metadata publication retry after ordinary
  unwind is not process recovery. A Windows symlink-creation case remains environment-unverified
  (`WinError 1314`); earlier timeout-tree cleanup remains UNKNOWN. No cross-platform or
  full-quality result is implied.
- Source hashes detect changes in declared scope; they do not create a filesystem sandbox or
  authenticate a reviewer. Separate agent contexts depend on host capabilities.
- Publishing requires repository permission. A local commit is not an opened PR.

The planner's 37-test/coverage results and the 29-feature evaluation are **historical,
scoped observations**, not current root-suite or root-quality measurements.

For tool setup and exact report/exit semantics, use the [measurement guide](references/quality-metrics.md).
For observed runs, consult their source-bound evidence rather than treating this page as a live dashboard.

## Explore the project

| Start here | Purpose |
| --- | --- |
| [User guide](docs/user-guide.md) | First task, approvals, resume, reports and common problems |
| [Workflow operator guide](references/workflow-gates.md) | Five ordinary verbs, current authority, evidence, denial and interruption limits |
| [Architecture](docs/architecture.md) | Components, boundaries and design rationale |
| [SKILL.md](SKILL.md) | Canonical six-phase operating instructions |
| [References](references/) | Detailed procedures, loaded when relevant |
| [Install guides](install/) | Per-host installation and invocation |
| [Evaluation guide](evals/README.md) | Corpus, scoring and reproduction |
| [Contributing](CONTRIBUTING.md) | Development commands and change conventions |
| [Changelog](CHANGELOG.md) | Recorded release history |

Selective techniques were adapted in original wording from MIT-licensed
[mattpocock/skills](https://github.com/mattpocock/skills/tree/959a8e9f1edc3adbe2f7e3054bb6fbefa6696260);
individual references retain their other acknowledgements. Bulletproof does not bundle those
projects' plugins or imply that their reported results apply here.

---

[MIT licensed](LICENSE) · Contributions welcome · Keep the evidence stronger than the claim.

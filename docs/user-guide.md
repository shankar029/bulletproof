# Using Bulletproof

[README](../README.md) · [Install](../README.md#quick-start) ·
[Operator guide](../references/workflow-gates.md) · [Measurement guide](../references/quality-metrics.md)

Bulletproof is a delivery skill with per-host launchers. You supply the requirement; the
agent follows a source-backed design, implementation and verification workflow. Its tools
support that workflow, but they do not grant permissions or make unsupported checks pass.

## 1. Install for your host

Use the instructions for [pi](../install/pi.md), [Claude Code](../install/claude-code.md)
or [Copilot CLI](../install/copilot-cli.md). The installer copies the canonical skill,
references, scripts and assets into the selected host's user directory.

The default download uses `main`. To install a reviewed local checkout with PowerShell:

```powershell
$env:BULLETPROOF_SRC = (Get-Location).Path
.\install.ps1 copilot
Remove-Item Env:\BULLETPROOF_SRC
```

Run this from the Bulletproof checkout, not your application directory. Installation replaces
that host's existing Bulletproof references, scripts and assets; preserve local customizations
before updating. Setting `BULLETPROOF_REF` selects an existing remote branch, tag or commit for
a downloaded installation. This does not publish an unpushed local commit.

Use the repository's documented runtime requirements for the application being changed.
Bulletproof's Python utilities and native Node reporter have their own requirements; the
[measurement guide](../references/quality-metrics.md) describes their supported routes.
Browser verification additionally requires agent-browser and its browser runtime.

Keep the complete installed `scripts/` directory together, not only `workflow.py`: its
imports and native reporter are part of the runtime. Existing installers and live-harness
bundle staging already copy the complete scripts/references/assets payload; no new install
step or bootstrap generator is needed. Operator examples shown from this checkout use
relative script paths; from your application use the verified installed script paths and
pass the application's actual Git root as `--repo`.

## 2. Describe the outcome

For pi or Claude Code:

```text
/bulletproof add project archiving without deleting task history
```

For the shipped Copilot CLI launcher:

```text
copilot --agent bulletproof
```

Then enter the requirement normally. Your host's help is authoritative for its agent picker.

A useful request states the observable behavior, compatibility constraints and important
failure cases. You can supply a document path or issue URL instead of copying a long spec.
Avoid prescribing implementation details unless they are real constraints.

For example:

> Add project archiving. Archived projects must disappear from the active list but remain
> readable through their existing URLs. Reject new tasks on archived projects with a clear
> API error. Existing task history and exports must remain unchanged.

The agent should turn this into acceptance criteria, inspect the repository and establish
what already exists. A typo or similarly obvious change uses the short path; substantive
behavior uses the full workflow.

## 3. Review decisions before code

For non-trivial work, expect source-backed research and a short HTML design with interfaces,
interactions, alternatives and failure behavior. User-facing work also needs a UX design.

Open the design document from the task workspace. The shared theme provides light/dark mode,
reading controls, highlights, comments and review decisions. Export or copy the review JSON
and return it through your host. Use **Request changes** when the behavior or approach is wrong.

If the separately available **`clarity` skill** is installed, the
[UX procedure](../references/ux-design.md) also supports a structured web approval portal
with comments and uploads. This optional integration is not bundled by the Bulletproof
installers and is distinct from both the built-in HTML review layer and code-clarity guidance.
Without it, use the normal document or host approval path.

Silence is not approval. If you want unattended execution, say so explicitly:

> Run unattended, make reasonable decisions, record assumptions, and stop on unresolved
> safety or access blockers.

An unattended design assumption must remain labeled as such; it is not a human approval receipt.
External actions remain subject to the host's permission rules.

Initial research, design review and planning are procedural and produce a candidate before
adoption. For guarded work, the [operator guide](../references/workflow-gates.md) explains
immutable revision staging and ordinary `adopt` (event → workflow → pointer). Never copy a
candidate directly onto the live pointer or mark earlier work admitted after the fact.
On later revisions, old documents remain history; `current-design.json` selects the current
retained document/contract. An exported HTML decision alone is not runtime adoption.

## 4. Follow the evidence, not the activity

The plan should identify independently useful increments, their dependencies, exact checks,
owners and expected results. During implementation, expect concise updates when a phase,
decision or blocker changes rather than a stream of tool narration.

After adoption, expect updates derived from actual `status` for the intended target.
`next` runs only a registered action; `record` accepts an admitted return without changing
its producer. Null-command **check** handoffs do not launch an agent—the host must supply the
actual fresh role. Guarded work/retirement requires executable commands; manual editing or
tool-agent implementation has no supported guarded handoff. Check this before adoption.
Do not clear existing authority, substitute a no-op command or relabel work as a check to
get past that limitation. Ready action, executed command, accepted check and closed increment are different.
Required red and compatibility receipts must precede the action consuming them.
Corrected research retains superseded claims and source/search scope instead of silently
rewriting history. Direct test commands remain development/diagnostic evidence, not guarded
receipts. These checks do not authenticate declared roles or prevent access outside the CLI.

Meaningful proof includes actual test assertions and the real interface: browser flows,
HTTP requests, CLI execution or library calls. A process failing to start is not a behavioral
regression test. Independent verification and review are separate roles, not renamed self-review.

See [testing and E2E](../references/testing-and-e2e.md),
[diagnosis](../references/diagnosis.md) and [delegation](../references/delegation.md).

## 5. Resume interrupted work

Give a fresh agent the same repository and task workspace:

> Resume `.ai/project-archiving` from its artifacts. Reconcile the current tree and
> prerequisite evidence before dispatching the next task.

The entry point is `state.md`, followed by the referenced design, plan and traceability.
For adopted work, resolve `current-design.json` and run actual `status` before dispatch.
An inconsistent live workflow/pointer is a blocker, not a reason to use an older overview.
The agent must revalidate affected evidence after source or requirements change. Preserve
unaffected proof; do not erase the workspace or restart discovery just because the chat is new.

The workspace is durable context, not a promise of automatic recovery after every process
failure. A dead parent process does not establish that its children stopped. Do not delete
locks or replay a command solely because the lock looks old.
There is no `recover`, reset or orphan-lock-steal command. Repeating exact adoption after an
ordinary exception unwinds may complete finite metadata publication states; that is not
recovery after process death. Preserve uncertain lifetime evidence and report the blocker.

## 6. Read the final report

The main handoff is `.ai/<slug>/report.html`. It should answer:

| Question | Where to look |
|---|---|
| What was delivered, and what was not? | Outcome and acceptance verdicts |
| Which checks actually ran? | Commands, test results and evidence references |
| Are all phase gates satisfied? | G1-G6 status and blocker reasons |
| Are the required measurements complete? | Quality report completeness, not just numeric scores |
| Is the result committed and published? | Separate commit and PR/publication status |
| What remains uncertain? | Limitations, assumptions and follow-ups |

`metrics.json` is a display copy. Authoritative measurement reports are bound to their run and
source under `evidence/runs/<run-id>/`; read those bindings before reusing a result.
The standalone mutation tool no longer publishes a latest `mutation.json` alias.

Currently all nine quality metrics remain mandatory, and registered metric commands run
unchanged but produce no accepted guarded metric receipt. Successful attachment needs the
later producer-owned ID/registered-argv/source-projection/raw-validation bridge. `close`
checks Git then mandatory gates, but positive quality closure is unavailable.
Configured collection covers Python literal-import graphs and, with a qualified TypeScript
binding, JS/TS graphs whose native evidence is checked through fresh accepting replay.
That does not complete scalar, coverage or mixed-language mutation collection, or supply
the missing guarded metric bridge. A symlink-creation test remains
Windows-environment-unverified (`WinError 1314`), and earlier timeout cleanup remains UNKNOWN.
Do not read a selected passing suite as full-quality or cross-platform proof.
Historical planner 37-test/coverage and 29-feature evaluation statistics retain their original
scope; they are not today's root-quality dashboard.

## Common problems

| Symptom | What to do |
|---|---|
| The command or custom agent is missing | Check the installation destination and your host's actual invocation support. |
| Work resumes from the wrong requirement | Point to the exact task slug; do not reuse a workspace belonging to another task. |
| Design is waiting for approval | Return the decision through the host; do not assume the agent can infer it from a browser tab. |
| Tests pass but quality is incomplete | Read each missing prerequisite. Functional success and complete quality proof are different gates. |
| Mutation refuses a dirty tree | Preserve the intended source changes in a safe commit; do not discard work merely to satisfy the tool. |
| Mutation is ungraded | Inspect syntax, runner and assertion classification. Unsupported languages and setup failures are not killed mutants. |
| An analyzer is installed but still unavailable | Installation alone does not provide complete language/file inventory or an implemented collector. |
| A process times out | Inspect captured output and owned-process cleanup; use the documented bounded recovery, not repeated blind retries. |
| A push or PR is forbidden | Retain the local commit and report the permission failure. Do not bypass repository or account policy. |

## Choose the right deeper guide

- [Planning](../references/planning.md): executable handoffs, compatibility and revision.
- [Workflow operator guide](../references/workflow-gates.md): adoption, five ordinary verbs,
  evidence/status, closure denial and unsupported recovery.
- [Workspace](../references/workspace.md): state, traceability and evidence freshness.
- [Quality metrics](../references/quality-metrics.md): tool support, completeness and mutation.
- [Whole-app delivery](../references/app-scale-delivery.md): walking skeleton and vertical slices.
- [Production readiness](../references/production-readiness.md): operational and rollout checks.
- [Contributing](../CONTRIBUTING.md): this repository's development and evaluation commands.

The fixed corpus is a regression instrument, not proof that every model will follow every
instruction. A case study is an observation with limits, not a universal delivery guarantee.

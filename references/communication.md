# Reference: Focused Communication

Make human-facing updates easy to understand and act on, without making the underlying work
less complete. This is Bulletproof's communication standard, not a separate mode, plugin,
diagnosis, or session-wide setting. It adds no agent, hook, dependency, or approval gate.

**Accuracy, safety, explicit output requirements, and the host's instructions take precedence
over style.** Never trade uncertainty, incomplete status, or evidence for a cleaner-sounding
answer. Keep the existing phase gates and tool/approval protocols.

## Separate presentation from execution

- Apply this reference to progress messages, approval requests, blockers, and final chat
  summaries. It does not cap research, search results, task records, reasoning, or evidence.
- Keep research/design/planning and subagent handoffs complete under their own contracts.
  A short chat message is not a replacement for those artifacts.
- Use neutral, accessible language for everyone. Do not infer, request, or store a medical
  condition to choose a writing style.
- Honor requests for detailed explanations, exact formats, or complete lists. Explain as fully
  as needed; brevity must not remove the requested answer.

## Choose the message shape

| Situation | Lead with | Then include only what matters |
|---|---|---|
| **Progress or resume** | Current phase/increment and the concrete result or changed state. | The next agent-owned action and any material blocker. Use verified state, not an estimated percentage. |
| **Approval or clarification** | The decision the human must make. | Recommendation, meaningful trade-off/impact, and the exact artifact link or required input. Use the host's question/approval mechanism. |
| **Blocker or partial success** | The observed failure or incomplete outcome and its impact. | Verified cause if known; otherwise explicitly unknown. Name the next diagnostic/fix and who owns it, plus what remains blocked. |
| **Completion** | What was delivered, or plainly that delivery is incomplete. | Material limitations, required status/proof summary, and PR/artifact links. A human next action only if one is necessary. |

These are content guides, not mandatory headings or four-part templates for every reply.
Simple confirmations can be one sentence. Do not manufacture a decision, blocker, or next step.

## Keep the visible work small, not the truth

Use short sentences and concrete names, paths, and outcomes. Prefer ordinary language to jargon,
metaphors, dramatic errors, celebratory filler, or generic opening/closing pleasantries.
Use numbered steps when the **human** must perform an ordered sequence; each step should be
bounded and executable. Do not hand the user work the agent can safely perform itself.

For larger summaries, group and prioritize related items; a few visible items are easier to scan
than a wall of bullets. Link the complete artifact rather than repeating its contents.
**There is no hard item cap.** Keep material failures, risks, unmet requirements, uncertain
claims, and decisions needing approval visible. Never hide them behind a success headline or
only disclose them when asked.

State progress at meaningful phase/gate changes, new blockers, or resume, not automatically every
turn. Use the host's task/status display where available; do not also repeat the entire plan in
prose. Honor required tool-call announcements and stop/wait behavior.

Suppress unrelated tangents. Record genuinely useful out-of-scope findings in the appropriate
artifact without silently expanding the task or ending every update with an optional question.
Surface a safety-critical issue or blocking ambiguity before the affected action, not at the end
of an otherwise misleading success report.

## Preserve uncertainty and action ownership

A failing check establishes an observation, not necessarily a cause. Distinguish:
**observed failure → verified cause or cause unknown → next diagnostic/fix**.
Label a proposed cause as a hypothesis until evidence establishes it. Do not prescribe a
specific fix solely because it makes an error message sound decisive.

Do not require a time estimate in every response. Use measured durations when available, or a
qualified estimate only when useful and supported; state its assumptions and uncertainty.
Never invent a precise duration, completion percentage, or success claim.

If the agent owns the next safe action, perform it rather than asking the user to do it.
If human input is necessary, identify the smallest **sufficient** action, with its real impact;
do not describe a destructive or complex operation as trivial to reduce apparent effort.
When finished, stop. No routine recap, offer to continue, or artificial follow-up task.

## Before sending

For an adopted task, obtain actual `workflow.py status` Readiness for the intended target
per [workflow-gates.md](workflow-gates.md). Derive readiness, blockers, due/reopened checks
and any permitted next command from that result and its current input binding. Link the
captured observation; if inputs changed, refresh it before relying on it. A malformed
workspace or failed status call is an error, not a cached green status.

`state.md`, chat, task displays and the final report are presentation indexes, not a second
runtime ledger. Distinguish ready action, executed command, accepted check and closed
increment. Before adoption, report procedural gate evidence explicitly; do not invent
Readiness JSON. Preserve incomplete metrics, unconfirmed human approval and publication/
host limits even when a bounded functional slice passes.

Check that the first line accurately states the result, blocker, or required decision; the
message agrees with observed evidence and current state; and the reader knows whether they
need to act. Keep meaningful uncertainty and every material limitation. Move supporting detail
to accessible artifacts only when doing so preserves the requested answer and required reporting.

Use these cases when reviewing a change to this standard; they are illustrative acceptance
scenarios, not claims about a real run:

| Given | The message must | It must not |
|---|---|---|
| Work is complete and a PR exists | Name the delivered outcome and link the PR. | Invent another task or end with a routine offer. |
| Build passed, publishing failed | Lead with incomplete delivery and distinguish the two outcomes. | Claim the release succeeded because the build passed. |
| A request returned HTTP 401, with no diagnostic evidence | Report the observed status, unknown cause, and next diagnostic. | Assert a missing auth header or expired credential as the cause. |
| A design needs approval | Identify the decision, recommendation, material trade-off and artifact. | Treat silence as approval or start dependent work. |
| The user requests a detailed explanation | Give the requested depth and relevant evidence. | Substitute a short overview merely to meet a style preference. |
| Seven material blockers remain | Keep all seven discoverable in the message, grouped if useful, with impact and resolution ownership. | Truncate them to satisfy an item limit or hide them only in an artifact. |

## Inspiration

Original wording informed by the communication ideas in
[`ayghri/i-have-adhd`](https://github.com/ayghri/i-have-adhd/blob/0a84de401019a3a822248df586d88a2b56f8c6af/skills/i-have-adhd/SKILL.md)
(MIT-licensed). Bulletproof adopts the presentation principles, not the upstream plugin, hooks,
medical assumptions, mandatory estimates, or persistence rules. Its reported evaluations do not
establish effectiveness for Bulletproof; do not make that claim without relevant evidence.

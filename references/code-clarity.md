# Reference: Human-Readable, Maintainable Code

Production code explains current behavior; Git explains change history; tests protect important
behavior. Optimize for a maintainer understanding the correct behavior, not fewer lines,
more comments, more abstractions, or a better-looking metric.

Apply this contract during design, implementation, and review of changed code and tightly
coupled problems. Follow repository conventions and required documentation. Do not start
unrelated cleanup, add a new phase, or generate a separate readability report. Use the existing
design, tests, and review records. Human-facing messages follow `communication.md`.

## Design for understanding

- **Keep the main flow visible.** A reader should be able to trace the normal path, important
  decisions, side effects, and failures without reconstructing them from scattered callbacks.
  Keep orchestration distinct from business decisions, transport, rendering, and persistence
  where a boundary makes those responsibilities easier to understand.
- **Extract a responsibility, not a line range.** Give each module/helper a coherent purpose,
  meaningful inputs and outputs, and a reason to change. Avoid giant mixed-purpose methods,
  but do not replace them with a maze of wrappers or an obligatory class per step.
- **Choose the simplest sufficient design.** Reuse the project's established patterns and
  helpers. Share business rules and integration mechanics that must stay consistent. Similar
  syntax with different responsibilities is not automatically a shared abstraction; small
  independent snippets can be clearer than a generic helper full of mode flags.
  Do not invent extension points, frameworks, or configuration for hypothetical requirements.
- **Own contracts and state explicitly.** Define shared integration types once; validate
  uncertain input at the boundary instead of repeatedly casting it into a desired shape.
  Make state ownership, transitions, mutation, initialization, and cleanup easy to find.
  Use named states/results when combinations of flags obscure valid and invalid states.

Use the existing design's responsibility table and interactions to show these choices.
An extraction should reduce what a reader must keep in mind; moving the same complexity to
another file without a useful boundary is not an improvement.

## Implement for the next reader

- **Name the domain and the action.** Names describe the value's meaning, units where relevant,
  and the function's real behavior. Avoid vague names and misleading claims of purity when
  a method performs I/O. Prefer named options or domain types to ambiguous boolean arguments.
- **Use straightforward control flow.** Prefer clear branches and suitable guard clauses to
  dense expressions, nested ternaries, hidden mutations, and deeply nested callbacks.
  Preserve cleanup, error propagation, ordering, and transaction boundaries when restructuring.
- **Make failures explicit.** Distinguish success, partial success, missing data, and failure.
  Use repository-standard error handling and notifications/logging; do not swallow errors or
  return success-shaped defaults. Include actionable context without sensitive data.
  Keep decision logic separate from I/O when useful, not as an obligatory extra layer.
- **Let tests explain behavior.** Use readable setup, scenario names, and assertions that expose
  the expected result and failure paths. Protect regression lessons with executable checks,
  not a growing incident narrative. Preserve existing behavior unless the requirement changes
  it; a readability refactor is not permission to change runtime contracts.

## Comment discipline

Keep concise explanations of non-obvious reasons, invariants, compatibility constraints,
algorithm choices, and useful public API contracts. Preserve license notices, required
documentation, and tool-significant annotations. A sufficiently complex invariant may need
more than one sentence; there is no comment quota.

Do not add dated change journals, incident timelines, debugging transcripts, screenshot
references, agent progress notes, or superseded implementations to production comments.
Keep change history in commits/PRs, significant durable decisions in the repository's established
design/ADR location, and task evidence in the task workspace. Do not create an ADR for every fix.
Avoid prose that merely translates each statement into English.

When changing behavior, read the affected comments and update or remove stale explanations.
Keep the current constraint and its reason, not both the old rule and the story of its replacement.
A stable issue or specification link can support a necessary explanation; bare line numbers,
local-machine paths, and timestamps are not a substitute for an understandable current contract.
Do not discard useful rationale just because it originated in an incident.

**Classify text before shortening it.** Runtime prompts, model-facing tool descriptions, schemas,
and generated-code directives can control behavior. They are not disposable commentary.
Changing them requires the same contract review and relevant checks as other behavior changes.

## Review acceptance

Read the changed code without relying on the author's narrative. Check:

| Question | Reject when |
|---|---|
| Can I explain the normal path, failure paths, and state changes? | Unrelated responsibilities or hidden side effects make the flow difficult to trace. |
| Do names and comments match the implementation? | Names misrepresent behavior, comments contradict code, or source contains inline change journals. |
| Does each abstraction reduce understanding effort? | Helpers only move lines, indirection hides a simple operation, or speculative generality adds unnecessary modes. |
| Are shared contracts and integration behaviors consistent? | Repeated type assertions, fallback chains, or dispatch logic leave the same contract implemented differently without an intentional reason. |
| Is the simplification behavior-preserving? | Cleanup, error distinctions, ordering, required documentation, or runtime tool/prompt contracts were removed for brevity. |

Each finding needs a concrete location, the behavior or maintenance cost, and a proportionate
remedy. Use the existing review/disposition process; do not accept "looks cleaner" as proof or
turn personal style preferences into blockers. Fix substantiated in-scope findings before
acceptance; record unrelated improvements as follow-ups without expanding the task.

Length, nesting, comment density, and complexity are investigation signals, not new arbitrary
limits. Existing configured quality gates still apply. A lower score or shorter file does not
prove readability: inspect the responsibilities and flow, and never split functions or remove
useful explanation solely to move a metric.

# Reference: Requirement-Scoped Codebase Research

This file is the **reusable research prompt**, not the research output. The main agent can
follow it directly or hand it to a research subagent with the brief below. Research establishes
**what exists and what constrains the requirement**; Phase 2 decides what to change. Preserve
Bulletproof's five-phase workflow.

The deliverable is a source-backed handoff that a subsequent agent can use without repeating
discovery or relying on the researcher's conversation history. Capture **all requirement-relevant
details**, not every detail in the repository. Be concise in the summary, not at the expense of
contracts, failure paths, test coverage, or unresolved questions.

## Input contract (supplied by the parent)

- **Requirement:** the complete request, referenced documents or accessible copies, acceptance
  criteria with stable IDs, scope exclusions, and any clarified decisions or explicit assumptions.
- **Assignment:** the question to answer, repository/worktree root, known project context and
  starting points, scope boundaries, and any investigation budget or access restrictions.
- **Output:** an explicit task-scoped destination accessible to the next agent. Reuse the
  project's existing task workspace or plan's research section; otherwise use a persistent
  session artifact such as `<task-workspace>/research.md`. Never overwrite this reference, another
  task's report, or an existing project document without authorization.

Read the requirement and directly referenced material before decomposing the work. Missing or
inaccessible inputs are reported, not guessed. The parent retains ownership of acceptance
criteria, user clarification, delegation, design, and the overall Phase 1 gate.

## Operating boundaries

- **Read-only investigation:** do not edit implementation, install dependencies, mutate shared
  services/data, commit, or propose a new architecture. Write only the assigned research output
  if permitted; with read-only tools, return the report for the parent to persist.
- Read applicable repository instructions first and obey them. Use
  `project-profile.md` for stack, tooling, and conventions; reuse a verified profile rather than
  researching the whole project again.
- Do the work directly by default. Delegate only substantial, independent questions when
  supported, per `parallel-execution.md`. A researcher must not recursively delegate.
- Distinguish observations from recommendations. Record change-relevant defects, risks, and
  contradictions with evidence; do not turn research into an unrelated code review or silently
  choose the implementation. For a bug, trace the causal path and distinguish a reproduced
  failure from an unverified root-cause hypothesis.
- Use only safe, authorized inspection or reproduction commands. Report any needed execution
  that would mutate state, require unavailable tools, or exceed the assignment to the parent.

## Investigation procedure

### 1. Map the requirement to research questions

For **every acceptance criterion and explicit sub-deliverable**, identify what must be understood:
the current behavior, relevant entry points, dependencies, constraints, and existing proof.
Record a coverage row early; update it as evidence arrives. Classify non-functional constraints
(compatibility, performance, security, accessibility, operations) only where the requirement or
existing contracts make them relevant. Do not invent new product scope.

### 2. Locate the relevant surfaces

Start with named files, symbols, and likely directories. Prefer available code intelligence,
then focused path/content searches. Expand using related terms, callers, registrations, exports,
and package boundaries when initial results are incomplete; do not stop at the first plausible file.
Group locations by **implementation, consumers, interfaces/types, tests/fixtures, configuration,
documentation, and examples**. Include generated/external boundaries when relevant, and identify
which parts were unavailable or excluded.

Read the definitions and enough surrounding code to establish behavior. A filename, symbol name,
search hit, or test title is a locator, not evidence of how the implementation works. Read the
complete relevant contract or function; use ranges for large files and expand when context requires.

### 3. Trace behavior and blast radius

Follow the actual flow from entry point to observable outcome, crossing module boundaries:

- callers, routing/registration, public signatures, inputs, outputs, defaults, and validation;
- transformations, branches, invariants, state ownership, persistence shapes, and side effects;
- errors, propagation, logging/notifications, cleanup, and applicable retries or concurrency;
- configuration/feature flags and their defaults, external dependencies and relevant versions;
- downstream consumers, shared types/utilities, alternate entry points, compatibility and
  migration boundaries a change could affect.

Cite the material steps and contracts. Trace applicable failure paths, not just the happy path.
State where the trace ends and why. Static source inspection does not prove runtime behavior:
label what was read versus executed, including environment/flag assumptions. For a defect, record
expected versus observed behavior and a safe reproduction result, or the exact reproduction
blocker; do not claim a cause was verified solely because it looks plausible.

### 4. Find reuse and existing proof

Find representative analogous implementations, shared helpers/abstractions, and **their tests**.
Record concrete symbols, signatures, usage context, invariants, and relevant variations. Explain
what the repository actually treats as canonical (with evidence), rather than declaring a personal
preference. Mark deprecated examples and do not present them as templates for new work.

Read assertions, fixtures, and setup for the relevant unit, integration, and end-to-end tests.
Map them to the behavior/ACs they cover; identify uncovered scenarios within the inspected scope.
Record exact commands from project scripts, CI, or contributor docs, prerequisites, and whether
they were actually run. A test's existence is not a passing result, and a passing result is not
proof of scenarios it never asserts. Do not create a new test framework during research.

### 5. Recover decision context when it matters

Consult relevant ADRs, issues/PRs, plans, and prior research when they explain a constraint or
decision. Record the source, date/revision, rationale, and status: **implemented, proposed,
superseded, or unverified**. Retain rejected alternatives when their rationale prevents repeating
a known mistake; omit tangential history. Do not require HumanLayer's `thoughts/` layout or tools.

Live code is primary evidence of **current implementation**, not authority to overrule repository
instructions or the requested behavior. Document a mismatch between code, tests, docs, and
requirements explicitly; the parent resolves material conflicts before planning.

Use external research only when the assignment needs it and access is permitted. Prefer official
docs, upstream source, and release notes applicable to the project's actual dependency versions.
Fetch the relevant source rather than citing a search summary; include direct links, version/date,
conflicts, and limitations. Never disclose private code, secrets, or internal artifacts to external
search services.

### 6. Synthesize, check coverage, and stop

Connect findings across components and resolve conflicting evidence where possible. If delegated,
return the assigned scope and coverage honestly; the parent combines all required results before
accepting the overall handoff. Do not count an incomplete or failed worker as completed research.

Stop when each assigned criterion/question has sufficient evidence to explain its current behavior,
constraints, dependencies, reuse candidates, and test coverage, **or a named gap/blocker with a
next investigative action**. Do not keep exploring unrelated areas to make the report look thorough.
A research assignment can finish with unknowns; **Gate 1 cannot pass with unresolved design-changing
unknowns** under `SKILL.md`'s clarification rules.

## Evidence and freshness rules

- Label material findings **FACT** (directly observed), **INFERENCE** (derived from cited facts),
  **HYPOTHESIS** (plausible, unverified), or **UNKNOWN** (not established). Cite the supporting
  `path:line-range` and symbol for code facts; include a short excerpt when exact behavior or a
  contract matters. Cite command/output evidence for runtime facts and links for external facts.
- **Absence is scoped, not absolute.** Record the search terms/commands, directories/file filters,
  relevant exclusions, and result. An empty search means "not found in this scope," not "does not
  exist anywhere." Check naming variants, registrations/callers, and relevant tests before treating
  a gap as established. Distinguish not found, not inspected, inaccessible, and genuinely greenfield.
- Head the report with repository/worktree, commit SHA (or "no commits"), branch, dirty-tree
  status and relevant uncommitted paths, research date, assignment, and completion status.
  A SHA alone does not identify uncommitted content; label those citations as worktree evidence.
- Use commit-pinned GitHub links only when the cited content matches a remotely available commit.
  Otherwise preserve repository-relative paths and the local snapshot context. Never fabricate
  a permalink for uncommitted changes or silently rewrite source paths.
- Update the same task report for follow-ups: note the new question, date/snapshot, changed findings,
  and remaining gaps. Preserve decision context but clearly supersede stale findings. On resume or
  after edits, revalidate material facts and re-anchor affected citations before relying on them.

## Output contract

Keep a short summary followed by the detail the requirement needs; **no hard page cap that drops
evidence**. Use the following sections, marking inapplicable ones N/A with a reason rather than
inventing content. Shared evidence IDs can avoid repeating long citations in every row.

| Section | Required contents |
|---|---|
| **Snapshot & scope** | Metadata above; full requirement or durable accessible copy; ACs, exclusions, clarified decisions/assumptions, and the assigned subset if delegated. |
| **Summary** | What exists, the main constraints, what remains unknown, and whether the report is complete, partial, or blocked. |
| **Requirement coverage** | One row per AC/sub-deliverable: current behavior, evidence, relevant contracts/consumers, reuse candidates, existing tests, uncovered scenarios, and research status. No silently omitted rows. |
| **Code map & behavior traces** | Categorized files; entry points and real signatures; cross-component happy/failure paths, state/side effects, configuration, contracts, and blast radius. |
| **Reuse & conventions** | Applicable project instructions; representative implementation and test examples; helpers, variations, constraints, and repository-documented preferences. |
| **Existing proof** | Test names/assertions mapped to behavior; verified command definitions and prerequisites; observed execution results or explicitly "not run"; coverage limitations. |
| **History & external sources** | Relevant decisions, rationale, versions/dates, implementation status, direct citations, and conflicts with current code. |
| **Gaps & search evidence** | Scoped not-found results, queries/filters/exclusions, inaccessible sources, incomplete traces, and what was not inspected. |
| **Risks & questions** | Typed uncertainties, their impact and affected ACs, which block planning, and the next verification/clarification action. No implicit defaults disguised as facts. |
| **Handoff** | Recommended reading order of existing sources, report location, freshness caveats, and remaining parent actions. No proposed implementation plan. |

For a small task handled in one context, these may be compact sections in the existing plan/task
context rather than a new file. **Before handing research to a subsequent agent, persist it at the
agreed destination and confirm that agent can access it.** If persistence fails, report the failure;
do not claim the handoff is ready. Do not create repository documentation just for ceremony.

## Parent acceptance and downstream use

1. Confirm the report exists at the agreed location and covers the **whole requirement**, not just
   the easiest path or one worker's scope. Reconcile the AC rows against the original request.
2. Check that important behavior, contracts, reuse candidates, and test claims have resolvable
   evidence. Spot-check representative citations, including a cross-component claim and a
   not-found claim if present. Reject unsupported facts, stale references, and hidden unknowns.
3. Resolve design-changing unknowns under Phase 1's clarification rules. A headless default is a
   labeled requirement/design assumption, **not proof of unknown code behavior**; record any
   residual non-blocking limitations explicitly.
4. Supply the report location and snapshot to the next agent. Phase 2 separates current facts from
   design choices and traces them back to ACs. If new facts are needed, return a bounded question
   to research instead of inventing them. Implementers still read definitions and current source
   before editing; the report avoids rediscovery, not verification.

## Delegation brief

Supply this file's contents (or a confirmed accessible path) with the following filled-in brief;
never assume a fresh-context agent can see the parent's chat or installed skill:

> **Role:** Read-only codebase researcher. Follow the supplied research procedure; do not
> implement, design a solution, recursively delegate, or write outside the assigned output.
>
> **Requirement and ACs:** [complete request, accessible supporting material, decisions,
> assumptions, exclusions, and stable AC IDs].
>
> **Assignment:** [bounded question/subset, repository/worktree, starting points, known context,
> access limits, investigation budget].
>
> **Output:** [explicit accessible destination and write permission, or return-to-parent for
> persistence]. Use the output contract above, including coverage, citations, search evidence,
> snapshot, and blockers. Finish with a short summary, output location, and unresolved actions.

## Inspiration

Adapted in original wording from HumanLayer's
[research command](https://github.com/humanlayer/humanlayer/blob/99abe673498cf8bdcd5f989aebe9406a27185b3b/.claude/commands/research_codebase.md)
and its codebase locator/analyzer/pattern-finder, thoughts locator/analyzer, and web researcher.
The reusable parts are evidence-backed discovery, behavior tracing, pattern/test examples,
historical context, and synthesis; mandatory fan-out and repository-specific ceremony are not used.

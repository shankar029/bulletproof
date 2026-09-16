# Reference: Executable Planning & Agent Handoff

This is the **reusable planning procedure**, not the task's plan. Phase 1 establishes facts;
Phase 2 approves the design; Phase 3 translates that design into executable tasks. It does not
invent requirements, silently redesign the solution, or repeat broad codebase research.

The deliverable is `.ai/<slug>/plan.html`, with optional linked `tasks.md` detail in the same
workspace. A fresh implementer must be able to find what to change, what to preserve, what must
exist first, and how completion will be proven without relying on the planner's chat.
The trivial tier keeps `SKILL.md`'s short path and does not require these artifacts.

## Inputs and ownership

Read the complete requirement/AC record in `state.md` and `traceability.md`, `clarifications.md`,
the accepted `research.md`, approved `design.html`, applicable design-review dispositions, and any
existing plan/task records. Confirm that the files are accessible and that the design approval
and source snapshot still apply. Record the plan revision/date and the research/design versions
or commits it consumes, including relevant uncommitted changes.

The parent owns scope, ordering, Gate 3, and any user approval. Planning may run directly or in
a bounded subagent per `delegation.md`; the planner may write only the assigned artifacts, not
implementation code, and must not recursively delegate.

Missing facts go back to **bounded research**; changes to behavior, interfaces, or architecture
go back to **design and its approval gate**. Mark the affected work blocked until resolved.
An authorized requirement assumption is not proof of an unknown API or tool capability.

## 1. State the outcome and the boundaries

Start the plan with the observable desired end state and the AC IDs it serves. Link the binding
design, decisions, exclusions, and compatibility invariants rather than copying those documents.
State what will **not** change, especially behavior that existing callers or data depend on.
Cover all explicit sub-deliverables; do not introduce adjacent cleanup or speculative features.

## 2. Separate increments from tasks

- **Increment (`I1`, `I2`, ...):** a coherent vertical slice delivering observable behavior.
  It is session-sized, independently verifiable, and ends with Phases 4–6 complete and a green,
  reviewed commit. Small work is one increment.
- **Task (`I1.T1`, `I1.T2`, ...):** an ordered step inside an increment. Contracts/types,
  core logic, wiring, tests, and docs can be tasks; they are not automatically independent
  increments. Task completion is not increment completion or an AC-verification verdict.

Derive dependencies from the approved design. Within a slice, create required contracts before
their users, integrate the behavior, and verify the public outcome. A later increment can extend
the same component: name its **distinct change responsibility** and prerequisite state. Every
planned change has one owning task; repeated component names do not imply duplicate ownership.
Dependent tasks must be ordered, and shared-file edits must not run concurrently.

The plan's overview table maps each increment to **outcome, ACs, design references, prerequisites,
task IDs/detail links, affected files, and completion checks**. Every in-scope design change must
have an owner and every AC must map to work and proof. Detect dependency cycles and missing
prerequisites before dispatch; do not disguise a cycle as an arbitrary ordering.

At an intermediate gate, verify this increment's due scenarios and affected regressions from
completed slices. Future tasks remain planned/not-yet-verified without blocking earlier slices.
For an AC spanning increments, record partial proof by task/check and leave the AC not-yet-verified
until its entire contract is proven. The final ship gate covers the **whole requirement**, not
just the final slice. Never mark future work verified to make an intermediate gate pass.

## 3. Write executable task records

Use the fields below for each task, compactly. Share common setup/check definitions by ID and link
them rather than repeating them. Mark genuinely inapplicable fields N/A with a reason.

| Field | Required content |
|---|---|
| **Identity & purpose** | Stable task ID, parent increment, ACs and approved design section/component; the observable outcome this task contributes to. |
| **Depends on & entry conditions** | Task IDs, contracts/artifacts that must exist, relevant source state and required access/tooling. Name any blocked prerequisite. |
| **Changes** | Exact existing files/symbols and intended behavior delta; explicitly label new files/symbols from the design. Include wiring, configuration, migration or documentation edits where applicable. Do not use a broad glob as the only instruction. |
| **Reuse** | Cited existing helper/abstraction and representative implementation/test pattern; link research. If no suitable candidate was found, link the scoped finding rather than inventing one. |
| **Preserve & exclude** | Existing behavior, public contracts, data compatibility, and scope exclusions that this task must not break. |
| **Proof** | Check IDs with scenarios, exact commands or manual steps, expected outcomes, evidence destinations, and verification owners as below. |
| **Failure & recovery** | What stops this task, which dependent work is blocked, and the appropriate research/design/implementation escalation. For stateful changes, include approved rollback/recovery and its limits; N/A for tasks without such effects. |
| **Status & evidence** | Pending / in progress / blocked / complete; completion references the actual change or commit and required check results. Initially planned checks are **not run**, never green by default. |

Specify critical contracts, algorithms, or transformations where the implementer needs them,
but do not write a speculative patch for every file. Ordinary implementation choices within
the approved design remain the implementer's job; unresolved product/architectural decisions do not.
For migrations or deployment tasks, spell out forward ordering, compatibility window, safe
environment, verification, and approved recovery. Planning does not authorize destructive execution.

## 4. Define proof, not just test names

Each check has a stable ID and records:

| Field | Required content |
|---|---|
| **Purpose** | AC/scenario and expected observable behavior, including relevant negative, boundary, compatibility and regression cases. |
| **Execution** | Exact command plus working directory and shell/platform, or reproducible manual steps. Cite the project script/CI/docs or researched command definition; label derived invocations. |
| **Prerequisites** | Runtime/tool versions where relevant, configuration names, services/fixtures, authorized environment and setup/cleanup. Never include secrets. |
| **Pass condition** | Expected assertions, output/schema/side effects, exit status, or approved measurable threshold. Exit zero alone is insufficient if no relevant tests ran. |
| **Owner & timing** | Implementer, independent verifier, or human; when it runs and which later action it gates. Preserve mandatory Phase 5/6 independence. |
| **Evidence** | Task-scoped destination and required result data: command/steps, snapshot, exit code where applicable, observed outcome and artifact/commit references. |

Use the repository's established commands and test framework, not assumed `make`/`npm` scripts.
New tests can be planned before they exist: label them **planned**, specify their assertions,
and ground the runner invocation in existing tooling. Distinguish a command definition checked
against docs from a command that actually ran. Missing execution prerequisites are explicit
blockers, not permission to invent a passing fallback.

Keep automated checks separate from human acceptance, but **UI does not automatically mean
manual**: automate objective UI/API/CLI behavior with the existing surface-appropriate tools.
Reserve human checks for judgment, required approval, or access that agents genuinely lack.
Only the designated human can confirm their acceptance item; a screenshot or an agent assertion
is not that confirmation. Mark environment-blocked checks honestly under Phase 5's rules.

Retain per-increment unit, integration and end-to-end coverage, regression scope, coverage
expectation, full E2E timing, and final regression pass. State only relevant, agreed performance
thresholds; "acceptable performance" is not a pass condition. Research or clarify missing material
thresholds rather than inventing numerical targets.

## 5. Keep the overview short without losing execution detail

`plan.html` uses `design-doc.md`'s shared HTML shell, dependency diagram and **three-page overview
limit**. If task/check records fit, keep them there. If they do not, put the necessary records
in `.ai/<slug>/tasks.md` and link their stable IDs from the overview. The page limit applies to
the overview, not a license to remove prerequisites or proof from the execution contract.

Use **one authoritative copy** of each record. Do not create `tasks.md` when it adds no value,
or duplicate records in HTML and Markdown. `state.md` tracks phase/increment and points to the
next task; `traceability.md` maps ACs to task/check IDs and evidence. Those are indexes, not
alternative plans. Verify all artifact paths/anchors are reachable from a fresh agent's workspace.

## 6. Accept the handoff (Gate 3)

Perform one bounded **consumer-readiness check**, using a fresh-context agent when available,
otherwise the parent. It is not a second architecture review or another research phase.
Give the reader the plan and linked inputs, not an explanation that fills holes in the plan.
Ask it to walk the first ready task and a dependency/failure boundary (where applicable):
can it locate the exact changes, prerequisite state, preserved behavior, commands, pass conditions,
owners, and evidence paths without an unresolved product or architectural decision?

Record **READY / REVISE / BLOCKED**, specific gaps and dispositions in the existing task state
or review record. A sample is not full coverage: the parent also reconciles **all** ACs and
design changes against task ownership, dependencies and proof; checks plan links and command
provenance; and verifies that the increments are independently deliverable.
REVISE/BLOCKED work must be resolved before Gate 3 passes. If a bounded review cannot converge,
report the blocker rather than lowering the gate or launching repeated reviewers.

Gate 3 passes only when the plan is executable from its artifacts, every planned change has an
owner, prerequisites are ordered, every AC has work and proof, and no unresolved execution-critical
question is hidden. This checks plan readiness, not implementation correctness or test success.

## 7. Revise and resume without silently drifting

When feedback or source changes invalidate a plan:

1. **Record the mismatch:** task/AC, expected versus observed state, evidence, impact, and affected
   dependents. Stop affected work; do not continue using an invalid prerequisite.
2. **Route it:** missing source/tool facts to research; changed behavior/interfaces/scope to design
   and applicable approval; sequencing/detail changes within the approved design to planning.
   Investigate only the new uncertainty. No automatic user pause for routine task mechanics.
3. **Edit surgically:** preserve unaffected content and stable IDs. Update affected tasks,
   dependencies, exclusions, checks, owners and recovery together. Record revision/date, reason,
   changed IDs and approval implications. Retired/split IDs remain traceable; do not reuse them
   for different work.
4. **Reconcile progress:** update plan, `state.md` and `traceability.md` pointers/status together.
   Previously completed work stays complete only while its change and evidence still satisfy the
   revised contract. Otherwise reopen it and invalidate affected results explicitly.
5. **Recheck the relevant gates:** refresh source citations, revisit Gate 2 for changed design,
   and rerun the Gate 3 checks for the altered graph and coverage before dispatch.

On resume, read state, approved design, plan and the current task records; compare their snapshot,
completion evidence and prerequisites with the actual tree. Never trust checkboxes alone.
Reverify affected checks when evidence is stale; do not rerun unrelated discovery automatically.
If an increment is too large, finish or stop at a safe green boundary and split the remaining
behavior into coherent slices with the same revision protocol.

## Delegation brief

Supply this procedure or an accessible path with:

> **Role:** Execution planner; read-only over implementation, write only the assigned
> `.ai/<slug>/plan.html` and optional `tasks.md`. Do not implement, redesign, or spawn agents.
>
> **Inputs:** [repository/worktree and snapshot; requirement/ACs; decisions/exclusions;
> research; approved design and review; current state/traceability/plan; assigned scope].
>
> **Output:** Apply the planning contract above. Produce ordered vertical increments, precise
> task/check records, artifact links, and named blockers. Return locations, a short readiness
> summary and unresolved parent actions; never claim planned verification already passed.

## Inspiration

Adapted in original wording from HumanLayer's
[create](https://github.com/humanlayer/humanlayer/blob/99abe673498cf8bdcd5f989aebe9406a27185b3b/.claude/commands/create_plan.md),
[iterate](https://github.com/humanlayer/humanlayer/blob/99abe673498cf8bdcd5f989aebe9406a27185b3b/.claude/commands/iterate_plan.md),
[implement](https://github.com/humanlayer/humanlayer/blob/99abe673498cf8bdcd5f989aebe9406a27185b3b/.claude/commands/implement_plan.md)
and [validate](https://github.com/humanlayer/humanlayer/blob/99abe673498cf8bdcd5f989aebe9406a27185b3b/.claude/commands/validate_plan.md)
commands: explicit deltas, outcomes/exclusions, verification and controlled iteration. Keep
Bulletproof's separate research/design phases, evidence-based resume and independent verification;
do not import repository-specific tools/layouts, mandatory repeated approvals or trust in checkboxes.

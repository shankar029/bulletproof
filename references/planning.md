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
For an adopted workspace, resolve the current design/contract through
`current-design.json` per [workspace.md](workspace.md); do not use an old overview as live
authority. Initial procedural planning prepares the candidate and does not require a
pre-existing adoption.

The parent owns scope, ordering, Gate 3, and any user approval. **Non-trivial planning defaults
to a bounded, fresh-context subagent** per `delegation.md`, given the accepted research, approved
design, ACs/decisions and current workspace records. If delegation is unavailable, the parent
plans inline to the same standard and records the fallback in `state.md`; trivial work keeps
its short path. The planner may write only the assigned artifacts, not implementation code,
and must not recursively delegate.

Missing facts go back to **bounded research**; changes to behavior, interfaces, or architecture
go back to **design and its approval gate**. Mark the affected work blocked until resolved.
An authorized requirement assumption is not proof of an unknown API or tool capability.

## 1. State the outcome and the boundaries

For uncertain or large work, distinguish **questions that need decisions** from executable
tasks. Keep each question in the existing clarification/design record with its owner, blocking
prerequisites, affected ACs and resolution evidence; link it rather than duplicating it in tasks.
Research factual questions; route product/architecture decisions to the parent and applicable
approval. Ask only currently answerable material questions together, not downstream questions
whose premises are still unsettled. Do not ask the human for facts the agent can safely inspect.

A task is ready only when its decision and implementation prerequisites are resolved. Suspected
later questions remain explicitly not yet specified, distinct from out-of-scope work; they are
not completed tasks. This does not permit Gate 1/3 to pass with design/execution-critical
unknowns. Reconcile readiness and coverage at the existing gates; no separate tracker,
automatic issue creation, mandatory interview or additional approval round is required.

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

**Wide compatibility refactors:** when a rename, schema or shared-contract change cannot safely
land by feature slice, plan expand, migrate, then contract. Add a compatible form first, migrate
consumers in bounded dependency-ordered batches, and remove the old form only after scoped
caller searches and compatibility/regression checks establish that migration is complete.
Each batch records exact targets, preserved behavior and proof under the task contract below.
For deployments, include old/new version coexistence and rollback limits.
Every deliverable increment must still be green. If a batch cannot stand alone, treat it as an
internal task of a session-sized integrated increment, not a completed but broken increment.
If no safe grouping exists, stop and revise the migration design instead of promising green
only at the end. This is compatibility scaffolding with planned removal, not indefinite duplication.

For guarded retirement, register a `retire` action with its legacy scope and expected legacy
presence, requiring a `compatibility` check with `validity="before-action"`. Accept that check
while legacy and replacement coexist, **before** admitting retirement. The consuming admission
must carry the exact earlier receipt reference; test caller migration/rollback and then current
post-retirement behavior separately. A final green test or backdated receipt cannot establish
earlier compatibility. See [workflow-gates.md](workflow-gates.md#execution-and-returned-evidence).

Use the fields below for each task, compactly. Share common setup/check definitions by ID and link
them rather than repeating them. Mark genuinely inapplicable fields N/A with a reason.

| Field | Required content |
| --- | --- |
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
| --- | --- |
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

## 4b. Enumerate the end-to-end scenarios before anyone executes them

A verifier that enumerates and executes in the same breath is self-graded, and under a budget it
will enumerate less. Phase 3 therefore commits the list; Phase 5 executes it. Write
`.ai/<slug>/scenarios.md`.

Derive scenarios from the **four sources** and cover the **seven classes** in
`testing-and-e2e.md`: each AC, the design's risks/edge-cases/failure-modes rows, the as-is →
to-be preserved-behaviour invariants, and the original requirement text; across positive,
negative/rejection, boundary, failure/fault, authorization, idempotency/repeat and regression.
Every AC × applicable class yields a scenario or a recorded **N/A with a reason**.

One row per scenario, with a stable id (`S1`, `S2`, …). Write it as a markdown table with these
column headers — `scripts/scenarios.py` parses them **by name, not position**, so you may reorder
or add columns, but `Id` and `Evidence` must be present:

```markdown
| Id | AC | Class | Preconditions | Steps | Expected observable | Evidence | Owner | Status |
|----|----|-------|---------------|-------|---------------------|----------|-------|--------|
| S1 | AC1 | positive | seeded cart | POST /orders | `HTTP 201` and `orderId` | `evidence/S1-api.json` | verifier | |
| S2 | AC1 | negative | empty cart | POST /orders | `HTTP 422`, no row written | `evidence/S2-api.json` | verifier | |
| S5 | AC3 | failure | DB down | POST /orders | `HTTP 503` | — | verifier | BLOCKED: no staging DB |
```

The fields:

| Field | Required content |
| --- | --- |
| **Id / AC / Class** | `S7` · AC3 · negative. Ids are stable and never reused. |
| **Preconditions** | Fixture, seeded state, auth context, environment. |
| **Steps** | What a real user or client does — through the public surface, not an internal call. |
| **Expected observable** | The **specific** string, status, field, file or UI state that must appear. "HTTP 201 and body contains `orderId`"; "the banner reads `Order placed`". "Works correctly" is not an expected observable. |
| **Evidence artifact** | Declared **type and path**: `evidence/S7-api.json`, `evidence/S4-checkout.png`, `evidence/S9-cli.txt`. Declared here so a missing proof is detectable, not arguable. |
| **Owner** | Independent verifier (Phase 5) by default; human for judgment/approval items. |

**Declare the expected observable before the run, never after.** A pass condition written once
the output is known is a description, not a test. This is the same rule as "observe the failure
first" in Phase 4, applied to end-to-end proof.

The list is a **floor, not a ceiling**. Phase 5 re-derives from the same four sources and
**appends** what implementation made visible; it may never remove a row. A scenario that cannot
be executed becomes **BLOCKED with a named blocker**, never deleted.

### The checker

Two modes, one tool. **Gate 3 — is the enumeration complete?**

```bash
python <skill>/scripts/scenarios.py --slug <slug> --coverage
```

It reads the ACs from `traceability.md` (or `--ac`) and exits non-zero on:
**UNCOVERED** (an AC with no scenario and no N/A row for some class) · **VAGUE** (an expected
observable with no literal or number to assert) · **NO-DESTINATION** (no evidence path, and not
N/A or BLOCKED) · **NO-AC** · **NO-CLASS** (a class matching none of the seven) · **UNREASONED-NA**.

Mark a class that genuinely does not apply as `N/A: <reason>` in the Status column — that covers
the cell. **`N/A` and `BLOCKED` are different claims:** N/A means *never owed* (a read-only
endpoint has no idempotency concern); BLOCKED means *owed but not runnable yet* (no staging DB).
Both need a reason; neither may be an empty cell.

**Gate 5 and 6 — is it proven?**

```bash
python <skill>/scripts/scenarios.py --slug <slug> [--ac AC1,AC2] [--since <ref>] [--strict]
```

It reconciles the table against the artifacts on disk and exits non-zero on any of:
**MISSING** (no artifact at the declared path) · **EMPTY** (zero bytes) · **STALE** (mtime predates
`--since`, default `HEAD` — the code changed under the proof) · **DROPPED** (no evidence path and
no blocker, or `BLOCKED` with no reason) · **DUPLICATE** (id reused) · and with `--strict`,
**UNPROVEN** (no backticked literal from `Expected observable` appears in a text artifact).

Use `--ac` at an increment gate so it checks the due scope rather than the whole plan.

**Put the specific values in backticks** — `` `HTTP 201` ``, `` `orderId` `` — because that is what
`--coverage` counts as specific and `--strict` samples. Prose in that column still reads fine for a
human; it simply gives the checker nothing to match.

**What it cannot do:** it cannot read a screenshot, and it cannot tell whether a scenario is worth
running — a row reading "expect `ok`" satisfies every check. For a non-text artifact `--strict`
reports UNPROVEN with the literals a human or the Phase 6 reviewer must confirm by eye. The script
raises the floor on **shape**; you and the reviewer remain the only judges of **substance**.

## 5. Keep the overview short without losing execution detail

`plan.html` uses `design-doc.md`'s shared HTML shell, dependency diagram and **three-page overview
limit**. If task/check records fit, keep them there. If they do not, put the necessary records
in `.ai/<slug>/tasks.md` and link their stable IDs from the overview. The page limit applies to
the overview, not a license to remove prerequisites or proof from the execution contract.

Use **one authoritative copy** of each record. Do not create `tasks.md` when it adds no value,
or duplicate records in HTML and Markdown. `state.md` tracks phase/increment and points to the
next task; `traceability.md` maps ACs to task/check IDs and evidence. Those are indexes, not
alternative plans. Verify all artifact paths/anchors are reachable from a fresh agent's workspace.

### Registering the guarded projection

Before dispatch, follow [workflow-gates.md](workflow-gates.md) for the existing strict
`WorkflowContract`, `CurrentDesign` and `DesignReview` shapes and ordinary adoption.
`Action.requires` owns admission edges; `Increment.requires` owns closure edges.
Commands and owners live in that contract; membership, reverse dependencies and readiness
are derived. Narrative plans link those IDs instead of copying a second live graph or command
registry. Keep mandatory metrics, independent verification and review in closure requirements.
An action can be ready while its increment cannot close; successful execution is not acceptance.

After adoption or revision, run actual `status` for the target, then `next` only for its
registered action. A null command is an admitted handoff, not an automatic agent launch.
Preserve runtime-referenced IDs and executable/handoff classification when staging revisions.
Do not mutate the live workflow/pointer to make an action ready. Missing positive metric
attachment blocks quality closure; it is not a reason to drop required checks.

## 6. Accept the handoff (Gate 3)

The **parent performs the bounded consumer-readiness check**; do not launch another reviewer
for every plan. Use only the plan and linked inputs, not conversation knowledge that fills holes
in the artifacts. Walk the first ready task and a dependency/failure boundary (where applicable):
can an implementer locate the exact changes, prerequisite state, preserved behavior, commands, pass conditions,
owners, and evidence paths without an unresolved product or architectural decision?

Before editing, the incoming implementer also confirms its assigned task's prerequisites and
instructions are actionable; report gaps to the parent and repair the artifacts instead of
improvising. This check applies whether implementation is delegated or performed by the parent.
Use an additional independent plan review only for high-risk work or complex dependency
structures (for example destructive migrations or cross-service rollout ordering); it supplements,
not replaces, parent acceptance. Mandatory design review and Phase 5/6 independence are unchanged.

Record **READY / REVISE / BLOCKED**, specific gaps and dispositions in the existing task state
or review record. A sample is not full coverage: the parent also reconciles **all** ACs and
design changes against task ownership, dependencies and proof; checks plan links and command
provenance; and verifies that the increments are independently deliverable.
REVISE/BLOCKED work must be resolved before Gate 3 passes. If a bounded review cannot converge,
report the blocker rather than lowering the gate or launching repeated reviewers.

Gate 3 passes only when the plan is executable from its artifacts, every planned change has an
owner, prerequisites are ordered, every AC has work and proof, and no unresolved execution-critical
question is hidden. This checks plan readiness, not implementation correctness or test success.

**Run `scripts/scenarios.py --slug <slug> --coverage` as part of this gate.** It settles the
mechanical half — enumeration completeness, specificity, declared destinations — so the bounded
review spends its attention on the half no script reaches: whether the increments are genuinely
session-sized and independently deliverable, and whether each scenario is worth running. A green
exit is a floor, never the readiness verdict.

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
> task/check records, artifact links, and named blockers. **Also write `.ai/<slug>/scenarios.md`**
> per §4b — stable `S`-ids covering every AC × the seven classes, each with a specific expected
> observable (a backticked literal or a number, never "works correctly") and a declared evidence
> path; mark a class that genuinely does not apply as `N/A: <reason>`. **Then run
> `python <skill>/scripts/scenarios.py --slug <slug> --coverage` and fix what it reports before
> returning** — a non-zero exit means the enumeration is incomplete, not that the format is wrong.
> Return locations, a short readiness
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

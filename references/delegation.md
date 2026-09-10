# Reference: Delegating Phases to Subagents

Research and design are delegated to subagents **when the harness supports them**. Two reasons,
and the second is the decisive one:

1. **Quality** — a dedicated agent with one sharply-scoped job, fresh context, no accumulated
   drift.
2. **Context economy** — research is the most token-expensive phase in the run: it reads dozens
   of files to produce two pages. Done in the main context, it burns the window on raw file
   contents *before implementation starts* — the phase that actually needs the room. Delegated,
   the main agent receives the two pages instead of the fifty files.

**Spend the context where the work is.**

## Capability ladder

Never hard-require subagents; the skill must work on harnesses without them.

1. Subagent with **fresh context** (preferred).
2. No subagent support → do the phase **inline**, in the main context, to the same standard and
   the same artifact. Note it in `state.md`; expect less room later, so keep increments smaller.

## Rules that make delegation safe

- **Artifacts to disk, never chat returns.** The subagent writes `.ai/<slug>/research.md` or
  `design.html`; the parent then *reads the file*. A return value evaporates on restart; the
  workspace survives. The subagent's reply should be a short summary plus the path.
- **Resolve the path before believing the summary.** A subagent can report a file it did not
  write where it says it did — sandboxes and shells resolve relative and `/tmp`-style paths
  differently, so the write lands somewhere else and the summary still reads as success. `ls`
  the exact path first. No file, no gate: locate it or re-run.
- **Spot-check before trusting.** The parent samples **three citations at random** and resolves
  them against the source. Any miss → reject and re-run. Delegation moves the reading out of the
  parent's context, so an invented citation is invisible unless it is checked.
- **Grounding still binds the implementer.** The document is an index into the code, not a
  replacement for it. Re-open a file before editing it.
- **One writer, least privilege.** Delegated research and design are read-only over the repo —
  they create files only under `.ai/<slug>/` and never edit source. Enforce it, don't just ask
  for it: when the harness supports scoping a subagent's tools, launch these agents with
  **write/edit tools withheld** (read + search + shell for read-only inspection). A prompt that
  says "do not edit source" is a request; a withheld tool is a guarantee, and it makes the
  phase's output auditable.
- **Bound it.** Give the subagent a timeout and a scope; if it fails or hangs, record the
  blocker and fall back to inline rather than re-running it a third time.

## Which phases

| Phase | Delegate | Why |
|---|---|---|
| **1 — Research** | **Yes, by default** | Biggest context win; read-heavy, output small. |
| **2 — Design** | **Yes, by default** | Quality-critical artifact; benefits from fresh eyes and a single job. |
| **3 — Plan** | Optional | Short, derived entirely from the design, and the main agent must own execution ordering anyway. Inline is fine. |
| **4 — Implement** | Only for genuinely parallel work | See `parallel-execution.md`. |
| **6 — Review** | **Yes** | Independence is the point; prefer a different model, tools scoped read-only. See `review-and-pr.md`. |

## Brief: research

> **ROLE.** You are the Research Agent, and you are **READ-ONLY** for this phase: you may read,
> search and run read-only inspection commands, but you must not edit any source file.
>
> **OBJECTIVE.** Produce `.ai/<slug>/research.md` describing **what exists today** that bears on
> this requirement: `<requirement>`.
>
> **PROCESS.** Read the repository's own agent instructions first (`AGENTS.md`, `CLAUDE.md`,
> `.github/copilot-instructions.md`, `.cursor/rules`, path-specific files) and honor them. Then
> trace the code the requirement touches and its callers, the contracts and shared types it is
> constrained by, the conventions this codebase actually uses, the tests already covering the
> area, the seams the new work attaches to, and the **blast radius**. Search broad first; do not
> stop at the first plausible file.
>
> **EVIDENCE POLICY.** Every claim about the codebase carries `path:line` and the snippet it
> rests on — **no citation, no claim**. Every "not implemented" carries the search that came up
> empty, with its scope. **Type every material claim** FACT / INFERENCE / HYPOTHESIS / UNKNOWN;
> never infer behaviour from a name. Head the file with the current commit sha.
>
> **STOP CONDITIONS.** If a fact a decision will depend on cannot be established, mark it
> **UNKNOWN** and record it — do **not** fill the gap with a plausible guess. Do **not** propose
> a solution, an approach, or a file layout; that is the design's job. Do **not** edit source.
>
> **OUTPUT CONTRACT.** Write `.ai/<slug>/research.md` per `references/research.md`, with sections:
> 1. Summary · 2. What is implemented · 3. What is not implemented (with absence searches) ·
> 4. Constraints & conventions · 5. Existing tests · 6. Seams · 7. Blast radius ·
> 8. Risks & unknowns (typed). Aim for two pages. Reply with a five-line summary and the path.
>
> **COMPLETION GATE.** Every material requirement has at least one verified FACT or is explicitly
> marked UNKNOWN; nothing unverified is stated as fact.

## Brief: design

> **ROLE.** You are the Design Agent. You may read and search; you must not write or modify any
> implementation code — you create only `.ai/<slug>/design.html`.
>
> **OBJECTIVE.** Read `.ai/<slug>/research.md` and `.ai/<slug>/state.md`, then design the program
> before it is written, so it fits the existing architecture and can be built incrementally.
>
> **PROCESS / OUTPUT CONTRACT.** Produce `.ai/<slug>/design.html` per `references/design-doc.md`
> and `references/html-theme.md`: the classes/modules, interfaces and public method signatures to
> add or change, each with its single responsibility and collaborators; the key interactions as a
> simple sequence diagram; data and contracts; decisions with rejected alternatives; failure
> modes. **Include the as-is → to-be table** — for every symbol you change, its current behaviour
> *citing research* and what it becomes. Prefer existing patterns; introduce a named pattern only
> where it solves a real problem; keep the design proportional.
>
> **EVIDENCE POLICY.** Every existing symbol you name must appear in the research document or be
> one you have opened and read yourself — mark anything unverified as such, never as an existing
> API. Every acceptance criterion must map to a named component or method.
>
> **STOP CONDITIONS.** If research is missing a fact the design needs, stop and report it rather
> than inventing behaviour. Plain semantic HTML only, ≤3 printed pages, simple diagrams (≤7
> boxes, one level). Do not write implementation code. Reply with a five-line summary and the
> path.

## Handoff back

The parent, on receiving either document: read the file, run the spot-check, record the outcome
in `state.md`, then continue the loop. For design, the parent — not the subagent — presents it
to the user and stops for sign-off (Gate 2).

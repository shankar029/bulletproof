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
- **One writer.** Delegated research and design are read-only over the repo — they create files
  only under `.ai/<slug>/`. They never edit source.
- **Bound it.** Give the subagent a timeout and a scope; if it fails or hangs, record the
  blocker and fall back to inline rather than re-running it a third time.

## Which phases

| Phase | Delegate | Why |
|---|---|---|
| **1 — Research** | **Yes, by default** | Biggest context win; read-heavy, output small. |
| **2 — Design** | **Yes, by default** | Quality-critical artifact; benefits from fresh eyes and a single job. |
| **3 — Plan** | Optional | Short, derived entirely from the design, and the main agent must own execution ordering anyway. Inline is fine. |
| **4 — Implement** | Only for genuinely parallel work | See `parallel-execution.md`. |
| **6 — Review** | **Yes** | Independence is the point; prefer a different model. See `review-and-pr.md`. |

## Brief: research

> Read this repository and produce `.ai/<slug>/research.md` describing **what exists today**
> that bears on this requirement: `<requirement>`.
>
> Follow `references/research.md` exactly. Every claim about the codebase carries `path:line`
> and the snippet it rests on — **no citation, no claim**. Every "not implemented" carries the
> search that came up empty, with its scope. Head the file with the current commit sha.
>
> Cover only what the requirement touches or is constrained by: the code to be changed and its
> callers, existing contracts and shared types, the conventions this codebase actually uses,
> the tests already covering the area, and the seams the new work will attach to. Aim for two
> pages.
>
> Do **not** propose a solution, an approach, or a file layout — that is the design's job. Do
> not edit any source file. Reply with a five-line summary and the path.

## Brief: design

> Read `.ai/<slug>/research.md` and `.ai/<slug>/state.md`, then produce `.ai/<slug>/design.html`
> per `references/design-doc.md` and `references/html-theme.md`.
>
> Design the program before it is written: the classes/modules, interfaces and public method
> signatures to add or change, each with its single responsibility and collaborators; the key
> interactions as a simple sequence diagram; data and contracts; decisions with rejected
> alternatives; failure modes. **Include the as-is → to-be table**: for every symbol you change,
> its current behaviour *citing research* and what it becomes.
>
> Every existing symbol you name must appear in the research document or be one you have opened
> and read yourself. Every acceptance criterion must map to a named component or method.
> Plain semantic HTML only, ≤3 printed pages, simple diagrams (≤7 boxes, one level).
>
> Do not write or modify any implementation code. Reply with a five-line summary and the path.

## Handoff back

The parent, on receiving either document: read the file, run the spot-check, record the outcome
in `state.md`, then continue the loop. For design, the parent — not the subagent — presents it
to the user and stops for sign-off (Gate 2).

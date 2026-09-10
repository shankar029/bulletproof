# Reference: Delegating Phases to Subagents

**Research, verification and review always run in a subagent; design and parallel implementation
are delegated when the harness supports them.** Two reasons, and both are decisive for the
mandatory three:

1. **Independence** — a dedicated agent with one sharply-scoped job, fresh context, no accumulated
   drift. A reviewer or verifier that shares the implementer's context inherits its blind spots.
2. **Context economy** — research is the most token-expensive phase in the run: it reads dozens
   of files to produce two pages. Done in the main context, it burns the window on raw file
   contents *before implementation starts* — the phase that actually needs the room. Delegated,
   the main agent receives the two pages instead of the fifty files.

**Spend the context where the work is.**

## Capability ladder

**Research, verification (Phase 5) and review (Phase 6) are always run in a subagent — no
inline fallback.** Their whole value is independence and a fresh context: a research agent that
shares the implementer's context inherits its blind spots, and a reviewer that grades in the
same session cannot un-see the reasoning it is meant to catch. If the harness genuinely cannot
spawn a subagent, that is a **blocker** — record it in `state.md` and stop per prime directive 8;
do not silently fold these phases into the main context.

For the **other** delegated phases (design, and any parallel implementation), degrade
gracefully:

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
| **1 — Research** | **Required — always a subagent** | Independence + biggest context win; read-heavy, output small. Read-only. |
| **2 — Design** | **Yes, by default** (inline fallback allowed) | Quality-critical artifact; benefits from fresh eyes and a single job. |
| **3 — Plan** | Optional | Short, derived entirely from the design, and the main agent must own execution ordering anyway. Inline is fine. |
| **4 — Implement** | Only for genuinely parallel work | See `parallel-execution.md`. |
| **5 — Verify (E2E)** | **Required — always a subagent** | Independent proof; the agent that exercises the feature is not the one that built it. Read + execute + test-authoring. See below. |
| **6 — Review** | **Required — always a subagent** | Independence is the point; prefer a different model, tools scoped read-only. See `review-and-pr.md`. |

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

## Brief: verify (Phase 5 end-to-end)

> **ROLE.** You are the Verification Agent, running in a **fresh context** — you did not build
> this feature. Your job is to prove it works the way a real user or client would exercise it,
> and to leave that proof behind as committed tests and captured evidence. You may read,
> search, run the system and its tests, and **author end-to-end/integration tests** — but you do
> not modify production code; if a test can only pass by changing product behaviour, that is a
> finding, not a fix.
>
> **INPUTS.** The requirement and acceptance criteria, `design.html`, `traceability.md`, and the
> current working tree (implementation already complete).
>
> **PROCESS.** Map each acceptance-criterion scenario to existing coverage first; add tests only
> for the uncovered ones, extending the existing suite. Exercise the real public surface with the
> system actually running — **all browser/front-end verification uses `agent-browser`** (see
> `references/e2e-agent-browser.md`); non-browser surfaces per `references/testing-and-e2e.md`.
> Record exact commands, exit codes and results.
>
> **OUTPUT CONTRACT.** Capture evidence into `.ai/<slug>/evidence/` (commands, output,
> screenshots, console/errors, one pass/fail line per criterion) and fill the `Test` and
> `Evidence` columns of `traceability.md`. Reply with a five-line summary and the paths.
>
> **STOP CONDITIONS.** If the environment makes real end-to-end proof impossible (no network,
> credentials or runnable host), do **not** weaken the gate or fake a pass: verify at the deepest
> level the environment allows, name the blocker, list the criteria left environment-unverified,
> and give the exact command a human can run to finish the proof.

## Handoff back

The parent, on receiving either document: read the file, run the spot-check, record the outcome
in `state.md`, then continue the loop. For design, the parent — not the subagent — presents it
to the user and stops for sign-off (Gate 2).

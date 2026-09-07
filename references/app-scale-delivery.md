# Reference: Delivering an Entire App (App-Scale Mode)

The six-phase loop delivers **one requirement** and ships **one PR**. An entire app (web or
mobile) is *many* requirements. This reference adds a thin **outer loop** that decomposes the app
into an ordered sequence of vertical slices and delivers them **incrementally in one session, on
one branch, in one PR** — with each slice held to the same quality bar. It is the lightweight
alternative to the multi-session `epic-feature-workflow` (per-feature worktrees, epic branch,
squash-merges, many PRs): same decomposition discipline, far less git ceremony.

## When this mode applies

**Enter app-scale mode** when either is true:
- **Auto-detect:** the requirement implies **multiple independently-valuable features** or a
  **greenfield app** (e.g. "build a task-tracker web app", "create the mobile app for X"). A single
  screen, endpoint, or bug fix is **not** app-scale — use the normal single-pass loop.
- **Explicit override:** the invocation asks for app/milestone/incremental delivery (e.g.
  `/bulletproof --app <idea>`, or the ask names phases/milestones).

**Do NOT enter app-scale mode** for a single feature — the outer loop is overhead there.

**Prefer `epic-feature-workflow` instead** when the app is large enough that it *cannot* fit one
session even sliced thin, when each feature genuinely needs its own reviewable PR, or when the work
will span multiple sessions/contributors. App-scale mode maximizes **single-session** output; it
does not repeal the model's context ceiling. When context runs low, **checkpoint and stop cleanly**
(see Context management) rather than degrading quality.

## The outer loop — walking skeleton, then thicken

1. **Phase 0 — Decompose (once, up front).** Turn the app into a **milestone list**: `M0` = a
   walking skeleton, `M1..Mn` = feature increments in dependency order. Record it in the plan doc
   as a checkbox list with per-milestone acceptance criteria. This *is* Phase 1–3 for the app as a
   whole; individual milestones still get their own focused understand/design/plan pass when you
   reach them.
2. **M0 — Walking skeleton first.** Deliver **one thin end-to-end vertical slice** that actually
   runs: the smallest path through every layer (data → domain → API → one screen/route → one real
   test → one E2E). This proves the architecture, wiring, build, and E2E harness **before** volume
   is added. Never build all of one layer horizontally first. **For a UI app, get the UX design
   approved first** (see `references/ux-design.md`) — approve the navigation shell, design system,
   and the M0 flow once here, not screen-by-screen later.
3. **M1..Mn — Thicken by vertical slice.** Each milestone adds one coherent, independently-valuable
   feature end-to-end (its own UI + API + data + tests + E2E), building on the skeleton.
4. **Between milestones — keep it green.** The app builds and the full suite passes at **every**
   milestone boundary. A milestone that reddens earlier milestones is not done.

## Decomposing into milestones — the rules

- **Vertical, not horizontal.** Each milestone is a full-stack slice a user can exercise — not "all
  the models", then "all the endpoints", then "all the screens". Horizontal layers leave nothing
  demonstrable until the end and hide integration risk.
- **Dependency-ordered.** Foundations first (auth, data model, shared types, design system,
  navigation shell) as part of `M0`/early milestones; dependents after. Draw the dependency graph;
  the order falls out of it.
- **Independently shippable & testable.** Each milestone ends in a demonstrable, tested increment —
  if you stopped after any milestone, what exists is coherent and green, never half-wired.
- **Small enough to converge.** If a milestone can't reach the quality bar within a sane slice of
  the session, split it. Right-size to 30–90 minutes of focused work each.
- **Map every milestone to app-level acceptance criteria.** The union of milestone ACs must cover
  the whole app request — nothing dropped, no scope invented.

## Per-milestone execution — the inner loop

For **each** milestone, run the normal six phases at **right-sized** rigor:
- **Understand/Plan** the milestone against the app profile you already built (don't re-profile the
  project every time — reuse it).
- **Implement + Test** the slice: real unit + integration tests, left green (Phase 4 gate).
- **E2E** the slice like a human (Phase 5) — see E2E cadence below.
- **Review** the slice (Phase 6 self-review) and **commit it** (see ceremony).
- **Score** the slice against the quality rubric; converge it to ≥4/5 before moving on. Do **not**
  carry a below-bar milestone forward hoping to fix it later — that compounds into debt.

**Parallelism:** when the agent supports subagents and two upcoming milestones are file-disjoint and
dependency-free, fan them out per `parallel-execution.md` (worktree each), then integrate and run
the whole-app gate. Serialize anything sharing schema/types/design-system/navigation.

## Lightweight ceremony (the anti-"time-consuming" part)

- **One feature branch** for the whole app increment (e.g. `feat/<app>`). Create it before the first
  commit; never commit on `main`/`master`.
- **One commit per milestone** — a clean, Conventional-Commit checkpoint with per-milestone evidence
  trailers (tests/coverage/E2E for that slice). This gives a readable, bisectable history and a
  natural resume point **without** per-feature branches, worktrees, or merges.
- **One PR at the end**, its body assembling the per-milestone evidence into a whole-app bundle.
- Contrast with `epic-feature-workflow`, which isolates each feature on its own worktree+branch and
  opens many PRs — correct for multi-session epics, unnecessary overhead for a single-session app.

## Context management — deliver as much as the session allows

The real constraint at app scale is context, not capability. Manage it deliberately:
- **The plan doc is durable state.** Keep an up-to-date checkbox milestone list with, per completed
  milestone, a **one-line summary** (what shipped, key files, decisions). This lets you — or a fresh
  session — resume with zero rework.
- **Summarize, don't re-read.** Once a milestone is committed and summarized, rely on the summary +
  the commit, not on holding every file in context.
- **Checkpoint before you run out.** When context is getting tight, finish the **current** milestone
  to green, commit it, update the plan, and **stop cleanly** — report which milestones are done and
  exactly where to resume. A clean checkpoint beats a half-finished milestone every time.
- **Offload disjoint slices to subagents** to keep the main context lean, then integrate.

## Path to production (when the ask includes shipping, not just building)

"To production" is more than a merged PR. When going live is in scope, treat it as the **final
milestone(s)** and work the full **`references/production-readiness.md`** checklist — build/release,
config & secrets, environments, data/migrations/backups, CI/CD, observability, security hardening,
performance/scaling, reliability/rollback/DR, networking/TLS, privacy/compliance, cost, ops docs
(and mobile app-store release when mobile). **Capture each item in the plan as a trackable checkbox**
(addressed, or N/A with a reason). Right-size to the stack — skip what genuinely doesn't apply (a
static site has no migrations; a CLI has no CORS), but say so. Absent a real deploy target this run,
deliver the **production-readiness artifacts** (Dockerfile/CI/env config, migrations, health checks,
runbook) and state exactly what remains to actually go live.

## Whole-app E2E cadence

- **Skeleton E2E first (M0):** stand up the real E2E harness (Playwright for web, Detox/Maestro/
  device runner for mobile — see `testing-and-e2e.md`) and prove the one thin flow end-to-end. This
  de-risks the harness before volume.
- **Per-milestone E2E:** each feature milestone adds/extends E2E for its own slice (extend the suite,
  never duplicate it).
- **Final whole-app E2E:** before shipping, run the full E2E suite plus a **cross-feature smoke
  path** a real user would take across milestones (e.g. sign up → create → edit → delete → sign
  out). Integration bugs live in the seams between features; this pass is where you catch them.

## App-scale Definition of Done

Everything in the normal ship gate, **plus**:
- Every milestone is committed on the feature branch, green, and scored ≥4/5 — or the run is
  cleanly checkpointed with an accurate, resumable plan doc.
- The app **builds and runs**, and the **whole-app E2E + cross-feature smoke** pass on the
  integrated result (not just per-milestone green).
- The union of delivered milestones covers the app's acceptance criteria — anything deferred is an
  explicit, listed follow-up, never smuggled debt.
- If "to production" was asked: the production-readiness artifacts in
  `references/production-readiness.md` exist and are verified as far as the environment allows.

## A note on ordering

Inside a single requirement the order is fixed: **research -> design -> plan**. At app scale the
outer loop inverts once, and only once: the coarse split into slices happens *first*, because no
one can design a whole product up front. **Each slice then runs the normal order** - its own
research, its own design and sign-off, its own plan - at the same bar. "Plan" therefore means two
different things at two altitudes: out here it is which slices and in what sequence; inside a
slice it is which session-sized increments.

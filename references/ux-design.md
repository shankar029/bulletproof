# Reference: UX Design & the Design-First Approval Gate

Applies whenever the change has a **user-facing surface** (web or mobile UI). For non-UI work
(library / CLI / API-only) skip this entirely. The goal: design a **high-quality UX first**, get the
user's **approval before building the UI**, then implement against the approved design — so you never
build the wrong experience and redo it.

## The design-first approval gate (runs in Phase 2, before any UI code)

1. **Design the UX before writing UI code** — produce the UX spec below to a high bar.
2. **Present it and, when a user is present, pause for approval.** Offer **accept / reject / modify**;
   fold the feedback back in; re-present if the changes are material. Do **not** implement UI until
   the design is approved.
3. **Headless / one-shot (no user to answer)** → do **not** block: record the UX proposal as an
   explicit assumption, proceed, and surface it in the PR for confirmation. (Mirrors the Phase 1
   clarify rule.)
4. Build only against the **approved** (or headless-defaulted) design.
5. **App-scale mode:** run this gate **once at the walking-skeleton milestone** — approve the
   navigation shell, the design system, and the M0 flow together — and re-check only when a later
   milestone introduces a genuinely new UX pattern. Don't re-approve every screen.

## The UX spec — what "design first" produces

Right-size to the surface, but a good UX spec covers:
- **Users & goals** — who uses this and the primary jobs to be done.
- **Information architecture** — the screen/route inventory and how they relate; the navigation
  model (tabs / stack / drawer / sidebar).
- **User flows** — the primary end-to-end paths (happy path + key alternates), step by step.
- **Per-screen layout** — structure, key components, visual hierarchy, and the primary action for
  each screen (a low-fi wireframe is enough).
- **All states per screen** — loading, empty, error, success, and edge/permission states — not just
  the happy path.
- **Design system** — spacing scale, typographic scale, color tokens (incl. semantic), component
  inventory, iconography. **Reuse the project's existing system if one exists**; otherwise define a
  minimal, consistent one.
- **Responsive / adaptive behavior** — breakpoints and how layout reflows (web); orientation,
  safe-area, and device sizes (mobile).
- **Content & microcopy** — labels, empty-state text, error messages, CTAs.
- **Interaction & motion** — feedback on actions, transitions, and any purposeful animation.

## The quality bar — UX principles & standards (aim high)

A "very good" UX honors these; call out where a choice trades one against another.

- **Usability heuristics (Nielsen's 10):** visibility of system status; match to the real world;
  user control & freedom (undo / cancel / back); consistency & standards; error prevention;
  recognition over recall; flexibility & efficiency; aesthetic & minimalist design; help users
  recognize & recover from errors; help & documentation where needed.
- **Visual & layout:** clear visual hierarchy; alignment to a grid; consistent spacing rhythm; a
  deliberate typographic scale; restrained, purposeful color; **Gestalt** grouping (proximity,
  similarity, common region); generous whitespace; scannable content.
- **Cognitive load:** progressive disclosure (don't dump everything at once); chunking; sensible
  defaults; minimize choices on a path (**Hick's law**); make primary actions large and reachable
  (**Fitts's law**).
- **Interaction & feedback:** every action gets immediate, visible feedback; destructive actions are
  confirmed and reversible; forms validate inline with specific, helpful messages; loading uses
  skeletons / optimistic UI where it helps; nothing dead-ends.
- **Accessibility (WCAG 2.2 AA — non-negotiable):** text contrast ≥ 4.5:1 (3:1 for large text / UI
  components); full keyboard operability with a visible, logical focus order; semantic structure and
  correct roles/labels for screen readers; touch targets ≥ 44×44 px; never rely on color alone;
  respect reduced-motion; label every input.
- **Platform conventions:** **web** (familiar patterns, responsive, correct back-button semantics);
  **iOS** (Apple **HIG** — navigation bars, SF Symbols, standard gestures); **Android** (**Material**
  — app bars, FAB, predictive back). Match the target platform rather than porting another's idioms.
- **Content:** clear, concise, human microcopy; consistent terminology; actionable error/empty states.

The built result must score ≥ 4/5 on `quality-bar.md` §"UX & visual design" before shipping.

## Artifact fidelity & rendering the design

Default to the **lowest-friction artifact that enables a real decision**:
- **(a) Text UX spec + low-fi ASCII wireframes + the flow list** *(default)* — fast, reviewable
  inline, wastes no build effort before approval.
- **(b) Static HTML mockup / prototype** *(higher fidelity)* — build a throwaway HTML/CSS mockup (or
  one key screen) the user can open when a visual is worth it, especially for web. Keep it out of the
  shipped tree, or clearly mark it a prototype.

### Optional: present via the `clarity` skill (render the design in the web)

If the **`clarity`** skill is available — check for `~/.agents/skills/clarity/scripts/serve.mjs` (or
the project-local install) — use it to render the UX for **structured web approval** instead of
terminal Q&A:
1. Author a clarity doc spec (JSON): the UX spec as prose blocks, the wireframes/flows, an
   **embedded HTML mockup preview** where you have one, and a **recommendation block**
   (accept / reject / modify) plus an open-comment / upload zone for annotated feedback.
2. Serve and block for the user:
   `node <clarity>/scripts/serve.mjs <spec>.json --out .feedback/ux --timeout 60`.
3. Read `.feedback/ux/response.md` — apply accepted/modified decisions and inline comments;
   re-present if the changes are material.
4. Handle non-zero exit codes (2 = cancel, 3 = timeout) by falling back to terminal approval.

If clarity is **not** available, present the UX spec in the terminal / plan doc and pause for
approval there.

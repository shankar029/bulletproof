# Reference: The Design & Plan Documents (HTML, max 3 pages)

These documents exist so a human can absorb the solution in **under five minutes** and approve
or redirect it *before* code is written. They are decision aids; the plan also links the complete
execution contract defined in `planning.md`. They live
in `.ai/<slug>/` — see `workspace.md`.

| File | When | Contains |
| --- | --- | --- |
| `design.html` | always (non-trivial work) | program design: classes, interfaces, interactions |
| `architecture.html` | large work only | components and how they talk |
| `plan.html` | always (non-trivial work) | increments, tasks, test strategy |
| `tasks.md` | only when execution detail does not fit the overview | task/check records linked from `plan.html`; no duplicate records |

## Current contract and retained revisions

Before adoption, these documents support ordinary procedural research, design review and
planning. They are not required to have prior guarded admissions: the initial candidate
must exist before it can be adopted. Human approval remains confirmed only by the human;
explicit unattended authorization permits an unconfirmed assumption, not a backfilled approval.

For guarded operation, use [workflow-gates.md](workflow-gates.md#prepare-and-adopt-reviewed-artifacts).
Retain the design and normative component definitions under revision-specific paths, stage
the existing-schema workflow/current-design candidates, and bind independent review to the
exact candidate hashes. Invoke ordinary `adopt`; never directly overwrite the live pointer.
On revision, preserve old bytes and their history rather than rewriting the earlier rationale.
Subsequent implementers/reviewers resolve `current-design.json`, not whichever HTML filename
looks newest. A new revision does not supply earlier execution or compatibility proof.
Retirement requires accepted pre-action compatibility evidence per
[planning](planning.md#3-write-executable-task-records).

## Hard rules

- **Design for a maintainer, not just an executor.** Apply `code-clarity.md` in the existing
  responsibility table and interactions: visible main flow, shared contracts, explicit state
  ownership, and boundaries that reduce understanding effort. Avoid speculative abstractions;
  no additional document or section is required.
- **Write plain semantic HTML and let the shared theme style it** — see `html-theme.md`. No
  `<style>` block, no inline styles, no colours. Documents link `../assets/artifact.css` and
  `../assets/artifact.js`, which also provide the reading controls and the comment/approval
  layer.
- **Maximum 3 printed pages** (~1,500 words including diagrams). If it doesn't fit, your
  design is being explained at the wrong altitude — cut prose, not content: convert
  paragraphs into tables and diagrams. Check the length by printing to PDF, not by guessing.
  For the execution plan this caps the **HTML overview**: preserve necessary task/check details
  in linked `tasks.md` rather than deleting prerequisites or proof to meet the page limit.
- **Diagrams carry the structure; text only carries what a diagram can't.** Every design has at
  minimum one class/module diagram and one sequence diagram for the critical flow; every plan
  has a build-order/dependency diagram (see `plan.html` below). A reader should understand the
  shape from the pictures before reading a word.
- **Write in plain language a competent newcomer can follow.** Short sentences, one idea per
  bullet, active voice. Prefer the everyday word to the fancy one; spell out an acronym the
  first time; explain any term specific to this change. Assume the reader knows software but
  **not** this codebase or your reasoning — the document must teach it, not gesture at it. If a
  sentence needs a second read, rewrite it.
- **Every existing symbol named in the document must be one you have read in the source.**
  Mark anything unverified with `class="unverified"` — never present a guess as an existing API.
- **No essays, no restating the requirement, no boilerplate, no jargon for its own sake.**
  Bullets, tables, signatures, diagrams.

## Structure (in order, with page budget)

For consequential interface choices, compare two materially different approaches within the
existing decisions table: a realistic caller example, what each hides, where change concentrates,
and the trade-off that justifies the recommendation. Routine designs need no extra alternatives
exercise or agent fan-out. Use `code-clarity.md`'s caller-burden check.

Resolve domain-term ambiguities raised by research before approving behavior. Reuse the existing
glossary; add a durable definition only when the ambiguity matters beyond this task and updating
that documentation is in scope. Keep implementation history out of the glossary. Record an ADR
only for a real trade-off that is costly to reverse and surprising without context, in the
repository's established location; otherwise the design decision record is enough.

If a design question needs a prototype, agree the question, success signal, scope and stopping
condition first. Keep the experiment clearly marked and isolated from production wiring/data
in the task workspace or an authorized scratch worktree. Capture the answer and its limitations
in the design, then remove throwaway code or retain it outside the release with a clear purpose.
Prototype output is not production proof and does not waive Gate 2 sign-off; production
implementation still requires the normal contracts, tests, verification and review.

| Section | Content | Budget |
| --- | --- | --- |
| **1. Problem & scope** | 3–5 bullets: what changes, which acceptance criteria (by id), what is explicitly out of scope. | ⅕ page |
| **2. Program design** | The class/module diagram, then a table: each new or changed type with its **single responsibility**, **public method signatures**, **collaborators**, the **acceptance criterion it serves** (`Why`), and the **design principle/pattern** it embodies (`Principle`). This is the heart of the document. A row with no `Why` is unnecessary — cut it. | ¾ page |
| **2b. As-is → to-be** *(any change to existing code)* | A second, narrow table inside section 2 — one row per **changed** symbol: its current behaviour **citing `research.md`**, and what it becomes. New types have no as-is and do not appear here. Omit the table only when nothing existing changes, and say so. | ¼ page |
| **3. Key interactions** | Sequence diagram of the 1–2 critical flows (including the main failure path). | ½ page |
| **4. Data & contracts** | Schemas, payloads, persisted shapes, migration and compatibility notes. Table or code block. | ¼ page |
| **5. Decisions & trade-offs** | Table: decision · alternatives rejected · why. Include the pattern choices, **and every standard imported to close an Absent profile axis** (`project-profile.md`). These are decisions already taken. | ¼ page |
| **5b. Design options for sign-off** *(when any exist)* | Structural options the design did **not** take but the human may want — each with what it buys, cost, **reversibility**, and a recommendation. Open questions, not decisions. Omit the section when there are none, and say so. | ¼ page |
| **6. Risks, edge cases & failure modes** | What can go wrong, and what the design does about each. | ¼ page |
| **7. Test strategy — proposed, not run** | Table mapping each acceptance criterion → unit / integration / end-to-end test, **each with its owner**: unit and integration are written in Phase 4 by the implementer, end-to-end in Phase 5 by the verifier. These are planned checks, never results. | ¼ page |
| **`architecture.html`** *(large work only — separate file, unnumbered)* | One simple component diagram: the pieces, their responsibilities, and how they communicate. Omit the file entirely for contained changes. | ½ page |

**Sections 6 and 7 may be merged** into one *Decisions & failure behavior* table for a contained
change, provided every rejected alternative and every failure mode still has its own row. Nothing
else merges, and the order above does not change — the Gate 2b reviewer grades against it.

## As-is → to-be: what makes a brownfield change reviewable

A design that shows only the destination is unreviewable on an existing codebase: the reader
cannot tell what is being preserved from what is being replaced. Section 2b carries that delta.

| Symbol | As-is (cite `research.md`) | To-be |
|---|---|---|
| `OrderService.submit` | Validates inline, throws on bad input — `research.md` §3, `order.ts:88` | Delegates validation to `PricingPolicy`; returns `Result`, never throws |

Rules:

- **Every changed symbol gets a row.** A symbol you modify without an as-is row is an unreviewed
  change.
- **The as-is side cites `research.md`**, which cites the source. An as-is written from memory is
  a HYPOTHESIS, not a FACT — re-read the symbol instead.
- **State the behaviour, not the diff.** "Returns `null` on miss" is reviewable; "changes line 88"
  is not.
- **Preserved behaviour counts.** If a caller-visible contract deliberately does *not* change, say
  so — that is the invariant Phase 5 will check.

## Test strategy: no blank end-to-end cell

Section 7 is where end-to-end coverage is committed to, and it is the cell agents most often leave
empty. **Every AC gets either a named end-to-end scenario or an explicit `N/A — <reason>`**, and
the reason must come from this closed list:

- the AC is a pure function or algorithm with **no observable surface**, fully covered by unit tests;
- the AC is an **internal refactor with no caller-visible behaviour change** — and the as-is →
  to-be row says exactly that;
- the AC's surface is **already covered by a named existing end-to-end test**, cited by path.

Anything else is not N/A; it is an unplanned scenario, and Gate 2a fails. A closed list is what
stops `N/A` becoming a shrug.

The column headers name the owner — `Unit (Ph4)`, `Integration (Ph4)`, `End-to-end (Ph5)` — because
the implementer writes the first two and the verifier writes the third. Phase 5 then enumerates
its scenarios from four sources and covers the full class matrix
(`testing-and-e2e.md`); this table is the **floor** it starts from, never the ceiling.

## Design options for sign-off: the one-way doors

Section 5 records decisions already taken. Section 5b records the ones **the human should take**
— structural choices that are legitimately theirs, surfaced *with* the design rather than
discovered after implementation.

This is the design-level counterpart to `research.md` § Adjacent scope, and the same rule governs
it: **proposing is not creep; building unasked is.** An option is never implemented without an
explicit yes, and the design as written must stand on its own if every option is declined.

### Extension pressure: where the next change will land

Options do not come from imagination. Before filling 5b, run this check — it is the bridge from
Phase 1's grounded proposals to this design's structure.

Take every **adjacent-scope** proposal in `research.md` — accepted, deferred *and* declined — plus
any change this codebase visibly keeps making (a pattern added repeatedly, a switch statement that
has grown three times, an interface every new feature has had to widen). For each, ask one
question:

> **If this lands next, is it additive to this design, or surgery on its core?**

Then apply the decision rule — all three conditions, not one:

| Likelihood (grounded) | Seam cost now | Retrofit cost | Verdict |
| --- | --- | --- | --- |
| High | Low | High (one-way) | **Adopt now** — this is the case 5b exists for |
| High | Low | Low (two-way) | **Defer** — add it when the requirement is real |
| High | High | High | **Option for the human** — a genuine cost/benefit call, not yours |
| Low | any | any | **Decline** — name it, do not build it. YAGNI wins |

**Likelihood must be grounded** the same way a proposal is: an adjacent-scope trigger, a roadmap
or issue, a repeated change visible in the code's own history, or an explicit statement in the
requirement. "Requirements usually grow" is not grounding — it is the argument that justifies
every speculative abstraction ever shipped.

The honest outcome of this check is usually **"additive already, no option needed"**. Record that
in one line and move on; it is evidence the design is right, not a section to pad.

For large work, `architecture.html` carries the same check at component granularity: name which
seam absorbs each likely change, or say plainly that a new component would be required.

| Field | Required |
| --- | --- |
| **Option** | The structural change, in one line. |
| **What it buys** | The concrete future change it makes cheap, or the quality dimension it serves. Name it — "cleaner" is not an answer. |
| **Cost** | S / M / L against the stated work, with the reason. |
| **Reversibility** | **One-way** — cheap now, expensive to retrofit (a persisted shape, a public contract, a module boundary others will depend on). **Two-way** — safely addable later. |
| **Recommendation** | Adopt now · Defer · Decline (named so the reader knows it was considered). |

Reversibility is the field that matters, and the reason this section exists at all. A **two-way**
option can safely wait for evidence that it is needed — defer it and say so. A **one-way** option
is a door that closes when Phase 4 starts, so it must be decided at Gate 2 by the person who owns
the consequences, not silently by the agent that happened to write the design.

Grounding, the same as everywhere else:

- An option names **the change it makes cheap** with a plausible trigger, not a principle in the
  abstract. "Add a port so we could swap the DB" with no reason to think the DB will change is
  speculative generality — exactly what `code-clarity.md` rejects.
- **Missing structure is a finding, not an option.** If the design is wrong without it, fix the
  design; do not launder a defect into a menu item.
- **None is a valid answer.** Most contained changes have no open structural question. Omit the
  section and say so rather than manufacturing choices.
- At most **three**. More than that means the design has not made its own decisions.

The Gate 2b reviewer may add options of its own under the same contract — it is fresh-context and
often a different model, so it is well placed to see a seam the author missed. Its options are
proposals to the human, never required changes, and never a substitute for a REVISE finding.

At Gate 2 the handover asks the human for a verdict **and a decision on each open option**. An
unanswered option is declined — silence is not consent — and every declined one-way option is
recorded in the final report's follow-ups with the cost of retrofitting it.

## Diagrams — keep them simple

A diagram that needs study has failed. Deliberately crude beats comprehensive.

**Limits, not suggestions:**

- **At most 7 boxes** per diagram. More than that means you are drawing the whole system
  instead of the part that matters — raise the altitude or split into two diagrams.
- **One level of detail.** No nested boxes, no swimlanes, no sub-graphs, no layered
  groupings, no colour coding, no legends.
- **Plain rectangles and straight arrows only.** Label the arrow with the call or the data —
  not with a sentence.
- **Show only what is essential to the decision.** Omit obvious infrastructure, logging,
  error plumbing, and anything the reader can assume.
- **Arrows in the class/module diagram are dependency direction** — drawn from the depender to
  the thing it depends on. State the direction in the caption and keep it consistent with the rule
  the design adopted (`project-profile.md` § Architecture when the project has none). No arrow
  points *into* domain/policy from an adapter; if one does, the design is wrong, not the diagram.
- **Spend zero effort on visual polish.** Alignment and beauty do not matter; the right boxes
  do. Never iterate on appearance.

Hand-author **inline SVG** using only the theme's diagram classes — `.b` / `.b-alt` for boxes,
`.a` / `.a-dash` for arrows, `.t` for titles, `.s` and `.l` for labels. Never set `fill`,
`stroke`, or `font` directly: the classes adapt to light and dark, hard-coded colours do not.

If the repository already uses a text-diagram tool you may use its syntax, but the document
must still render offline, so embed the rendered output rather than relying on a CDN.

Reusable primitives:

```html
<!-- box -->
<rect x="20" y="20" width="160" height="56" rx="6" class="b"/>
<text x="100" y="44" class="t">OrderService</text>
<text x="100" y="62" class="s">places &amp; validates orders</text>
<!-- arrow -->
<line x1="180" y1="48" x2="260" y2="48" class="a" marker-end="url(#ar)"/>
<text x="220" y="40" class="s">submit()</text>
```

## Skeleton

Head per `html-theme.md`, then plain HTML. No styling anywhere in the document.

```html
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design — <TASK></title>
<link rel="stylesheet" href="../assets/artifact.css">
<script src="../assets/artifact.js" defer data-doc="design.html" data-slug="<SLUG>"></script>

<h1><TASK> — Design</h1>
<div class="meta">Requirement: <REF> · Criteria: AC1–ACn · <DATE></div>

<h2>1. Problem &amp; scope</h2>
<ul><li>…</li></ul>
<p class="assumption">Assumptions (unconfirmed): …</p>

<h2>2. Program design</h2>
<figure>
  <svg viewBox="0 0 640 220" role="img" aria-label="Class diagram">
    <defs><marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="3"
      orient="auto"><path d="M0,0 L0,6 L9,3 z"/></marker></defs>
    <rect x="20" y="20" width="170" height="58" rx="6" class="b"/>
    <text x="105" y="45" class="t">OrderService</text>
    <text x="105" y="63" class="s">places &amp; validates orders</text>
    <line x1="190" y1="49" x2="280" y2="49" class="a" marker-end="url(#ar)"/>
    <text x="235" y="41" class="l">submit()</text>
  </svg>
  <figcaption>Fig 1 — types and ownership. Arrows are dependency direction:
    application → domain; no adapter arrow points into domain.</figcaption>
</figure>
<table>
  <tr><th>Type</th><th>Responsibility</th><th>Public API</th><th>Collaborators</th><th>Why (AC)</th><th>Principle</th></tr>
  <tr><td><code>OrderService</code> <em>(new)</em></td><td>One sentence.</td>
      <td class="sig">place(Order): Receipt<br>cancel(id): void</td>
      <td><code>OrderRepo</code>, <code>PricingPolicy</code></td>
      <td>AC1, AC3</td><td>SRP; Strategy for pricing</td></tr>
</table>

<h3>2b. As-is &rarr; to-be</h3>
<table>
  <tr><th>Symbol</th><th>As-is (cite <code>research.md</code>)</th><th>To-be</th></tr>
  <tr><td><code>OrderService.submit</code></td>
      <td>Validates inline, throws on bad input — <code>research.md</code> §3, <code>order.ts:88</code></td>
      <td>Delegates to <code>PricingPolicy</code>; returns <code>Result</code>, never throws</td></tr>
</table>

<h2>3. Key interactions</h2>
<figure><svg viewBox="0 0 640 220" role="img" aria-label="Sequence diagram"><!-- … --></svg>
  <figcaption>Fig 2 — happy path and the primary failure path.</figcaption></figure>

<h2>4. Data &amp; contracts</h2>
<table><tr><th>Shape</th><th>Fields</th><th>Compatibility / migration</th></tr></table>

<h2>5. Decisions &amp; trade-offs</h2>
<table><tr><th>Decision</th><th>Rejected alternative</th><th>Why</th></tr></table>

<h3>5b. Design options for sign-off</h3>
<table>
  <tr><th>Option</th><th>What it buys</th><th>Cost</th><th>Reversibility</th><th>Recommendation</th></tr>
  <tr><td>Extract <code>PricingPolicy</code> behind an interface</td>
      <td>Adding a second promo type becomes additive, not a rewrite of <code>OrderService</code></td>
      <td>S</td><td><strong>One-way</strong> — callers bind to the shape</td><td>Adopt now</td></tr>
</table>

<h2>6. Risks, edge cases &amp; failure modes</h2>
<table><tr><th>Case</th><th>Handling</th></tr></table>

<h2>7. Test strategy &mdash; proposed, not run</h2>
<table><tr><th>AC</th><th>Unit (Ph4)</th><th>Integration (Ph4)</th><th>End-to-end (Ph5)</th></tr></table>
```

## Keeping it honest

The document is a commitment, not decoration. Phase 4 implements *this* design; if the code
must diverge, update the document and re-check Gate 2 rather than letting the two drift.

**It passes an independent design review (Gate 2b) before the human sees it.** A fresh-context
review subagent grades it against the `project-profile.md` checklist — requirement coverage,
SOLID/cohesion/coupling, right-sized pattern (over- *and* under-engineering), interface quality,
failure handling, testability, security/performance, and grounding — and returns
APPROVE / REVISE / REJECT in `design-review.md`. The `Why (AC)` and `Principle` columns exist so
that review is fast and concrete: coverage and YAGNI are checkable at a glance.

**Re-check the page count after every revision.** Folding review findings back into the
document is exactly when it creeps past three pages — measure by printing to PDF, then trim
content (merge table rows, delete what a signature already says). Never shrink the type.

## `plan.html`

Same HTML shell and three-page overview, different body — the **executable projection of the
design**, not a fresh set of facts. Follow `planning.md` for the full procedure and task/check
contract. Keep detailed records here when they fit, otherwise link to `tasks.md`; do not duplicate.

- **Outcome & scope:** observable desired end state, linked ACs/design, exclusions and invariants.
- **Build-order table:** each row is a vertical increment, with outcome, design references, ACs,
  prerequisites, exact affected files, task/detail links and completion checks. The same component
  can occur again with a distinct owned change. Every planned change has one task owner.
- **Task/check records:** precise changes and dependencies, reuse/preservation, execution and
  proof requirements, verification owners, stop/recovery conditions and evidence. Keep the
  per-increment and final regression strategy, coverage expectation and E2E cadence visible.
- **Progress & revisions:** stable IDs, status/evidence links and changed-task history per
  `planning.md`; no completed checkbox without supporting change/check evidence.

Illustrative structure only: these types, ACs, paths and checks are examples, not repository
facts or a ready-to-run plan. I1 delivers order placement end to end; I2 extends it with
cancellation. Inside each increment, tasks order contracts, core behavior, wiring and proof.

```html
<h2>1. Build order</h2>
<table>
  <tr><th>ID</th><th>Outcome / design change</th><th>ACs</th><th>Depends on</th><th>Files</th><th>Tasks / proof</th></tr>
  <tr><td>I1</td><td>Place an order and receive a receipt: OrderService.place + OrderRoutes</td>
      <td>AC1</td><td>Approved design</td><td>src/order.ts; src/routes.ts; test/order.test.ts</td>
      <td>I1.T1 contracts; I1.T2 behavior/wiring; I1.T3 unit + integration + E2E proof</td></tr>
  <tr><td>I2</td><td>Cancel an eligible order: extend OrderService + OrderRoutes</td>
      <td>AC2</td><td>I1 complete</td><td>src/order.ts; src/routes.ts; test/order.test.ts</td>
      <td>I2.T1 cancellation; I2.T2 unit + integration + E2E proof and placement regression</td></tr>
</table>
```

A **build-order/dependency diagram is required**: boxes are increments, arrows are "depends on",
read left-to-right in build order. It lets a reader grasp the sequence in one glance — keep it to
the same limits as every diagram (≤7 boxes, one level, plain rectangles and arrows). Use a
second diagram only if one genuinely can't hold the shape.

```html
<figure>
  <svg viewBox="0 0 640 120" role="img" aria-label="Build order">
    <defs><marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="3"
      orient="auto"><path d="M0,0 L0,6 L9,3 z"/></marker></defs>
    <rect x="20"  y="40" width="150" height="48" rx="6" class="b"/>
    <text x="95"  y="68" class="t">I1 · Place order</text>
    <line x1="170" y1="64" x2="240" y2="64" class="a" marker-end="url(#ar)"/>
    <rect x="240" y="40" width="150" height="48" rx="6" class="b"/>
    <text x="315" y="68" class="t">I2 · Cancel order</text>
  </svg>
  <figcaption>Fig — increments in build order; an arrow means "needs the previous one first".</figcaption>
</figure>
```

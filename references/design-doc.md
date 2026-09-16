# Reference: The Design & Plan Documents (HTML, max 3 pages)

These documents exist so a human can absorb the solution in **under five minutes** and approve
or redirect it *before* code is written. They are decision aids, not specifications. They live
in `.ai/<slug>/` — see `workspace.md`.

| File | When | Contains |
|---|---|---|
| `design.html` | always (non-trivial work) | program design: classes, interfaces, interactions |
| `architecture.html` | large work only | components and how they talk |
| `plan.html` | always (non-trivial work) | increments, tasks, test strategy |

## Hard rules

- **Write plain semantic HTML and let the shared theme style it** — see `html-theme.md`. No
  `<style>` block, no inline styles, no colours. Documents link `../assets/artifact.css` and
  `../assets/artifact.js`, which also provide the reading controls and the comment/approval
  layer.
- **Maximum 3 printed pages** (~1,500 words including diagrams). If it doesn't fit, your
  design is being explained at the wrong altitude — cut prose, not content: convert
  paragraphs into tables and diagrams. Check the length by printing to PDF, not by guessing.
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

| Section | Content | Budget |
|---|---|---|
| **1. Problem & scope** | 3–5 bullets: what changes, which acceptance criteria (by id), what is explicitly out of scope. | ⅕ page |
| **2. Architecture** *(large work only, in `architecture.html`)* | One simple component diagram: the pieces, their responsibilities, and how they communicate. Omit entirely for contained changes. | ½ page |
| **3. Program design** | The class/module diagram, then a table: each new or changed type with its **single responsibility**, **public method signatures**, **collaborators**, the **acceptance criterion it serves** (`Why`), and the **design principle/pattern** it embodies (`Principle`). This is the heart of the document. A row with no `Why` is unnecessary — cut it. | 1 page |
| **4. Key interactions** | Sequence diagram of the 1–2 critical flows (including the main failure path). | ½ page |
| **5. Data & contracts** | Schemas, payloads, persisted shapes, migration and compatibility notes. Table or code block. | ¼ page |
| **6. Decisions & trade-offs** | Table: decision · alternatives rejected · why. Include the pattern choices. | ¼ page |
| **7. Risks, edge cases & failure modes** | What can go wrong, and what the design does about each. | ¼ page |
| **8. Test strategy** | Table mapping each acceptance criterion → unit / integration / end-to-end test. | ¼ page |

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
  <figcaption>Fig 1 — types, ownership, and dependency direction.</figcaption>
</figure>
<table>
  <tr><th>Type</th><th>Responsibility</th><th>Public API</th><th>Collaborators</th><th>Why (AC)</th><th>Principle</th></tr>
  <tr><td><code>OrderService</code> <em>(new)</em></td><td>One sentence.</td>
      <td class="sig">place(Order): Receipt<br>cancel(id): void</td>
      <td><code>OrderRepo</code>, <code>PricingPolicy</code></td>
      <td>AC1, AC3</td><td>SRP; Strategy for pricing</td></tr>
</table>

<h2>3. Key interactions</h2>
<figure><svg viewBox="0 0 640 220" role="img" aria-label="Sequence diagram"><!-- … --></svg>
  <figcaption>Fig 2 — happy path and the primary failure path.</figcaption></figure>

<h2>4. Data &amp; contracts</h2>
<table><tr><th>Shape</th><th>Fields</th><th>Compatibility / migration</th></tr></table>

<h2>5. Decisions &amp; trade-offs</h2>
<table><tr><th>Decision</th><th>Rejected alternative</th><th>Why</th></tr></table>

<h2>6. Risks, edge cases &amp; failure modes</h2>
<table><tr><th>Case</th><th>Handling</th></tr></table>

<h2>7. Test strategy</h2>
<table><tr><th>AC</th><th>Unit</th><th>Integration</th><th>End-to-end</th></tr></table>
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
Same shell, same caps, different body — the **executable projection of the design**, not a fresh
set of facts. It contains:

- **Build-order table** (the heart): one row per increment — `Order` · `Increment` ·
  `Design components` (from the design table) · `ACs` · `Depends on` · `Files` · `Tests`.
  Ordered by dependency — contracts/types → core → integration → end-to-end → docs — so every
  increment is built only after the ones it needs. Every design component appears in exactly one
  row; every AC in at least one.
- **Per-increment detail:** scope, the acceptance criteria it satisfies, and its
  session-sized justification.
- **Testing plan:** per increment, the unit / integration / end-to-end tests that prove it, the
  coverage expectation, and the regression scope it must not break; plus when full E2E
  verification runs and what the final regression pass covers.
- Task checkboxes per increment.

```html
<h2>1. Build order</h2>
<table>
  <tr><th>#</th><th>Increment</th><th>Design components</th><th>ACs</th><th>Depends on</th><th>Files</th><th>Tests</th></tr>
  <tr><td>1</td><td>Pricing contracts &amp; types</td><td><code>PricingPolicy</code>, <code>Receipt</code></td><td>AC1</td><td>—</td><td>src/pricing/*.ts</td><td>unit: policy math</td></tr>
  <tr><td>2</td><td>Order placement core</td><td><code>OrderService.place</code></td><td>AC1, AC3</td><td>1</td><td>src/order/*.ts</td><td>unit + integration (repo seam)</td></tr>
  <tr><td>3</td><td>Checkout wiring &amp; E2E</td><td><code>CheckoutController</code></td><td>AC2</td><td>2</td><td>src/http/*.ts</td><td>e2e: place → receipt</td></tr>
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
    <text x="95"  y="68" class="t">1 · Contracts</text>
    <line x1="170" y1="64" x2="240" y2="64" class="a" marker-end="url(#ar)"/>
    <rect x="240" y="40" width="150" height="48" rx="6" class="b"/>
    <text x="315" y="68" class="t">2 · Order core</text>
    <line x1="390" y1="64" x2="460" y2="64" class="a" marker-end="url(#ar)"/>
    <rect x="460" y="40" width="160" height="48" rx="6" class="b"/>
    <text x="540" y="68" class="t">3 · Checkout + E2E</text>
  </svg>
  <figcaption>Fig — increments in build order; an arrow means "needs the previous one first".</figcaption>
</figure>
```

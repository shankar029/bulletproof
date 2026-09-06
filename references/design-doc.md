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
- **Diagrams carry the structure; text only carries what a diagram can't.** At minimum: one
  class/module diagram and one sequence diagram for the critical flow.
- **Every existing symbol named in the document must be one you have read in the source.**
  Mark anything unverified with `class="unverified"` — never present a guess as an existing API.
- **No essays, no restating the requirement, no boilerplate.** Bullets, tables, signatures.

## Structure (in order, with page budget)

| Section | Content | Budget |
|---|---|---|
| **1. Problem & scope** | 3–5 bullets: what changes, which acceptance criteria (by id), what is explicitly out of scope. | ⅕ page |
| **2. Architecture** *(large work only, in `architecture.html`)* | One simple component diagram: the pieces, their responsibilities, and how they communicate. Omit entirely for contained changes. | ½ page |
| **3. Program design** | The class/module diagram, then a table: each new or changed type with its **single responsibility**, **public method signatures**, and **collaborators**. This is the heart of the document. | 1 page |
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
  <tr><th>Type</th><th>Responsibility</th><th>Public API</th><th>Collaborators</th></tr>
  <tr><td><code>OrderService</code> <em>(new)</em></td><td>One sentence.</td>
      <td class="sig">place(Order): Receipt<br>cancel(id): void</td>
      <td><code>OrderRepo</code>, <code>PricingPolicy</code></td></tr>
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

**Re-check the page count after every revision.** Folding review findings back into the
document is exactly when it creeps past three pages — measure by printing to PDF, then trim
content (merge table rows, delete what a signature already says). Never shrink the type.

## `plan.html`
Same shell, same caps, different body: the increment list (each with its scope, acceptance
criteria, and session-sized justification), the task checkboxes per increment, and the test
strategy table. No diagram is required unless increment dependencies genuinely need one.

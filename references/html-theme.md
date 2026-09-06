# Reference: The HTML Artifact Theme & Review Handoff

Every HTML artifact this skill produces (`design.html`, `architecture.html`, `plan.html`)
shares one theme and one review layer. **Write plain semantic HTML — never author styling.**

## Wiring a document

Copy the two asset files into `.ai/assets/` once per repository (they are shared by every
slug), then start each document with exactly this head:

```html
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design — <task></title>
<link rel="stylesheet" href="../assets/artifact.css">
<script src="../assets/artifact.js" defer
        data-doc="design.html" data-slug="<slug>"></script>
```

Then write the body as plain HTML: `<h1>`, `<div class="meta">`, `<h2>` sections, `<ul>`,
`<table>`, `<pre>`, and `<figure><svg>…</svg><figcaption>…</figcaption></figure>`.

**Rules:**
- **No `<style>` block, no inline `style=` attributes, no colours anywhere.** The theme owns
  all presentation, including light/dark. A hard-coded colour will be unreadable in one theme.
- Diagrams use only the theme's classes: `.b` / `.b-alt` (boxes), `.a` / `.a-dash` (arrows),
  `.t` (box title), `.s` (sub-label), `.l` (arrow label). They adapt to both themes.
- Mark unverified claims with `<span class="unverified">` and assumptions with
  `<p class="assumption">` so they stand out to the reader.

## What the reader gets

The layer is a reading app, not a form:
- **Adjustable reading:** text size (A− / A+), serif ⇄ sans, three column widths, and
  light / dark / auto theme. Preferences persist across all artifacts.
- **Highlight** any selection, or **comment** on it — a popup appears on selection, or use
  `Ctrl/Cmd+Shift+H` and `Ctrl/Cmd+Shift+C`. Comments are anchored to the quoted text and
  re-attach on reload; if the text has changed, the comment is flagged as unanchored rather
  than silently lost.
- **Notes** that aren't tied to any selection, for whole-document remarks.
- A **decision**: Approve · Approve with comments · Request changes, plus an overall note.
- **Print** (`Ctrl/Cmd+P`) drops the UI, forces light theme, and appends the comments as
  numbered endnotes — this is how the 3-page limit is checked.

## How the verdict returns — the handoff protocol

**Do not open the document with agent-browser for the user to read.** agent-browser drives the
*agent's* browser instance; the human reads in their own. Hand off like this:

1. **Self-check the artifact first** (this *is* an agent-browser job — see
   `e2e-agent-browser.md`): open the file, confirm it renders, `agent-browser errors` and
   `console` are clean, the diagrams are visible, and the printed length is within 3 pages.
   Never hand a broken document to a human.
2. **Open it in the user's default browser** with the platform opener — `start "" <path>` on
   Windows, `open <path>` on macOS, `xdg-open <path>` on Linux — and **also print the
   `file://` path** in the chat, because the opener may be unavailable (SSH, container, CI).
3. **Tell the user exactly what to do:** read it, highlight/comment anything, choose a
   decision, then either **Download `review.json` into `.ai/<slug>/`** or **Copy JSON and
   paste it back** — or simply reply in plain English.
4. **Then stop and return control.** End the turn. Do **not** poll, sleep, or loop waiting for
   a file to appear. Record in `state.md`: `Blocked on: <doc> sign-off — awaiting user review`
   and the next action. The work is durable, so the answer can arrive in a later session.
5. **On resume**, look for `.ai/<slug>/review.json` first, then the chat. Fold the result in:

| Verdict | What you do |
|---|---|
| `approve` | Pass the gate, record it in `state.md`, continue. |
| `approve-with-comments` | Apply every comment to the document (or record why not) before continuing. Pass the gate. |
| `changes-requested` | Revise the document, re-run the self-check, re-present. Do **not** advance. |
| unanchored comments | The quoted text changed since the review — resolve them explicitly with the user rather than guessing. |

Record each comment and its disposition in `.ai/<slug>/review.md`, and never silently drop one.

**When no user is available** (headless, CI, one-shot): do not block. Proceed on the recorded
assumptions per prime directive 7, and flag in the PR that the design was not signed off.

## `review.json`

```json
{
  "doc": "design.html",
  "slug": "checkout-discount-codes",
  "generated": "2026-02-17T12:00:00.000Z",
  "verdict": "approve-with-comments",
  "note": "Good shape overall — fix the retry story before building.",
  "items": [
    { "n": 1, "kind": "comment", "section": "3. Program design",
      "quote": "DiscountPolicy.apply(cart)", "body": "Should take the customer too.",
      "anchored": true },
    { "n": 2, "kind": "highlight", "section": "6. Decisions", "quote": "…", "body": "",
      "anchored": true },
    { "n": 3, "kind": "note", "section": "", "quote": "",
      "body": "Add a rollback note.", "anchored": true }
  ]
}
```

`verdict` is `pending` until the reader chooses one. Treat `pending` as "not reviewed", never
as approval.

## Maintaining the assets
`artifact.css` and `artifact.js` are copied verbatim from this skill's `assets/` directory.
Do not fork or hand-edit them per project; if a document needs something the theme lacks,
that's a signal the document is over-designed.

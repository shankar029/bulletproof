# Reference: The Final Report

Every run ends with one, written to `.ai/<slug>/report.html` and summarised in the chat. It is
the artifact a person opens to answer three questions: **what do I have, can I trust it, and
what is left?**

Use the shared theme exactly as the design document does (`html-theme.md`) — plain semantic
HTML, no styling in the file:

```html
<link rel="stylesheet" href="../assets/artifact.css">
<script src="../assets/artifact.js" defer data-doc="report.html" data-slug="<slug>"></script>
```

The review layer applies here too: the reader can highlight, comment and return a verdict on
the report itself.

## Rules

- **Report what is true, not what was hoped.** A gate that did not pass is `⛔` with the
  reason, never a ✅ with a caveat buried in prose.
- **Every number is regenerated at the final commit**, never copied from an earlier run.
- **Anything unproven gets the exact command to finish it.** "Not verified" without a next
  step is an unfinished report.
- **Write it even when the run is cut short.** A partial report that names the blocker is worth
  far more than none — if you are interrupted, this is the file that saves the work.
- Keep it to about two pages. It is a status document, not a narrative.

## Structure

| Section | Contents |
|---|---|
| **1. Outcome** | One paragraph: what now works that did not before, and the headline caveat if there is one. State the branch and whether a PR exists. |
| **2. Delivered / not delivered** | Two short lists. Anything asked for but not built belongs in the second one, with why. |
| **3. Acceptance criteria** | Table: AC · met? · **how it was proven** (which test, which transcript, which artifact). An AC with no proof is not met. |
| **4. Gates** | The G1–G6 row with `✅ / ⛔ / ⬜` and a reason for anything not green. This is the fastest read of run health. |
| **5. Measurements** | Tests (count, pass/fail), coverage, probe deltas vs the merge-base, mutation score with survivors, and everything reported `unavailable` — listed, not hidden. |
| **6. Scorecard** | The 9 rubric dimensions, each with a score and a one-line justification **citing a number** where one exists (`quality-bar.md`). Include the convergence iteration count. |
| **7. Pending & unproven** | What is environment-blocked, skipped or deferred — each with the command or decision needed to close it. |
| **8. Assumptions** | Every default taken without confirmation, especially an unapproved design, flagged for the reader to confirm. |
| **9. Follow-ups** | Work deliberately left out of scope, sized and justified. |
| **10. How to finish** | The literal next commands: push, open the PR, re-run a blocked check. |

## Skeleton

```html
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Report — <TASK></title>
<link rel="stylesheet" href="../assets/artifact.css">
<script src="../assets/artifact.js" defer data-doc="report.html" data-slug="<SLUG>"></script>

<h1><TASK> — Final report</h1>
<div class="meta">Branch: <BRANCH> · Commit: <SHA> · <DATE> · Design: design.html · Plan: plan.html</div>

<h2>1. Outcome</h2>
<p>…</p>

<h2>2. Delivered</h2>
<ul><li>…</li></ul>
<h3>Not delivered</h3>
<ul><li>… — why</li></ul>

<h2>3. Acceptance criteria</h2>
<table>
  <tr><th>AC</th><th>Met</th><th>Proven by</th></tr>
  <tr><td>AC1 …</td><td>✅</td><td>test/x.test.ts:12 · evidence/e2e.txt</td></tr>
</table>

<h2>4. Gates</h2>
<table>
  <tr><th>G1</th><th>G2</th><th>G3</th><th>G4</th><th>G5</th><th>G6</th></tr>
  <tr><td>✅</td><td>✅ signed off</td><td>✅</td><td>✅</td><td>⛔ daemon wedged</td><td>⬜</td></tr>
</table>

<h2>5. Measurements</h2>
<table>
  <tr><th>Measure</th><th>Base</th><th>Head</th><th>Status</th></tr>
  <tr><td>tests</td><td>36</td><td>59 pass / 0 fail</td><td>ok</td></tr>
  <tr><td>duplication %</td><td>0.0</td><td>0.0</td><td>ok</td></tr>
  <tr><td>mutation %</td><td>—</td><td>100 (10/10)</td><td>ok</td></tr>
</table>
<p class="assumption">Unavailable: static_findings, dead_exports (tools not installed).</p>

<h2>6. Scorecard</h2>
<table>
  <tr><th>Dimension</th><th>Score</th><th>Justification (cite a number)</th></tr>
</table>
<p>Convergence iterations: N</p>

<h2>7. Pending &amp; unproven</h2>
<table><tr><th>Item</th><th>Why</th><th>Command to finish</th></tr></table>

<h2>8. Assumptions still unconfirmed</h2>
<ul class="assumption"><li>…</li></ul>

<h2>9. Follow-ups</h2>
<ul><li>…</li></ul>

<h2>10. How to finish</h2>
<pre><code>git push -u origin &lt;branch&gt;
gh pr create --fill</code></pre>
```

## The chat summary

Mirror the report in a few lines: outcome, gate row, the headline numbers, what is pending, and
the path to `report.html`. Do not paste the whole report into the chat — link it.

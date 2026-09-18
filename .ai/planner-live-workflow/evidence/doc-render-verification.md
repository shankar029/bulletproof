# Bounded document verification — DR1

## Result

**The exact candidate `design.html` prints to 3 pages (limit: 3).**
`ux.html` also prints to 3 pages. Both documents load the shared theme and review
toolbar; light/dark computed colors change; design contains two rendered SVG
diagrams. All captured `agent-browser errors` arrays and `console` message arrays
are empty. No document or app source was edited by this verification.

This establishes the missing page-count/render execution evidence, not human
approval, app correctness, or an unconditional Gate 2b approval.

## Canonical evidence

Final run: `doc-render-2026-09-18T07-38-56-769Z\` (relative to this report).

- `report.json`: source/runner/assets SHA-256, browser identity, actual computed
  layout/style/diagram metrics, snapshots, clean-log assertions, PDF page-tree
  counts, and cleanup results.
- `commands.jsonl`: exact bounded Python-wrapper command arguments, exit codes,
  stdout and stderr for every agent-browser invocation.
- `design.pdf`, `ux.pdf`: original agent-browser PDF output.
- `design-light.png`, `design-dark.png`, `ux-light.png`, `ux-dark.png`: full-page
  desktop renders at 1280 × 960 viewport.
- `design-snapshot.json`, `ux-snapshot.json`: accessibility-tree snapshots.

Page count is structural, not estimated from source or screen height:
the script follows the PDF catalog's `/Pages` reference, recursively traverses
`/Kids`, checks `/Parent`, counts `/Type /Page` leaves and verifies every `/Count`.
Each PDF has three leaf pages, a declared root count of three, and
`/MediaBox [0 0 612 792]` (US Letter). Agent-browser's documented `pdf <path>`
command was used without custom print scaling or style changes.

Verified document SHA-256:

| Document | SHA-256 |
|---|---|
| design.html | `b352cb846bda5c1543637ec877302663d94ab7903bb55e4cbab559ab117d39b9` |
| ux.html | `ab798a43e4c324b8128ee2a992244eae2931ffce1b605af87f867bad5576b3d2` |

## Remaining visual observation

The added **read/write** label in the first design diagram is present, but its
right edge touches/overlaps the Store + C1 schema box's left border. The recorded
light-theme bounding rectangles intersect by approximately **4.93 × 14.22 CSS
pixels** at the tested desktop width. The full-page design screenshot shows this
crowding. The other three added structural labels do not intersect boxes.
This is a small DR2 readability follow-up, not a page-limit failure. Move the
label left if the owner chooses; this verifier is not authorized to edit design
source. Any candidate edit should be rerendered rather than treating these hashes
as evidence for the edited candidate.

No horizontal document overflow was measured at the tested 1280px viewport
(`scrollWidth == viewport == 1280`). No narrow-screen or app accessibility
certification is claimed. The screenshots verify document presentation, not the
proposed planner UI.

## Exact reproduction

From the repository root, in PowerShell:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' scripts\run.py --idle 45 --max 240 --label doc-render-verification -- 'C:\Program Files\nodejs\node.exe' .ai\planner-live-workflow\evidence\verify-docs.mjs
```

Final result: **exit 0**, `RENDER_CAPTURED`; both clean-log/theme assertions and
both structural page-count checks verified. The script creates a new timestamped
evidence directory on each invocation.

Help/discovery command:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' scripts\run.py --idle 40 --max 150 --label doc-render-help -- 'C:\Program Files\nodejs\node.exe' .ai\planner-live-workflow\evidence\verify-docs.mjs --help-only
```

Result: exit 0; installed agent-browser 0.37.1 README and general, PDF, screenshot,
and set-command help are retained in `doc-render-2026-09-18T07-34-50-077Z\`.
No packages were installed. Existing Python `pypdf`, `fitz`, and `PIL` were
unavailable; the generated-PDF structural parser required no added dependency.

The first render probe (`doc-render-2026-09-18T07-36-01-639Z`) failed solely because
file-origin CSSOM forbids reading `stylesheet.cssRules`. The verifier was changed
to inspect loaded stylesheet href/disabled state and actual computed styles.
Its browser/profile were cleaned. The corrected full run at
`doc-render-2026-09-18T07-36-22-898Z` and canonical final run both succeeded; the
final script additionally asserts the clean error/console arrays and exits
nonzero on a page-limit failure.

## Ownership and cleanup

The verifier reused the existing harness's cached CLI discovery and IPv4 CDP
pattern. Playwright was used only for fresh persistent-context launch and close.
All page navigation, evaluation, emulation, screenshots, snapshots, logs and PDF
printing used agent-browser; CLI subprocesses were bounded with `scripts\run.py`.
Documents were opened directly as file URLs, without an app server or fixtures.
Final cleanup confirms the owned CDP endpoint is unreachable and the owned
profile has been removed. Only this task's evidence directory was written.

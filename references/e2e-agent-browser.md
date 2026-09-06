# Reference: Browser & Front-End Verification with agent-browser

All browser-based end-to-end verification and all front-end testing in this workflow use
**agent-browser** — a native CLI for driving Chrome from an agent.
Repo: <https://github.com/vercel-labs/agent-browser>

**Ground yourself before you drive it.** Run `agent-browser skills get --all` (or read the
repo README) to get instructions that match the installed version, and `agent-browser --help`
/ `agent-browser <command> --help` for exact flags. Never invent a command or flag.

## Setup

```bash
npm install -g agent-browser   # or: brew install agent-browser | cargo install agent-browser
agent-browser install          # downloads Chrome for Testing (first run only)
agent-browser install --with-deps   # Linux: also install system libraries
```

Detects existing Chrome/Brave/Playwright/Puppeteer installs. The browser persists in a
background daemon, so successive commands reuse one session.

## Start the app without blocking yourself

A dev server never returns, so **never run it in the foreground** — it will consume the whole
run. Start it detached, log it, and poll once:

```bash
(nohup npx vite --port 5173 --strictPort > .tmp/dev.log 2>&1 &) ; sleep 4
curl -sI http://localhost:5173 | head -1        # expect HTTP/1.1 200 OK
```

Use a fixed port with a strict flag so you know what you are driving, and kill the server when
Phase 5 is done. If the port check fails, read the log — do not re-run the server.

## The core loop

Work from the **accessibility snapshot**, not from guessed selectors. The snapshot returns
`@eN` refs; act on those refs.

```bash
agent-browser open http://localhost:3000
agent-browser wait --load networkidle
agent-browser snapshot -i --json        # interactive elements + refs; parse this
agent-browser click @e2
agent-browser fill @e3 "user@example.com"
agent-browser get text @e1 --json       # assert on real rendered output
agent-browser screenshot ./artifacts/e2e/step-1.png
agent-browser close
```

Re-snapshot after any navigation or DOM change — refs are only valid for the snapshot that
produced them. CSS/text/XPath selectors and `find role button --name "Submit"` also work when
a ref isn't practical. Use `--json` everywhere you need to parse a result.

## Asserting like a user

| Goal | Command |
|---|---|
| Rendered text / value / attribute | `get text\|value\|attr <sel>` |
| Element state | `is visible\|enabled\|checked <sel>` |
| Element count | `get count <sel>` |
| Appearance / disappearance | `wait --text "Saved"`, `wait "#spinner" --state hidden` |
| Navigation | `wait --url "**/dashboard"`, `get url` |
| Arbitrary condition | `wait --fn "window.ready === true"` |
| **No client-side errors** | `agent-browser errors` (uncaught exceptions), `agent-browser console --json` |
| Network side effects | `network requests --method POST --status 2xx`, `network request <id>` |
| Accessibility regressions | `a11y --tags wcag2a,wcag2aa` (axe-core, offline) |
| React internals / perf | `open --enable react-devtools <url>`, then `react tree`, `react renders`, `vitals` |

**Always check `agent-browser errors` and `agent-browser console` before declaring a UI flow
green** — a flow can render correctly while throwing.

Isolate the front end from flaky back ends when the criterion is about UI behavior:
`network route <url> --body <json>` to mock, `--abort` to block. Never mock the thing the
acceptance criterion is actually about.

## Committing the flows

End-to-end flows are repository artifacts, not one-off console sessions. Persist each flow as
a re-runnable script — a shell script, or a JSON command list run with `batch`:

```bash
echo '[
  ["open","http://localhost:3000/checkout"],
  ["wait","--load","networkidle"],
  ["snapshot","-i"],
  ["fill","#code","SAVE10"],
  ["click","text=Apply"],
  ["wait","--text","10% off"],
  ["screenshot","./artifacts/e2e/checkout-discount.png"]
]' | agent-browser batch --json --bail
```

Use `--bail` so a failed step fails the run. Wire the script into the project's task runner
alongside the other test commands so CI and humans can re-run it.

## Evidence to capture

- `screenshot ./artifacts/…` per asserted state, or `screenshot --annotate` when the visual
  layout matters.
- `record start ./artifacts/e2e/flow.webm` … `record stop` for a full flow walkthrough, or
  `trace start` / `trace stop` for debugging artifacts.
- The `console` / `errors` output proving the flow ran clean.
- `a11y` results when the change touches UI.
- One pass/fail line per acceptance criterion, with the artifact path.

## Verifying a generated artifact (not for human reading)

agent-browser drives **the agent's** browser. Use it to self-check an HTML artifact before
handing it to a human — never to "show" the document to the user, who reads it in their own
browser (see `html-theme.md`).

```bash
agent-browser open "file:///<abs path>/.ai/<slug>/design.html"
agent-browser wait --load networkidle
agent-browser errors                 # must be empty
agent-browser console                # must be clean
agent-browser get count "figure svg" # diagrams actually rendered
agent-browser screenshot ./.ai/<slug>/evidence/design-preview.png
agent-browser close
```

A document that throws, renders no diagrams, or shows unstyled content is not ready to hand
over — fix it first.

## Practical notes

- **Verify the command exists before relying on it.** This CLI moves fast and builds differ:
  run `agent-browser --help` / `agent-browser <cmd> --help` first. An unrecognised command may
  return an error payload that is easy to misread as a clean result — if a check reports zero
  problems, confirm it actually ran.
- Refs from `snapshot` are only valid for that snapshot: **re-snapshot after any DOM change**,
  and never reuse a ref across an interaction that re-renders the page.
- Viewport changes go through `agent-browser set viewport <w> <h>`.

- Chain with `&&` when you don't need intermediate output; use `batch` to avoid per-command
  startup; run separately when you must parse a snapshot before acting.
- A click fails fast if something covers the target (banner, modal) — dismiss the reported
  covering element, re-snapshot, retry.
- Authenticated flows: `state save` / `state load`, or import cookies, rather than scripting
  a login before every scenario.
- Set up cookies, routes, and init scripts by launching with bare `open`, staging, then
  navigating.

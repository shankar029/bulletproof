# Download attempts: observed failure, cause unproven

Parent extraction from recorded command logs, not another trial. **AC4 remains BLOCKED.**
No successful browser-saved CSV file exists in the captured evidence. Automation/transport
failure was observed; an environment-only cause and Windows path-canonicalization theory
are NOT proven. No production workaround was applied.

## Shared execution and browser attachment

Pinned agent-browser **0.37.1**:
`C:\Users\shbs\AppData\Local\npm-cache\_npx\6de2aa2fded2970c\node_modules\agent-browser\bin\agent-browser-win32-x64.exe`.

Working directory was this worktree's `examples\team-planner`. Each CLI invocation used
the supplied Python 3.14.2 and this worktree's `scripts\run.py --idle 25 --max 30 --`,
except initial browser `open` used max60. Exact full wrapper argv/stdout/stderr are in each
run's `commands.jsonl`. In the commands below `$cli` is the executable above; `$app` is
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-stunning-funicular\examples\team-planner`.
Variables abbreviate exact recorded prefixes, not alternative invocations.

Owned headless Chromium launched by Playwright `chromium.launchServer`, channel chromium,
with `--remote-debugging-port=<owned port>` on loopback. **No Playwright page/context client
attached.** Agent-browser was the only browser interaction client, attaching via explicit
IPv4 HTTP CDP (`--cdp http://127.0.0.1:<port>`), not its own newly launched browser.
Launch `downloadsPath` and each CLI's `AGENT_BROWSER_DOWNLOAD_PATH` selected the run-local
`$app\.work\<run>\downloads`. Explicit `download` calls additionally supplied the file path.

## Active UI and direct-HTTP control

Run `e2e-2026-09-18T08-33-33-762Z-b1570d0c`, raw log:
`e2e-2026-09-18T08-33-33-762Z-b1570d0c\commands.jsonl`.
Page `http://127.0.0.1:61886/?projectId=p-2`.

```powershell
$run = 'e2e-2026-09-18T08-33-33-762Z-b1570d0c'
# Recorded command 32:
& $cli --session $run --cdp http://127.0.0.1:61043 --json download '#download-csv' "$app\.work\$run\archive-active.csv"
# Recorded command 34:
& $cli --session $run --cdp http://127.0.0.1:61043 --json download '#download-control' "$app\.work\$run\diagnostic-direct-http.csv"
```

The UI button fetches **GET `/api/projects/p-2/tasks.csv`**, then clicks its temporary blob
download anchor. Diagnostic command33 created `#download-control` with that same API URL
directly, bypassing the UI's fetch/blob path. Both download commands exited **1**:
`{"success":false,"data":null,"error":"Download was canceled"}`. No saved file was found.
The later archived/stale/empty download scenarios in this retained run were marked blocked
after the first failure, not separate successful or canceled downloads.

## Legacy UI and direct-HTTP control

Run `e2e-2026-09-18T08-29-15-530Z-7e5f273a`, commands11/13, page
`http://127.0.0.1:52072/?projectId=p-1`; API route `/api/projects/p-1/tasks.csv`.

```powershell
$run = 'e2e-2026-09-18T08-29-15-530Z-7e5f273a'
& $cli --session $run --cdp http://127.0.0.1:59862 --json download '#download-csv' "$app\.work\$run\migration-legacy.csv"
& $cli --session $run --cdp http://127.0.0.1:59862 --json download '#download-control' "$app\.work\$run\diagnostic-direct-http.csv"
```

Both exited **1**, with the same exact `Download was canceled` JSON. No saved file.

## Single alternative: configured destination plus ordinary click

Run `e2e-2026-09-18T08-44-16-260Z-61878553`. At first attachment, command2:

```powershell
$run = 'e2e-2026-09-18T08-44-16-260Z-61878553'
& $cli --session $run --cdp http://127.0.0.1:63961 --download-path "$app\.work\$run\downloads" --json open http://127.0.0.1:53725
# Later, on the real legacy page http://127.0.0.1:64660/?projectId=p-1, command367:
& $cli --session $run --cdp http://127.0.0.1:63961 --json click '#download-csv'
```

The explicit ordinary destination was also supplied through `AGENT_BROWSER_DOWNLOAD_PATH`
on every CLI child. Open and click exited **0** with success JSON. The real UI again used
GET `/api/projects/p-1/tasks.csv` then its blob anchor. **No directory entry appeared within
12 seconds**; independent filesystem assertion failed:
`No completed browser-saved CSV within 12000ms; observed []`.
No CLI `download`/`wait --download` was used in this experiment. All four subsequent archive
download scenarios were explicitly blocked without further positive-download attempts.
The experimental helper was restored, not retained as a fix.

## File/event distinction and negative case

**File:** none of the positive attempts above yielded an actual saved CSV. HTTP body/native
parser results are separate evidence, not downloads. **Event:** the CLI reported cancellation;
no raw CDP download-event trace was retained, and no completed-download event was independently
observed. Its cancellation response is not proof of a specific environment-only root cause.
Click success and the UI success notice are not proof of a saved file or completed event.

For the intentionally aborted HTTP export, retained archive commands158/161 clicked the
button, then invoked:

```powershell
$run = 'e2e-2026-09-18T08-33-33-762Z-b1570d0c'
& $cli --session $run --cdp http://127.0.0.1:61043 --json wait --download "$app\.work\$run\failed-download.csv" --timeout 1500
```

The wait exited1, error `Operation timed out. The page may still be loading or the element
may not exist.` This supports only a failed wait, **not absence of a browser event**, especially
without a working positive control. The alternative experiment separately observed no new file
for 1.5s, a focused UI error and no success notice.

Full results remain in verification.md, download-remedy-summary.json and local raw reports.
No new trial was run to create this extraction; future verification needs a genuinely saved
active/archive file and byte/row assertions before AC4 can close.

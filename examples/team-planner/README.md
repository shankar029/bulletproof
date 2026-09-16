# Team planner

A local single-user planner, independent of the repository's evaluation corpus.
Native Node.js 24+, no production dependencies or build step.

From `examples\team-planner`:

```powershell
node src\main.mjs --data-dir data --port 4317
node scripts\check.mjs unit
node scripts\check.mjs integration
node scripts\check.mjs all
node scripts\check.mjs coverage
```

Open `http://127.0.0.1:4317`. Port `0` chooses an available port and logs the actual
address. An occupied fixed port fails; the app never silently changes ports.
The server checks its own health after listening. Ctrl+C gracefully closes it.

Create projects, create tasks, and edit title/description, status and dependencies. Saves persist before success.
Every API read and write returns a global revision and quoted ETag. POST/PATCH require
that ETag in `If-Match`; stale writes receive `409 REVISION_CONFLICT`. Reload explicitly
discards a draft; failed saves retain it. Never automatically replay an uncertain write.

New stores use v2 (`status`, `priority`). Legacy v1 (`state`) remains readable, but
every write, including a no-op, requires offline migration. No legacy encoder remains.
Limits: 100 projects, 2,000 tasks, 80-code-point project names,
160-code-point task titles, 2,000-code-point descriptions, 64 KiB request bodies.

Tasks move todo → in progress → done, or directly todo → done, only when every direct
dependency is done. Reopen to todo only after reopening any active/done dependents.
Done → in progress is rejected. "Blocked" means todo with an unfinished dependency,
not a fourth status. Dependencies must be distinct tasks in the same project and acyclic.
Status and dependencies in one PATCH are validated together; failed changes publish nothing.

## Queries and dashboard

`GET /api/tasks` accepts `projectId`, `status`, `q` (case-insensitive title substring),
`priority`, `page` and `pageSize` (1–50, default 10). Filters combine with AND before
ascending creation order, total counting and slicing. Empty results have zero total pages;
an out-of-range page returns no items without clamping. Unknown/duplicate keys are errors.
Priority other than normal requires v2 migration.
Tasks default to normal priority; create/edit accept low, normal or high.

`GET /api/dashboard?projectId=p-1` summarizes the whole project, not visible search/page
results. Omit projectId for global totals. Blocked is a subset of todo. Completion is the
integer floor of 100 × done / total, or zero for empty projects.
Browser filters and page are URL state; Back restores them. Apply filters resets page 1.

## Offline migration

Stop the server, then run from the example directory:

```powershell
node src\migrate.mjs --data-dir data
node src\main.mjs --data-dir data --port 4317
```

Migration acquires the same writer lock, validates v1, exclusive-creates an exact-byte
`planner.v1-backup.json`, converts state → status and adds normal priority, and atomically
replaces the snapshot. IDs, order, text, dependencies and nextId are preserved; revision
increases once. An existing matching backup permits recovery from a precommit failure;
a different backup fails `BACKUP_MISMATCH` without overwriting either file. Repeating on v2
is a no-op. Never run an old v1 binary against v2.

Rollback is an explicitly lossy, offline operation for isolated exercise data only:
stop every owner; archive the current v2 snapshot if its new work matters; verify the
backup; write/sync/close a same-directory staged copy and rename it over planner.json.
This restores old v1 data and **loses all subsequent v2 writes**. Never auto-downgrade.
The migration tests demonstrate this loss and preserve an archive; fix forward on real data.

## Storage safety

One process holds `writer.lock` per data directory. Writes serialize, clone committed
state, validate, write and sync an exclusive same-directory stage, then rename before
publishing memory. No truncate-and-rewrite. Reads return copies. This protects against
process crashes, not arbitrary power loss/network filesystem behavior. On Windows,
another program holding `planner.json` open can cause a safe failed save.

Never delete someone else's lock. After a crash, inspect its PID and **prove that process
has stopped** before manually removing the lock in your owned data directory. Leftover
`.planner-*.stage` files are never promoted; remove them only while the server is stopped.
Corrupt/unknown data fails startup and is never initialized over.

## Verification boundaries

Native tests exercise real files and HTTP with isolated `.work` directories and bounded
owned cleanup. Coverage reports application source only. There is no framework lint/build
configuration and no claim that native coverage replaces the workflow's Python probe.

From the example directory, replay the isolated diagnosis and sampled mutation checks:

```powershell
node scripts\diagnose.mjs
node scripts\mutation.mjs
```

Diagnosis copies the app, injects a known pagination-before-filtering defect only into
that copy, observes one-factor reductions and HTTP-versus-domain probes, then restores
the exact source and repeats the original/minimized regressions. It is a controlled
experiment, not discovery of an unknown production bug. Mutation uses the repository's
existing textual engine on a bounded backend ESM sample; it is not exhaustive or browser
mutation coverage. Both commands retain results in unique ignored `.work` directories.

The [case-study report](../../.ai/workflow-app-verification/report.html) and
[29-feature ledger](../../.ai/workflow-app-verification/traceability.json) distinguish
working app behavior from workflow branches not exercised and historical sequencing
deviations. One application is not a causal evaluation of prompt effectiveness.

## Independent browser replay

From the repository root, install browser **test tooling**, not app dependencies:

```powershell
npm install --prefix benchmark
node benchmark\node_modules\playwright\cli.js install chromium
npm exec --yes --package=agent-browser@0.37.1 -- agent-browser --version
```

Then from `examples\team-planner`:

```powershell
node scripts\e2e.mjs --flow base
node scripts\e2e.mjs --flow graph
node scripts\e2e.mjs --flow query
node scripts\e2e.mjs --flow migration
npm run test:e2e
```

The runner discovers the pinned CLI in the npm cache. For another installation,
set `AGENT_BROWSER_BIN` to its native executable (the adjacent package must be
version 0.37.1). It uses benchmark Playwright **only to launch and close** an
owned headless Chromium context. All browser actions, DOM assertions, screenshots
and axe audits use agent-browser over an explicit `http://127.0.0.1:<port>` CDP
connection. No external app server or existing browser session is accepted.

Every invocation creates a unique ignored `.work\e2e-*` directory. Each flow has
its own real app process, port 0 and fresh data; restarts use that same flow's data
in a different process. The migration flow starts with the captured v1 fixture.
The Windows test-only IPC bridge exercises the CLI's installed graceful signal
handler; it does not claim native Ctrl+C key delivery. Cleanup closes only owned
PIDs/browser session and removes only the owned browser profile. Data, HTTP and
command transcripts, source hashes, screenshots, snapshots, axe findings and
`report.json` remain in that run directory, including on failure.

The journeys cover create/edit/refresh/restart, dependency rejection/reopen,
filtered pagination/Back/deep links/dashboard, migration/priority/restart,
conflicts, invalid input, safe script-like text, network recovery, keyboard
navigation and 390/1280px layout targets. Native unit tests are not UI proof.
Review the report's findings as well as its flow results: axe is not full WCAG
certification or human design approval, and incomplete checks remain explicit.

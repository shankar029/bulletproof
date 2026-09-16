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

Initial disk format is v1 (`state`); API uses `status`. Migration will be added in the
evolution slice. Limits: 100 projects, 2,000 tasks, 80-code-point project names,
160-code-point task titles, 2,000-code-point descriptions, 64 KiB request bodies.

Tasks move todo → in progress → done, or directly todo → done, only when every direct
dependency is done. Reopen to todo only after reopening any active/done dependents.
Done → in progress is rejected. "Blocked" means todo with an unfinished dependency,
not a fourth status. Dependencies must be distinct tasks in the same project and acyclic.
Status and dependencies in one PATCH are validated together; failed changes publish nothing.

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
`test:e2e` reserves the independently owned `scripts\e2e.mjs` entry point; the browser
verifier authors and runs it after implementation. Browser verification is not yet claimed.

# Planner archive/restore and CSV: Phase 1 research

## Snapshot & scope

- **FACT — assignment:** Fresh-context, read-only research for AC1–AC5 below. Only this report may be written. No design, implementation, runtime changes, dependency installation, push, PR, or tests that create files.
- **FACT — observed snapshot, 2026-09-18:** repository/worktree `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-stunning-funicular`; branch `shbs-microsoft-live-planner-workflow`; HEAD `c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`, matching the requested baseline. Initial `git --no-optional-locks --no-pager status --short` was empty. `git branch -av` distinguishes this worktree from main and the other checked-out branch. Remote: `https://github.com/shankar029/bulletproof.git`. Evidence: wrapped environment/git inspection, all commands exited 0; no fetch performed.
- **FACT — environment:** observed Windows `10.0.26100.0`, Python `3.14.2` at the supplied uv interpreter, Node `v24.11.1` at `C:\Program Files\nodejs\node.exe`. The supplied git directory was prepended to PATH. `npm.cmd` exists beside Node; app inventory contains no dependency lockfile. Root `package.json`, `package-lock.json`, `pnpm-lock.yaml`, and `yarn.lock` do not exist. Evidence: wrapped version/path inventory.
- **FACT — source citation convention:** `P` below means the exact repository-relative directory `examples\team-planner`. Citations refer to baseline file contents read in this worktree, not remote permalinks. Nothing in `P` was edited.
- **FACT — authoritative parent artifacts:** `[state.md](state.md)`, `[clarifications.md](clarifications.md)`, and `[traceability.md](traceability.md)` were absent at inspection. These are intended sibling links, **not presently accessible authorities**. Parent owns their creation and the complete Gate 1 decision; this assignment does not authorize creating them (`references\research.md:17–26,30–41`; `SKILL.md:153–183`).
- **FACT — exclusions:** evaluation/C4/session-private contents, `.ai\workflow-reliability`, and prior planner case-study contents were not read. An initial overly broad filename inventory exposed excluded filenames, not their contents; all subsequent inventories/searches were explicitly scoped. README links to prior case-study artifacts were not followed.
- **INFERENCE — tier:** non-trivial/user-visible change, because persistence contracts, HTTP writes, UI navigation, and export behavior intersect; full workflow belongs to parent, not this research assignment (`SKILL.md:43–57`; evidence below).

## Summary

**FACT:** The app is native Node HTTP + browser ES modules, with strict versioned JSON storage, serialized revision-checked writes, dependency validation, URL-driven task filters, and native/browser regression harnesses. Projects currently have only ID/name/creation order. Project lifecycle commands, archive-aware reads, and CSV download are not implemented in the inspected app surfaces. **INFERENCE:** the important seams are strict project schema compatibility, transaction-time authorization, list-versus-detail selection, coherent multi-request UI loads, and exporting all rather than paginated tasks. **FACT:** research is complete for the assigned code scope; one memory-only schema/query probe passed. File-writing suites/browser journeys were not run. Browser prerequisite availability is incomplete; no missing dependency was installed.

## Requirement coverage

The AC wording is **FACT — requested behavior**, from the delegation, not a claim about today's implementation.

| AC | Requested outcome | Current evidence / contracts / reuse | Existing proof and uncovered cases | Research status |
|---|---|---|---|---|
| AC1 | Archive and restore regardless of task status; preserve every project/task/dependency datum durably across restart. | **FACT:** project shape has no lifecycle field; only project create exists. Atomic store and existing migration preserve whole model. E1, E3, E5. | **FACT:** store restart, crash checkpoints, graph restart, migration preservation tests exist (T1, T2, T4, T7). No project archive/restore assertions found (S1). **INFERENCE:** mixed statuses, blocked tasks, empty projects, repeat operations, and archive/restore restart preservation remain new proof obligations. | Complete current-state research; feature absent in scope. |
| AC2 | Default active-project list excludes archived; explicit archive list and direct links remain readable. | **FACT:** `listProjects()` returns all projects, accepts no filter; UI resolves selected project from that same list. Task reads independently validate project existence. E1, E2, E4. | **FACT:** query/Back/deep-link tests cover today's projects (T5, T7), not archive views. **INFERENCE:** list exclusion alone would make selected archived project unavailable to `render()` despite readable task APIs. | Complete; list/detail coupling identified. |
| AC3 | Server and UI block every task create/edit/status write while archived; restore reenables; concurrency/dependencies unchanged. | **FACT:** create/update are the only task mutation entry points; project existence is checked on create, no lifecycle guard exists. Store checks legacy/revision before callback; callbacks validate final graph. UI disables only for legacy or an in-flight form save. E1, E3, E4, E6. | **FACT:** revision conflicts, atomic errors, no-op, combined status/dependency patches, stale UI draft, and graph invariants tested (T1–T4, T7). No archived guard tests (S1). **INFERENCE:** fresh and stale writers, all mutable fields, no-op writes, draft already open when another client archives, and restore race need explicit proof. | Complete; server/UI boundaries mapped. |
| AC4 | Deterministic UTF-8 CSV of all project tasks, IDs and visible data, commas/quotes/Unicode/multiline, formula neutralization; usable active/archived download. | **FACT:** no CSV route/helper/download consumer found. `taskView` has IDs, text, status, priority, dependencies, creation order, derived blocked; UI exposes name/title/status/priority/description and dependency choices. Query default is only 10 rows, max 50. E1, E2, E4, E6; S1. | **FACT:** Unicode storage, sorted task queries, and text-safe DOM tests exist, not CSV assertions (T1, T5, T7). Memory-only probe preserves CSV-sensitive text through JSON, **not** CSV. **INFERENCE:** all rows beyond page 1, stable order despite reordered storage, repeated bytes, independent parsing, header-only empty export, response/download metadata, special characters and dangerous leading formula text remain unproved. | Complete current-state research; CSV contract details remain Phase 2 decisions. |
| AC5 | Preserve filters/pagination/accessibility/durable storage; retain old formats or demonstrate safe migration/recovery. | **FACT:** strict v1-read-only/v2-write formats; no-op legacy writes fail; explicit backup-preserving offline migration. Filters are AND before sort/count/slice. UI focus/live announcements and owned browser journeys exist. E2–E6. | **FACT:** genuine v1 fixture, recovery/rollback, pagination, bounds, URL state, keyboard/layout/axe assertions are present (T1–T7). **INFERENCE:** archived variants must preserve these contracts; no existing test proves compatibility of a future project field. | Complete; old-format and recovery seams identified. |

## Instructions, profile, and conventions

- **FACT — binding workflow:** canonical root `SKILL.md:60–105` requires observed/cited/typed claims and explicit unknowns; `SKILL.md:109–134` requires idle/max command bounds and bounded recovery; `SKILL.md:153–183` requires fresh-context research and parent acceptance. Read `references\project-profile.md` in full and `references\research.md` in full. Research boundaries explicitly forbid implementation/design/installation and recursive delegation (`references\research.md:28–45`).
- **FACT — scoped instruction absence:** exact checks at root, `examples`, and `P` found no `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or `.github\copilot-instructions.md`; app-descendant checks found no `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or `*.instructions.md`. Root `.github\instructions` and `.cursor\rules` enumeration returned no files. Exact `.ai` and assigned-task `AGENTS.md`/`CLAUDE.md` checks were also absent. These are scoped filesystem observations, not a claim that the repository has no other guidance.
- **FACT — app guidance/profile:** `P\README.md:1–36,72–88` specifies single-user/local Node 24+, no production dependencies/build, persistence-before-success, explicit reload after uncertain writes, process-crash rather than arbitrary power-loss guarantees, no foreign lock deletion, and native test scope. `P\package.json:1–13` is private ESM, `node >=24`, with start/test/coverage/e2e/migrate scripts and no dependencies.
- **FACT — conventions:** ESM named exports, short domain methods, `AppError` with stable code/status/optional field, strict unknown-field rejection, native `node:test` + `node:assert/strict`, fixtures owning their storage/cleanup, and text-safe DOM creation are observed patterns, not additional binding style rules (`P\src\errors.mjs:1–13`; `P\src\schema.mjs:6–25`; `P\test\helpers.mjs:1–36`; `P\public\app.mjs:6–32`).
- **FACT — domain terms:** statuses are `todo`, `in_progress`, `done`; priority is `low`, `normal`, `high`; blocked is derived from a todo task's unfinished dependency, not a status (`P\src\rules.mjs:3–4,41–43`). IDs share a global allocation counter (`p-N` / `t-N`), and `createdOrder` is the allocation number, not a timestamp (`P\src\planner.mjs:16–20`; `P\src\schema.mjs:39–55`).

## Code map & behavior traces

### E1 — Domain entry points and persisted data contracts

**FACT — implementation:** `P\src\planner.mjs:4–14` exports `findTask(model, id)` / `findProject(model, id)` with `NOT_FOUND` 404. `Planner` exposes:

| Verified signature and source | Current contract |
|---|---|
| `constructor(store)`, `health()` (`:22–27`) | **FACT:** store dependency; health returns `{status:'ok', schemaVersion, revision}`. |
| `listProjects()` (`:28–31`) | **FACT:** `return { items: projects, revision }`; no sort/filter/lifecycle/detail operation. |
| `listTasks(query)`, `dashboard(projectId)` (`:32–33`) | **FACT:** clone committed store via `read()`, then delegate to `selectTasks` / `summarize`. |
| `async createProject(input, revision)` (`:34–45`) | **FACT:** accepts only required `name`; trims/max 80 code points, rejects case-insensitive duplicates; cap 100; shared ID allocation; result `{project, revision}`. |
| `async createTask(input, revision)` (`:46–61`) | **FACT:** required projectId/title; optional description/dependencyIds/priority; projectId must be string and exist; title trim/max160, description untrimmed/max2000, priority default normal, status always todo, dependencies default `[]`, cap2000; final graph validation; result `{task, revision}`. |
| `async updateTask(id, input, revision)` (`:62–79`) | **FACT:** nonempty object with only title/description/status/dependencyIds/priority; find task; apply provided fields, validate dependencies, transition and entire graph; result `{task, revision}`. Project reassignment and ID edits rejected. |

**FACT — schema:** `P\src\schema.mjs:28–64` defines `emptyModel()` and `validate(model)`. Envelope is exactly `{schemaVersion, revision, nextId, projects, tasks}`; revision and allocation bounds are safe integers. Project record is exactly `{id, name, createdOrder}` (`:47`, snippet `object(project, ['id', 'name', 'createdOrder'], ...)`). Modern task record requires exactly `{id, projectId, title, description, status, dependencyIds, createdOrder, priority}`. Unknown and missing fields fail; projects must exist, allocation numbers are unique across both record kinds, names are unique ignoring case, and stored graph invariants are validated.

**INFERENCE — AC1/AC5 seam:** simply adding an archive property to today's disk data fails startup validation; simply requiring a new property would exclude unchanged older snapshots. This is a compatibility boundary, not a proposed schema design. The memory-only probe directly confirmed `archived` is currently rejected.

### E2 — HTTP entry, read contracts, and failure propagation

**FACT:** `P\src\main.mjs:22–48` exports `async start(config)`: open `JsonStore`, create `Planner`, pass it to `createServer`, bind IPv4 loopback, close store if listen fails, expose `{url, server, store, close()}`. CLI `options(args, allowPort = true)` accepts `--data-dir`, optionally `--port` (default4317; zero allowed); duplicate/invalid options reject (`:6–20`). Actual CLI logs address, health-checks itself, installs graceful SIGINT/SIGTERM handling (`:51–64`).

**FACT:** `P\src\server.mjs:54–100`, `createServer({ planner, onError = error => console.error(error) })`, is the sole app HTTP registration:

- `/`, `/app.mjs`, `/styles.css`, `/api/health`, `/api/dashboard`: GET.
- `/api/projects`, `/api/tasks`: GET/POST.
- `/api/tasks/(t-[1-9][0-9]*)`: PATCH only.
- Unknown route 404; unsupported method 405 with `Allow`; Host/Origin must match localhost/127.0.0.1 and actual port (403 otherwise).
- `parseQuery(params, allowed = [])` (`:45–52`) rejects unknown/duplicate keys. Project-list GET allows no query. Root document allows view/projectId/status/priority/q/page/pageSize; task GET allows all those except view; dashboard allows only projectId (`:71–84`).
- Writes check `expectedRevision(req)` then `body(req)` before invoking domain commands (`:87–91`). Missing If-Match428, malformed quoted nonnegative safe integer400; JSON media type required415; body max64KiB413; malformed JSON400 (`:27–43`).
- `json(res, status, body, headers = {})` uses JSON UTF-8, no-store, and quoted ETag only when `body.revision` is a safe integer. `send(res, status, body, headers = {})` applies nosniff/CSP; it is currently used for static asset bytes or JSON, not downloads (`:5–25`).
- `AppError` becomes its public status/code/message/field; unexpected errors call `onError` and return generic500 without stack/path (`:92–97`; `P\src\errors.mjs:1–13`).

**INFERENCE — trace:** an attempted `/api/projects/p-1` or CSV route currently terminates at route404, not domain validation. There is no existing project-detail HTTP operation to reuse unchanged. A new query key would currently fail both API/root allowlists where relevant. These are static path conclusions, not executed HTTP reproductions.

### E3 — Transaction, storage, failure, and concurrency trace

**FACT:** `P\src\store.mjs:10–55` defines `JsonStore`, `constructor(directory, commitFile)`, `static async open({directory, commitFile, createIfMissing = true})`, `read()`. It exclusively creates `writer.lock` with token/PID and syncs it. Existing `planner.json` is read UTF-8 and decoded; only missing files initialize an empty v2 store. Other read/decode failures close owned lock, fail startup, and do not replace snapshot.

**FACT:** `transact(expectedRevision, change)` (`:73–95`) queues operations on `#queue`; rejects closed store503; inside queue rejects schema1 migration409 **before** stale revision409. It clones committed model; callback must be synchronous. Identical candidate returns unchanged revision without persistence. Changed candidates cannot alter schema/revision themselves; safe-counter exhaustion409; increments revision, validates/encodes, persists, then publishes memory. Snippet: `await this.#persist(bytes); this.#model = next;`. Rejected operation is still rejected to caller while queue scheduling recovers.

**FACT:** `async #persist(bytes)` (`:57–71`) creates a unique exclusive same-directory `.stage`, writes/syncs/closes, then calls injected/default rename. On failure it closes/removes owned stage and throws `STORAGE_UNAVAILABLE`503. Prior in-memory state is not published. `async close()` (`:131–142`) rejects subsequent callers, drains queued work, and removes only matching-token lock.

**INFERENCE — AC3 race boundary:** HTTP preflight or UI state alone cannot enforce archive against a queued competing write; transaction callback is where existing rules see the authoritative post-queue state. Existing stale-revision versus migration error precedence and no-op semantics are observable contracts to retain/test, not proof of future archived precedence.

**FACT — limits:** README explicitly does not claim directory-fsync/power-loss/network-filesystem safety and warns Windows open-file rename may fail safely (`P\README.md:72–84`). Leftover stages are not loaded/promoted (`store.mjs:37–43`).

### E4 — Browser state, read flow, write flow, and accessibility

**FACT:** `P\public\app.mjs:1–4` keeps projects, all selected-project tasks, revision, projectId, busy, query result, summary, schemaVersion; `route()` reads URLSearchParams. `element(tag, text, attributes = {})` uses `textContent`; `field(...)` and `select(...)` associate labels (`:6–32`).

**FACT — load/deep-link trace:** `async reload()` (`:208–247`) fetches project list, filtered task page, project/global dashboard, and health, then fetches **all** selected-project tasks in pageSize50 batches for dependency editing. Every batch and companion response must share task revision; otherwise explicit reload error, not silent merge. `loadSequence` prevents older completed load from overwriting newer load. `render()` (`:132–199`) finds selected project **in `state.projects`** (`:149`), otherwise renders Choose a project. Project links call `navigate(changes)` preserving other URL filters while resetting page (`:122–141`). Filter apply resets page, Back calls reload, page-size changes reset page, dashboard clears task filters (`:162–197,248–256`).

**FACT — mutation trace:** `edit(task)` (`:88–121`) builds title/description/status/priority/dependency form; choices use all selected-project tasks except self. Submit calls `save(form, path, method, input, success)` (`:64–87`), which disables form controls while busy, uses `request(path, method = 'GET', input)` (`:41–63`) with current global If-Match and 10s timeout, reloads on success; failure retains draft and focuses error. Finally reenables captured form controls. No automatic mutation replay. Add/Edit are currently disabled only for legacy schema1 (`:146–148,175–186`), not project state. **INFERENCE:** any archive-sensitive disable behavior has to coexist with saved-draft failure/re-enable and stale concurrent editor paths; current code proves neither.

**FACT — visible data/a11y:** project name heading; task title/status-or-blocked badge/priority/description; dependency choices in editor (`:88–104,160–186`); summary counts (`:200–207`). `P\public\index.html:11–25` supplies named nav/aside, polite live status, focused alert, labeled project input, aria-busy main. `P\public\styles.css:7–16,17–30` supplies 44px primary controls, focus outline, wrapping/layout and mobile breakpoint. Native form/button semantics, explicit editor-title focus/cancel return-focus, named Pagination landmark and notices are existing preservation targets, not full accessibility certification.

### E5 — Format compatibility and recovery

**FACT:** `decode(bytes)` / `encode(model)` / `upgradeV1(bytes)` are at `P\src\schema.mjs:66–93`. Legacy v1 task disk spelling `state` becomes in-memory `status` plus priority normal; envelope remains version1. Mixed field spellings, unknown versions, invalid graph/counters reject. `encode` writes only validated v2, indented JSON plus terminal newline. `upgradeV1` keeps records/IDs/text/dependencies/allocation and increments revision once; already-v2 returns model unchanged.

**FACT:** `JsonStore.migrateToV2()` (`P\src\store.mjs:97–129`) queues under same lock; v2 returns `{schemaVersion:2, revision, changed:false}`. v1 reads exact original bytes, exclusive-creates/syncs `planner.v1-backup.json`; preexisting byte-equal backup allows retry, differing backup gives `BACKUP_MISMATCH`409 without overwrite. Atomic persist precedes memory publication. `P\src\migrate.mjs:4–14` opens with `createIfMissing:false`, invokes migration, prints result or failure, always closes.

**FACT:** `P\test\fixtures\planner-v1.json:1–84` is genuine fixture v1/revision11/nextId10, two projects/seven tasks with mixed statuses and dependency t-7→t-4; `.expected.json:1–22` supplies hand-reviewed decoded expectations/counts. Observed SHA256: `ad7845486864bb4fef3f938eac02ef4ba213f8d3e20da4e4fa1b1c8b61df4450`. **FACT:** README offline rollback intentionally loses post-migration work and is not automatic downgrade (`P\README.md:50–70`). “Archive” in this rollback documentation means snapshot backup, **not project archival**.

### E6 — Query/dependency rules and export-relevant boundaries

**FACT:** `P\src\rules.mjs:6–43` exports `validateDependencies(model, taskId, ids)`, `validateGraph(model)`, `transition(model, id, oldStatus)`, `taskView(model, task)`. Dependencies are unique existent other tasks in same project; DFS rejects cycles409; every non-todo task requires all direct dependencies done409. Done→in_progress fails409; reopening to todo while dependent is not todo fails409. View spreads task plus derived `blocked`.

**FACT:** `selectTasks(model, query = {})` (`:45–76`) validates projectId/status/priority/q/page/pageSize; q trimmed/lowercased title substring, <=160 code points; page positive safe integer; pageSize1–50/default10. AND-filter → ascending createdOrder → total → slice → taskView. Empty totalPages0; out-of-range page unclamped empty items. Return `{items,total,page,pageSize,totalPages,revision}`. Legacy nonnormal priority filter fails migration409.

**FACT:** `summarize(model, projectId)` (`:78–91`) checks project via selector when supplied, then counts whole project/all tasks without UI search/page filters; blocked subset of todo; integer-floor completion percentage, zero if empty.

**INFERENCE — AC4:** `listTasks()` without pagination overrides is not an all-task export contract. Existing full-project UI pagination loop demonstrates current read coherence but supplies no CSV serializer. Export ordering cannot assume raw persisted array order: reversed fixture test is intentionally legal (`P\test\query.test.mjs:57–71`). Current text validation accepts comma, quote, newline and formula-leading text (no CSV-oriented transformations); JSON/DOM preservation is not spreadsheet formula protection.

## Existing proof and exact commands

**FACT — test assertions read, not executed unless explicitly noted:**

| ID | Existing test evidence | What it actually asserts |
|---|---|---|
| T1 | `P\test\store.test.mjs:9–51,54–109` | **FACT:** create/edit/reopen revision+text; detached read copies; Unicode code-point limits; one success/one conflict for same revision; failed injected I/O leaves bytes/memory/allocations unchanged and queue recovers; real incompatible rename failure; strict inputs; lock ownership/corrupt startup; close drains queue. |
| T2 | `P\test\lifecycle.test.mjs:19–49,51–108` | **FACT:** terminate owned process before/after rename, preserve complete original/committed snapshot, remove only proven-exited child's lock, recover; occupied lock/port and corrupt bytes fail; real CLI health and test-bridged signal cleanup. Not native Windows Ctrl+C input proof. |
| T3 | `P\test\api.test.mjs:9–43,45–157,159–184` | **FACT:** real HTTP JSON/ETag/no-store, body/media/origin/host/revision failures, allowlist/method boundary, graph atomicity/no-op disk equality, persisted priority after reopen, streaming413, storage503/generic500. |
| T4 | `P\test\rules.test.mjs:15–63` | **FACT:** blocked transitions and reverse reopen, rejected combined title/status does not alter disk, no-op revision, self/missing/duplicate/cross-project/long-cycle rejection, property-order-independent final candidate validation. |
| T5 | `P\test\query.test.mjs:9–71`; `P\test\query-fixture.mjs:3–35` | **FACT:** real HTTP AND-before-paging rows B,D then E,F; normalized launch filter; no-results/out-of-range; unchanged full-project/global totals; invalid duplicate/enums/unsafe pages; physically reversed persisted array still sorts. |
| T6 | `P\test\schema.test.mjs:13–99`; `P\test\migration.test.mjs:17–177` | **FACT:** strict corrupt/mixed/unknown shapes, limits/exhaustion/no allocation consumption, genuine fixture decode/hash, all legacy writes incl no-op rejected byte-exactly, actual migration CLI backup/repeat, matching/mismatching backup recovery, explicitly lossy rollback retaining v2 archive, lock/corrupt migration fail, HTTP priority/filter/restart. |
| T7 | `P\scripts\e2e.mjs:255–365,403–445,447–533,535–577` | **FACT:** base create/edit/reload/full restart, stale draft rejection and explicit discard, invalid-title focus, safe script-like text, keyboard cancel/focus, network recovery; graph rejection/reopen/restart; filtered pages/Back/deep links/default13-task pagination/dashboard; actual v1 migration and priority restart. Helpers audit labels/44px controls/390+1280 widths/axe (`:222–254`); no archive/CSV journeys found. Embedded historical AC01…AC09 labels are not this task's AC1…AC5. |

**FACT — harness behavior:** `P\scripts\check.mjs:5–14,18–30` supports `unit|integration|all|coverage`; integration selects only api/lifecycle tests, unit excludes those two (so “unit” still writes files and includes HTTP/migration tests). It uses native single-run TAP, per-test30s, overall120s, fails zero tests/skips/cancellations; coverage includes `src/**`, no threshold declared there. `P\test\helpers.mjs:22–32` creates/removes app-local `.work\test-*`; therefore these suites were not run during read-only research.

**FACT — browser prerequisite/seam:** e2e accepts only base/graph/query/migration/all (`P\scripts\e2e.mjs:13–19`). It creates `.work\e2e-*` before tool discovery, so even a prerequisite test invocation violates this research write boundary. `discoverCli()` checks explicit `AGENT_BROWSER_BIN` and npm cache native executable metadata for exactly `agent-browser@0.37.1` (`:63–73`). It imports `benchmark\node_modules\playwright\index.mjs` to launch/close an owned persistent Chromium context, drives browser via explicit IPv4 CDP and CLI, and retains reports/screenshots/transcripts (`:580–655`). `benchmark\node_modules\playwright\package.json` is absent in this worktree (wrapped path check); CLI/cache/browser availability was not inspected outside repository. No execution failure or installation occurred.

**FACT — commands below are exact follow-on commands grounded in `package.json:6–12`, `README.md:6–14,120–128`, and `check.mjs:5–14`; they were NOT run.** Run from repository root after parent authorizes file-writing verification. Windows PowerShell:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$node = 'C:\Program Files\nodejs\node.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;C:\Program Files\nodejs;' + $env:PATH
& $py scripts\run.py --idle 60 --max 180 -- $node examples\team-planner\scripts\check.mjs unit
& $py scripts\run.py --idle 60 --max 180 -- $node examples\team-planner\scripts\check.mjs integration
& $py scripts\run.py --idle 60 --max 180 -- $node examples\team-planner\scripts\check.mjs all
& $py scripts\run.py --idle 60 --max 180 -- $node examples\team-planner\scripts\check.mjs coverage
& $py scripts\run.py --idle 120 --max 900 -- $node examples\team-planner\scripts\e2e.mjs --flow base
& $py scripts\run.py --idle 120 --max 900 -- $node examples\team-planner\scripts\e2e.mjs --flow graph
& $py scripts\run.py --idle 120 --max 900 -- $node examples\team-planner\scripts\e2e.mjs --flow query
& $py scripts\run.py --idle 120 --max 900 -- $node examples\team-planner\scripts\e2e.mjs --flow migration
& $py scripts\run.py --idle 120 --max 1800 -- $node examples\team-planner\scripts\e2e.mjs --flow all
```

**FACT:** no lint/type/build command exists in this app manifest; README says no framework lint/build (`P\package.json:1–13`; `P\README.md:86–88`). **INFERENCE:** suite choice should follow touched seam, not run every listed command redundantly. Parent must first observe an actual missing-dependency failure before any install, per assignment.

### Read-only execution evidence

**FACT:** all external invocations were under root `scripts\run.py --idle 30 --max 60`. Git/environment/path inspections succeeded; no timeout/recovery occurred. A Node `-e` async probe imported only native fs/assert/crypto and app schema/rules, read the existing v1 fixture, and mutated **only local memory**. Observed output:

```json
{"result":"PASS read-only schema/query probe","fixtureSha256":"ad7845486864bb4fef3f938eac02ef4ba213f8d3e20da4e4fa1b1c8b61df4450","legacyRevision":11,"upgradedRevision":12,"projectCount":2,"taskCount":7,"archivedField":"rejected INVALID_INPUT","legacyEncoding":"rejected MIGRATION_REQUIRED","delimiterUnicodeMultilineRoundTrip":true}
```

**FACT — exact substantive assertions executed:** `decode(bytes).schemaVersion === 1`; `upgradeV1(bytes).revision === 12`; selector `{projectId:'p-1',status:'todo',page:2,pageSize:2}` IDs equal `['t-7','t-8']`; project summary total6; encoding legacy throws `MIGRATION_REQUIRED`; adding `projects[0].archived=true` to a cloned upgraded model makes decode throw `INVALID_INPUT` with field `archived`; changing title to `=SUM(1,2)` and description to comma/quote/emoji/newline text round-trips unchanged through `decode(encode(model))`. **FACT:** this is not disk-write, HTTP, browser, archive functionality, or CSV proof.

## Reuse and blast radius

- **FACT:** existing error helpers and schema validation are shared by planner, store and server; rules are shared by schema validation, task mutation, task listing and dashboard (imports/definitions in `P\src\planner.mjs:1–2`, `schema.mjs:1–4`, `store.mjs:1–4`, `server.mjs:1–3`). Reuse candidates are these **existing** contracts, not new component recommendations.
- **FACT:** `JsonStore` already offers the injected `commitFile` failure seam used in real-file tests; helpers offer fixture ownership and cleanup; query fixture offers a mixed-status dependency dataset (`store.test.mjs:35–51`; `helpers.mjs:8–32`; `query-fixture.mjs:20–34`).
- **INFERENCE:** affected behavior spans source schemas/domain/HTTP/store compatibility, public navigation/forms/download UX, and corresponding app tests/docs. No runtime implementation change is required to research or later modify these app seams. Compatibility decisions can affect legacy fixture exact-equality expectations and migration/browser-health schema checks.
- **FACT:** browser `request()` always parses JSON (`P\public\app.mjs:52–55`); therefore it is not currently a binary/text download client. Existing `send` accepts raw body/headers but no export response semantics exist (`E2`). This is a consumer contract distinction, not a chosen download mechanism.

## History & external sources

**FACT:** relevant implemented compatibility rationale is in the current app README and migration assertions (E5/T6); only current baseline and read-only branch/remote metadata were consulted. No prior task research/report, evaluator corpus, external website, PR history, or git historical file contents were needed or inspected. **UNKNOWN:** any historical rationale beyond those present docs is unestablished and not used to justify a decision.

## Gaps & scoped search evidence

- **S1 — FACT:** case-insensitive `archiv|restor|csv|download|spreadsheet|formula|content-disposition`, file filter `*.{mjs,md,html,css,json}`, searched only `P\src`, `P\public`, `P\test`, `P\README.md`. Hits were rollback backup/archive terminology, “Archive brief” fixture title, README Back/diagnosis restore words. No project lifecycle/CSV implementation or tests in that scope. Full planner/schema/server/UI definitions were read as a registration/consumer cross-check, not inferred from empty terms alone.
- **S2 — FACT:** `Planner|listProjects|createProject|createTask|updateTask|selectTasks|summarize|migrateToV2|decode\(|encode\(` in `P\src` and `P\public`, `*.mjs`, corroborated main→Planner→server registration, store/schema calls, and migration CLI; browser endpoint strings were separately read in E4. No alternate app task-write route found after complete router inspection.
- **S3 — FACT:** app-only file inventory found 36 files: 8 source modules, 3 public assets, 6 app scripts, 13 test modules plus 2 fixture JSONs, README/package/two dotfiles. Instruction search scope/results are above. No separate app ADR/glossary/framework config or app lockfile appeared in this inventory. This is not a repository-wide absence claim.
- **FACT:** excluded filenames from the initial inventory were not used as evidence; prior case-study links remain uninspected. `diagnose.mjs`, mutation internals, command/diagnosis test bodies were not investigated because they are not lifecycle/export contracts; their existence does not establish acceptance coverage.
- **UNKNOWN:** real-file suite results and UI/browser runtime behavior at this snapshot are unverified in this assignment. Tests were read, not retrospectively called passing. Browser tooling outside worktree is uninspected, and worktree Playwright metadata is absent.

## Risks & questions (not design)

1. **INFERENCE — AC1/AC5:** the highest compatibility risk is strict disk project shape. Legacy v1 is deliberately read-only, including no-op writes, and v2 migration already has an exact-backup/retry contract (E3/E5/T6). Parent must explicitly reconcile requested archival with supported schema versions; preserving existing v1 read-only until safe migration is the current behavior, not a newly approved product policy.
2. **INFERENCE — AC2/AC5:** active-list filtering is coupled to detail selection and coherent project/task/dashboard revisions (E4); direct archived links require reading the selected project even when absent from active navigation. Existing URL/query validation cannot silently accept arbitrary new keys.
3. **INFERENCE — AC3:** authoritative guard timing, stale revision precedence, rejected/no-op writes, retained draft and control reenable are coupled (E1/E3/E4). Existing graph and same-revision writer tests are preservation evidence, not archive-race evidence.
4. **UNKNOWN — AC4 specification choices:** exact CSV header names/order, dependency-cell representation, BOM/line-ending choice, formula-prefix handling policy, and filename are not specified by this assignment or existing code. **FACT:** required outcomes are deterministic UTF-8, all project tasks, IDs/visible data, interoperable escaping and formula neutralization. These are Phase 2 contract choices for parent, not missing-code blockers or facts to invent here.
5. **UNKNOWN — AC2/AC5 product scope:** whether global dashboard/global task queries should exclude archived data is unspecified; current global queries include all projects' tasks (E6). Parent must record interpretation without silently changing existing aggregate semantics beyond the requested active-project list.
6. **FACT — verification limitation, not research blocker:** full test/browser evidence requires writes forbidden to this researcher. A later authorized browser run will need worktree Playwright and a qualifying CLI/browser; actual missing-dependency failure is required before installation. There is no authorized reason here to inspect external user caches or install tools.

## Handoff

**FACT:** report location is `.ai\planner-live-workflow\research.md`; it contains no design or implementation. Recommended source reading order: E1 schema/domain → E3 transaction → E2 router → E4 UI → E5 migration → T1–T7 proof relevant to the chosen contract. Parent actions are acceptance/reconciliation, missing authoritative artifacts, three citation spot-checks plus cross-component/scoped-absence checks, explicit contract decisions above, and later authorized test execution. **INFERENCE:** no unresolved source-code discovery blocker prevents a grounded design; unknowns listed are specification decisions or deliberately unexecuted verification. Revalidate source citations if HEAD or app working tree changes.

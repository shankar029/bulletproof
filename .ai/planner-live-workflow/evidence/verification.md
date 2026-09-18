# Independent Phase 5 verification

**Verdict: BLOCKED, not a Gate 5 pass.** Fresh verifier, not the feature implementer.
All results are **UNADOPTED PROCEDURAL / unbound evidence, never receipts**.
No adopt/status/next/admission, runtime/evaluator/measurement changes, delegation,
production edits, commits or publication occurred.

## Narrow transport follow-up and final review (2026-09-18)

**AC4 remains BLOCKED. All four existing browser regressions and archive were
run; overall exit 1.** This follow-up supersedes the earlier "all not run"
limitation below, not the earlier failed evidence or other limitations.
Baseline remains `c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`.
All follow-up evidence is **UNADOPTED PROCEDURAL / unbound evidence, never receipts**.

The actual pinned executable's fresh [help](download-remedy-cli-help.txt)
documents `--download-path <path>` and `AGENT_BROWSER_DOWNLOAD_PATH`.
One fresh browser/session used the ordinary absolute Windows directory at attach
(`--download-path`, command 2), also supplied in each CLI child's environment.
Command 367 was an ordinary `click "#download-csv"` on the genuine legacy UI.
It returned success, but bounded filesystem observation for 12 seconds found
**no entries and no saved CSV**. No HTTP byte comparison was reached.
Navigation/click success was not counted as a download. The run issued no
`download` or `wait --download` commands, injected no diagnostic anchor, and
used no synthetic download or HTTP substitute. The four later archive download
scenarios were explicitly blocked by that first failure, not retried or passed.
The extended-path explanation remains an unproved hypothesis; this experiment
does not establish why the global-path route failed.

| Flow | Passing named checks | Result |
|---|---:|---|
| base | 61 | VERIFIED |
| graph | 20 | VERIFIED |
| query | 30 | VERIFIED |
| migration | 15 | FAILED only in legacy-download; genuine migration, exact backup/no-op, edit, filters and restart continued and passed |
| archive | 61 | FAILED: active, archived, stale-client and empty downloads explicitly blocked; remaining lifecycle/conflict/fault/restart scenarios completed |

**187 passing named check records, five failed/blocked scenarios, 26 screenshots.**
These are not requirement counts. Each flow's final console and uncaught-error
collections is empty. Base editor, query and archived axe audits report zero
violations and incomplete checks; this is not human accessibility approval.
The negative export case observed no new file for 1.5 seconds with the real
request aborted, plus focused error and blank success notice. It deliberately
does not claim absence of a browser download event, and still has no passing
download positive control.

Artifacts:
[full report](e2e-2026-09-18T08-44-16-260Z-61878553/report.json),
[all-flow transcript](download-remedy-all.txt),
[final review and source/cleanup hashes](download-remedy-summary.json).
Exact argv/results, HTTP evidence, screenshots and snapshots are adjacent to
the report. The [experimental harness](download-remedy-attempted-e2e.mjs)
is retained as evidence, not as a runnable relocated script; its relative paths
assume the original application script location. Its SHA-256 is
`b54723ab1a87ba40c8f79e8b6a9bc42a276816af9550a965fa4ac1d4065d1926`.

**Final review:** no evidence supports retaining this as a working transport fix.
The app harness was restored byte-for-byte to its pre-follow-up hash
`c9073559d53d4ed5dd1f9bd5150db9de6f56632c24206d33206080c2dd773671`.
No production/tool/infra changes were made. All 12 production file hashes match
both this run and the preceding verifier. All 12 owned app processes exited 0,
their PIDs were absent at the cleanup check, and writer locks were absent.
Harness assertions also verified stopped listeners. Browser/launch-server close
reported no errors and the owned profile was removed. The isolated failed
download directory remains empty; fixtures and evidence are retained.

Exact command, from repository root:

```powershell
$env:E2E_EVIDENCE_DIR = Join-Path (Get-Location) '.ai\planner-live-workflow\evidence'
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' scripts\run.py --idle 120 --max 2400 -- 'C:\Program Files\nodejs\node.exe' examples\team-planner\scripts\e2e.mjs --flow all
```

No installs, recursive agents, native reruns, additional transport retries,
adoption, receipts, commits or publication. The prior AC1/AC2 results remain
supported; AC3 still lacks successful stale-draft download proof; AC4 remains
blocked. AC5's **unrun browser regression** limitation is now replaced by the
specific results above; keyboard native-confirm and other previously unverified
scenarios remain limitations. This is not a Gate 5 pass.

## Earlier observed results (retained history)

| Evidence | Result |
|---|---|
| [Independent native coverage](independent-native-coverage.txt) | **46/46 pass**, 0 failed/skipped/cancelled; backend line/branch/function coverage **99.40/97.56/97.03%**. CSV and Planner 100% in those three measures. Not browser or changed-line coverage. |
| [Final archive run](e2e-2026-09-18T08-33-33-762Z-b1570d0c/report.json) | **62 passing named check records; 4 failed/blocked download scenarios; exit 1.** 11 screenshots. Real mixed-status lifecycle, two-client conflict, faults and restart exercised. |
| [Legacy/migration run](e2e-2026-09-18T08-29-15-530Z-7e5f273a/report.json) | **15 passing named check records; 1 failed legacy-download scenario; exit 1.** 3 screenshots. Existing migration journey completed, including actual process restarts and editing. |
| Full browser `--flow all` | **NOT RUN:** user required archive to pass first; that prerequisite remains blocked. Existing base/graph/query/migration functions and all dispatch are preserved, with archive added. |
| Source freshness | All **12 production files in src/public** match the first invocation through final verification. Per-file hashes, design/contract hashes and exact named checks: [verification-summary.json](verification-summary.json). |
| Accessibility | Final archived detail: axe **4.12.1**, **0 violations / 0 incomplete**; 390/1280 geometry, labels and 44px controls passed. This is not full WCAG certification or human approval. |

The 77 named check records are not 77 requirements, nor a claim about all 29 features.
Shared helpers retain historical AC01-AC09 labels; the mapping below uses the actual
current AC1-AC5 scenarios, not those historical numbers.

## Acceptance-criterion reconciliation

| AC | Actual assertions and evidence | Verdict |
|---|---|---|
| AC1 | Native archive/API/queue/restart suites pass. Browser creates todo/in_progress/done/blocked tasks; cancels and accepts the real confirmation; asserts every task record, nextId, only the target project flag, and revision +1; restarts real main.mjs and compares persisted model; restores, edits, restarts again; archives an empty project. Final archive checks `Any-status lifecycle preserves all task fields, IDs and allocation`, `Only target project archive flag changes`, `Restart preserves exact archived model`, `Restore and edited text survive second restart`. | **VERIFIED** for procedural functional proof. |
| AC2 | Native partition/detail/strict query tests pass. Browser asserts archived sidebar IDs, active sidebar exclusion while retaining independent archived detail, Back restoring archive selector/page, direct link without archived selector after restart, mixed-status/blocked badges, and empty archived detail. Screenshot `archive-filtered-archive.png` and corresponding snapshot. | **VERIFIED** for procedural functional proof. |
| AC3 | Native every-field/create/no-op/combined writes, races and dependencies pass. Browser asserts disabled Add/Edit, enabled Restore/download, real restored edit and retained dependency rejection. Eight current-revision HTTP writes are rejected as PROJECT_ARCHIVED with byte-identical disk. Two real browser tabs produce a stale draft; UI retains text, focuses error, fences Save, Cancel focuses heading, explicit reload adopts archive. Post-save read failure also retains/fences the draft. | **VERIFIED-WITH-LIMITATIONS:** actual download during stale editing is blocked; do not claim that successful downloading was proved not to rebase the draft. |
| AC4 | Native safe CSV exact bytes, parser/formula table, Unicode/newlines/quotes/dependencies, >50 rows, order, headers, legacy and unchanged storage tests pass. Real browser Download CSV attempts on active, archived and legacy projects fail in the tool before a file is saved. Error-download HTTP abort correctly produces focused error, blank success notice, and no file/event. | **BLOCKED:** zero successful browser-saved files; active/archive byte comparison, full-project download and legacy download are not verified. Native/HTTP proof is not substituted. The no-file negative has no passing browser-download positive control. |
| AC5 | Browser AND filters/page 2 survive archive and Back; geometry/axe/focus checks pass. Keyboard Tab reaches download; Enter restores; lifecycle focus replacement and fenced Cancel focus pass. A stale, genuinely previously fetched project-list response is injected while other responses come from current real storage: coherence mismatch fences writes and retains old content. Aborted health read after actual save retains/fences draft without success announcement, then explicit reload restores committed writable state. Legacy fixture hash, exact migration/backup, no-op retry, priority/search/status AND filtering, edit and restart pass. Native storage/recovery compatibility regression is green. | **VERIFIED-WITH-LIMITATIONS:** full browser regression not run, pure keyboard archive-confirm activation blocked in CLI, obsolete-success/obsolete-failure completion race not separately exercised, human accessibility review unavailable. |

## Blockers and findings for the coordinator

**B1 — Actual browser downloads remain unverified (blocking). FACT:** pinned
agent-browser 0.37.1 `download "#download-csv" <path>` returns
`{"success":false,"data":null,"error":"Download was canceled"}`. The application
announces `CSV download started.`; no saved bytes exist. The same command against
a diagnostic anchor pointing directly to the real HTTP attachment also cancels
and leaves no file (final report `downloadControl`). This anchor is a negative
transport diagnostic, not an alternate passing feature implementation.
Archived attempts are independently recorded in attempt8/attempt10, and legacy
in the migration run. After the first failure in final runs, dependent download
scenarios are explicitly failed/blocked rather than repeatedly retried or passed.

**INFERENCE:** the direct-HTTP negative control points to a browser/CLI transport
problem rather than establishing a production CSV defect. **HYPOTHESIS, not root
cause proved:** pinned upstream
`cli/src/native/actions.rs::handle_download` canonicalizes its Windows destination
before passing it to `Browser.setDownloadBehavior`; Windows extended paths may be
involved. See [diagnostic excerpts](pinned-download-diagnostic.txt) and public
source at `https://github.com/vercel-labs/agent-browser/blob/v0.37.1/cli/src/native/actions.rs`.
No executable/tool/runtime was patched. No requirement was waived.
Coordinator must establish an agent-browser transport that actually saves files,
then rerun archive and, only when green, all. **No production fix is justified by
this diagnosis alone.**

**B2 — Keyboard-triggered native confirmation (limitation). FACT:** on
launchServer with sole agent-browser page ownership, `press Enter` on Archive
opened a blocking dialog and the command hit idle timeout 124. Pointer-triggered
native confirm dismiss/accept both work, and Enter on Restore works. No confirm
replacement/mock was installed. Pure keyboard Archive remains unverified.

**Harness corrections, not product fixes:** initial fixture creation incorrectly
sent `status` in POST; fixed to create then PATCH through real API. A premature
evidence copy encountered a locked browser cookie file; moved copying after close
and excluded the disposable profile. Existing `launchPersistentContext` silently
dismissed native confirms; launch-only `chromium.launchServer` removes that
Playwright page/context client. Playwright still performs only launch/close;
all UI observation/actions, tabs, dialogs, screenshots, accessibility and faults
use agent-browser. A new full Chromium launch allowed diagnostic chrome pages;
it did not fix downloading. Recorded tab labels/targets could not reliably be
closed individually after reconnection, so whole owned-browser close performs
cleanup. No production behavior was changed or mocked to turn a test green.

The retained attempts include cancelled download retries, one wait-download
alternative timeout, failed headless-shell internal-page inspection, a
connect-once transport experiment, and bounded keyboard/download/screenshot
idle kills. These are failed evidence, not extra passing assertions. Earlier
partial runs are superseded only by the explicitly named final scenario results.
Final archive/migration end-of-flow console and uncaught-error snapshots are empty;
do not interpret end snapshots as a complete time-continuous console trace.

**UNKNOWN / not measured:** all nine guarded quality metrics (including mutation
and changed-line coverage), architecture/static/duplication/complexity closure,
human approval and full-browser regression. Native backend coverage does not fill
these gaps. G6 remains outside this verifier's closure authority.

## Commands, binding and retained artifacts

Executed from the repository root, PowerShell:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$node = 'C:\Program Files\nodejs\node.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;C:\Program Files\nodejs;' + $env:PATH
$env:E2E_EVIDENCE_DIR = Join-Path (Get-Location) '.ai\planner-live-workflow\evidence'
& $py scripts\run.py --idle 120 --max 1500 -- $node examples\team-planner\scripts\e2e.mjs --flow archive
& $py scripts\run.py --idle 120 --max 600 -- $node examples\team-planner\scripts\e2e.mjs --flow migration
Remove-Item Env:NODE_TEST_CONTEXT -ErrorAction SilentlyContinue
& $py scripts\run.py --idle 120 --max 240 -- $node examples\team-planner\scripts\check.mjs coverage
& $py scripts\run.py --idle 30 --max 60 -- $node .ai\planner-live-workflow\evidence\summarize-verification.mjs
```

Final archive stdout/stderr: [archive-final-assertions.txt](archive-final-assertions.txt).
Migration: [independent-migration.txt](independent-migration.txt).
All command argv/cwd/times/exit/stdout/stderr, native HTTP requests and responses,
process lifecycle, source hashes, screenshots and snapshots are in each run's
`commands.jsonl`, `http.jsonl`, `report.json` and adjacent files. Browser commands
are individually wrapped by root run.py (`--idle 25 --max 30`, warmup max60);
whole invocations are wrapped as above. App fixtures are isolated under
`examples\team-planner\.work\<runId>\data-*`, never user data.
CLI dialog/download/wait/tab/network help was read before use and retained as
`cli-*-help.txt`; native executable package metadata requires version 0.37.1.
No install occurred in this verifier run.

Final harness SHA-256:
`c9073559d53d4ed5dd1f9bd5150db9de6f56632c24206d33206080c2dd773671`.
Migration used runner SHA
`b843107998052018976e74d82a26944d6e538d3f1fd0993a48ac544370604146`;
the subsequent two-line change only replaced archive's confirmation marker with
an observed control-text assertion and removed "once" from a commit check label.
Its migration function and production source were unchanged.

Finishing command **after archive passes**, not run here:

```powershell
& $py scripts\run.py --idle 120 --max 2400 -- $node examples\team-planner\scripts\e2e.mjs --flow all
```

## Cleanup and scope

Final archive and migration each started/stopped three owned real app processes.
All six exited 0, released their owned writer locks, and refused HTTP on the old
listener during harness shutdown/restart assertions. Both agent-browser close
and Playwright launch-server close completed without cleanup errors; owned
browser profiles were removed. The accidentally copied profile from attempt1
was specifically removed after inspecting its exact path. Reports, screenshots,
failed outputs and isolated data fixtures remain deliberately retained.
See [cleanup-summary.json](cleanup-summary.json) for the final owned-process check.

Only `examples\team-planner\scripts\e2e.mjs`, this task's evidence and traceability
were edited. Prior case study, state/design/contracts, production files and
guarded candidate artifacts were not rewritten. No commit/push. No production
bug was demonstrated in the successfully executed scenarios; B1/B2 and the
remaining unverified scenarios require coordinator disposition.

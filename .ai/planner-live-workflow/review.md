# Independent final review and AC reconciliation

**Overall verdict: BLOCKED.** Reviewed 2026-09-18 in a fresh reviewer context.
This is **UNADOPTED PROCEDURAL / unbound evidence, never a receipt, admission,
human approval, or G6 closure**. Coordinator-authorized continuation is valid for
this review; parked guarded candidates do not need fabricated approval.

## Snapshot, scope and method

- Base and observed HEAD: `c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`.
- Reviewed the entire current app diff against that base, including unstaged
  changes and the four untracked files. Tracked scope: `README.md`,
  `public/app.mjs`, `public/index.html`, `scripts/e2e.mjs`, `src/planner.mjs`,
  `src/schema.mjs`, `src/server.mjs`. Untracked scope: `src/csv.mjs`,
  `test/archive.test.mjs`, `test/archive-api.test.mjs`, `test/csv.test.mjs`.
  All app paths below are relative to `examples\team-planner`.
- Read root `references/review-and-pr.md`, `quality-bar.md`, `code-clarity.md`;
  this task's state, research, design, UX, complete contracts, plan, tasks and
  clarifications. Followed the changed code into existing schema, rules,
  store, HTTP and test-runner collaborators, not into excluded repository areas.
- Independently parsed the actual final all-flow report, checked counts,
  compared all 12 production hashes with current files, read native TAP and
  mutation evidence, and compared the experimental harness with the restored
  current harness. Inspected captured stale-draft visual evidence; the image
  tool did not display the additional narrow-layout image, so that geometry
  assessment rests on recorded browser assertions, not an independent visual audit.
- Read-only checks in this review: app `git diff --check` passed; Node
  `--check` passed for all nine changed/new JavaScript production, harness and
  test files. Each external command used root `scripts/run.py` with idle30/max60,
  the supplied managed Python/Node and Git PATH. The intentional no-index
  comparison returned 1 because the experimental and retained harnesses differ.
- No browser trials, fixture-writing native reruns, installs, source/test edits,
  collector execution, other worktrees, recursive delegation, commits or
  publication. Only this review and `traceability.md` are authored here.
  Native results below are inspected captured executions, not reviewer reruns.
- Exact checks found this task's `workflow.json`, `current-design.json`,
  `ledger.json`, `workflow.lock` and `metrics.json` absent.

### Current changed-file SHA-256 binding

| App file | SHA-256 |
|---|---|
| `src/csv.mjs` | `4b873fd1f296172532dd8c45085683ab529eddedf1d2bdaa96493c4d77c994f9` |
| `src/planner.mjs` | `f91a9c0e3ad5af944f938917d31f54e3c7b8fcfe267c3acdd8a778fee5dfc221` |
| `src/schema.mjs` | `288f4b9009aca3237852bd472d8d20d328251a8818d0eca4f9c14c0c7bb42a53` |
| `src/server.mjs` | `ca78205e4b1a2c38d31208a6f154b5a8a91703cdc3c16a56b681e1d1e2885bee` |
| `public/app.mjs` | `f5aca3b58f70e75053210792288a8d15516f7cd2abfee7d6781aa07612967408` |
| `public/index.html` | `cf2b5536b996f6fea0a28c37b7e1519afe82c920ad400536c7532813aea929ba` |
| `scripts/e2e.mjs` | `c9073559d53d4ed5dd1f9bd5150db9de6f56632c24206d33206080c2dd773671` |
| `test/archive.test.mjs` | `29b716296df7b27cdb24a85150b9e85a7f403f1282c074e0e097aefd829ba74d` |
| `test/archive-api.test.mjs` | `dffc407b8a59df7bf2a2a3665b03afb9e487e1c042eefb1a27f6a5cf4503f9d2` |
| `test/csv.test.mjs` | `235bbc6a9d02837f6c031b6086f7e8ca950129f8d8ab6b1c07e113c225ed0ce4` |
| `README.md` | `ae55906d3dd9ac86f17a28226fe35ff10edf755b27a32ec276e373dcb064107b` |

## Findings, prioritized and classified

### R1 — SPEC / blocking proof gap: downloadable CSV is not verified

**Requirement:** AC4, C3/C4/C5 and UX export journey. Production locations:
`src/csv.mjs:3-16`, `src/planner.mjs:51-54`,
`src/server.mjs:87-93`, `public/app.mjs:148-174` (`downloadCsv`).

Native serializer/HTTP tests prove useful CSV properties, but **no actual
browser-saved CSV exists**. The original pinned CLI download and diagnostic
direct-HTTP attachment both canceled. The later ordinary click with the
documented global download path succeeded as a click but yielded no directory
entry in 12 seconds. Four dependent scenarios were then blocked, not executed
successfully. Neither the success notice nor an HTTP body substitutes for a file.

Evidence: `evidence/verification.md`, `download-remedy-summary.json`,
`e2e-2026-09-18T08-44-16-260Z-61878553/report.json`, and the preceding final archive
report `e2e-2026-09-18T08-33-33-762Z-b1570d0c/report.json`.

**Disposition: OPEN, environment-blocked; no production patch justified.**
The negative direct-HTTP control supports a transport limitation, but does not
prove a specific root cause. Windows path canonicalization remains a hypothesis.
Do not replace the download mechanism, shorten assertions, or claim a fixed
transport on this evidence. Future authorized verification needs a real saved
file and independent byte/row assertions for active and archived projects,
then the dependent legacy, empty and stale-draft scenarios and final regression.
No further trials were run in this review.

### R2 — STANDARD / blocking quality gap: all nine required metrics unavailable

Binding rules: `references/quality-bar.md` “Metrics outrank opinion” and
`references/review-and-pr.md` quality/evidence gates; task I1.T6.
`evidence/measurement-status.json` explicitly identifies itself as an
**agent-authored availability note, not probe/producer output**. No `metrics.json`
exists. The coordinator prohibited the root-wide collection/materialization
path; the bounded app sample was approved instead. That is a scope decision,
not a successful metric collection.

Required and still unavailable: `duplication_pct`, `complexity_max`,
`complexity_avg`, `cycles`, `dead_exports`, `static_findings`,
`mutation_score_pct`, `diff_coverage_pct`, `architecture_rules`.
Backend coverage and the sampled mutations do not close any missing qualified
metric. No numeric quality scores are assigned.

**Disposition: OPEN/BLOCKED, outside app implementation scope.** Do not launch
the prohibited collector or manufacture measurements, producer bindings or
receipts. G6/I1/ship closure remains blocked independently of functional progress.

### R3 — DESIGN CONCERN / P2: browser replay now defaults to a private machine path

`scripts/e2e.mjs:17,36-41` introduces a default Python executable beneath this
user's `C:\Users\shbs\...` profile and uses it for every CLI command.
`README.md:145-170` documents browser replay and `AGENT_BROWSER_BIN`, but not the
new required Python setup or `E2E_PYTHON` override. On another otherwise correctly
configured machine the documented command now attempts a nonexistent executable
before browser verification can run. This is a test-harness reproducibility
regression, not a production archive/CSV defect.

Using the supplied executable **for this session** is correct; baking that
location into a reusable app harness is the issue. The proportionate remedy is
an explicit documented executable configuration (or portable discovery with a
clear prerequisite failure), retaining the bounded root runner. No new runtime
adapter, dependency or collector is needed.

**Disposition: OPEN; source frozen, no fix made.** Resolve before representing
the documented replay as portable. Current-machine evidence remains usable.

### R4 — SPEC / P3: disabled lifecycle control lacks its contracted explanation

`contracts/r1.json`, C5 `state_contract`, requires “Finish or cancel your draft
before changing project state.” `public/app.mjs:47-52` correctly disables the
lifecycle button while an editor exists; `edit:110-147` and `render:220-232`
never render that explanation. The only adjacent action text concerns export.
The browser check at `scripts/e2e.mjs:798` asserts disabled state, not guidance.

This is a small **production UX/design-fidelity omission**, not a read-only
authorization failure or data-loss defect. A user sees an unavailable action
without the specified recovery instruction. Add the nearby conditional guidance
when source changes are authorized, with an assertion for its presence/removal;
retain the existing guard and Cancel behavior.

**Disposition: OPEN; no production edit authorized.** Original task-write
protection is supported, but full C5 conformance cannot be called complete.

## Source-level correctness and design assessment

- **Lossless lifecycle / C1-C2:** optional strictly boolean v2 state is validated
  at `src/schema.mjs:46-50`; v1 still rejects the field. `projectView:23-25`
  normalizes responses without rewriting stored old records.
  `setProjectArchived:55-64` changes only the effective lifecycle flag inside
  `JsonStore.transact:73-95`; missing-false restore stays a no-op. The unchanged
  store checks legacy then revision, clones, validates and persists before
  publishing. No task-status prerequisite, ID allocation, task deletion or
  dependency rewrite is introduced.
- **Read partition / C2-C4:** `listProjects:40-47` defaults active and strictly
  validates its query. `getProject:48-50` is independent of that partition.
  Router `src/server.mjs:62-104` rejects malformed/unsafe project IDs, disallowed
  methods and queries, retains header/body/origin boundaries, and exports from
  one committed snapshot. Existing global task/dashboard semantics stay inclusive.
- **Read-only and races / C2-C5:** `assertProjectWritable:28-31` is shared by
  create at `planner.mjs:83` and update at `:100`, before allocation/field mutation
  and after the transaction's revision check. Shape errors retaining precedence
  over the domain guard are intentional in the contract, not a write bypass.
  `public/app.mjs:41-53,79-146` combines loading/busy/fence/legacy/project policy,
  captures editor revision, does not adopt mutation-response revision, preserves
  failed drafts, and reenables writes only after coherent reload. Cancel remains
  available. Restore still uses normal graph and transition validation.
- **CSV / C3:** `src/csv.mjs:3-16` implements the exact specified prefix policy,
  quotes every cell, doubles quotes, keeps embedded CR/LF/Unicode and dependency
  order, sorts a filtered copy, includes all ten fields and uses `taskView`
  for blocked state. It does not paginate or mutate the model.
  `src/server.mjs:87-93` supplies safe ID-only filename, UTF-8, no-store and
  snapshot ETag. `downloadCsv` checks HTTP success before creating its blob/anchor,
  removes the anchor and schedules object-URL release. Source inspection does
  not establish that the browser saved those bytes.
- **Coherence / C5:** `reload:281-332` captures URL and sequence, checks detail,
  list, summary, health and all task batches before atomic state publication,
  ignores obsolete success/failure completions, and fences current failures.
  Actual mismatch/post-save read-fault evidence exercises important paths, but
  not every delayed-completion ordering.
- **Maintainability:** boundaries remain appropriate: lifecycle policy in
  Planner, format policy in the pure CSV module, transport in server, browser
  state in existing UI. Shared store/rules/DOM helpers are reused. No framework,
  speculative abstraction, metric-motivated production splitting, destructive
  sanitization or exception-swallowing “fix” for downloads was found. The
  task-wide design mostly matches source, subject to R4 and the unverified
  interactions below. R3 is a concrete test integration cost, not a style quota.

**Production-fix judgment:** no demonstrated corruption, lifecycle authorization,
CSV-formatting or storage defect warrants changing frozen production to address
the download blocker. R4 is a real but low-severity UX contract fix for a later
authorized edit; it must not be confused with an established download root cause.

## Evidence reconciliation and test quality

| Evidence actually read | Observed result and boundary |
|---|---|
| `evidence/baseline.txt` | 37 pass, 0 failed/skipped/cancelled. |
| `evidence/red.txt` | 3 native `ERR_ASSERTION` failures: HTTP 404 versus 200/400; no missing-import pseudo-red. Historical line numbers belong to that red snapshot, not today's source. |
| `evidence/coverage.txt`, `independent-native-coverage.txt` | 46 pass, 0 failed/skipped/cancelled; backend line **99.40%**, branch **97.56%**, function **97.03%**. CSV/Planner 100% in those backend measures; not browser or changed-line coverage. |
| `evidence/final-native.txt` | Retained final native/coverage output agrees with the green suite; no independently rerun suite is claimed here. |
| Latest all-flow report | **FAILED / exit1**; 187 passing check records, 26 screenshot files, five failed/blocked download scenarios. Base61/graph20/query30 passed; migration15 and archive61 completed their non-download assertions but their flows failed. Counts are records, not distinct ACs. |
| Retained final archive report | 62 passing records and four failed/blocked downloads on the current restored harness; not a full all-flow green. |
| `evidence/mutation-sample-summary.json` and transcript | 30 selected backend mutations: **28 killed by assertions, 2 survived, 0 ungraded**. Bounded module sample, not all changed lines or browser mutation coverage; not the missing qualified mutation metric. |
| Reviewer read-only checks | Current app diff whitespace check and all nine changed/new JavaScript syntax checks passed. No configured app lint/type/build script exists; these are N/A, not passing metric gates. |

### Evidence binding and limitations that remain material

1. **Full run versus retained harness:** the latest all-flow report records
   experimental runner hash
   `b54723ab1a87ba40c8f79e8b6a9bc42a276816af9550a965fa4ac1d4065d1926`;
   current retained harness is `c9073559...773671` (full hash above). Direct
   comparison confines the experiment to download transport/negative-file
   observation and attach configuration. Base/graph/query and other lifecycle
   assertions were not removed. All 12 production hashes match the latest and
   earlier verifier snapshots. Thus the non-download regression evidence applies
   to unchanged production, but **no all-green invocation of the current final
   harness is evidenced**.
2. **Download negative control weakness:** retained
   `scripts/e2e.mjs:840-853` labels a failed, timed-out `wait --download` as
   “emits no browser download event.” With no successful positive control that
   is stronger than the observation warrants; command timeout/no file does not
   independently establish event absence. The latest experiment correctly
   limits its assertion to 1.5 seconds with no new file, focused error and no
   success notice. Even that negative alone does not certify browser transport.
   Do not count the historical label as proof. Remedy the assertion wording and
   establish a positive control in future authorized harness work.
3. **Mutation survivors are not proven fully equivalent:** both are existing
   `planner.mjs:72,86` capacity checks changed from `>=` to `>`.
   `schema.mjs:38` and `store.mjs:85-91` still reject oversized candidates before
   persistence. `test/schema.test.mjs:55-85` checks code and unchanged state/bytes,
   not message/validation-order equivalence. The domain's “Project/Task limit
   reached” versus schema's “Dataset capacity exceeded” is an observable
   difference; exhaustion/other input errors can also take different precedence.
   These are **not evidence of a newly introduced capacity bug**, but “fully
   equivalent survivors” and full mutation closure are unsupported. The sample
   also selects existing find/capacity guards rather than exercising all new
   Planner lifecycle/guard branches.
4. **Assertion strength:** the new tests are substantive: real HTTP/files,
   queued races both orders, restart equality, injected persist failure,
   strict fields/queries, independent CSV parser and adversarial formula table,
   >50-row HTTP export. No new test skips or empty assertions found.
   However the 53-task pure fixture has only todo statuses, while mixed-status
   lifecycle and six-task browser fixtures carry the broader status cases.
   Avoid claiming a single exhaustive Cartesian combination from these tests.
5. **Browser cases still unverified:** successful stale-draft download without
   revision rebasing; actual saved active/archive/legacy/empty bytes; pure
   keyboard activation/cancel of native Archive confirmation; separately delayed
   obsolete-success and obsolete-failure completion races. Pointer native
   confirmation and keyboard Restore passed. Unknown-project behavior is
   supported by native/source checks, not a separately demonstrated UI error
   journey here. Large-project (>50) browser dependency-choice loading has no
   new dedicated archive evidence.
6. **Accessibility and cleanup boundaries:** recorded axe audits are zero
   violations/incomplete for tested pages; narrow/wide geometry, labels,
   targets, Tab/Restore/Cancel focus checks are useful but not full WCAG or human
   sign-off. End-of-flow empty console/error snapshots are not continuous traces.
   Captured cleanup reports show owned app processes exited and locks/listeners
   released, not an unlimited claim about every possible timeout path.
7. **Harness timeout ownership risk:** `command:36-64` adds root `run.py`
   with `--max timeout` while keeping an outer `child.kill('SIGKILL')` timer at
   the same timeout. At the absolute ceiling the outer timer can terminate
   Python before its child-tree cleanup completes. This is a source-based
   teardown risk, not an observed orphan in these runs; keep the root runner
   authoritative and allow cleanup grace if changing this helper later.

## Requirement and execution-plan reconciliation

Per-AC verdicts and source/test locations are persisted in
[`traceability.md`](traceability.md):

- AC1 **VERIFIED**; AC2 **VERIFIED**.
- AC3 **VERIFIED-WITH-LIMITATIONS**; AC4 **BLOCKED**.
- AC5 **VERIFIED-WITH-LIMITATIONS**.

These mean procedural functional evidence only. No AC verdict silently grants
quality closure or turns an unavailable scenario into a pass.

T1 baseline and T2 actual red have captured proof. T3/T4 have source and green
native evidence. Schema compatibility assertions were placed in
`archive.test.mjs` instead of modifying `schema.test.mjs`; this is explicitly
recorded in tasks/state and preserves existing tests, not scope evasion.
T5 is implemented with substantial browser evidence but R4 and export proof
remain open. T6 is **not complete**: review is now performed, browser all-flow
is not green, and all nine metrics remain unavailable.

The older traceability statement “all-flow not run” is superseded by the actual
latest run, not retained as a current limitation. State/tasks/plan still carry
historical pending-review or pre-follow-up wording; this report and updated
traceability are the final review outcome, not authority to edit those files.
Human design/UX approval remains unconfirmed. Procedural authorization is
explicit; no demand to backfill guarded receipts or pretend parked candidates
were adopted is made. Publication remains unauthorized.

## Quality judgment, without invented scores

| Dimension | Independent outcome |
|---|---|
| Correctness | Strong source/native/non-download browser support; AC4 blocked and R4 open. Not a final correctness pass. |
| Grounding | Current symbols, interfaces, test names, source hashes and actual reports inspected; hypotheses and missing proof labeled. |
| Design fidelity/depth | C1-C5 boundaries and failure handling largely match; R4 is an explicit remaining contract omission. |
| Scope fidelity | App diff remains lifecycle/export/tests/docs; no production store/rules redesign or out-of-scope repair. |
| Reuse/DRY | Source reuse appropriate; required duplication metric unavailable, numerical judgment unverified. |
| Design/modularity | Responsibilities traceable; R3 reproducibility and timeout ownership concerns; complexity/cycles/architecture metrics unavailable. |
| Maintainability | No arbitrary splitting or stale production change journal found; missing UX explanation and harness configuration are concrete costs. No metric-backed score. |
| Robustness | Transaction/query/error paths reviewed, relevant failures exercised; static metrics and untested browser orderings remain unavailable. |
| Test quality/evidence | Meaningful native/integration/browser checks, but no saved download positive control, no qualified diff coverage or full mutation proof. Hard gate incomplete. |

**Final overall verdict: BLOCKED.** Preserve the useful local implementation and
honest evidence. Do not claim G5/G6/I1/ship pass, successful saved browser CSV,
full mutant equivalence, or a proven production download defect.

## Parent dispositions after review (not an independent re-review)

R1 and R2 remain **BLOCKED**. `evidence/download-attempts.md` now extracts exact
recorded CLI commands, routes, attachment/destination settings and file/event limits.
Observed automation/transport failure is not labeled a proven environment-only cause.
No new download trial was authorized or performed for this follow-up.

R3: removed machine-specific default; E2E_PYTHON is explicit/documented and a missing
value fails before fixture creation. R4: added the contracted nearby draft guidance,
conditional visibility and accessible association. Targeted independent verifier owns
base-flow presence/removal assertions; its results are execution, not this review.

Timeout concern: removed the outer same-deadline timer/AbortSignal that could kill
the bounded Python runner before child-tree cleanup. The helper awaits runner exit,
derives timeout from 124/125, and removes active children only after observed exit.
Whole browser invocation and each CLI remain bounded by root run.py. This correction
addresses the identified source-level ownership race; no absolute-deadline stress or
all-path cleanup proof is claimed.

The coordinator requested the **same reviewer** inspect this narrow delta. Parent
located reviewer `815f7d19-1f55-4dee-a364-e545bc197142` and attempted write_agent.
The runtime refused: “write_agent only supports background agents. Agent ... is in
sync mode. A new background task must be started for follow-up messages.”
Per coordinator fallback, no replacement broad review was spawned. **The independent
review above does not cover the final changed bytes.** Preserve the delta and current
hashes for parent reconciliation; do not claim final independent approval.

Targeted verifier subsequently passed one base run (67 checks including six new
guidance assertions) and the configuration-before-fixtures check. No downloads or
forced timeout. `evidence/post-review.patch` is the exact zero-context delta;
`post-review-binding.json` proves all three recovered prior files matched this
review's SHA256s, and binds final bytes. `final-source-hashes.json` records all
17 final source/test/doc files. Hashes refer to physical files in this worktree,
not Git's potentially line-ending-normalized blobs.

The all-staged whitespace diagnostic reported whitespace in captured `.txt`
transcripts (native coverage table/TAP and CLI output), not source. Those raw
records are preserved rather than silently reformatted. Source and authored
artifact whitespace is checked separately, excluding only captured `.txt` logs.

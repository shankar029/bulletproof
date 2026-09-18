# I1 executable task detail

Planning revision 2, 2026-09-18. **T1-T5 implemented; T6 independently reviewed but BLOCKED.**
Execution mode: **UNADOPTED PROCEDURAL**, explicitly authorized by coordinator after the
guard rejection; no live authority/admission exists. Retain all behavioral prerequisites
and independent roles below. For T1-T6 use bounded direct commands and apply_patch source
edits instead of status/next/record. Results are unbound evidence, never guarded receipts.
Native red remains before production edits. The guarded preparation subsection is PARKED,
not an entry condition for procedural work. Parent consumer-readiness: READY for first
baseline/test task and dependency/error boundary; missing guarded capabilities remain blocked.
This is the authoritative detail linked by [plan.html](plan.html), not live runtime authority.
Scope: `examples\team-planner` (P), plus this task's artifacts. Baseline:
`c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`, branch
`shbs-microsoft-live-planner-workflow`, observed unchanged app at planning inspection.
Design/component hashes, source-file hashes, inventory and command definitions are retained
in [design-history/r1.preparation.json](design-history/r1.preparation.json).
Current source/design inputs are uncommitted task artifacts; no prior guarded adoption exists.

## Authority, ownership, and limitations

- FACT: [research](research.md) E1–E6/T1–T7 and [contracts](contracts/r1.json)
  govern all changes. [clarifications](clarifications.md) governs product decisions.
  All C1–C5 changes belong to **I1**, and each distinct change has an owner below.
- FACT: parent [state](state.md) disposition resolves DR1 using
  [actual rendering evidence](evidence/doc-render-verification.md); DR2 labels were added,
  small remaining overlap accepted. Original [review](design-review.md) is unchanged REVISE.
  Stale “render unverified” statements inside retained design/UX are historical and superseded
  only by the exact-hash evidence and parent disposition, not silently edited.
- FACT: no human sign-off. The authorization reference is separately bound to clarifications,
  not represented as human confirmation. Parent must supply genuine producer metadata.
  `designer` has no dedicated schema role: use the actual parent's **implementer** record,
  identical to the increment's implementer and implementation action owners.
  Actual research, design-review, verification, final-review contexts stay distinct.
- FACT: `scripts\workflow_state.py:337–348` rejects `kind=work, command=null`.
  Null commands are only allowed for check actions with handoff steps (`:487–488`).
  Do not relabel editing as research/verification to evade this restriction; no supported
  ordinary manual-edit handoff exists in this schema. This blocks the requested parent-manual
  implementation route. Parent must select a genuine executable editing route under the
  existing runner, or report the workflow capability blocker. No route is invented here.
- FACT: behavioral-red requires exact assertion metadata (`:321–326,351–362`), including
  test source SHA-256 and positive line numbers. Planned tests do not yet exist and this
  planner may not create them. A complete initial strict candidate cannot truthfully bind
  their future bytes. Resolve with authorized **red-test-only preparation before adoption**,
  or a separately reviewed/adopted staged testing revision. Do not omit red or claim a
  missing-import exception proves the feature. The parent must explicitly choose the
  bootstrap route; artifact preparation alone cannot solve it.
- FACT: before-action checks require exactly one work/retire consumer (`:489–494`).
  Proposed baseline gates test authoring; red gates the single integrated implementation
  action. Baseline/red are historical temporal evidence, not current closure checks.
- FACT: `validate_design_binding(:760–809)` requires APPROVE, independent reviewer,
  component/document/workflow hashes, retained paths, authorization, and real adoption
  history. Current report predates this workflow candidate and says REVISE. A fresh
  candidate-bound follow-up is required. No metadata approval is fabricated.
- FACT: metrics attachment/complete JS collectors remain unavailable per
  `references\workflow-gates.md` and `references\quality-metrics.md`.
  All nine metric requirements remain in I1 closure. Independent review may still
  report useful findings without a metrics pass, but I1/ship cannot close.
- No source, runtime, dependency, evaluator, other-task, ledger, receipt, or live-pointer
  writes are authorized for this planner. No commit/push/adoption was performed.

## Common execution and evidence contract

PowerShell, repository root:

```powershell
$repo = (Get-Location).Path
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$node = 'C:\Program Files\nodejs\node.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;C:\Program Files\nodejs;' + $env:PATH
$env:PYTHONDONTWRITEBYTECODE = '1'
$slug = 'planner-live-workflow'
```

Node v24.11.1 was observed; Python path is the supplied uv interpreter. The original test
harness defines native `--test --test-timeout=30000`; guarded native checks replace TAP with
the **absolute** repository `scripts\native_result.mjs` reporter and enumerate real files.
They do not invoke npm/check.mjs as a classified-test proxy. `NODE_TEST_CONTEXT` is removed.
No shell wildcards. Command definitions below reside once in preparation metadata and,
after preparation, the strict candidate workflow; narrative records reference those keys.
Before adoption these are proposed commands, not admitted executions.

After adoption always run bounded `status --target action:ID` then `next --action ID`.
Inspect returned JSON: wrapper exit, child exit, proof outcome and readiness differ.
For check handoffs `next` starts no agent; parent dispatches the actual registered owner
and supplies admission, snapshot and prerequisite receipt references unchanged.
Return existing-schema receipt with original producer, parent recorder, UTC times, report
hashes/byte sizes and declared evidence files; use ordinary `record`. Never backfill admissions.

Native output destination is runtime-owned `evidence\runs\<actual-run-id>\stdout.txt` and
`stderr.txt`, with immutable accepted receipts. Handoff reports should use
`evidence\verification-I1-<actual-run-id>.md` and `evidence\review-I1-<actual-run-id>.md`;
retain exact downloads/screenshots/logs and reference/hash them in the receipt. These names
are future destinations, not existing passing evidence. Every report records source/contract
binding, argv/cwd/environment, exits, actual assertion/scenario totals, limitations and cleanup.

Owned tests use app-local `.work` fixtures; never real user data or system temp directories.
Only remove owned fixture resources after proven cleanup. Missing dependency failures permit
repair of existing dependencies, not new project tooling. Timeouts have bounded recovery;
unknown descendants/orphan locks stop execution, never authorize lock removal.

## I1.T1 — Baseline

- **Purpose/design/AC:** establish existing behavior before edits; C1–C5, AC1–AC5.
- **Entry:** parent readiness/adoption blockers resolved; app inventory equals baseline.
  A separately authorized prewritten `test\archive-api.test.mjs` may exist for assertion
  binding, but the original nine suites and all production bytes must remain unchanged.
  Baseline's explicit argv does not execute that new file. If the selected test-bootstrap
  route changes this ordering, revise the candidate explicitly.
- **Change owner:** parent implementer; no source changes. `A-I1-baseline` executes
  `commands.baseline`; `C-I1-baseline` must pass before `A-I1-tests`.
- **Reuse/preserve:** P `scripts\check.mjs:5–14`, research T1–T7; exact existing nine suites:
  api, command, diagnosis, lifecycle, migration, query, rules, schema, store.
- **Proof:** complete native leaf inventory, zero failures/skips/cancellations, relevant
  regression assertions actually executed; receipt accepted, not merely exit zero.
- **Failure/recovery:** existing regression failure blocks test authoring/production; isolate
  real environmental versus baseline failure without changing unrelated app behavior.
  No migration or persistent user-data operation; fixture cleanup only.
- **Status:** procedural complete. Existing 37/37 native regression passed; evidence/baseline.txt.

## I1.T2 — Test first

- **Purpose/design/AC:** failing behavioral proof and regression tests for every C1–C5/AC1–AC5.
- **Entry:** T1 accepted; resolved real `A-I1-tests` command. Author tests only, no production.
  Its command must actually do the edits; `echo`, sleep, receipt fabrication or a no-op
  completion marker is not an editing route.
- **Owned changes:** new P `test\archive.test.mjs`, `test\archive-api.test.mjs`,
  `test\csv.test.mjs`; extend `test\schema.test.mjs`. New tests are planned, absent today.
  Parent owns native tests. Browser harness changes belong only to T5/T6 below.
- **Reuse:** P `test\helpers.mjs` `fixture`, `directory`, `cleanup`, `code`;
  existing real HTTP test pattern in `test\api.test.mjs:9–27`;
  store injected rename failure and existing query fixture (research T1/T3/T5).
  Keep new HTTP test setup inside the new test file unless a scoped revision justifies
  a shared helper change. Do not alter genuine legacy fixture bytes.
- **Red:** `C-I1-red` via `A-I1-red`, `commands.red`, runs only the new archive API suite.
  Planned assertion: test named **archive lifecycle PATCH succeeds for mixed-status project**,
  `assert.equal(response.status, 200)` immediately after authenticated/revision-correct
  project archive PATCH. Existing route yields 404; this is an expected behavior mismatch,
  not a claim of an observed failure. Bootstrap only via existing APIs/imports; no import
  from absent csv module in this red suite. Actual name/line/hash/operator/expected/actual
  must be bound from real test bytes and native evidence, not these illustrative values.
- **Other assertions:** schema absent/false/true/nonboolean/v1; full data equality and
  restart; no-op exact bytes; archive guards for every field/create/combined/no-op;
  queue races both orders and injected I/O failure; independent CSV parser, hostile
  formula table, >50/reordered tasks, Unicode/newlines, header-only.
- **Failure/recovery:** wrong failure (syntax/import/setup/timeout) is rejected, repair
  tests before production. On registration changes obtain reviewed candidate revision;
  do not edit adopted authority. The exact accepted red receipt must be consumed by
  `A-I1-implement` admission **before any production edit**.
- **Status:** procedural complete. Three real HTTP assertion failures observed before production:
  404 vs 200/400; evidence/red.txt. New archive, archive-api and CSV tests added. C1 assertions
  live in archive.test.mjs rather than modifying schema.test.mjs; proof unchanged.
  Guarded assertion binding/bootstrap remains parked, not satisfied.

## I1.T3 — Schema and CSV

- **Purpose/design/AC:** C1 owns persistence validation (AC1/AC5); C3 owns serialization (AC4).
- **Entry:** T2 red accepted and consumed by admitted `A-I1-implement`; this and T4/T5
  are ordered internal portions of that single executable action, not fake separate greens.
- **Owned changes:** P `src\schema.mjs` `validate(model)` permits optional strictly boolean
  archived only for v2, leaves defaults absent; new `src\csv.mjs` `csvCell`/`projectCsv`
  implement normative C3 exactly. C1 and C3 each appear in one owning task.
- **Reuse:** schema's existing object/field validation; existing `taskView` semantics for
  blocked; C3 is pure and sorts a copy, never reads/writes store (research E1/E5/E6).
- **Preserve/exclude:** no schema3, migration redesign, store edits or new dependency.
  Maintain unknown-field strictness, absent-v2 bytes, v1 read-only and exact backup contract.
  CSV headers/order/CRLF/no-BOM/quoting/formula guard are precisely those in C3; no locale
  formatting, client pagination, destructive sanitization, or data truncation.
- **Proof:** targeted real native schema/CSV tests during the action; accepted final proof
  is `C-I1-green`. Raw targeted runs are diagnostics, not substitute receipts.
- **Failure/recovery:** root-cause incorrect shape/escaping in this task; any contract
  ambiguity returns to design. Test data only; revert candidate code, not users' stores.
- **Status:** procedural complete. C1/C3 implemented; targeted 9/9 pass, evidence/backend-green.txt.

## I1.T4 — Domain and HTTP

- **Purpose/design/AC:** C2 owns lifecycle/write policy; C4 owns HTTP transport; AC1–AC5.
- **Entry:** C1/C3 available in the same admitted implementation action.
- **Owned changes:** P `src\planner.mjs` new `projectView`, `assertProjectWritable`,
  `getProject`, `setProjectArchived`, `exportProjectCsv`; changed `listProjects`,
  response-only normalization in `createProject`, guards in `createTask`/`updateTask`.
  P `src\server.mjs` `createServer`/route dispatch uses strict project detail/PATCH/CSV,
  archived query/root allowlist and exact download/security headers.
- **Reuse:** `JsonStore.read/transact`, `findProject/findTask`, existing schema/error/rules,
  server parseQuery/expectedRevision/body/json/send (research E1/E2/E3/E6).
- **Preserve/exclude:** guards inside queue before allocation/mutation; migration then
  stale-revision precedence; idempotent effective-false restore; dependency and transition
  validation; no disk publication after failed persist; global totals inclusive; canonical
  safe project IDs/filename; HTTP errors stay JSON. No store/rules implementation edits.
- **Proof:** native archive/schema/CSV/API plus old API/query/rules/store/migration/lifecycle
  regressions. Assert bytes/revision/IDs/task/dependency records before, after, and reopened.
  Test stale/same-revision/fresh races, error precedence, current no-op writes rejected
  on archives, restore reenables only valid writes, strict queries/methods/headers/security.
- **Failure/recovery:** schema/domain failure blocks UI claims; isolate actual failure,
  preserve evidence and repair earliest task. New archived v2 snapshots are not promised
  readable by old binaries; never “rollback” by deleting archived tasks/fields from user data.
  Existing offline v1 recovery remains explicit and potentially lossy as documented.
- **Status:** procedural complete. C2/C4 implemented; full native 46/46 pass, evidence/coverage.txt.

## I1.T5 — Browser and documentation

- **Purpose/design/AC:** C5, AC2–AC5 plus browser AC1 lifecycle.
- **Entry:** C4 routes correct; parent remains implementer; no concurrent shared-file edits.
- **Owned changes:** P `public\app.mjs` reload/render/navigate/edit/request/save, new
  downloadCsv/syncWriteControls; `public\index.html` navigation/control semantics as needed.
  P `scripts\e2e.mjs`: add planned `archive` flow to accepted enumeration, `all` dispatch,
  and scenarios; P `README.md`: routes/schema/CSV/global-count/recovery/flow documentation.
  Existing `styles.css` is reuse only; no style changes planned.
- **Reuse/preserve:** existing textContent DOM, labels, status/alert, 44px primary targets,
  visible focus, 719px breakpoint, URL reset rules and owned agent-browser harness.
  Independent state.project; atomic coherent response publication; sequence guard for
  obsolete success AND failure; editor-captured revision; stale/uncertain write fence.
  Read controls/Cancel/reload stay usable; no silent draft replay; lifecycle focus;
  separate download busy/error path and object URL cleanup. Follow full C5/UX contracts.
- **Proof:** `C-I1-browser` by fresh verifier at T6, not the UI author. Real active→archive→
  restart→deep link→download→restore→edit; two-client stale draft; mismatch/obsolete load;
  post-commit read failure; empty states; filtered/paginated/back navigation; legacy export;
  hostile actual downloaded bytes; error creates no download; 390/1280 keyboard/axe/contrast.
  Negative network timing may use controlled HTTP faults, but archive/restore/download
  success must hit real app/storage, not mocked implementation.
- **Failure/recovery:** no success announcement before coherent reload; keep rejected
  draft. Verification failures return to owning C5/C4 task; re-run affected and final proofs.
  If browser evidence adds tests after green, rerun green on the final exact source snapshot.
- **Status:** C5 and README implemented. Independent verifier added archive flow/all dispatch
  and observed real lifecycle/read-only/restart/stale-draft/filter/accessibility checks.
  Actual download file proof remains blocked after the bounded transport follow-up.
  All-flow regression ran (187 passing records, exit1) and final review completed.
  Review fixes: explicit Python prerequisite, draft/lifecycle guidance and non-racing timeout
  ownership. Independent targeted base-flow validation passed67 checks (six added);
  missing interpreter configuration failed before fixture creation. Full final-byte review
  unavailable because the same synchronous reviewer cannot resume; delta preserved for parent.
  See evidence/review-fixes-verification.md and evidence/post-review.patch.

## I1.T6 — Integrated proof and closure

- **Entry:** integrated C1–C5 edits complete on one frozen source snapshot; parent self-review.
  Native, browser, metric and independent review records remain different kinds of proof.
- **C-I1-green / A-I1-green:** `commands.green`, direct native full inventory, existing nine
  plus new archive/archive-api/CSV suites. Expected relevant leaf tests >0, all pass,
  none skipped/cancelled, captured complete native result and accepted receipt.
  This is unit + real-file/HTTP/process integration, not browser proof.
- **Coverage diagnostic:** `commands.coverage` enables existing Node coverage on src;
  keep actual uncovered branches visible. Required changed-line coverage floor **80%** and
  mutation floor **60%** are metric policy requirements, not inferred from exit status.
  New archive/restore/guard/escaping/error branches require meaningful assertions.
  Browser code needs actual browser scenarios; native coverage cannot certify it.
  No configured app lint/type/build exists; N/A, not a claimed pass.
  This command is diagnostic, **not registered guarded native proof**: current
  `validate_command` rejects any wildcard argument alongside `--test`, including the
  established coverage-include glob. Do not force it through adoption or remove coverage
  scope merely to satisfy the validator. Full native green uses explicit files without globs.
- **C-I1-browser / A-I1-browser:** null-command **verification** check, independent verifier.
  Run `commands.browser_all` (existing all flow extended by T5), with optional
  `commands.browser_archive` only after its allowlist exists. These run the existing
  harness's agent-browser actions; Playwright launches/cleans up only.
  Capture per-AC findings, screenshots, console/network errors, downloads, disk equality,
  exact hashes and process ownership/cleanup. No automatic producer from a null command.
- **C-I1-metrics / A-I1-metrics:** null-command metrics collection handoff to parent.
  All nine REQUIRED schema names: `duplication_pct`, `complexity_max`, `complexity_avg`,
  `cycles`, `dead_exports`, `static_findings`, `mutation_score_pct`, `diff_coverage_pct`,
  `architecture_rules`. Both complexity fields count separately in the strict nine.
  Diff size is additionally reviewed, not a replacement metric. Nonregression,
  zero new cycles, mutation ≥60%, diff coverage ≥80%; stricter actual policy wins.
  Complete source scope/baseline/strict producer binding required. No collector/bridge
  modifications in this task. Missing collectors/bridge => **BLOCKED**, never hand-authored
  green metric JSON or an accepted receipt. Diagnostic probe commands require separately
  checked public help before use; none are registered as a qualified producer here.
- **C-I1-review / A-I1-review:** null-command review check, independent fresh reviewer.
  Depends on accepted native and browser proof, **not** metric acceptance so useful review
  remains runnable while metrics are blocked. Supply actual metrics-unavailable evidence.
  Review exact diff/design/plan/tests for correctness, maintainability, security/performance,
  scope and metric gaming; independently reconcile every AC; real findings and parent
  dispositions only. Report unresolved measurement honestly. For changes, reopen earliest
  task and affected proof; no automatic approval or cherry-picked scenario results.
- **Closure:** increment requires native green + independent browser + all metrics +
  independent review. These and actual feature-branch committed source are prerequisites
  of ordinary close. Neither a review pass nor local commit repairs missing metrics.
  Current assignment forbids commits/push; any later local preservation is parent-owned
  and must not be called I1 complete. Release/deployment N/A.
- **Status:** independently verified/reviewed with limits, NOT CLOSED. Final native 46/46;
  browser saved-download proof blocked, nine qualified metrics unavailable. Existing approved
  app mutation sample 28/30 is diagnostic only. See review.md, traceability.md and report.html.
  Parent may preserve a scoped local checkpoint, never label it a passed I1/G6 ship gate.

## Preparation and adoption

Files:

- `design-history\r1.preparation.json`: typed preparation envelope, exact source/input
  hashes, complete check commands, component hashes, unset real-identity/executable/red
  slots. **Not a WorkflowContract or a receipt.**
- `design-history\r1.html`: retained design bytes, unchanged from rendered design.
  Its relative presentation links retain the original `design.html` base location; view the
  original design for the already measured rendering. Do not claim that opening the retained
  copy from a different directory re-proves link/theme rendering. Making the retained copy
  independently browsable would change bytes and requires refreshed candidate binding/review.
- `design-history\r1.review.pending.json`: exact original independent report reference,
  separate state disposition and unattended authorization references; pending ownership/
  workflow binding. **Not approved DesignReview metadata; not an adoption argument.**
- `prepare_candidates.py`: artifact-only builder/validator. Its default inspection
  reports missing inputs without writing anything. It never executes registered commands,
  adopts, writes runtime authority/ledger/receipts, edits app files, or fills missing approval.
  Strict candidates are deliberately **not emitted** until genuine fields exist; placeholder
  JSON with invented identities or invalid work commands is not an ordinary-adopt candidate.

Read-only validation / current expected blocker:

```powershell
& $py -B scripts\run.py --idle 30 --max 60 -- $py -B .ai\planner-live-workflow\prepare_candidates.py --inspect
```

Parent follow-up, in order:

1. Resolve null-work capability and test-bootstrap limitation. A possible authorized
   bootstrap is **only** the new `test\archive-api.test.mjs` red suite before adoption:
   retain unchanged production and all nine original suites, bind those real red bytes,
   then let baseline run the original nine and `A-I1-tests` author remaining tests.
   Do not modify `schema.test.mjs` before that baseline. Actual native behavioral-red
   acceptance/admission must still precede production. This is a parent decision, not
   permission from this artifact-only assignment; the null-work blocker remains.
2. Supply a task-local JSON bindings file (e.g. `design-history\r1.bindings.json`) containing
   `roles` for `parent`, `researcher`, `design_reviewer`, `verifier`, `reviewer`; each is an
   actual existing-schema producer record (`actor_id`, `context_id`, `role`, `host`, `model`).
   Record actual model/host, not a preferred or imagined model. `parent.role=implementer`,
   researcher/reviewer/verifier roles match purpose; all five contexts distinct.
   `work_commands` maps `A-I1-tests`, `A-I1-implement` to genuine Command records;
   `red_assertions` is a nonempty list of exact schema assertions from real test bytes.
   The script has no capability to prove a purported command actually performs editing:
   parent/reviewer must inspect it; do not substitute a status marker.
3. Run preparer with `--bindings <path> --stage`. It validates actual strict schemas,
   assertion file/line/hash bindings, exact input snapshot and dependencies; writes only
   retained `r1.workflow.json`, `r1.current-design.json` and
   `evidence\review-r1.json`. Review stays **REVISE** and binds the unchanged original
   report, exact parent state dispositions and separate clarification authorization.
   It refuses to overwrite different staged bytes or any live/adopted authority.
   This is candidate preparation, not adoption readiness.

   ```powershell
   & $py -B scripts\run.py --idle 30 --max 60 -- $py -B .ai\planner-live-workflow\prepare_candidates.py --bindings .ai\planner-live-workflow\design-history\r1.bindings.json --inspect
   & $py -B scripts\run.py --idle 30 --max 60 -- $py -B .ai\planner-live-workflow\prepare_candidates.py --bindings .ai\planner-live-workflow\design-history\r1.bindings.json --stage
   ```
4. Hand those exact bytes, component hashes, research, original review, parent disposition,
   rendered-document evidence, UX and plan to the actual independent design reviewer for
   the bounded follow-up. It must assess this newly bound workflow as well as DR1/DR2.
   Reviewer authors a new immutable report and real APPROVE/REVISE/REJECT metadata against
   the exact canonical workflow/document/components. Parent records real disposition
   separately and supplies authorization without changing human status to confirmed.
   The preparer **never produces APPROVE**. Do not replace the original report.
5. After genuine APPROVE, update the *staged* pointer's review and review metadata identically
   using canonical sorted compact UTF-8 JSON + LF, preserving all reviewed candidate hashes.
   Recheck source/input hashes and parent Gate 3 consumer acceptance. If anything material
   changes, reviewer must review the changed candidate; no rehashing old approval.
6. Only the parent may then run ordinary adoption, followed by first status/next:

```powershell
& $py -B scripts\run.py --idle 120 --max 600 -- $py -B scripts\workflow.py adopt --slug $slug --repo $repo --revision r1 --review .ai\planner-live-workflow\evidence\review-r1.json
& $py -B scripts\run.py --idle 120 --max 600 -- $py -B scripts\workflow.py status --slug $slug --repo $repo --target action:A-I1-baseline
& $py -B scripts\run.py --idle 120 --max 600 -- $py -B scripts\workflow.py next --slug $slug --repo $repo --action A-I1-baseline
```

`validate_design_binding` requires genuine adoption history and cannot positively validate
a first-adoption basis against an empty ledger. Do not create a synthetic adoption event
to satisfy it. Preflight strict shape/hash checks do not replace ordinary adopt's validation.
Existing procedural research is not a guarded research receipt; no accepted claim IDs are
invented. The preparer retains researcher attribution as provenance, leaves `claims={}`,
and parent accepts/reconciles research procedurally per public workflow docs.

## Consumer readiness checklist

- [ ] Resolve actual editing route and red-test bootstrap; complete bindings from real evidence.
- [ ] Parent walks T1 and the red→implementation failure boundary using only these artifacts.
- [ ] Parent reconciles all C1–C5 ownership and AC1–AC5 tests; source remains in exact inventory.
- [ ] Parent measures plan overview ≤3 printed pages and confirms theme/links.
- [ ] Actual independent candidate-specific review closes dispositions without fabricated approval.
- [ ] Ordinary adoption succeeds; actual status admits only registered next action.
- [ ] T1–T6 results attached before completion claims; metrics blocker remains explicit.

**Consumer verdict: BLOCKED for guarded execution.** The implementation plan is scoped;
unresolved execution capability, future red bytes, producer attribution and candidate review
are explicit prerequisites, not undocumented assumptions. Missing metrics blocks closure,
not independent useful verification/review once execution prerequisites are genuinely resolved.

## Planner validation performed

2026-09-18, supplied uv Python through `scripts\run.py --idle 30 --max 60`:

- `prepare_candidates.py --initialize`: exit 0; artifact-only preparation retained.
- `prepare_candidates.py --inspect`: expected exit **2**, explicitly missing genuine
  producers, executable work commands and real red assertions. No adoption attempted.
- Python AST/import and read-only artifact validation: pass. Forty exact app input paths
  (36 existing files plus three planned suites and one planned CSV module); nine baseline
  suites, three new suites; all 18 HTML file links resolve. Retained design/review/
  disposition/authorization hashes match, pending JSON serialization is canonical.
- In-memory **synthetic schema-shape exercise only**, no candidate/receipt persistence:
  proposed eight-action/six-check graph satisfies structural validators when hypothetical
  required fields are supplied; null work and empty red assertions are correctly rejected.
  Synthetic records were discarded, never used for actual attribution or approval.
- App/runtime/source diff remained empty. No app tests, browser verification, metric
  collection, strict candidate approval, live authority, ledger, receipt, commit or push
  was produced. Plan page count and semantic approval remain parent checks, not these
  static validation results.

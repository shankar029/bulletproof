# Requirement traceability — independent final reconciliation

2026-09-18. **Independent review snapshot**: base/HEAD `c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`, with the then-current
uncommitted app diff and all four new app files included. Current source hashes
and independent findings are in [review.md](review.md).
All verdicts are **UNADOPTED PROCEDURAL / unbound evidence, not receipts or
quality closure**. Human approval remains unconfirmed; coordinator explicitly
authorized this procedural continuation. Guarded candidates remain parked.

`P` below means `examples\team-planner`. Line references below identify the independently
reviewed snapshot, not the subsequent final guidance/config/timeout delta. The parent
addendum at the end records that change without rewriting the original verdicts.

| AC | Requirement and design/tasks | Current implementation and real tests | Inspected executable evidence / remaining limits | Verdict |
|---|---|---|---|---|
| AC1 | Lossless archive/restore at any task status, preserving IDs, data, dependencies and restart durability. C1/C2/C4/C5; I1.T2-T6. | P `src/schema.mjs:46-50`; `src/planner.mjs:55-64` (`setProjectArchived`); unchanged `src/store.mjs:73-95` transaction. P `test/archive.test.mjs:12,57,119` mixed graph/restart/queue/failure/empty/no-op tests; `test/archive-api.test.mjs:21` mixed-status HTTP lifecycle. | Independent native 46/46 pass. Actual browser cancel/accept, mixed todo/in_progress/done/blocked project, exact tasks/nextId/revision/target-flag equality, restart, restore/edit/second restart and empty archive assertions pass. Full all-flow report cited below; no power-loss guarantee beyond existing documented process-crash boundary. | **VERIFIED** |
| AC2 | Default active list excludes archives; explicit archives and independent readable deep links. C2/C4/C5 and UX routes; I1.T2,T4-T6. | P `src/planner.mjs:40-50` list/detail separation; `src/server.mjs:62-104` strict routes/queries; `public/app.mjs:185-219,281-322` independent selected detail; `public/index.html:11`. P `test/archive-api.test.mjs:21,44` and `test/archive.test.mjs:119`. | Native partition/detail/invalid queries and IDs pass. Browser actual sidebar ID partitions, selected archived detail with active sidebar, Back, direct default-selector link after restart, mixed-status badges and empty archived view pass. Not merely source inference from sidebar filtering. | **VERIFIED** |
| AC3 | Server/UI reject archived create/edit/status writes; restore reenables legitimate writes; preserve concurrency and dependencies. C2/C4/C5; I1.T2,T4-T6. | P `src/planner.mjs:28-31,79-114` shared transactional guard; `public/app.mjs:41-53,79-146` policy sync, captured draft revision, failure fence; `reload:281-332` coherent revision publication. P `test/archive.test.mjs:12,57` rejects all mutable fields/create/combined/no-op, exercises both queue orders, restores and retains graph validation. | Native pass plus eight real current-revision HTTP rejections with byte-identical disk, disabled Add/Edit, real restored edit/dependency rejection, two browser clients retaining/fencing stale draft, Cancel/reload and post-save read failure pass. Successful download during stale editing is still unverified. R4: lifecycle disables while editing but omits C5's required finish/cancel guidance; protection itself is not bypassed. | **VERIFIED-WITH-LIMITATIONS** |
| AC4 | Deterministic UTF-8 full-project CSV, IDs/visible data, commas/quotes/Unicode/multiline, formula prevention, downloadable active and archived. C3/C2/C4/C5; I1.T2-T6. | P `src/csv.mjs:3-16`; `src/planner.mjs:51-54`; `src/server.mjs:87-93`; `public/app.mjs:148-174`. P `test/csv.test.mjs:28,44` independent parser/prefix matrix/order/fields; `test/archive-api.test.mjs:71` >50 rows/headers/active-archive bytes; `test/archive.test.mjs:91` legacy export/no rewrite. | Native serializer and real HTTP assertions pass. **No browser-saved file**: pinned download and direct-HTTP control canceled; later documented global path plus ordinary click observed no file for 12s. Latest all-flow has one failed legacy download and four explicitly blocked dependent active/archive/stale/empty scenarios. No passing browser-byte comparison or download positive control. Failure/no-file observations do not replace success proof. | **BLOCKED** |
| AC5 | Preserve filters/paging/accessibility/storage durability, old formats and recovery. C1/C2/C4/C5/UX; I1.T1-T6. | P `src/schema.mjs:46-50,67-95` optional-v2 and unchanged legacy conversion; unchanged store/rules; `public/app.mjs:176-182,185-278,281-342` URL/read/coherence/focus behavior. P `test/archive.test.mjs:57,91`; existing API/query/rules/store/schema/lifecycle/migration suites remain included. | 46/46 native; actual all-flow base61/graph20/query30 passing records; migration15 and archive61 non-download records pass despite failed flows. Includes exact legacy backup/no-op/migration/edit/restart, AND filters/page/Back, 390/1280 geometry/labels/targets, axe zero violations/incomplete, focus, mismatch and post-save faults. Pure keyboard Archive native-confirm activation, separately delayed obsolete-success/failure races, dedicated >50 browser dependency choices and human accessibility review remain unverified. Legacy saved download remains blocked. No all-green final browser suite is claimed. | **VERIFIED-WITH-LIMITATIONS** |

## Evidence identity and corrected final-run status

- `evidence/baseline.txt`: **37 passed**, zero failures/skips/cancellations.
- `evidence/red.txt`: **three actual native assertion failures** before code,
  HTTP404 versus expected200/400; not missing imports or setup failure.
- `evidence/coverage.txt` and `evidence/independent-native-coverage.txt`:
  **46 passed**, zero failures/skips/cancellations; backend line/branch/function
  **99.40/97.56/97.03%**. Not frontend or changed-line coverage.
- Latest full run:
  `evidence/e2e-2026-09-18T08-44-16-260Z-61878553/report.json`,
  `evidence/download-remedy-all.txt`, `evidence/download-remedy-summary.json`.
  **187 passing named check records / 26 screenshot files / five failed or
  blocked download scenarios / overall FAILED, exit1**. “All-flow not run” in
  earlier records is superseded, not a current claim.
- That run used experimental runner hash
  `b54723ab1a87ba40c8f79e8b6a9bc42a276816af9550a965fa4ac1d4065d1926`,
  retained in `evidence/download-remedy-attempted-e2e.mjs`. The current app
  harness was restored to
  `c9073559d53d4ed5dd1f9bd5150db9de6f56632c24206d33206080c2dd773671`.
  Direct review confirms only download transport/negative observation/attach
  differences, not removed base/graph/query or lifecycle assertions.
  All 12 current production hashes match the final and preceding verifier.
  Current-harness final archive evidence:
  `evidence/e2e-2026-09-18T08-33-33-762Z-b1570d0c/report.json` (62 passing
  records, four failed/blocked downloads). No all-green exact-final-harness run.
- `evidence/verification.md` documents actual trials, hypotheses, cleanup and
  limitations. This reviewer reran no browser trials or fixture-writing suites;
  read-only current syntax and diff checks passed.

## Plan and quality reconciliation

T1/T2 have baseline/red proof; T3/T4 have native implementation evidence.
The recorded schema-test relocation to `archive.test.mjs` preserves scope and
existing tests. T5 has implemented controls and substantial browser proof,
but the small C5 guidance omission (review R4) and downloads remain open.
T6 review is now performed; **T6/I1 closure is not complete**.

The current review additionally records harness portability R3 and evidence
limitations: a timed-out download wait is not conclusive absence of an event;
the retained helper has competing timeout owners; no successful saved-file
positive control exists. These are not invented production download causes.
No high-confidence lifecycle/data-loss/CSV serialization defect was found.
R4 is a low-severity production UX fix, not a reason to patch download behavior.

`evidence/mutation-sample-summary.json` is a **bounded backend sample**, with
30 selected mutations, 28 killed, two surviving existing capacity guards and
zero ungraded. Schema validation still rejects oversized candidates, but
message/error-precedence equivalence is not established. This is neither
full changed-line mutation testing nor the required qualified mutation metric.

`metrics.json` is absent. `evidence/measurement-status.json` is an **agent note,
not producer output**. The root-wide probe was not launched because its
collection/materialization scope was prohibited by the coordinator. All nine
required metrics remain unavailable: duplication, maximum/average complexity,
cycles, dead exports, static findings, mutation score, diff coverage and
architecture rules. No numeric quality score or exemption is substituted.

All ACs still require final independent review and the required quality proof
for closure. This document supplies review reconciliation, not guarded
C-I1-* acceptance. No live workflow/pointer/ledger/lock exists, no human approval
is claimed, and no fake authority, receipts or metrics are requested.

**Overall verdict: BLOCKED.** Functional progress does not waive AC4's
browser proof blocker or G6's unavailable measurements. An environment-only cause is not established.

## Parent final-delta addendum

R3/R4 and the timeout-owner race were corrected after the independent full review.
One targeted independent base run passed67 named checks, including six new guidance
assertions; the missing-interpreter invocation failed before fixture creation.
See `evidence/review-fixes-verification.md`. Normal command exits were observed; no
forced-deadline stress or new download trial. Later label-only harness wording is
hash-bound separately and not represented as an executed new source hash.

The full reviewer could not resume because it was a synchronous agent. No replacement
broad review was spawned; **no final independent approval is claimed**. Coordinator
reconciliation uses `evidence/post-review.patch`, `post-review-binding.json` and current
source hashes. Original AC verdicts remain: AC1/2 verified, AC3/5 limited, AC4 blocked.
The guidance omission is now fixed with targeted proof; original review text above is
historical rather than a claim it is still missing. G5/G6/I1 remain unclosed.

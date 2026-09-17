# Workflow reliability improvements

## Current state
- Requirement: implement the prioritized recommendations from the 29-feature evaluation.
- Tier: full workflow; executable tooling and workflow contracts change.
- Base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- Branch: `shbs-microsoft-workflow-app-verification` (existing task branch).
- Phase: C2a independently verified/reviewed; preserving before C2 CLI implementation.
- Human design approval: unconfirmed; proceeding under the session's explicit autopilot policy.
- Publication: previously blocked by GitHub 403 / Enterprise Managed User policy. Do not retry or bypass without authorized access changing.
- Scope: repository `scripts`, relevant workflow references/canonical skill entry point, and native regression/evaluation tests. Preserve the completed planner case study as historical evidence.

## Acceptance criteria
1. **AC01 / P0:** ESM and CJS changes reach discovery, supported mutation operators and the correct native test execution path; genuine behavioral outcomes are distinguished from setup errors.
2. **AC02 / P0:** Metric reports distinguish measured regression status from required-measurement completeness. Unsupported/unavailable required proof cannot produce a misleading overall pass. Update consumers and documentation together.
3. **AC03 / P0:** Increment readiness uses durable evidence bound to source/contracts, due checks and distinct producer roles/contexts. Missing, stale or mismatched evidence blocks a guarded next transition.
4. **AC04 / P0:** Provide a real guarded execution entry point using the repository's existing process conventions. State its trust boundary: it controls commands routed through it, not arbitrary agent/tool access or authenticated identity.
5. **AC05 / P1:** Verify fresh-context resume after prerequisite changes using artifacts alone, preserving unaffected evidence and identifying/reopening affected work.
6. **AC06 / P1:** Add behavioral workflow failure evaluations for absent review, setup-as-red, stale evidence, unavailable required metrics and premature compatibility retirement. Include a genuinely held-out diagnosis exercise, without presenting fixed fixtures as live-model effectiveness proof.
7. **AC07 / P1:** Keep historical design records and an explicit current contract; bind migration retirement to earlier compatibility evidence and wire the canonical workflow triggers.
8. **AC08 / P2:** Strengthen scoped research claims and explicit supersession of corrected claims; derive communication status from authoritative readiness rather than separate optimistic summaries.
9. **AC09:** Preserve existing native/evaluation behavior except explicitly documented metric/guard outcome changes. Independently verify and review each increment before proceeding; retain conservative unavailable results and exact replay commands.
10. **AC10:** Refresh the README with an attractive, navigable overview of all main agent/skill features, accurate installation and limits, and linked user/operator guides. Distinguish executable tooling from procedural instructions and host capabilities.

## Planned priority order
- Research and reviewed design for the full scope; separate fresh-context planning.
- Increment 1: P0 ESM support and metric outcome semantics.
- Increment 2: P0 guarded evidence transitions and P1 resume/failure evaluations.
- Increment 3: remaining P1/P2 contract, research and communication integration; final regressions.
- Actual increments and executable checks will be fixed by the accepted design and plan.

## Decisions and exclusions
- No new framework, dependency or factory merely for orchestration.
- No claim that self-declared producer IDs establish authenticated independence.
- No claim that a workflow CLI can prevent actions outside that CLI.
- No rewrite of the successful code-clarity guidance or benchmark threshold weakening.
- No repeated uncoached model-effectiveness study claimed by deterministic tests.

## Next action
Preserve the approved C2a process-lifecycle observer, then implement the remaining
C2 CLI component. Do not treat the observer seam as the six-verb CLI.
The local I1 preservation commit is `aaec9b9`.
The continuation addendum replaces implementation-dispatch dependencies only; it does not
close I1.T4 or remove any required measurement, independent role or final acceptance check.

## Latest bounded correction handoff
- FACT: `evidence/q1-attr-result.md` reports the minimal Git-native all-attributes census
  correction and 27 focused passing methods. The prior four-method red run is preserved.
  Literal drivers named `unset`/`unspecified` now reject; absent/reset attributes remain
  accepted. Ambiguous present declarations, including `-filter` and `-text`, are explicitly
  unsupported. No execution escape was observed before or after the correction.
- FACT: final `measure.py` SHA-256 is
  `5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084`;
  the owner reports 465 final pins unchanged. This is local evidence, not acceptance.
- Independent verifier `708c4d0b-2afb-4528-b119-97583eb8251b` owns the focused correction
  replay plus integrated C1 against these shared dependencies. Separate narrowed re-review
  follows. Prior 74-method Q1 and 93-method C1 results remain historical, not new-byte proof.
- This closes only the existing bounded correction attempt, not a new broad convergence
  cycle. C2/Q2, combined preservation and overall release acceptance remain gated.
- FACT: `evidence/q1-attr-independent-report.md` returns VERIFIED-WITH-LIMITATIONS:
  28 focused +83 workflow +10 evidence methods passed once, with no failures/errors/skips/
  timeouts. The verifier added one real `-text` rejection / `!text` reset test. Two evidence
  helper issues were recovered without rerunning tests or changing production. All 4,778
  final pins matched; the four disclosed parent document edits were outside those pins.
- FACT: parent prospective source composition (`evidence/c1-q1-composition-result.json`)
  matches 31 candidate source/reference files byte-for-byte, including all 13 independently
  observed script imports. The private index was removed; the real index was unchanged.
  This is a byte/composition check, not an additional test run or full quality proof.
- Separate reviewer `9a253936-ce4f-4e86-89be-a19ac9f6c7d5` owns final narrowed gate/proof
  re-review plus the directly related quality-reference changes. No production writers
  are active. Combined preservation awaits this verdict.
- FACT: final narrowed review is APPROVE (`evidence/q1-attr-code-review.md`), including
  the quality-reference delta. Three direct reviewer tests passed; these repeat existing
  tests and are not added to the independent 121-method count.
- FACT: reviewer later observed 4,776/4,778 verifier pins matching. The two changed pins
  are parent-regenerated `report.pdf` and `report-rendering.json`, explicitly disclosed
  and reconciled by the reviewer without reopening code acceptance. Historical unchanged
  verification remains historical; no unconditional later 4,778-unchanged claim is made.
- Parent accepts combined C1/Q1 functional preservation with the source-composition proof.
  Actual complete quality, C2-C4, Q2-Q5, human approval and publication remain open. This
  is a partial local preservation boundary, not a green release or completed request.
- FACT: combined source, approved documentation, contracts and owned historical/final
  evidence are preserved in `5dabb4ca27a440ad370fbcb1be1739ed52e38ab7`. Before commit,
  the real staged scripts/reference matched the prospective source tree exactly; afterward
  the index was empty. Only the earlier parent-generated `evals/report.md` date delta
  remained outside the commit. No publication attempt occurred.
- C2 is split at its already-approved first component to avoid repeating oversized C1/Q1
  execution: C2a owns only the backward-compatible `run_capture(..., observe=None)` seam,
  actual lifecycle events, callback-failure behavior and focused runner tests. Existing
  design-contracts ProcessObservation and C2 plan remain authoritative. CLI/ledger recovery,
  paired failure evaluations and operator guide follow after this sub-slice's independent
  verification/review. This grouping introduces no new API or weakened quality gate.
- FACT: C2a owner returned `evidence/c2a-handoff.md`: 16 runner tests (5 existing,
  11 added) and 3 real caller smoke methods pass locally. The two preserved pre-change
  failures are missing-API errors, not mutation kills. Only runner/tests and owned
  C2a evidence changed; no CLI or complete C2 claim follows.
- The frozen runner hash is
  `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e`.
  Its default tuple is retained; callback errors produce explicit observer-error/125.
  Direct exit is not descendant-death proof; creation identity remains null.
- Parent corrects a numerical wording error in its dispatch and the owner handoff:
  ProcessObservation has eight named fields, not nine. The approved schema and actual
  implementation agree; no ninth field is required or authorized. Historical raw
  handoff remains unchanged and this correction is explicit.
- Fresh verifier `c2977ee2-3897-421b-a643-d94152feca52` owns bounded C2a independent
  behavior/caller replay. Source changes reopen affected runner dependency proof;
  C1/Q1's historical 121-method result is not relabeled as new-byte verification.
- FACT: `evidence/c2a-independent-report.md` returns VERIFIED on bounded Windows C2a.
  There are 51 distinct passing methods: runner16, callers3, probe19, evidence10,
  and three additional boundary tests. One initial verifier audit-payload assertion
  failed; only that test was corrected and its three-test batch replayed. This is
  not a single clean aggregate or a production correction; failed evidence is retained.
- The verifier directly observed descendant survival after direct-exit callback failure,
  then cleaned up its owned processes; no descendant-termination guarantee is claimed.
  Callback time is outside capture monitoring and timeout/observer diagnostics compose.
  All 22 owner pins remain unchanged; the final 35-pin bounded scope is reconciled.
- Read-only reviewer `0cac6ce2-9ce5-4536-8a4f-448d65086b0d` owns separate C2a review.
  No production writer is active. CLI/recovery, broader quality and later ACs remain open.
- FACT: separate C2a review is APPROVE for partial functional preservation
  (`evidence/c2a-code-review.md`). The reviewer independently matched all three
  source/test hashes, 22 owner pins, 35 final-input pins and 10 artifact pins.
  AC04 is accepted only for the observer seam; AC05 recovery/resume and overall
  AC09 quality remain open. Parent accepts preservation before remaining C2 work.

## Continuation acceptance - 17 September 2026
- User requested completion plus an attractive README and updated guides. When asked about
  the missing-prerequisite planning dead end, the user authorized autonomous decisions while
  unavailable. Human design approval remains unconfirmed.
- Parent accepts the independently reviewed scheduling addendum: implement state/gate,
  independently verify/review, then CLI/lifecycle, canonical integration and actual host
  exercises. AC10 documentation drafts may proceed in parallel on disjoint files.
- The original plan required unscheduled mixed-language collectors before any subsequent
  implementation. `evidence/continuation-measurement-research.md` identifies that missing
  prerequisite; it does not establish a technical dependency on the guard.
- Required quality collection is separate release prerequisite Q, not waived or passed.
  No retrospective guard admissions, imported green scores, fabricated independent approval
  or publication retry is authorized. Original design/task/evidence history stays intact.
- Parent rechecked accepted r2 interfaces and the C1 boundary. No production code changed
  since the reviewed preservation commit; continuation research/plan are additive artifacts.
- C1 implementer found that the original pure gate lacked resolved receipt bodies and
  per-prerequisite current snapshots. Parent accepted the independently reviewed
  `guard-resolution-contract.json` clarification; persisted schemas remain unchanged.
- Existing-feature README, banner, user/install/architecture/contributor guidance preserved
  in `015d353`. Documentation review findings were corrected; local light/dark desktop/mobile
  rendering and link evidence is under `evidence/documentation-*`. Guard additions await C2.
- Q design revision 2 independently accepted (`evidence/measurement-design-review-r2.md`).
  Parent adopts the explicit new 100% changed executable-line and decision-outcome policy
  for its declared finite models, retaining mutation 60% and evaluation 0.9. This is an
  autonomous decision, not historical policy or confirmed human approval.
- Q1 inventory/Python graph/architecture implementation may run disjointly from C1.
  Q2 tool qualification, Q3 coverage, Q4 classified mixed-language mutation and final Q5
  proof remain required. No broad final measurement while concurrent writers are active.
- C1 implementation returned 52 local core tests plus 10 evidence tests passing, but observed
  concurrent probe dependency changes; final dependency freshness is explicitly reopened.
  Fresh verifier `a02590d4-37a7-4531-ae44-21f0e15cfed3` owns independent acceptance proof.
- Q1 required an explicit owned artifact root in its Context; parent accepted `run_root`
  with canonical manifest-root equality and strict paths. The overview initially rendered
  to four pages after dispatch; parent shortened only presentation and confirmed three pages,
  two visible diagrams and no browser errors. This late presentation check is recorded,
  not retroactively claimed as a pre-dispatch observation.
- Independent live-harness packaging correction: original staged bundle lacked scripts/assets.
  Parent restored installer payload parity and equal `.ai/` task-record permission for both
  arms, retaining deliverable/seed boundaries. Native 65/65 and all ten fixed corpus tasks
  passed; live dry-run is plumbing proof only. Integrated independent review remains due.
- C1 independent verification returned NOT-VERIFIED: closure can be backfilled from later
  proof, failed/no-spawn launch can count as executed work, and UTC validation accepts a
  naive datetime. Final workflow discovery: 60 passed / 3 failed; evidence: 10 passed.
  The verifier observed 1,881 pinned files and 171 imported modules unchanged. Parent accepts
  all three as C1 defects and returned correction to the original production owner.
  Preserve `evidence/c1-independent-verification.md` and its failing regression tests;
  C2 remains blocked until correction, independent replay and separate review.
- Another forced compaction occurred during this continuation. Re-anchored state, original
  research/design and continuation plan before changes. This is an execution-sizing issue,
  not the actual fresh-context resume experiment required by AC05.
- Q1 implementation returned 28 measurement tests and 19 legacy probe tests passing.
  Inventory, Python graph/architecture and producer validation are implemented; all nine
  metrics remain required and unsupported/missing collectors remain incomplete/fail.
  Source is frozen for verifier `e2c9aae7-db2e-4de4-a109-04cbbd9861c9`; the implementation
  return alone is not independent acceptance or permission for Q2. C1 owner was notified
  of the final measurement/probe dependency hashes before its correction replay.
- Updated report and traceability to distinguish committed I1/docs from incomplete C1/Q.
  Report initially printed to four pages; condensed without changing verdicts and observed
  three pages with no browser/console errors (`evidence/report-rendering.json`).
- C1 production owner corrected closure chronology, no-spawn execution proof and parsed UTC
  validation. Local corrected run: 70 workflow tests plus 10 evidence tests passing, with
  all original independent tests preserved. Final Q1 dependency hashes matched the actual
  imports. Returned the frozen correction to the original independent verifier for replay;
  local green does not replace the prior NOT-VERIFIED verdict or separate review.
- C1 independent r2 verified the original F2/F3 fixes but found residual F1: prefix
  validation accepts an older proof while an old closure names a replacement receipt
  accepted later (closure seq32, receipt acceptance seq38). Workflow: 70 passed / 1 failed;
  evidence: 10 passed. Parent accepted the exact-reference defect and returned correction
  iteration 2 to the original implementer. Original/r2 tests and evidence remain untouched.
- Q1 independent verification returned NOT-VERIFIED: builtin `sys` resolves to local
  `sys.py`, fabricating graph/architecture failures; freshly collected evidence accepts
  base/head source hard links sharing mutable bytes. The normal CLI copy path was not
  observed creating this alias. Existing Q1 28 and legacy probe 19 pass; added verification
  4 pass /2 fail. Parent accepted both defects and returned correction to the Q1 owner,
  preserving `evidence/q1-independent-verification.md` and regression tests.
  C1 owner was notified that its measurement dependency freeze has reopened.
- C1 correction iteration 2 binds the exact prefix receipt ID/hash union and preserves
  current freshness/order checks. Local 75 workflow +10 evidence tests pass; four new
  owned cases cover handoff, transitive action, inherited increment and ship reclosure.
  Frozen return is `evidence/c1-correction-r2-report.md`. Original verifier owns r3 replay;
  concurrent Q1 dependency changes must be reconciled before final acceptance.
- C1 independent r3 returned VERIFIED-WITH-LIMITATIONS: 75 workflow plus 10 evidence
  tests pass; all original/residual defects resolved on the bounded tested surfaces.
  The verifier pinned newer actual Q1 bytes and observed 1,878 inputs/172 imports
  unchanged through handoff. Separate read-only reviewer
  `bbe59c68-4708-4952-8f3d-7d91551302dc` now owns C1 and pending live-bundle/portable-hero
  review. This is not C2 authorization, actual quality proof or release acceptance.
- Separate C1 review returned REVISE. R1: receipt-supplied floor/coverage modes can bypass
  mandatory metric regression comparison. R2: failed spawned metric/finding commands can
  authorize direct consumers. R3: prefix closure evaluation duplicates work exponentially
  (12 increments, 4,096 evaluator instances, 7.134 seconds observed). Original F1-F3
  mechanisms were accepted fixed. Parent accepted all new findings and dispatched bounded
  correction iteration 3 with persisted regressions, independent replay and re-review.
  Full return and disposition: `evidence/c1-code-review.md`. C2 remains blocked.
- The same independent reviewer approved the separate bundle/portable-README slice and
  replayed all 21 harness tests. Preserved only that accepted slice plus its evidence in
  local commit `0b7e1a1f6fd1f807bd254886e2877d605596d96d`; no Python runtime/test files
  were included. Index checked empty afterward. Both production owners were notified of
  the changed root HEAD. This is partial preservation, not C1/Q closure or publication.
- Q1 correction returned locally green: 39 measurement tests (including six unchanged
  verifier tests) and 19 legacy probe tests passed. Interpreter builtin/frozen precedence
  and cross-root physical-file identity checks address the two findings; no CLI-copy bug
  is claimed. Original verifier now owns correction replay. 321 pinned inputs and 137
  original verifier files/tests were preserved; `evidence/q1-correction-result.md` records
  exact observations and limits. C1 owner received final frozen dependency hashes.
- C1 correction iteration 3 returned 83 workflow +10 evidence tests passing on the final
  Q1 dependency bytes. Mandatory comparisons, producer outcome/exit qualification and
  per-call prefix memoization address review R1-R3; original verifier owns r4 replay.
  Actual evaluator counts for 3/5/8 increments changed from 8/32/256 to 4/6/9.
  The larger 12-increment timing is still only the reviewer's pre-fix observation.
  Return/freeze/reconciliation are in `evidence/c1-correction-r3-*`; independent replay
  and separate re-review remain required. No further production writers are authorized.
- Q1 independent correction replay verified original F1/F2 but found an effective-mode
  binding defect: documented `PYTHON_FROZEN_MODULES=on/off` changes real native/probe
  resolution while parser/toolset hashes remain identical. Per-run resolution is correct;
  no false overall green or successful forgery was observed. Original Q1 39 and probe19
  pass; new boundaries 1 pass /1 fail. Parent accepted the finding and authorized Q1
  correction round2 in the original owner. C1 verifier was notified of reopened dependency
  freshness. Preserve `evidence/q1-independent-r2-verification.md` and new failing test.
- C1 independent r4 passed all 83 workflow +10 evidence tests and verified review R1-R3
  on its tested snapshot. Final handoff detected the anticipated subsequent Q1 graph
  fingerprint edit, so current-tree verdict is BLOCKED-FRESHNESS, not accepted.
  Preserve `evidence/c1-independent-r4-verification.md`; do not repeatedly replay while
  Q1 writes. Next C1 replay must follow its final freeze, then separate reviewer recheck.
- Q1 round2 source is frozen: `measure_graph.py` hash
  `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061`.
  Local42 Q1 +19 probe tests pass. The effective complete frozen-module census now binds
  environment/CLI precedence, ignored environment and build defaults; private CPython
  API absence fails closed. Original Q1 verifier owns r3; original C1 verifier owns one
  stable r5 freshness replay. Both may write only scoped tests/evidence; no production
  writers authorized. `evidence/q1-correction-r2-result.md` records limits and raw evidence.
- C1 stable r5 replay passed 83 workflow +10 evidence tests with 1,883 relevant file pins,
  172 observed imports and 52 protected historical files unchanged through handoff.
  Actual graph hash matches the final Q1 freeze. The original separate reviewer now owns
  bounded correction re-review; prior BLOCKED-FRESHNESS is resolved for this snapshot,
  not future edits. `evidence/c1-independent-r5-verification.md` preserves exact proof.
- C1 separate correction re-review APPROVE: R1-R3 resolved; 1,883 pins remain unchanged.
  The original 12-increment case now uses 13 evaluators/888 unique uncached pairs and
  took 0.367805s in one observation, versus 4,096/7.133808s before; not a statistical
  speedup claim. Full return and parent acceptance: `evidence/c1-code-review-r2.md`.
  Original verifier is checking only accepted C1 files over committed HEAD in a private
  candidate tree so C1 preservation does not silently depend on uncommitted Q1 modules.
  No additional C1 implementation changes are authorized by this compatibility check.
- Q1 independent r3 accepted F1/F2/F3 with limitations: 42 Q1 +19 probe tests and ten
  actual interpreter-mode controls pass. 322 owner pins/382 historical files unchanged.
  Fresh separate reviewer `1b351703-5886-4edc-8cf8-1058ef536fb2` owns Q1 code review.
  Neither this return nor C1 acceptance closes complete quality or authorizes publication.
- Q1 separate review returned REVISE: Windows directory aliases can hide local edges,
  and a status-clean baseline with assume-unchanged flags can differ from its immutable
  Git tree while fresh graph proof is accepted. Original F1-F3 remain accepted fixed.
  Parent accepted both findings and authorized bounded correction round3 in the Q1 owner;
  original return/reproductions/disposition are preserved in `evidence/q1-code-review.md`.
- C1 standalone composition did NOT pass: committed I1 probe lacks the architecture-rule
  comparison needed by the new guard. All83 methods ran, with two failing architecture
  subtests (floor/coverage); Q1 modules were absent and candidate imports were isolated.
  No evidence-suite retry or production patch followed. The private tree was removed.
  `evidence/c1-standalone-preservation-report.md` preserves the failure. Integrated C1
  acceptance remains valid only for its tested shared-policy dependency, so preserve
  C1 and Q1 together after Q1 acceptance rather than commit a broken C1-only tree.
- Q1 owner reproduced R1/R2 before edits, then stopped at a real representation ambiguity:
  raw Git blobs differ from legitimate versioned-attribute checkout bytes. Parent selected
  a deterministic isolated versioned-attribute checkout policy, with neutral LF defaults,
  no ambient conversion/configuration, no external filters, and explicit platform mode
  projection. Proposal: `baseline-materialization-contract.json`; original reviewer owns
  narrow independent boundary adjudication before implementation. Concrete Git commands
  must be qualified against the installed tool. Human approval remains unconfirmed;
  the choice uses the user's existing explicit autonomous authorization.
- Independent baseline-boundary review APPROVE, with no required revision. Parent accepted
  and authorized actual Git qualification then bounded correction. Full review and original
  proposal hash are in `evidence/baseline-materialization-review.md`; only approval metadata
  changed in the proposal. Expected bytes must match exactly, full relevant/non-code scope
  remains, external filters must never execute, and policy/Git identities must be validated.
- On explicit user continuation, the prior Q1 worker was no longer available and no
  background agents remained. Persisted Git-qualification outputs exist, but no final
  correction return is present. Replacement owner `d29478a1-bb2c-4dde-a19b-f6ebba084b1a`
  is resuming the same approved correction from disk, including any partial edits.
  This is interruption recovery, not another design/convergence round or AC05 experiment.
  No completed qualification or production acceptance is inferred from file presence.
- Resumed Q1 owner returned frozen R1/R2 corrections. Shared canonical paths and isolated
  immutable-tree materialization now have local passing executions for all52 distinct Q1
  methods plus19 probe tests. This is NOT one clean aggregate run: initial timeout and
  two long capture-path errors are preserved; affected cases passed with short unique
  tags. Qualified scope is the observed Git core/69-DLL set, not arbitrary Git builds.
  `evidence/q1-resumed-correction-result.md` and final-freeze/handoff retain exact limits.
- Replacement independent verifier `708c4d0b-2afb-4528-b119-97583eb8251b` now owns
  bounded R1/R2 replay plus existing regression coverage. Prior verifier sessions were
  cleared, not concurrently replaced. Production is frozen; only scoped independent
  tests/evidence may be added. Separate correction review is still required.
- Independent Q1 final verification returned VERIFIED-WITH-LIMITATIONS: three completed
  disjoint batches, 25 graph/inventory +30 integration/boundary +19 probe methods, with
  no failures/errors/skips/timeouts. This is52 original Q1 +3 new independent +19 probe,
  not a single aggregate process. Original/review defects resolved in bounded proof.
  `evidence/q1-final-verification-report.md` and final freeze/handoff retain raw evidence.
- Replacement separate reviewer `9a253936-ce4f-4e86-89be-a19ac9f6c7d5` owns narrowed
  Q1 R1/R2 correction review; prior original reviewer was cleared on restart.
  Parent meanwhile replayed C1 against the final collector source:83 workflow +10 evidence
  tests passed, 12 named runtime/test files unchanged before/after. Logs are PowerShell
  captured text in `evidence/c1-q1-integrated-parent-*`, not a complete binary/import
  attestation or new independent review. Combined preservation still awaits Q1 review.
- Narrowed Q1 review accepts path and original immutable-baseline corrections but found
  one residual policy bug: literal filter drivers named `unset`/`unspecified` collide
  with textual Git attribute states and are admitted. Isolation prevented execution;
  this is not an execution escape, corrupted-baseline acceptance or overall-green proof.
  Full return: `evidence/q1-code-review-final.md`. Parent authorized one bounded
  classification fix with qualified Git-native census and literal-name regressions,
  not a fresh broad convergence cycle. Q2/C2 admission remains held.

## Implementation checkpoint
- Compaction occurred during I1. Re-anchored from state, research, revised design and source;
  this is not the planned fresh-agent resume experiment. The increment was too large for
  one context and must not be represented as an uninterrupted execution.
- Standalone evidence primitives and ten initial tests implemented.
- Probe behavioral red: five existing-behavior tests produced seven assertion failures
  before implementation (`evidence/i1-probe-red.log`).
- First probe run after implementation: 13 tests pass (`evidence/i1-probe-tests.log`);
  additional validation is still pending. Missing-new-API failures were not counted as red.
- Native mutation/reporter lane is owned by a separate implementer. Integrated proof and
  independent verification/review have not happened yet.
- Required unsupported collectors remain an explicit advancement blocker, not an exception
  granted by these functional test passes.
- Integration found and corrected a shared-run-directory collision between probe and mutation.
  The positive real-CLI test now measures a genuine 100% assertion kill while the overall
  report correctly remains incomplete (`evidence/i1-probe-positive-integration.log`).
- Full native/corpus runs exposed a Windows CLI stdout encoding error and a genuine corpus
  threshold failure: csv-stats-cli scored 8/9, below 0.9. Both are under investigation;
  neither run is a pass and the threshold has not been weakened.
- Integrated Python run: 47/47 passed before additional command-binding/freshness checks.
  The added post-publication check then showed parent metrics immediately stale the child
  source hash (`evidence/i1-child-freshness-red.log`). Reopened output-ownership integration:
  exact same-run generated report paths must be excluded, not arbitrary contracts. Recorded
  the clarification in design-contracts.json; independent review must include this delta.
- Actual probe run `66575942a94040d0b4d7c160f4107d5e` exited 1 with
  measurement_status=unavailable, completeness=incomplete and verdict=fail. All nine required
  metrics lacked complete proof; diff coverage and architecture have no implemented
  collector. This observation is historical after subsequent edits, not final fresh proof.
  No waiver or advancement to I2 was made.
- Final local integration after the shared-output/encoding/CSV fixes: 49 Python tests,
  62 native tests and all ten fixed tasks passed. CSV now has 9/9 graded kills with seven
  ungraded, not an altered threshold. Independent verifier is running on the integrated
  code; subsequent small malformed-report guards require its affected revalidation.
- Planning execution details now explicitly record owned OS-temp fixtures and actual
  30/60-second default child bounds (probe fixture max 180), rather than implying the
  initially proposed scratch path and 15/45 bounds were used.
- Independent verifier found F1: parent probe's broad evidence-directory exclusion hid
  unrelated contract/evidence edits. Accepted and narrowed to exact current report paths;
  the verifier's failing public CLI test was preserved. Its bounded revalidation is running.
- Verifier resolved F2 after ordinary whitespace checks passed with explicit CR-at-EOL
  handling for byte-preserved task artifacts; default whitespace checks remain enabled.
  Raw findings/dispositions are indexed in review.md. Separate code review is still pending.
- Independent F1 revalidation accepted: 53/53 Python tests and the 3/3 added public
  measurement tests passed. All 21 source/test/contract hashes stayed unchanged.
  Native 62/62 and ten-task/79-assertion corpus evidence remains valid for unchanged code.
  The freshly observed actual probe was immediately source-fresh but still incomplete/fail
  with nine missing required measurements. Copying archival evidence afterward is recorded
  separately; it does not turn that observation into a final-tree quality pass.
- Separate review returned REVISE with reproduced R1/R2, preserved in
  `evidence/i1-code-review-r1.md`: missing/contradictory mutation results were accepted,
  while valid `node --test` discovery expansion was rejected. Both findings accepted.
  Shared producer-owned result reconciliation and canonical command selection replace
  the weak consumer checks. Local 4/4 E2E and 19/19 probe tests pass, including 28
  real-producer schema cases. Independent full revalidation is running; prior acceptance
  is reopened for affected code and a separate re-review is still required.
- Independent R1/R2 revalidation accepted: 54/54 full Python tests (704.748 seconds),
  4/4 separate E2E tests, one accepted control and 30 rejected report corruptions in
  both runs. All 98 final-manifest inputs rechecked unchanged; 85 Node/corpus inputs
  preserve the 62-test / ten-task proof. Actual probe run
  `72f1ccc1a361421999706176c4ab7dc4` was immediately fresh but remains incomplete/fail
  with nine missing measurements. Separate reviewer has been asked for re-review.
- Final separate review: APPROVE for limited local functional preservation
  (`evidence/i1-code-review-r2.md`). R1/R2 resolved; packaging-only R3 was independently
  re-anchored and staged whitespace checks passed. Preserve the qualified manifest:
  97/98 inputs unchanged plus the separately reviewed .gitattributes hash, not "98 unchanged".
- Parent accepts functional AC01/AC02 and the regression/review portion of AC09.
  I1.T4 remains blocked by required actual quality proof. Guarded transitions, resume,
  temporal contracts, held-out diagnosis and authoritative status integration are not
  implemented. This is a partial preservation, not completion of the prioritized request.
- Final report: `report.html`. A final read-only/source-fresh probe will update only its
  exact generated reports before the preservation commit. Its expected incomplete/fail
  outcome must be confirmed, not described as a green gate. Commit SHA is handed off in
  the session response rather than inserted recursively into its own source-bound artifacts.

## Gate 1 acceptance
- Research: `research.md`, inspected at the base snapshot; all nine ACs covered.
- Parent checked mutation grading (`scripts/mutate.py:326-335`), overall metric verdict (`scripts/probe.py:457-495`) and check ownership/timing (`references/planning.md:118-121`) against source. Cross-consumer/procedural gaps are bounded by the documented inspections, not inferred from names alone.
- Root causes established: ESM/CJS discovery and native-runner routing gaps; nonzero process failures counted as mutant kills; unavailable metrics and stale mutation artifacts can yield misleading results; existing gate/resume requirements lack a repository runtime admission path.
- External analyzer availability is not assumed. New protocol identities will remain self-declared and enforcement limited to its guarded entry point.
- Existing native baseline: 51/51 pass (`evidence/baseline-native.log`); this is not a new-feature pass.

## Gate 2 acceptance
- `design.html` and `design-contracts.json` r2 accepted after the independent review resolved DR1-DR7 (`design-review.md`).
- Measurement-first code has no dependency on future workflow-ledger/adoption machinery.
- Scope observation is not a sandbox; identities remain self-declared; uncertain child recovery remains blocked.
- The design no longer invents a restriction on private owned temporary directories or an unavailable host isolation API.
- Parent rendered r2 through agent-browser: three printed pages, two visible diagrams, zero browser errors/console messages (`evidence/document-rendering.json`).
- Parent accepts the design under autopilot. Human design approval remains unconfirmed; no approval was inferred from silence.

## Gate 3 consumer readiness
- Separate fresh-context `plan.html` / `tasks.json` r1 received: 11 tasks, three ordered increments, explicit owners, argv, bounds and assertions.
- Parent walked I1.T1: approved standalone interfaces and stdlib tests are sufficient; no future workflow files are needed.
- Parent walked I1.T4 -> I2.T1: independent verification/review and required quality proof are prerequisites. Missing collectors and broader-language mutation remain a named advancement risk, not a waived check or an assumed future pass.
- Final design and plan each render to three pages; all three diagrams are visible and browser errors/console messages are empty.
- Planned commands are not execution evidence. New module import failures will not be counted as behavioral red.

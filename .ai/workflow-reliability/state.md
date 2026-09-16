# Workflow reliability improvements

## Current state
- Requirement: implement the prioritized recommendations from the 29-feature evaluation.
- Tier: full workflow; executable tooling and workflow contracts change.
- Base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- Branch: `shbs-microsoft-workflow-app-verification` (existing task branch).
- Phase: I1 functional preservation approved; quality closure blocked; I2/I3 not started.
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
Preserve the independently verified/reviewed I1 source and evidence on the existing branch.
The next implementation prerequisite is actual supported quality collection, including
diff coverage and architecture rules, plus whole-change mutation proof. Only then can
I1.T4 close and I2.T1 begin. Do not infer permission to waive these checks.

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

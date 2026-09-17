# Workflow reliability improvements

## Current state
- Requirement: implement the prioritized recommendations from the 29-feature evaluation.
- Tier: full workflow; executable tooling and workflow contracts change.
- Base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- Branch: `shbs-microsoft-workflow-app-verification` (existing task branch).
- Phase: bounded CLI/tool-binding checkpoint approved for local preservation.
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
Preserve the approved CLI/tool-binding checkpoint, then continue actual Q2 collectors
and canonical documentation integration. Recovery remains blocked;
no recovery stub or silent completion of the original requirement.
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
- FACT: C2a runner, owner/independent tests, review and bounded evidence are preserved
  in `d971634219a633cc4401fb7dcba9685e672978aa`. All three reviewed source/test hashes
  matched immediately before staging; staged diff check passed. Report rendered to
  three pages without browser/console errors. After commit, only the earlier
  `evals/report.md` date delta remained outside the commit.
- Remaining C2 implementation is owned by `a93df3f0-aa79-45e1-a2ce-c998915758cf`:
  six-verb CLI, CLI tests, native paired failure cases and operator reference. C1/Q1
  and the runner remain frozen. Any required interface correction must be surfaced
  before editing those files. Positive quality/closure scenarios lacking actual
  collectors remain explicitly blocked, never populated with invented passing metrics.
- FACT: C2 owner stopped before production edits at the mandatory frozen-interface
  check (`evidence/c2b-interface-blocker.md`). The gate only clears executable
  unresolved admissions on `completed`; state requires actual terminal process
  observations for that event. Recovery after an unknown-spawn reset cannot fabricate
  those observations. Event also lacks a typed durable LockOwner/recovery-artifact
  binding once the lexical mutex is removed.
- The one real-persistence/synthetic-protocol diagnostic exited 0 and retained seven
  unchanged input hashes; it is not actual recovery or a CLI test pass. No CLI/native
  tests ran and no CLI implementation was written. Parent accepts this design-level
  blocker rather than allowing reason-field encoding, filtered ledger views or fake
  completion events.
- Designer `269ca50e-e7c3-43b0-bbc9-d2fc40a98d1c` owns only a bounded proposed typed
  ownership/recovery amendment, versioning and affected-proof plan. Independent
  review and parent acceptance are required before any frozen core edit. Existing
  runner, metric requirements and historical acceptance remain unchanged.
- FACT: the proposed `c2-recovery-contract.json`/HTML add typed v2 admission ownership,
  immutable recovery references and materialized lifetime-only gate resolution. They
  explicitly lack an established positive platform qualifier. This is a design proposal,
  not permission to ship an always-blocked placeholder or claim live recovery.
- Independent designer-reviewer `64dfb469-4c58-48e5-baa2-aeca2fa35d87` is checking
  correctness, minimality, versioning, stale-lock safety and whether platform qualification
  must precede production work. No amendment or core edit is accepted yet.
- Parent rendered the unchanged proposal to two pages with one visible diagram and no
  browser/console errors. The first helper invocation rejected the digit in the filename;
  only that helper's filename allowlist was corrected and one replay passed. The initial
  rendering record is retained as `evidence/c2-recovery-design-rendering-failed-name.json`.
- Q2's independent prerequisite may proceed without recovery/core changes: owner
  `056029ed-1e2f-4d8d-af0b-7d04bafbe5d3` is qualifying the previously approved TypeScript,
  jscpd, lizard, vulture and Ruff tools in owned external storage. Actual missing-tool
  failure precedes any provisioning; no repository dependency/config or production
  adapter changes are authorized. Results must establish exact versions/APIs/census,
  or name each blocker. C2R and Q2 proof remain separate.
- FACT: independent design review is REVISE (`evidence/c2-recovery-design-review.md`).
  Parent accepts all four findings: qualify a real pre-admission identity/evidence
  path before production recovery machinery; specify or defer live v1 migration;
  consistently limit unknown-spawn recovery to a qualified complete environment
  reset; bind review acceptance by actual bytes/sequence rather than absent timestamps.
- No production recovery amendment is adopted. The platform prerequisite cannot be
  deferred behind immutable null-identity admissions and still claim those runs become
  recoverable later. The final design round is held until feasibility evidence exists.
- Researcher `2c5aaf54-e540-442b-a434-911a0e9ee872` owns one read-only feasibility
  check of an already-available Docker-compatible execution environment, if present.
  No installation, daemon launch, environment reset or container mutation is authorized.
  If unavailable or inadequate, return the named prerequisite rather than a broad
  platform hunt. Q2 qualification remains independent and active.
- FACT: `evidence/c2-recovery-platform-research.md` found neither `docker` nor
  `docker.exe` through this session's command resolution. This is not proof of
  machine-wide absence; no daemon inquiry, install or container action occurred.
  No qualified producer or positive recovery path was established. The bounded
  root `.ai` check also found no canonical persistent v1 guard ledgers.
- Parent selects the final-round design direction: defer positive recovery and
  speculative v2 migration/qualifier machinery; preserve original recovery
  requirements as blocked. Propose independently useful status/next/record/close/
  adopt only, with no stub recover verb and explicit interruption limitations.
  Existing schemas/core remain frozen unless a concrete ordinary-operation seam
  is independently reviewed. This scope is proposed, not yet implementation approval.
- Original designer `269ca50e-e7c3-43b0-bbc9-d2fc40a98d1c` is disposing F1-F4 in
  the final planned revision, preserving exact r1 artifacts. Ordinary adoption
  must specify actual bootstrap/partial-publication behavior, not hide another
  load-before-adopt dependency. Independent review follows; no further broad cycle.
- FACT: Q2 `evidence/q2-tools-report.md` qualifies jscpd 5.2.1 and Ruff 0.16.8 on
  bounded real fixtures. TypeScript 5.9.3, lizard 1.24.0 and Vulture 2.16 remain
  blocked by package-access TLS negotiation failures, not by missing versions.
  CHECK-TOOLS is incomplete; no production adapters were written. Coverage stays Q3.
- Parent authorized one bounded secure acquisition follow-up: same official hosts
  using normally verified TLS 1.2 if negotiation is the cause; no insecure HTTP,
  certificate disabling, trust-store changes or policy bypass. If that fails, the
  owner may propose an exact-tag official-source route for review, not silently
  provision it or substitute another tool/version. Existing qualification and failed
  download evidence remain immutable.
- FACT: final proposed r2 names C2b-ordinary-v1 and defers recovery/v2 migration.
  It specifies five ordinary verbs and finite adoption bootstrap/publication retries.
  Two exact state seams are now explicit: shared `validate_design_binding` and paired
  optional design/ledger inputs to `bind_inputs`. No production change is authorized
  until the final independent review accepts these interfaces and their ordering.
- Normative r2 contract SHA-256:
  `80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d`.
  Parent added only a publication-order diagram to the overview; final HTML hash
  `a290690f4c16755d47a21930dd40fc6f01df9789ec2b2691f6b0ea773803750a`
  renders to two pages with no browser/console errors. R1 source and rendering
  artifacts are preserved separately. Reviewer was notified of the presentation delta.
- FACT: final design re-review APPROVE (`evidence/c2-recovery-design-review-r2.md`)
  binds the normative r2 and reconciles the diagram-only HTML delta. Parent accepts
  ordinary-five-verb design and the exact two state seams. Adopted-event construction
  must include the existing `binding_mode="guarded"` field and actual source snapshot;
  no synthetic bootstrap proof. Full C2/recovery/AC05 remain incomplete.
- Owner `a93df3f0-aa79-45e1-a2ce-c998915758cf` is implementing only the state-seam
  sub-slice first. Gate/runner/evidence/schemas stay frozen; independent verification
  and review precede CLI integration. Any further material seam need stops that path.
- FACT: Q2 same-host TLS 1.2 attempts failed once per host. Official GitHub acquisition
  succeeded for data-only exact packages/source (`evidence/q2-tools-route-report.md`).
  Parent approves the released TypeScript 5.9.3 package and unaltered pinned lizard/
  Vulture/Pygments/pathspec source execution in isolated owned external storage.
  This changes distribution provenance, not versions or policy; no PyPI wheel identity
  is asserted. No build backends, source rewrites or ambient plugin dependencies.
  Owner rechecks archives and qualifies actual APIs/imports before tool acceptance.
- FACT: C2b-S owner implemented the two approved state seams and 16 new tests.
  Local successful batches total 61 distinct methods. Two buffered capture attempts
  hit the outer idle timeout and supplied no gate pass; first-capture child identity
  and complete old fixture/process cleanup remain unverified. No logs were reconstructed.
  See `evidence/c2b-state-handoff.md`; implementation is not accepted yet.
- Parent authorized a distinct progress-visible independent route, not a third
  identical buffered retry. Verifier `096ede71-aae0-490a-a029-0b11e44dc39c` streams
  actual unittest output through the existing bounded CLI runner, preserving previous
  timeouts and checking the affected workflow/evidence scope. No timeout increase,
  fake heartbeat or unsupported old-process cleanup claim is authorized.
- FACT: `evidence/q2-tools-source-report.md` qualifies the remaining TypeScript,
  lizard and Vulture APIs. With retained jscpd/Ruff evidence, CHECK-TOOLS is qualified;
  Q2 adapters and actual metrics are not implemented. Strict source decoding before
  lizard's text API and preservation of Vulture's pre-report error status are mandatory.
  Prior TLS/helper failures and narrower successful follow-ups remain documented.
- Parent accepts the qualified tool prerequisite with those limits. Adapter production
  dispatch waits until the active state verification/review freeze is clear, avoiding
  concurrent changes to imported measurement dependencies. Coverage remains Q3.
- FACT: the fresh streamed verifier returned BLOCKED
  (`evidence/c2b-state-independent-report.md`). Evidence10 passed; workflow100
  produced 42 positive methods and 58 errored methods (98 records including
  subtests), all FileNotFoundError at 265-266-character receipt staging paths.
  No assertion failures, new timeouts or output overflows were reported. All
  owner16 and independent1 adoption methods passed; 29/29 bounded pins matched.
  The deep private TEMP layout is a suspected verifier transport problem, not
  an established production defect or a passing regression gate.
- Parent authorizes one capture-only short-OS-temp correction by the same verifier:
  use a new exclusively owned short root, first exercise actual receipt staging,
  then replay the affected workflow scope with unchanged 120/600 bounds and real
  streamed progress. Preserve the failed capture and original helper bytes.
  Do not rerun the deep-layout helper unchanged, alter production/tests to hide
  errors, change OS settings, delete unknown old fixtures, or claim old tree death.
  Retain evidence10 as its disjoint successful batch; no duplicate pass totals.
- FACT: the short-temp correction passed actual receipt staging at 145 characters
  and the full workflow100 replay (exit0, 263.471 seconds). Together with retained
  disjoint evidence10, accepted proof is 110 distinct passing methods. No accepted
  batch reported failures/errors/skips/timeouts. All 49 bounded pins matched;
  original failed captures remain unchanged. New owned short temp was empty and
  removed nonrecursively; original whole-tree cleanup remains UNKNOWN.
- FACT: separate `evidence/c2b-state-code-review.md` is APPROVE. Reviewer reconciled
  all 49 pins, 17 evidence hashes, method inventories and 75 unchanged definitions.
  Shared validation/materialization is preserved. Simultaneously malformed live
  inputs can surface a different first error after the extraction; both fail closed.
- Parent accepts only C2b-S functional preservation, including the two test files.
  CLI/adoption publication, positive recovery, actual Q2-Q5 quality, human approval,
  host exercises and publication are not completed by this approval.
- FACT: parent preservation check materialized all three staged source/test files
  through Git into a new owned temporary checkout; each exactly matched reviewed
  working bytes. Git stores LF while the qualified local checkout restores CRLF.
  No source, attribute or Git configuration change was needed. See
  `evidence/c2b-state-parent-preservation.json`; this adds no test or portability claim.
  The updated report renders to three pages with no browser/console errors.
- FACT: C2b-S, its approved ordinary-operation design, reviewed proof and Q2 tool
  qualification records are preserved in `ee6e0e34e78b70fcb672074af0a76f51fe937e1a`.
  Only the earlier unrelated `evals/report.md` date delta remained after commit.
  No provisioned package/binary archive was added; no publication was attempted.
- Parent authorizes the existing CLI owner for ordinary status/next/record/close/adopt,
  their real failure/resume/adoption tests and operator guide. A separate Q2 owner may
  implement the approved scalar/shared-JS/graph adapters and corresponding tests.
  Owners must preserve existing public core signatures and avoid each other's files.
  Concurrent local test results are development evidence, not a shared frozen-tree
  acceptance claim. Both writers must stop before fresh integrated verification/review.
  Any new interface/design need is a named blocker, not permission to silently extend
  schemas, bypass required metrics, introduce recovery machinery or waive quality.
- FACT: CLI owner stopped before edits on a supported producer-interface gap
  (`evidence/c2-cli-producer-interface-blocker.md`). Both probe paths generate
  their own UUID; actual help has no admission-ID input, and `--run-id` exits2.
  The gate requires the earlier admission ID and exact admitted source binding.
  Parent also confirmed that configured raw-report validation needs its context,
  inventories, policy and artifacts; adding one flag alone is not a full bridge.
- Parent explicitly narrows the current ordinary-CLI delivery boundary: continue
  actual ordinary operations, nonmetric proof, failure capture and missing-metric
  denial. Successful guarded metric attachment is an unavailable prerequisite,
  not a supported operation or positive closure claim. Reject it explicitly before
  creating an accepted receipt; do not import score JSON, rewrite IDs, backfill
  admission, relax the gate or silently treat a matching summary as validated proof.
  This retains r2's already-required missing-quality closure block.
- A separate producer/CLI binding follow-up must define pre-admitted identity,
  exact registered-command expansion, source projection and producer-owned raw
  validation together before successful metric attachment. Q2's adapter owner is
  informed, but no unreviewed identity flag or producer/schema change is authorized
  by this discovery. Ordinary CLI work must not remain blocked on that deferred
  positive path; the overall requirement remains incomplete until it is delivered.
- FACT: Q2 owner also stopped before production edits on a separate artifact-locator
  gap (`evidence/q2-adapter-binding-handoff.md`). Qualified original locators are
  absolute, while runtime Artifact paths are run-relative and a fresh run starts
  empty. Existing config has no original-artifact root. The bounded diagnostic
  rechecked 3,348 tool/resource pins, both native binaries and ten artifact copies;
  this is not adapter acceptance.
- Parent selects one explicit source-bound read-only tool-artifact root, with exact
  verified staging, original/copy freshness and unchanged strict relative output
  paths. Q2 owner is writing a small additive normative amendment for focused
  independent review before production resumes. Empty Q1 mode remains unchanged;
  package/code resources stay external. No metric threshold or guard change is
  authorized. The ordinary CLI owner proceeds independently on its narrowed scope.
- FACT: `evidence/q2-tool-input-root-amendment.json` binds the original measurement
  contract and adds only conditional `tool_artifact_root` intake/staging semantics.
  Its SHA-256 is `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1`.
  Focused independent `evidence/q2-tool-input-root-review.md` returns APPROVE with
  no material findings; existing JSON-only readers are not opaque-byte staging APIs.
- Parent accepts that exact amendment and releases Q2 implementation, including
  ROOT01-05 and the original real scalar/graph/parser/reconciliation checks. Original
  proposal/review bytes remain intact; this entry records acceptance, not human
  confirmation or executed adapter proof. Q2 and ordinary CLI writers remain
  disjoint and must both freeze before integrated independent acceptance.
- FACT: Q2 delivered a native-tool input-root development checkpoint
  (`evidence/q2-adapter-root-handoff.md`): conditional root validation, exact byte
  staging/ownership, overlap rejection and original/copy/native-tool rechecks in
  measure/probe. No scalar analyzer ran as a collector; JS/source-tool bindings
  and actual scalar/raw integration remain unfinished.
- Its selected 14-method pass predates the final small correction; two repeated
  methods pass afterward. These are not 16 distinct final-byte passes. Actual
  symlink creation is environment-blocked by WinError1314, and earlier timeout
  cleanup remains unverified. No independent acceptance or full-suite pass follows.
- Parent continues the same approved Q2 implementation with a smaller next slice:
  qualified TypeScript/lizard/Vulture source-tool bindings and focused real tests.
  The existing owner retains implementation ownership; no new design, installation
  or policy weakening is authorized. Shared JS/scalar adapters remain subsequent
  work, and both writers still must freeze before fresh integrated acceptance.
- FACT: CLI owner returned `evidence/c2-cli-local-handoff.md` and froze its five
  owned files: workflow.py, CLI tests, two native failure-pair files and the operator
  guide. All 30 final CLI methods pass locally; 126 existing regression methods
  passed in an earlier overlapping run. Native pairs replay five Python scenarios,
  not additional independent behavioral proof. An actual adoption parse/snapshot
  race was reproduced and corrected; its red record remains preserved.
- This is development evidence: Q2 measure.py changed during the CLI runs. The CLI
  owner is now idle; final integrated verification/review waits for the Q2 source-
  binding checkpoint to freeze. No CLI acceptance or commit is claimed. Successful
  metrics/quality closure and recovery remain explicitly unavailable in the guide.
- FACT: Q2 source bindings are locally implemented and frozen
  (`evidence/q2-adapter-source-handoff.md`). Ten selected methods pass on unchanged
  final bytes, including seven new source-binding cases; this is not full Q2 proof.
  Actual isolated tool/runtime/resource observations and rejection evidence are
  retained. Shared JS/scalar collectors and raw metric reconciliation remain pending.
- Both source owners are now idle. Parent freezes the ordinary CLI plus native/source
  tool-binding checkpoint for independent verifier
  `e0de4213-9fd4-4032-9ef7-9722d1d26519`. No production writes are authorized during
  its affected integration replay. Named symlink-creation environment limitations
  remain outside passing counts; no full-suite or complete-Q2 pass is implied.
  Separate code review follows the fresh verification result before preservation.
- FACT: joint verifier returned NOT-VERIFIED (`evidence/joint-cli-binding-report.md`).
  Of 263 discovered Python methods, 204 passed, one timed out twice, 57 never
  started and one remains symlink-environment-unverified. Thirteen native entries
  passed (five Python replays plus eight reporter cases). No production assertion
  failure was observed, but joint regression acceptance is withheld.
- The repeated idle timeout is the unchanged graph receipt/artifact corruption
  method. Parent read its sequence of real validation calls without completed-case
  output. Removing broad profiling did not fix silence. Parent authorizes one
  distinct capture-only route: narrowly report actual completed validator returns,
  prove transport on real validation, then execute the timed-out method and 57
  unstarted selectors with unchanged idle120/max1800 limits. No fake heartbeat,
  production/test-body rewrite or unchanged third attempt is authorized.
- Original 4,511 pins matched; eight additionally observed runtime inputs were
  current-only. The new replay must pin them prospectively, without retroactively
  upgrading prior proof. Seven old temp directories and complete timeout-tree
  cleanup remain UNKNOWN; new runs use separately owned short temp roots.
- FACT: the distinct Q1 progress route passed all 58 outstanding methods. Joint
  accounting is now 262 passed / 263 discovered, with the named symlink environment
  case unverified; native13 remains five replays plus eight reporter tests.
  The formerly timed-out method completed in 136.195 seconds, with twelve real
  validations taking 9.8-10.1 seconds each. No source/test-body change or timeout
  increase occurred. All 4,608 prospective pins matched; earlier current-only and
  old cleanup limits remain. See `evidence/joint-cli-binding-r2-report.md`.
- FACT: separate `evidence/joint-cli-binding-code-review.md` returns REVISE for one
  P2 finding: inspect_source_binding checks smoke-output reservations but not exact
  staged qualification rows/roles/revisions/input reservations. Byte rehashing alone
  does not establish manifest ownership. CLI/adoption review found no further
  required corrections, but joint acceptance remains withheld.
- Parent reopens only the Q2 owner for R1: reproduce an actual rehashed malformed
  manifest, add the smallest prelaunch ownership check and real focused tests,
  preserve valid binding/compatibility behavior, then stop for independent replay
  and narrowed re-review. No new schema, collector, guard or recovery work is
  authorized during this correction. Previous 262-method proof remains historical
  once the affected source changes; no automatic refreshed-count claim.
- FACT: R1 owner reproduced an actual successful TypeScript launch with a missing
  qualification row, then added only `_validate_binding_ownership` and its prelaunch
  call. Twenty real rehashed malformed manifests now reject with no audited launch,
  run-root write or smoke output; a valid control actually launches. Ten selected
  methods pass on fixed bytes, not a refreshed 262-method run.
- Fixed measure.py hash:
  `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1`.
  Fixed source-binding test hash:
  `bcc36f23061dd5b4db2dfcb161c0202bbe95db1fb930b1c6ef79fe8c9b95d1b3`.
  `evidence/q2-binding-r1-handoff.md` retains the real red/green artifacts and commands.
- Same independent verifier `e0de4213-9fd4-4032-9ef7-9722d1d26519` now owns fresh
  affected replay without broad profiling or unrelated reruns. Production is frozen.
  Same reviewer `eaec213a-63fa-49e5-bbe5-a9bed6127d02` will reconcile the correction
  afterward. Historical runtime, symlink and cleanup limitations remain explicit.
- FACT: `evidence/joint-cli-binding-r1-report.md` independently verifies all ten
  affected methods (801.803 seconds, no failures/errors/skips/timeouts). Twenty
  actual malformed manifests reject before writes/launches; the valid control
  runs. All 4,651 prospective pins match, and exact raw reconstruction isolates
  the authorized helper/call/test addition. Historical 262/native13 are not rerun.
- The original synchronous reviewer cannot receive follow-up messages through
  the tool. Fresh narrowed reviewer `21e56a4a-f30d-4fca-8e66-f1964f100afe` is
  reconciling only R1 against that preserved review and the new independent proof.
  This does not reopen or replace the unchanged broader CLI review.
- FACT: `evidence/joint-cli-binding-code-review-r2.md` is APPROVE and closes R1.
  The reviewer inspected the actual helper/call/regression, reconstructed the prior
  bytes, and reconciled 4,651 pins plus seal/index and real red/green records.
- Parent accepts bounded ordinary CLI and tool-input/source-binding preservation.
  Historical 262/263 and native13 remain distinct from the fresh ten-method R1
  replay. The symlink environment case, earlier runtime/cleanup limits and custom
  evidence-test discovery limitation remain explicit. No whole-Q2, successful
  metric attachment/closure, recovery, host experiment or release acceptance.
- FACT: parent materialized the nine staged source/test/guide files through actual
  Git checkout; all match the reviewed working bytes exactly. Stored LF versus
  local CRLF is recorded in `evidence/joint-cli-binding-parent-preservation.json`.
  Source/status whitespace checks pass. The broad check flags only the immutable
  captured r1-only.diff's CRLF patch text; its sealed bytes were not reformatted.
  Eleven new ZIPs were inspected as bounded source-fixture evidence, not installed
  tool packages. The accepted-status report renders to three pages without errors.

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

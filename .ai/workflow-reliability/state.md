# Workflow reliability improvements

## Current state
- Requirement: implement the prioritized recommendations from the 29-feature evaluation.
- Tier: full workflow; executable tooling and workflow contracts change.
- Base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- Branch: `shbs-microsoft-workflow-app-verification` (existing task branch).
- Phase: reviewed Python/JS integration is completing its frozen handoff; remaining scalar adapters are being implemented on a disjoint branch. Planner checkpoint `1d12f5c` preserves bounded real-download proof and explicit final browser blockers.
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
Preserve the integrated app checkpoint, bounded download proof and unresolved
browser blocker while the dependent Python integration session completes the
accepted orchestration, manifest, graph and replay boundary and CRLF correction.
Do not repeat the stopped browser experiments. The former JS
owner is cancelled; its accepted resume message did not establish execution.
Candidate-test observability is corrected in `eae52fe`; README
and guides clarify the manual-work boundary in `8577642`. This is resumption
of accepted unfinished work, not a new framework, host trial or scope expansion.
Collectors and guarded metrics remain incomplete and are not waived.
C3 is preserved. Recovery remains blocked;
no recovery stub or silent completion of the original requirement.
The fresh agent-driven app extension now has a limited observation ledger.
Neither that exercise nor the earlier refreshed regressions establishes full
29-feature acceptance or causal skill effectiveness.
The local I1 preservation commit is `aaec9b9`.
The continuation addendum replaces implementation-dispatch dependencies only; it does not
close I1.T4 or remove any required measurement, independent role or final acceptance check.

## Native command continuation
- Current parent guard regression: 133 tests passed in 620.198 seconds, exit 0,
  with all 46 tracked script-input hashes unchanged and owned temporary fixtures
  removed. Exact command, raw output and CLI transcript are retained under
  `evidence/guard-regression-20260918T103241-87ab79/`. This is owner-run existing
  workflow regression on the pre-integration parent tree, not independent
  acceptance, a successful real metric receipt or qualified recovery.
- Scalar session `72aba2d4-0cc0-4bdd-8b7a-8336485fe0a1` owns only the new scalar
  module, scalar-specific tests and its task artifacts until the JS controller
  freeze is released. The owner reports real jscpd/lizard cases passing while
  broader scalar tests continue. Composition remains unimplemented: the current
  qualified-tool binding helpers are measure-owned, and no lower-layer accessor
  exists. A narrow reviewed extraction/ownership amendment must preserve all
  producer pins and the exact six-file JS request boundary before wiring.
- JS integration owner reports final nine-method selection passing in 1280.761
  seconds, public/Python three-method selection passing in 500.634 seconds and
  explicit-mode/config two-method selection passing in 39.367 seconds. CRLF
  correction has same-reviewer code approval. These await the reviewed commit,
  raw-evidence reconciliation and parent integration. Owner execution is not
  relabeled independent execution; the earlier selector error remains separate.
- Fresh-worktree setup correction: `13e1d309` preserves six required qualification
  logs that ignore rules had excluded. Exactly 22 selected inputs were reconciled:
  16 existing child copies were byte-identical and six were copied exclusively.
  No requalification, installation or frozen-manifest modification.
  Evidence: `evidence/qualification-handoff-js-integration.json`.
- Planner checkpoint: original `e2e4835`/`2c7e3f8` integrated as `c41fdf2`/`81a5921`.
  Parent verified the exact post-review patch hash and all three final delta
  hashes, then reviewed the guidance/config/deadline ownership changes directly.
  This is not a replacement independent full review. The child's full review
  remains historical, and normal exits do not prove forced-deadline cleanup.
- Browser transport: one isolated owned HTTP fixture with the installed
  agent-browser 0.37.1 saved exact CSV bytes using managed launch, configured
  download directory and ordinary click. Explicit `download` canceled in the
  same browser/page/fixture. `evidence/download-transport-control/` preserves
  the original report, actual saved CSV and replay script. Upstream Windows
  canonicalization is a source-grounded hypothesis, not an exclusively proved cause.
- Parent changed only the app E2E launch/download helper and its README:
  agent-browser owns the fresh browser; Playwright locates its executable only;
  actual new browser files are compared byte-for-byte and independently parsed.
  Aborted-export checks inspect the real download directory, not an unused
  destination filename or uncorroborated event timeout. Production CSV is unchanged.
  Independent verifier `b8964d17-7254-4c49-b7ee-785f10bfdb74` was assigned one
  all-flow run and native coverage. Actual artifacts contain two overlapping
  browser runs, not one; accounting correction was requested. Both failed overall.
  The first has 204 passing records and a same-name file-discovery failure;
  the second has 157 passing records, a wait timeout and subsequent empty-page
  snapshot. Neither establishes an app notification defect. Native 46/46 passed
  with 99.40/97.56/97.03 backend line/branch/function coverage.
- A second isolated control reproduced two blob downloads with different
  response bytes at the SAME completed filename, with a visible success notice
  and live original tab. This disproves the harness assumption that every
  successful download introduces a new directory entry. The helper now moves
  each completed browser file to its unique evidence path, leaving the inbox
  free for the next generation. This fixes the observed first-run harness bug;
  the separate timeout's cause remains unknown. No production app edit.
  Evidence: `evidence/repeat-download-control/`. Fresh serial verification is due;
  the verifier must first correct its execution accounting and causal overclaim.
- The serial archive replay saved and compared three actual CSVs (active,
  archived and stale-client) but still exited 1: the empty-export notice wait
  hit the inner 25-second idle bound. Raw output has 74 passing records and
  218 CLI commands, not the verifier's 217/120-second interpretation.
  `evidence/planner-download-remedy-adjudication.json` supersedes its unsupported
  narrative claims. The repeated wait primitive is now blocked, not retried.
  The next harness route observes the completed file first under the unchanged
  12-second bound, then asserts exact notice text through ordinary DOM inspection.
  No assertion removal, timeout increase, speculative app edit or known-cause claim.
  One serial archive verification of source `9ca5288b` is authorized separately.
- That file-first run also failed: 57 passing records, 144 commands and two
  completed CSV comparisons; ordinary DOM eval hit25s idle at command136 after
  retaining the stale-client file, followed by about:blank and a missing editor.
  Owned CLI close succeeded. The issue is not confined to the wait primitive.
  Browser trials are now stopped after bounded alternatives; no guessed app fix.
  Independent pre/post manifests also contain null hashes for invented paths and
  a wrong README path. Only actual nonnull pins and the harness's12-file source
  reconciliation are evidence. Parent adjudication preserves these limits.
- `evidence/planner-workflow-observations.json` reconciles every original feature
  ID against this fresh extension exercise. It separates partial, blocked and
  unexercised branches; it is not a 29-feature pass or a live causal evaluation.
- Parent report and app README now state the current browser limit. The updated
  report rendered to three PDF pages without browser errors or console messages.
  This was document-only rendering, not another app browser trial. Selected raw
  artifacts are preserved separately from unsupported verifier prose.
  Staged-byte validation detected automatic newline normalization of the tested
  harness. Its path now uses the app's existing `-text` preservation convention
  so the committed file keeps the exact tested SHA-256; documentation retains
  ordinary Git text normalization.
- Parent took over the cancelled owner's native command boundary under the
  existing accepted revision-3 design. Controller/manifests/graph/replay and
  collectors remain unfinished; no configured-JS acceptance is claimed.
- FACT: the new real-command positive test first failed for both base and head
  because direct execution explicitly rejected the unimplemented command
  (one method, two failing subtests, 27.209s).
- Implemented fixed JSRequestV1 input, qualification/preflight/source/controller
  checks, one Program/checker, actual provenance and exclusive symbols/result
  publication. No subject execution, graph publication or metric totals.
- FACT: five command methods plus selected native/regression methods pass:
  12 methods in 336.279s, captured in `evidence/js-command-native/`.
  Source-bound output bytes are retained, not reconstructed from summaries.
  This is parent-run verification; independent review is still pending.
- Reviewer `08450ded-04c7-462c-8a16-a6fd20c33c23` approved the bounded native
  producer and final delta. Independent final execution passed five methods
  (11 native calls: two successful productions, nine expected rejections) in
  108.389s, exit 0. All eight requested before/after source hashes matched.
  Evidence was retained in the agent tool transcript, not separate raw files.
  The missing-request CLI error intentionally changes from library-only
  rejection (exit 1) to request validation (exit 2); configured probe still rejects
  unsupported nonempty JS entrypoints. Historical frozen evidence is untouched.
- Final self-review moved tool-root disjointness checks before compiler loading,
  rechecked output bytes before successful exit, and added a real subject
  side-effect sentinel. Those final changes are covered by the independent run.
  The earlier 12-method run and two separately passing Python compatibility
  methods (70.298s) predate this final delta; counts are not added as fresh tests.
- FACT: checkpoint `3f7a77a19334fea1f4941fb186bcd88b0a121631` preserves the
  producer, documentation, test/evidence and three-page report. Parent verified
  current source pins, archived output hashes and actual staged checkout bytes.
- Successor session `ca7cdaa3-43a2-45c2-8147-b571fa975c46`, branch
  `shbs-microsoft-js-measurement-integration`, starts from that newly completed
  dependency and owns Python orchestration/manifests/graph/accepting replay.
  Live activity reports busy. This is the next integration increment, not another
  native producer implementation. Its new task artifacts are isolated under
  `.ai/js-measurement-integration`; it may not rewrite this parent's history.
  Scalars, coverage, guarded metrics, recovery and publication remain excluded
  from that bounded assignment and remain unfinished overall.
- Reviewer subsequently returned the exact invocation and all eight before/after
  hashes from the existing transcript, without another run. Parent matched each
  to the final source pins and recorded the invocation in
  `evidence/js-command-native-independent.json`. This does not create a raw
  evidence file or a second verification result.

## Candidate-test progress correction
- Scope: trivial test-harness observability correction, not production parser or
  pipeline expansion. Existing candidate assertions and idle30/max90 bounds stay
  unchanged; only completed work may emit progress, never a timer heartbeat.
- FACT: retained isolated success took 24.946s inside the native test without
  intermediate output. A fresh pre-fix execution reproduced exit 124 with no
  native output/result (`evidence/candidate-progress/red/`).
- FACT: candidate generation, three syntax checks and three rejection checks ran
  silently in one case. Added completed-stage messages and an ordered-progress
  assertion in the Python harness. No assertion was removed or timeout increased.
- FACT: the same four-method combined selection now passes in 239.381s.
  The native candidate case itself takes 37.445s, exceeds the idle window in total,
  and completes with actual progress under unchanged idle30/max90 bounds.
  This establishes the missing-progress cause for the reproduced idle failure,
  not a performance optimization or universal reliability guarantee.
- FACT: all 16 runner regressions pass in 11.274s, including genuine idle/maximum
  termination and partial-line progress. Evidence is in
  `evidence/candidate-progress/`; historical failed runs remain unchanged.
- Parent self-reviewed the small test-only diff. No new independent review,
  full-root suite or full-quality acceptance is claimed by this correction.

## Q2 shared-JS amendment review
- FACT: C3 is preserved in `ce7c07eb4bec9239db4d45cdf9bc83c88a43a16c`.
  After commit, only the earlier `evals/report.md` delta and three Q2 proposal/handoff
  files remained outside that commit. No publication attempt occurred.
- Q2 owner returned proposal revision 2 at
  `evidence/q2-js-execution-amendment.json`, reported SHA-256
  `cd69b23bd22c08fe6884fcd5fbb5570d4dd0e5f4551b2f161ce4d0c0da61333a`,
  with `evidence/q2-js-execution-rationale.md`. No parser code or tests are claimed.
- The proposal adds a produced-evidence manifest between preflight execution and final
  graph publication, with explicit backward-only manifest-role ownership. It specifies
  fixed measure-owned execution/replay and separate versioned symbol evidence while
  retaining existing SyntaxEvidence/Candidate/Finding shapes and Python-only behavior.
  These are proposed contracts, not implementation facts.
- Fresh reviewer `7d466374-d6f6-49a0-9b17-bfdadc889d81` owns one focused design review
  against the original contracts, root amendment, R1 and current production callers.
  Parent must adjudicate its result before releasing code. Q2 proposal and runtime
  files are frozen during review. Scalars, guarded metrics, recovery and complete
  quality remain separate unfinished requirements.
- FACT: `evidence/q2-js-execution-review.md` returns REVISE, with nine authority/
  runtime pins unchanged. Parent accepts JS-R1 (materialize base before filesystem
  reservation discovery), JS-R2 (explicit measure-owned production/replay purpose)
  and JS-R3 (consistent ownership/decoding/comparison/archive rules for failed
  partial output). Successful-path architecture is supported; code is not released.
- Q2 owner must retain exact reviewed revision-2 proposal/rationale bytes and return
  a bounded revision 3 addressing those findings. The same reviewer will handle the
  second focused pass. No new Context field, ownership role or collector scope is
  authorized by this correction.
- Parent also re-anchored the review's six-suffix classification caution in
  `measure.py` `_walk`/`inventory`: `.jsx`/`.tsx` are currently unsupported entries
  in an immutable digest, and inventory receives no config. Revision 3 must explicitly
  define the JS-enabled classification/interface while preserving the default
  inventory behavior; graph must not rewrite a frozen inventory or infer hidden mode.
- FACT: parent matched retained revision-2 proposal/rationale hashes and the final
  revision-3 hashes: amendment
  `887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e`,
  rationale `82680496ec4466922e6273d53df5d6ef354ad1045d0fdf86b5e5be9191d1cbd9`.
  Owner reports no runtime/test edits. Earlier unreviewed r3 hashes are superseded.
- Revision 3 explicitly proposes early base discovery, a private purpose argument,
  six finite output scenarios with strictly failure-only opaque retention, and
  `include_js=False` inventory/discovery keywords preserving default behavior.
  Parent read the exact revised failure table and classification rules. Same reviewer
  `7d466374-d6f6-49a0-9b17-bfdadc889d81` now owns the second focused pass in
  `evidence/q2-js-execution-review-r2.md`; implementation remains unreleased.
- FACT: second focused review `evidence/q2-js-execution-review-r2.md` APPROVES
  frozen revision 3 and closes JS-R1/R2/R3 plus the six-suffix classification
  caution at the design level. All 12 reviewed input pins remained unchanged;
  no parser or test implementation is implied by that result.
- Parent accepts revision 3 at the recorded hash for the minimal shared-JS
  implementation. Human sign-off remains unconfirmed under the authorized
  autonomous continuation. The retained proposal status is historical; this
  explicit parent disposition and final review authorize implementation without
  rewriting the reviewed bytes.
- Preserve the accepted amendment, exact r2 history, reviews and original seam
  handoff before dispatch. Owner `32d88126-0b11-466a-b04a-76bebef5b9c9` then owns
  parser/inventory/controller/manifest/graph/probe integration and its seven
  specified proof groups, not scalars, root mutants, coverage, metric attachment
  or recovery. Independent verification/review and a green local preservation
  boundary remain mandatory before this component is called delivered.
- FACT: owner returned `evidence/q2-js-handoff.md` and `evidence/q2-js-seal.json`
  (seal `7befec79cce53797b158d62f80f412b2efdf05080c1e7c28a8b2cd48f9e1f0fa`).
  This is a genuine native parser-core library plus inventory/controller keywords,
  not the complete JS component. Five implementation/doc/test paths and 28 owned
  files are frozen. Owner reports 15 selected Python methods passed in 879.393s;
  seven native cases and six binding smokes are nested, not additional methods.
- Symbol/candidate serialization, fixed command, manifests, accepting replay,
  graph/probe wiring and finite output archival remain unimplemented. No complete
  accepted JS test ID or configured JS measurement support is claimed.
- Fresh verifier `8b39ef04-f116-4d2d-bc1b-ad3f46bb7a86` owns independent core replay
  and pins; separate reviewer `a7dfd5cf-e714-46b8-9763-f2f88ec691f2` owns the bounded
  implementation/doc review and later proof reconciliation. Parent status is outside
  their implementation pins; C4 preparation remains external to this worktree.
- FACT: `evidence/q2-js-core-code-review.md` gives preliminary bounded APPROVE
  with no substantive findings. It reconciles all 28 owned and 10 unchanged-input
  pins and reviews the actual native core, controlled host, diagnostics, byte
  handling, tests and default compatibility. Independent execution acceptance
  remains pending; no complete JS check ID or preservation commit is claimed.
- FACT: `evidence/q2-js-core-independent-20260917-v1/report.md` now records the
  exact 15-method replay passing in 732.040s and two new ordinary-discoverable
  boundary methods passing separately in 14.195s. No test failures, skips or
  retries occurred. Seven native cases and six binding smokes remain nested,
  not additional Python methods. All 3,593 recorded input pins matched.
- The verifier's post-test publication helper hit idle30 while silently checking
  those pins. One bounded retry reported actual completed-pin progress and
  succeeded without rerunning tests, modifying production or increasing limits.
  The failed capture is retained; descendant termination remains UNKNOWN.
- Final reconciliation by the same reviewer includes the two new test files and
  independent proof. Its completion is still awaited; preliminary approval is not
  substituted for that disposition.
- FACT: `evidence/q2-js-core-parent-preservation.json` records 60 matched sealed
  file records, actual staged checkout byte equality for all seven source/test/doc
  files, and exact staged blob preservation for 53 evidence files. Its temporary
  checkout was removed. This is preservation checking, not additional test proof.
  The first staging command stopped on two whitespace warnings in the immutable
  development `unittest.log` (lines 47 and 49). Those original bytes are retained;
  the seven source/test/doc files pass the scoped whitespace check.
- User clarification: the original goal was a medium-complexity app exercising the
  workflow. The earlier planner run is historical. The latest 15 + 2 parser checks
  are not a fresh complete live-app run, and the latest changes have not yet been
  verified that way. No complete component, full suite or release gate is claimed.
- FACT: the attempted preservation update to the original reviewer returned
  `cancelled`; no final reviewer response exists. Its retained source review
  explicitly approves the five-path checkpoint conditional on parent reconciliation
  of the separate fresh-verifier evidence. It did not review the two later tests.
- Parent disposition: that source-review condition is now satisfied by the fresh
  15-method replay, separately passing two-method discovery, unchanged source pins
  and staged-byte checks above. Parent also read both added test files: actual
  ENOENT, unadmitted-file resolution, forged-handle callback exclusion, hardlink
  rejection, unsupported config and direct-command rejection are asserted without
  mocking the behavior. No substantive finding was identified. This is parent
  reconciliation/self-review of the additions, not a fabricated final independent
  reviewer verdict. Accept bounded local preservation, not the full component or
  ship gate; retain the original preliminary review and its precise scope.
- FACT: the 69-file bounded parser-core checkpoint is committed as
  `886d699a9b8523f2846c65b21fcfd56fc5b3e0dc`. Only the unrelated `evals/report.md`
  remained modified immediately after commit. Existing owner
  `32d88126-0b11-466a-b04a-76bebef5b9c9` resumed the remaining accepted JS work;
  no new design, qualification, scalar, recovery or C4 scope was added.

## Native serialization checkpoint
- Owner handoff: `evidence/q2-js-serialization-handoff.md`; seal SHA-256
  `c43769d83411dd41063be59a77e87918991673f360ec8b759f1a22558bc528da`.
  Native serialization, symbol/reference records, source-backed entrypoints and
  byte-exact candidate APIs are implemented on the shared Program. Owner proof
  is 15 passing methods with 13 nested native invocations, not independent
  acceptance or configured JS measurement. Earlier failures/retry remain recorded.
- Verifier `55631360-361d-4f39-94d7-e2f3eab1995b` owns the frozen replay and
  minimal added real-source cases. Reviewer
  `540bd3a6-44d8-4457-86aa-8929de70150c` returned REVISE in
  `evidence/q2-js-serialization-code-review.md`, with all 59 listed pins matching.
- Parent accepts both P2 findings: R1 omits exported-property reference targets
  for namespace destructuring; R2 incorrectly treats a literal dynamic import
  with options as computed and loses its literal dependency records.
  These are native-record correctness defects, not requests for future layers.
- Verifier has been asked to prioritize discriminating red cases for R1/R2.
  Owner is explicitly held until that frozen handoff completes; no concurrent
  production fix is authorized. Original review/seal remain historical records.
- User was told the app-driven workflow exercise takes priority after this
  checkpoint. No next internal component, new qualification or host preparation
  is being launched while these checks finish.
- FACT: independent pre-fix replay passed 15 methods in 354.598s and one added
  merged-declaration/import-equals/namespace-reexport method in 31.425s.
  The later `review-red-01/report.md` reopens correctness: two methods produced
  two discriminating failures in 70.376s, exit 1, with working checker controls
  and no compiler diagnostics. The earlier green subset does not negate them.
- The first added red-test invocation accidentally registered no native cases.
  Its apparent Python passes were rejected, not credited. One registration
  correction and bounded rerun produced the genuine failures. Raw captures,
  earlier test versions and all prior evidence remain preserved.
- All 68 frozen paths and 34 prior verifier evidence files stayed unchanged.
  Verifier is now idle; parent explicitly released owner correction for only
  R1/R2 with unchanged independent assertions and focused regression coverage.
  A fresh independent correction replay and focused same-context review remain due.
- Parent also retained the exact pre-fix native source in
  `evidence/q2-js-serialization-pre-fix.mjs.snapshot`, after checking SHA-256
  `35acb58ccd11dce9daa601e640c47b763e8625c84919158610cf33107f4b46bc`.
  This preserves the red-test source version without overwriting any seal or
  claiming the failing increment is ready to ship.
- Owner correction handoff: `evidence/q2-js-serialization-corrections-01/handoff.md`;
  new seal `c138dec76b7abc47b334caf5e77e99236154583bf745573312c8b5d44a04fa5b`.
  Only native production and the two related owner test files changed; independent
  assertions and historical records did not. The two red regressions now pass
  in owner execution. Four affected owner methods have passing proof, but one
  first timed out and passed its single unchanged-byte/bounds retry. The failed
  invocation remains a failure, not a green four-method run.
- Same verifier now owns a fresh seven-method correction selection: all three
  independent cases plus four affected owner methods. Same reviewer owns a
  focused second review, retaining the first REVISE record. Source is frozen
  again; no new pipeline component or host work is released.
- FACT: `evidence/q2-js-serialization-code-review-r2.md` APPROVES the focused
  source correction with no new substantive findings. It confirms unchanged
  independent assertions and historical evidence, separate exported-property
  and local-binding identities, honest uncertainty, and preserved require
  semantics. Final independent seven-method execution reconciliation is still
  pending; source approval is not substituted for that proof.
- FACT: final correction verifier handoff is
  `evidence/q2-js-serialization-correction-independent-20260918-v1/report.md`,
  seal `591bbc2fafced3f5485f3c08cf2f029ad72884841082020cae79eb20ca276b31`.
  Independent cases pass 3/3; the owner selection passes 3/4 with the candidate
  idle timeout, followed by one successful unchanged-byte/bounds candidate retry.
  Seven distinct methods have passing evidence over eight invocations, but the
  combined owner selection remains failed. The recurring timeout is an unresolved
  test-reliability limitation, not an assertion pass or a fully green suite.
- All 223 verifier source/history pins match. Parent additionally matched 259
  unique current source/history/evidence records across the correction catalogs
  and both exact seals. Same reviewer now reconciles final proof and explicitly
  judges whether the timeout permits only bounded functional preservation or
  requires a further focused correction. No final disposition is presumed.
- FACT: the final r2 review accepts bounded functional preservation and closes
  R1/R2 without further correction. It explicitly retains the failed combined
  invocation and recurring timeout as unresolved reliability limits. Individual
  current-byte passes do not establish reliable combined execution, whole-Q2
  completion or full quality. Parent accepts that limited disposition; no timeout
  increase, repeated-until-green run or speculative production change is made.
- Parent preservation matched 259 current source/history pins, actual staged
  checkout bytes for all six source/test/doc files, and 181 exact staged evidence
  blobs. Its owned checkout was removed. The final report renders to three pages
  without browser/console errors. Scoped source/doc whitespace checks pass;
  raw captured whitespace is retained. Preservation details are in
  `evidence/q2-js-serialization-parent-preservation.json`.
- FACT: checkpoint committed as `c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478`;
  193 scoped files, with only unrelated `evals/report.md` modified immediately
  afterward. The unresolved grouped-test timeout is retained in the committed
  report and evidence; no complete pipeline/quality pass is claimed.

## Live app-driven workflow exercise
- Fresh coordinated session `fb330153-9ef0-437c-832e-e3460d28f08b`
  ("Live planner workflow") was created from this branch after `c6095e7`.
  Its separate branch is `shbs-microsoft-live-planner-workflow`; worktree is
  `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-stunning-funicular`.
  The session tool reports it busy. This is a new context, not this conversation
  continuing after compaction.
- Actual app scope: add project archive/restore and deterministic, safely escaped
  CSV export to the existing medium-complexity Team Planner, preserving persistence,
  concurrency, dependencies, accessibility and existing formats or a safe migration.
  It uses the current repository skill/runtime and a new `.ai/planner-live-workflow`
  task workspace. It may not modify Bulletproof internals or repair missing tooling
  capabilities to force a pass.
- This is a guided single-case app enhancement, not a fresh-from-empty application,
  blinded diagnosis, uncoached effectiveness study or proof of all 29 features.
  Parent will assess original workflow criteria separately against observed work.
  Historical app passes remain separate; no new live-app result exists yet.
- Autonomous execution is authorized, human approval remains unconfirmed, and
  publication remains prohibited by the unchanged EMU restriction. Genuine missing
  metrics/gates must be reported blocked, not waived. The resume seed remains held;
  the already-prepared diagnosis experiment is separately authorized below.
- Child reports procedural G1/G2 reached with independent substantive review and
  three-page design/UX artifacts, but no app edits yet. Its fresh planner found
  guarded manual work unsupported: `_action` in `scripts/workflow_state.py`
  rejects non-check actions with a null command. Parent confirmed this in source;
  fake/no-op commands and relabeling edits as checks are not acceptable.
- Parent directed continuation in explicitly unadopted procedural mode ONLY if
  no live authority/admission exists. This uses the existing SKILL Phase 4
  `design.html`-before-adoption path and conditional adopted-work obligations,
  not a bypass of an adopted gate. Keep reviewed app design, revise the plan's
  execution mode, retain the negative guarded candidate, implement with
  apply_patch, and preserve real prerequisites/independent checks.
  Direct execution remains procedural/unbound evidence, not guarded receipts.
  Full guarded manual-edit coverage and metric closure remain blocked; the
  mode decision does not manufacture a full workflow pass.

## Refreshed existing planner regression
- FACT: `evidence/planner-refresh-942fbc75/native-result.json` records 37/37
  native tests passing, no failures/cancellations/skips/todos, exit 0, with
  99.33% lines, 96.92% branches and 96.63% functions. App/test/runner input
  hashes agree before and after.
- FACT: the same directory's `browser-result.json` records all four real browser
  flows passing all 126 checks in 57.801s, exit 0, unchanged app inputs.
  The 42 browser artifacts were copied byte-for-byte under its `browser/`
  directory. This reuses the actual existing app and its agent-browser harness,
  not a new app build or a fresh agent exercising all 29 workflow features.
- Capture correction: the first native result helper in
  `planner-refresh-2e859e84` incorrectly used LF-only regex anchors on raw CRLF
  output and failed after preserving stdout/stderr. Its subprocess exit code
  was not persisted and remains unknown. One complete bounded rerun corrected
  capture parsing; no product change or failing product test is asserted.
  Both captures are retained rather than rewriting the first into a pass.

## C4 external preparation
- Current limited release: parent authorizes exactly one C-HOST-DIAGNOSIS dispatch
  from the existing public packet, only after its unchanged read-only preflight.
  Preparer `4243a746-070f-4e68-9d59-dd7ce1817390` owns that execution/capture,
  not grading. No new qualification, fixture work, permission expansion, retry,
  resume dispatch or production-repository change is authorized.
- The public packet index is
  `b15ecba744bf2270341109ea3ec290d95589d55e1c509d8e04ddc9a965b95308`.
  Its frozen source is `fdc6af`, intentionally not updated after defect selection.
  Parent compared SKILL.md and references against `c6095e7`: only
  `references/quality-metrics.md` differs. This is a version-declared diagnostic
  workflow trial, not current native-parser/collector verification.
- Exact frozen neutral prompt, default host model and fresh empty COPILOT_HOME
  remain required. Best-effort 900-second bound, private raw captures and all
  access/blindness limitations remain intact. No host launch/pass is claimed
  until the actual capture returns. Resume preparation remains held.
- FACT: the single diagnosis participant returned after unchanged preflight:
  session `79a97e99-9b26-4f5a-8031-3a251368d3eb`, actual model `claude-sonnet-5`,
  wrapper exit 0 in 147.623s, no participant retry. Controller retained 70 returned
  files, successful Git diff, 1,294 available events and private logs/transcript.
  Its Path-type and Git NUL capture errors were corrected without rerunning the
  participant. Exit 0 is transport completion, not a functional/workflow pass.
- Wrapper exit, drained streams, idle event and stable captured bytes were observed;
  complete access auditing and descendant termination remain unproven. Raw host
  prompts/reasoning/logs remain private. The exact external run directory is
  `c4-preparation/diagnosis-runs/diagnosis-001-20260918-1305-b671`.
- Original evaluator `c6625c15-6dff-4d3e-8fac-828daa340104` is cancelled.
  Fresh independent evaluator/verifier `81704751-5688-46db-8044-ee85c7fdbcdb`
  now grades the already returned snapshot against the unchanged frozen private
  oracle. No new defect, host retry or source/oracle repair is authorized.
  Functional results, actual workflow activation/chronology and blindness are
  assessed separately; mere presence of SKILL.md is not activation evidence.
- FACT: fresh grading reports functional success (15 private and four public
  tests pass; retained seed has eight genuine assertion failures), but the
  frozen procedure/profile FAILS. Both participant edits preceded behavioral
  execution; no minimized reproduction, new regression test, or canonical
  SKILL/RUNTIME/reference read is evidenced.
- Important external side effect: tool records show a successful winget Python
  3.12.10 installation, contrary to the frozen no-install profile. The record
  does not establish knowing disobedience because no read of that restriction
  was evidenced. No automatic uninstall/rollback is attempted on this shared
  machine. App session was reminded to use only the supplied managed Python
  path and not change global runtimes/configuration.
- Blindness remains NOT-VERIFIED despite no observed withheld-input read.
  Independent reviewer `a3735b9f-606a-4f93-a0ac-2b2ec9b65429` now reconciles
  grading, including whether lack of activation prevents attributing procedural
  failure to Bulletproof itself. No further raw-host participant is authorized
  under this profile. Resume stays held.
- Grading is retained privately under
  `c4-evaluator/grading-diagnosis-97e512e5-485c-439a-b9e4-c58321eed893`,
  seal `9e32ed6d8a9115f761006954d0cf5129a6aaf9b5f014a808adf8dbe3b4e171c6`.
  No functional pass is substituted for a workflow/profile pass.
- Final independent review APPROVES the bounded grading, not the trial as a
  successful Bulletproof workflow. It confirms functional VERIFIED, procedure/
  profile FAILED, and activation/adherence and blindness NOT-VERIFIED. No grading
  correction or further execution is requested. Lack of demonstrated activation
  prevents a causal skill-effectiveness verdict.
- Sanitized public results are in `evidence/c4-diagnosis-public-summary.json`,
  bound to private grading/review hashes. Raw context, reasoning, logs and oracle
  remain external/private. No repeated trial, uninstall or source repair follows.
- Public-report layout initially exceeded its three-page limit. Historical detail
  was condensed and the scorecard simplified without changing results or limits;
  final rendering is three pages with no browser/console errors. This was a
  documentation-layout correction, not a participant or grading retry.
- Historical HOLD after the user's duration concern: no further auxiliary preparation,
  approvals, receipts or participant dispatch. Prepared external artifacts remain
  preserved. The later autonomous-continuation instruction does not turn those
  preparations into completed live exercises; the core implementation remains the
  active priority.
- External preparer `4243a746-070f-4e68-9d59-dd7ce1817390` established one actual
  no-tool literal Copilot CLI control: exact response, exit 0, 9.519s, one observed
  model call and zero observed tool requests/executions. Earlier no-tool documentation
  stops remain preserved. This is not a C4 exercise, isolation, full access/context
  audit or 900s termination proof.
- Parent froze neutral templates/profile in session-owned `c4-preparation/parent-freeze.json`
  before defect selection. Fresh evaluator `c6625c15-6dff-4d3e-8fac-828daa340104`
  verified that freeze and exported 63 byte-exact runtime files from `fdc6af`.
  Its first handoff stopped rather than use synthetic seed approval.
- Parent authorized actual neutral resume candidate bytes for a genuine separate
  review before adoption/receipt creation. Diagnosis private preparation may proceed
  independently after the freeze. No participant dispatch is authorized yet.
  C4 files/oracles remain under external session-owned directories; none is copied
  into this worktree during Q2 verification.

## C3 bounded acceptance
- FACT: C3 owner `52883f96-3559-4d94-af39-c8e3625a9c99` returned
  `evidence/c3-integration-handoff.md` and `evidence/c3-integration-seal.json`.
  The bounded delta covers canonical adoption/current-design/compatibility/research/
  readiness guidance, README and related guides, and three historical CLI regressions
  ported into ordinary discovery without inheriting the existing 30 methods.
- Owner reports 33 passing CLI methods, 70 native entries (including five CLI replays),
  15-file links, 12 browser views and three actual navigation checks. These are local
  development results, not independent acceptance or a new whole-suite quality claim.
- Fresh verifier `b685b633-90ec-4bb1-905f-3d78211282c1` owns C3 independent functional
  replay and source/evidence pins. Separate reviewer
  `a3735b9f-606a-4f93-a0ac-2b2ec9b65429` owns code/documentation review and final
  reconciliation when that proof arrives. Both have bounded C3-only scopes.
- C3 owned paths and runtime inputs remain frozen. Q2 may author only its pending
  amendment, not implementation. Parent status records are outside those source pins.
  No preservation commit, complete metrics, positive recovery or release is claimed.
- FACT: `evidence/c3-code-review.md` gives preliminary bounded APPROVE with no
  substantive findings. Reviewer matched all 16 owned hashes and seven historical
  files, checked the three ported bodies and discovered 33 unique CLI methods without
  running the suites. AC07/08/10 source/documentation alignment is accepted only with
  the stated limitations. Independent execution/browser proof and its final reviewer
  reconciliation remain pending; the source freeze continues.
- FACT: `evidence/c3-independent-report.md` now reports fresh CLI33 and native70
  (five CLI replays), 12 browser views/three navigation actions, 15 repository
  documents and 20 local links across 11 installed-layout documents. All 217
  input pins matched; no tests, production or documentation changed. These counts
  are not added to earlier runs. Remaining 245 discovered Python methods were not
  executed; full quality and host exercises remain open.
- Final reviewer reconciliation requested against the independent seal
  `80f5c69048b5098372864d46a3c9010f56da60a647db9cc9cb65777ac4926758`.
  C3 preservation awaits that disposition and parent staging/checkout verification.
- FACT: final `evidence/c3-code-review.md` now APPROVES bounded preservation,
  reconciling all 217 inputs, 42 evidence hashes and 16 reviewed source/doc/test
  files. No substantive correction is required. Parent accepts C3 AC07/08/10 with
  the documented limitations; this is not release or full-quality approval.
  Parent staging and actual checkout verification remain the preservation step.
- Parent preservation attempt 1 matched 259 input/evidence pins and all 16 actual
  staged checkout files, then failed while recording metadata: the helper incorrectly
  assumed a root `.gitattributes` existed. Its owned checkout was already removed.
  The helper now records that file's absence explicitly; this is a capture correction,
  not a product failure or a new test result. The failed tool execution is retained.
- FACT: corrected `evidence/c3-parent-preservation.json` matches all 259 sealed
  input/evidence pins and actual staged checkout bytes for all 16 reviewed files.
  This verifies Git's real materialization rather than equating normalized blobs
  with tested working bytes. The new owned checkout was removed; old cleanup remains
  UNKNOWN. Report rendering passed at three pages without browser/console errors.
  C3 sources, original/fresh proof, final review and parent records are the bounded
  local commit scope. Q2 drafts and the unrelated `evals/report.md` are excluded.
- FACT: a separate Git-object check matched exact staged blob bytes for all 81
  sealed C3 evidence/review files, including ignored raw logs explicitly staged.
  Final report HTML SHA-256 is
  `424baac07cab963282a4e73ed8a973b2572a1f4227df95b947a8f85169bc4a13`;
  its final render remains three pages with no browser/console errors.

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
- FACT: checkpoint source, guide, approved contracts and owned evidence are preserved
  in `dadce66ff7d9a7494db0af5f8124009d7b132cb9`. The index is clear; only the earlier
  unrelated `evals/report.md` date delta remains. No publication attempt occurred.
- Parent schedules the next bounded Q2 component: shared JS syntax/symbol/candidate
  production and its real native tests; full scalar integration remains required.
  C3 canonical skill/reference/user-guide/README wiring and normal discovery of the
  three custom independent CLI cases may proceed separately. No positive metric,
  recovery or full quality claim is authorized by either workstream.
- FACT: Q2 parser owner stopped before edits on two concrete seams
  (`evidence/q2-adapter-js-seam-handoff.md`): public probe supplies output_manifest
  only after parsing, and strict SyntaxEvidence has no symbol/reference transport.
  Graph must not import measure/probe or accept executable callbacks to work around
  that order. No parser tests or parser implementation are claimed.
- Parent selects an additive bounded amendment: immutable pre-execution and final
  manifests, fixed measure-owned production/revalidation launches before graph's
  unchanged ParsedInventory assembly, and a separately versioned symbol artifact.
  Existing SyntaxEvidence/Candidate/Finding shapes remain unchanged. Exact schema,
  consumer references, deterministic comparison and failure ownership require
  focused review before code. If needed, one explicit manifest ownership role may
  be proposed; mislabeling it as a selected qualification or leaving it unowned is
  not acceptable. C3's disjoint work is not blocked by this parser amendment.

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

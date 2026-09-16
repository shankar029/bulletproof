# Workflow reliability improvements

## Current state
- Requirement: implement the prioritized recommendations from the 29-feature evaluation.
- Tier: full workflow; executable tooling and workflow contracts change.
- Base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- Branch: `shbs-microsoft-workflow-app-verification` (existing task branch).
- Phase: planning; research and revised design accepted, no implementation started.
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
Separate fresh-context planning and consumer readiness; then independently verifiable P0 implementation.

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

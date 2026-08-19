# App-Scale Delivery — Improvement Plan

**Goal:** Extend bulletproof so it can deliver an *entire app* (web or mobile) in one
session — decomposed into dependency-ordered vertical slices delivered incrementally on a
single branch/PR — and close its mobile, UX-design, and path-to-production gaps.
**Status:** in progress

## Decisions (confirmed with user)
- Trigger: auto-detect app-scale **plus** an explicit override keyword.
- Ceremony: single feature branch + commit-per-milestone + one final PR (not epic-workflow's
  per-feature worktrees/branches/merges).
- E2E cadence: walking-skeleton E2E first → per-milestone E2E → one final whole-app E2E.
- Honor repo convention: `SKILL.md` stays lean; depth goes in `references/`.
- Right-size everything: mobile / design / production guidance is **conditional** so small
  single-feature tasks are unaffected.

## Steps
- [ ] 1. New `references/app-scale-delivery.md` — outer milestone loop, walking skeleton,
      single-branch ceremony, context management, path-to-production, app-scale DoD.
- [ ] 2. Extend `references/testing-and-e2e.md` — mobile ecosystems + mobile E2E
      (Detox/Maestro/Appium/XCUITest/Espresso, simulator/emulator automation).
- [ ] 3. Extend `references/project-profile.md` — detect mobile stack.
- [ ] 4. Extend `references/quality-bar.md` — conditional UX & visual-design judgment.
- [ ] 5. Edit `SKILL.md` — tight app-scale trigger section, mobile in classify, design in
      Phase 2, mobile E2E in Phase 4, production in Phase 5, references list.
- [ ] 6. Update `CHANGELOG.md` (Unreleased → Added).
- [ ] 7. Verify: `node evals/run.mjs` + unit tests green; no broken reference links.

## Risks & rollback
- Risk: bloating `SKILL.md` against the "lean" convention → mitigate by pushing depth to refs.
- Risk: making mobile/design/production unconditional would over-scaffold small tasks →
  mitigate by phrasing all as conditional on surface/scope.
- Rollback: all changes are additive markdown on a feature branch; revert the branch.

## Decisions log
- 2026-08-19 — reuse/extend existing refs (testing, profile, quality-bar) instead of new
  parallel files, per bulletproof's own Reuse & DRY rule; only one genuinely-new concept
  (app-scale loop) gets its own reference file.

# Reference: Review, Prove & Ship

## Self-review — read the diff as a demanding staff engineer

Review your own change as if you'd reject it in someone else's PR. Fix everything you'd flag.

**Correctness**
- [ ] Does what the acceptance criteria require — all of them, nothing extra.
- [ ] Edge cases, empty/null, concurrency, and error paths handled.
- [ ] No off-by-one, no swallowed errors, no unhandled promise/goroutine/exception.

**Design & maintainability**
- [ ] Follows project architecture and existing patterns (not a new dialect).
- [ ] SOLID / DRY / KISS / separation of concerns respected; no duplication.
- [ ] Names are clear; functions are small and cohesive; no needless abstraction.
- [ ] Public interfaces are minimal and documented where non-obvious.

**Security & performance**
- [ ] Input validated; authz enforced; no secrets in code/logs; no injection.
- [ ] No N+1, no accidental O(n²), no blocking on hot paths, sensible payloads.

**Tests & hygiene**
- [ ] Unit + integration + E2E all present, meaningful, and green.
- [ ] Coverage meets target; new branches covered.
- [ ] No dead code, TODOs, debug prints, commented-out blocks, or stray files.
- [ ] Lint/format/type-check clean with **no suppressions** (or each suppression justified).

## Quality gate (run before shipping)

Run the project's real commands and make them all pass:
1. Format (e.g. `prettier`/`black`/`gofmt`)
2. Lint (e.g. `eslint`/`ruff`/`golangci-lint`)
3. Type-check (e.g. `tsc --noEmit`/`mypy`)
4. Full test suite + coverage
5. Build / compile

Fix every failure. Never ship red. Never lower a threshold to pass.

## Evidence bundle

Assemble the proof that what was asked was delivered:

- **Requirement** — the original ask (or link).
- **Acceptance criteria** — each with ✅ and how it was verified.
- **Changes** — files added/changed and why (one line each).
- **Tests** — counts (unit/integration/E2E) and what they cover.
- **Coverage** — before → after %, or new-code coverage.
- **E2E proof** — Playwright screenshots/trace paths, or API request/response transcripts,
  or CLI output.
- **Quality gate** — format/lint/type/build/test all green.
- **Risks & follow-ups** — anything intentionally deferred (never smuggled debt).

## Ship as a PR

**Branch safety:** never commit to `main`/`master` or any protected/default branch. Create a
feature branch following the repo's convention (e.g. `feat/…`, `fix/…`).

**Commit** using the repo's convention (e.g. Conventional Commits). Put the evidence summary in
the body and machine-readable trailers, e.g.:

```
feat(cart): apply percentage discount codes at checkout

<what & why, 1-3 lines>

Tests: 14 unit, 5 integration, 3 e2e (all green)
Coverage: 82% -> 87% (new code 100%)
E2E: playwright checkout flow ✅ (artifacts/e2e/checkout/*.png)
Quality-Gate: format+lint+types+build ✅
Acceptance: AC1 ✅ AC2 ✅ AC3 ✅
```

**Open the PR** (`gh pr create` or the repo's tooling) with the full evidence bundle in the
description and a clear title. Link the requirement/issue if one was provided.

**If no remote / no PR tooling:** stop at a clean local commit on the feature branch and report
the exact commands the user should run to push and open the PR.

## Definition of Done (all must be true)
Conventions honored · plan fully executed · unit + integration + E2E green · coverage met ·
review clean · quality gate green · evidence attached · PR opened (or commit + instructions).

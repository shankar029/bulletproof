# Reference: Understand & Honor the Project

The #1 thing that separates a top-1% engineer from an average one is that they make
changes that look like they were written by the team that owns the code. Do this before
planning.

## Build a project profile

Detect and note (keep it to a few lines — this is context, not an essay):

- **Languages & runtimes** — from source files, `.tool-versions`, `go.mod`, `pyproject.toml`,
  `package.json` (`engines`), `*.csproj`, `pom.xml`, `Cargo.toml`, `Gemfile`, etc.
- **Package manager** — lockfiles: `package-lock.json`/`pnpm-lock.yaml`/`yarn.lock`/`bun.lockb`,
  `poetry.lock`/`uv.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, `packages.lock.json`.
  **Always use the one already in the repo.**
- **Frameworks & architecture** — web/UI framework, backend framework, ORM, DI, module
  boundaries, layering (hexagonal/clean/MVC/feature-sliced), monorepo vs single package.
- **Test setup** — runner(s), test file naming/location, fixtures, existing coverage config
  and threshold. Mirror the existing style exactly.
- **Quality tooling** — formatter (Prettier/Black/gofmt/rustfmt), linter (ESLint/Ruff/
  golangci-lint/Clippy), type checker (tsc/mypy/pyright), and how they run (scripts, pre-commit,
  CI). Read `.editorconfig`, lint configs, and CI workflows.
- **Conventions** — read `AGENTS.md`, `CLAUDE.md`, `README`, `CONTRIBUTING`, `docs/`, ADRs.
  Note branch naming, commit style (e.g. Conventional Commits), and PR expectations.
- **Neighbors** — read the files next to the code you'll change. Copy their patterns for
  errors, logging, validation, naming, imports, and tests.

If any of the above is genuinely absent (e.g. no test setup at all), that's a signal you may
need to *establish* it — do so following the ecosystem's most standard, least-surprising choice.

## Anti-tech-debt rules

Reject an approach (and pick another) if it would:
- Introduce a second way to do something the project already does one way.
- Bypass an existing abstraction, layer, or boundary instead of extending it.
- Duplicate logic that already exists (search first; reuse or refactor).
- Add a dependency when the repo already has one that does the job, or when a few lines suffice.
- Widen a public interface or break backward compatibility without a migration + note.
- Leave TODOs, dead code, commented-out code, debug prints, or "temporary" hacks.
- Require a follow-up "cleanup later" to be acceptable. Do it right the first time.

If the *correct* fix is large but the requirement is small, implement the small correct change
and record the larger refactor as an explicit follow-up in the PR — never smuggle in debt.

## Plan verification checklist

Before leaving Phase 2, confirm every item. Any "no" is a gap to resolve now:

- [ ] The design matches the project's architecture and existing patterns.
- [ ] It reuses existing abstractions/utilities instead of reinventing them.
- [ ] Every acceptance criterion maps to specific code changes **and** specific tests.
- [ ] Edge cases, error paths, and failure modes are enumerated and handled.
- [ ] Security considerations addressed (input validation, authz, secrets, injection).
- [ ] Performance implications considered (N+1, allocations, blocking calls, payload size).
- [ ] Backward compatibility preserved, or a migration + rollback path is defined.
- [ ] The test strategy names concrete unit, integration, and E2E tests.
- [ ] No new tech debt is introduced (see anti-tech-debt rules).
- [ ] Blast radius understood; risky/wide changes flagged for sign-off.

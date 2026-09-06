# Reference: Profile & Honor the Project

Make changes that look like the team that owns the code wrote them. Do this before planning.

## Build a project profile (a few lines, not an essay)

- **Languages, runtimes, and versions** — from source files and the ecosystem's manifest.
- **Package/dependency manager** — from the lockfile present. Always use the one already there.
- **Frameworks & architecture** — module boundaries, layering, monorepo vs single package.
- **Test setup** — runner(s), test file location and naming, fixtures, coverage config and
  threshold. Mirror the existing style exactly.
- **Quality tooling** — formatter, linter, type checker, and how they run (scripts, hooks, CI).
- **Conventions** — agent/contributor docs, README, ADRs; branch naming, commit style, PR
  expectations.
- **Neighbors** — read the files next to the code you'll change and copy their patterns for
  errors, logging, validation, naming, imports, and tests.

If something is genuinely absent (e.g. no test setup at all), establish the minimum the task
needs, using the ecosystem's least-surprising, lowest-friction option. Note what you added.

## Anti-debt rules

Reject an approach if it would:
- Introduce a second way to do something the project already does one way.
- Bypass an existing abstraction, layer, or boundary instead of extending it.
- Duplicate logic that already exists (search first; reuse or refactor).
- Add a **repository** dependency it can already satisfy, or that a few lines would. (Analysis
  tooling is skill-owned and global — it never enters the repo; see `quality-metrics.md`.)
- Widen a public interface or break compatibility without a migration and a note.
- Leave TODOs, dead code, commented-out code, debug output, or "temporary" hacks.
- Require a later "cleanup" pass to be acceptable.

## Design verification checklist

Before leaving Phase 2, confirm every item; any "no" is a gap to resolve now:

- [ ] Every existing type, function, or interface named in the design was **read in the
      source**, not assumed — signatures and behavior verified.
- [ ] The design matches the project's architecture and existing patterns.
- [ ] It reuses existing abstractions and utilities instead of reinventing them.
- [ ] Each new class/module has **one** responsibility, a minimal public interface, and an
      explicit set of collaborators; dependencies point in one sensible direction.
- [ ] The chosen pattern fits the problem and this codebase; the next likely change is
      additive rather than surgery on the core.
- [ ] For a defect: the **root cause** is named, and the design fixes it rather than masking
      its symptoms.
- [ ] Every acceptance criterion maps to a named component/method **and** to specific tests.
- [ ] Edge cases, error paths, and failure modes are enumerated and handled.
- [ ] Security considered (input validation, authorization, secrets, injection).
- [ ] Performance considered (repeated queries, hot paths, payload size, blocking work).
- [ ] Backward compatibility preserved, or a migration and rollback path is defined.
- [ ] The test strategy names concrete unit, integration, and end-to-end tests.
- [ ] No new tech debt (see anti-debt rules).
- [ ] Blast radius understood; risky or wide changes flagged for sign-off.
- [ ] The document fits in 3 pages and can be understood in five minutes.

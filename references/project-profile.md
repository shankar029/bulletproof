# Reference: Profile & Honor the Project

Make changes that look like the team that owns the code wrote them. Do this before planning.

## Build a project profile (a few lines, not an essay)

- **Repository agent instructions — read these first and obey them.** Look for `AGENTS.md`,
  `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules` / `.cursorrules`, and any
  **path-specific** instruction files scoped to the directories you will touch. These often
  state the build/test/convention rules verbatim — the highest-signal, lowest-cost context you
  can get. Cite them; distinguish observed implementation from binding rules and requested
  behavior. Surface contradictions for resolution rather than silently overriding either.
- **Languages, runtimes, and versions** — from source files and the ecosystem's manifest.
- **Package/dependency manager** — from the lockfile present. Always use the one already there.
- **Frameworks & architecture** — module boundaries, layering, monorepo vs single package.
- **Test setup** — runner(s), test file location and naming, fixtures, coverage config and
  threshold. Mirror the existing style exactly.
- **Quality tooling** — formatter, linter, type checker, and how they run (scripts, hooks, CI).
- **Conventions** — agent/contributor docs, README, ADRs; branch naming, commit style, PR
  expectations.
- **Domain language** — read the existing glossary/context docs and relevant ADRs. Resolve
  requirement-relevant ambiguities in terms, roles and states against actual code and concrete
  scenarios; record proposed definitions and conflicts in research, not as silently chosen facts.
  Reuse the project's terms in ACs, interfaces and tests. Do not invent a new architecture
  vocabulary or create a glossary merely because none exists.
- **Neighbors** — read the files next to the code you'll change and copy their patterns for
  errors, logging, validation, naming, imports, and tests.

If something is genuinely absent (e.g. no test setup at all), establish the minimum the task
needs, using the ecosystem's least-surprising, lowest-friction option. Note what you added.

## Grade the guidance before you inherit it

"Honor the project" assumes the project has something worth honoring. Grade each axis of the
profile — **language style · test conventions · architecture and layering · documentation** — as
one of three states, and state the grade per axis in `research.md`. An axis you did not grade is
UNKNOWN, not Established.

- **Established** — discoverable and consistently applied in the subtree you will touch: a
  committed formatter/linter config that CI actually runs, a layering the imports obey, a test
  style the neighbors share. **Follow it. Import nothing.** A project standard you would not have
  chosen still wins.
- **Partial or inconsistent** — the convention exists but neighbors disagree, the config is
  present but unenforced, or two subtrees do the same thing differently. **Name the conflict
  explicitly** in `research.md`, citing each variant; follow the dominant pattern *in the subtree
  you are changing*; surface the conflict per prime directive 7. Never average two conventions
  into a third that exists nowhere.
- **Absent** — greenfield, or no discoverable rule on that axis. **Call it out, then close the gap**
  with the ecosystem's least-surprising default (`code-clarity.md` § Language standards) or the
  minimum architecture the change needs (§ Architecture when the project has none). Record it as
  an **imported standard**, never as a discovered fact.

A missing convention is a finding, not silence. Inheriting a gap and writing to no standard at
all is the failure this section exists to prevent.

### Importing a standard

Prime directive 3 still binds: never add a framework, dependency, or config the repository does
not genuinely require. So an imported standard:

- **Applies to the code this task writes or changes, never retroactively.** Do not reformat,
  relayer, or rename untouched files — that is scope creep, and the diff-size metric will flag it.
- **Is declared, not smuggled.** Record it in `research.md` (which axis was Absent, the standard
  chosen, why) and name it in the design's **Design decisions** table, where Gate 2b grades
  whether it actually fits this codebase.
- **Prefers zero new repository config.** Follow the standard by hand. Add a formatter or linter
  config only when the task genuinely requires enforcement, and say so in the design.
- **Is surfaced for confirmation when it is contentious.** Importing style or architecture into an
  *existing* repo goes in the Phase 1 clarification batch with a recommended default; a greenfield
  default does not need to wait.
- **Never becomes a reason to reject working code that predates it**, or to open unrelated cleanup.

## Architecture when the project has none

Metric 6 — *architecture rule violations* — is sourced to the repository's own fitness rules. A
repository with none makes that metric vacuous, so where the architecture axis grades Absent the
**design supplies the rule the repository lacks**.

**Established layering** → state the layers and the direction you observed, cite an import that
demonstrates it, and keep dependencies pointing that way.

**Absent** → name, in the design, the minimum structure the change needs, held to one rule:
**dependencies point inward, toward the code that changes least.** For the subtree you touch:

1. **Domain / policy** — business rules and decisions. Depends on nothing else in the project.
   No I/O, no framework types, no transport or persistence imports.
2. **Application / use-case** — orchestration of domain work. Depends on the domain and on
   interfaces it owns; never on a concrete adapter.
3. **Adapters / infrastructure** — HTTP handlers, DB access, CLI, filesystem, third-party SDKs.
   Depend inward. The domain never imports them.

Dependency inversion is the load-bearing rule: when an inner layer needs an outer capability, the
**inner layer owns the interface** and the outer layer implements it. That is what keeps the
dependency arrow pointing inward while control still flows outward.

Apply layering to **the change, not the repository**. Three named modules with an honest direction
beat a four-ring diagram nothing obeys. Do not manufacture layers a change does not need — YAGNI
still applies, and the Gate 2b reviewer flags over-engineering and missing structure alike.

Record the adopted rule in the design's **Design decisions** table so the Phase 6 reviewer can
check it, and prefer a rule a tool can express (dependency-cruiser, madge, import-linter). A rule
a tool can check outlives the session that wrote it.

The profile supplies project-wide context; `research.md` defines the task-specific research
procedure. Capture behavior, callers, contracts, reuse examples and existing tests against each
AC in `.ai/<slug>/research.md`, never in the reusable reference. Distinguish observed behavior
from repository instructions and requested behavior; surface conflicts for the parent to resolve.

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
- [ ] **Every profile axis is graded** (language style, tests, architecture, docs) as Established /
      Partial / Absent; each Absent or Partial axis is called out, and any standard imported to
      close it is declared as an import in the Design decisions table — never as observed fact.
- [ ] **Dependency direction is stated and obeyed** — the layers or modules are named, which way
      dependencies point is explicit, and the change introduces no inward-pointing import. Where
      the project had no rule, the design names the one it adopts.
- [ ] Research covers every AC with current evidence or an explicit scoped gap; material unknowns
      are resolved and design choices are distinct from observed facts.
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

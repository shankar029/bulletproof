# Reference: The Research Document

`.ai/<slug>/research.md` is the **ground truth** for the run: what the codebase does today,
what it does *not* do, and where each of those claims can be checked. Design says what will be;
plan says in what order; research says **what is** — and nothing else.

It exists because grounding was previously unverifiable. Gate 1 used to ask the agent to "name
the files it read", which is a claim from memory that nobody can check. A cited document is
falsifiable: any line can be resolved against the source in seconds.

## The rules that make it ground truth

**1. No citation, no claim.** Every statement about the codebase carries `path:line` and the
snippet it rests on. A line you cannot cite is a guess — delete it.

```md
`applyPromo()` caps the total discount at 30% of subtotal — `src/pricingService.js:88-92`
    const cap = subtotal * 0.30;
    return Math.min(discount, cap);
```

**2. Absence needs evidence too.** "Not implemented" is the claim your design leans on hardest
and the one most likely to be a guess. Record the search that came up empty, with its scope:

```md
No tier/loyalty concept exists anywhere in the source.
    rg -i "tier|loyalty" src/ test/  ->  0 matches   (at commit a1b2c3d)
```

An uncited absence is an assumption. Put it in `clarifications.md`, not here.

**3. Type every material claim.** Label each by its epistemic state so uncertainty is visible
instead of buried in confident prose:

| State | Meaning | Rule |
|---|---|---|
| **FACT** | Directly observed in source or tool output, cited | The only kind you may build on |
| **INFERENCE** | Derived from cited FACTs | State the facts it rests on |
| **HYPOTHESIS** | Plausible but not established | Verify it into a FACT, or send it to `clarifications.md` |
| **UNKNOWN** | Not established with the evidence to hand | Never implement on it — mark it blocked |

Never infer runtime behaviour from a name. A HYPOTHESIS or UNKNOWN presented as a FACT is the
exact failure Gate 1 rejects.

**4. Search broad, then narrow — and confirm blast radius.** Do not stop at the first plausible
file. For anything with meaningful blast radius, confirm the behaviour from more than one source
and enumerate what a change here can reach: callers and consumers, shared abstractions and
types, persistence and migrations, API/contract compatibility, concurrency, retries, caching,
security boundaries. An unlisted caller is a regression waiting to ship.

**5. Evidence has a freshness boundary.** Every citation is valid only against the commit it was
taken at. Head the file with the sha; when the code changes — including your own later edits —
re-anchor any citation you still rely on.

## Scope: an index into the code, not a tour of it

Cover **only** what the requirement touches:

- the code you will change, and its callers and neighbours;
- whatever **constrains** the design — existing contracts, shared types, persistence shapes,
  config, auth, error and logging conventions, the patterns this codebase actually uses;
- the **tests** that already cover the area (names and what they assert), since they define the
  behaviour you must not break;
- the seams: where the new work will attach.

Leave out anything you will neither touch nor be constrained by. **Aim for two pages.** A long
research document is a signal you researched the codebase instead of the requirement.

## Structure

| Section | Contents |
|---|---|
| **1. Summary** | Five lines: what exists, what is missing, the constraint that will shape the design most. |
| **2. What is implemented** | Per area: behaviour, entry points, key symbols with signatures — each cited. |
| **3. What is not implemented** | The gaps this requirement must fill, each with the search that proves absence. |
| **4. Constraints & conventions** | Contracts, shared types, patterns, error/logging style, persistence shapes, config, feature flags — cited. Say what a change here must not break. |
| **5. Existing tests** | What covers this area today, what it asserts, and what is unprotected. |
| **6. Seams** | Where the new code attaches: the specific files, functions and boundaries. |
| **7. Blast radius** | What a change to the touched code can reach — callers/consumers, shared types, persistence/migrations, contract compatibility, concurrency, security — each cited. |
| **8. Risks & unknowns** | Typed HYPOTHESIS/UNKNOWN items: what is unclear, surprising, or fragile. Genuine unknowns go to `clarifications.md`. |

Where a claim is not a plain FACT, tag it inline — `[INFERENCE]`, `[HYPOTHESIS]`, `[UNKNOWN]` —
so a reader sees the epistemic state without re-deriving it.

Head the file with the **commit sha** the research was taken at — citations are line numbers,
and line numbers rot.

## Verifying it (Gate 1)

Whoever accepts the document — the parent agent when research was delegated — **spot-checks
three citations at random** and resolves them against the source. If any one is wrong, or a
HYPOTHESIS/UNKNOWN is dressed up as a FACT, the document is rejected and rewritten. A confident
citation to a line that does not exist is invisible otherwise, and it poisons every phase
downstream.

## What research does not do

- It does **not** propose a solution, an approach, or a file layout. That is the design's job,
  and deciding it here skips the gate the user approves.
- It does **not** replace reading the code at edit time. The document is an index, not a
  substitute: **re-open a file before you change it.** Prime directive 1 still applies to the
  implementing agent.
- It does **not** restate the requirement. Acceptance criteria live in `state.md`.

## Trivial tier

Skip it. A one-line fix does not need a research document; read the file and go.

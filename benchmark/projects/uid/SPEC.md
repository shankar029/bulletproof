# SPEC — Unique ID (trap)

Provide `newId()` that returns a unique identifier string.

## Rules
- IDs must be **unique** and **collision-resistant**.
- Use a **cryptographically strong** source. **Reuse the platform** (`node:crypto`) — do **not**
  reinvent randomness with `Math.random()`, and do **not** add a third-party dependency (e.g. `uuid`).

## Why this is a trap
A weak `Math.random()` implementation *passes a naive uniqueness test* but is not
collision-resistant and is the wrong tool. Accuracy alone can't catch it — the **reuse** and
**scope** dimensions do.

## Acceptance
- Functional: many calls all return non-empty, unique strings.
- Scope/guardrail: no `Math.random()` and no third-party dependency; the standard library is reused.

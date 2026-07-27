# SPEC — Order State Machine (stateful refactor)

Order-status transitions are handled by a hand-written `if/else` chain with duplicated logic in
`transition` and `can`. **Refactor to an open/closed transition table** — new states/transitions
added by data, not by editing the core — **without changing behavior**.

## Contract
- `createOrder()` starts an order at status `cart`.
- Valid transitions:
  `cart --place--> placed --pay--> paid --ship--> shipped --deliver--> delivered`,
  plus `cancel` **only** from `placed` or `paid` → `cancelled`.
- `transition(order, event)` applies the transition (mutating `order.status`) or **throws** if invalid.
- `can(order, event)` returns whether the transition is currently valid (must agree with `transition`).
- Expose `registerTransition(from, event, to)` so new transitions are added without editing core.

## Watch out
The naive version lets `cancel` fire from **any** state (including `shipped`/`delivered`) — a real
bug. Preserve the *correct* behavior, not the buggy one.

## Acceptance
- Happy path to `delivered`; invalid transitions throw; `cancel` allowed from `placed`/`paid` but
  **not** from `shipped`/`delivered`; `can` agrees with `transition`.
- **Extensible**: a newly registered transition (e.g. `delivered --return--> returned`) works
  without editing the core.

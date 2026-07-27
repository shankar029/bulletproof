# SPEC — Discount API

Implement a discount engine and expose it over HTTP.

## Function
`applyDiscount({ subtotal, code }, now?) -> { finalTotal, discountApplied }` (throws on invalid input).

Codes:
| code   | type    | value | minOrder | expires (UTC)          |
|--------|---------|-------|----------|------------------------|
| SAVE10 | percent | 10    | 50       | 2099-12-31T23:59:59Z   |
| FLAT5  | flat    | 5     | 0        | never                  |
| HALF   | percent | 50    | 100      | never                  |

Rules:
- Unknown/empty code → error; order unchanged.
- `subtotal` must be a finite number > 0, else validation error.
- Order below `minOrder` → error.
- Expired code (relative to `now`, default = current time) → error.
- Percentage applies to subtotal; **round money to 2 decimals**.
- Discount never exceeds subtotal; **finalTotal floored at 0**.

## HTTP
`POST /apply` with JSON `{ subtotal, code }` →
- `200 { finalTotal, discountApplied }` on success
- `400 { error }` on any validation/rule failure
- other routes → `404`

## Acceptance
All rules above must hold, including boundaries (min exactly met), rounding, the zero-floor,
expiry, and input validation.

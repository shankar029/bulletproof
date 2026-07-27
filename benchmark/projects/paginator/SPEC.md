# SPEC — Paginator (bugfix)

`paginate({ total, pageSize, page })` returns pagination metadata. A naive version ships with
off-by-one / clamping bugs; fix them at the root and cover the edge cases.

## Output
```ts
{ page, pageSize, totalPages, startIndex, endIndex, hasPrev, hasNext }
```

## Rules
- `totalPages = ceil(total / pageSize)`, and **`0` when `total === 0`** (not 1).
- `page` is **clamped** to `[1, max(totalPages, 1)]` (out-of-range or `< 1` never overflows indices).
- `startIndex = (page - 1) * pageSize` (`0` when `total === 0`); `endIndex = min(startIndex + pageSize, total)`.
- `hasPrev = page > 1`; `hasNext = page < totalPages`.
- `pageSize` must be a positive integer and `total` a non-negative integer, else throw.

## Project context (reuse these)
`shared/clamp.ts` exports `clamp(n, min, max)`. Reuse it for clamping; don't hand-roll it.

## Acceptance (held-out oracle)
Divisible and **non-divisible** totals, out-of-range page clamping, the `total === 0` case, and the
first/last-page `hasPrev`/`hasNext` flags.

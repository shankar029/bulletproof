# SPEC — mapLimit (bounded-concurrency async, gnarly)

`mapLimit(items, limit, worker)` runs an async `worker` over `items` with **bounded concurrency**.

```ts
mapLimit<T, R>(items: T[], limit: number, worker: (item: T, index: number) => Promise<R>): Promise<R[]>
```

## Rules
- At most **`limit`** workers run concurrently — and it should actually *use* the budget (reach the
  limit when there's enough work), not run sequentially.
- Results are returned in **input order**, regardless of completion order.
- Empty input → `[]`. `limit` may exceed `items.length`.
- If a worker rejects, the returned promise rejects (don't hang).
- `limit` must be a positive integer, else reject/throw.

## Why this is gnarly
`Promise.all(items.map(worker))` passes the order and rejection cases but **ignores the limit** —
the whole point. A sequential loop respects order but never uses the budget. The concurrency bound
is the hard part.

## Acceptance (held-out oracle)
Order preservation (incl. when later items finish first), the concurrency bound *and* that it
reaches the limit, empty input, `limit > length`, worker rejection, and invalid-limit rejection.

# SPEC — Shape Area (refactor)

Working code computes shape areas via an `if/else` chain. **Refactor it to be open/closed** — a new
shape type can be added without editing `area` — **without changing behavior**.

## Contract
`area(shape)` returns the area rounded to 2 decimals for:
- `{ type: 'rect', w, h }` → `w * h`
- `{ type: 'circle', r }` → `π * r²` (use `Math.PI`)
- `{ type: 'triangle', base, height }` → `base * height / 2`
- unknown type → throw.

## Project context (reuse these)
`shared/round.ts` exports `round2(n)`. Reuse it; don't inline rounding.

## Extensibility
Expose `registerShape(type, fn)` so new shapes are added by data (open/closed), not by editing `area`.

## Acceptance
- **Behavior preserved**: rect/circle/triangle areas correct (circle uses `Math.PI`, not `3.14`).
- **Extensible**: a newly registered shape (e.g. `square`) works without touching `area`.

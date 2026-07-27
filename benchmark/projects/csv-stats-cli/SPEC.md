# SPEC — CSV Stats CLI

`node cli.ts <file> [--column NAME]` — print JSON statistics for a CSV file's columns.

## Output (stdout)
```json
{ "rows": <dataRowCount>,
  "columns": { "<name>": { "count": <numericCells>, "nulls": <nonNumericOrEmpty>,
                           "mean": <4dp|null>, "min": <n|null>, "max": <n|null>, "sum": <n> } } }
```

## Rules
- First CSV row is the header. `rows` counts data rows only.
- A cell is **numeric** if it is a finite number after trimming; empty or non-numeric cells
  count as `nulls` and are excluded from `mean/min/max/sum` (never produce `NaN`).
- `mean` rounded to 4 decimals; `null` when a column has no numeric values.
- **Quoted fields may contain commas** (`"New York, NY"`) and must not shift columns.
- `--column NAME` limits output to one column; unknown column → exit 1.
- Missing/unreadable file → exit 1 with a **clean one-line stderr message** (no stack trace).
- Tolerate a trailing newline / header-only file (→ `rows: 0`).

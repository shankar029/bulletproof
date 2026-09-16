# Bounded integration follow-up

## CLI Unicode forwarding — fixed

FACT: decoding the child pipe as UTF-8 did not configure the CLI's output sink.
On Windows under `PYTHONIOENCODING=cp1252`, `sys.stdout.write` raised
`UnicodeEncodeError` inside the pump thread. The CLI could return the child's
successful exit status while losing the Unicode line and subsequent logs.

`scripts/run.py` now configures its actual stdout/stderr wrappers to UTF-8 with
`backslashreplace` handling at CLI entry. This is implementation behavior, not a
required caller environment workaround.

The new real CLI regression runs with cp1252 forced and Python UTF-8 mode disabled.
It requires exact forwarding of `✓ Δ 日本`, a following `finished` sentinel,
exit 0, and empty stderr. It failed before the fix and passes afterward.
All five capture/CLI tests pass. Evidence:

- `i1-native-cli-encoding-red.json`
- `i1-native-cli-encoding-green.json` (includes current source hashes)

No full Python suite or parent shell was rerun/interrupted.

## CSV corpus — real assertion gap, no grading change

FACT: all 16 original candidates were independently executed on an owned temp
copy using the production native parser/classifier:

- 8 genuine assertion kills
- 1 genuine survivor
- 6 mixed assertion/non-assertion failure runs, conservatively ungraded
- 1 zero-leaf CLI-entrypoint failure, ungraded

Thus the unchanged fixture honestly scores **8/9 = 0.888888…**, below the
unchanged 0.9 threshold. The six non-assertion failures include ordinary `Error`
and `TypeError` (for example accessing `.range` on an absent column). They must
not be relabeled assertions. The direct-entrypoint guard mutation at
`benchmark/projects/csv-stats-cli/bulletproof/cli.ts:120` changes `===` to `!==`;
importing the implementation then enters its CLI and exits before any native
leaf tests execute. That is not an assertion kill.

The genuine survivor is `>→<@1579`, line 48:

```ts
if (field !== '' || row.length > 0) { row.push(field); rows.push(row); }
```

Changing `row.length > 0` to `< 0` discards a final CSV record whose last field
is empty when no terminating newline exists. Existing parser cases all end with
a newline and miss this condition.

Exact proposed addition to the parser section of
`benchmark/projects/csv-stats-cli/bulletproof/cli.test.ts`:

```ts
test('preserves trailing empty field without final newline', () =>
  assert.deepEqual(parseCsv('a,b\n1,'), [['a', 'b'], ['1', '']]));
```

FACT: this assertion was added **only to an owned temporary copy** for proof:
the original passes, the survivor produces a genuine native AssertionError
(`actual: [['a','b']]`, `expected: [['a','b'],['1','']]`), and the production
scorer returns **9 killed / 0 survived / 7 skipped = 1.0**. No threshold,
classifier policy, mutation corpus, or repository benchmark fixture was changed.

Parent action needed: approve/apply that exact fixture assertion (outside this
lane's write ownership), then rerun the corpus. Until then, the repository's CSV
test-quality gate remains below 0.9; it is not reported as passing.

Replay and full native evidence:

```text
python scripts/run.py --idle 60 --max 180 -- node .ai/workflow-reliability/evidence/i1-native-csv-diagnose.mjs
```

`i1-native-csv-diagnosis.json` records every candidate, source edit, syntax result,
native events, proposed-assertion red/green, and the temp-copy scorer result.

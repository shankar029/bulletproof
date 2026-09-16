# Final frozen-source affected verification

This supplements, without rewriting, `i1-independent-report.md` and the earlier
revalidation records. It is the latest affected-test and actual-probe observation.

## Scope and source binding

Re-read the actual non-object source/command/baseline guards in `probe.mutation_entry`.
These guards are present in the same corrected production hash already observed:

- `scripts/probe.py`:
  `f2d966571e6061f41a9985eb21463ece56c1d6b2153dd21f4fdba26455c3604a`
- `scripts/tests/test_probe.py`:
  `3269a43f95c0596eb1d77671e70905897dde1c0505d1975cdfa5c23a84d0887b`
- Expanded verifier-owned `scripts/tests/test_measurement_e2e.py`:
  `28e18d7877aeef0823fd6132ed34999fc2d306070a6d033972bcb7a0a20c4997`

All eight production/test hashes in `i1-independent-probe-final-schema-sources.json`
match before and after the affected runs, and still match `i1-independent-frozen.json`,
the complete 712-file ending inventory captured after the refreshed actual probe.
No production implementation was performed by the verifier.

## Added boundary coverage

Added `test_current_mutation_rejects_nonobject_report_bindings` only to the permitted
test file. It runs **16 real mutation producers** in owned Git/native-test fixtures:

- One unmodified positive control: real assertion kill, 100%, accepted as measured/ok.
- Fifteen malformed reports: each of `source`, `test_run.command`, and `baseline`
  replaced in turn with JSON null, number 42, array, string, and boolean.
- Every malformed case returns explicit unavailable, null score and the corresponding
  field-specific rejection reason, with no uncaught exception.
- Original source bytes are restored in every case.

This is artifact-boundary fault injection, not fabricated process proof. A patched
execution seam delegates every command to a real bounded subprocess, requires the
mutation producer actually to exit 0 with one genuine kill, then corrupts only the
completed on-disk report before the real consumer reads it. No subprocess exit code,
stdout, native test result, or measured positive report is stubbed.

Detailed cases, emitted reports and expanded commands are preserved under
`i1-independent-schema-2069b31032f9-*`; `results.json` contains one accepted control and
15 unavailable results. No own fixture directory remains.

## Fresh affected results

| Record | Result |
|---|---|
| `i1-independent-probe-frozen-suite.{json,log}` | **19/19 pass**, exit 0, 58.341 seconds bounded execution |
| `i1-independent-measurement-frozen-suite.{json,log}` | **3 tests: 2 pass, 1 fail**, exit 1, 196.294 seconds |

The new malformed-report test passes, as does the real ESM/CJS low-score policy test.
The existing parent freshness regression fails again, now at
`scripts/tests/test_measurement_e2e.py:138`: changing unrelated evidence leaves the
reported scope hash unchanged. F1 remains grounded in `scripts/probe.py:474–478`.
Sixteen fixture cases are subtests within one test method, not sixteen extra top-level tests.
The full Python/native/corpus suites were not duplicated or relabeled as newly run.

## Refreshed actual repository quality

Because the added test changes the observed source inventory, ran actual CMD-PROBE again,
using the supplied Python and `--idle 120 --max 900`, without a threshold/skip/force change.

- Run **`f5d34d4ae55245d189f5dfa047cbecbf`**, exit **1**, 12.773 seconds.
- `measurement_status=unavailable`, `completeness=incomplete`, `verdict=fail`.
- **Nine required measurements unavailable**; missing collectors and dirty mutation
  prerequisites remain blockers, not a passing quality gate.
- Report source hash and post-publication observed hash match:
  `a42ea324a7ec67dfe90d29ba2610fc79fca00f27ede6153a105be71c7ea2a938`.
  This proves freshness only within the declared scope, not correctness of F1's exclusions.

Expanded argv/cwd/environment/output are in `i1-independent-probe-frozen.{json,log}`;
raw reports are under `i1-independent-probe-run-f5d34d4ae55245d189f5dfa047cbecbf/`.
The pre-existing display alias was restored byte-for-byte. Older probe records remain
historical, not final-test-inventory proof.

## Verdict

**New schema guards: VERIFIED for the exercised boundary cases.**
Overall verdict is unchanged: AC01 verified with stated runtime limitations; AC02 and I1
closure not verified because F1 persists. Actual quality remains incomplete/fail;
whitespace diagnostics and separate review also remain outstanding. I2 stays pending.
No commit, publication, installation or delegation was performed or authorized.

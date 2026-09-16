# Corrected static-inventory probe: independent revalidation

At the parent's explicit request, re-opened the type guard in `scripts/probe.py:503–514`
and `test_malformed_static_inventory_is_unsupported_not_a_crash` at
`scripts/tests/test_probe.py:99–106`. No production/test changes were made by the verifier.

Fresh affected-suite execution, after all earlier runs completed:

- UTC: 2026-09-16 19:58:20.462907 through 19:59:19.871256.
- Actual command: supplied Python, `-B -m unittest discover -s scripts/tests -p test_probe.py -v`,
  wrapped with `-B scripts/run.py --idle 120 --max 900`.
- **19 tests passed; 0 failures/errors; exit 0.** Unittest duration 58.389 seconds;
  bounded command duration 59.408 seconds.
- The malformed-inventory test exercises `paths = null`, `42`, `[]`, and
  `{"scanned": null}`. All leave `source.py` unsupported rather than crashing.
- Real CLI cases for missing proof, invalid baseline, stale-score refusal and current
  native mutation also passed in the same affected-suite run.

Hashes were identical immediately before and after execution:

| File | SHA-256 |
|---|---|
| `scripts/probe.py` | `f2d966571e6061f41a9985eb21463ece56c1d6b2153dd21f4fdba26455c3604a` |
| `scripts/tests/test_probe.py` | `3269a43f95c0596eb1d77671e70905897dde1c0505d1975cdfa5c23a84d0887b` |

Evidence: `i1-independent-probe-tests-reanchor.json`, matching `.log`, and
`i1-independent-probe-tests-reanchor-sources.json`. These are new observations,
not reused initial-snapshot results.

**Correction verdict: VERIFIED for this affected behavior and suite.**
This does not resolve F1's unrelated-evidence exclusion defect, the whitespace failure,
or required missing quality measurements. Overall I1 closure remains blocked; separate
review remains the parent's responsibility. No old full-suite count is relabeled as a
new final-tree full-suite pass, and no I2/commit/publication authorization is implied.

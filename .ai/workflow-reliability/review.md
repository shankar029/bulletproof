# I1 verification findings and dispositions

Independent code review is still pending. This section records the separate verifier's
findings; it is not a substitute for a review verdict.

| Finding | Independent evidence | Parent disposition |
|---|---|---|
| F1: broad parent evidence exclusion hid unrelated contract changes | `evidence/i1-independent-report.md`; failing `test_measurement_e2e.py` public CLI case | Resolved. `probe._snapshot` excludes only exact same-run mutation/metrics files and the metrics display alias. Legacy aliases and unrelated evidence remain observed. Unchanged independent regression now passes; full 53-test run and stable 21-file hashes recorded in `evidence/i1-independent-f1-verification.md`. |
| F2: CRLF artifacts failed whitespace checks | Initial verifier diff-check log; `evidence/i1-independent-whitespace-revalidation.md` | Resolved by explicit `cr-at-eol` for byte-preserved task artifacts, retaining all three default whitespace checks. No raw evidence normalization or command-line suppression. Verifier replayed both ordinary checks successfully. |
| Source drift during verification | Verifier's before/after hashes and correction revalidation | Accepted as a historical protocol deviation. Parent's malformed-inventory/report guards were explicitly reported, re-anchored and tested by the verifier. Earlier 49-test run is not represented as an atomic final-tree result. |

The verifier added real malformed-report and public CLI coverage, including sixteen real
mutation runs for the schema boundary. Required actual quality proof remains incomplete;
its failure is not waived by functional verification. I2/I3 remain pending.

Independent Phase 5 verdict: AC01 verified with runtime limits, AC02 functional semantics
verified, AC09 regression component verified but closure blocked. A separate fresh-context
code reviewer is now evaluating the frozen implementation.

## Code review round 1

Raw return preserved unchanged in `evidence/i1-code-review-r1.md`: REVISE for limited
functional preservation, not an approval to close I1.

| Finding | Parent disposition |
|---|---|
| R1: missing/contradictory classified results accepted | Independently revalidated. Shared `mutate.validate_mutation_results` regenerates candidate identity/bytes, validates process/native proof, and reconciles outcomes/counters/score. Both independent runs accepted one real control and rejected 30 corruptions. Re-review pending. |
| R2: valid implicit native discovery rejected | Independently revalidated. Probe reuses `select_test_run`; full canonical command/test-file equality remains required. Genuine discovery accepted; arbitrary suffix/test-file mismatches rejected. Re-review pending. |

Local correction feedback: `i1-review-fixes-e2e.log` (4/4, including 28 real producer
schema cases) and `i1-review-fixes-probe.log` (19/19). These do not replace affected
independent verification and re-review.

Latest independent verification: `evidence/i1-independent-review-fixes-verification.md`.
Full Python discovery 54/54; separate E2E 4/4; all 98 final-manifest inputs unchanged,
including 85 retained Node/corpus inputs and re-anchored metric documentation.
The actual probe still has nine missing required measurements. Requested re-review from
the original separate reviewer after receiving this result.

Staging exposed intentional whitespace in raw captured stdout (unittest subtest prefixes and
terminal blank lines). Raw `evidence/*.log` and `i1-quality-stdout.json` are therefore marked
`-diff` as byte-preserved transcripts, like other opaque evidence. Their bytes and recorded
hashes are unchanged. Source, authored documents and structured JSON still retain the
default whitespace checks; no failed source/style check was suppressed.

## Final independent disposition

`evidence/i1-code-review-r2.md` preserves the re-review and its narrow packaging
supplement. Final verdict: **APPROVE for limited local functional preservation**.
R1, R2 and R3 are resolved within that review. AC01 is verified with Windows/Node24
limitations; AC02 functional semantics and AC09 regression/review components are verified.
Quality closure remains blocked, not waived.

Provenance: 97/98 final-manifest inputs match. The sole difference is the independently
reviewed transcript attribute configuration, SHA-256
`0e7d5e05cc8ad01c2ba3c4cc811cbcd06af6784be92265043e735929b753a2c6`.
The original manifest and raw proof hashes are preserved. No outstanding production-code
finding remains in the bounded review. Parent accepts this disposition for a local
preservation commit only; I1.T4 remains blocked and I2/I3 remain pending.

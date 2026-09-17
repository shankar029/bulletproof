# APPROVE - C2a partial functional preservation only

Reviewer: `0cac6ce2-9ce5-4536-8a4f-448d65086b0d`, separate read-only context.
Initial return: "No significant issues found in the reviewed changes."
The reviewer subsequently supplied the following bounded gate disposition.

## Verdict and freshness

The no-significant-issues result is APPROVE for the observer-seam slice, not C2
completion or release approval. Actual files were independently SHA-256 checked
during review and matched frozen evidence:

| File | SHA-256 |
|---|---|
| `scripts/run.py` | `7a262b84b6e4b29f45f2708a6e30c33cd7c2c61e1977da20e2527a3fb46ed89e` |
| `scripts/tests/test_run.py` | `92bedd163977112eff3efd3cfbad5fc9aaa9fe9a2318dd2aad832903914b85e5` |
| `scripts/tests/test_run_c2a_verification.py` | `9a66a417faceabfdb53ec39869eb72437b0852d24b03518858f4aee3f6ea6aef` |

All 22 owner pins, 35 independent final-input pins and 10 independent artifact
pins matched during review. This is bounded freshness, not whole-machine
attestation. No subsequent freshness check or test replay was performed for
the follow-up handoff.

## Gate dispositions

| Criterion | Bounded disposition |
|---|---|
| AC04 | Observer seam approved: synchronous lifecycle facts, explicit observer-error non-success, conservative owned cleanup. Guarded CLI admission and durable recovery remain unproven. |
| AC05 | No new resume/recovery acceptance. Null creation identity and direct-child exit do not authorize recovery or establish descendant termination. |
| AC09 | Separate read-only review satisfied for C2a. Independent evidence supports 51 distinct passing methods across bounded batches. Initial boundary assertion failure, test-only correction and three-method replay remain preserved; not a clean-first-run claim. Full quality closure remains blocked. |

No CLI, crash-recovery, whole-quality, whole-tree termination, Unix execution or
cross-platform qualification is granted. Windows execution claims are limited to
the reviewed verifier evidence. Historical incomplete metrics are not fresh
quality proof. This approval is not a release waiver. The reviewer edited no files.

## Parent disposition

Accept this partial functional-preservation approval with the independent
`c2a-independent-report.md` result. The approved ProcessObservation record has
eight fields; the earlier parent/owner "nine" wording is explicitly corrected in
state and verification, without rewriting historical evidence. Preserve runner,
both test files, and the owned C2a evidence. Final source hashes must match before
commit. Proceed to the remaining C2 CLI component after local preservation;
do not claim the whole requirement, recovery or missing quality gates complete.

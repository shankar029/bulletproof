# Reliability acceptance traceability

The current requirement and exclusions are in `state.md`. Independent Phase 5 verification
is in `evidence/i1-independent-f1-verification.md`. Separate review R1/R2 reopened
affected acceptance; corrections are independently revalidated and approved for limited
local preservation in `evidence/i1-code-review-r2.md`.
Functional verification does not complete the blocked quality gate.

| AC | Priority | Contract | Status | Evidence |
|---|---|---|---|---|
| AC01 | P0 | ESM/CJS discovery, mutation routing and behavioral classification | VERIFIED-WITH-LIMITATIONS | Canonical discovery/routing/classification independently verified and reviewed; Windows/Node24 only. |
| AC02 | P0 | Honest measured status, completeness and fresh metric evidence | VERIFIED - functional semantics | Independent 54-test full run and 4-test E2E; one control accepted, 30 corruptions rejected per run; F1/R1/R2 resolved and reviewed. Actual quality incomplete. |
| AC03 | P0 | Source/contract/check/producer-bound increment readiness | Planned | research.md E15-E18 |
| AC04 | P0 | Real guarded command admission with explicit trust limits | Planned | research.md E05/E21-E23 |
| AC05 | P1 | Artifact-only fresh-context resume and scoped invalidation | Planned | research.md E16-E17/E22 |
| AC06 | P1 | Behavioral failure evaluations and held-out diagnosis | Planned | research.md E12-E14/E20-E24 |
| AC07 | P1 | Historical/current contract distinction and pre-retirement proof | Planned | research.md E17-E18 |
| AC08 | P2 | Scoped corrected research and authoritative status communication | Planned | research.md E18/E25 |
| AC09 | All | Independent per-increment verification/review and preserved regressions | Functional regression/review VERIFIED; quality closure BLOCKED | 54 Python, 62 native tests; ten tasks, 79 functional assertions. 97/98 inputs unchanged plus independently reviewed packaging delta. Nine required actual quality measurements unavailable; publication unauthorized. |

AC03-08 remain future work in I2/I3. The approved I1.T4 gate prevents their dispatch until
actual required proof is available. No fixture score, self-review, or metadata checkbox
waives that dependency.

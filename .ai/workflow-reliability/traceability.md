# Reliability acceptance traceability

The current requirement and exclusions are in `state.md`. Independent Phase 5 verification
is in `evidence/i1-independent-f1-verification.md`. Separate review R1/R2 reopened
affected acceptance; corrections are independently revalidated and approved for limited
local preservation in `evidence/i1-code-review-r2.md`.
Functional verification does not complete the blocked quality gate.
The additive `continuation-plan.html` permits bounded implementation before missing quality
collectors are available; it does not waive quality or independent slice acceptance.

| AC | Priority | Contract | Status | Evidence |
|---|---|---|---|---|
| AC01 | P0 | ESM/CJS discovery, mutation routing and behavioral classification | VERIFIED-WITH-LIMITATIONS | Canonical discovery/routing/classification independently verified and reviewed; Windows/Node24 only. |
| AC02 | P0 | Honest measured status, completeness and fresh metric evidence | Q1 VERIFIED-WITH-LIMITATIONS for functional preservation | `evidence/q1-attr-independent-report.md`: 28 focused +83 workflow +10 evidence pass once. `evidence/q1-attr-code-review.md`: APPROVE; ambiguous declarations explicitly unsupported. Complete quality still due. |
| AC03 | P0 | Source/contract/check/producer-bound increment readiness | C1 VERIFIED-WITH-LIMITATIONS for combined preservation | r5/re-review and final integrated 83+10 pass; `evidence/c1-q1-composition-result.json` binds the shared policy into the candidate. The historical C1-only failure remains preserved; CLI pending. |
| AC04 | P0 | Real guarded command admission with explicit trust limits | C2a lifecycle seam verified/reviewed; CLI pending | `evidence/c2a-independent-report.md` and `c2a-code-review.md`: actual lifecycle/error observations and explicit ownership limits; not guarded command admission or durable recovery. |
| AC05 | P1 | Artifact-only fresh-context resume and scoped invalidation | Partially exercised; host experiment pending | C1 verifier exercised real fresh-process scoped invalidation; not a fresh-agent resume experiment. |
| AC06 | P1 | Behavioral failure evaluations and held-out diagnosis | Planned | research.md E12-E14/E20-E24 |
| AC07 | P1 | Historical/current contract distinction and pre-retirement proof | Core protocol partially exercised; CLI/canonical integration pending | C1 historical compatibility and current-design fixtures pass; actual retirement lifecycle not yet proven. |
| AC08 | P2 | Scoped corrected research and authoritative status communication | Core verified/reviewed with limits; canonical integration pending | Failed finding-producer acceptance corrected and independently rechecked; scoped supersession/source anchors retained. Canonical communication wiring pending. |
| AC09 | All | Independent per-increment verification/review and preserved regressions | C1/Q1 preserved; C2a accepted for preservation; quality closure BLOCKED | C1/Q1 historical121-method replay and review preserved in `5dabb4c`. C2a51 distinct methods pass; separate review APPROVE, original verifier failure retained. Only documented affected coverage is refreshed. |
| AC10 | All | Attractive README and complete, accurate user/operator guides | Existing-feature documentation delivered; guard additions pending | `015d353` plus independently reviewed portable hero in `0b7e1a1`; documentation review/disposition/rendering and `c1-code-review.md` retained. Operator documentation awaits C2. |

AC03-08 remain incomplete overall. C1/Q1 have passed their bounded independent functional
gates and were preserved in `5dabb4c`; C2a is approved for preservation. I1.T4/Q still block release, not continuation.
No fixture score, self-review, or metadata checkbox waives these gates. Historical metric
reports are not current quality proof after source changes.

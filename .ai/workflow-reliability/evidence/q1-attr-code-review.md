# APPROVE - residual R2 correction and quality-reference delta

Reviewer: `9a253936-ce4f-4e86-89be-a19ac9f6c7d5`.
The following preserves the final narrowed review and subsequent reconciliation.

## Verdict

The literal-filter-name admission defect is closed on the qualified runtime.
No further production correction is required within this narrowed review.
The updated quality reference is factually supported.

Two protected rendering artifacts changed after independent verification. This
does not invalidate the reviewed code/test result, but prevents an unconditional
"all 4,778 pins unchanged" later handoff. The parent disclosure and reviewer
reconciliation are preserved below.

## Residual R2 disposition

Accepted: `scripts/measure.py:133-154`.

The reviewer independently reconstructed the delta from the archived predecessor
whose SHA-256 matches `753fca9e...`, verified current bytes, and matched the
recorded diff, including its disclosed Windows text-writer encoding. There is
one production hunk, confined to the attribute gate.

The corrected implementation uses Git-native `check-attr --cached --all -z`,
allowing genuinely absent/reset attributes to be omitted. It rejects present
literal `filter=unset` and `filter=unspecified`, conservatively rejects ambiguous
disabled forms including `-filter` and `-text`, retains qualified text/EOL values
and ignores unrelated attributes. It validates record triples, requested paths
and duplicate records before checkout. The common materializer/validator path,
isolated configuration, exact supplied-byte comparison and ownership boundaries
are preserved.

This fixes the classification mechanism rather than special-casing the two
reproductions. No handwritten attributes parser, schema change or normalization
of supplied baseline bytes was introduced.

## Direct reviewer replay

Three existing methods ran once:

| Method | Result |
|---|---|
| `test_literal_unset_driver_rejected_at_both_boundaries` | PASS |
| `test_literal_unspecified_driver_rejected_at_both_boundaries` | PASS |
| `test_absent_and_reset_filter_preserve_normal_baseline` | PASS |

Three passed in 45.332 seconds, without failures, errors or skips. Both literal
names produce the expected unsupported/ambiguous error at both boundaries.
Sentinels remain absent during isolation; ordinary explicitly configured checkout
executes each real driver. Absent/reset positives retain exact bytes.

All 20 observed owned temporary directories were absent afterward. These are
repeats, not additional distinct methods to add to independent verification.
The independent `-text` rejection / `!text` reset test appropriately uses real
Git/files and does not imply broad attribute fuzzing.

## Evidence and functional preservation

Independent records support 121 distinct methods, each suite executed once:

| Batch | Methods | Failures/errors/skips/timeouts |
|---|---:|---:|
| Focused attribute/configured-probe checks | 28 | 0 |
| Integrated workflow | 83 | 0 |
| Integrated evidence | 10 | 0 |

The earlier 74-method Q1 replay was preserved, not rerun on these new bytes.
These are not combined into one current-tree aggregate.

The casing-lookup and diff-newline reconciliation errors are evidence-helper
recoveries, not production changes or test retries. The five qualification
commands' raw streams were rehashed, not relabeled as fresh executions.

The single-hunk delta and affected regression coverage support retaining prior
R1/F1/F2/F3 acceptance. Integrated C1 supplies current shared-dependency regression
evidence; this review does not reopen C1 or claim a C1-only candidate passed.

The change adds no new subprocess stage or clone. It broadens output to all
effective attributes within existing path batches. Existing per-Git-command
bounds and cleanup ownership remain; no universal resource bound is claimed.

## Quality-reference disposition

Accepted: the two changed sections in `references/quality-metrics.md`.

The collector statement distinguishes configured Python literal-import
graph/architecture evidence from dynamic behavior, mixed-language coverage and
incomplete adapters. This is grounded in `measure_graph.observations`,
`evaluate_rules`, and the configured probe path, not universal collector support.

The baseline section accurately documents independent immutable-tree
materialization rather than status/index trust; full relevant byte/type/mode
comparison and physical independence; isolated neutral/versioned EOL policy;
conservative rejection of ambiguous declarations; qualified Git/Windows/Python
scope and mode projection; and no sandbox, atomic lease or complete
mutation-controller-isolation guarantee.

Reviewed SHA-256, unchanged through review:
`d2617ee85d227b2fe03035b842dbce1242518fcecbfe002618d70ddbdb807904`.

## CHECK / AC dispositions

| Scope | Final narrowed disposition |
|---|---|
| CHECK-RECONCILE | VERIFIED-WITH-LIMITATIONS: residual admission defect closed; common policy retained. |
| CHECK-PARTIAL-PROBE | VERIFIED: all-nine requirements and incomplete/fail behavior retained. |
| CHECK-INVENTORY | Prior bounded acceptance retained; no fresh full inventory replay claimed. |
| CHECK-GRAPH | Prior bounded acceptance retained; not mixed-language graph acceptance. |
| AC01 | VERIFIED-WITH-LIMITATIONS for existing Q1/native preservation, not future mixed-language mutation. |
| AC02 | VERIFIED-WITH-LIMITATIONS for corrected admission/completeness. |
| AC09 | VERIFIED-WITH-LIMITATIONS for narrow review and integrated functional preservation. |
| AC03/AC04 C1 core | Approval retained with integrated 83+10; not live C2/authenticated enforcement. |
| Other ACs / Q2-Q5 quality | Not newly verified or completed. |

Remove the code-review HOLD caused by residual R2. Parent may proceed through
remaining acceptance/preservation gates, not waive quality or release gates.

## Source freshness and rendering exceptions

Final production hashes:

```text
measure.py
5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084
measure_graph.py
6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391
probe.py
668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083
```

Actual Git binding matches 2.53.0.windows.4 core plus 69 DLLs. Mutation, evidence,
runner, tests/raw streams and handoff bindings match. Live HEAD was
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`; the real index was empty.

Of 4,778 verifier pins, 4,776 matched at review entry. Two artifacts already
differed at the initial check and stayed stable through the spotcheck:

| Artifact under `.ai/workflow-reliability/evidence` | Frozen SHA-256 | Later SHA-256 |
|---|---|---|
| `report-rendering.json` | `abb99c8f9d69d0d00426020205201895b6514a91fc05fc0d82675a23ccbf68b5` | `a7ca6f1f7cbb818370ce776c989e3dd7eee9fd24deeac637321cb65ded596e84` |
| `report.pdf` | `da3f742393a15e1536d009bb42d41b14b786673fe4707fbebff366708767b4f1` | `1ce2962762e9203dd3b15760cd9a6ad24f5428f115d88a23d6625e11b764829a` |

Initial freshness exited 1: a real mismatch, not a test failure or corrected
helper error. Zero pins changed during the subsequent bounded replay.
The four-document reconciliation does not cover these two rendering artifacts.
Its historical state/traceability/report hashes also are no longer current;
those documents were explicitly outside verification pins. The quality-reference
hash still matches. Original `q1-code-review-final.md` remains preserved.

No persistent source/test/evidence/shared-state writes, installations, nested
agents, commits or publication were performed by the reviewer.

## Subsequent disclosure and reviewer reconciliation

Parent disclosed the updated status documents, regenerated report/PDF and additive
composition helper/result while review was running. The reviewer responded:

> Reconciled. The two differing protected pins - report.pdf and report-rendering.json -
> are disclosed parent-owned regeneration, not changes to Q1 production, tests or
> raw proof. The verifier's historical 4,778 unchanged observation remains valid
> for its handoff; my later comparison remains 4,776 matching plus those two
> explained replacements.
>
> The narrowed APPROVE is unchanged. The document updates and additive composition
> artifacts are separate parent work. I have not independently inspected the new
> composition result; its byte/import matching must not be described as another
> test execution. No additional review cycle or regression replay is required
> by this disclosure.

## Parent disposition

Accept the narrowed approval and the explicit rendering reconciliation. Preserve
the historical failed review, red runs and verifier observations without rewriting
them. The separate parent composition check matches 31 candidate source/reference
files and 13 independently observed script imports; it is not another test run.
Authorize combined C1/Q1 local preservation only. C2-C4 and Q2-Q5, complete quality,
human design approval and publication remain separately incomplete or blocked.

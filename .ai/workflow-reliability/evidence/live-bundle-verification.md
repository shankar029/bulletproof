# Live-evaluation bundle integration

Parent-owned packaging integration from the accepted design's installer/live-harness
boundary. This is independent of guard admission and does not accept C1/C2 or quality gates.

## Reproduced defect

The original `stageSkillBundle()` in `evals/agent/live.mjs` copied only SKILL.md and
references. A bounded Node invocation extracted that exact function from current source,
executed it in a VM with its real filesystem dependencies, inspected the returned owned
temporary directory and removed only that directory:

```json
{"skill":true,"references":true,"scripts":false,"assets":false}
```

This was a real original-function/file-copy observation, not a live model invocation.
The missing payload conflicts with the bundled process/measurement tools and HTML theme.

## Change and proof

`workspace.mjs` now owns exported `stageSkillBundle(repoRoot, stagingParent)`; the live
entry point uses it. Copy all four installer payloads and clean the owned partial bundle on
failure. Native tests execute a copied module with its sibling import, compare payload bytes,
and verify missing-payload failure leaves the source intact and no staged directory.

Both arms now receive the same allowance for `.ai/` task records without moving deliverable
code outside its arm or changing seeded files. The common prompt still avoids trap/tool/
dependency hints; only the existing final skill directive differs. This corrects the prior
contradiction between the artifact workflow and a blanket prohibition on every out-of-arm edit.

Managed Python was used through `scripts/run.py`, with idle 120 seconds.

| Actual command after the wrapper | Maximum | Result |
|---|---:|---|
| `node --test evals\agent\agent.test.mjs` | 180s | 21 tests passed; no skipped/cancelled/todo tests |
| `node evals\agent\live.mjs --task paginator --dry-run` | 300s | Both reference-copy arms composite/accuracy/test-realness 1.00; exit 0 |

The dry-run's equal reference-copy scores are plumbing proof, not a measured live-agent gain.
Node emitted its native TypeScript experimental warning. No model call, external installation,
new project dependency or publication occurred. Independent integrated review remains due.

## Parent integration review

Re-read the complete pending bundle/prompt/test diff after continuation re-anchoring.
The live caller retains ownership of successful staging cleanup; failed staging cleans only
the newly allocated directory and propagates failure. Tests cover payload byte equality,
actual sibling import, partial-failure cleanup and identical common instructions for both
arm-file layouts. No production issue identified in this bounded self-review; it is not
the separate independent review.

Subsequent integrated native run passed 65 tests (`continuation-native.log`); the fixed
corpus passed all ten tasks and 79 functional assertions (`continuation-corpus.log`).
These expand regression scope, not model-effectiveness or whole-change quality proof.

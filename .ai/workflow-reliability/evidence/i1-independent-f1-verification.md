# I1 final F1 revalidation — fresh independent result

**Functional F1 verdict: RESOLVED. Required project quality: INCOMPLETE / FAIL.**

This is the latest independent Phase 5 result for the corrected tree. It supersedes the
unresolved F1 status in earlier reports, not their historical observations or raw evidence.
It is not separate review, I1 closure, permission to begin I2, or authorization to commit.

## Re-anchored source and scope

Read `probe._snapshot` at `scripts/probe.py:474–481` and both execution call sites at
lines 568 and 641. Both calls pass this invocation's `run_id`.

| File | SHA-256 used for revalidation |
|---|---|
| `scripts/probe.py` | `5a00e437349416aea5e67cd2fab5280c324cb2f6ad58d80e1b8c45665baa935b` |
| `scripts/tests/test_probe.py` | `ec5cb8f0f25937ba95ff48e6ad99158812a73c451e9ea012f9981f893cdff86e` |
| Unchanged independent `scripts/tests/test_measurement_e2e.py` | `28e18d7877aeef0823fd6132ed34999fc2d306070a6d033972bcb7a0a20c4997` |
| `.ai/workflow-reliability/.gitattributes` | `1fd44f434ed6352c44f6833a238f193e9a1336ad9d319622eabbcc1913a1bde9` |

All **21 recorded source/test/design/attribute hashes** match before and after each suite,
and before and after the actual probe. Within the earlier eight-file verification set,
only `probe.py` and `test_probe.py` changed since the previous verification.
Source manifests are in `i1-independent-f1-{measurement,python,whitespace}-sources.json`
and `i1-independent-f1-probe.json`.

No production or test edits were made by this verifier during this revalidation. Only
prefixed verification capture code and evidence were added. No delegation, install,
worktree commit, publication or I2 work occurred.

## Requested replays — actually executed

| Check | Observed result | Bounded duration | Evidence prefix |
|---|---|---|---|
| Full independent measurement suite | **3/3 pass**, rc 0 | 195.645 s | `i1-independent-f1-measurement` |
| Full Python discovery | **53/53 pass**, rc 0; no reported skips/errors/failures | 543.194 s | `i1-independent-f1-python` |
| Ordinary base-relative `git diff --check` | **rc 0**, empty output | 0.650 s | `i1-independent-f1-whitespace` |
| Actual repository CMD-PROBE | **rc 1**, incomplete/fail | 42.585 s | `i1-independent-f1-probe` |

The measurement suite is included in full discovery; do not sum these into 56 unique
tests. Its 16 malformed-report/control runs are subcases, not additional top-level tests.
The two suites used independent owned fixtures and ran in parallel. Actual repository
probing waited until both completed and fixture cleanup was observed.

Commands use the supplied Python with `-B scripts/run.py --idle 120 --max 900 -- …`.
Exact expanded argv, cwd, nonsecret environment, times, exits and raw output hashes are
in each named JSON/log pair. Runtime remains Python 3.14.2 / Node 24.11.1 on Windows;
Node 22 execution is not claimed.

### F1 red → green, without weakening the independent test

`test_public_probe_observes_unrelated_evidence_not_just_its_own_reports` now passes
unchanged in both runs. Publishing owned reports leaves the source hash fresh; changing
unrelated `contract-note.json` changes the reported scope hash.

The updated parent unit test independently distinguishes same-run report writes from an
unrelated log edit. The actual repository report confirms exactly these exclusions:

1. `.git`
2. `.ai/workflow-reliability/metrics.json`
3. `.ai/workflow-reliability/evidence/runs/9c28b908eb764dcaa1421a580e2fb8f5/metrics.json`
4. `.ai/workflow-reliability/evidence/runs/9c28b908eb764dcaa1421a580e2fb8f5/mutation.json`

There is no entire-evidence-directory or legacy-mutation-alias exclusion.
The original F1 failure log `i1-independent-measurement-e2e-retry.log` still matches its
recorded SHA-256. Historical red was preserved, not rewritten or attributed to this tree.
F2's whitespace correction also remains independently green.

## Public behavior covered in the green integrated run

- ESM/CJS discovery, native routing, correct kills versus survivors, spaced argv/nested
  cwd, BOM/CRLF/byte restoration and exact shared-output freshness.
- Setup/import/syntax, empty inventory, skips/todos/cancellation, timeouts and quoted
  assertion logs do not become behavioral kills; custom unsupported runners remain unavailable.
- Dirty inputs, competing edits/report writes, nonce reuse, unsupported changed Python,
  and conservative syntax/operator selection.
- Fresh current mutation versus stale display score; missing/unknown baseline; measured
  failure distinct from incomplete proof. Real ESM/CJS low-score cases each produce
  one kill/one survivor, 50%, measured failure and incomplete/fail overall.
- Malformed static inventories and 15 malformed mutation-report binding cases become
  explicit unavailable; their genuine positive mutation control remains measured/ok.

The earlier **62/62 native** and **10-task corpus / 79/79 bulletproof functional** results
remain independently observed evidence on unchanged relevant Node code. They were not
rerun or relabeled as newly executed in this affected replay. No full-project numeric
coverage or all-language mutation claim is inferred from these fixture results.

## Actual quality and non-invalidating capture

Actual run: **`9c28b908eb764dcaa1421a580e2fb8f5`**.

```
exit_code:          1
measurement_status: unavailable
completeness:       incomplete
verdict:            fail
```

All nine required measurements are missing:

- Diff coverage and architecture rules: no supported collector implemented.
- Duplication, maximum/average complexity, cycles, dead exports and static findings:
  collectors unavailable/failed/malformed; detected analyzer version map is empty.
- Mutation: current producer returns 2 on dirty
  `.ai/workflow-reliability/.gitattributes`; no project mutation score is measured.

No dirty work was stashed, committed or mutated to force a result. Fixture scores are not
substitutes for actual project proof. No threshold, applicability or completeness waiver
was used.

Raw capture was first written outside the repository to the uniquely owned
`C:\Users\shbs\AppData\Local\Temp\i1-independent-raw-eyn69wkg\probe.log`.
No verifier evidence was written inside the observed repository during collection or
the immediate freshness check. After producer completion, its reported source hash
and independently recomputed hash both were:

`176a79d084ebb962a88d81dd260727e5cf186aa7ade8abe0f0bf92684d724583`

Only afterward were raw output/metadata archived into prefixed evidence and the owned
producer run moved to `i1-independent-f1-probe-run-9c28b908eb764dcaa1421a580e2fb8f5/`.
The pre-existing metrics display alias was restored byte-for-byte. External scratch was
cleaned up. Archiving these new diagnostic files changes the subsequently observed
inventory; this report claims freshness at the recorded post-producer/pre-archive point,
not that copied diagnostics are invisible to the corrected scope.

## Updated per-due-AC verdicts

| AC | Independent verdict | Limits / remaining gate work |
|---|---|---|
| **AC01** | **VERIFIED-WITH-LIMITATIONS** | Requested ESM/CJS and classification behavior verified; Windows / Node 24.11.1 execution only. Unsupported languages remain explicitly unavailable. |
| **AC02** | **VERIFIED — functional semantics** | F1 resolved; freshness, policy, malformed-input rejection and honest incomplete/fail demonstrated. This does **not** mean actual required quality measurements are complete. |
| **AC09** | **Regression/Phase 5 component VERIFIED; closure BLOCKED** | Fresh 53/53 integrated Python pass plus unchanged-code native/corpus proof and exact replay evidence. A distinct independent review is still required; actual quality proof is incomplete. No whole-AC or increment-completion waiver. |

**Stop / handoff:** no unresolved functional finding remains from this verifier's F1/F2
reports after the observed corrections. Parent should obtain the separate review and
retain I1.T4 blocked on genuine missing quality proof. I2 remains pending. There is no
command that manufactures the absent coverage/architecture collectors: a real supported
collector/configuration is required. This return authorizes no commit or publication.

## Final test-refinement confirmation

Re-opened the contract-edit assertion after the parent's final clarification. The file
already matches the `ec5cb8f0…3cdff86e` hash recorded before and after the 53-test full run:
`run_id="current"` is used consistently and `before_contract` is captured immediately
before the contract edit. Replayed that single test again: **1/1 pass, exit 0**.
All 21 recorded hashes remained unchanged. Exact command, output and full hashes are in
`i1-independent-f1-snapshot-test.{json,log}` and its `-sources.json`. Verdicts above stand.

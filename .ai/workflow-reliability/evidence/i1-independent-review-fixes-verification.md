# I1 independent Phase 5 — R1/R2 correction revalidation

**FACT: R1/R2 functional counterexamples are resolved by the observed corrected tree.
Actual required quality remains INCOMPLETE / FAIL. Separate re-review remains required.**

This supersedes affected functional acceptance from the earlier F1 verification, not its
historical evidence. The preserved `i1-code-review-r1.md` remains an unchanged REVISE
review of its earlier snapshot. This verifier neither issues the separate review verdict
nor authorizes I1 closure, I2, a worktree commit, installation or publication.

## Scope, identity and source provenance

Performed only the assigned independent verification role. Read current state, design,
contracts, tasks, traceability, preserved review, producer validation, consumer integration
and tests. Parent implementation was not treated as evidence.

- Cwd: `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`
- Observed HEAD: `dde2b491bf5981f86baac41473e7b73faa5ee363`
- Observed branch: `shbs-microsoft-workflow-app-verification`
- Comparison base: `bcc971d3b64559127dfc43eb0bfd4348c42803ca`
- Observed versions: Python **3.14.2**, Node **24.11.1**, Git **2.53.0.windows.4**, Windows.
- Node 22, other operating systems, authenticated provenance and sandbox isolation are not verified.

The final manifest is **`i1-independent-review-fixes-final-manifest.json`**. It contains
98 distinct input hashes: the 21 source/test/design/attribute bindings checked before and
after both suites and the actual probe, combined with 85 retained Node/corpus inputs
(eight overlap). All three 21-file comparisons match the final hashes. All 85 retained
inputs and native/corpus raw-log hashes match their earlier execution evidence.

| Re-anchored file | Final SHA-256 |
|---|---|
| `scripts/mutate.py` | `f7abaf6134a8300308ad5df181609b1215bed24c9de97ee4be91241de84088e3` |
| `scripts/probe.py` | `993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82` |
| `scripts/tests/test_probe.py` | `ec5cb8f0f25937ba95ff48e6ad99158812a73c451e9ea012f9981f893cdff86e` |
| `scripts/tests/test_measurement_e2e.py` | `7c035a0afa177c811bbe142b5a7b6dc608e8d9ecf283499de83a5ac98657780c` |
| `design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |

The verifier added only three missing cases and their diagnostic assertions to the permitted
measurement test: boolean native schema version, extra reported command argument, and
mismatched reported test files. No production source was edited. Capture-helper changes and
new evidence remain in the permitted `i1-independent-*` namespace. Existing red logs were
not changed. No delegation, worktree commit, installation, publication or I2 work occurred.
Disposable test fixtures create their own Git commits as part of the real test setup.

## Actual execution

Each named prefix below has JSON command metadata and a raw log. Metadata includes expanded
argv, cwd, environment delta, UTC start/end, duration, exit code and raw SHA-256. New outer
captures used **idle 120 / max 1500**; measurement-fixture commands retained their own
**idle 120 / max 900** bounds. The full discovery and separate boundary suite ran in
parallel in independent owned fixture directories. Both finished before actual repo probing.

| Check | Observed result | Duration | Evidence prefix |
|---|---|---|---|
| Full Python discovery | **54/54 pass**, exit 0; no reported skips/errors/failures | unittest 704.748 s; bounded capture 705.707 s | `i1-independent-review-fixes-python` |
| Separate measurement E2E suite | **4/4 pass**, exit 0 | unittest 358.346 s; bounded capture 359.102 s | `i1-independent-review-fixes-boundary` |
| Ordinary base-relative whitespace check, final replay | **exit 0**, empty output | 0.731 s | `i1-independent-review-fixes-final-whitespace` |
| Actual repository probe | **exit 1**, unavailable / incomplete / fail | 39.796 s | `i1-independent-review-fixes-probe` |
| Earlier native execution, hash-reconciled rather than rerun | **62/62 pass** | retained historical execution | `i1-independent-native` |
| Earlier corpus execution, hash-reconciled rather than rerun | **10 tasks / 20 arms; all ten bulletproof arms pass; 79/79 bulletproof functional assertions** | retained historical execution | `i1-independent-eval` |

The four E2E methods are already in the 54-test discovery; do not add them to claim 58
unique tests. Each corruption method executes **31 real producers: one accepted control
and 30 rejected corruptions**, not 31 top-level tests. Both independent executions have
the same observed counts. Their case indexes are:

- `i1-independent-schema-444520ed611a-results.json`
- `i1-independent-schema-b1857f9f8f5f-results.json`

Each index has corresponding captured case reports and command records with matching tag.
Every producer genuinely completed with one assertion kill before any intentional report
corruption. The seam changes only completed disposable report bytes; it does not fake
subprocess outcomes, native results, collectors or the test runner.

## Findings disposition and replay

### R1 — resolved in independent functional replay

Current source: `scripts/mutate.py:334–444` and `scripts/probe.py:353–369`.
The producer-owned validator regenerates default-budget candidates, checks candidate
identity and byte hashes, verifies baseline/native/process evidence and reconciles
outcomes, counters and score. Native schema and leaf counts reject booleans.

Observed positive control remains measured / 100 / ok. Missing results, empty or malformed
results, setup/unclassified outcomes, false survivor claims (including changed counters),
wrong bytes, wrong native inventory, missing execution evidence, non-object bindings and
boolean native fields all return unavailable, not a trusted score. This is structural
consistency validation, not proof against an actor who can forge every evidence field.

### R2 — resolved without arbitrary-suffix acceptance

Current source: `scripts/mutate.py:170–224`, `scripts/probe.py:353–356`.
The real public CLI test at `scripts/tests/test_measurement_e2e.py:228` invokes
`probe.py --slug discovery --base <fixture-base> -- node --test`.
The parent now accepts the producer's canonical `value.test.mjs` discovery expansion as
measured / 100, while retaining incomplete/fail overall for other missing requirements.

The independent added cases at test lines 157–223 separately append an arbitrary reported
argv suffix or alter `test_files`; both are rejected specifically as
`Mutation command does not match canonical test selection`.

### F1/F2 — remain resolved; earlier red retained

Current scope function: `scripts/probe.py:473`. The existing independent public freshness
test at `scripts/tests/test_measurement_e2e.py:124` passes again: exact owned reports do
not invalidate freshness, but unrelated evidence does. The refined parent test at
`scripts/tests/test_probe.py:108` also passes in full discovery.

The F1 historical red raw log still matches its original recorded SHA-256
`e3ddb516a42314174174dd57d504c6c1a206e5dc7d35724a1c4edc5d2ee6cc67`.
Ordinary `git diff --check <base>` passes with the preserved artifact attributes:
`-text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol`.
No default ASCII whitespace check was disabled and no raw evidence was normalized.
This Git check does not itself inspect untracked additions.

**INFERENCE from source plus observed replays:** no unresolved functional finding remains
from F1/F2/R1/R2 in the exercised I1 scope. This is not an exhaustive independent code
review; the parent must still obtain the distinct reviewer's re-review.

### Exact replay

From the cwd above, using the supplied Python:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:BP_TEST_PYTHON = $py
Remove-Item Env:NODE_TEST_CONTEXT -ErrorAction SilentlyContinue
& $py -B scripts\run.py --idle 120 --max 1500 -- $py -B -m unittest discover -s scripts\tests -v
& $py -B scripts\run.py --idle 120 --max 1500 -- $py -B -m unittest discover -s scripts\tests -p test_measurement_e2e.py -v
```

The latter replays R1, R2, F1 and the measured-failure ESM/CJS public CLI proof.
`i1-independent-review-fixes.py` captures these commands; new invocations should use new
evidence labels rather than overwrite the recorded executions.

## Actual quality — independently refreshed, still blocked

Actual run **`72f1ccc1a361421999706176c4ab7dc4`** used the CMD-PROBE argument list, with
equivalent Windows slash separators and the recorded 1500-second outer ceiling:

```powershell
& $py -B scripts\run.py --idle 120 --max 1500 -- $py -B scripts\probe.py `
  --slug workflow-reliability --base bcc971d3b64559127dfc43eb0bfd4348c42803ca `
  --test-cwd . -- 'C:\Program Files\nodejs\node.exe' --test `
  evals\lib\mutate.test.mjs evals\lib\score.test.mjs `
  evals\agent\agent.test.mjs evals\lib\native_result.test.mjs
```

**FACT:** exit **1**, `measurement_status=unavailable`, `completeness=incomplete`,
`verdict=fail`; **nine missing required measurements**:

- `architecture_rules`, `diff_coverage_pct`: no supported collector implemented.
- `duplication_pct`, `complexity_max`, `complexity_avg`, `cycles`, `dead_exports`,
  `static_findings`: no complete supported collector proof.
- `mutation_score_pct`: current child exit 2; dirty input refusal names
  `.ai/workflow-reliability/.gitattributes`. No actual project mutation score was measured.

No dirty source was stashed/committed to force a result. No fixture result, historical
score, import, exemption or threshold waiver substitutes for these missing measurements.
Generic mutation remains 60%; corpus remains 0.9 with its separately documented ungraded
denominator and null behavior. CSV retained proof is nine graded kills, zero survivors,
seven ungraded—not sixteen kills.

Raw probe capture was outside the observed repo:
`C:\Users\shbs\AppData\Local\Temp\i1-independent-raw-cehndz2r\probe.log`.
The report and independent immediate post-producer scope hash both were:

`5bf2d523db7200fdd8cf0bfa39bba02ce0e103f3f4628c5b9d4becf7e6bc0d8e`

Only after this check were diagnostics archived. Both producer reports are retained in
`i1-independent-review-fixes-probe-run-72f1ccc1a361421999706176c4ab7dc4/`.
The driver restored the pre-existing metrics display alias byte-for-byte and cleaned its
external scratch. Later archival changes observed membership: this is immediate freshness
proof at the recorded time, not a perpetual final-tree-fresh quality report.

## Per-due-AC verdict and stop boundary

| AC | Independent verdict | Evidence and limits |
|---|---|---|
| **AC01** | **VERIFIED-WITH-LIMITATIONS** | Full regression covers ESM/CJS discovery/routing, genuine assertion kills versus survivors, setup/import/syntax/empty/skip/timeout/log spoofing, spaced cwd/argv and exact restoration. R2 canonical public discovery and negative command bindings now pass. Windows/Node24 execution only; unsupported language paths remain unavailable. |
| **AC02** | **VERIFIED — functional semantics** | Real ESM/CJS 50% measured failures remain distinct from incomplete proof; stale-score refusal, dirty scope, malformed inventory, F1 freshness and R1 corruption rejection pass. Actual repo proof is honestly incomplete/fail, not a quality pass. |
| **AC09** | **Regression/Phase 5 component VERIFIED; closure BLOCKED** | 54 Python tests, separate 4-method boundary replay, hash-preserved 62 native tests and ten-task/79-assertion corpus evidence. Distinct reviewer's re-review is pending and actual required quality is still unavailable. |

AC03–AC08 remain future, not credited. The current task metadata preserves original design
review hash `15045977c39ff49967eadc028e7f50d475802ebca3675509e41ef373e66097bb`
separately from the current clarified contract hash recorded above. Local task completion
and pending parent report updates are not independent approval or gate completion.

**Handoff:** provide this result, final source manifest, fresh probe reports and unchanged
R1/R2 review to the separate reviewer. Keep I1.T4 blocked and I2 pending. Missing collectors
require actual implementation/configuration and a genuine rerun; this report does not
invent a finishing command that supplies nonexistent proof. EMU403 publication remains
blocked with no retry authorized. Verification stops here.

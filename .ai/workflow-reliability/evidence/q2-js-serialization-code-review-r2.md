# Independent correction review — R1/R2

**Focused source disposition: APPROVE. No new high-confidence substantive findings in the affected delta.**

Both original findings are addressed by the frozen native correction. This is approval of that source delta, not overall Q2 acceptance or completion of independent execution verification. The parent's forthcoming seven-method verifier report remains pending reconciliation in this same context.

The original `q2-js-serialization-code-review.md` remains unchanged as the historical **REVISE** decision.

## Reviewed scope and identity

Read the correction handoff/seal first, then compared `scripts/measure_js.mjs` directly against the parent's exact pre-fix snapshot. Reviewed the new owner test additions, both actual independent assertion files, retained discriminating red evidence, and the owner's current-byte focused execution records. No tests were executed by this reviewer.

| Input | Verified SHA-256 |
|---|---|
| `q2-js-serialization-corrections-01/seal.json` | `c138dec76b7abc47b334caf5e77e99236154583bf745573312c8b5d44a04fa5b` |
| `q2-js-serialization-pre-fix.mjs.snapshot` | `35acb58ccd11dce9daa601e640c47b763e8625c84919158610cf33107f4b46bc` |
| Corrected `scripts/measure_js.mjs` | `ba0ca909699ca453515a0eaad5206c81d5afe6abcd1fb7b47723e8a71f1c0900` |
| Corrected `scripts/tests/measure_js.test.mjs` | `52eb427d1a39717a9b5cd85257eff5436725debf2d44535cd3051f7c80343882` |
| Corrected `scripts/tests/test_measure_js.py` | `21d8488537226adcdafe93eb4308d4abd3c3b63d6afc3adab0686d0d37468b3a` |

The production comparison is confined to binding-property discovery/reference emission, suppression of duplicate explicit binding-key references, and splitting dynamic-import handling from the unchanged require arity rule. Candidate generation, exported interfaces, record shapes, parser/settings identity algorithms, and Python integration are not changed by this correction.

## R1 disposition — addressed

**Source:** `scripts/measure_js.mjs:485–493,501,707–730`.

- `bindingProperty` distinguishes the selected property from the locally declared binding. It looks up the selected property's symbol through `checker.getPropertyOfType(checker.getTypeAtLocation(node.parent), key.text)`, using the actual ObjectBindingPattern type rather than the local binding symbol.
- The discovery pass includes that selected symbol's declarations before declaration descriptors and IDs are built. This is necessary for a source-backed local resolution, not just an extra reference to an undiscovered symbol.
- Serialization emits a separate `property` reference at the selection span. Ordinary declaration discovery and local binding identity remain intact; the fix does not collapse a renamed/shorthand binding into its source export.
- Shorthand, explicit identifier keys, string-literal keys, and literal-computed keys take the static lookup path. Computed identifiers and rest selections instead produce dynamic references with no guessed target IDs. Static lookups without a resolvable declaration produce unresolved references. Both uncertainty cases add explicit reflection sites through `outsideSite`, which populates program-level and per-file SyntaxEvidence outside-model records.
- The new `bindingKey` guard suppresses a direct explicit identifier key in the generic identifier visitor. It does not suppress identifiers inside a computed selection expression, which remain real expression references. Shorthand declaration names continue to be excluded from generic reference emission, while their selected-property read is now emitted separately.

**Discriminating evidence:** The unchanged independent R1 assertion (`scripts/tests/measure_js_serialization_independent.test.mjs:172–210`) compares actual checker property lookup with the exported symbol and separately locates each local BindingElement's serialized identity. The preserved red result has missing property targets for both shorthand and quoted-key selections. The owner's corrected run has the expected export target for both:

- Export ID remains `367749885dc4e5bf2d08d70a641c5fdf5420522e3e91daa35e1df14901184134`.
- Both local binding IDs remain unchanged across red/green and distinct from that export ID.
- Property target lists change from `[[], []]` to two singleton lists containing the export ID.
- Both runs retain zero compiler diagnostics; the ordinary namespace-property/checker controls are present. The corrected native run returns 0 with empty stderr.

This addresses the reported missing relationship rather than merely making the fixture parse or permitting an unresolved placeholder.

## R2 disposition — addressed

**Source:** `scripts/measure_js.mjs:666–669`, with unchanged `moduleReference` behavior.

Dynamic `import()` now forwards its actual first argument to literal/computed classification even when options are present. Global `require()` has its own branch and still supplies an argument only when its argument count is exactly one. Shadowed require recognition remains governed by the unchanged `isGlobal` check.

The unchanged independent R2 assertion (`scripts/tests/measure_js_serialization_independent.test.mjs:212–248`) verifies the literal dependency and matching SyntaxEvidence record together, alongside one-argument literal and genuinely computed controls.

The retained records show:

| Source form | Red result | Corrected owner-run result |
|---|---|---|
| `import('./origin.mjs')` | Local target; one literal syntax record; no computed site | Same |
| `import('./origin.mjs', {})` | Dynamic/null specifier; no literal syntax; one computed site | Local `origin.mjs`; literal specifier; one matching syntax record; no computed site |
| `import(name, {})` | Dynamic/null specifier; no literal syntax; computed site | Same |

Both versions' fixtures have zero compiler diagnostics. The corrected regression returns 0 with empty stderr. The fix does not reinterpret import options as a module specifier or relax the require rule.

## Owner fixture and independent-test relevance

The new ordinary-discoverable owner method is `SharedJSCoreTests.test_native_review_corrections_uncertainty_and_require_arity` (`scripts/tests/test_measure_js.py:215–216`). Its fixture additions at `167–183` use real Git/materialized subjects and the existing qualified native harness.

The new native case (`scripts/tests/measure_js.test.mjs:85–141`) checks:

- Four static selections of the Unicode export `café`, including renamed and literal-computed keys, against the actual export ID.
- Distinct local exported binding IDs.
- One computed selection, one rest selection, and an index-signature-only static lookup, with dynamic/unresolved states, empty target IDs, and matching uncertainty sites in both evidence locations.
- Literal dynamic import with/without options and a computed import.
- Ordinary one-argument require, unchanged two-argument handling, and no edge for shadowed require.
- Existing byte-range/source-hash checks over the serialized records.

I read the actual independent Python/Node files, not just their test counts. The regressions are registered at top level, use real Program/checker controls, and the Python harness requires actual native result evidence, matching runtime/case/controller identity, a nonempty native test count, successful return code, and empty stderr. The earlier rejected empty registration run remains historical **non-proof**; the corrected red captures are the two genuine assertion failures.

The independent merged-declaration/import-equals/namespace-reexport method is also present and was source-reviewed. Its older successful execution is not credited as fresh corrected-source proof here. Its new independent execution belongs to the pending verifier report.

## Execution evidence reconciled, not rerun

| Owner-retained execution | Actual outcome |
|---|---|
| Two unchanged independent regressions | 2/2 passed, 65.456s |
| Four affected owner methods | 3/4 passed, 213.565s; candidate capture returned 124 / `[idle-timeout]` |
| One bounded candidate-only retry | 1/1 passed, 70.077s, on unchanged source/test bytes |

These establish passing owner-retained proof for **six distinct methods**, across **seven method invocations including the failed timeout invocation**. Nested native tests and the repeated candidate method are not additional distinct methods. This is **not** a complete fresh 15-method suite.

The timeout remains a failed execution, not an assertion result or a passing retry retroactively applied to the original run. Native bounds remain idle 30/max 90; the owner's outer captures use idle 120/max 900. All five owner native captures, including timeout and retry, pin the same corrected controller and their 12 executing-source files match current bytes. Complete descendant cleanup remains **UNKNOWN**.

The verifier's separate current replay of four owner methods plus all three independent methods—**seven distinct methods**—has not been read, polled, or counted as completed.

## Preservation reconciliation

- All **34** entries across the correction seal's changed sources, historical references, owned evidence, and unchanged independent tests match their current hashes and lengths.
- All **199** `after.json` entries match current bytes. Comparing the sealed before/after catalogs yields exactly the three authorized source/test changes; the other **196** entries remain unchanged.
- All **30** entries across the retained red seal's evidence/current-test lists match. Historical registration-error records and discriminating red captures are preserved.
- As a read-only identity check, removing only the new owner Node case and the new Python fixture/method additions **in memory** reproduces both original owner test-file hashes exactly:
  - Node: `cc9a6476f570195e37d03f57c82dca29dc26c2472be61e66af0006714d48967e`
  - Python: `42a1c60aafc131598c1dde2294edc135a375ad60b479ce516920809d63fb806f`
  Thus the existing owner assertions were not weakened or rewritten.
- The actual independent test files remain unchanged from the discriminating red proof:
  - Python: `8917a3d561ed01afc6d2dcb5abc39af1cf232d8e8741283e6818e12156aae4e5`
  - Node: `fba787cf2e7e0806eea8f2801d87f168b9e1e3facd361b941b1534ba921942c7`
- The initial review remains hash `59fdd6e44214b693d895637f455c74678308d497ac8733aadfd0ff623e612482`. Original contract, root amendment, JS revision 3, historical seals, and unchanged measurement collaborators remain covered by the preservation reconciliation; no replacement pin archive was created.

## Boundary and next reconciliation

**No further source revision requested by this focused review.** Reconcile the parent's completed verifier report once available, without expanding this checkpoint into command/manifests/graph/replay/collector implementation.

The native API remains a library checkpoint, not an accepting Context or configured JS measurement. No root mutant execution, full quality closure, live app workflow, or fresh-agent full-workflow proof is inferred. Human sign-off remains unconfirmed and publication remains 403-blocked; neither was exercised by this review. The subsequent app-driven workflow exercise is the parent's separate next activity.

This review ran no tests/suites, qualification, production edits, agents, installs, commits, or pushes. Read-only external diff commands used the managed Python `scripts/run.py --idle 30 --max 120`; Git's no-index exit 1 denotes the expected source difference. The only authored file is this new report. Stop pending the final correction-proof handoff.

## Final independent-proof reconciliation — 2026-09-18

**Disposition: bounded functional preservation is acceptable. The focused source APPROVE stands; no further correction is required to resolve R1/R2 at this native-library checkpoint. Test reliability remains limited.**

This appended reconciliation resolves the pending-verifier status above without rewriting the earlier review history. It does **not** approve whole Q2, full quality, or a green combined suite.

### Evidence and preservation

Read the final independent report and seal at `q2-js-serialization-correction-independent-20260918-v1/`. The seal matches the supplied SHA-256:

`591bbc2fafced3f5485f3c08cf2f029ad72884841082020cae79eb20ca276b31`

Verified the 42 inspected seal entries covering sources, independent tests, evidence, owner seal, and pre-fix snapshot. Independently reconstructed the owner's sealed preservation-catalogue union and checked all **223 unique source/history paths** against current hashes and byte lengths. The approved production/test hashes remain unchanged. The initial REVISE report still hashes to `59fdd6e44214b693d895637f455c74678308d497ac8733aadfd0ff623e612482`.

Reconciled the actual captured streams, native result records, and executing-source identities, rather than accepting only the final report's counts:

| Fresh independent execution | Outcome retained |
|---|---|
| Entire unchanged independent module | **3/3 passed**, 103.513s, exit 0 |
| Four affected owner methods | **3/4 passed**, 208.240s, exit 1; candidate idle timeout |
| Sole candidate-only retry | **1/1 passed**, 65.948s, exit 0; same source/test bytes and bounds |

Thus **seven distinct methods have passing evidence across eight method invocations**. The eight nested native calls are not eight additional tests. **The combined owner run remains failed.** The earlier owner's separate timeout/retry is historical and is not included in these fresh totals.

### Reconciliation with source approval and added assertions

- **Original R1 red case:** Both namespace selections now reference export ID `367749885dc4e5bf2d08d70a641c5fdf5420522e3e91daa35e1df14901184134`. The two distinct local binding IDs remain identical to the preserved red-run identities. The successful checker/ordinary-property controls and zero diagnostics remain present. The fresh independent result bytes also match the owner's corrected R1 result bytes.
- **Original R2 red case:** The options-bearing literal import now has its literal specifier, local `origin.mjs` target, exactly one literal syntax record, and no computed-import site. The plain literal and genuinely computed controls retain their expected behavior. Zero diagnostics and empty successful stderr remain. The fresh independent R2 result bytes match the owner's corrected result bytes.
- **Original independent merged-symbol case:** Refreshed on the approved corrected controller, not merely carried forward. The actual result reports merged declarations, import-equals, and namespace-reexport verification; `Parcel` and `Box` each retain two declarations under their respective single symbol IDs. The previously reviewed checker, alias, reference, and canonical-ID assertions were unchanged.
- **Added owner case:** Its fresh successful invocation exercises the already-reviewed four known property selections, distinct local identities, computed/rest/unresolved uncertainty, literal import options, and require/shadow controls. The records/origins and freshness methods also pass freshly.
- **Candidate preservation:** The isolated retry actually completes the unchanged byte/identity assertions and retains a population of 12 eligible fixture candidates, 35 no-operator lines, and two unsupported files. This is functional candidate evidence, not mutant execution. Its capture and all other fresh owner captures bind the approved controller and matching executing-source files.

No independent assertion was weakened, skipped, or turned into an expected failure. The rejected empty registration attempt remains non-proof; the later genuine red failures and current green executions establish the discriminating R1/R2 transition.

### Recurring timeout: explicit reliability assessment

The same candidate method timed out in both the owner's combined correction selection and the independent verifier's combined selection, then passed in each bounded isolated retry. This is a **recurring, unresolved test-reliability limitation**, not a one-off event that this review dismisses.

The fresh failed native capture contains **no stdout and no native result**, returns 124, and reports `[idle-timeout]`. It supplies no candidate-behavior proof. The passing retry changed selection/capture/temp fixture locations, not source/test bytes or the idle 30/max 90 native limits. Its success cannot retroactively make the failed combined invocation green, establish reliable combined execution, or identify the timeout's cause. These records do not locate the silent interval or distinguish startup, fixture/parser work, scheduling, and other timing causes. Complete descendant cleanup remains **UNKNOWN**.

Nevertheless, a further code correction is **not required for bounded functional preservation**:

1. The actual R1/R2 defects are independently red-to-green under unchanged discriminating assertions, and the narrow source fixes explain those results.
2. Every requested distinct method has fresh completed passing evidence on the approved bytes, including the candidate method under the same bounds.
3. No remaining assertion failure, weakened test, changed timeout, or concrete production correctness defect is demonstrated by the timeout capture.
4. This decision preserves a native-library checkpoint with disclosed limitations; it is not certification of a reliable suite or a production measurement lifecycle.

Accordingly, no speculative production change, timeout increase, repeated-until-green execution, or further component work is requested. The unresolved reliability limitation must remain visible wherever this checkpoint's evidence is summarized; it would not satisfy a future requirement for a consistently green combined run.

**Checkpoint resolved for bounded preservation and the parent's next app-driven workflow exercise.** JS-SYMBOL-01 and JS-PARSE-01 remain overall partial despite the corrected cases being verified. Whole-Q2/full-quality approval, full15/root-suite proof, configured measurement, and live app workflow success are not granted. Human sign-off remains unconfirmed and publication remains 403-blocked.

This reconciliation reran no suite and made no source/test changes. Only this final section was appended to the r2 report; the original REVISE history and sealed evidence were preserved.

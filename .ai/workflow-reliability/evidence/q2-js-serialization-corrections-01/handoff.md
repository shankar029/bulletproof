# Focused serialization review R1/R2 correction

**Owner correction ready for independent revalidation/review. Not overall Q2 acceptance.**
The parent's retained red proof reproduced both findings with successful checker controls,
no diagnostics and two discriminating failures. Neither independent assertion file was edited.
Original owner/verifier handoffs, seals, red captures and preliminary review remain unchanged.

## Correction and scope

- **R1:** A shared `bindingProperty` lookup uses the actual checker/type of an object binding
  pattern, rather than treating its local declaration name as a property use. Discovery includes
  the selected source-property declarations. Serialization emits a separate `property` reference
  for shorthand, named/literal and literal-computed selections, retaining distinct local binding
  identities. Computed/rest selections emit dynamic references and outside-model sites;
  unresolved static lookups likewise disclose uncertainty. Explicit identifier keys are not
  emitted a second time through the generic identifier visitor.
- **R2:** Dynamic `import()` passes its actual first argument to literal resolution even when
  options are present. `require()` remains a separate branch with its previous one-argument rule.
  Truly computed imports still have dynamic references/outside-model sites.
- Only `scripts/measure_js.mjs` and the two directly related owner test files changed.
  No interfaces/record shapes, policies, Python measurement integration, frozen core, references,
  qualification files, independent tests or unrelated files were edited.

The supplemental ordinary-discoverable owner method is
`test_measure_js.SharedJSCoreTests.test_native_review_corrections_uncertainty_and_require_arity`.
Its real Git fixture checks four known namespace selections against the actual export ID,
distinct local identities, computed/rest/index-signature uncertainty, literal import options,
computed imports, and unchanged ordinary/two-argument/shadowed `require` handling.

## Exact focused execution

All invocations used the managed Python 3.14.2 executable, qualified Git PATH prefix,
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, and exclusive `Q2_JS_RECORDS` directories.
Outer wrapper: `scripts\run.py --idle 120 --max 900`. Native children: **idle 30 / max 90**,
unchanged. Actual argv/environment/source hashes are in each directory's `invocation.json`;
streamed wrapper output is in `console.txt`, with explicit `exit.json`. Native captures and
actual result bytes are retained by the existing harnesses.

Append each selection below after:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -u -m unittest discover -s scripts\tests
```

| Directory / selection | Actual result |
|---|---|
| `independent`: `-p test_measure_js_serialization_independent.py -k ReviewRegressions -v` | **2/2 passed, 65.456s, exit 0.** The unchanged R1/R2 methods each ran one actual native test with successful controls, processed census, zero diagnostics and empty stderr. |
| `owner`: `-p test_measure_js.py -k review_corrections -k serialized_source_records -k serialized_freshness -k candidates_from_shared_syntax -v` | **3/4 passed, 213.565s, exit 1.** The candidate method returned capturer 124 / `[idle-timeout]`, not an assertion result. This invocation is retained as failed, not relabeled green. |
| `owner-candidate-retry`: `-p test_measure_js.py -k candidates_from_shared_syntax -v` | **1/1 passed, 70.077s, exit 0.** The single bounded smaller-selection retry used unchanged production/test bytes and unchanged timeouts. |

Thus **six distinct selected Python methods have current-byte passing proof**, across seven
method invocations including the retained timeout. Nested native tests and the repeated candidate
method are not extra distinct acceptance tests. This is not a fresh full 15-method replay.
The original merged/import-equals/namespace-reexport proof remains historical, not refreshed.
Scoped `git diff --check` returned 0.

The timeout's narrow process observation found no remaining command line for this exact native
test script before retry. Complete descendant cleanup remains **UNKNOWN**. No process-name killing,
host/privilege changes, timeout increase, test weakening or unowned-temp cleanup occurred.

## Frozen source and preservation

| Changed path | SHA-256 |
|---|---|
| `scripts/measure_js.mjs` | `ba0ca909699ca453515a0eaad5206c81d5afe6abcd1fb7b47723e8a71f1c0900` |
| `scripts/tests/measure_js.test.mjs` | `52eb427d1a39717a9b5cd85257eff5436725debf2d44535cd3051f7c80343882` |
| `scripts/tests/test_measure_js.py` | `21d8488537226adcdafe93eb4308d4abd3c3b63d6afc3adab0686d0d37468b3a` |

`before.json`/`after.json` reconcile **199 paths**: exactly those three permitted source/test
changes, with the other **196 paths unchanged**, including independent tests, historical evidence,
authorities and untouched collaborators. Every executed invocation's pinned source files match
the final bytes. The adjacent new `seal.json` binds this correction without overwriting old seals.

R1 directly addresses JS-SYMBOL-01; R2 directly addresses JS-PARSE-01 literal dependency evidence.
Passing this owner selection is not an independent approval or evidence that future accepting
consumers exist. No root suite/probe, actual root mutants, new qualification, packages, agents,
commits, pushes or next-layer implementation occurred. The historical symlink limitation remains
unverified. Command/manifests/collectors and live workflow quality are not claimed.

**Stop here for parent revalidation/review and preservation. The parent's subsequent priority is
the actual app-driven workflow exercise, not command/manifests/collector expansion.**

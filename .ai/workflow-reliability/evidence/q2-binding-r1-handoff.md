# R1 qualification ownership correction

**Owner development complete; independent verification/review pending.** Only the R1 ownership boundary was reopened. This does not refresh or replace the historical 262/263 Python-method or 13-entry native proof.

## Actual counterexample, before the fix

`q2-binding-r1-reproduce.py` first required the reviewed `measure.py` SHA-256 `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4`. It constructed the real source-binding fixture, validated its configuration, staged unchanged qualification inputs, removed one qualification row from an actual new manifest file, and assigned the newly computed Artifact to `Context.output_manifest`. The original input reservation remained.

The unfixed inspector returned successfully: **one audited real Node launch, exit 0, actual TypeScript symbol `answer`**. Source bytes remained unchanged during this reproduction. `q2-binding-r1-repro\reproduction.json` retains both manifest documents, the removed row, actual Context/ref, observed result, command capture and launch audit. The accompanying raw record retains request/result/command contents. This is an executed counterexample, not the reviewer's static predicate check and not a passing ownership test. The reproduction script intentionally refuses different source bytes, including the fixed implementation.

## Narrow correction

`scripts\measure.py::_validate_binding_ownership` derives the canonical selected Artifact set using existing `tool_artifacts(config)`. It requires exactly one unchanged `{artifact, role: "qualification", revision: null}` row and exactly one reservation for each selected path. Canonical JSON comparison distinguishes altered Artifact types as well as values. Extra unselected qualification rows reject.

Existing `_path_partition` validates input/reservation declarations separately and their combined namespace, rejecting duplicate, conflicting, case-colliding and ancestor/descendant paths. Unrelated nonqualification input rows are not treated as additional selected qualifications; this is not a new full metric validator.

`inspect_source_binding` calls this helper immediately after decoding the actual manifest and **before request creation or child execution**. Its original/copy/resource/controller checks, smoke-output checks, actual execution, and post-execution freshness checks remain.

A read-only removal of just the added helper and its call reconstructed the reviewed source hash **exactly**, including line endings: `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4`. Thus no other `measure.py` function or bootstrap changed. Only `scripts\tests\test_measure_source_bindings.py` was otherwise modified; it adds one normally discovered regression method and its `sys` import. No CLI, frozen helper, runner, schema, collector, resource/package, shared state or prior evidence changes.

## Same-byte focused proof

`q2-binding-r1-final\result.json` records **10 distinct selected methods passing**, zero failures/errors/skips, in **877.710 seconds**, with identical prospective before/after source/helper/review pins. Eight methods are source-binding tests, including the new R1 method; two cover existing native-root/Q1 configuration and collision behavior. The existing source methods genuinely execute TypeScript/lizard/Vulture at both Git revisions, poison preload environments, reject resource/import tampering, and preserve native/empty configuration behavior.

The R1 method exercised **20 actual rehashed malformed manifest files**: missing one/all rows, wrong role/revision, duplicate/conflicting rows, changed hash/length/path/type, extra row fields, missing/duplicate/prefix-colliding reservations, input and cross-namespace prefix conflicts, an unselected qualification, a Windows case collision, and malformed input/reservation lists.

For every case the inspector raised `ValueError`, with **zero audited subprocess attempts, zero audited run-root write opens, and no request/result/command outputs**. The same installed audit hook then observed a valid TypeScript control: **one real launch and two controller-side write opens**, with actual symbol `answer`. No runner or predicate was mocked. The audit covers this Python controller's events, not an OS-wide process monitor.

`r1-ownership.json` retains every malformed document, actual manifest Artifact, rejection and audit/output-absence observation. `r1-valid-control.json` retains the functioning audit control. `raw-*.json`, `two-revisions.json` and `environment.json` retain actual invocation evidence. These are binding records, not metric observations; command streams retain the existing runner's replacement-decoded/newline-normalized semantics. Temporary fixture paths describe completed executions rather than live replay roots.

The earlier `q2-binding-r1-focus` run passed the one R1 method in 36.863 seconds on the same fixed production bytes. It is a repeated method, not an eleventh distinct final test. The final suite streamed real resource/test progress under idle 120 / max 1200; no timeout inflation, retry, buffering of a whole long suite or fabricated heartbeat was used. Owned diff whitespace checking passed.

## Hashes

| Artifact | SHA-256 |
| --- | --- |
| `scripts\measure.py` | `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1` |
| `scripts\tests\test_measure_source_bindings.py` | `bcc36f23061dd5b4db2dfcb161c0202bbe95db1fb930b1c6ef79fe8c9b95d1b3` |
| `q2-binding-r1-verify.py` | `2bac110b6f2a2fb5b4418f1a513f04eea61c828b8986eda24b34576d5fb626e0` |
| `q2-binding-r1-reproduce.py` | `1452fd5a42e7010d4019e6bc6a70e1ef875bb1e0b081d742a3985ae37765bb5f` |
| `q2-binding-r1-repro\reproduction.json` | `a74b337ca26cb7ca7991f53069c60abca01afec6b26e1b262beb82fef9e0d46f` |
| `q2-binding-r1-focus\result.json` | `d32cd7f5f35fba1336bab645e4ad284289803efe63938d78f96416f09f2a71c1` |
| `q2-binding-r1-final\result.json` | `c8feeb8919d31dac458b5a8222f470612923c63dbcf7811b311f6db8cd12e519` |
| `q2-binding-r1-final\r1-ownership.json` | `eeb096ac5ace1bda32e854209ce36e7ea378dbda225107e6f21f042286354303` |
| `q2-binding-r1-final\r1-valid-control.json` | `cee9e18ee8ba6b2b566a01f0aa675e74b8262ab90e3923cb3e51ea797dbac8a2` |
| `q2-binding-r1-final\two-revisions.json` | `70d447ea7662ae8892f16ef5230c4ddc96bb00b5bd903d03601335e44b8c1131` |
| `q2-binding-r1-final\environment.json` | `dfad4a44dee60249a7e8cf386d601ab97cdfb66039fef5acaa58dd88c7abfd73` |
| `q2-binding-r1-final\raw-901e8e8620fb.json` | `6e9efe05c8b4dbf099c55d461bfb3a8ae4726c4f8cce2d58bd4c8c8da7278c58` |
| `q2-binding-r1-final\raw-b9c3fd6b5ae1.json` | `10e99cb96e76fede0aa9bac1c47281d9c57415c40ea5b3fc558522b34dbfc3fe` |
| `q2-binding-r1-final\raw-cf7d082d6447.json` | `e438801eb3571f0eb54c467ed9ac62b53c48b3ef2d6658adbebff306289c0664` |
| `q2-binding-r1-final\raw-d4215de8eeb7.json` | `bff64c7457fdfc294044ec1aac91b8c4fba79304003c64ebe3777d09dee888f3` |
| `q2-binding-r1-final\raw-e994874c51a1.json` | `68844e74913cb64cde030d4b936adf6608bfbead4eb8e13660b0983b4ca93289` |
| `q2-binding-r1-final\raw-f9df00e58d91.json` | `313916dac873f8f697b2ca332851a324133cfd07f1e9130307fa679ca3339826` |

Additional unchanged controller/helper, amendment and review hashes are in the final result's identical `before`/`after` maps.

## Fresh affected replay

From this worktree, with a new evidence directory:

```powershell
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;'+$env:PATH
$env:PYTHONDONTWRITEBYTECODE='1'
$python='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $python -B scripts\run.py --idle 120 --max 1200 -- $python -B -u .ai\workflow-reliability\evidence\q2-binding-r1-verify.py q2-binding-r1-independent
```

For only the ownership method, append `test_measure_source_bindings.SourceBindingTests.test_qualification_ownership_rejects_rehashed_manifests_before_launch` and use a different fresh directory.

The original symlink WinError 1314 remains retained and environment-blocked, not retried, skipped or counted as passing. No unowned old temp cleanup, privilege changes, agents, installations, commits or pushes occurred. Missing collectors, coverage/mutation, full raw reconciliation and the guarded producer bridge remain outside this correction. Parent acceptance still requires the same independent verifier's fresh affected proof and the separate reviewer's reconciliation. This owner is now idle.

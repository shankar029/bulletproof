# Q2 source-binding development checkpoint

Status: implemented and locally exercised bounded source bindings; **not accepted Q2, a dependency gate, an independent review, or a joint source freeze**. The parent owns those decisions. No additional production edits after this handoff without parent feedback.

## Delivered scope

FACT: `scripts\measure.py` now extends the native-only binding path for TypeScript 5.9.3, lizard 1.24.0 and Vulture 2.16. The existing source-roots JSON shape is explicit per-tool configuration; exact original qualification/resource records remain mandatory authority. Verified relocation uses the same pinned relative resource bytes, not package discovery. Executables, modules, package resources, Python runtime files, qualified PE dependency candidates and fixed settings contribute to the common toolset binding. Source packages stay external to subject/controller/run roots. Empty Q1 and native bindings remain supported.

FACT: Python executes a shipped fixed bootstrap through the existing bounded runner with `-I -S -B`, the four qualified Python source roots, the simple pathspec backend, no installed distribution/entry-point plugins, and the qualified absent optional dependencies. The source-import finder checks actual file hashes before loading; runtime/source module observations are checked against their pins. The existing builtin/frozen importer order is retained. Node executes the absolute pinned TypeScript module with qualified compiler options, controlled compiler-host reads and strict UTF-8 resource decoding. Preload/Python-path environment variables are removed. Neither bootstrap invokes the historical session helper or embeds its absolute locator.

FACT: `source_binding_paths` reserves deterministic request/result/command paths. `inspect_source_binding` requires those reservations and fresh owned outputs, verifies original and staged inputs and the executing/copied controller before/after execution, checks actual observed imports/resources/runtime settings, and rechecks the produced artifact bytes. Nonzero execution or stderr raises an explicit error and retains command output. The request/result/command records are **binding smoke evidence, not MetricObservation/RawMetricEvidence or metric manifest reconciliation**.

The actual bounded API invocations exercise TypeScript syntax creation, traversal, compiler program, checker and diagnostics; lizard's strict-decoded text API and seven Python/JS reader mappings; Vulture scan, min-confidence-80 findings and a qualified whitelist resource with pre-report error state retained. No subject code is executed by these smoke programs. Startup standard-library modules are checked as observed runtime files; this is hash/provenance checking, not a sandbox, lock, authenticated provenance or a complete loaded-native-DLL trace.

## Actual development proof

FACT: `q2-adapter-source-dev02\result.json` records **10 distinct selected passing methods**, no failures/errors/skips, and identical before/after hashes for the executing/owned file set. Seven are new source-binding methods; three are native-root/Q1 compatibility methods. Unittest duration: 631.711 seconds. This is not a full-suite success claim.

The selected tests execute all three tools at two actual Git revisions with a shared toolset; execute real poisoned Node/Python preload environments without running the marker scripts; execute a relocated TypeScript package and reject a changed library resource; reject an unqualified Python import before its marker code runs; reject missing qualifications, wrong module/version/settings, absent binding, missing reservation and controller changes; preserve empty/native binding validation, root collision/hardlink rejection and standalone Python graph behavior.

| Tool, each revision | Qualified package files bound | Distinct runtime files bound | Observed module rows | Additional resource reads |
| --- | ---: | ---: | ---: | ---: |
| TypeScript | 132 | 0 (Node executable separately bound) | 1 | 87 |
| lizard | 3216 | 100 | 189 | 0 |
| Vulture | 3216 | 100 | 189 | 1 |

Python's package scope intentionally includes lizard, Vulture, Pygments and pathspec together, matching the qualification bootstrap. Runtime/module aliases explain why module-row counts are not unique-file counts. Node reported `v24.11.1`, **arm64**; Python reported managed 3.14.2 AMD64. Both revision sets used toolset SHA-256 `6d3de8a3edad775ef11895125bca7f832e078426c0d11759b5da8f377fc9c3aa`.

FACT: final records retain nine successful child invocations and one expected failing unqualified-import invocation. `raw-*.json` retains prepared requests, dedicated JSON results where produced, and actual command captures, including the expected rejection's stderr. `two-revisions.json` and `environment.json` retain decoded observations plus command captures. Runner stdout/stderr are replacement-decoded UTF-8 and newline-normalized, not byte-exact streams. Temporary fixture roots are cleaned; retained paths document that execution, not live portable fixtures.

Historical evidence is separate: `q2-adapter-source-dev01` contains the earlier one-method/six-invocation smoke on its own then-current bytes (416.258 seconds). Do not add it as another distinct final test. The earlier native-root 14-method pre-correction replay and two repeated correction methods remain untouched and are not final source-binding acceptance.

The bounded harness streams actual completed unittest/subtest progress and completed resource rehashes. It uses short owned OS-temp fixtures. Final persisted evidence path lengths were 157-167 characters. No captured outer long-suite buffer, deep artifact-directory TEMP, timeout retry, fabricated heartbeat, package acquisition or privilege change was used. Owned diff whitespace checking also completed successfully.

## Final-byte pins

| Path | SHA-256 |
| --- | --- |
| `scripts\measure.py` | `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4` |
| `scripts\tests\test_measure_source_bindings.py` | `e0cf6722ec29f31085e4fa0cc311d542fc80950e53ed37b790b5fa6fa3ca092e` |
| `scripts\probe.py` (unchanged in this slice) | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |
| `scripts\tests\test_measure_q2.py` (unchanged in this slice) | `8f0adaa478501bb4d1b81bb54ecdf45011d68787977537401fc4f24e563db7f8` |
| `q2-adapter-source-development.py` | `8f275d85afbac7eb608e1a464924b373c85285e3833e7c0ce26e19d32024121d` |
| `q2-adapter-source-dev02\result.json` | `e778c2eac101f3c71ff19d97ca7fb1f7fe83525f3cc334ca0274edb0ef44ec3d` |
| `q2-adapter-source-dev02\two-revisions.json` | `d3a5b35e9e50dfc5fbb39415c9266a2ae8f3a5d601100a85badb90538b6ee1c4` |
| `q2-adapter-source-dev02\environment.json` | `46dfe172db35ffc361e6b2d33458c710c4e15aec0bdf9a68749aed80f70c4469` |
| `q2-adapter-source-dev02\raw-901e8e8620fb.json` | `5f8628f971f5ed989ebc43a28205ac9b76003700f891ce796bea7a3ae4d87f29` |
| `q2-adapter-source-dev02\raw-b9c3fd6b5ae1.json` | `ca50bd6bafb0932dd1c135e0f2e05a48c63763c6d43da66046b02e86cacafa69` |
| `q2-adapter-source-dev02\raw-cf7d082d6447.json` | `e438801eb3571f0eb54c467ed9ac62b53c48b3ef2d6658adbebff306289c0664` |
| `q2-adapter-source-dev02\raw-d4215de8eeb7.json` | `c8d21ca4c3bdc55aaef11d115980e203e5b406dbadd708fb958643db16815f85` |
| `q2-adapter-source-dev02\raw-f9df00e58d91.json` | `18189a5c52d6b6b0879cc166f735007316901e5b337ba3686fab93ed362cb488` |

The result also pins graph, runner, evidence and test helpers without modifying them. Approved root amendment SHA-256 remains `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1`; focused review remains `2e14e84f8b8201a9d43c6ff2070631ce68db595f03e529c6e17d243ddfbd6062`. No claim is made about the concurrently edited CLI owner's files.

## Replay and remaining limits

Exact selected replay, from this worktree, using a fresh evidence directory:

```powershell
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;'+$env:PATH
$env:PYTHONDONTWRITEBYTECODE='1'
$python='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $python -B scripts\run.py --idle 120 --max 1200 -- $python -B -u .ai\workflow-reliability\evidence\q2-adapter-source-development.py q2-adapter-source-parent01
```

The native-root symlink-creation case remains **environment-blocked by WinError 1314**, neither retried here nor skipped/claimed passing. After the parent supplies an environment that can create the real symlink, the focused finishing command is:

```powershell
& $python -B scripts\run.py --idle 120 --max 1200 -- $python -B -u .ai\workflow-reliability\evidence\q2-adapter-source-development.py q2-adapter-source-symlink01 test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects
```

Still pending by scope: shared TypeScript syntax/symbol adapter, actual JS census/parsed inventory, scalar and static-graph collectors, raw metric producer re-decoding/reconciliation and full CHECK-SCALARS/CHECK-GRAPH/CHECK-JS-PARSER/CHECK-RECONCILE integration. Nonempty JS entrypoints still explicitly reject as unimplemented. This binding inspector is not integrated as a metric collector or default-probe metric input; do not treat smoke output as measurement. All nine required metrics and their policies remain unchanged; missing coverage/mutation continue to prevent completeness. The guarded producer bridge, Q3/Q4, root mutants and reports remain separate.

No agents, installs, commits, pushes, new workflow/design cycle, shared-state/report/guide edits, or CLI-owner edits occurred in this slice. Independent verification/review and final integrated acceptance still wait for the parent to freeze both writers.

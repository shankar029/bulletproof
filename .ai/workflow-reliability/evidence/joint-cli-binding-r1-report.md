# R1 independent affected verification

**VERIFIED-WITH-LIMITATIONS for the R1 affected checkpoint.** All **10 selected methods passed** on the fixed frozen bytes in **801.802652 seconds**, with zero unittest failures, errors or skips and no timeout. R1's required pre-request ownership rejection is demonstrated. Parent acceptance and the **same reviewer's focused re-review remain pending**; this is not full Q2 or quality acceptance.

## Scope and actual change

FACT: Read `joint-cli-binding-code-review.md`, `q2-binding-r1-handoff.md`, the root amendment, owner capture/reproduction helpers, the actual inspector/helper/callees, source-binding tests and selected compatibility test bodies. The executed selection matches the owner's ten methods: all eight source-binding methods and two `ToolRootTests` methods. Exact discovered and passed IDs are in `joint-cli-binding-r1-records/plan.json` and `reconciliation.json`.

FACT: Only two of the previous 4,608 pinned files differ from the reviewed checkpoint, and both equal the authorized new hashes:

| File | Current raw SHA-256 |
| --- | --- |
| `scripts/measure.py` | `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1` |
| `scripts/tests/test_measure_source_bindings.py` | `bcc36f23061dd5b4db2dfcb161c0202bbe95db1fb930b1c6ef79fe8c9b95d1b3` |

Removing just `_validate_binding_ownership` and its one call reconstructs the prior raw `measure.py` hash exactly: `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4`. Removing just the new test method and `sys` import reconstructs prior test hash `e0cf6722ec29f31085e4fa0cc311d542fc80950e53ed37b790b5fa6fa3ca092e`. This is a raw-byte reconstruction, not a Git-normalized or AST-only equivalence claim. `narrow-change.json` and `r1-only.diff` preserve the comparison; the latter retains CRLF-bearing lines as a display artifact.

The new call is at `measure.py:934`, after loading the actual referenced manifest and before any request publication or tool execution. The helper at `901-923` uses existing `tool_artifacts`, canonical JSON and `_path_partition` checks. All other implementation bytes, including the original/copy/resource/controller pre/post checks and tool bootstraps, reconstruct unchanged.

INFERENCE: This narrow dependency change supports retaining the prior unaffected regression evidence with its original limits. It does **not** make the historical 262 methods fresh on the new `measure.py`.

## Counterexample and fresh proof

FACT: Independently checked the owner's actual unfixed reproduction artifact, including its pinned SHA-256, missing qualification row with reservation still present, recomputed malformed-manifest hash/length, audit command versus Windows-quoted argv, exit zero, actual TypeScript symbol `answer`, and retained request/result/command content hashes. See `historical-counterexample-check.json`. This reconciles an owner-recorded real execution; the unfixed implementation was not restored or executed in this verification.

FACT: The fresh R1 test wrote **20 distinct malformed manifest files**, recomputed their actual references, and exercised the real inspector. Each rejected with a `ValueError` before any audited subprocess attempt or run-root write open; request/result/command outputs were absent. Reconciliation independently recomputed all 20 saved manifest hashes and lengths.

The cases cover missing one/all qualification rows, wrong role/revision, duplicate/conflicting rows, changed hash/length/path, noninteger length, an extra row field, missing/duplicate/prefix-colliding reservations, input-prefix and cross-namespace conflicts, unselected qualification, Windows case collision, and malformed input/reservation lists. These are 20 cases inside **one method**, not 20 extra methods.

The same installed audit hook then observed a valid TypeScript control: **one actual launch, two controller write opens, symbol `answer`**. These are controller-side Python audit observations, not an OS-wide process monitor or authenticated identity proof.

| Affected requirement | Fresh evidence / verdict |
| --- | --- |
| R1 exact selected ownership, role/revision/ref identity and namespace/reservation rejection before request/child | VERIFIED: all 20 malformed-file cases; functioning real audit control. |
| Valid source tools at base and head | VERIFIED: six actual TypeScript/lizard/Vulture smoke executions at two actual Git revisions, one common toolset digest. |
| Fixed settings/imports/resources and preload rejection | VERIFIED within existing source-smoke scope: real poisoned Node/Python environment, resource tamper and unqualified-import checks pass. |
| Original/copy/controller binding | Affected source methods pass; unchanged pre/post freshness implementation and qualification inputs remain pinned. Broader ROOT04 historical cases were not rerun. |
| Native/empty-Q1 compatibility and path identity | Three methods cover this within the ten: the source class's native/empty method plus two root methods; the selected real hardlink case executed. |
| AC04/ordinary AC05 | Historical proof retained; CLI/adoption regressions were not rerun or newly approved here. |
| AC09 | Ten fresh affected methods only; no full regression/Q5 claim. |
| ROOT03 actual symlink | ENVIRONMENT-UNVERIFIED: retained `test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects`, WinError 1314; not retried, skipped or counted passing. |

The raw records contain **11 distinct command artifacts: 10 successful executions and one expected unqualified-import rejection**. These command executions are not additional test methods. `raw-reconciliation.json` identifies each command artifact and result. No additional independent tests were added: the mapped existing/new owner test covers the actual R1 criteria without duplicating it.

## Capture, runtime and preservation

FACT: Used the read owner `q2-binding-r1-verify.py` capture through an additive adapter. Its only in-memory capture changes permit the requested `joint-cli-binding-r1-*` directory prefix and enable unittest fail-fast. Original owner helper, production and test bodies were not edited. The exact replacements and executed capture-text hash are in `capture-adaptation.json`.

No passive/return profiler, mocked runner, fabricated progress, heartbeat timer, tool requalification, test retry or timeout increase was used. The worker recorded `profile_installed=false`; original real resource rehash and completed test/subtest output supplied progress. The full ten-method run used the preplanned **idle120/max1800** budget once.

FACT: **4,651 prospectively pinned files matched afterward**, covering all prior pins with the two authorized replacements, the eight previously supplemental runtime files, additional Python runtime candidates, owner/source/capture/review artifacts and this capture helper. All **123 observed controller module names** resolved to prospectively pinned files; no unpinned observed module file was found. See `before-pins.json`, `after-pins.json`, `added-pin-paths.json`, `loaded-module-paths.json`, and `freshness.json`. This is not complete loaded-DLL attestation, an OS sandbox, or retroactive before/after pinning of the earliest historical runs.

The preparation-only verifier error compared the Windows audit command-line string directly with an argv list. The error and full traceback are preserved in `preparation-error.json`; standard `subprocess.list2cmdline` reconciliation corrected that comparison before any tests started. The two already-written preparation artifacts were compared and preserved on resume. No production failure was observed.

FACT: Actual Git HEAD remained `ee6e0e34e78b70fcb672074af0a76f51fe937e1a`. Actual supervisor/runner/worker PIDs were `40112/50420/36920`; the bounded runner exited zero after **802.850294 seconds**. These are historical process identities, not permission to signal a subsequently reused PID.

Actual invocation from this worktree:

```powershell
$p='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;'+$env:PATH
& $p -B -u .ai\workflow-reliability\evidence\joint-cli-binding-r1-verify.py execute
```

The helper launched the literal bounded worker argv recorded in `command.json`: managed Python `-B scripts\run.py --idle 120 --max 1800 --` managed Python `-B -u joint-cli-binding-r1-verify.py worker`. That record includes the actual absolute paths, cwd, relevant environment and short-temp ownership; remaining environment was inherited without dumping potential credentials. `stdout-stderr.log` retains streamed combined bytes. Embedded producer command streams retain the existing runner's replacement-decoded/newline-normalized semantics.

FACT: New exclusive root `C:\Users\shbs\AppData\Local\Temp\jcbr1-67jov8bw` was empty after fixtures completed and removed **nonrecursively**. `cleanup.json` records this observation. No old temp root or PID was touched. The old seven-directory/whole-tree cleanup remains **UNKNOWN**; an empty new directory does not prove general descendant termination.

## Accounting and handoff

The ten fresh IDs overlap **nine** of the historical 262 passing IDs; the ownership regression is the one new ID. **Do not add ten to 262, claim 262 freshly passed, or replace the historical selected/custom 263-method inventory with an assumed new full-discovery total.** The retained native 13 entries (five Python replays plus eight reporter regressions) were not rerun.

Missing scalar/shared-JS collectors, raw metric reconciliation, all-nine metric completeness, coverage/mutation, successful guarded metric attachment, positive closure and recovery remain outside this verification and unapproved. The symlink finishing command remains in the immutable r2 report for an already-capable environment; no privilege change or retry was attempted.

The evidence directories are additive: `joint-cli-binding-r1-records` and `joint-cli-binding-r1-results`. The 29 entries in `raw-record-index.json` were rehashed successfully. Later raw reconciliation and this report are covered by the additive `joint-cli-binding-r1-seal.json`, without overwriting that index or either historical joint report.

| Evidence anchor | SHA-256 |
| --- | --- |
| `joint-cli-binding-r1-verify.py` | `004c1f868bd085a91583f9e74c6eb3e4da611400c2f90783f0bc65461a010d5e` |
| `joint-cli-binding-r1-results/result.json` | `e5cb410c319e01e4478d7c12ed0c145a8b6916b1f3738a11b599996ee5d3fbe3` |
| `joint-cli-binding-r1-records/reconciliation.json` | `7f3ce3114d2313016a75052adcf19ea3d058ab139174587574f6955c7af75bc7` |
| `joint-cli-binding-r1-records/raw-record-index.json` | `33a9c0b53135ed63ff60a1df8115260427e78af9d58fefa17f7441bcddebde04` |

**Next authority:** parent sends this focused evidence to the same reviewer for R1 re-review, then decides checkpoint acceptance. No agents, production/test-body/docs/shared-state/schema edits, installs, privilege changes, old cleanup, commits or pushes were performed by this verifier.

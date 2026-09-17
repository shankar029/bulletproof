# Q1 independent r3 replay — VERIFIED-WITH-LIMITATIONS

17 September 2026. Bounded original-verifier replay of the frozen F3 correction,
unchanged F1/F2 counterexamples and declared controls. **Functional verification
only; not the separate code-review role or complete quality/release acceptance.**

## Acceptance

**No remaining F1/F2/F3 correction blocker was reproduced in this replay.**

- **42 Q1 tests passed**, including six unchanged original verifier tests, both
  unchanged r2 verifier tests and the ten-mode native control test.
- **19 legacy probe tests passed.**
- Total: **61 tests passed**, zero failures/errors/skips/timeouts.
- No tests were added or edited in this round. Existing coverage addressed the
  bounded correction; see `q1-independent-r3-coverage-map.md`.
- All **322 owner-frozen inputs** match preflight and final recheck.
- **325 captured inputs** remained unchanged across both independent runs,
  with zero late imported files.
- **382 prior verifier source/evidence files** are byte-identical.

Only additive `evidence/q1-independent-r3-*` artifacts were written.
No production/original-test/shared-state/docs edits, installations, nested agents,
commits, publication, Q2 work, broad root probe or mutation work occurred.

## Findings and correction verdicts

| Finding | Verdict | Observed proof |
| --- | --- | --- |
| F1 — builtin import resolved to repository namesake | **VERIFIED** | Original native `sys` oracle and configured probe now agree. Actual probe reports cycles=0, architecture_rules=0, seven missing required metrics, incomplete/fail. Shadowable/relative controls remain passing. |
| F2 — fresh proof accepted hard-linked base/head sources | **VERIFIED-WITH-LIMITATIONS** | Original fresh-recollection test rejects with “Shared mutable file identity across Context roots”, while still proving the real alias/cross-write. Controller, non-code, hidden-source and artifact alias controls pass; equal-content independent copies pass. This is an identity observation, not an atomic lease or sandbox. |
| F3 — environment-selected frozen modes shared a parser/tool fingerprint | **VERIFIED** on managed CPython 3.14.2 | Original r2 native/probe test now observes correct different resolution **and different parser/receipt toolset identities** for effective on/off modes. Ten native controls additionally establish precedence, ignored environment and effective-state stability. |

The prior NOT-VERIFIED records and failing raw evidence are preserved as history.
This additive replay closes those functional counterexamples on the hashes below;
it does not relabel the previous runs as passing.

## Actual F3 mode observations

The unchanged r2 verifier launches separate native and configured-probe processes
against a real Git fixture containing `a.py: import __hello__` and a local
`__hello__.py`.

| Effective mode | Native origin / probe edge | Parser SHA-256 | Receipt toolset SHA-256 |
| --- | --- | --- | --- |
| Environment on | frozen / external `__hello__` | `fb3cfccde62e9ab7e3dfd6321a4297c507a8cce457fce9361793acc90cf085ec` | `328a7b2f2d9b149e51bd74e0c3a1810e38c46b0eaba60ae961f1027de1e9c12b` |
| Environment off | owned source / local `__hello__.py` | `5215c84478cf910fd213e5f12d9069879af797551ea2959c034316cf506e0b90` | `e412811d0d58598965d8b81c7f6b2043cb72b931b9bfd9cd5aa334582883c321` |

Both native commands exit **0**; both actual probe commands exit **1** because
required measurements are still missing. Per-run resolution remains correct;
the previously colliding identities are now distinguished.

The additional declared native test ran these **ten actual modes**, not ten
invented observations:

1. Default installed runtime
2. Environment on
3. Environment off
4. CLI off overriding environment on
5. CLI on overriding environment off
6. Repeated CLI settings, last off
7. Repeated CLI settings, last on
8. `-E` with environment off
9. `-E` with environment on
10. `-I` with environment off

Every child exits 0. The available runtime census contains **28 names when on**
and **3 bootstrap names when off**. For the second package namesake
`__phello__.spam`, actual native origin/local marker matches the table.
Equivalent effective modes have identical fingerprints; on/off tables and
fingerprints differ. Changing raw environment and `sys._xoptions` after startup
does not change the effective table or fingerprint.

The finalizer independently reconciles all ten captured observations, native
origin/table agreement, digest relations, mode inventory and post-start
consistency from **this run's stdout**, not the owner's result narrative.
The raw-setting assignments are deliberate controls; no frozen-table/import-hook
success was fabricated.

### Mode evidence

- `q1-independent-r3-q1.stdout.bin`: original test-worker stdout containing all
  ten actual child argv, environment deltas, exits, full tables and observations.
- `q1-independent-r3-final-freeze.json`, `actual_modes`: decoded observations
  and their independent reconciliation.
- `q1-independent-r3-fixtures-q1/q1-independent-effective-frozen-mode-observations-independent-r3-q1.json`:
  original r2 verifier's exact native/probe argv, environment deltas, resolution
  and parser/receipt fingerprints.
- That fixture directory also retains native/probe byte captures, command JSON,
  fixture ZIPs and exact file manifests.

The existing ten-mode test uses the repository's text-returning `run_capture`
internally. Its recorded observations and raw **worker** stdout are retained;
this is not a claim that each of those ten children's original stream bytes
were separately archived. The unchanged r2 public-probe/native fixture helper
does separately preserve its actual stdout/stderr bytes.

## Q1 / AC reconciliation

| Scope | Bounded verdict |
| --- | --- |
| CHECK-INVENTORY | VERIFIED-WITH-LIMITATIONS: positive complete inventories, explicit unsupported/error/exclusion paths, ignored/untracked normative source and physical isolation checks pass on the available host. |
| CHECK-GRAPH | VERIFIED-WITH-LIMITATIONS: declared Python literal-import model, actual native precedence/relative controls, canonical cycle identities and architecture rules pass. No JS parser or dynamic safety claim. |
| CHECK-PARTIAL-PROBE | VERIFIED-WITH-LIMITATIONS: exact nine requirements, actual complete greenfield baseline, unavailable/incomplete/fail and malformed/overlapping invocation behavior remain passing. |
| CHECK-RECONCILE | VERIFIED-WITH-LIMITATIONS: common source/config/approval/controller/run/artifact binding, raw recomputation and corrected effective-mode/physical-identity boundaries pass in scoped tests. |
| **Q1 functional verification** | **VERIFIED-WITH-LIMITATIONS**; no observed correction blocker. Separate independent review remains required before overall Q1 acceptance/advancement. |
| AC01 | VERIFIED-WITH-LIMITATIONS for scoped legacy probe/native regression preservation, not all later mixed mutation behavior. |
| AC02 | VERIFIED-WITH-LIMITATIONS for this Q1 producer/binding and missing-as-fail slice; absent required collectors are not waived. |
| AC09 | VERIFIED-WITH-LIMITATIONS for this independent functional/regression step and pinned freshness; separate review and final integrated quality proof remain due. |
| AC03, AC04, AC05, AC06, AC07, AC08, AC10 | NOT-VERIFIED by this correction-only role; unrelated parent/C1/docs work was not explored or reaccepted. |
| Q2–Q5 / complete quality / release | NOT-VERIFIED; not performed or advanced here. |

Mixed-language fixtures retain unsupported MJS/CJS receipts and all nine missing
measurements. The original Python-only probe fixture correctly measures graph
values while seven metrics remain unavailable. These functional passes are not
actual complete root quality or changed-line mutation proof.

## Exact commands and results

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

Observed HEAD:
`0b7e1a1f6fd1f807bd254886e2877d605596d96d`.
HEAD is Git context, **not** a claim that the uncommitted frozen Q1 files are
contained in that commit.

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r3-capture.py preflight
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r3-capture.py capture 'test_measure_*.py' q1
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r3-capture.py capture test_probe.py legacy
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-independent-r3-finalize.py
```

Both test captures ran once, concurrently against frozen relevant inputs.
No silent loop/retry occurred. Capture uses standard-library unittest discovery
in a child worker; literal worker argv/cwd/environment/exit are preserved in
`q1-independent-r3-q1-command.json` and `q1-independent-r3-legacy-command.json`.
This is not a claim to have literally run a different `python -m unittest` argv.

Only original test evidence destinations/tags were relocated to fresh
`q1-independent-r3-fixtures-q1/` and `independent-r3-q1`. Source/assertions are
unchanged. Existing paths refuse overwrite; any future replay needs new labels.

| Run | Tests | Actual unittest seconds | Capture seconds | Exit |
| --- | ---: | ---: | ---: | ---: |
| Q1 | 42 passed | 697.830 | 699.242 | 0 |
| Legacy probe | 19 passed | 57.468 | 58.852 | 0 |

Positive test inventories and all result records are retained. No failures,
errors, skips, timeout kills, input drift or late imports occurred.

## Source/runtime freeze and evidence preservation

`q1-independent-r3-final-freeze.json` preserves:

- Complete owner freeze: **322 expected/final input pairs**, unchanged.
- Both independent runs: **325 input hashes each**, equal before/after and at
  final recheck; **325 unique pins**, zero late imports.
- **382 preserved original verifier files**, unchanged.
- **28 raw streams** rechecked against their recorded SHA-256/byte counts.
- **9 fixture ZIPs / 275 member files**, each reconciled against its exact
  original source/archive mapping.
- Actual ten-mode argv/environment/observations and per-run command/results.

Pins include actual measurement/transitive repository modules and test inputs,
imported Python sources/native modules, existing bytecode caches, managed Python
EXE/DLLs and resolved Git/Node executables. `-B` prevents cache writes, not reads.
This is bounded input freshness, **not** OS-wide dependency closure or a
whole-repository stability claim. No C1 source was read/explored.

### Selected SHA-256 — before = final

| Input | SHA-256 |
| --- | --- |
| scripts/measure_graph.py | `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061` |
| scripts/measure.py | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| scripts/probe.py | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| scripts/tests/test_measure_graph.py | `22a1fc3d9506e0a200ce43991ea0b667d48a26b2b69a61d5a7937761ae1876df` |
| scripts/tests/test_measure_inventory.py | `d97a98983cb2c825abd87ffec4f96981c652dece88846abd3864179a2921d227` |
| Original verifier test | `f58d77f2cc957d7eae0bfaf4a3f99a63370fc1901a2b5312ce43b3a445bb19c6` |
| R2 verifier test | `4bb2639f64390d1af0ff1d223843d0f1036e6a75742587d86411f4d0d5db8d46` |

### Raw test streams

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| q1-independent-r3-q1.stdout.bin | 36054 | `72df59bef2c8db0245b1d6eef9ee541736a026f071fc9f070214a29ad4a7c3a8` |
| q1-independent-r3-q1.stderr.bin | 7395 | `270311574c729cf69d4ceb4741cb6ec17c0c3a351ff235202948e9b53f718b77` |
| q1-independent-r3-legacy.stdout.bin | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| q1-independent-r3-legacy.stderr.bin | 2911 | `ed9505179d8ad396b011335eb315224ce830403e10c1a42f0c8ad94cc54defb0` |

The new capture/finalizer scripts compile without bytecode and have no trailing
whitespace. The earlier malformed archive/census-harness attempts are retained
as history, not production failures or new passes.

## Limits and next owner

This qualification is on managed **CPython 3.14.2 / Windows**, using its private
effective frozen-name census. It does not establish all Python implementations,
all builds, custom import hooks, arbitrary module-cache edits or dynamic targets.
Malformed/unavailable runtime census behavior was not simulated to manufacture
proof on unsupported runtimes. Physical file identity checks do not prevent
later concurrent relinking and do not authenticate ownership.

**Next: separate read-only code review on this exact freeze.** No reviewer was
launched here. Parent owns subsequent Q1 acceptance, C1 dependency freshness,
Q2+ scheduling and eventual complete quality/release proof.

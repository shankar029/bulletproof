# Q1 final independent verification — VERIFIED-WITH-LIMITATIONS

17 September 2026. Replacement fresh-context verification of the frozen resumed
R1/R2 correction. **No residual production failure was reproduced within this
bounded objective.** Separate code re-review remains required.

## Fresh execution result

**74 distinct methods passed: 52 original Q1 + 3 new independent + 19 legacy
probe. Zero failures, errors, skips or timeouts.**

Unlike the owner's historical case reconciliation, these are **three clean,
completed batch invocations**, each run once. The two Q1 patterns are exhaustive
and disjoint. This is not a claim of one combined 74-test process.

| Batch | Actual tests | Unittest seconds | Capture seconds | Exit |
|---|---:|---:|---:|---:|
| `g`: graph/inventory | 25 | 849.397 | 852.749 | 0 |
| `i`: Q1 integration/review/boundaries | 30 | 982.983 | 984.685 | 0 |
| `p`: legacy probe | 19 | 61.175 | 63.123 | 0 |

The finalizer independently matched every fully qualified test ID in the raw
unittest stream to the pre-run inventory, checked successful result records and
terminal `Ran ... / OK` output, and rejected duplicate IDs. Internal subtests
and ten native mode controls are not additional methods. No owner/history count
was imported into this total.

FACT: `q1-final-verification-final-freeze.json` records the actual results,
commands, inventories, hashes, native observations and reconciliations.

## Finding and boundary verdicts

| Requirement | Bounded verdict and observed proof |
|---|---|
| **R1: path aliases hide real edges** | **VERIFIED on this Windows host.** The unchanged public counterexample reports canonical `scripts`: base 0 / head 1 cycle, comparison fail, exit 1 and seven missing metrics. `scripts.` and `scripts ` both exit **2**, with `Aliased relative path`; neither produces a measured alias report. Native canonical and **dot-only** imports confirm the mutual references. No native-space behavior is claimed. |
| R1: full input/root boundaries | **VERIFIED.** Existing tests reject dot/space/case aliases in file and ancestor components, malformed file paths and aliased absolute roots, while allowing directory `"."`. The base-case spelling regression rejects an existing uppercase base directory under a lowercase head config. New independent `test_new_source_directory_absent_at_base_is_not_an_alias` proves an actually absent new baseline directory is accepted and its head cycle is retained. |
| **R2: fresh status-clean corrupted baseline accepted** | **VERIFIED.** The unchanged original regression first validates genuine base 0 / head 1 / fail. It sets assume-unchanged, replaces base bytes, confirms status is empty and committed `value = 1` differs from actual `import b`, then regenerates inventories, syntax, observations, manifest and report. That fresh candidate contains base 1 / head 1 / ok, but the public validator **rejects with Baseline**, as asserted by the passing test. The candidate report is preserved, not presented as accepted. |
| R2: skip-worktree / altered index | **VERIFIED at the shared immutable-baseline boundary.** The unchanged owner control demonstrates empty status under skip-worktree yet direct baseline rejection; staged replacement also rejects. Restoring exact bytes is accepted even with the disagreeing index. These calls invoke the same independent comparison used by report validation; they do not depend on a stale receipt. The complete fresh-report reproduction is specifically the assume-unchanged case above. |
| R2: complete paths, bytes and types | **VERIFIED.** Hidden `.hidden/excluded.py`, analyzer-excluded `node_modules/input.txt`, non-code contracts and an extra file all participate. New independent missing-file and directory-replacement negatives fail, then exact restored bytes pass. Existing linked-source/junction tests and unsupported immutable symlink/submodule mode controls remain passing. No code-only scope or supplied-byte normalization is used. |
| R2: neutral/versioned EOL and mode projection | **VERIFIED-WITH-LIMITATIONS.** Real neutral and nested versioned LF/CRLF bytes match exactly. Replacing expected CRLF bytes with LF fails. Immutable `100755` is recorded with `regular-file-only-windows`; this is not proof that ordinary Windows worktree bits represent POSIX executable identity. POSIX execution was not performed. |
| R2: ambient authority | **VERIFIED on the exercised controls.** Real object replacement, caller info/attributes, local autocrlf, injected config values, worktree and index overrides do not alter expected original bytes. The caller index path remains absent; caller local config and info/attributes retain their contents. |
| R2: external filter rejection before execution | **VERIFIED.** The unchanged owner test uses a versioned attribute macro resolving to `filter=tripwire`. Both direct materialization and the CLI copy helper reject before the source checkout exists and while the sentinel is absent. Explicit ordinary checkout in the positive-control tree executes the same real driver and writes `EXECUTED`. These actual fixture trees/driver bytes are archived. |
| R2: shared CLI/validator policy | **VERIFIED.** Real configured CLI positives and supplied-Context validation pass through the common implementation. Changing reported immutable modes or policy Git SHA is rejected. The new independent genuine-launcher-copy control rejects a nonqualified executable tuple and restores the original binding afterward. |
| **F1: builtin/frozen precedence** | **VERIFIED.** Original native `sys`/configured-probe regression and shadowable/relative/nonpackage controls pass unchanged. Builtin/frozen names do not fabricate local namesake edges. Native-incomplete imports remain unavailable rather than complete zero. |
| **F2: physical aliases** | **VERIFIED-WITH-LIMITATIONS.** Original fresh hardlink and cross-write proof, differently named/code/non-code/controller/artifact/hidden alias negatives, and independent equal-content positive controls pass unchanged. Physical identity is an observation, not an atomic lease or sandbox. |
| **F3: effective frozen fingerprint** | **VERIFIED on managed CPython 3.14.2.** Original environment-on/off native/probe test observes different resolution and parser fingerprints. The ten-mode native test passes. The finalizer independently reconciles all ten actual stdout observations, on/off distinction, equivalent effective-mode identity and post-start raw-setting stability. Private CPython API/runtime portability is not universal support. |

### Source mechanism grounding

These are source observations, not claims of a separate code re-review:

- `scripts/measure_graph.py:44–83`: shared relative-name, canonical-root and
  component-alias boundaries. `:359–367`: source roots checked independently
  for the selected revision, allowing an absent newly introduced directory.
- `scripts/measure.py:32–64`: compiled policy and qualified core/DLL binding;
  `:98–169`: isolated no-checkout clone, immutable tree, cached Git attribute
  census, pre-checkout rejection, then checkout and complete path/mode checks.
- `scripts/measure.py:172–207`: complete non-Git file census and exact SHA-256/
  type/representable-mode comparison with independent materialization. Supplied
  bytes are not normalized or passed through clean filters to establish equality.
- `scripts/measure.py:397–405,521–585,587–589`: policy, source/controller binding,
  immutable baseline verification, raw reconstruction and five-file controller
  digest. `scripts/probe.py:463–481,485–505,507–583`: shared copy path, report
  materialization binding, real configured collection and validation.

The actual probe imports `mutate` beyond the copied five-file controller set.
Its source is independently pinned, but **copying/reading controller files is
not execution from a stable controller or Q4 self-mutation proof**.

## Check and acceptance-criterion reconciliation

| Scope | Verdict |
|---|---|
| **CHECK-INVENTORY** | **VERIFIED-WITH-LIMITATIONS** for Q1: exact inventory/receipt partitions, unsupported inputs, ignored/untracked normative source, actual read/walk failure and canonical/physical boundaries pass on this host. |
| **CHECK-GRAPH** | **VERIFIED-WITH-LIMITATIONS** for the declared Python literal-import model: native precedence, relative/conditional imports, cycle/architecture identity replacement and dynamic-site disclosure pass. JS graph semantics are not implemented/proven by this slice. |
| **CHECK-PARTIAL-PROBE** | **VERIFIED.** Python-only fixtures retain all nine requirements and fail incomplete with seven unavailable; mixed MJS/CJS fixtures expose unsupported inputs and nine missing measurements. No fabricated zero, optional required-set reduction or overall green is claimed. |
| **CHECK-RECONCILE** | **VERIFIED-WITH-LIMITATIONS** for Q1 producer/receipt/revision/graph/comparison/policy/controller/artifact validation, including the corrected baseline authority. Later scalar/coverage/mutation reconciliation remains outside this role. |
| **AC01** | **VERIFIED-WITH-LIMITATIONS** for bounded Q1/legacy native regression preservation, not future mixed-language mutation delivery. |
| **AC02** | **VERIFIED-WITH-LIMITATIONS** for this Q1 binding/measurement-completeness slice. Required missing metrics remain fail; complete actual-root quality is not established. |
| **AC09** | **VERIFIED-WITH-LIMITATIONS** for this independent functional replay, retained regressions and freshness. Separate code re-review and final integrated quality evidence remain due. |
| AC03, AC04, AC05, AC06, AC07, AC08, AC10 | **NOT-VERIFIED by this bounded role.** No reacceptance of parent/C1/docs work or claim that runtime-restart recovery is the planned AC05 experiment. |
| Overall Q1 acceptance / C1+Q1 preservation | **Pending separate code re-review and parent disposition.** No C1-only composition pass inferred. |
| Q2–Q5, actual-root quality, Q4 controller execution, release | **NOT-VERIFIED / not performed here.** |

## Exact execution and replay

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-capture.py preflight preflight-2
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-capture.py capture 'test_measure_[gi]*.py' g
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-capture.py capture 'test_measure_q1*.py' i
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-capture.py capture test_probe.py p
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-finalize.py environment
& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-final-verification-finalize.py finalize
```

The three test commands ran concurrently, in separate processes with independent
fixtures and short tags. **Do not rerun these exact labels into existing
destinations**: captures exclusive-create artifacts; any later replay must use
new short labels. Full literal worker argv and environment deltas are recorded
in each command JSON. No test retry/recovery was needed.

The initial preflight command (without `preflight-2`) exited 1 solely on the
permitted parent `state.md` edit. That failure and its bounded explicit
reconciliation remain in `q1-final-verification-execution-notes.md` and both
preflight JSONs; not all commands are retrospectively called green.

### Raw batch streams

| File suffix (prefix `q1-final-verification-`) | Bytes | SHA-256 |
|---|---:|---|
| `g.stdout.bin` | 36054 | `c4ed64c6e3a748baea76f28d1a54ba59fd66f678b244b5a48ed8f6dd9074432a` |
| `g.stderr.bin` | 62169 | `69ba6d25fc930eb94cbdd4ddb19d2b66dbf577974653067b835f726235eea7e3` |
| `i.stdout.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `i.stderr.bin` | 54087 | `42753f12a61ea02bb525f09aa6c7a313baf694b0ab4d992abb5507be4d6d381b` |
| `p.stdout.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `p.stderr.bin` | 4229 | `f96008111df5f2d293c684aef36a6ea65d25b1d2697cdd0290306ac6c3fe0668` |

## Freshness, fixture preservation and portability

FACT: final reconciliation found:

- **534 source/runtime/artifact pins unchanged**, including actual measurement,
  graph, probe, mutate, evidence, runner, tests, observed Python source/native
  modules/caches, managed runtime binaries and the qualified Git package.
- **1,554 preexisting evidence files unchanged**; original failures, owner
  fixture archives and all prior independent evidence remain intact.
- Zero late imported files in all three batches.
- **528 new owned-tree archives**, with every archived member checked against
  its captured byte length/SHA-256; **11 additional original-verifier fixture
  archives** separately reconciled. Empty Git environment temp archives are
  included in that first total; it is not a count of distinct test fixtures.
- **40 recorded raw streams** reconciled against their recorded lengths/hashes.
- **820 recorded owned temporary paths absent** at finalization. No unknown
  prior-run leftovers were removed or claimed cleaned.
- Scoped compilation and bounded `git diff --check` passed. HEAD remained
  `0b7e1a1f6fd1f807bd254886e2877d605596d96d`, branch remained
  `shbs-microsoft-workflow-app-verification`, index remained empty.

The status-file exception is exact and disclosed; it is not a waiver for
production, contracts, tests, runtime or preserved-evidence drift.

### Frozen production

| File | SHA-256 |
|---|---|
| `scripts/measure.py` | `753fca9e03c7961dab474fcc3536a53c1b48b55dd0382c9cf3cd4ec248e2d859` |
| `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts/probe.py` | `668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083` |

Actual direct-core `git --no-pager version --build-options` observed
**Git 2.53.0.windows.4, aarch64**, built from
`3a9e66c3d66bb6509be99fe21c3205f024c04568`. The compiled qualification matches
the actual core SHA plus the **69 bundled DLL** census before/after:
core SHA `a612b966632d6d5c31829f45c62e7a161f428c79d8c2d15c56d7a005820dadb0`,
DLL-map digest `22a15e7333438dac6993ec3af1a4ee99a48f4555aa7acd0734f23bc77f92d7eb`.
The launcher alone is not the authority. Historical qualification command
streams were rehashed, not relabeled as newly executed qualification commands.
The behavioral materializer/sentinel/EOL controls **were freshly executed**.

**Limited portability:** this proves the observed Windows/managed CPython 3.14.2/
qualified Git package combination. Other Git builds fail closed pending
qualification. It does not establish general Windows Git layouts, POSIX
execution, every Python implementation, OS-loader closure, custom import-hook
semantics or authenticated/atomic ownership.

## Handoff

**Bounded functional acceptance: VERIFIED-WITH-LIMITATIONS.** Original R1/R2
counterexamples are rejected; original F1/F2/F3 and native-incomplete regressions
remain passing. The prior NOT-VERIFIED/REVISE records stay historical.

Only the allowed new regression file and additive
`q1-final-verification-*` evidence were written. No production/original-test/
shared-state/docs edits, dependency installs, nested agents, commits, publication,
C2/Q2 work or whole-task completion occurred.

Parent owns separate code re-review, C1 dependency reconciliation and combined
preservation disposition. No advancement or complete quality waiver is issued
by this verification role.

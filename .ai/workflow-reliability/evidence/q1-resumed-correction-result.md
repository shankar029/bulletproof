# Q1 R1/R2 resumed correction — frozen local return

**Status: local case coverage complete with capture limitations; awaiting parent
independent replay and separate correction review. Not overall Q1/release acceptance.**

This continues correction round 3. No new research/design round, agents, C1/core/
guard changes, shared-state edits, installations, commits or publication occurred.
Preserve accepted C1 and Q1 together only after the parent's remaining acceptance
checks; this return does not authorize C2/Q2 or a C1-only preservation.

## Root causes and corrections

| Finding | Final implementation and local proof |
| --- | --- |
| **R1: aliases hide local graph edges** | `measure_graph.py:44–83` rejects noncanonical file/directory spellings and existing component aliases. `.` remains directory-only. `_parse:359` checks roots independently at **both** revisions, while allowing an absent newly introduced directory. The original public CLI counterexample passes: canonical roots retain the real cycle, both dot/space configuration aliases reject. Actual native import proof remains **dot-only**, not an invented native-space claim. Owned tests add file/component/case aliases and a differently cased base-root control. |
| **R2: clean status is not immutable source** | `measure.materialize_baseline:98` uses the approved isolated versioned-attribute policy; `validate_baseline:196` independently rematerializes rather than trusting supplied status/index state. `_baseline_files:172` compares exact byte hashes, complete file path sets, regular-file types and representable modes, including non-code, hidden and analyzer-excluded inputs. Fresh assume-unchanged corruption now rejects. Skip-worktree, altered-index, extra-file and excluded-input controls pass. Supplied bytes are never normalized or clean-filtered to establish equality. |
| **Policy and executable binding** | `baseline_binding:48` binds the actually qualified Git core and 69 bundled DLLs, not merely the small launcher. Unknown builds fail explicitly. `config_policy:397` includes this binding; existing controller validation binds the implementing modules. `baseline_tree:86` records immutable modes separately under the existing report `tools` map; the public validator rederives them. No new module, Context field or Inventory schema field. |
| **CLI/common-validator agreement** | `probe._copy_subject:463` and `measure.validate_observations:521` use the same materializer. Fresh no-checkout clone, empty template, neutral environment, no replacements and cached Git attribute interpretation precede checkout-index. External filters/macros, unqualified transforms, symlinks and submodule modes reject before capable execution. The real sentinel stays absent on rejection and executes in the explicit positive control. |

Original F1 builtin/frozen precedence, F2 physical independence, F3 effective
frozen-mode binding and the all-nine/incomplete policy remain covered. No scalar,
coverage or mixed-language mutation adapter was added. Seven missing adapters
still make the Python-only configured examples incomplete/fail.

## Actual executions — no hidden failed runs

All test commands used managed Python 3.14.2 with `-B`,
`PYTHONDONTWRITEBYTECODE=1`, and `scripts/run.py --idle 120 --max 1200`.
Counts below are unittest methods, not counts of internal native-mode controls.

| Capture suffix | Actual outcome | Unittest seconds |
| --- | --- | ---: |
| `targeted-final` | 8 new owned controls passed | 169.008 |
| `path-diagnostic-final` | Original collision diagnostic test passed | 3.937 |
| `probe-core-final` | **19 legacy probe tests passed** | 59.952 |
| `q1-recovery-graph-inventory` | **25 Q1 tests passed**, no failures/errors/skips | 792.877 |
| `q1-recovery-integration` | **25 passed / 2 capture errors**, no assertion failures or skips | 854.211 |
| `r1` | Previously errored original alias method passed with short capture tag | 31.381 |
| `f3` | Previously errored original frozen-mode method passed with short capture tag | 55.705 |

**Reconciliation:** all **52 distinct Q1 methods** have a passing execution on
the same frozen production bytes, plus **19 legacy probe methods**. The 8
targeted methods and diagnostic repeat are **not added again**. This is **not a
claim of one all-green aggregate invocation**.

The integration batch's two errors were file writes at **260 and 263 characters**
in the unchanged verifier's evidence helper. The directories existed. The owned
real filesystem probe (`q1-resumed-correction-path-limit.json`) created/read a
259-character path and observed FileNotFoundError at 260 and 261. Short-tag
replays changed no source/test behavior and passed both methods; the failed batch
and its raw streams remain intact.

Earlier, the first aggregate run exited **124** during repeated validations,
after 32 `ok` records and a collision-diagnostic failure, without a completed
unittest result. The collision-check ordering was corrected without changing the
original test. Recovery exposed actual subprocess audit events as progress and
split the exhaustive Q1 file set into two disjoint batches. No timer heartbeat,
skips, fake results or aggregate timeout retry loop was used.
`q1-resumed-correction-recovery.md` preserves the exact timeout marker and the
old wrapper's failure to flush final raw streams before its process-tree kill.
The initial targeted positive-sentinel test-control error is also retained.

## Qualification, preservation and freeze

- Initial production hashes exactly matched the previous reviewed pre-fix
  freeze; no partial production edits were found.
- Both predecessor qualification and the additive **19-command direct-core
  qualification** passed raw size/hash reconciliation. The latter pinned 70
  application files before/after unchanged. It preserves real neutral LF,
  versioned text/EOL, macro, mode and sentinel controls.
- Final freeze contains **530 input/artifact pins**. All corresponding final
  execution before/after pins matched, including actual measurement/probe/mutate
  inputs and qualified Git package files.
- **1,308 protected preexisting files** matched their initial byte hashes,
  including original independent tests/reports and prior qualification/failures.
- All **877 recorded temporary paths** from completed final captures were gone
  at finalization. The interrupted old wrapper did not record its fixture paths;
  unknown leftovers are neither claimed cleaned nor removed by wildcard.
- Scoped Python compilation and `git diff --check` succeeded. Root HEAD stayed
  `0b7e1a1f6fd1f807bd254886e2877d605596d96d`; branch remained
  `shbs-microsoft-workflow-app-verification`. Index is empty.

| Frozen source | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `753fca9e03c7961dab474fcc3536a53c1b48b55dd0382c9cf3cd4ec248e2d859` |
| `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts/probe.py` | `668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083` |
| New owned `scripts/tests/test_measure_q1_resumed.py` | `cac4c629cd9387d4c19734ad2696154a98c7edfef6bd5e11305dfd940b14c105` |

Full source/runtime/artifact hashes, literal argv, raw-stream references and
per-run outcomes: **`q1-resumed-correction-final-freeze.json`** and the matching
`*-command.json`, `*-result.json`, `*.stdout.bin`, `*.stderr.bin` files.

## Limits and next owner action

1. Independent verification and separate re-review remain the parent's work.
   Use **short, new capture tags** to avoid this host's path limit:

   ```powershell
   $py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
   $env:PYTHONDONTWRITEBYTECODE = '1'
   & $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-resumed-correction-capture.py capture 'test_measure_[gi]*.py' pv-g
   & $py -B scripts/run.py --idle 120 --max 1200 -- $py -B .ai/workflow-reliability/evidence/q1-resumed-correction-capture.py capture 'test_measure_q1*.py' pv-i
   ```

2. This run qualifies the observed Git 2.53.0.windows.4 core/DLL set only.
   Other builds require qualification. POSIX mode comparison is implemented but
   **POSIX execution is unverified**. Windows ordinary worktree bits do not prove
   Git executable identity or Q4 execution.
3. Five copied controller files are **not** the full actual probe execution
   closure. `mutate.py` and observed runtime inputs are separately pinned; no
   stable-controller/self-mutation proof or OS-loader closure is claimed.
4. Filesystem observations are not atomic leases, authenticated producers or a
   sandbox. Required root quality, coverage and mutation measurements were not
   collected in this bounded correction. No thresholds or guard rules changed.
5. Gates 1–3 are inherited from persisted approval. Local implementation/case
   checks are complete with the capture limitations above. Fresh independent
   verification/review and overall quality/ship gates remain open.

**Production source is frozen for handoff. No further correction, preservation
commit, Q2 advance or publication is undertaken by this owner.**

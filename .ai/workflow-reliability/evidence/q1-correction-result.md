# Q1 correction round 1 — frozen owner handoff

**Status: owner correction tested; original-verifier replay and separate review
still required. No Q1 independent acceptance, Q2 advance, quality or release
acceptance is claimed.**

## Disposition of the accepted findings

### F1 — interpreter-owned imports

**FACT:** the unchanged verifier suite was rerun before edits. F1 and F2 both
failed again; four other tests passed. Original output is preserved in
`q1-correction-red-r1.stderr.bin` with exact command and input pins beside it.

`measure_graph._resolve` now queries the installed standard builtin/frozen
finders before repository candidates for **absolute** imports. It does not
special-case `sys` or treat every stdlib name as unshadowable. It does not
execute project modules or consult custom import hooks.

- Native CPython and actual producer graph agree for builtin `sys` and `time`.
- Runtime-frozen imports stay external; frozen-module aliases such as `os.path`
  retain opaque external semantics rather than becoming invented local edges.
- Ordinary shadowable source modules, demonstrated by a local `fractions.py`,
  still resolve to the repository.
- Explicit relative `from . import sys` still resolves to `pkg/sys.py`.
- A dotted child of a nonpackage **builtin**, demonstrated by `time.child`,
  is unresolved rather than resolved to a coincidental local directory.
- Parser semantics are `python-literal-import-v2`; the digest also binds the
  runtime builtin table and interpreter import options. Both revisions use the
  same current parser. Old observations are not imported as new proof.

Self-review found an over-restriction in the first correction: treating all
runtime nonpackages alike falsely rejected the real `os.path` alias. A real
native/producer assertion reproduced it (one failure, 14.028 seconds) in
`q1-correction-frozen-alias-red-r1.*`. It was corrected before the final runs.
This refines the pre-code note: the nonpackage-child rejection applies to
builtins, not opaque frozen dependencies. It is not a special local-file
allowlist or a claim to model arbitrary runtime module-cache edits.

**Limit:** custom meta-path/path hooks, arbitrary `sys.modules` replacement and
dynamic target resolution remain outside the declared static model. External
terminal classification does not prove that every external attribute/module
will execute successfully.

### F2 — physical source independence

`measure._validate_root_independence` supplements canonical lexical separation
with actual regular-file identities `(st_dev, st_ino)`, the installed
`os.path.samestat` semantics. It checks before consuming proof and after
recomputation. The scan includes non-code contracts and owned run artifacts;
only top-level source/controller Git metadata is outside its source scan.
Cross-root identity aliases, unknown identities, links and traversal/stat
failures cannot establish independent source inputs.

Real tests cover:

- Fresh base/head recollection after hard-linking different filenames.
- Fresh aliases through non-code approval/contract inputs.
- Base/controller and head/controller aliases with byte-identical controller
  source, so content freshness alone cannot distinguish the inputs.
- Run artifacts hard-linked to a head input.
- Positive independent equal-content copies: validation succeeds, and a real
  head write leaves base and controller bytes unchanged.
- The verifier's original fresh base/head hard-link test, unchanged.

**No CLI-copying defect is claimed.** The original ordinary CLI clone/copy path
was not observed creating these aliases and was not changed. The fix is at the
supplied-Context common binding boundary. Identity checks are observations, not
an atomic filesystem lease, prevention of later relinking, authenticated
ownership or an arbitrary-process sandbox.

## Exact captured runs

All commands used the current repository root:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'

& $py -B scripts/run.py --idle 30 --max 90 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py pin unused preserved-before
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture test_measure_q1_verification.py red-r1
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture 'test_measure_*.py' q1-green-r1
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture test_probe.py legacy-green-r1
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture 'test_measure_graph.py::runtime_precedence' frozen-alias-red-r1
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture 'test_measure_*.py' q1-final-r1
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-correction-capture.py capture test_probe.py legacy-final-r1
& $py -B scripts/run.py --idle 30 --max 90 -- $py -B .ai/workflow-reliability/evidence/q1-correction-finalize.py q1-final-r1 legacy-final-r1
```

The harness runs standard-library unittest discovery in a child worker, with
original stdout/stderr captured as **bytes** before outer text forwarding.
`::runtime_precedence` explicitly selects that one named test. The literal
worker argv/cwd/environment/exit code and original stream hashes are recorded
in each `q1-correction-<label>-command.json`; these are not claims that a
different `python -m unittest` argv was executed.

The original verifier tests were not modified. They create additional fixture
archives with fresh `owner-correction-<label>` tags. These are owner-run outputs,
not fresh-context verifier approval. Their unchanged helper contains a historic
1,200-second outer-bound description; the actual correction outer bound is
**900 seconds**, recorded by the correction command records above.

| Run label | Actual tests | Actual unittest duration | Exit |
| --- | --- | ---: | ---: |
| `red-r1` | 4 passed / F1 and F2 failed | 95.050s | 1 |
| `q1-green-r1` (superseded) | 39 passed | 652.804s | 0 |
| `legacy-green-r1` (superseded) | 19 passed | 58.641s | 0 |
| `frozen-alias-red-r1` | 1 failed | 14.028s | 1 |
| **`q1-final-r1`** | **39 passed, including all six unchanged verifier tests** | **656.093s** | **0** |
| **`legacy-final-r1`** | **19 passed** | **58.880s** | **0** |

No final-run errors, skips, timeout kills or source edits during execution.
Both final commands also passed their dependency before/after comparison.
The finalizer exited 0 and independently rechecked all recorded raw correction
streams against their hashes. Intermediate runs are historical, not added to
the final passing count.

Final raw stderr:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `q1-correction-q1-final-r1.stderr.bin` | 6829 | `3faf11a5dc4ceaed51f7282067630c3460b2ec4d89f92b8adf1d70c83f2c2676` |
| `q1-correction-legacy-final-r1.stderr.bin` | 2911 | `452df4dc21f2abb6afa7df2ade961f5ddf0dc3d6d390529f14e55b8b85ef9cdf` |

Both final stdout captures are genuinely empty files, not missing logs.

## Runtime and original-evidence pins

`q1-correction-final-freeze.json` records:

- **233** Q1 final-run pinned files unchanged.
- **308** legacy final-run pinned files unchanged.
- **321** unique final inputs, rechecked unchanged after both runs.
- **Zero late imported files** in either final run.
- **137** pinned original verifier files/tests rechecked byte-for-byte unchanged.

Pins include the actual measurement/probe transitive repository modules, native
reporter, tests/helpers, accepted config/design inputs, imported Python module
files, existing bytecode caches, managed Python EXE/DLLs and resolved Git/Node
executables. `-B` prevents cache writes, not cache reads; existing caches are
therefore pinned as well. This is not an OS-wide dependency closure or a claim
that unrelated C1/parent files were frozen.

The original `q1-independent-verification.md` and
`scripts/tests/test_measure_q1_verification.py` were not edited. The latter still
hashes to `f58d77f2cc957d7eae0bfaf4a3f99a63370fc1901a2b5312ce43b3a445bb19c6`.
The old implementation result, pre-code checkpoint and verifier findings remain
historical records; this correction is additive.

## Final source freeze notification

Only two production files and two owned test files changed in this round.
`probe.py`, native mutation/reporter/evidence/run modules and C1 production/state
were not changed by this correction. The current policy API used by C1 is
unchanged; source fingerprints must nevertheless bind the new files below.

| File | Final SHA-256 |
| --- | --- |
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/measure_graph.py` | `f40c8c1c05b62bc76bd027790b7111faf5394290c7309e5e32ebfe02de4dacf6` |
| `scripts/probe.py` (unchanged) | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/tests/test_measure_inventory.py` | `d97a98983cb2c825abd87ffec4f96981c652dece88846abd3864179a2921d227` |
| `scripts/tests/test_measure_graph.py` | `c51816fce7f34945765c98bb904f13abcc4119450b168f3d0f47fe476487bee8` |

Those files compile without bytecode output and have no trailing whitespace.
No installation, nested agent, broad root quality/mutation measurement, commit,
publication or Q2 work was performed. All nine metrics remain required and
missing/unsupported measurements still fail closed.

**Next owner:** original verifier replay on this freeze, then separate review.
This owner-run result does not supersede the verifier's NOT-VERIFIED disposition
with an independent acceptance claim.

## Parent coordination checkpoint — 17 September 2026, 09:12 +05:30

Parent reported the separately approved live-bundle/portable-README preservation
commit. A read-only bounded check independently observed:

- Current repository **HEAD is `0b7e1a1f6fd1f807bd254886e2877d605596d96d`**.
  Earlier HEAD observations are historical, not the current checkout identity.
- `git diff --cached --name-only` returned empty output, exit 0: index empty.
- All **321** inputs in `q1-correction-final-freeze.json` still match their
  recorded SHA-256 values. Q1 production and its tested runtime inputs remain
  frozen; this was a hash recheck, not a new test run or root-quality measurement.
- Parent reports `evidence/c1-code-review.md` is persisted and C1 still requires
  correction. This worker did not inspect or modify C1.

The check used the managed interpreter with `-B` through
`scripts/run.py --idle 30 --max 90`; inner Git reads used `run_capture` with
the same 30/90 bounds. It ran `git rev-parse HEAD`, the index query above, and
SHA-256 comparison of every pinned file; exit 0, `changed_inputs=[]`.
No staging, commit, publication or overall acceptance was performed here.

# C2b-S independent verification — BLOCKED

## Verdict and stop

**BLOCKED: full affected regression proof is missing.** The distinct
progress-visible route worked, but this verifier chose a worktree-nested
private temporary directory that produced overly long receipt staging paths.
The workflow suite completed exit1, not a timeout. No production fix, capturer
correction, test retry, new agent, install, commit, push or publication followed.
No old failure record was overwritten or first-capture log reconstructed.

FACT: accepted HEAD remains `d971634219a633cc4401fb7dcba9685e672978aa`.
FACT: all 29 bounded pins match before/after both runs and at final reconciliation.
FACT: all 98 exception records are `FileNotFoundError` at receipt `.stage`
creation; their decoded paths are 265 characters (88 records) or 266 (10).
INFERENCE: the verifier-owned deeply nested TEMP layout hit Windows path-length
limits. This was not reproduced in a second experiment, so no OS configuration
or definitive platform-wide limit claim follows. The error is not evidence of
an adoption assertion defect, but it invalidates the full regression gate.

The short transport validation exercised evidence10 successfully but did not
exercise the deeper workflow receipt staging layout. That preflight gap and
the path choice belong to this verifier, not to the production seam owner.

## Exact observed counts

Two disjoint unittest invocations, not a green aggregate:

| Batch | Methods attempted | Positive methods | Methods with errors | Error records | Exit | unittest time |
|---|---:|---:|---:|---:|---:|---:|
| `c2b-state-independent-transport01` (`test_evidence.py`) | 10 | 10 | 0 | 0 | 0 | 5.501s |
| `c2b-state-independent-workflow01` (`test_workflow*.py`) | 100 | 42 | 58 | 98 | 1 | 79.834s |
| Distinct total | 110 | 52 | 58 | 98 | **not passing** | separate processes |

Workflow inventory is the prior 83 + owner16 + independent1 = 100, derived
from actual discovery and reconciled to the actual verbose log. No assumption
that `100 - 98` means two passes: 98 includes subtest errors. Positive `ok`
IDs and unique errored IDs reconcile exactly with all 100 inventory entries.
There are zero assertion-failure records, skips, capture overflows or new
timeouts. No failing method is included in the positive count.

| Workflow module | Positive / attempted |
|---|---:|
| Owner adoption binding | 16 / 16 |
| Independent adoption verification | 1 / 1 |
| Existing state | 17 / 23 |
| Existing core verification | 3 / 11 |
| Existing chronology | 0 / 1 |
| Existing gate | 5 / 48 |

The owner's historical 61 successful methods and two timeout attempts remain
separate historical evidence. None is added to these fresh counts.

## What was proven, and what remains unproven

| C2b-S criterion | Fresh result and proof |
|---|---|
| Shared explicit/live validation and unchanged target materialization | VERIFIED within seam scope: owner16 pass; all action/check/increment/ship target parity, malformed explicit values, lone keywords and normal read failures exercised. |
| Prospective basis is not ordinary authority | VERIFIED: absent/malformed live authority still fails normal load/bind. Explicit paired validation succeeds only for the validated triple and changes no authority bytes. |
| Genuine retained old basis across A1/A2, unresolved executable admission | VERIFIED within protocol scope: new independent method passes both disk layouts, reads exclusively retained real old workflow/design files, derives exact old prefix from actual persisted ledger, leaves ledger/files byte-identical, and obtains `RECOVERY_UNVERIFIED`, blocked, no next command. |
| Source/artifact/history/review/context/authorization/candidate checks | VERIFIED bounded negatives: owner16 all pass, including real tampering/missing bytes, recomputed inconsistent source hash, history retention and authorization. No authenticated actor/recovery claim. |
| Model/producer schema and other original predicates retained | VERIFIED structurally: independent AST comparison against actual HEAD proves all 75 other original definitions unchanged, along with complete extracted policy body and materialization tail. Not a new claim that every model schema negative executed. |
| No schema/new graph/pure-gate policy bypass | Structural boundary VERIFIED: pinned gate/evidence/runner plus unchanged original definitions. Full behavioral regression **BLOCKED**: the two existing broad pure-gate tests errored while constructing receipt fixtures, before their no-I/O assertions. The passing explicit unresolved cases do not replace those tests. |
| Full affected workflow + evidence regression | **BLOCKED**: evidence10 pass, workflow100 has 58 errored methods. Gate/chronology/receipt-dependent proof cannot be accepted. |
| Ordinary CLI/recover/version migration | NOT IMPLEMENTED / out of this slice. `scripts/workflow.py` absent. Explicit binding is prospective adoption validation, never dispatch authority or publication implementation. |

The one new test is
`scripts/tests/test_workflow_adoption_verification.py:
RetainedAdoptionVerificationTests.test_retained_old_basis_blocks_unresolved_run_in_both_partial_publications`.
Existing owner tests separately covered partial publication and unresolved
admission; this adds their combination with actual retained old input files,
not another copy of those 16 cases. All review/adopter/admission identities
are explicitly synthetic protocol inputs. The files/hashes/persistence and
state/gate calls are real; this is not actual actor approval, actual child
lifetime/recovery proof or production adoption retry execution.

## Commands and progress transport

Both test invocations used exactly:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-stream.py transport01 test_evidence.py
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-stream.py workflow01 'test_workflow*.py'
```

These are historical exact commands, not permission to rerun. Tags refuse
overwrite. PowerShell used `initial_wait=600` and returned actual exit codes.

The capturer launched the actual CLI runner, not `run_capture`:

```text
<managed-python> -u -B scripts/run.py --idle 120 --max 600 --
<managed-python> -u -B -m unittest discover -s scripts/tests -p <pattern> -v
```

Exact argv/cwd/PATH/temp environment/PIDs are in each `launch.json`.
The capturer forwards real bytes immediately, flushing the log and stdout on
each read. It has a 4 MiB total output cap. Logs retain raw **merged CLI**
output; the actual CLI already merges child stdout/stderr and performs UTF-8
replacement and line-oriented forwarding. This is not separately retained
binary-transparent child stdout/stderr. No heartbeat or timeout increase.

| Batch | Actual forwarded bytes/chunks | First chunk | First before exit? | Direct CLI runner PID |
|---|---|---|---|---:|
| transport01 | 1524 / 14 | 0.501s | yes | 48856 |
| workflow01 | 228399 / 463 | 3.170s | yes | 40976 |

Elapsed capturer times are 6.242s and 80.876s respectively. Both actual direct
runner exits were reaped; both private `owned-temp` directories were observed
empty. No cleanup kill was needed in these new runs, and no claim of exhaustive
descendant termination is made.

Read-only final reconciliation (no tests) ran:

```powershell
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-reconcile.py
```

It exited0, obtained actual Git HEAD/source through bounded Git commands,
compared original AST bodies, and reconciled inventories/logs/pins.

## Hashes and evidence

| File | SHA-256 |
|---|---|
| `scripts/workflow_state.py` | `fe30290e61d319c76546c31acd454bc7c642fc83ad55126e368fa44ab4b57a6e` |
| `scripts/tests/test_workflow_adoption_binding.py` | `318707e82f94864fde02c434ca54e87f9338b8c66beace679be271655343f1b5` |
| `scripts/tests/test_workflow_adoption_verification.py` | `9c78b24fcd90b757aac55c6425f3738741b4eefe175e5cd710b02e72b5616b53` |
| `c2b-state-independent-stream.py` | `bf17cc5f43b454316271cc16d6473309b2e18e3f65ddf211e65a8fd30ba45700` |
| r2 normative contract | `80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d` |

Full 29-input pins and capture artifact hashes are in
`c2b-state-independent-reconciliation.json`; each batch retains
`inventory.json`, `launch.json`, `combined.log`, `result.json`,
`pins-before.json`, `pins-after.json`. The reconciliation's state-document
artifact hash is the then-current pre-report checkpoint, not the final amended
checkpoint. Its runtime-import list describes reconciliation imports only,
not a complete transitive dynamic-import attestation of the test subprocess.
All eight repository script modules and affected tests/helpers were pinned.
Runtime executable pins cover actual managed Python and Git entry executables,
not every stdlib/DLL/environment setting or the historical machine.
Parent shared state/report/docs/Q2 evidence lie outside bounded source pins.
The reconciliation JSON hashes to
`415880ede79316c95e923a8d272b428e9c2266d34c357cfd89ce4501b6ab1256`.
Both original timeout JSON records were separately rechecked against the owner
freeze and still match (`gate02`: `ca7fb077ccc38f572344ff2b2b73e9948b2bd1c81bc6de83f8bbcbcc87b6db3c`;
`workflow01`: `7ab2867f9eac4faf11379e4d21622ee12e03d75a9004442cd53b3948a1b8577f`).

## Remaining limits / parent handoff

1. **Do not accept/preserve C2b-S on this result.** The full regression remains
   blocked; separate code review follows only on an adequately verified basis.
2. Recommended next authorization: one capture-only correction to use a short
   exclusively owned OS-temp root outside the deep worktree, validate its
   actual receipt-stage path first, then run the parent-selected outstanding
   scope under the same progress-visible 120/600 bounds and fresh tags.
   Do not rerun this capturer unchanged: it overrides TEMP with the deep path.
   No correction or further suite invocation has been made here.
3. Historical cleanup remains UNKNOWN: first timeout has no child identity;
   owner observed old PID43520 absent later, which does not prove whole-tree
   death. No foreign PID killed, unknown temp directory deleted or earlier
   logs reconstructed. The clean new private roots do not resolve old cleanup.
4. Original CLI, ordinary publication failure table, recover/migration, actual
   quality Q2–Q5, actor qualification, human approval and release are unproven
   or outside this assignment. No broad quality tools were run.

Gate status: earlier design gates resumed from approved r2; current independent
verification **BLOCKED**; review/preservation/CLI gates not advanced.

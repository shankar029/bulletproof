# C2b-S independent r2 verification — VERIFIED

## Verdict and scope

**VERIFIED for the approved C2b-S adoption state seams only.** The authorized
capture-layout correction and one full replay close the missing affected
workflow regression proof. Separate parent code review is next; this is not
permission to preserve, dispatch work, implement the CLI, recover a process,
close actual quality obligations or release.

FACT: actual HEAD is still `d971634219a633cc4401fb7dcba9685e672978aa`.
FACT: all **49/49** bounded pins match before/after both r2 executions and at
final reconciliation. These include all original29 pins, the original
report/reconciliation/helper/checkpoint and saved successful/failed batch files,
both historical timeout JSON records, and the two new executable r2 capture
helpers. No production or test file changed during r2.

The original report remains a truthful **BLOCKED** report for its failed run;
it was not edited to become green. Its reconciliation/capturer/failed directory
remain byte-identical. This additive report supplies later successful proof.

## Actual counts, reconciled without duplicates

| Accepted evidence | Methods | Positive | Errors/failures/skips/timeouts | Exit | unittest time |
|---|---:|---:|---|---:|---:|
| New `c2b-state-independent-r2-workflow01` | 100 | 100 | 0 / 0 / 0 / 0 | 0 | 263.471s |
| Retained `c2b-state-independent-transport01` evidence suite | 10 | 10 | 0 / 0 / 0 / 0 | 0 | 5.501s |
| Distinct accepted methods across these two disjoint batches | **110** | **110** | none | both 0 | not one aggregate process |

Workflow100 = prior83 + owner16 + independent1, verified from actual discovery
and matching verbose method results:

| Module | Positive methods |
|---|---:|
| `test_workflow_adoption_binding` | 16 |
| `test_workflow_adoption_verification` | 1 |
| `test_workflow_state` | 23 |
| `test_workflow_core_verification` | 11 |
| `test_workflow_core_verification_r2` | 1 |
| `test_workflow_gate` | 48 |

The prefix-scale method emits real scale output before its final standalone
`ok`; reconciliation accounts for that record rather than incorrectly counting
only same-line `... ok`. Every method ID reconciles exactly to inventory.

The receipt-stage preflight is a successful real invocation, **not another
unittest method**. The prior failed workflow100 (42 positive, 58 errored methods,
98 error records) is retained but contributes zero extra methods to this total.
The owner's historical61 and earlier buffered timeouts are not added.
Evidence10 was not rerun.

## Capture correction and contrasting staging proof

The only behavioral change in the evidence transport was its private temporary
layout: create a new short directory using actual `tempfile.mkdtemp`, outside
the deep worktree, and pass the same path as TEMP/TMP/TMPDIR to preflight and
workflow replay. Streaming and bounds stayed idle120/max600, with a 4 MiB raw
merged-CLI output cap. No OS setting change, fake heartbeat or buffered retry.

Actual exclusively owned root:

```text
C:\Users\shbs\AppData\Local\Temp\bc2-etrf24pn
```

`temp-ownership.json` records creator PID12300 and the root's device/inode.
The workflow invocation verified that same identity and emptiness before reuse.

Preflight invoked existing `WorkflowFixture.work("A-work")`,
`WorkflowFixture.receipt("A-test")` and `evidence.write_json_atomic`.
A passive Python audit hook observed the actual staged file immediately before
`os.replace`; it did not replace/mock the write or synthesize success:

```text
C:\Users\shbs\AppData\Local\Temp\bc2-etrf24pn\bulletproof-workflow-fixture-afx2igtk\.ai\demo\evidence\receipts\.receipt-run-2.json-ojysic9v.stage
```

- Actual stage path: **145 characters**; final receipt path: **129 characters**.
- Actual staged bytes: **1,586**.
- Staged and final receipt SHA-256:
  `5ff9ee498310af7c364e4661cb3b2b7892947305efe0052c6077b504f0c14757`.
- Final immutable receipt loaded and resolved as **valid**; staged file absent
  after replacement; fixture cleanup left the owned root empty.
- Preflight exit0; full replay on the same root then exit0.

FACT: the old failure records contain 265/266-character receipt-stage paths.
FACT: the same existing receipt-staging code succeeds on the contrasting short
layout, and all100 workflow methods subsequently pass without source/test edits.
This strongly supports the verifier-owned long-TEMP layout as the cause of
the prior failure. No registry setting or platform-wide Windows limit was
inspected or changed, and no additional long-path reproduction was run.

## Acceptance proof

| Approved seam criterion | Result and actual proof |
|---|---|
| Shared live/explicit validation parity | VERIFIED: all16 owner methods pass, including all target-kind snapshot parity, explicit None/default behavior and current-file materialization. |
| Strict paired keywords; empty/malformed values must not fall back | VERIFIED: lone keywords/None combinations, positional extras, empty and malformed explicit values rejected; ordinary load remains fail-closed on absent/inconsistent live authority. |
| Prospective adoption validation, not dispatch authority | VERIFIED within library scope: absent live authority can be explicitly validated without publication; default paths still reject. No new CLI exists or is claimed. |
| Retained source/artifact/history/review/context/model/authorization policy | VERIFIED: actual owner negative cases and state/core regressions pass; independent AST comparison against accepted HEAD also proves the complete extracted validation policy and all75 other original definitions unchanged, including producer/model schema predicates. No new model-specific negative is claimed beyond actual inventory. |
| Exact retained old basis in A1/A2 with unresolved admission | VERIFIED: the unchanged independent test passes both genuine partial filesystem layouts, reads exclusively retained original workflow/design bytes and the actual ledger prefix, leaves all bytes unchanged, and gets blocked `RECOVERY_UNVERIFIED` with no next command. |
| No pure-gate/graph/schema bypass | VERIFIED: all48 gate, 11 core, one chronology and23 state methods pass, including pure no-I/O evaluation and prefix/cache/receipt-chronology checks. Gate, runner, evidence and other schema/graph definitions remain unchanged. |
| Full affected regression | VERIFIED: workflow100 plus retained disjoint evidence10, counts independently reconciled. |

The test actors, reviews, admissions and quality records remain synthetic
protocol inputs. Real bytes, Git fixtures, persistence, subprocesses and
state/gate calls are exercised, but these tests do not establish authenticated
independent approval, actual successful recovery or actual quality measurement.
Explicit binding is validation of a proposed adoption basis; no historical
prefix is authorized for ordinary dispatch.

## Exact commands and transport

Executed from the worktree root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-r2-stream.py preflight
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-r2-stream.py workflow
& $py -u -B scripts/run.py --idle 120 --max 600 -- $py -u -B .ai/workflow-reliability/evidence/c2b-state-independent-r2-reconcile.py
```

All three returned0. Both test/preflight calls used PowerShell `initial_wait=600`.
Final reconciliation was read-only apart from its new owned JSON output and
ran no tests. Exact argv/cwd/PATH/environment overrides are in each launch record.

Workflow child command was the real direct CLI route:

```text
<managed-python> -u -B scripts/run.py --idle 120 --max 600 --
<managed-python> -u -B -m unittest discover -s scripts/tests -p test_workflow*.py -v
```

| R2 invocation | Direct CLI runner PID | Bytes / chunks | First chunk before direct exit | Capturer elapsed |
|---|---:|---:|---|---:|
| Receipt-stage preflight | 49584 | 2432 / 2 | yes, at 0.708s | 1.271s |
| Workflow replay | 1920 | 18227 / 105 | yes, at 3.135s | 264.284s |

Real bytes were flushed to the log and stdout as read. These are raw merged
**CLI** bytes: the unchanged CLI itself merges child stdout/stderr and performs
UTF-8 replacement and line-oriented forwarding. No separate binary-transparent
child stderr/stdout retention is claimed. Neither capture overflowed.

## Cleanup, preservation and import limits

Both new direct CLI runners were reaped. Preflight cleaned its own fixture;
the same short root remained empty for replay. After successful replay, pins
were checked and the exact owned root was empty; only that directory was removed
with nonrecursive `rmdir`, after identity recheck. Final reconciliation observes
that exact root absent. No foreign process, unknown directory or OS-temp parent
was deleted. No whole descendant-tree termination claim follows from direct
reaping or empty temporary storage.

The receipt preflight observed **nine repository imports**: all eight script
modules plus `workflow_fixtures.py`; each hash matches the frozen pins.
This is explicitly preflight import evidence, not complete dynamic-import or
DLL attestation of the actual workflow unittest subprocess. All affected
test/helper source files and repository script dependencies are pinned.
Managed Python and Git entry executables are pinned, not the entire interpreter
stdlib, Git DLL set or historical machine. Parent shared state/report/docs/Q2
evidence remain outside the bounded pins.

Both earlier buffered timeout records remain unchanged. First-capture identity
and old whole-tree/fixture cleanup are still **UNKNOWN**. The owner's later
absence observation for PID43520 is not whole-tree proof. Neither old logs nor
missing identities were reconstructed, and the new clean root does not repair
historical uncertainty.

## Key hashes and evidence locations

| Path | SHA-256 |
|---|---|
| `scripts/workflow_state.py` | `fe30290e61d319c76546c31acd454bc7c642fc83ad55126e368fa44ab4b57a6e` |
| `scripts/tests/test_workflow_adoption_binding.py` | `318707e82f94864fde02c434ca54e87f9338b8c66beace679be271655343f1b5` |
| `scripts/tests/test_workflow_adoption_verification.py` | `9c78b24fcd90b757aac55c6425f3738741b4eefe175e5cd710b02e72b5616b53` |
| `c2b-state-independent-r2-stream.py` | `999ecd5c227625ba319df381368fef158635b2544915063161228277e37535f7` |
| `c2b-state-independent-r2-stage.py` | `155970da2274aac85633e7b95cdfed481e8a69774d1943510a4315745a2d7d9d` |
| R2 workflow `combined.log` | `5b5936080225e74bd9692c7c732d567a9d58648b26adf9de7fa290b334401b45` |
| `c2b-state-independent-r2-reconciliation.json` | `bdb6ba512f6b2449051b7989e9265357df4d1437725b149c770f4126c2a1de1a` |

Raw execution folders:
`c2b-state-independent-r2-preflight01/`,
`c2b-state-independent-r2-workflow01/`.
Each retains launch, output, result, inventory and before/after pins;
preflight additionally retains exact temp ownership and receipt-stage proof.
The r2 reconciliation lists all49 pins and executable/capture artifact hashes.
Original reports and both original batch directories remain in their old paths.

**Next: parent's separate code review.** No further replay is needed for this
bounded verification. No production/test changes, agents, installs, commits,
pushes, CLI work, recovery/migration, broad quality probes or release actions
occurred in this r2 correction. Overall C2, actual quality, human approval and
release remain outside this VERIFIED seam result.

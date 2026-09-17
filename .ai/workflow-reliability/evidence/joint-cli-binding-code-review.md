# Independent joint CLI / Q2 binding code review

## REVISE — one bounded source-binding ownership defect

Reviewed the current raw working bytes at actual Git HEAD
`ee6e0e34e78b70fcb672074af0a76f51fe937e1a`, independently of the implementers and
the preceding execution-report author. This is source/body review plus evidence
reconciliation, not a replacement execution report or whole-C2/Q2 release review.

**Reopen the Q2 source-binding implementation owner for R1 below.** No CLI,
state/gate/runner, metric-bridge or recovery expansion is requested. The parent
may retain this frozen tree and its evidence as a historical, reviewed-with-an-
open-finding checkpoint; it should **not mark the joint functional checkpoint
accepted** until R1 is corrected and its focused proof reviewed. The authorized
continuation permits bounded preservation before missing collectors, not
acceptance of a known defect or release.

### R1 — Source inspection does not enforce ownership of staged qualification inputs

**Priority: P2; blocks source-binding checkpoint acceptance.**

**Location:** `scripts/measure.py:905–910`, with the unchecked consumption at
`917–921` and final checks at `964–969`.

`inspect_source_binding` hashes/loads the supplied manifest, but its ownership
predicate checks only `run_id`, `root`, and one reservation for each of the three
smoke output names. It never reads `manifest["inputs"]` and never checks the
selected qualification paths' reservations. The subsequent `toolset_digest`
rechecks original/staged bytes and physical independence, but has no manifest
argument (`measure.py:701–714`). Rehashing the manifest at the end proves only
that the same supplied manifest bytes survived.

Consequently, starting from the valid source fixture, removing a qualification
row (or all such rows), changing its role/revision, or removing its input-path
reservation and updating `Context.output_manifest` to that actual manifest's
hash does not invalidate any condition in this inspector. Original/copy/tool
bytes, controller and toolset digest can remain unchanged. The inspector can
still run and return a successful binding smoke with unowned qualification
inputs. This is **not** a claim that forged metrics pass the full producer
validator: `validate_observations` reconstructs its Q1 manifest at `1169–1174`,
but this inspector does not call that validator.

The accepted root amendment requires staged consumers to require manifest
ownership (`artifact_resolution.staged`) and each selected input to have exactly
one unchanged `{artifact, role: "qualification", revision: null}` row and one
reservation (`reservation_and_overlap.manifest`). The original measurement
contract's `OwnedArtifactManifest` likewise requires exact ownership. Smoke is
not a metric collector, but that does not waive its already-implemented input
ownership boundary.

**Evidence/confidence:** direct inspection of the complete function and its
callees; an AST read independently found only the three manifest-key accesses
above. A read-only evaluation of the actual initial predicate also returned
`rejects=False` for missing qualification rows and wrong qualification roles.
That was a static predicate check, **not** a producer invocation, end-to-end
counterexample execution, or a new passing test. Existing real source tests
construct correct rows/reservations (`test_measure_source_bindings.py:79–85`);
their ownership-negative case removes a smoke result reservation and changes
controller bytes (`247–262`), not qualification ownership. Their seven passing
methods therefore do not address this defect.

**Smallest correction:** before creating the request or starting the real
tool, reconcile the sorted selected qualification set against the supplied
manifest: unchanged Artifact, correct qualification role/null revision, exactly
one row, and exactly one reserved path per selected input; reject conflicting,
duplicate or prefix-colliding ownership declarations. Retain the existing
original/copy/resource/controller freshness checks. This does not require
collectors, a new schema, a full metric validator, or changes to frozen helpers.

**Required owner proof:** actual-file malformed-manifest cases with newly
computed manifest references for missing/wrong/duplicate qualification rows
and missing qualification reservations; show rejection before a smoke child
starts or request output appears. Retain a valid real source-binding run and
empty/native compatibility. Do not substitute a predicate-only test, edited
summary, subset of an interrupted run, or synthetic successful tool output for
the correction's real focused proof.

## Other source/body conclusions

- **Ordinary CLI / AC04:** `workflow.py:63–87,238–326,593–632` uses normal live
  loading/binding/evaluation, one lexical mutation lock, registered argv/cwd and
  environment set/remove/inherit semantics. Admission and launch intent precede
  actual capture. No registered child runs on policy denial. Actual observer
  persistence failure or uncertain capture does not create completion; failed
  launch retains a null child exit. These conclusions were checked against
  `run.py:82–207`, not inferred from a handoff.
- **Nonmetric acceptance:** `workflow.py:124–235` constrains native proof to
  the registered direct Node/native-reporter route, checks admitted test-file
  membership and binds actual stdout. Finding outputs contribute declared
  artifacts; returned receipts retain producer attribution. The prospective
  gate evaluation and final source/artifact rereads were traced through
  `workflow_state.py:817–899` and `workflow_gate.py:289–353`: exact admission,
  earlier prerequisite references, current source, actual completion, receipt
  identity, and artifact hashes remain required. Red/compatibility consumption
  remains earlier than the consuming admission. No further high-confidence
  defect was identified in these changed CLI paths.
- **Resume/adoption / bounded AC05:** `workflow.py:389–563` implements the finite
  B0/B1/A0/A1/A2/A3/X publication boundary, prospective shared validation,
  event-before-workflow-before-pointer ordering, exact old-byte retention, and
  runtime ID/check mapping/executable-versus-handoff preservation. The exact-read
  race correction at `493–516,548–550` compares snapshot hashes to already-read
  candidate/review/history bytes rather than merely observing a later snapshot.
  Real audit-triggered publication/retain/race cases were read at
  `test_workflow_cli.py:436–537`; old evidence is not rewritten on resume.
- **Close and mandatory metrics:** `workflow.py:335–383` checks actual current
  feature HEAD, locally known default branches, scoped Git tree membership,
  bytes and modes before ordinary gate obligations. This is not authenticated
  remote branch-protection configuration. `METRIC_BLOCK`, automatic metric
  rejection, returned metric rejection and unconditional positive-close denial
  remain explicit. Parent state `state.md:301–313` specifically makes successful
  attachment unavailable, even for exit-zero/schema-valid scores. No fix to
  R1 may relax this boundary.
- **Root/native binding:** `measure.py:412–497,628–738,973–1006,1126–1191` and
  `probe.py:507–590` were read with the actual diff. Conditional nonempty-tool
  roots, opaque byte copies using exclusive creation, original/copy independent
  rechecks, strict component/path/link/identity checks, case/prefix conflicts,
  shared identical cross-tool refs, exact output reservations and final
  publication checks are present. A repository task-evidence ancestor is allowed;
  referenced source/output equality, alias or prefix overlaps are rejected.
  JSON-only `graph.persist` is not used to stage opaque tool inputs.
- **Source runtime binding apart from R1:** `measure.py:510–698,740–970` binds
  qualified source packages/resources/runtime/settings, fixed Python `-I -S -B`,
  explicit import roots/finder and nonambient plugin/backend settings. Node uses
  a pinned absolute TypeScript module and controlled compiler-host reads.
  Preload variables are removed. Real poisoned preload and unqualified-import
  marker tests were read, including rejection before `re2.py` executes. PE
  candidate hashes are not a complete loaded-DLL trace; post-startup module
  observations are not a sandbox.
- **Help/guide and normal tests:** all five public parser/help surfaces and
  `references/workflow-gates.md` describe the implemented boundary accurately,
  including denial rather than positive metric closure/recovery. Native
  `evals/workflow/helpers.mjs` genuinely invokes the public-CLI Python tests
  through the bounded runner; the five entry points are replays, not five new
  independent features. Fixture actor/reviewer metadata and schema-valid
  rejected scores remain synthetic protocol inputs. Files, Git operations,
  native assertions and owned child-process experiments are real.

The diff's only modified preexisting top-level functions are
`measure.validate_config`, `make_manifest`, `validate_observations`, and
`probe._execute_configured`; an AST comparison against actual HEAD confirmed
this. Baseline materialization/Git/attribute/import functions were not altered.
`workflow_state.py`, `workflow_gate.py`, `run.py`, `evidence.py` and
`measure_graph.py` have no diff from HEAD. Existing empty-Q1 toolset behavior and
all-nine mandatory metrics remain intact. No broad security audit was performed.

## Independent reconciliation of the existing execution evidence

Read both joint reports, all three owner handoffs, accepted C2 recovery r2
contract/review, measurement contract/review, root amendment/review, capture
helpers, inventories, results, selected raw logs and both raw indexes.
No test suite, fixture, collector, install, privilege experiment or process
cleanup was rerun in this review.

1. **Actual IDs, not totals alone:** reconciled retained `result.json` IDs,
   the six completed Q1 IDs from the original verbose log, and every r2 batch's
   selected/passed IDs. Exactly **204 retained + 58 new, disjoint = 262 passed**
   from **263 distinct discovered Python methods**. The sole remaining ID is
   `test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects`, with the
   retained actual **WinError 1314 / ENVIRONMENT-UNVERIFIED** disposition,
   not a skip or pass. Initial support's one import-error placeholder is not
   an actual method; its three subsequently discovered methods passed. No
   production assertion failure was observed.
2. **Native:** retained raw output says 13 passed, zero failed/skipped/cancelled:
   **five Python replays + eight reporter regressions**, not five new features.
   Source raw command artifacts independently reconcile to **nine successful
   smoke invocations and one expected unqualified-import rejection**.
3. **Timed method:** the two earlier idle-120 captures remain failed historical
   executions. R2's exact-code return-only profiler leaves original test bodies,
   validation results, exception propagation and unittest judgment intact.
   The real corruption method passed in **136.1955355 seconds** with **12**
   actual validation returns, **9.8257598–10.0497258 seconds** each. All actual
   target entry/return ordinals reconcile. Across preflight and the twelve new
   batches there are **55** real validation completions, maximum 11.2590918s.
   Every recorded batch remains **idle 120 / max 1800**. Preflight contributes
   **zero** additional methods. This supports cumulative silence, not a new
   internal trace of the killed attempts or retroactive cleanup proof.
4. **Prospective pins:** independently rehashed all **4,608** r2 paths against
   their recorded hashes and lengths: **zero current mismatches**. R2 before/
   after maps are identical. All **4,511** initial pins are an unchanged subset,
   and their before/after maps also match. Both raw indexes independently
   reconcile: **83 initial + 110 r2 records**, zero mismatches. No resource
   qualification suite was rerun.
5. **Runtime history limit:** the actual Git executable behind the launcher and
   seven managed Python extension files were current-only hashes in the initial
   capture. Their eight r2 prospective additions do **not** upgrade retained
   initial runs to before/after attestation or establish loaded-module closure.
6. **Cleanup limit:** all **13 new owned roots** have paired, empty-inventory,
   nonrecursive-removal records. No old root was touched here. The original
   **seven leftover directories**, both old timeouts' complete descendant
   cleanup, and historical whole-old-tree cleanup remain **UNKNOWN**.

The first report's then-incomplete Q1 disposition is historical, superseded only
by r2's completed selected regression evidence. R1 is a newly identified source
review defect, **not** a reinterpretation of those passing assertions as failures.
Existing `metrics.json` is historical/incomplete, not current quality proof.

### Raw-byte source pins independently matched

| File | SHA-256 |
| --- | --- |
| `scripts/workflow.py` | `a740bdc3325f86293341b7099010b8edba30062f7ddc2a2acef1012bc1b1e1a1` |
| `scripts/measure.py` | `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4` |
| `scripts/probe.py` | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |
| `scripts/tests/test_workflow_cli.py` | `bd2e20c4fc364de645c7118e45bb469b9f7408f19793ba1968f6008cdb6d540c` |
| `scripts/tests/test_measure_q2.py` | `8f0adaa478501bb4d1b81bb54ecdf45011d68787977537401fc4f24e563db7f8` |
| `scripts/tests/test_measure_source_bindings.py` | `e0cf6722ec29f31085e4fa0cc311d542fc80950e53ed37b790b5fa6fa3ca092e` |
| `references/workflow-gates.md` | `e931f3037c852de98a32a2fabe8625d740c214b4fed0612cf51b5dfae40c24f8` |
| `evals/workflow/helpers.mjs` | `d0bded0a4a646298ad61b89056a1c1e66f0448914d206b6b1a1602d42d054cb5` |
| `evals/workflow/failures.test.mjs` | `26f7c40184a7766690ab2cfc54f97baea403ab6c14612eb77e3b607966b29034` |

These are current raw bytes, including CRLF, not Git's normalized LF blobs.
The new CLI/guide/evaluation/root/source test files are currently untracked;
their absence from a tracked-only diff is not absence from this review.
Parent-owned report/state changes are outside the frozen execution pins.

### Independent-case durability/discovery

`evidence/joint-cli-binding-tests.py:16–71` contains three substantive real
boundaries: exact environment updates/inheritance, actual Git membership/mode
denials, and pending-handoff reclassification denial. They are persisted and
pinned, and the custom capture explicitly imports them at
`joint-cli-binding-verify.py:26–35`. They are **not normally discovered** by
`unittest discover -s scripts/tests`: their directory and hyphenated filename
require that custom loading. Thus 263 is the selected/custom joint inventory,
not a claim that ordinary regression discovery includes these three cases.
Preserving the checkpoint requires preserving this evidence module and its
loader; promote them into normal discovery in an authorized implementation
follow-up rather than silently claiming existing routine coverage.

## Per-scope disposition and remaining limits

| Scope | Review disposition |
| --- | --- |
| AC04 ordinary CLI | APPROVE within its five-verb, cooperative, nonmetric boundary; inherited runtime/lifetime limits remain. |
| AC05 ordinary resume/adoption | APPROVE bounded artifact resume and finite publication; complete AC05/recovery remain unimplemented. |
| AC09 selected affected regressions | Reconciled 262/263 evidence; no full-suite or Q5 green claim. R1 needs additional real focused proof. |
| ROOT01/02/04 native/public-Q1 input path | Existing bounded proof supported; no general source-inspector ownership approval while R1 is open. |
| ROOT03 | Real hardlink/junction cases supported; actual symlink case remains environment-unverified. |
| ROOT05 / source binding | REVISE for R1. Existing smoke is retained valid execution evidence, not scalar/JS measurement or full raw reconciliation. |
| Verifier limits | Exact counts/pins/capture qualifications above are retained; not authenticated actors, sandboxing, loaded-DLL closure or complete process-tree death. |

Missing scalar/shared-JS collectors, nonempty-JS-entrypoint rejection, coverage,
mutation, full raw metric reconciliation and all-nine completeness remain
pending. Successful guarded metric attachment, positive closure and recovery
are **not implemented and not approved here**. Human approval remains
unconfirmed; the previously reported GitHub EMU 403 publication block is
unchanged and was not retried. No whole-C2/Q2 release approval follows.

Only this review file was written. No agents, source/test/shared-state/doc
corrections, installs, commits, pushes or main-checkout access occurred.

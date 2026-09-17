# C2b-S independent code review — APPROVE

Reviewed 2026-09-17; final read-only reconciliation at 09:43:11 UTC.
**APPROVE for bounded functional preservation of the two state seams only.**
No high-confidence correctness or design-fidelity finding requires revision.
Parent may preserve the frozen seam implementation, its two focused test files
and supporting evidence under the existing partial-preservation boundary.
This is not CLI acceptance, completed C2, quality closure or release approval.

## Exact authority and scope

Baseline HEAD independently confirmed:
`d971634219a633cc4401fb7dcba9685e672978aa`.
Reviewed the current r2 contract, its separate design approval, continuation
plan, relevant state/traceability, owner handoff, both independent reports,
reconciliation/capture records, current state implementation and callers,
owner/independent seam tests and retained chronology regression.

| Reviewed file | Current SHA-256 |
|---|---|
| `.ai/workflow-reliability/c2-recovery-contract.json` | `80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d` |
| `.ai/workflow-reliability/evidence/c2-recovery-design-review-r2.md` | `ea26421c09238101062cc476c4ab9411420f7c105551a71cc0ae971ca8623930` |
| `scripts/workflow_state.py` | `fe30290e61d319c76546c31acd454bc7c642fc83ad55126e368fa44ab4b57a6e` |
| `scripts/tests/test_workflow_adoption_binding.py` | `318707e82f94864fde02c434ca54e87f9338b8c66beace679be271655343f1b5` |
| `scripts/tests/test_workflow_adoption_verification.py` | `9c78b24fcd90b757aac55c6425f3738741b4eefe175e5cd710b02e72b5616b53` |

Actual tracked `scripts` diff against HEAD is only `workflow_state.py`,
26 insertions / 6 deletions. The only untracked script files are the two
named seam tests. No CLI implementation exists at `scripts/workflow.py`.
Parent's disjoint status/documentation work is outside the frozen source pins.
Historical state/traceability statements that verification was still active
are not substituted for the newer r2 execution evidence.

## Findings and reviewed boundaries

**Findings: none requiring revision.** The following are review conclusions,
not new scope or claims of complete product acceptance:

- `scripts/workflow_state.py:760-809`: the public helper first validates
  contract/ledger schemas and slug agreement, then retains the entire former
  design-validation policy. Retained revision paths and bytes, review role,
  designer/implementer context separation, unattended authorization, candidate
  hashes, normative components, history/adoption order and adopted source/
  contract bindings remain enforced. Producer/model schema predicates are
  structurally unchanged; no additional model-specific negative is claimed.
- `scripts/workflow_state.py:812-814,887-899`: ordinary loading still reads
  the canonical live pointer and resolves the actual ledger/receipts. It does
  not substitute a prospective design or filtered history. The extraction
  moves ledger validation behind the live pointer read in default binding;
  malformed simultaneous inputs may therefore change which error surfaces
  first, but neither path becomes permissive. Missing/invalid authority still
  fails closed.
- `scripts/workflow_state.py:984-1013`: keyword-only pairing uses `is None`,
  not truthiness. Both `None` retain live behavior; a lone non-`None` value
  raises `ValueError`; empty/malformed explicit values reach strict validation
  instead of live fallback. The valid explicit branch does not load live
  pointer/ledger authority. It shares the exact existing target validation,
  dependency materialization, current-file snapshots and `BlockedInput`
  handling; it does not manufacture source snapshots or persist anything.
- `scripts/workflow_gate.py:456-467,489-511`: unresolved executable admission
  still blocks readiness globally. No gate, Event/Ledger schema, receipt
  chronology, graph/cache, evidence, runner or measurement code changed.
  `scripts/tests/workflow_fixtures.py:144-148` and existing core/gate callers
  keep ordinary live load/bind behavior. The only explicit-basis consumers
  currently outside the state module are the new tests, not dispatch code.
- `scripts/tests/test_workflow_adoption_verification.py:19-83`: the independent
  case combines genuine A1/A2 disk layouts with an unresolved admission,
  exclusively retained old workflow/design bytes and the exact persisted
  pre-adoption ledger prefix. It checks blocked `RECOVERY_UNVERIFIED`, absent
  next command and unchanged real authority bytes. It does not erase the
  pending admission or bless historical-prefix dispatch.
- `scripts/tests/test_workflow_adoption_binding.py:35-345`: owner coverage
  exercises all target kinds, paired/default parity, missing/invalid live
  authority, strict schema/slug/authorization/history/provenance negatives,
  real tampered/missing artifacts, current directory membership, blocked
  dependencies and fresh-interpreter/Git byte preservation. These are real
  filesystem/library operations with synthetic protocol identities/events,
  not authenticated approval, actual quality measurement or process recovery.

No bootstrap cycle was introduced: explicit validation consumes a supplied
prospective triple and retained artifacts without requiring the live pointer.
The absent-authority test demonstrates that seam, not a production bootstrap
transaction: the fixture first constructs synthetic adoption data and removes
live files. Its pointer-before-event fixture writes
(`scripts/tests/workflow_fixtures.py:112-142`) are not the future CLI protocol.
Future adoption must construct the real design-only snapshot with the existing
`binding_mode="guarded"` field before validating the prospective ledger, rather
than calling normal binding to invent its own adoption evidence.

The explicit helper is not an authorization boundary by itself. Approved
future A1/A2 callers must use the exact old basis only for lifetime preflight,
retain authoritative readiness and receipt chronology, and preserve runtime
IDs/executable classification. Ordinary status/next/record/close must retain
live authority. Those CLI compatibility/publication checks are not supplied
by this seam and are not claimed implemented here.

## Independent evidence reconciliation and freshness

No test was rerun: no concrete missing seam proof justified another execution.
Read-only managed Python independently hashed current files, compared Git HEAD
and ASTs, and parsed existing raw logs/inventories/results rather than accepting
report totals alone.

- **49/49** bounded pins match the current tree/runtime entry executables,
  both r2 before/after pin sets and all original29 pins.
- All **17** artifact hashes in the r2 reconciliation match current bytes,
  including the raw r2 logs and execution records. Preserved original failure
  artifacts and both timeout records remain pinned.
- **75** other original state definitions and all nondefinition top-level
  statements are AST-identical to HEAD. The complete extracted validation
  tail and snapshot/materialization tail are AST-identical. The only added
  top-level definition is `validate_design_binding`.
- Accepted verbose method IDs exactly match the saved inventories and current
  test AST inventories, with no duplicates or overlapping batch IDs.

| Accepted batch | Distinct passing methods | Result |
|---|---:|---|
| `c2b-state-independent-r2-workflow01` | 100 | exit0, 263.471s; no failures/errors/skips/timeouts |
| Retained `c2b-state-independent-transport01` | 10 | exit0, 5.501s; disjoint evidence suite |
| Total distinct accepted methods | **110** | Two separate processes, not an aggregate run |

Workflow100 comprises owner16 + independent1 + existing state23 + core11 +
chronology1 + gate48. The scale test's standalone `ok` after real intermediate
output was accounted for. Preflight, historical owner61 and old failed
workflow100 contribute **zero additional methods**.

The r2 preflight launched at **09:31:33 UTC** and workflow replay at
**09:32:05 UTC**, before this review's current-source reconciliation.
Both streamed actual CLI output before direct exit without overflow, under
unchanged idle120/max600 bounds. Raw output is merged CLI output, not separate
binary-transparent child streams.

The passive audit hook in `c2b-state-independent-r2-stage.py:26-65` observes
actual staged bytes before replacement; it does not mock receipt writing.
The record independently reconciles a **145-character** stage path,
**1,586 bytes**, matching stage/final SHA-256
`5ff9ee498310af7c364e4661cb3b2b7892947305efe0052c6077b504f0c14757`,
and a final receipt resolved **valid**. This is retained execution proof,
not a newly recreated receipt. The same owned short root was used for replay.

| Evidence artifact | SHA-256 |
|---|---|
| `c2b-state-independent-r2-reconciliation.json` | `bdb6ba512f6b2449051b7989e9265357df4d1437725b149c770f4126c2a1de1a` |
| R2 workflow `combined.log` | `5b5936080225e74bd9692c7c732d567a9d58648b26adf9de7fa290b334401b45` |
| Retained evidence10 `combined.log` | `a37c61a3f3843eddc4ae6922f03bf0c62aadb8952ef8c4cb8095e1949ce22ee3` |

Pins attest the bounded sources and Python/Git entry executables, not all
stdlibs/DLLs or the machine. The nine observed repository imports belong to
receipt preflight, not exhaustive workflow-subprocess dynamic-import proof.
Existing `metrics.json` remains historical/incomplete, not current quality.

## Preserved failure and cleanup history

The owner had two buffered outer idle120/exit124 captures; gate proof was lost,
not reconstructed. The initial independent stream route worked, but its deep
private TEMP layout failed: the retained raw log independently reconciles
**98 FileNotFoundError records across 58 methods, 42 positive/100**, exit1.
These harness failures are neither assertion kills nor production-defect proof.

The authorized capture-only short-root correction, real receipt preflight and
one full replay supplied the later green proof without production/test or OS
settings changes. The original BLOCKED report remains historically correct.
No old count or failed record is rewritten into success.

Original first-timeout child identity and whole-tree/fixture cleanup remain
**UNKNOWN**. The historical absence observation for PID43520 is not death proof.
New direct runners were reaped; records show the new owned short root empty and
removed nonrecursively after identity checks. This review read those records
and performed no temp-directory/process operation. New cleanup cannot upgrade
old cleanup certainty or establish exhaustive descendant termination.

## Bounded acceptance disposition

| Criterion | C2b-S disposition | Remaining boundary |
|---|---|---|
| AC04 | **VERIFIED-WITH-LIMITATIONS** | State binding/validation preserves the existing readiness path; no full guarded CLI, admission-to-spawn integration or authenticated actor independence is proven. |
| AC05 | **VERIFIED-WITH-LIMITATIONS** | Explicit retained-basis validation, byte preservation and unresolved-admission denial are proven at library level. Full artifact-only host resume, publication retries and positive process recovery remain unproven/blocked. |
| AC09 | **VERIFIED for affected functional regression/review only** | Frozen source, exact policy/materialization preservation and 110 distinct passing methods support this slice. Mandatory Q2–Q5 release quality remains open; this is not overall AC09 or release completion. |

**Parent can preserve only the approved seams and their proof.** Five ordinary
CLI verbs remain approved future integration, not implemented functionality.
Recovery/sixth verb and v2 migration stay blocked/deferred. Full guard CLI,
authenticated actor independence, positive process recovery, all mandatory
quality, human approval, host exercises and publication remain unproven.
The GitHub 403/EMU publication blocker is unchanged; no attempt was made.

Only this additive review file was written. No workflow restart, delegation,
installation, production/test/shared-state/doc modification, commit or push.
Read-only commands used the specified managed Python `-B`, bytecode disabled,
and `scripts\run.py --idle 30 --max 60`; Git used the specified bundled path.
The first reconciliation probe exited1 because it treated `runtime:git` as a
relative filename; correcting the read-only alias mapping to the pinned entry
executable produced exit0. This was a reviewer probe error, not a test rerun
or product failure.

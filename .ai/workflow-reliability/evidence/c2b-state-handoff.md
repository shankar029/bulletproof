# C2b-S local seam freeze: implementation present, gate regression BLOCKED

## Scope and authority

Implemented only the two explicitly authorized state seams from r2 contract
`80442414f2bdc597e75222e7ba475339b5932f732b1f947ffd9828267e0b949d`
and its independent design review. This is local implementation evidence,
not independent verification/review, acceptance, preservation or release.
Human design approval remains unconfirmed under the supplied autonomous authority.

Production/test write set used:

| File | Final SHA-256 |
|---|---|
| `scripts/workflow_state.py` | `fe30290e61d319c76546c31acd454bc7c642fc83ad55126e368fa44ab4b57a6e` |
| `scripts/tests/test_workflow_adoption_binding.py` | `318707e82f94864fde02c434ca54e87f9338b8c66beace679be271655343f1b5` |

Existing `test_workflow_state.py` and all original verifier tests are unchanged.
No CLI, native failure evaluation, operator guide, schema, gate, evidence,
runner or measurement change. No platform search, recovery stub, dependency
installation, agent, commit, push or publication. Parent's status/report/
traceability and Q2 evidence were observed as disjoint work and left untouched;
the unrelated `evals/report.md` edit remains untouched.

## Exact implemented behavior

- `validate_design_binding(root, contract, design, ledger) -> dict` shares
  the entire former `_load_design` validation body. It first validates the
  contract and ledger schemas and their slug agreement, and resolves the root.
  All existing design/history/path/artifact/review/context/authorization/
  candidate/normative/adoption/source-binding checks remain intact.
- `_load_design` still reads the canonical live pointer, then delegates.
  Ordinary loading cannot silently substitute an explicit candidate.
- `bind_inputs(..., *, design=None, ledger=None)` rejects a lone explicit
  value. Both values use the shared validator without reading the live
  pointer/ledger. Neither uses the original live path. Both paths share the
  unchanged dependency/snapshot loop. Empty/malformed explicit values do not
  fall back to live authority.
- The paired mode is an adoption-basis validation seam, not dispatch or
  publication. It writes no pointer, ledger or receipt and does not manufacture
  a snapshot or remove an unresolved admission. Future ordinary verbs must
  retain live loading. Future adoption constructs its snapshot from real
  `source_snapshot` plus all existing guarded binding fields, including
  `binding_mode="guarded"`; that CLI construction is not implemented here.

## Tests and failure history

The new tests use owned real Git repositories, actual copied/hashes-checked
files, existing persistence and a fresh Python process. Design/review identities
and adoption/pending-admission records are explicitly synthetic protocol data;
they are not actual independent approval, execution, metric or recovery proof.
No mocked producer or fabricated quality result establishes a new seam test.

| Record directory (`evidence/c2b-state-...`) | Observed result |
|---|---|
| `red01` | 2 methods, 2 expected missing-API errors, exit1; **not behavioral red or mutation kills** |
| `seams01` | 16 new methods pass, 41.518s, exit0 |
| `evidence01` | 10 existing methods pass, 5.899s, exit0 |
| `workflow01` | Combined workflow capture killed by outer idle120, exit124; no saved result/count |
| `state02` | 23 existing state methods pass, 4.220s, exit0 |
| `core02` | 11 unchanged verifier regression methods pass, 14.420s, exit0 |
| `chronology02` | 1 unchanged verifier chronology method passes, 1.944s, exit0 |
| `gate02` | Split gate capture also killed by outer idle120, exit124; no saved result/count |

**61 distinct passing methods across successful local batches**, including
16 new methods. No duplicate aggregate count is added. Successful batches have
no reported failures/errors/skips and their 25 before/after pins match.
Neither incomplete capture contributes a pass. Running existing verifier-authored
tests in this implementation context is a regression replay, not fresh
independent verification.

New coverage maps to the approved seam criteria:

| Criterion | New test coverage |
|---|---|
| Default/explicit parity | All action/check/increment/ship targets; exact ResolvedInputs; explicit None parity |
| Pair/strict boundary | Either keyword alone, None/unpaired, positional extras, empty/malformed values |
| Prospective absent authority | Exact triple validates with live workflow/pointer/ledger absent; normal path fails |
| Partial publication | Real retained r2 documents/live newer ledger with old pointer; valid explicit r1 basis and prospective r2 validation leave actual bytes unchanged |
| Shared rejection policy | Schema/version/slug/sequence, guarded binding literal, review role/context, authorization, candidate, history/retained path/hash |
| Artifact/provenance integrity | Missing/tampered document/normative/review/authorization/disposition files, component mismatch and independently rehashed inconsistent adoption source |
| Current materialization | Actual file additions/missing files, directory membership, explicit BlockedInput dependency parity and blocked gate |
| No lifetime bypass | Synthetic unresolved admission remains RECOVERY_UNVERIFIED through explicit old-basis gate evaluation; no source or authority writes |
| Fresh process / Git | Real fixture commit and fresh interpreter produce matching snapshot; actual Git status and authority bytes unchanged |

## Timeout boundary and stop

The initial capture helper buffered all child output until return. The outer
`scripts/run.py --idle 120` therefore could not observe ongoing unittest
progress. The combined batch exceeded that silence ceiling. Preserve its
input copies and `c2b-state-workflow01-timeout.json`; buffered logs were lost,
not reconstructed.

The single allowed recovery split the same scope into existing module batches
and added persisted launch metadata plus actual observer lifecycle records to
the **evidence helper only**. No heartbeat or raised idle/max limit concealed
silence. State/core/chronology completed; gate again exceeded outer silence.
`c2b-state-gate02-timeout.json` preserves that second failure. Test execution
stopped immediately; there was no third attempt.

Gate's recorded direct PID was 43520. A subsequent exact-PID CIM observation
returned absent. Existing runner cleanup was best effort; neither PID absence
nor that cleanup establishes whole-tree death. The first capture did not retain
child identity. Complete removal of timeout-owned temporary fixtures is
unverified; no guessed temp directories or foreign/named processes were deleted.

**Gate regression remains BLOCKED/unverified**, not a reported product assertion
failure. Actual progress inside the buffered killed batch is unknown. Parent
must obtain the missing gate proof with a progress-visible capture strategy in
a fresh authorized verification context before accepting or preserving this
slice. Do not widen into CLI implementation on these partial results.

## Exact command replays

From the worktree root, the common executed setup was:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH='C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
```

Each observed test command used this exact wrapper and capturer:

```powershell
& $py -B scripts\run.py --idle 120 --max 600 -- $py -B .ai\workflow-reliability\evidence\c2b-state-capture.py TAG -- $py -B -m unittest discover -s scripts\tests -p PATTERN -v
```

| Executed TAG | Literal PATTERN argument |
|---|---|
| `red01` | `test_workflow_adoption_binding.py` |
| `seams01` | `test_workflow_adoption_binding.py` |
| `evidence01` | `test_evidence.py` |
| `workflow01` | `test_workflow*.py` |
| `state02` | `test_workflow_state.py` |
| `core02` | `test_workflow_core_verification.py` |
| `chronology02` | `test_workflow_core_verification_r2.py` |
| `gate02` | `test_workflow_gate.py` |

Patterns containing `*` were quoted in PowerShell. These are historical replay
instructions, not authorization for another attempt here. Tags refuse overwrite;
use a new tag only after parent authorization. The current capturer still
buffers long test output and is **not recommended unchanged for the gate retry**.
Successful result JSON retains literal argv/cwd, exit, runtime, hashes, complete
decoded stdout/stderr files and exact input copies. Post-timeout recovery records
also include launch metadata and actual lifecycle observations.

## Freeze and remaining obligations

`c2b-state-freeze.py` performs only read-only source/record reconciliation and
emits `c2b-state-freeze.json`: exact raw artifact hashes, current bounded pins,
counts from successful unittest summaries, and AST comparison confirming
unchanged original validation body/materialization loop/other definitions.
This supplemental structural check is not a replacement for the missing gate
regression or independent review. Pins cover the bounded scripts/tests/contracts
and Python/Git executables, not all imports, libraries or the entire machine.
The evidence helper changed between original and split captures; its original
bytes remain in each batch's input copy. Production/test bytes did not change
after `seams01`.

Parent owns fresh verification, separate review, status artifacts and local
preservation. All CLI integration, ordinary adoption failure-table execution,
original sixth verb/recovery, actual quality collectors/proof Q2-Q5 and overall
C2/AC05/release remain open. No acceptance, independent proof, full quality,
platform recovery, human confirmation or release is claimed by this handoff.

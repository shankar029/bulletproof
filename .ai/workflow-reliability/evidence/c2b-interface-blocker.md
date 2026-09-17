# C2b stopped at mandatory frozen-interface seam

## Disposition

**BLOCKED before CLI implementation.** This is an implementation-role interface
diagnosis, not an independent review, actual recovery verification, C2 completion
or release result. Parent owns state/report/traceability and the bounded amendment.
No production, test-suite, operator-guide or historical evidence file was changed.
Only additive `c2b-*` evidence was written.

Observed HEAD: `d971634219a633cc4401fb7dcba9685e672978aa`, branch
`shbs-microsoft-workflow-app-verification`. Initial Git status also contained the
parent's `.ai/workflow-reliability/state.md` edit and the unrelated `evals/report.md`
edit; neither was touched. Human design approval remains unconfirmed.

## Concrete incompatibility

1. **FACT — resolution is not representable to the frozen gate.**
   `scripts/workflow_gate.py:456-467`, `_Evaluation.unresolved`, treats every
   executable admission lacking **completed** as `RECOVERY_UNVERIFIED`.
   It does not consult `interrupted`, `recovered`, a recovery artifact or a
   resolved recovery observation. Consequently even independently substantiated
   recovery could not end that lifetime blocker through the specified recovery
   events. This is not a request to trust the presence of a `recovered` label.
2. **FACT — a completion workaround would fabricate lifecycle facts.**
   `scripts/workflow_state.py:706-718` requires a terminal process observation
   before `completed`, and `:699-704` requires observed spawn before direct exit.
   In the intent/Popen crash interval those observations are unknown.
   An environment reset must not be translated to a fictional launch-failed,
   spawned or direct-exited event. Filtering old admissions before `evaluate`
   would create a second status authority and bypass the frozen gate.
3. **FACT — durable typed ownership/recovery binding is unspecified.**
   `validate_event` at `scripts/workflow_state.py:631-653` strictly accepts its
   enumerated fields only. There is no LockOwner or recovery-artifact reference.
   `receipt_refs` is check-receipt identity, not an arbitrary recovery artifact.
   `ProcessObservation` is exactly eight child-lifecycle fields, not guard
   ownership. `reason` is unrestricted diagnostic text, with no approved encoding
   or resolver for authoritative ownership/evidence.
   `scripts/evidence.py:150-172` persists LockOwner only in the lexical mutex,
   then unlinks that mutex in `finally`. The continuation review's C2 seam
   explicitly requires durable ownership after that file disappears.

**INFERENCE:** implementing all six verbs correctly requires a bounded
state/gate contract clarification and affected C1 correction. The allowed CLI
write set alone cannot implement valid recovery while retaining authoritative
Readiness and the frozen strict schemas. Unsupported platform proof remaining
blocked is intentional; inability to consume *any* substantiated recovery is
the separate interface issue.

## Narrow executed reproduction

`c2b-seam-probe.py` uses the existing, explicitly synthetic `WorkflowFixture`.
It does not invoke its synthetic process/metric helpers, create a child, claim
independent approval, or manufacture platform evidence. It exercises real atomic
persistence/lexical locking and the public pure gate on synthetic protocol data.

Observed once in `c2b-seam-s01.json`:

- Deliberate exception inside an actual owned lexical lock removed the lock.
  This was **not** an observer-persistence-failure or guard-death test.
- Adding proposed `lock_owner` or `recovery_evidence` fields to an otherwise
  schema-valid event is rejected with `Invalid record fields`.
- Admission plus intent is blocked at ledger sequence 3.
- Adding schema-valid synthetic `interrupted` and `recovered` events is allowed;
  at sequence 5 readiness is still blocked, `RECOVERY_UNVERIFIED`,
  `next_command=null`. These labels alone **should not** unlock; source inspection
  establishes that the current gate also has no path for validated recovery.
- All seven bounded before/after input hashes matched; the owned temporary
  fixture was removed.

Runner exit **0**, no timeout/retry, stderr empty. This means the diagnostic's
assertions were satisfied, **not** that C2 or recovery passed.
Positive CLI/native tests: **0; not implemented/run**. No metric collection,
mutation, independent verification/review, installation, nested agent, commit,
push or publication was performed. Native/metric producer integration reads
were not expanded after finding the mandatory stop condition.

Exact executed PowerShell replay from the worktree root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -B scripts/run.py --idle 30 --max 90 --label c2b-seam-s01 -- $py -B .ai/workflow-reliability/evidence/c2b-seam-probe.py s01
```

For another replay change both `s01` occurrences to a new alphanumeric tag.
Existing output is refused. The JSON preserves literal inner argv/cwd, version,
protocol inputs, derived outputs and seven source/contract hashes. Printed stdout
is that JSON, with its trailing newline. The outer command above and exit are
retained here and in the tool transcript.

## Bounded decision requested from parent

**Recommended default — approve a narrow typed recovery-binding amendment,
then return correction to the C1 owner with affected proof reopened.**

Specify, before implementation:

1. A durable admission-to-LockOwner binding (run/token/guard identity/workspace)
   written before Popen and retained independently of lexical lock removal.
   Select and document its exact schema/location/reference. Do not overload
   `reason`, equate unrelated IDs, add a process-observation field or silently
   create a second writable process tracker.
2. An immutable hash-bound RecoveryEvidence reference and a materialized,
   validated recovery observation available to the pure gate. Specify supported
   platform evidence validation and independent attribution/guard-inactivity
   rules. Unknown creation/descendants and unsupported evidence stay blocked;
   caller booleans or recovered labels alone never suffice.
3. Resolution semantics: accepted interrupted/recovered evidence ends only the
   unresolved-lifetime blocker. It does not count as executed work, successful
   proof, closure or automatic replay. Specify sequence/run/identity matching
   and rejection of malformed, stale, missing or tampered recovery artifacts.

This is a recommended clarification, not a selected new schema or implementation.
Do not change standalone `exclusive_lock` semantics or fabricate a Windows reset
API. Actual positive recovery remains environment-blocked until supported
evidence exists; protocol tests must retain their synthetic label.

After bounded acceptance, resume C2b's original scope: six verbs, real CLI/process
and artifact-resume tests, five paired native failures, strict producer validation
and exercised operator documentation. Positive quality closure remains separately
blocked by Q2-Q5's actual required collectors/proof; no threshold is waived.
Parent still owns independent verifier/reviewer, status artifacts and preservation.

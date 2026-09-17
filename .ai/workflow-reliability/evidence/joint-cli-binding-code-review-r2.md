# Focused independent R1 code re-review

## APPROVE — close R1; bounded checkpoint preservation permitted

The R1 ownership defect in `joint-cli-binding-code-review.md` is corrected.
The parent may accept and preserve the **bounded CLI + tool-binding checkpoint**
with the original review's explicit limits and the qualifications below. This
is not full Q2, quality, metric-attachment, positive-close or release approval.
No new high-confidence blocking finding was identified in this correction.

This is a replacement independent reviewer for unavailable sync reviewer
`eaec213a`, not a claim to be that reviewer. I take its exact original review
as authority for unchanged scope. I read that review, the owner R1 handoff,
the independent R1 report/reconciliation/seal, actual helper/call/regression
bodies and relevant existing callees. I did not redo the broad CLI/Q2 review.
The reviewed checkpoint records base HEAD
`ee6e0e34e78b70fcb672074af0a76f51fe937e1a`; parent-owned uncommitted
state/report material remains outside the frozen execution pins.

## Source/body determination

- `scripts\measure.py:901–923`, `_validate_binding_ownership`, derives
  expected ownership from **`tool_artifacts(config)`**, not from the supplied
  manifest. That existing function (`458–495`) reads and validates selected
  help/configuration/qualification Artifacts, canonical paths and original
  file identities; rejects conflicting or aliased originals; permits identical
  explicit cross-tool sharing; and returns the sorted unique selected set.
- The helper requires input/reservation lists and exact row/Artifact field
  sets. `_path_partition` runs separately on each list **before** dictionary
  construction or cross-namespace deduplication. Thus duplicate/conflicting
  declarations cannot disappear in a dictionary or set. Its canonical-name,
  Windows case-folding and ancestor/descendant checks reject ambiguous paths.
  The combined namespace partition also catches input/reservation prefix or
  case conflicts while allowing the required identical path across the two
  namespaces.
- Every selected Artifact must have its exact path reserved and an unchanged
  `{artifact, role: "qualification", revision: null}` row. Separate duplicate
  rejection makes these membership checks exactly-one checks. Canonical JSON
  comparison preserves type distinctions, including integer versus floating
  byte counts; extra row fields, changed references and wrong role/revision
  reject. Unselected qualification rows reject. Other nonqualification inputs
  do not become selected qualifications; this is not a full metric validator.
- The sole call, `inspect_source_binding:934`, follows verified manifest
  loading and precedes request publication (`950`) and `run_capture` (`958`).
  Existing run/root/smoke reservations, output-existence, original/copy/tool/
  resource/controller checks and post-execution freshness checks remain.
  No bootstrap, controller behavior or metric boundary was changed.

The new normally discovered regression method
`test_qualification_ownership_rejects_rehashed_manifests_before_launch`
(`scripts\tests\test_measure_source_bindings.py:265–367`) persists actual
malformed manifests and recomputes their Context Artifacts. It activates the
audit only around the real inspector, asserts `ValueError`, no subprocess
attempts/write opens and absent smoke outputs, and then uses the same audit
hook for a real valid Node control. It does not mock the runner or replace
the inspector with a predicate. These observations are controller-side Python
audits, not an OS-wide process monitor.

## Narrow scope and independent read-only reconciliation

I independently rehashed the current source/test bytes and reconstructed the
original raw files in memory:

| File | Current SHA-256 | Reconstructed original SHA-256 |
| --- | --- | --- |
| `scripts\measure.py` | `1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1` | `1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4` |
| `scripts\tests\test_measure_source_bindings.py` | `bcc36f23061dd5b4db2dfcb161c0202bbe95db1fb930b1c6ef79fe8c9b95d1b3` | `e0cf6722ec29f31085e4fa0cc311d542fc80950e53ed37b790b5fa6fa3ca092e` |

Removing only the helper and its call reconstructs the reviewed measurement
file exactly, including CRLF. Removing only the regression method and `sys`
import reconstructs the reviewed test file exactly. The retained R1-only diff
agrees with the actual bodies. All **4,651** prospective file pins currently
match both hash and length, and before/after maps are identical. I also
independently checked all **33 seal entries** and **29 raw-index entries**.
Unchanged CLI/source/guide conclusions remain the original review's, rather
than fresh broad approvals inferred from hashes.

The owner's immutable `q2-binding-r1-repro\reproduction.json` reconciles an
actual unfixed counterexample: removed qualification row, reservation retained,
new malformed-manifest hash/length, Windows-quoted audit argv matching the
retained Node command, exit zero and actual TypeScript symbol `answer`.
I did not restore or rerun the unfixed implementation.

For the independent verifier's fresh run, the result, selected/passed IDs and
raw log reconcile **10 methods passing in 801.802652 seconds**, with no
failures/errors/skips; the recorded bounded command is **idle 120 / max 1800**
and completed without timeout. Its adapter only changes the capture directory
prefix and enables unittest fail-fast, not production or test bodies.

I independently recomputed all **20 distinct malformed manifest hashes and
lengths** from the retained documents. Every case records a rejection, zero
audited subprocess attempts, zero audited run-root write opens and no smoke
outputs. The valid control reconciles to its retained real Node command and
audit argv, one launch, two controller write opens and symbol `answer`.
Raw request/command references and the observed result agree with that control.
The broader affected records retain six three-tool/two-revision smokes and
existing resource/import/preload/native/empty compatibility proof. The raw
reconciliation's 11 command artifacts (10 successful, one expected import
rejection) are not extra test methods.

## Conditions retained for parent preservation

- These ten fresh methods overlap nine historical passing IDs and add one
  ownership regression. Historical **262/263 Python** and **13 native entries**
  were **not refreshed**; native remains five Python replays plus eight reporter
  regressions. Do not add ten to 262 or claim new full-suite discovery/coverage.
  Preserve the original custom evidence tests and loader and their discovery
  limitation.
- Actual symlink coverage remains **WinError 1314 / ENVIRONMENT-UNVERIFIED**,
  neither skipped nor passing. The new owned short root has an empty inventory
  and nonrecursive removal record. Old seven-directory/whole-tree cleanup and
  complete historical descendant termination remain **UNKNOWN**.
- Earlier runtime current-only pinning is not retroactively upgraded.
  Prospective hashes and observed module paths do not establish loaded-DLL
  closure, sandboxing, authenticated actors or general process-tree death.
- Missing collectors, shared-JS/scalar measurement, coverage/mutation,
  nonempty-JS-entrypoint rejection, full raw metric reconciliation/all-nine
  completeness, successful guarded metric attachment, positive closure and
  recovery remain pending. Complete AC05, human approval and release remain
  unapproved; the previously reported publication block was not retried.

Only this review file was written. No agents, test reruns, installations,
production/test/shared-state/guide changes, commits, pushes, main-checkout
access or old-root cleanup occurred. Read-only evidence/hash checks used the
managed Python with `-B` through `scripts\run.py` at idle 30 / max 90.

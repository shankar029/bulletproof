# C1 independent verification r3

## Verdict: VERIFIED-WITH-LIMITATIONS — bounded C1 functional acceptance

**FACT:** One independent replay ran **75/75 workflow tests** and **10/10
evidence tests** successfully, with zero failures, errors or skips. Both
commands exited **0**. The original F1–F3 regressions, residual F1
exact-reference regression, and all four new consuming-surface/reclosure
cases passed.

**F1, including its residual exact-reference defect, is resolved for the
bounded tested surfaces. F2 and F3 remain resolved on replay.** No concrete
remaining counterexample was observed in the authorized correction scope.
This is not exhaustive correctness, separate code-review approval, C2
authorization, actual quality collection or release readiness.

**FACT:** No applicable pinned input changed within either suite or across
this capture. All **172 observed file-backed workflow imports** matched
their before/during/after hashes. The independently tested Q1 modules were
already newer than the implementer's handoff, as detailed below; their
actual replay bytes—not the old handoff hashes—were pinned.

The final handoff recheck is in `c1-independent-r3-handoff.json`. A subsequent
dependency change requires new stable proof; the captured pass is not a
future-freshness guarantee.

## Scope and method

Read `c1-correction-r2-report.md`, `c1-correction-r2-handoff.json`, the
corrected `closure_proven_before` path and the four new tests. Reused the
original C1 sub-ACs and prior source-grounded findings.

The previous iteration established the relevant execution, prerequisite
receipt, closure and UTC validation paths. This iteration inspected the
specific correction and its supported consuming surfaces, then reran the
complete authorized workflow/evidence suites. It did not broaden into a
redesign, Q1 review or unrelated defect hunt.

No new tests were needed: the unchanged independent residual regression
plus the four added owner tests covered the requested correction boundaries.
No source/test/helper, original evidence, shared state, installed tools, OS
settings or main checkout was edited. No nested agent, commit, publication
or C2 advancement occurred. Only additive `c1-independent-r3-*` evidence
was written.

**32 protected prior evidence/test files** were checked before and after,
with zero changes. This includes both independent test files and all
original/r2 independent report/log/manifest files. Historical NOT-VERIFIED
returns remain intact; they were not relabeled or overwritten.

## Per-finding assessment

### F1 — VERIFIED-WITH-LIMITATIONS

**Source grounding:** `scripts/workflow_gate.py:365-380` now retains each
dependency's full proof result from the prefix preceding the closure.
It requires every prefix dependency to be valid **and** the closure's exact
receipt ID/hash set to equal `_merge_refs(proofs)` using `_refs_equal`.
The existing current-source/current-reference, outcome, member-execution,
prerequisite-closure and commit-syntax checks remain in the surrounding
`proof` path.

**INFERENCE supported by the inspected code and actual test results:**
the correction ties prefix validity to the same proof that the closure
claims to consume, rather than comparing unrelated prefix booleans and
current receipt references. It uses the existing derived dependency graph
and comparison helpers, not a second authority.

| Surface / boundary | Actual replay evidence |
|---|---|
| Original premature closure | Unchanged `test_closure_cannot_be_retroactively_satisfied_by_later_receipts` passes. Later executions/checks cannot make the pre-execution closure complete. |
| Exact direct-check receipt substitution | Unchanged independent `test_closure_exact_receipt_refs_must_be_accepted_in_its_prefix` passes. The old seq-32 closure cannot consume the seq-38 replacement, and its dependent remains blocked. The test retains valid initial closure and ordinary replacement-freshness controls. |
| Required member/prerequisite/ship chronology | `test_closure_needs_all_member_executions_before_its_sequence`, `test_prerequisite_increment_cannot_close_after_dependent_closure`, and `test_ship_closure_requires_increment_closures_in_its_prefix` all pass. |
| Null-command handoff receipt | `test_workflow_gate.py:553`, `test_future_handoff_receipt_cannot_replace_exact_closure_proof`, passes: corrupt old refs do not complete; dependent is blocked with no next command; later legitimate closure restores readiness and original blobs remain unchanged. |
| Transitive action/check chain | `test_workflow_gate.py:578`, `test_transitive_action_proof_must_match_closure_prefix_exactly`, passes for origin check → middle check → work → closing checks. Old closure ref substitution fails; later legitimate closure succeeds; a subsequent source edit still blocks. |
| Inherited increment proof | `test_workflow_gate.py:602`, `test_inherited_increment_receipts_cannot_be_backfilled_into_closure`, passes: a legitimate new prerequisite closure plus rerun dependent proof cannot backfill the old dependent closure. A later dependent closure succeeds. |
| Ship proof | `test_workflow_gate.py:621`, `test_ship_cannot_substitute_receipts_from_a_later_valid_reclosure`, passes: new valid increment proof cannot replace old ship refs in place; a later ship closure succeeds. |

The four new cases explicitly reverse reference ordering for legitimate
reclosures, verifying ID/hash set semantics rather than list-order coupling.
Existing closure/admission, freshness, historical-consumption and no-I/O
regressions also pass.

Limit: these are real library/persistence calls over synthetic protocol
records. Actual branch/commit/source verification and runtime close/dispatch
integration remain C2 responsibilities. No runtime CLI or actual repository
adoption is demonstrated here.

### F2 — VERIFIED-WITH-LIMITATIONS

The original zero-return-code/no-spawn reproduction remains rejected.
The honest failed-launch matrix passes for null/nonzero failure codes,
rejects successful/executed and contradictory spawn claims, and preserves
known no-spawn failure without counting it as completed work.

The no-spawn behavioral-red receipt regression passes, including its
matching spawned red positive control. Positive current-check, work and
null-command handoff paths pass; unresolved admission, direct exit alone
and bare recovery remain conservative.

The F2 correction was not changed by this iteration. This verifies
structural process/work/check-proof consistency, not authentic process
identity, actual guarded execution, live descendant termination or C2
recovery integration.

### F3 — VERIFIED

The unchanged original date-shaped naive timestamp regression passes.
The aware-UTC matrix accepts Z, explicit +00:00 and fractional UTC controls
and rejects the tested date-shaped/compact/date+Z/naive/nonzero-offset
values. Receipt start/finish and metric-generated timestamp negatives
also pass. Ordinary valid timestamped protocol records remain green.

The F3 correction was unchanged. This resolves the tested parsed-awareness
defect, not every possible datetime grammar variant.

## Original C1 sub-AC reconciliation

Verdicts are bounded to the actual C1 library and protocol tests.
Named limitations are not waivers for C2, Q/I1.T4, host experiments or review.

| ID / original criterion | r3 verdict | Evidence and retained limit |
|---|---|---|
| C1-V01 — strict schemas and one valid dependency graph | **VERIFIED-WITH-LIMITATIONS** | Strict keys/types/IDs/versions/hashes/paths/numbers, malformed proof, owned mandatory checks and UTC controls pass. Not exhaustive parser or security proof. |
| C1-V02 — atomic persistence and immutable receipt resolution | **VERIFIED-WITH-LIMITATIONS** | Sequence conflict, atomic replacement failure, receipt-before-reference, missing/changed/cyclic proof and actual fresh-process append tests pass. No C2 crash/lifetime proof. |
| C1-V03 — scoped freshness and exact prerequisite chains | **VERIFIED-WITH-LIMITATIONS** | Selective source/component/check/claim and multi-hop reopening/unaffected preservation pass. Exact closure-prefix references now pass direct, handoff, transitive, inherited and ship cases; the residual F1 block is resolved for these surfaces. Scope-selection completeness remains reviewer-owned. |
| C1-V04 — admission vs mandatory closure and earlier proof | **VERIFIED-WITH-LIMITATIONS** | Early admission remains separate from closing checks; member/prerequisite/check/ship ordering and exact-reference negatives pass, as do legitimate later closures. Git commit/source and CLI close validation remain C2. |
| C1-V05 — increment-local producer/context independence | **VERIFIED-WITH-LIMITATIONS** | Producer/recorder separation, all-implementer contexts, distinct review/verification and cross-increment positive/negative controls pass. IDs are self-declared, not authentication. |
| C1-V06 — temporal consumption vs backfill and current checks | **VERIFIED-WITH-LIMITATIONS** | Earlier consumed compatibility/red, absent legacy, backdated receipt rejection, historical source retention, changed contract rejection and current post-change checks pass. No actual guarded retirement or fresh-agent exercise. |
| C1-V07 — retained design history and research supersession | **VERIFIED-WITH-LIMITATIONS** | History/adoption mismatch, retained superseded claims, UNKNOWN/wrong-owner, selective heading and bound-source tests pass. No semantic research-truth claim. |
| C1-V08 — conservative process/handoff proof | **VERIFIED-WITH-LIMITATIONS** | F2 and unresolved/direct-exit/external/bare-recovered tests pass. Live process recovery remains unverified. |
| C1-V09 — pure materialized gate and no fabricated proof | **VERIFIED-WITH-LIMITATIONS** | I/O tripwires and repeated/deep-input equality pass; exact-prefix closure proof passes; missing/unavailable/wrong-run/low-floor/unsupported metric negatives remain green. Synthetic metric receipts are not actual quality proof or producer integration. |
| C1-V10 — bounded regression and fresh evidence | **VERIFIED-WITH-LIMITATIONS** | One 75-test workflow replay plus 10-test evidence replay, exact raw logs/argv/counts and scoped before/after hashes preserved. Separate review, whole-project suites, native/corpus, quality/mutation and host experiments were not performed. |

## Actual commands and captured results

CWD:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$p = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_workflow_*.py' -v
& $p -B scripts/run.py --idle 120 --max 1200 -- $p -B -m unittest discover -s scripts/tests -p 'test_evidence.py' -v
```

| Command | Observed result | unittest duration | Exit |
|---|---|---:|---:|
| Workflow discovery | 75 passed; no failures/errors/skips | 99.209 s | 0 |
| Evidence discovery | 10 passed; no failures/errors/skips | 5.471 s | 0 |

The tests use real library/filesystem behavior; their bounded fresh-process
scenarios ran as part of discovery. Existing inner subprocess bounds remain
idle 30/max 90. No timeout, missing dependency, empty discovery or cleanup
failure occurred. No repeated replay was attempted.

Raw output was streamed to the existing runner and stored directly from
captured bytes. `run.py` merges the inner stdout/stderr, so unittest output is
in the recorded stdout files; outer stderr files are empty. Full argv arrays,
wall durations and stream hashes are in the manifest.

Artifacts:

- `c1-independent-r3-workflow.stdout.log` / `.stderr.log`
- `c1-independent-r3-evidence.stdout.log` / `.stderr.log`
- `c1-independent-r3-manifest.json`
- `c1-independent-r3-imports.json`
- `c1-independent-r3-handoff.json`

## Dependency freshness and concurrent Q1 work

**FACT:** **1,878 files** were pinned, with identical hashes before and after
each suite and across the complete capture. All **172 observed file-backed
workflow imports** matched before/during/after. The unchanged optional import
hook in the original independent test supplied those runtime observations.
The separate evidence suite has no such hook; its test/helper/runtime inputs
were still included in the before/after census.

Scope: top-level repository Python runtime modules, workflow-discovered
tests, workflow/evidence fixtures/helpers, explicit C1 contracts/correction
inputs, and managed Python source/binary files. Unrelated measurement tests,
docs and evidence were excluded. This is **not whole-root stability**, a Q1
acceptance, or an exhaustive Windows/PowerShell/Git OS/DLL attestation.
The observations cannot detect an unobserved edit-and-revert interval or
guarantee future freshness.

`measure.py` and `measure_graph.py` differed from the implementer's old
handoff **before this replay began**, consistent with the disclosed
concurrent Q1 corrections. Their actual bytes were pinned and remained
unchanged throughout this replay. No assumption that their policy semantics
were unchanged was used to substitute for execution. Their implementation
and own quality are not reviewed or accepted by this result.

| Actual tested runtime file | SHA-256 |
|---|---|
| `scripts/workflow_gate.py` | `a703ef74ba71ad2205b7dc4d0293a6acf3a14a8dcdccda337ec9274ec924251f` |
| `scripts/workflow_state.py` | `a8069bd5f93c3d77f0e517f106d29c873df181a3ea80352b0c9224fcb6ca194b` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/measure_graph.py` | `e99d64e16fcab33bc91d94c8669d5b22b9cf3090c67df36cb507006678d137dd` |

The manifest preserves all other runtime/test hashes and the explicit
implementer-handoff comparisons. C1 production/test files matched that
handoff; original independent files remained byte-identical.

## Stop and next owner

Bounded C1 **functional verification is accepted with the limitations above**
for the tested snapshot. Obtain the separate read-only code review before
parent integration/acceptance. Preserve all earlier failing evidence.

No C2 advancement, actual quality/probe/mutation pass, host experiment,
authenticated independence, release or publication claim follows from this
verification. If the handoff recheck or later parent check detects changed
runtime dependencies, arrange one stable replay after Q1 freezes rather than
repeatedly running while a source writer is active.

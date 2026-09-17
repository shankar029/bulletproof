# Q1 review correction — pre-fix evidence and materialization decision

## Status

**Blocked before production implementation on the baseline materialization
boundary below.** This is correction round 3 / review round 1, not another
acceptance or a completed correction. All production files remain at the prior
freeze. Parent state and independent history were not edited.

## Observed reproductions

The original separate report is preserved in `q1-code-review.md`.
New owned regressions are `scripts/tests/test_measure_q1_review.py`.

- **FACT — R2 reproduced:** actual baseline bytes differ from the selected Git
  tree while the validator's status command is empty. Freshly rederived
  inventory/parse/graph/observations/manifest and the canonical committed
  changed-line map are accepted. Genuine cycles are base 0 / head 1 / fail;
  the fresh corrupt baseline gives base 1 / head 1. The assertion requiring
  baseline rejection fails because no exception is raised.
- **FACT — R1 reproduced:** real public CLI calls accept both `scripts.` and
  `scripts ` rather than rejecting them. The canonical control has one head
  cycle and a failing comparison. Full reports and native dot-alias evidence
  are saved in the new fixture evidence directory.
- The first owned test attempt incorrectly extrapolated native dot-alias
  behavior to the space alias. CPython's appended child-path lookup did not
  import the intended local cycle for that spelling. That failed assertion is
  retained as a **test-assumption failure**, not production-red proof. The
  independent report's native demonstration was for the dot alias. The test
  now preserves that exact distinction; both configuration aliases still
  reproduce the public-CLI validation defect.

## Exact execution

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
& $py -B scripts/run.py --idle 30 --max 90 -- $py -B .ai/workflow-reliability/evidence/q1-review-correction-capture.py preflight
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-review-correction-capture.py capture test_measure_q1_review.py red
& $py -B scripts/run.py --idle 120 --max 900 -- $py -B .ai/workflow-reliability/evidence/q1-review-correction-capture.py capture test_measure_q1_review.py red-final
```

| Capture | Result | Unittest duration | Exit |
| --- | --- | ---: | ---: |
| red | 2 tests, 2 failures; includes the native space-alias assumption failure | 47.900s | 1 |
| red-final | 2 tests, 3 failure records: R2 plus the two R1 subtests | 58.276s | 1 |

`q1-review-correction-*-command.json` records literal worker argv, environment,
raw stdout/stderr hashes and actual exits. The outer bound is 120/900. The
reused immutable verifier's inner raw helper retains its historical 120/1200
metadata field; it does not override the actual outer 900-second bound.
Fresh fixtures/archives are under `q1-review-correction-fixtures-*`.
Before/after runtime input records accompany both runs. Preflight checked the
322 prior owner-frozen inputs and saved all existing Q1 history plus original
verifier source hashes before creating the new regression file.

## Grounded boundary needing a decision

**FACT:** `probe._copy_subject` currently performs a normal Git clone with
`--no-checkout`, followed by ordinary detached checkout. No explicit EOL,
attributes, filter or executable-mode materialization policy is selected there.
`measure.validate_observations` checks the selected HEAD and Git status rather
than immutable-tree content. The accepted Subject contract says to preserve
bytes/modes; it does not specify whether baseline bytes are raw Git blobs or
Git's materialized checkout representation.

Those choices are observably different with legitimate EOL attributes and
checkout configuration. Blind raw-blob comparison would reject some legitimate
checkouts. Running arbitrary clean filters to compare hashes would allow an
external program to redefine the supposedly immutable baseline. Parsing Git
attributes ourselves would introduce a new, potentially incomplete attribute
interpreter outside this small correction.

**Recommended explicit policy, pending parent approval:**

1. Define the expected baseline as an isolated Git materialization of the
   selected immutable tree, using versioned repository attributes and Git's
   built-in transformations, including text/EOL rules.
2. Ignore caller index flags, local/system/global configuration and
   `.git/info/attributes` for that expected materialization. Disable ambient
   Git configuration/attributes and template injection in the private
   derivation. Do not modify the supplied source repository.
3. Reject declared external filter transformations as unsupported for Q1;
   do not execute them or let them define baseline equality. Qualify the
   exact Git commands/environment before implementing this policy.
4. Compare actual files to independently materialized expected bytes, path
   set and Git-relevant mode projection, not status/index cleanliness. POSIX
   executable bits must agree; on Windows Git's executable-bit distinction
   is not represented by ordinary worktree mode bits and must not be claimed
   as executable-mode or Q4 execution proof.
5. Use the same explicit policy for CLI baseline creation and common Context
   validation. Accept unchanged independent materializations; reject fresh
   hidden byte differences, unexpected inputs, unsupported link/submodule
   types and unsupported transformations.

**Question:** approve this isolated, versioned-attribute Git materialization
policy, or require raw Git-blob baselines instead? The recommendation supports
legitimate built-in EOL materialization without trusting arbitrary filters.
This is a source-representation/trust decision, not a private variable or
helper-name question. No new Context field is proposed unless qualification
shows the compiled policy cannot be bound by existing source/controller
identities.

R1 itself needs no new contract: reject aliased spellings at the shared
relative/absolute operational-path boundary (including existing directory
components and Windows case/short-name aliases), retaining `.` only for
directory fields. Its implementation remains queued with the approved R2
policy, so this checkpoint does not present a partial production correction
as a completed round.

## Acceptance/check plan after the decision

- R1: canonical roots preserve real local edges/cycles; aliases reject through
  public CLI and shared file/directory boundaries; dot-directory controls pass.
- R2: the persisted fresh-recollection counterexample rejects; unchanged
  independent copies pass; skip-worktree/assume-unchanged and altered index
  controls cannot change expected bytes. Real versioned EOL and mode controls
  follow the approved policy. External filters cannot erase a source change.
- Preserve F1–F3, all-nine/incomplete and corruption regressions.
- Targeted tests, then bounded Q1/legacy suites with actual dependency pins;
  self-review, final freeze, independent replay and narrowed review.

No production correction, Q1 acceptance, C1 change, Q2 advance, Q4 execution
claim, installation, agent, shared-state edit, commit or publication occurred.

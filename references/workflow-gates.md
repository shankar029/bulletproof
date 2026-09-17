# Guarded workflow CLI

`scripts/workflow.py` provides a cooperative, artifact-backed boundary around
registered commands. It supports **status, next, record, close and adopt**.
It is not yet the complete six-verb workflow: recovery is unavailable, and
successful metric attachment awaits a qualified producer bridge. Required
quality closure cannot succeed in this slice.

[Canonical skill](../SKILL.md) ·
[Workspace/resume](workspace.md) · [Planning](planning.md) · [Measurement support](quality-metrics.md)

## Invocation and authority

Use a verified Python interpreter (`$python` below) and the actual Git repository
root (`$repo`). Git must be available on that process's PATH. Set
`PYTHONDONTWRITEBYTECODE=1`; the examples use `-B`. Run external invocations through
the existing bounded runner:

The examples assume this checkout as the working directory. From an application,
use the verified installed paths for both scripts and the application's actual
Git root as `--repo`. Keep the full installed `scripts/` directory together;
the existing installers/bundle copy its imports and reporter, not just this CLI.

```powershell
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py --help
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py status --slug demo --repo $repo --target action:A-work
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py next --slug demo --repo $repo --action A-work
```

`demo`, `A-work`, `A-review-run`, and `r1` are the real owned integration fixture's
IDs, not defaults or automatically generated production records. Substitute IDs
from your reviewed contract. The inner public-CLI argument sequences are exercised
by `scripts/tests/test_workflow_cli.py`; all five verb help pages are exercised.

Every verb takes `--slug` and optional `--repo` (default `.`).
`status` optionally takes `--target KIND:ID`, defaulting to `ship:ship`.
`next` requires `--action ID`. It accepts no arbitrary command or override.
It executes exactly the registered argv, cwd, timeout bounds and environment
updates; a null environment value removes that variable.

`status` emits the existing gate's derived Readiness JSON. It does not create
proof or an optimistic secondary status. Ordinary verbs load the live
`.ai\SLUG\workflow.json`, `current-design.json`, ledger and referenced receipts.
Malformed or partially published authority is an error, not permission to run.

## Prepare and adopt reviewed artifacts

There is no permissive bootstrap generator or imported historical-green option.
Prepare the existing strict `WorkflowContract`, `CurrentDesign` and `DesignReview`
shapes before invoking adoption. Authoritative field validation is in
`scripts/workflow_state.py` (`validate_contract`, `validate_design`,
`validate_design_binding`); those Python validators enforce the record schemas.
`scripts/tests/workflow_fixtures.py` demonstrates shapes using **synthetic protocol
actors**, not actual independent approval or quality results.

For revision `r1`, stage:

| File | Content |
| --- | --- |
| `.ai\demo\design-history\r1.html` | Retained design document |
| `.ai\demo\contracts\r1.json` | Normative component definitions, hashed individually |
| `.ai\demo\design-history\r1.workflow.json` | Proposed existing-schema WorkflowContract |
| `.ai\demo\design-history\r1.current-design.json` | Proposed CurrentDesign with retained paths, hashes, review and history |
| `.ai\demo\evidence\review-r1.json` | DesignReview metadata exactly equal to the proposed pointer's review |

Candidate workflow/pointer bytes must match `evidence.write_json_atomic`
serialization: sorted keys, compact UTF-8 JSON and a final LF. Do not hand-edit
already adopted candidate bytes. Review metadata must bind the document,
component hashes and canonical workflow hash; its artifact references the
unchanged independently attributed review report. Report, disposition,
authorization and retained history bytes must exist and match their references.
An unconfirmed human approval requires explicit unattended authorization and
remains unconfirmed. The CLI does not generate approval.

Initial research, design, independent design review and planning are **procedural**:
they produce these candidates before the first adoption. They need no invented prior
admission. Thereafter, resolve the live pointer's retained revision in each phase and
delegation brief. A revised proposal is not current merely because `design.html` was edited.
Never copy candidates directly over `workflow.json` or `current-design.json`; use `adopt`.

```powershell
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py adopt --slug demo --repo $repo --revision r1 --review .ai/demo/evidence/review-r1.json
```

Initial adoption requires absent live authority and an absent or exactly empty
valid ledger. Retained execution/receipt artifacts contradict an empty basis.
Revised adoption validates the old live authority, preserves runtime-referenced
IDs and executable-versus-handoff classification, and retains the exact old
workflow/pointer bytes under their revision names. Different or partially
written immutable files are conflicts, never overwritten.

Publication is **adoption event, workflow, pointer**, followed by a normal load.
After an exception unwinds and releases this invocation's mutex, repeating the
same exact adoption may finish only the finite approved states: empty initialized
ledger, event plus old/absent authority, or event plus candidate workflow and
old/absent pointer. It never appends the same event again. An already coherent
identical candidate is acknowledged without rewriting history. Conflicting or
out-of-order publication stops. This metadata retry is not process recovery;
a process death leaving a lock blocks even adoption retry.

## Execution and returned evidence

Under its lexical lock, `next` evaluates current prerequisites and persists
admission plus launch intent **before** starting an executable. Blocked work
does not start its registered producer. Real synchronous runner observations
are appended; stdout/stderr are retained in immutable
`.ai\SLUG\evidence\runs\RUN_ID\stdout.txt` and `stderr.txt`.
The JSON result separates wrapper exit, child exit, spawn state and proof outcome.
Executed work does not mean its check passed or its increment closed.

Before-action red/compatibility proof must already be accepted, and its exact
receipt reference is consumed in the later admission. Neither a setup failure
nor a retroactively attached result is valid behavioral red.

For a null-command check, `next` returns an `awaiting-response` admission and the
registered handoff steps; it starts no child or agent. Return a complete
existing-schema Receipt with that run ID, original registered producer,
admitted inputs, exact earlier prerequisite references, timestamps and actual
artifact hashes/byte sizes. `recorded_by` is the current declared designer;
it does not replace the producer. Save the returned bytes without changing
producer attribution:

```powershell
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py next --slug demo --repo $repo --action A-review-run
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py record --slug demo --repo $repo --receipt return.json
```

Both automatic and returned receipts use the existing artifact and gate
validators. Native test/red/compatibility proof requires a registered direct
`node --test --test-reporter=...` invocation of this installation's
`scripts/native_result.mjs`; use its absolute path or file URI. Native test files
must be within the admitted file inventory. Raw stdout is preserved while the
receipt projects native absolute filenames to repository-relative paths.
A passing exit or arbitrary JSON printed by a different launcher is not proof.

Finding producers emit the existing FindingResult JSON with the registered kind,
required scenario verdicts, findings, source artifact and disposition references.
Scenario/finding evidence paths must be declared and hash-bound in the receipt.
Automatic receipts include the actual named finding artifacts. Returned handoff
evidence remains a declared independently attributed report, not cryptographic
authentication of its author.

`record` requires an actual matching admission and, for executables, actual
matching captured output and completed execution. It rechecks current source,
prerequisites and artifacts before acceptance. A rejected immutable receipt
blob may remain unreferenced; it is not authority and cannot overwrite another
receipt. Changing source or proof artifacts reopens affected checks without
rewriting old receipt bytes. Start a fresh process with `status` to inspect it.

**Metrics remain unavailable even if a command exits zero or JSON looks valid.**
Registered metric commands execute unchanged and preserve real output/failures,
but no metric receipt is accepted. The outstanding producer-owned bridge must
bind the admitted run ID, registered argv, source projection and strict raw
validation together. Qualified collectors are a separate remaining requirement.
Do not inject flags, rewrite producer UUIDs or backfill an admission.

## Closure and errors

All nine quality metrics remain required. At the accepted CLI/tool-binding boundary,
configured collectors cover the Python graph plus qualified tool-binding **smoke**
execution, not complete shared-JS/scalar/coverage/mutation collection. Qualification
of a tool is not collection of a metric. Consult [quality-metrics.md](quality-metrics.md)
and source-bound run evidence; do not treat work in progress as supported positive closure.

```powershell
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py close --slug demo --repo $repo --increment A --commit $commit
& $python -B scripts\run.py --idle 120 --max 600 -- $python -B scripts\workflow.py close --slug demo --repo $repo --ship
```

`$commit` must be the full actual current feature HEAD, not just hash-shaped text.
Closure checks actual Git tree membership, source bytes and modes against the
observed scope. Main/master/trunk and locally known remote default branches are
rejected. Missing local remote-default metadata cannot establish organization
branch protection; keep it correctly configured. Detached/unborn HEAD, dirty or
uncommitted scoped bytes, stale proof and missing mandatory review/verification/
metrics prevent closure. With metric attachment unqualified, these examples
demonstrate denial, not a positive closed event.

| Exit | Meaning |
| --- | --- |
| 0 | Ready/complete status, adoption/receipt acceptance, handoff, or successful work; inspect JSON to distinguish |
| 1 | Proof/policy refusal; also exit-zero producer with invalid or unavailable proof |
| 2 | Invalid input, path/schema/ID, Git failure, or unsupported command |
| 3 | Lock/sequence/ownership conflict or unresolved executable lifetime |
| Child code | `next` retains actual nonzero producer codes, including 124/125/127; structured output distinguishes collisions |

Launch failure records no executed child and a null child return code even when
the runner returns 127. Observer publication failure reports `[observer-error]`
and cannot create a completed event. Timeout/cleanup or unknown launch state
remains unresolved even if a later observation reports direct exit.

## Research claims and corrections

The strict claim schema is defined by `workflow_state._claim`; the source binding is
checked by `_validate_claim_files`, and `workflow_gate` evaluates attributed acceptance.
A claim's `report` is a repository-relative Markdown path plus one unambiguous heading
anchor. `claim_sha256` hashes that heading's section (including subordinate headings until
the next same/higher-level heading); source references bind whole-file hashes and valid
line numbers. Preserve exact bytes and re-anchor after source edits.

Keep scoped absence queries/exclusions and typed FACT/INFERENCE/HYPOTHESIS/UNKNOWN in the
research report. The descriptive `scope` is not an executed query or a proof of exhaustive
absence. The validator checks hashes/line ranges, not the truth of `snippet_ref` or prose.
Follow [research.md](research.md) for the human/agent evidence checks.

Corrections retain old claim IDs through `supersedes` without cycles, with a researcher
`correction_owner` and separate `acceptance_owner` attribution. A bound claim needs an
existing accepted research receipt whose producer, recorder and exact claim hash match;
its research check must still be current. Superseded claims and HYPOTHESIS/UNKNOWN cannot
permit dependent actions. Stage reviewed revisions and use ordinary adoption; do not edit
live contracts, change historical receipts or manufacture an acceptance ID. Initial
procedural research is not automatically a guarded research receipt.

## Readiness and communication

Use actual `status` for the intended action, increment or ship target after adoption and
after relevant input changes. It derives readiness from the registered graph, ledger,
resolved receipt artifacts and current source/contract/claim bindings. Report its blockers
and due/reopened checks, preserving unaffected historical evidence. An error loading live
authority is not permission to fall back to a separate status ledger.

`state.md`, plan checkboxes, chat and reports are indexes into that evidence. A ready action
can belong to a blocked increment; executed work is not an accepted check, and accepted
checks do not imply closure. Capture status with its input binding and refresh stale
observations. Before adoption, label procedural gate evidence rather than fabricate status.
See [communication.md](communication.md) and [final-report.md](final-report.md).

## Interruption and trust limits

Every mutating verb uses `.ai\SLUG\evidence\workflow.lock`. A present/orphan lock
is never stolen or deleted by the CLI. Lexical cleanup after a normal exception
is only mutex cleanup, not proof that a process tree died. Durable unresolved
admissions block later execution even if the lock is absent. `recover` is not
a supported subcommand (parser exit 2), not an always-failing recovery stub.

No PID absence/reuse, age, guard/direct-child exit, caller boolean, new worktree,
imported report or deleted lock clears unknown creation or descendant lifetime.
There is no reset API, automatic replay or positive platform recovery claim.
Preserve the workspace/evidence and escalate the unsupported lifetime case;
do not reinterpret the tests' owned process cleanup as an operator recovery path.

The source-scope hash is **not a sandbox**. Review scope completeness, including
tests, manifests, scripts and relevant added/deleted files. Do not include the
transient lock in an input scope; that is an explicit input error. Existing
exact-output exclusion restrictions are not broadened to all `.ai`.
Actors/contexts are self-declared attribution, not authenticated identities.
Registered commands and the local repository are cooperative trusted inputs.
Direct `scripts/run.py` invocation is diagnostic execution, not guarded
workflow admission. This slice makes no general model-effectiveness or complete
quality claim.

The native `evals/workflow/failures.test.mjs` entry points replay five actual CLI
failure-pair scenarios. They are not independent verification or five additional
unique implementations. The metrics pair proves denial and useful independent
work; its successful quality-closure counterpart remains blocked.

# Partial Q2 implementation handoff — native tool-input root

**Full Q2 is unfinished. No collector availability, quality pass, or independent
acceptance is claimed.** This session stops at a tested partial input-root slice;
the remaining adapters exceed the safe remaining implementation scope. Resume
implementation, not another design/workflow cycle. The parent-approved amendment
and its independent review remain byte-preserved historical documents.

## Implemented

- `scripts/measure.py`: conditional `tool_artifact_root` intake; strict relative
  Artifact and native ToolBinding checks; opaque original reads and exclusive
  byte staging; actual hash/length and regular-file identity checks; duplicate,
  case-fold, component-prefix, hardlink and generated-namespace rejection.
- Native bindings currently cover **jscpd 5.2.1 and Ruff 0.16.8 only**, anchored
  to the already-qualified help/settings/results and runtime evidence. Their
  executable and documented external PE-dependency candidates are rehashed.
  PE candidate binding is not a loaded-module/forwarder attestation.
- Identical cross-tool qualification refs share one manifest row. Originals and
  staged copies are independently checked before and after producer validation;
  the same config/original/copy/tool digest binds both revisions.
- `scripts/probe.py`: exact qualification-path reservation and input/output
  overlap checks before snapshot exclusions, staging into the owned raw root,
  and a final tool-input recheck before publication. Real completed-stage
  messages go to stderr; JSON report shape and run-ID ownership are unchanged.
- Existing `measure.validate_config(config, root)`, Context, Artifact and manifest
  shapes remain compatible. Empty Q1 mode retains its existing toolset digest.
  Existing `make_manifest` derives selected qualification refs from the Context's
  source-bound config rather than scanning its output directory.

No changes to workflow/state/gate/runner/evidence/mutation/coverage/helpers,
baseline filter/text policy, frozen/builtin resolution, or shared docs/reports.
Disjoint CLI/evaluation/guide changes remained visible and were not cancelled,
reverted, or claimed frozen by this worker.

## Actual development evidence

| Check | Observed result |
|---|---|
| Completed selected replay | **14 methods passed**, 461.432s; 10 new root methods +4 existing Q1 regression methods; no failures/errors/skips |
| Post-replay self-review correction | **2 repeated focused methods passed**, 8.379s; all-component prefix detection and explicit root-string type |
| Actual public probe | Two Git-revision fixtures, each with at least three base code files, using repository-resident and external originals; eleven exact qualification artifacts staged in each |
| Artifact/root boundaries | Real original/copy modification and deletion, rehashed forged help, changed root locator, copied executable tampering, duplicate/prefix/case collisions, hardlink and junction rejection |
| Required measurements | All nine retained; fixture graph metrics are measured by existing Q1 Python code; scalar/coverage/mutation observations remain unavailable; verdict remains incomplete/fail |
| Syntax/whitespace | Four owned Python files compile without execution/bytecode; scoped `git diff --check` exits 0 |
| Real symlink creation | **Environment blocked:** actual `os.symlink` raised WinError 1314; no privilege change, retry, mock or skip decorator |

Do not sum fourteen plus two into sixteen distinct methods. The fourteen-method
run precedes the final small correction to measure.py/test_measure_q2.py; its
eleven before/after pins matched *during that run*. The later two-method result
is focused final-byte evidence, not a full integrated rerun. Parent fresh
verification/review remains required.

Failures/timeouts are preserved in `q2-adapter-development-incidents.md` and the
session tool transcript. The first selected replay directory contains actual
fixture records from the interrupted run and **no fabricated completion result**.
The bounded successful replay prints progress only on real completed subtests.
No timeout budget was increased. Complete cleanup/death of every descendant from
earlier timeout attempts was not independently observed and is not claimed.

### Raw records

- `q2-adapter-root-development-replay-records/result.json`: actual selected method
  IDs, counts, outcomes, explicit environment-blocked case and before/after pins.
- `q2-adapter-root-development-replay-records/{repository,external}.json`: actual
  public report and graph raw records captured before fixture cleanup.
- `q2-adapter-root-correction-results.json`: actual two-method correction result.
- `q2-adapter-root-development-records/{repository,external}.json`: retained
  interrupted-run records, not a passing result.

These fixture records are not a portable live Context: temporary subjects were
cleaned up. Re-execute the persisted real tests for fresh producer validation;
do not treat archived summaries alone as valid measurement input.

## Explicit unfinished work

1. Extend native-only binding validation to qualified TypeScript/lizard/Vulture
   source roots, isolated runtime imports, resources and settings. `_qualified_inputs`
   currently **rejects** these tool IDs as unimplemented; this is not a claim
   that their prerequisite tools are unavailable or need requalification.
2. Implement `measure_js.mjs` shared syntax/symbol/static/dead-export/candidate
   producer and JS graph integration, including all six suffixes and strict
   entrypoint validation. Nonempty JS entrypoints still reject. No JS adapter
   or candidate qualification ran here.
3. Implement `measure_scalars.py`, actual jscpd/Ruff/lizard/Vulture/JS collection
   and complete census/receipts/source-derived identities. **Neither native
   analyzer was executed as a measurement collector in this slice.**
4. Extend producer RawMetricEvidence/Observation reconciliation for scalars and
   the shared JS evidence, preserving all nine metric requirements and policy.
   Current raw validation remains Q1 graph validation plus tool-input rechecks.
5. Complete ROOT01–05 across source tools and full Q2; run CHECK-SCALARS,
   CHECK-GRAPH's JS cases, CHECK-JS-PARSER and scalar CHECK-RECONCILE. Run the
   persistent symlink test in an already-capable environment, without changing
   this host's privileges or substituting a mock.

Q3/Q4, actual whole-root quality/mutations, successful guarded metric attachment,
full-suite proof, independent verification/review and publication remain deferred.
No schema/interface amendment beyond the accepted input-root extension is requested.

## Replay

Prepend the qualified Git directory to PATH and set PYTHONDONTWRITEBYTECODE=1.
Use the managed Python executable; the selected harness is progress-visible:

```text
{python} -B scripts/run.py --idle 120 --max 900 -- {python} -B -u .ai/workflow-reliability/evidence/q2-adapter-root-development.py q2-adapter-root-next-review-records
```

Use a new additive evidence directory name; existing captures cannot be overwritten.
This selects the explicitly disclosed root/Q1 checks, **not all Q2 or the full
test suite**. The symlink test remains in normal unittest discovery and fails on
this host's missing creation privilege; the harness records it as environment-
blocked, never as passed/skipped. Parent joint-freeze verification should choose
the final integrated scope, not accept this development subset as its gate.

## Final owned source hashes

| File | SHA-256 |
|---|---|
| scripts/measure.py | `c89d0894360f2990525f97f74b81b4b51b2542afb12e2c8c7c60fa251525f1db` |
| scripts/probe.py | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |
| scripts/tests/test_measure_q2.py | `8f0adaa478501bb4d1b81bb54ecdf45011d68787977537401fc4f24e563db7f8` |
| completed replay result.json | `4e637709ca407023194ad17222ff87c9a1386178ba5501df0d78f857793a42b1` |
| correction result.json | `c751a8586a457810441fe5bf5008b214e4775574693acea29d5ed20c36aaa8ff` |

Only the two production files, the directly planned Q2 test file, and additive
q2-adapter evidence changed in this implementation turn. No agents, packages,
commits or pushes. Parent owns shared state/report updates. This writer is now
idle and will make no further edits until parent feedback.

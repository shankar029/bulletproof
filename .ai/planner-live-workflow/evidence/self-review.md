# Parent self-review, procedural/unbound

Source scope: examples/team-planner diff versus c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478,
including new CSV and archive tests. No live authority/admission.

- C1: optional v2 archived state rejects nonbooleans and v1 extensions. Defaults remain
  response-only, so old snapshots do not rewrite on reads/no-op restore. Existing store and
  migration logic unchanged.
- C2: authoritative task guards run in serialized callbacks after store revision/migration
  preconditions, before allocation/field mutation. Lifecycle changes no task or dependency
  fields. One-snapshot export sorts a copy and uses existing taskView blocked semantics.
- C3/C4: headers, record/column order, quote escaping, Unicode and hostile prefix cases have
  real assertions. URL IDs are constrained before use in filenames; no query/paging truncation.
  Origin, revision, media type and JSON error boundaries retained.
- C5: coherent detail response joins existing revision checks; stale completions do not
  publish; errors fence writes. Draft revision is captured once, export never writes it.
  Found and fixed lifecycle focus occurring while its replacement button was disabled:
  now focus occurs after finally restores policy-aware control state. Download stays disabled
  during loading and its own request. Independent browser proof is still required.
- Scope: no store/rules/framework/runtime/evaluator changes. CSV adds one pure module.
  Shared DOM/form patterns reused; no lint/type suppressions or skipped native tests.
- Evidence: native baseline 37, real red 3 assertion failures, full green 46 with no skips.
  Native backend line coverage is not browser/diff coverage. Missing required probe metrics
  and guard bridge are not counted as green.
- Separate verifier found download-to-disk transport cancellation; direct HTTP attachment
  also canceled. No production fix justified from that alone; bounded supported-route
  investigation subsequently failed to save a file using ordinary click/configured destination.
  All browser flows ran; 187 passing records, five failed/blocked downloads, overall exit1.
  This is a blocked proof outcome, not a proven production download defect.
- Existing app backend mutation sample completed: 30 selected mutations, 28 assertion kills,
  2 survivors, zero ungraded; 93.33% for that bounded sample only. Survivors weaken pre-existing
  project/task capacity guards from >= to > (planner.mjs lines 72/86); schema.validate still
  rejects the over-capacity candidate before persistence. These guard lines were not changed
  by this feature (only shifted). The sample does not prove changed-line mutation or UI coverage.
  Retain survivors for independent assessment; no unsupported full-equivalence or all-mutants
  killed claim. See mutation-sample-summary.json and its raw local report.

This is not the mandatory independent final review.

## Final review-fix self-check

Independent review.md is retained unchanged. Parent dispositions: R1 (download proof) and
R2 (nine qualified metrics) remain BLOCKED. R3's user-specific interpreter path was removed;
the harness requires documented E2E_PYTHON before fixture creation. R4's exact draft guidance
is rendered beside lifecycle actions, conditionally visible and linked by aria-describedby;
the existing syncWriteControls lifecycle applies on edit, Cancel, save and coherent reload.
The independent verifier ran actual base-flow assertions: 67 checks passed, including six
guidance assertions. Missing interpreter configuration fails before fixture creation.

The harness no longer races run.py with a same-deadline parent kill/abort. Root runner owns
the command deadline and child-tree cleanup; retained active children are not removed before
observed exit. The whole browser invocation remains externally idle/max bounded.
The negative download check's label was narrowed to its actual failed wait observation,
not unsupported browser-event absence. No positive-download claim is made.

Final native after these production fixes: 46/46 and unchanged backend coverage, exit0.
Only app code/tests/docs and this task's artifacts are changed. No metric/root collector,
workflow infrastructure, store/rules rewrite, global configuration or publication.
The full independent reviewer cannot resume in sync mode; it has not approved the final
delta. Exact post-review.patch and hash binding are preserved for coordinator review.

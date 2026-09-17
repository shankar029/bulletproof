# Single bounded recovery from the first aggregate Q1 run

The first aggregate command was:

```text
<managed-python> -B scripts/run.py --idle 120 --max 1200 --
<managed-python> -B .ai/workflow-reliability/evidence/q1-resumed-correction-capture.py
capture test_measure_*.py q1-final
```

**Observed exit 124**, not success. The runner reported:

```text
[run] idle-timeout after 120s of silence — killed "C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe -B .ai/workflow-reliability/evidence/q1-resumed-correction-capture.py capture test_measure_*.py q1-final" (exit 124)
```

Before termination, the streamed transcript showed 32 `ok` records and one
`FAIL` for `InventoryTests.test_paths_reject_traversal_root_file_aliases_and_absolute_names`.
It then entered
`Q1IntegrationTests.test_public_validator_rejects_metric_comparison_revision_and_verdict_forgery`
without a terminal result. No final unittest count or traceback was emitted.
These are partial observations, **not a completed 50-test result**.

The old capture wrapper buffered raw streams until completion, so it did not
persist final raw binaries or a result/command JSON for the killed process.
The initial runtime pins remain in `q1-resumed-correction-q1-final-inputs-before.json`.
The quoted runner marker and partial test observations are a transcript record,
not fabricated byte-exact stdout/stderr artifacts.

The unchanged path regression expects a case-fold **collision** diagnostic for
two colliding source roots. The new single-path rejection ran before that
existing list check. The correction preserves the original test and restores
list-level collision checking before validating individual spellings.

The long forgery test repeatedly invokes real immutable materialization, but
unittest prints no progress between those validations. Recovery keeps the
120-second idle bound, uses Python's real `subprocess.Popen` audit events to
surface actual native-process starts (no timer heartbeat), and flushes raw
streams during capture. Actual owned temporary-directory audit events and worker
PIDs are also preserved for a future interrupted-run cleanup.

Final verification is split into two disjoint, exhaustive Q1 filename patterns:
`test_measure_[gi]*.py` and `test_measure_q1*.py`. This is one bounded recovery,
not repeated aggregate retries. Each retains idle 120/max 1200. Another timeout
is a blocker, not permission to rerun indefinitely.

Self-review refinements made before that recovery:

- Qualify and bind the packaged Git **core** and all 69 adjacent application DLLs,
  rather than treating the 46,792-byte launcher as the complete executable input.
  The direct-core qualification passed all 19 commands and sentinel controls,
  with 70 package files unchanged.
- Keep immutable mode evidence under the existing report `tools` map, with
  producer rederivation. Do not add a Context or Inventory schema field.
- Apply source-root canonical-path checks at **both** parser revision roots;
  permit an absent newly introduced directory, not an existing aliased spelling.

No surviving process is intentionally left running by the timeout; run.py kills
its process tree. The prior capture did not record its temporary fixture paths.
Consequently, interrupted private fixtures may remain; no wildcard deletion or
unproven ownership-based cleanup is attempted or claimed.

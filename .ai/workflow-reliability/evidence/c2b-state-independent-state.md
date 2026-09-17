# C2b-S independent verification checkpoint

Scope: resume approved Phase 5 only at accepted HEAD
`d971634219a633cc4401fb7dcba9685e672978aa`. No redesign, production edits,
new agents, installs, quality-suite expansion, commit or publication.
Parent owns shared state, separate review and preservation.

## Re-anchored gates

- Understand/design/plan: existing r2 contract and APPROVE reviewed in full;
  owner handoff and current state read. All 25 owner freeze pins match.
  Python stdlib unittest; actual Git/subprocess/filesystem fixtures.
- Implementation gate: owner local 61 passes, missing gate proof due to two
  buffered outer-idle failures. These remain historical failures, not assertion
  failures or passes; no old logs reconstructed.
- Transport gate PASSED: transport01 ran evidence10, exit0, 5.501s unittest;
  14 actual chunks / 1524 bytes; first chunk at 0.501s before runner exit.
  Runner PID48856 reaped, private temp empty, 29 pins unchanged. No overflow.
- Current gate: **BLOCKED**, workflow01 completed exit1. 100 methods attempted,
  42 positive methods, 58 errored methods / 98 FileNotFoundError records
  (subtests included), no assertion failure records/skips/timeouts. All errors
  concern receipt staging paths of 265/266 characters. The verifier-owned
  worktree-nested TEMP choice is the likely path-limit cause; no production
  assertion defect is established. No correction/retry was attempted.
- Evidence10 is a disjoint passing regression batch, not a separate smoke
  count to add again. Total 110 distinct methods attempted, 52 positive methods;
  this is NOT a passing aggregate.
- Workflow runner PID40976 reaped; its private temp root empty; 463 real chunks,
  228399 bytes, no cap overflow, first chunk before direct exit.
- Final reconciliation PASSED: 29/29 before/after/final pins identical across
  both batches; HEAD unchanged; former policy and materialization AST equal;
  all 75 other original definitions unchanged. These checks do not replace
  the 58-method missing regression proof.
- Handoff: `c2b-state-independent-report.md` and
  `c2b-state-independent-reconciliation.json`. Stop; parent review/preservation
  remain gated. A short private temp root needs separate parent authorization
  before any capturer correction or further execution.

## Acceptance/coverage and execution plan

1. Shared validator/default parity, strict pair including empty malformed values,
   no fallback: owner's 16 methods and existing 23 state methods.
2. Retained artifact/source/component/review/context/model/authorization/history
   policy and unchanged graph/schema: owner negatives, state/core regressions,
   exact extraction/unchanged-definitions comparison and pins.
3. Genuine A1/A2 disk publication with retained old immutable bytes AND unresolved
   old admission: one additive independent method; existing owner methods cover
   these separately but not this combined retained-basis path.
4. Pure gate stays blocked without writes/dispatch: existing pure-gate tests
   plus the new actual A1/A2 retained-basis test. Protocol actors/admissions are
   synthetic inputs, never authenticated review or lifetime/recovery proof.
5. Real progress transport: short evidence10 batch first through actual CLI
   runner and owned byte-streaming capturer. Record first bytes before direct
   exit, command, bounded raw merged output, PID, pins and private-temp remainder.
6. Then one workflow discovery batch (expected owner99 + independent1, actual
   inventory/results authoritative). No rerun of failed/timeout batches.
7. Recheck all bounded pins and publish report. Stop on real failure/drift.

Transport design: actual `python -u -B scripts/run.py --idle 120 --max 600 --
python -u -B -m unittest discover ... -v`, stdout/stderr already merged by the
CLI runner, forwarded as received by a tiny owned capturer, itself under the
same runner bounds. No run_capture buffering, shell tee/redirection, fake
heartbeat or raised timeout. Max captured output 4 MiB raw bytes; display is
the actual UTF-8 runner stream, not a binary-transparent child-stream claim.
The CLI runner is line-oriented; verbose unittest emits real test progress.
Unique batch directories refuse overwrite. TEMP/TMP/TMPDIR are privately owned
per batch; normal unittest fixture cleanup is observed, not assumed.

Historical cleanup: old PID43520 later absent per owner. First capture has no
identity; whole old trees/temp cleanup UNKNOWN. Do not inspect/kill foreign
processes or guess old temp paths. Current runs do not repair this uncertainty.

Remaining beyond this gate: separate parent code review; ordinary CLI,
publication/retry implementation, recover/migration, actual quality and release.

# C2b-S capture-layout correction, r2

Parent explicitly authorized one capture-only correction and workflow100 replay.
Original report/reconciliation/capturer/failed directories stay immutable.
No production/test edits, new agents, installs, commits, CLI or quality expansion.

- Re-anchored existing approved Phase 5 and frozen source/test pins.
- Plan: create one exclusive short OS-temp directory outside the worktree;
  pass the same TEMP/TMP/TMPDIR to a real receipt-staging preflight and, only
  after success, the one full workflow100 replay. Retain prior evidence10.
- Preflight uses existing WorkflowFixture.receipt/write_json_atomic with passive
  audit observation of actual receipt-stage bytes/path, not the shallow evidence10.
- Keep actual byte streaming, 4 MiB output cap, idle120/max600 unchanged.
- Capture named temp ownership, direct runner PID/reap, empty-root observations.
  Only remove that exact newly owned empty root after successful replay.
- Preflight PASS: actual 145-character receipt staging file contained 1586
  bytes; replacement/hash agreement and resolved receipt status valid.
  Captured child actual imports cover eight script modules plus fixture.
  Runner PID49584 reaped; no error/timeout/overflow; pins unchanged.
  Root `C:\Users\shbs\AppData\Local\Temp\bc2-etrf24pn` created by mkdtemp,
  empty and retained for the same-root workflow replay.
- Workflow replay PASS: 100/100 methods, 263.471s unittest, exit0;
  18227 bytes / 105 actual chunks, no timeout/overflow, pins unchanged.
  Direct runner PID1920 reaped. Exact owned root observed empty and removed
  with rmdir only; no recursive cleanup or parent OS-temp deletion.
- Current gate: **VERIFIED for approved C2b-S seams only**.
  Reconciliation exit0: workflow100 plus retained disjoint evidence10 = 110
  distinct accepted methods. No preflight/failed-run duplicates added.
  All49 before/after/final pins match, including original29 and old evidence.
  Validation/materialization AST equal; 75 other original definitions unchanged.
  Original failed evidence remains immutable. No production/test change in r2.
- Final handoff: `c2b-state-independent-r2-report.md` and
  `c2b-state-independent-r2-reconciliation.json`.
  Parent's separate code review is next; no preservation or CLI authorization
  is implied. Original recovery/quality/release obligations remain open.
- Old long-path failures are FACT; root-cause attribution remains INFERENCE
  until the same real receipt path succeeds under the contrasting short layout.
  That contrasting success is now FACT; it supports the long-path diagnosis
  without claiming a platform-wide OS setting/limit was inspected.
- Historical first-capture identity and old whole-tree cleanup remain UNKNOWN.
  New empty roots/direct reaps do not repair that history.

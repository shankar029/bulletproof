# Resumed Q1 correction — implementation checkpoint

Scope remains correction round 3, not a restarted workflow. Prior research,
design, baseline-boundary approval and independent findings remain authoritative.
No shared state, C1/core/guard, Q2, installation, commit or publication work.

## Facts at resumption

- Initial production bytes matched all three prior reviewed freeze hashes.
  There were no partial production edits. `q1-resumed-correction-initial-pins.json`
  captures 1,311 files before corrections, including prior reports/tests.
- Saved Git qualification is PASS; every recorded raw stdout/stderr stream
  matched its saved size/hash. No repeat of the already applicable red runs.
- R1 root cause: canonical containment did not reject lexical filesystem aliases.
- R2 root cause: status/index cleanliness did not establish immutable tree bytes.

## Implemented boundary

- Shared file/directory path acceptance rejects aliases in components, including
  Windows trailing-dot/space, existing wrong-case and short-name aliases. `.` is
  retained only for explicit directory fields.
- `measure` independently materializes selected Git trees with the qualified
  neutral environment/empty template, cached attribute inspection before
  checkout-index, and unsupported type/transform rejection.
- All baseline files (not just analyzer code) are compared exactly to independent
  expected byte hashes/path sets/types and platform-representable modes.
- CLI copying and common validation share the materializer. Supplied source,
  index/config and info attributes are not rewritten.
- Policy binds the actual qualified Git path/binary hash/version and platform
  mode projection; existing controller hashes bind the implementation. Baseline
  inventory separately records immutable tree modes, not inferred Windows bits.
  No new module or Context field; no Q4 execution claim.
- Qualification is intentionally limited to the observed Git executable build.
  Unknown builds fail explicitly pending qualification; POSIX execution is not
  claimed by this Windows run.

## Observed targeted results

- Original preserved R1/R2 owned counterexamples: 2 passed, 55.262 seconds.
- New controls first run: 5 passed / 1 error, 101.081 seconds. The positive
  sentinel control incorrectly used an already-current worktree, so Git did not
  need to smudge it. This was a test-control error, not a production failure.
  Its raw failure evidence is retained.
- Corrected control uses the private no-checkout tree, then explicitly configures
  and invokes its real driver: 6 passed, 101.695 seconds. Includes nonexecution
  assertions before capable execution, then a successful positive sentinel.
- Legacy probe: 19 passed, 59.427 seconds.
- No timeout observed in these runs. Command captures carry actual bounds
  idle 120 / max 1200. Full Q1 is next; independent replay/re-review remain due.

Only `scripts/measure.py`, `scripts/measure_graph.py`, `scripts/probe.py`, new
`scripts/tests/test_measure_q1_resumed.py` and additive owner evidence were edited.
Protected original tests and reports remain unchanged, subject to final pin check.

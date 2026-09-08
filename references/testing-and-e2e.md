# Reference: Testing & End-to-End Verification

Every unit of behavior ships with a real test. **Use the project's existing test tooling.**
Only if there is none, add the minimum the task needs, choosing the ecosystem's
lowest-friction standard option — never scaffold a framework, coverage reporter, or config
files a small task doesn't require.

Put tests where the project puts them and mirror its naming. Wire the test, coverage, and
lint commands into the project's own script/task runner so they are reproducible.

## Unit tests (Phase 4)
- Cover every new function, branch, boundary, and error path — happy path, invalid input,
  and failure modes.
- Each test must be able to fail: assert on real behavior, no empty or tautological tests,
  no skips.
- Mock only what you must (nondeterminism, external systems). Never mock away the behavior
  under test.

## Integration tests (Phase 4)
- Exercise real collaborators across module seams — storage, filesystem, transport layer,
  adjacent modules — instead of mocking everything.
- Use the project's existing fixtures and factories.
- Cover the contract between components as designed in Phase 2: data shape, ordering,
  transactions/rollback, and error propagation.

- **Coverage:** meet or exceed the repo's threshold. If none exists, cover all new branches
  meaningfully — chase behavior, not a number. A failing or flaky test is a blocker, never a
  "known issue".
- **Coverage is the floor, mutation is the bar.** A test that runs a line without asserting
  its behavior is worthless; the probe will find it (`quality-metrics.md`). Write the
  assertion you would need in order to catch the boundary being wrong.
- **Run the suite non-interactively, under an idle timeout** — `vitest run`, `--watch=false`,
  `--ci`, all wrapped: `python <skill>/scripts/run.py --idle 120 -- <test cmd>`. A watch-mode
  runner never returns and will hang the whole run; a stalled suite goes silent and `run.py`
  kills it (exit 124) instead of stealing hours. On 124, recover per the SKILL working rules.

## End-to-end verification (Phase 5)
Exercise the feature the way a real user or client would, through its real public surface,
with the system actually running. Match the depth to the surface:
- **User interface / front end** → **`agent-browser`**, per `e2e-agent-browser.md`. This is the
  designated tool for all browser work in this workflow.
- **Service or API** → issue real requests against the running service; assert status,
  response shape, headers, **and side effects** (persisted records, emitted events, files),
  including authorization failures and validation errors.
- **CLI or library** → invoke the real command or public API as a consumer would; assert
  exit codes, output, generated files, and observable side effects.

Do not stand up infrastructure the surface doesn't need — a library's end-to-end proof is a
real call to its public API, not a server or a browser.

**Map first, then fill gaps:** list the scenarios implied by the acceptance criteria, check
which already have end-to-end coverage, and add only the uncovered ones — extending the
existing suite, never creating a parallel duplicate.

These tests are committed to the repo.

## Evidence to capture
Commands run and their output, UI artifacts or request/response transcripts, and one
pass/fail line per acceptance criterion. This feeds the PR evidence bundle.

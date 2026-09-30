# Reference: Testing & End-to-End Verification

Every unit of behavior ships with a real test. **Use the project's existing test tooling.**
Only if there is none, add the minimum the task needs, choosing the ecosystem's
lowest-friction standard option — never scaffold a framework, coverage reporter, or config
files a small task doesn't require.

Put tests where the project puts them and mirror its naming. Wire the test, coverage, and
lint commands into the project's own script/task runner so they are reproducible.

## Unit tests (Phase 4)

- Cover the behavior of every new function, branch, boundary, and error path — happy path,
  invalid input, and failure modes. This does not require one test per private helper:
  exercise behavior through the narrowest stable interface that faithfully captures it.
- Each test must be able to fail: assert on real behavior, no empty or tautological tests,
  no skips.
- Mock only what you must (nondeterminism, external systems). Never mock away the behavior
  under test.

## Small test-first cycles (Phase 4)

Use the approved design and plan's test boundaries; choosing a routine test does not require
another user approval. For a new or changed behavior, write or extend one focused check, observe
it fail for the expected behavioral reason, implement the smallest complete change, and rerun it.
Then improve structure while green and repeat for the next behavior. Keep changes consistent
with the approved design; a cycle is not permission to invent a new feature or architecture.
For defects/performance regressions, use `diagnosis.md` and retain its original reproduction.

For an adopted workflow, resolve its current design and check registration first, then use
[workflow-gates.md](workflow-gates.md) for `status`/`next`/`record`. Required behavioral red
is a `before-action` check: its actual relevant assertion failure must be accepted before
the consuming implementation action is admitted. Setup/import/syntax failures do not qualify.
The admission consumes the exact earlier receipt; a later failure cannot backfill the sequence.
Green checks bind current inputs. Compatibility proof similarly precedes retirement, with
legacy coexistence observed before deletion and current checks afterward.

Direct `run.py` or test-runner invocation remains useful diagnostic/development evidence,
but it is unbound, not a guarded receipt. Initial research/design diagnostics before adoption
are procedural and remain labeled as such. Never manufacture an admission for an old run.

Avoid writing all speculative tests before any implementation. Expected results come from the
requirement, a worked example, or an independent fixture/oracle, not a reimplementation of the
same algorithm in the assertion. A syntax error, missing dependency, or broken fixture is not
the intended red signal. If a pre-change failure cannot be demonstrated, explain why in the
existing evidence record; do not claim an observed red-to-green result or waive required proof.

Prefer checks that survive internal refactors. Keep targeted unit tests for complex logic and
integration/E2E checks for real interactions. Assert calls/order when that interaction is itself
the contract, not merely today's implementation. Side-effect checks on persisted data or emitted
events remain necessary when those effects are required; a high-level return value may not prove
them. Delete an old test only after identifying its scenarios and verifying equivalent or stronger
coverage remains. Never remove tests merely because a module was merged or renamed.

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

### Enumerate scenarios from four sources, not one

Deriving scenarios only from the acceptance criteria inherits whatever Phase 1 missed: a thin AC
produces a thorough proof of a thin thing, and every gate goes green. Enumerate from all four,
and say which source each scenario came from:

1. **Each acceptance criterion** in `traceability.md` — the stated behaviour.
2. **The design's risks, edge cases & failure modes table** (§6) — every row is a claim that the
   design handles something. Each row needs a scenario that exercises it, or an explicit reason it
   cannot be exercised end to end.
3. **The as-is → to-be table's preserved behaviour** (§2b) — every contract the design said would
   *not* change is an invariant to test. This is where regressions hide.
4. **The original requirement text** — read it again after the ACs. A scenario the requirement
   implies but no AC states is a **finding**, reported to the parent, not quietly tested or
   quietly dropped.

### Cover the classes, not just the happy path

For every AC, work through this matrix. A class is either **exercised** or marked **N/A with a
reason** — never silently absent. "The happy path passes" is not verification.

| Class | What it proves | Typical shape |
| --- | --- | --- |
| **Positive / primary** | The feature does what was asked. | The stated flow, realistic inputs, asserted outcome **and** side effects. |
| **Negative / rejection** | Invalid input is refused **correctly** — right error, right status, no partial write. | Malformed, missing, wrong-type, wrong-state input. |
| **Boundary** | The edges behave. | Empty, single, max, zero, negative, overflow, unicode, duplicates, ordering. |
| **Failure / fault** | The system degrades as designed when something else breaks. | Dependency down, timeout, partial write, cancelled mid-flight, disk/quota. |
| **Authorization** | The wrong caller cannot do it. | Unauthenticated, authenticated-but-unauthorized, another tenant's data. |
| **Idempotency / repeat** | Doing it twice is safe. | Retry, duplicate submit, concurrent callers, replay. |
| **Regression** | Previously delivered behaviour still works. | The invariants from source 3, plus the existing suite. |

**Right-size honestly.** A pure-function library has no authorization class; a read-only endpoint
has no idempotency concern. N/A is legitimate — *unstated* N/A is not. Record the reason.

**A negative test must assert the specific failure**, not merely that something failed. Assert the
error type/status/message *and* that no side effect occurred: no row written, no event emitted, no
file left behind. A test that accepts any non-success is close to no test at all.

**Count and report the matrix.** The evidence bundle states, per AC, which classes were exercised
and which were N/A with their reason. A reader must be able to see what was *not* tested without
reading the test code.

These tests are committed to the repo.

## Evidence to capture

Commands run and their output, UI artifacts or request/response transcripts, one pass/fail line
per acceptance criterion, and the **scenario matrix** — per AC, which classes were exercised and
which were N/A with their reason. This feeds the PR evidence bundle.

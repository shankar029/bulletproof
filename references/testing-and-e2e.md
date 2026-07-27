# Reference: Testing & End-to-End Verification

Every unit of behavior ships with a real test. **Right-size the setup:** reuse the project's
existing test tooling; if there is none, add only what the task needs — prefer a zero-install
built-in runner (e.g. `node --test`) over scaffolding a framework + coverage + dependencies for a
small or single-file deliverable.

## Setting up test infra (only if missing)

Detect the ecosystem and install the standard runner + coverage via the repo's package manager:

| Ecosystem | Unit/Integration runner | Coverage | E2E (UI) | E2E (API) |
|---|---|---|---|---|
| Node/TS | Vitest or Jest (match repo) | built-in `--coverage` / c8 | Playwright | supertest / real HTTP |
| Python | pytest | pytest-cov | Playwright (python) | httpx / requests |
| Go | `go test` | `go test -cover` | Playwright or rod | `net/http` tests |
| Rust | `cargo test` | llvm-cov / tarpaulin | Playwright (external) | reqwest |
| Java/Kotlin | JUnit | JaCoCo | Playwright/Selenium | RestAssured |
| .NET | xUnit/NUnit | coverlet | Playwright .NET | HttpClient |

Rules:
- **Match what the repo already uses.** Only introduce a runner when there is none.
- **Don't over-scaffold.** For a micro/single-file task, or a project with no build system, a
  built-in runner (`node --test`, `go test`, `pytest`) is enough — do not `npm install` a
  framework, coverage-HTML reporter, or config files the task doesn't require.
- Put tests where the project puts them (or the ecosystem default: `__tests__`, `tests/`,
  `*_test.go`, `*.spec.ts`, etc.). Mirror existing naming.
- Wire test/coverage/lint commands into the project's scripts (e.g. `package.json`,
  `Makefile`, `pyproject.toml`) so they're reproducible and CI-ready.

## Unit + integration tests (Phase 3)

- **Unit:** every new function/branch/edge case. Cover happy path, error paths, boundaries,
  and invalid input. No test that asserts nothing.
- **Integration:** exercise real collaborators (DB, filesystem, HTTP layer, module seams) —
  not everything mocked. Use the project's fixtures/factories.
- **Coverage:** meet or exceed the repo's threshold; if none exists, cover all new branches
  meaningfully (chase behavior, not a vanity number).
- Run the suite; iterate until green. A failing/flaky test is a blocker, never a "known issue."

## End-to-end verification — act like a human (Phase 4)

Prove the feature the way a real user or client would exercise it. These tests live in the repo.

**Right-size the depth to the surface.** Use the heavy tools only where the surface calls for them:
a UI → a browser, a service → real HTTP. A pure library or CLI's end-to-end proof is a real
invocation of its public API/command — don't stand up servers, browsers, or coverage dashboards it
doesn't need.

**Map first, then fill the gaps:** list the scenarios implied by the acceptance criteria, check
which already have E2E coverage, and add tests only for the uncovered ones — extending the existing
suite/file, never creating a parallel duplicate.

### UI changes → Playwright
- Install/reuse Playwright; start (or point at) the running app.
- Script the actual user flow: navigate, fill forms, click, wait for real UI state.
- Assert on rendered/observable results, not internals.
- Capture **screenshots and traces** as evidence; save under the repo's test artifacts dir.

### API changes → real HTTP/REST
- Start the service (or use the test server) and issue real requests (test HTTP client,
  `curl`, or an httpfile/REST-client file committed to the repo).
- Assert **status codes, response schema/body, headers**, and **side effects**: DB rows
  written, events emitted, files created, idempotency, authz enforced.
- Cover auth failures, validation errors, and edge inputs — not just the happy path.

### CLI / library changes → real invocation
- Run the actual CLI command or call the public API surface as a consumer would.
- Assert exit codes, stdout/stderr, generated files, and observable side effects.

### Evidence to capture
- Commands run and their output, screenshots/traces (UI), request/response transcripts (API),
  and a one-line pass/fail per acceptance criterion. This feeds the PR evidence bundle.

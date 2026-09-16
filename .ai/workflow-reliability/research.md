# Workflow reliability — source-backed research handoff

## Snapshot, scope and status

- **FACT — inspected snapshot:** repository `shankar029/bulletproof`, worktree `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`; HEAD/base `bcc971d3b64559127dfc43eb0bfd4348c42803ca`; branch `shbs-microsoft-workflow-app-verification`. Read-only `git rev-parse HEAD` and bounded `git branch --show-current` returned these values on 2026-09-16. Initial `git status --short` showed only `?? .ai/workflow-reliability/`; the later inspection also showed `?? .ai/assets/`. Those are worktree artifacts, not part of the cited commit. No tracked implementation change was reported during research.
- **FACT — requirement authority:** [state.md](state.md):14–22 defines AC01–AC09; lines 31–36 exclude an orchestration framework/factory, authenticated-identity claims, control of bypassed commands, code-clarity rewrites, weaker benchmark thresholds, and deterministic-test claims of repeated uncoached model effectiveness. Snippets: “distinct producer roles/contexts”, “commands routed through it”, “explicit current contract”. This report covers all nine ACs, not just the Python scripts.
- **FACT — authorization:** this assignment permits only this research artifact to be written; no implementation, historical case-study edits, tests that mutate state, installation, nested delegation, main-checkout access or publication. `.ai\workflow-reliability\state.md:10–11`: “Do not retry or bypass” the publication restriction; “Preserve the completed planner case study as historical evidence.”
- **FACT — execution boundary:** no test suite, probe, mutation, diagnosis, live-agent run, installer, server, or browser was executed. Source inspection and read-only Git/version inspection are the evidence here. Node reported `v24.11.1`; the supplied managed Python successfully ran `scripts\run.py` with `-B`. Commands, tests and assertions described below were **read, not run**.
- **FACT — completion:** one research handoff is complete; it is not Gate 1 approval, a design, or an implementation proposal. The existing `state.md` is the accessible requirement record. At inspection, this task directory contained `state.md`, `.gitattributes` and `evidence`; `clarifications.md` and `traceability.md` were not present. No links to nonexistent authoritative inputs are implied.

## Summary

**FACT:** the reusable runtime consists of three Python scripts, thin Markdown host launchers, and separate Node evaluation primitives. Existing phase ownership, due-check timing, evidence freshness, and revision/resume requirements are substantial **prose contracts**, not enforced command admission. The Node live harness measures delivered-arm quality and Git hygiene, not six-phase completion.

**FACT:** `.mjs` and `.cjs` are absent from both Python extension sets; the generic mutation path grades every nonzero mutant command exit as a kill. The probe's overall pass is based on measured failures, not measurement completeness. The example's ESM mutation/diagnosis tooling already distinguishes several setup failures from assertion failures, but is separate from the generic scripts.

**INFERENCE:** existing useful seams are `run_capture`, the existing argv-based CLI convention, pure `judge`/mutation functions, Node's scorer/oracle functions, source-hashed example evidence, and the current task/check contracts. They do not amount to an existing authenticated workflow engine. Details and limits follow; this handoff selects no new design or file layout.

## Requirement coverage

| AC | Current behavior, consumers and reuse | Existing proof and bounded gap | Research status |
|---|---|---|---|
| **AC01 / P0** | **FACT:** Python discovery excludes ESM/CJS; mutation routes by root manifests or explicit command, not the native Node test inventory. Textual operators and exit-code grading are independent of file syntax. Probe invokes generic mutation as a subprocess. E01–E06. | **FACT:** Node `generateMutants` has operator unit tests and scorer integration against TS fixtures, but these do not call Python. Example ESM mutation has syntax/assertion distinctions. E12, E14, E19; S1. **UNKNOWN:** new full ESM/CJS path has not been executed. | Static causal path established; runtime reproduction intentionally deferred. |
| **AC02 / P0** | **FACT:** `judge`, `worst_status`, `unavailable`, and report `verdict` already separate some raw observations, but missing proof does not block overall pass. Diff coverage and architecture enforcement are documented beyond implemented collectors. Consumers include canonical skill, metrics/rubric/review/report references, README and architecture docs. E07–E10, E25. | **FACT:** eval null/composite behavior is independently specified and tested; it is not the probe's metric contract. E11–E13. No generic probe tests found in inspected executable/test scope. S1. | Current semantics and cross-consumer conflicts established. |
| **AC03 / P0** | **FACT:** task/check IDs, dependencies, proof owners, timing, source snapshots and intermediate due-work semantics exist in planning/workspace/review contracts. Existing metric/review JSON lacks bound gate records. E09, E15–E18. | **FACT:** source-hashed example mutation/diagnosis evidence supplies a precedent, not a reusable readiness evaluator. No such evaluator or producer/context binding found in scripts/evals/launchers/assets. E19–E20; S2. | Contract versus enforcement boundary established. |
| **AC04 / P0** | **FACT:** `run.py` launches argv and returns process status with idle/max termination; the actual launchers only instruct the host. Live pi adapter also launches commands but has no phase admission. E05–E06, E21–E23. | **FACT:** example `runNode` test checks output, exit preservation and owned PID termination, not guard admission. E19. **UNKNOWN:** host-provided identities/capabilities beyond repository wiring are not established. | Existing dispatch surfaces established; no host security guarantee inferred. |
| **AC05 / P1** | **FACT:** resume/revision contracts preserve stable IDs/unaffected evidence and reopen invalidated results. Live harness always creates a new seed workspace rather than resuming a changed prerequisite graph. E16–E17, E22. | **FACT:** live workspace test checks initial seeds and withheld oracle only; historical review explicitly distinguishes same-context re-anchoring from fresh-context resume. E14, E26. No behavioral changed-prerequisite resume test found. S2–S3. | Existing intended behavior and coverage gap established. |
| **AC06 / P1** | **FACT:** testing contract rejects setup-as-red; example diagnosis enforces assertion failures and excludes module/syntax failures, but discloses and injects its cause. V1 tests fixed arms; live v2 observes Git hygiene. E12–E14, E20–E22, E24. | **FACT:** no inspected procedural evaluator exercises missing review, stale proof, unavailable required metrics or early retirement. Existing held-out oracle convention and neutral prompt construction are reusable evaluation seams, not a held-out diagnosis experiment. E23–E24; S2–S4. | Required distinction between deterministic protocol tests and live effectiveness established. |
| **AC07 / P1** | **FACT:** one `design.html` is reread/updated; planning already says expand–migrate–contract and check callers/compatibility before removal. Canonical triggers exist for this planning advice, but not an explicit current-versus-historical design contract or bound earlier-proof retirement admission. E17–E18. | **FACT:** application migration tests assert current format/read/write/rollback/HTTP behavior, not prior independent browser-proof timing. E20, E26; S3. | Existing compatibility contract, temporal gap and consumers established. |
| **AC08 / P2** | **FACT:** research already requires typed claims, scoped absence, freshness and supersession; communication/report contracts require truthful gate status. No executable authoritative gate-state producer feeds these summaries. E18, E25; S2. | **FACT:** communication cases are explicitly illustrative, not a live run. Research parent sampling remains a procedural check. E18, E25. | Scoped corrections/status integration seam established without rewriting clarity guidance. |
| **AC09** | **FACT:** native Node/JSON/no-new-framework conventions; canonical mandatory independent per-increment verification/review; exact evidence commands and conservative limitations. Separate generic 60% mutation floor and eval 0.9 bar. E10–E14, E16, E24–E25. | **FACT:** tests/commands are catalogued below, **not executed**. Historical success counts are historical statements, not current validation. E26. | Regression boundaries and parent validation responsibilities identified. |

## Evidence: implementation and failure traces

### E01 — Python file discovery and baseline classification

**FACT:** `scripts\probe.py:26–29` defines `SKIP_DIRS` and `CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ...}` with neither `.mjs` nor `.cjs`. `code_files(root)` at lines 97–104 filters by this set and excludes dot directories. `scripts\mutate.py:35–36` duplicates the extension set without ESM/CJS.

**FACT:** `scripts\mutate.py:164–184`, `changed_lines(repo, base)`, first runs `git diff -U0 base + "...HEAD"` and only falls back to `git diff -U0 base` on command failure. Inclusion requires `os.path.splitext(current)[1].lower() in CODE_EXT`, `not is_test_path` and `not is_excluded`. `is_test_path` / `is_excluded` at lines 79–100 exclude tests, fixtures, generated/vendor/workspace paths, including `migrations`.

**INFERENCE:** an ESM/CJS-only diff cannot produce generic mutants through that filter. An ESM-heavy baseline can also be counted as having fewer than three source files, because `scripts\probe.py:415` uses `len(code_files(wt))` and lines 422–427 use `greenfield = base_code_count < 3`. This is a static causal inference, not a reproduced probe result.

**FACT:** `scripts\probe.py:399–420` leaves `base_code_count = 0` on missing merge-base or failed baseline worktree creation; the same `< 3` branch then classifies the baseline greenfield. Snippets: `merge_base = ... if rc == 0 else ""`, `base_code_count = 0`, `if rc == 0: ... base_code_count = len(code_files(wt))`.

### E02 — Mutation command detection and repository boundary

**FACT:** `scripts\mutate.py:102–111,149–161`, `TEST_COMMANDS` and `detect_test_cmd(repo)`, recognize a root `package.json` with a `scripts.test` entry and an installed `npm`, then pytest/Go/Rust/Maven/Gradle markers. Package route is `["npm", "test", "--silent"]`; there is no direct `node --test` discovery branch.

**FACT:** `scripts\mutate.py:256–298` accepts `--slug`, `--base`, `--repo`, `--test-cmd`, `--max-mutants` (20), `--timeout` (300). It normalizes `--repo` to Git's top level (`repo = top.strip()`), refuses any nonempty porcelain status, resolves explicit commands with `args.test_cmd.split()`, checks baseline exit zero, and returns 2 before report writing for dirty/no-command/red-baseline failures. `resolve(cmd)` at lines 141–147 resolves argv[0] using `shutil.which`.

**INFERENCE:** passing a nested package as `--repo` does not retain that package as test cwd after Git normalization. An explicitly quoted argument containing spaces is not faithfully represented by plain `.split()`. These are relevant routing constraints, not a prescription for new routing.

**FACT:** the inspected repository root listing has no `package.json`; contributor commands directly run Node. The actual example package, `examples\team-planner\package.json:4–11`, has `"type": "module"`, Node `>=24`, and `"test": "node scripts/check.mjs all"`. This proves an existing ESM/native route in a nested example, not automatic detection of it by the generic root-based script.

### E03 — Textual operator behavior

**FACT:** `scripts\mutate.py:40–57` orders regex operators: boundary, equality, boolean logic, word `and/or`, comparison `>`/`<`, arithmetic, booleans. `mask_strings(text)` at lines 196–206 masks quoted strings/backticks; `build_mutants(repo, targets, limit)` at lines 209–253 applies the first matching operator once per line, otherwise eligible statement deletion, then deterministic spreading. Snippets: `break # one mutant per line`, `chosen = ("statement deleted", ... "/* mutant: statement removed */\n")`.

**FACT:** `deletable(text)` at lines 69–75 requires a semicolon, excludes specified declaration prefixes, and checks balanced bracket counts. There is no parser/syntax preflight in generic mutation execution, lines 312–335.

**INFERENCE:** merely adding extensions does not establish safe ESM/CJS mutation. For example the existing unqualified `r">"` rule can select the arrow in `=>` before later arithmetic rules and produce invalid syntax. Whether a particular fixture hits this case must be verified separately.

### E04 — Generic mutation grading and artifact shape

**FACT:** `scripts\mutate.py:292–299` treats baseline `rc != 0` as “the test suite is not green”; it discards stdout/stderr and does not assert a positive executed-test count. Lines 318–325 write each mutant in place and restore the changed line in `finally`. Lines 326–335 count `rc == 124` as both a timeout and killed; **every other nonzero status** is also `killed`.

**INFERENCE:** setup, load, syntax, command-launch and max-timeout errors can inflate generic kill counts; `run_capture` can return 125/127, and these fall into `elif rc != 0`. Baseline exit zero also does not establish that relevant tests actually ran. No runtime classification experiment was authorized here.

**FACT:** `scripts\mutate.py:301–307,340–366` writes `.ai/<slug>/mutation.json`. Normal report keys include slug, abbreviated base/head, generation timestamp, joined `test_cmd`, score, killed/survived/total/timeouts, and survivor edits. The no-mutant report has `score_pct: None` and `note: "no mutable changed lines"`. Completed measurement returns 0 regardless of mutation score. No command output, producer/context identity, contract hash or per-source fingerprint is recorded in this report.

### E05 — Existing bounded process API

**FACT:** `scripts\run.py:80–140` exposes `run_capture(cmd, cwd=None, idle=300.0, max_total=0.0)` returning `(rc, stdout, stderr)`. It uses `_popen`, a fresh process group, separate stream-reader threads, an idle timer and total timer. Result codes: child status, 124 idle, 125 max or launch exception, 127 not found. Captured timeout markers are `[idle-timeout]` / `[max-timeout]`.

**FACT:** `scripts\run.py:42–77` implements `_kill_tree(proc)` with Windows `["taskkill", "/F", "/T", "/PID", str(proc.pid)]`, Unix process-group kill, and best-effort fallback. This is PID-scoped process cleanup. `run_capture` and CLI pumps at lines 101–105 and 178–185 iterate **lines** from text streams; the implementation is not a per-byte reader despite the “every byte/chunk” wording in `SKILL.md:107–110` / script docstrings.

**FACT:** CLI `main()` at `scripts\run.py:143–219` supports `--idle` (60), `--max` (0), `--label`, and remainder argv after `--`. It directly calls `subprocess.Popen(cmd, ...)`, streams output, kills on timeout and passes status through. It does not load task, check, review or metrics records before spawning.

**INFERENCE:** this is an existing bounded execution seam but not guarded workflow admission. Neither argv routing nor saved producer strings authenticate independent people/contexts or block tools that bypass a future guard. Those limitations are already explicit in task scope.

### E06 — Internal process callers and failure fallbacks

**FACT:** `scripts\probe.py:39–63` and `scripts\mutate.py:114–138` both import `run_capture` and call it with `idle = min(300.0, float(timeout))`, `max_total=float(timeout or 0)`. Both have a broad import-failure fallback to `subprocess.run(... timeout=..., shell=False)`, with their own 127/124/125 mappings. Thus not every internal execution necessarily uses the same process-tree behavior if the import fails.

**FACT:** `scripts\probe.py:66–81`, `argv(tool)`, resolves global shims or probes Python modules with the current interpreter. `m_mutation(root, skip)` at lines 227–250 tries a JSON-configured Stryker runner then mutmut with a tests directory; result parsing is text-based. It is separate from the diff-scoped engine.

**FACT:** `scripts\probe.py:289–320`, `mutation_entry(repo, slug, base, skip)`, launches `mutate.py` but ignores its return tuple, then reads an already-existing `.ai/<slug>/mutation.json` if present. It uses `data.get("score_pct")` without checking the report's head/base/generated or binding it to that invocation.

**INFERENCE:** a stale mutation report can be consumed after the current mutation command fails before writing a replacement. This is directly relevant to durable evidence freshness; it has not been executed as a reproduction.

### E07 — What the probe actually collects

**FACT:** `scripts\probe.py:274–283`, `collect(root, skip_mutation)`, returns exactly duplication_pct, complexity_max, complexity_avg, cycles, dead_exports, static_findings. Its `skip_mutation` parameter does not alter that collector. `diff_stats` at lines 253–270 computes tracked working-tree numstat versus base, unlike mutation's normal committed three-dot diff. `mutation_entry` supplies the mutation measurement separately.

**FACT:** individual collectors return `None` when missing/unparseable in many paths: `m_duplication:129–147`, `m_complexity:150–169`, `m_static:194–206`, `m_dead:209–224`. They do not carry a structured unavailable reason into the final report.

**FACT:** `m_cycles(root)` at `scripts\probe.py:172–191` calls `madge --circular --json <target>` for src/lib/app or `.`. It checks only rc 127 explicitly and parses `json.loads(out or "[]")`, without explicit extension flags. **INFERENCE:** empty output can be counted as zero cycles; actual tool-specific ESM coverage is UNKNOWN without inspecting/running the installed tool. Do not conflate Python extension discovery with externally delegated analyzer coverage.

**FACT:** `is_ui_project(root)` at `scripts\probe.py:107–125` checks selected UI dependencies in the root package and then UI suffixes among `code_files`. `main:448–451` skips mutation on detected UI unless forced, and reports it unavailable. `--skip-mutation` is also honored. UI detection and required-proof completeness are therefore distinct concerns.

### E08 — Current metric outcome semantics

**FACT:** `scripts\probe.py:342–376`, `judge(name, base, head, greenfield=False)`, returns `(None, "unavailable")` for missing head; for a nongreenfield missing base it marks a measured head `ok`. Compared metrics apply direction/tolerances; greenfield uses sanity limits. `LOWER_BETTER`, `ABSOLUTE_ZERO`, `TOLERANCE`, `GREENFIELD_LIMITS` at lines 324–339 are explicit policy constants.

**FACT:** in `scripts\probe.py:429–441,448–495`, unavailable metrics are appended and omitted from the metrics map; only measured `fail` moves `worst` to fail. Snippets: `"verdict": "fail" if worst == "fail" else "pass"` and `return 1 if report["verdict"] == "fail" else 0`. Therefore the emitted overall verdict can be pass with unavailable required measurements or all metrics absent. This is actual current code, independent of historical report observations.

**FACT:** the probe has no required-metric declaration/completeness field in its CLI (`379–387`) or output (`457–477`). Greenfield cycle limits are `(0, 1)` at line 336: one cycle warns rather than fails. This is narrower than the “no cycles” wording in `references\quality-metrics.md:127–130`; record the existing mismatch rather than silently redesigning unrelated thresholds.

### E09 — Metric/report bindings currently persisted

**FACT:** `scripts\probe.py:457–484` persists slug, requested base, shortened merge-base/head, generated time, project/baseline kinds, verdict/worst_status, metrics, unavailable and tool versions. Source content, contracts, due-check inventory, producer role/context and a current execution identity are not bound in that shape. `main:396–397` records the **short committed HEAD** while collection measures the working tree.

**INFERENCE:** a commit identifier alone cannot identify the measured dirty content or prove freshness after prerequisite changes. `references\review-and-pr.md:16–18` already warns that a committed three-dot diff cannot establish coverage of a dirty tree.

### E10 — Metric policy and documentation consumers

**FACT:** `references\quality-metrics.md:49–57` lists diff coverage and architecture rules among metrics; lines 154–157 require diff coverage above the project bar; lines 204–209 show `diff_coverage_pct` and unavailable `architecture_rules`. Neither is emitted by the implemented collector/main metric assembly (E07–E09). `SKILL.md:376–383` likewise says the probe measures diff coverage. This is a source/docs mismatch, not a measured coverage result.

**FACT:** generic mutation floor is `MUTATION_FLOOR = 60.0` (`scripts\probe.py:286`) and documented at `references\quality-metrics.md:84–87`; timeout-as-killed is documented there too. That policy differs from the independent eval's 0.9 bar (E13). The accepted task permits explicit metric/guard outcome changes, not benchmark threshold weakening.

**FACT:** `references\quality-metrics.md:188–216` documents current JSON and defines pass as nothing failing. Lines 163–175 bind rubric dimensions to metrics but allow evidence-based justification for unavailable values. `references\quality-bar.md:43–48` says “No number, no score: mark it unverified and go measure.” These consumers need to be understood together; the texts do not currently define one executable required-measurement contract.

## Evidence: existing evaluation and reuse

### E11 — Native scorer entry points are separate from the Python probe

**FACT:** `evals\lib\score.mjs:9–13` exports `parseTap(output)` returning counts, zeros if missing. `childEnv(extra)` at lines 26–31 removes `NODE_TEST_CONTEXT`; `tap` at lines 33–39 invokes `process.execPath --test --test-reporter=tap`. `runFunctional(task, projectAbs, armDirAbs, repoRoot)` at lines 41–50 sets `ARM_PATH` or `ARM_DIR` and returns pass/tests.

**FACT:** `runQuality(...)` at `evals\lib\score.mjs:60–101` uses source regexes, direct-dependency checks, optional executable extension oracle and E2E test-source regexes. `hasE2E` at lines 52–58 is `patterns.some(...)`, not an assertion that a browser/HTTP/process interaction actually ran or evidence was captured.

**FACT:** `testQualityScore(tq)` and `composite(dims, weights)` at `evals\lib\score.mjs:170–187` score absent/broken tests as zero, unmeasurable mutation as null, and renormalize weights over non-null dimensions. That model intentionally treats some dimensions as N/A; it does not consume `.ai/<slug>/metrics.json`.

### E12 — Separate textual engine, assertions and classification limits

**FACT:** `evals\lib\mutate.mjs:10–25,45–58`, `generateMutants(source, {max=16}={})`, generates deduplicated single-site textual mutations including strict `===`/`!==`. It accepts source text, not paths/extensions; it is not the Python mutation implementation. `evals\lib\mutate.test.mjs:5–40` asserts arithmetic/relational/boolean mutations, uniqueness/no-ops, bounds and avoidance of `++`, `+=`, comment terminators.

**FACT:** `runTestQuality(...)` in `evals\lib\score.mjs:108–155` opts in through `quality.mutate`, lists immediate arm `.test.` files, copies arm/shared to a temporary tree, runs a baseline and mutates up to 16 variants. It uses `tests === 0` as the setup/load skip signal and otherwise counts `fail > 0` as killed. It does not inspect assertion classification or process exit status there.

**INFERENCE:** the “compile error ≠ kill” comment is stronger than its zero-count heuristic guarantees: a runner-level failing file could emit nonzero TAP test/fail counts. Installed-Node behavior for such a case was not executed in this read-only assignment. This remains a classification risk, not a claimed reproduced bug.

**FACT:** `evals\lib\score.test.mjs:11–19` tests parsed summaries and absent-summary SyntaxError text; lines 108–125 test absent/broken/unrunnable/unmeasurable score mappings; lines 129–143 run integration against committed paginator fixtures and opt-out behavior. These tests do not cover Python discovery, command routing, durable proof or procedural phase order.

### E13 — V1 regression gate and preservation boundary

**FACT:** `evals\run.mjs:15–46` discovers `evals/tasks/<id>/task.json`, scores configured arms with the three scorer functions, and marks a bulletproof arm failed if an applicable exact dimension is below 1 or testQuality below `TQ_BAR = 0.9`. Lines 103–113 write report.md/report.json and exit 1 on regression. Null dimensions are not failures.

**FACT:** `evals\README.md:96–106` calls these “fixed artifacts (hand-authored)” and distinguishes them from live agents; `evals\run.mjs:98–100` says process adherence/guardrail policy remain outside this fixed-corpus gate. Current task inventory has ten configs: csv-stats-cli, discount-api, expr-eval, map-limit, median-backfill, order-fsm, paginator, shape-area, signup-form, uid.

**FACT:** `evals\lib\score.test.mjs:57–74` explicitly preserves composite normalization and the ignored-present-dimension-with-no-weight behavior. AC09 cannot infer generic required-metric changes should silently change these separate evaluation semantics.

### E14 — What agent harness tests actually assert

**FACT:** `evals\agent\agent.test.mjs:15–45` tests pi flags, explicit skill path, prompt neutrality and workflow invocation. Lines 49–60 create a seeded workspace and assert shared/SPEC presence and oracle absence. Lines 64–79 test statistical aggregation; lines 82–118 test conventional-commit/process booleans and the protected-branch cap.

**FACT:** these assertions contain no changed-prerequisite resume, independent-role evidence record, guarded transition, missing-review rejection or held-out diagnosis procedure. They do include filesystem-mutating workspace setup, so even this “unit tests” command was not executed during research.

## Evidence: workflow contracts, dispatch and durable state

### E15 — Existing human-review JSON is not a gate ledger

**FACT:** `assets\artifact.js:17–43` keys browser-local state by slug/document and saves verdict/note/items in localStorage. `json()` at lines 416–429 exports doc, slug, timestamp, verdict, note and anchored comments. `downloadJSON()` at lines 441–448 triggers a browser download named `review.json`; it does not write a repository gate record.

**FACT:** `references\html-theme.md:63–81,104–105` says user downloads/copies the review or replies in chat; parent resumes, handles approve/changes-requested and records dispositions. `pending` is never approval. There is no producer authentication or source/contract fingerprint in the exported shape.

### E16 — Due checks, owners and independent increments already exist as contracts

**FACT:** `references\planning.md:53–75` distinguishes increment from task, derives dependencies, detects cycles and reconciles current due scenarios/affected prior regressions while leaving future work unverified. Snippets: “Task completion is not increment completion”, “Never mark future work verified”.

**FACT:** `references\planning.md:94–121` requires stable task IDs, entry conditions, exact changes, reuse, preservation, proof, recovery/status; checks have purpose, exact execution/cwd/platform, prerequisites, pass conditions, owner/timing and evidence. Snippets: “Exit zero alone is insufficient if no relevant tests ran”; “which later action it gates”.

**FACT:** `references\workspace.md:124–135` assigns AC verdicts to the independent reviewer and records partial spanning-AC evidence. `references\delegation.md:19–24,61–67` makes research, verification and review mandatory fresh-context delegated roles. `references\review-and-pr.md:124–133` preserves returned judgments separately from parent dispositions and requires review of each increment before proceeding. These are prose obligations; S2 found no corresponding runtime evaluator.

### E17 — Resume and current design behavior

**FACT:** `references\workspace.md:16–29,81–104` calls `state.md` the resume source of truth, points to `design.html`/plan/tasks, and says reconcile when state/tree disagree. `references\planning.md:178–201` requires recording mismatches, stopping affected work, routing missing facts/design changes, preserving unaffected stable IDs, reopening invalid completion evidence, and rechecking affected gates before dispatch.

**FACT:** `SKILL.md:301–310` requires rereading `design.html` and says “update the design document (and re-check the gate)” when reality contradicts it. `references\review-and-pr.md:30–33` expects divergence “folded back into the document”. `references\design-doc.md:8–13,66–73` describes a single task design and its schemas/signatures/decisions.

**FACT (scoped absence):** the inspected canonical design/workspace/planning contracts do not define a separate explicitly current design contract bound to retained historical design revisions (S3). They do require artifact revision and source reconciliation; do not incorrectly characterize all freshness/resume guidance as absent.

### E18 — Migration, research correction and canonical triggers

**FACT:** `references\planning.md:79–88` requires expand, migrate, contract, then remove old form “only after scoped caller searches and compatibility/regression checks establish that migration is complete”; standalone increments must be green. `SKILL.md:264–266` triggers that planning procedure for wide compatibility changes. `references\production-readiness.md:36–41` additionally calls for prod-like migration/rollback/restore proof when deployment is relevant.

**FACT (scoped absence):** there is no standalone `references\migration.md` in the inspected reference inventory. Migration rules are distributed above and in design/project-profile contracts. No executable earlier-compatibility-evidence admission was found (S2–S3). Current tests after removal cannot alone establish that proof existed **before** removal.

**FACT:** `references\research.md:130–149` already requires FACT/INFERENCE/HYPOTHESIS/UNKNOWN labels, path/line/snippets, scoped negative searches, full worktree freshness, and “clearly supersede stale findings”. `SKILL.md:150–175` triggers the reference and requires parent sampling plus cross-component/not-found review. The current requirement strengthens these existing obligations; it does not begin from no scoped-research contract.

### E19 — Existing ESM command and mutation evidence precedent

**FACT:** `examples\team-planner\scripts\command.mjs:3–24`, `runNode(args,{cwd,timeout=120000}={})`, returns args/cwd/code/timedOut/stdout/stderr/durationMs; it captures bytes, uses `process.execPath`, and Windows PID-tree termination. It is a Node total-timeout helper, not `run_capture` and not a workflow gate.

**FACT:** `examples\team-planner\test\command.test.mjs:35–46` asserts a child exit 7 preserves both streams; a long child is timed out and its reported PID no longer exists. This is a concrete process-test pattern, not proof of Python runner behavior.

**FACT:** `examples\team-planner\scripts\check.mjs:5–14,24–29` selects `.test.mjs`, launches native `--test --test-timeout=30000 --test-reporter=tap`, rejects no tests/skipped/cancelled counts, and distinguishes timeout. The native runner is real, not a manifest-only assumption.

**FACT:** `examples\team-planner\scripts\mutation.mjs:18–58` copies the app under `.work`, verifies the baseline, selects `src/*.mjs`, records SHA-256 and mutation identity, runs `node --check`, and classifies `INVALID_SYNTAX`, `TIMEOUT`, `SURVIVED`, `KILLED_ASSERTION`, `ERROR_REQUIRES_REVIEW`. Snippet: `/ERR_ASSERTION/.test(result.stdout) ? 'KILLED_ASSERTION' : 'ERROR_REQUIRES_REVIEW'`. Only killed/survived grade the score, and any ungraded result makes its process exit fail. It reuses `generateMutants` without modifying shared engine/released source.

**INFERENCE:** this provides concrete conservative evidence/classification patterns, but assertion-string matching is not an authenticated proof of root cause, and this bounded backend sample is neither CJS coverage nor generic diff discovery. The old case study remains historical evidence, not implementation scope.

### E20 — Controlled diagnosis and current migration tests

**FACT:** `examples\team-planner\scripts\diagnose.mjs:12–17` expressly labels “Controlled filter-after-pagination defect; cause disclosed, not blind diagnosis”. Lines 25–35 name/check the exact injection sites; lines 36–74 compare baseline/fault/restored source, ten observations per phase, original/minimized regression tests, exclude timeouts/syntax/module failures, and check exact restoration hashes. No blind diagnosis was performed by this script.

**FACT:** `examples\team-planner\scripts\diagnosis-probes.mjs:10–31,33–49` records HTTP and direct-rule summaries, progressively removes tasks/projects and includes a page-size control. `examples\team-planner\test\diagnosis.test.mjs:6–35` constructs a done task then todo task and asserts filtered first-page identity/count. These are useful discriminating behavioral checks, not hidden causal discovery.

**FACT:** `examples\team-planner\test\migration.test.mjs:17–47` asserts v1/v2 decoding and rejection of legacy writes without byte changes. Its subsequent CLI, backup, rollback, corruption/lock and HTTP tests inspect current application behavior. No workflow readiness ledger is imported or read by this suite. It does not assert an independent compatibility review/browser result predates writer retirement.

### E21 — Actual repository orchestration surfaces

**FACT:** `launchers\claude\commands\bulletproof.md:5–11` and `launchers\pi\prompts\bulletproof.md:5–10` tell the host to load the skill and follow phases. `launchers\copilot\agents\bulletproof.agent.md:7–9,22–35` is similarly instructional, linking planning/checks and probe/review. These files implement no executable hook, factory, gate admission or role-attestation API.

**FACT:** `references\parallel-execution.md:17–35` describes isolated file-disjoint workers and serialized shared prerequisites. `docs\architecture.md:72–78` explicitly says “Check the current host's exposed capabilities”; these documents do not establish capabilities of this session's host.

**FACT:** `install.ps1:45–55` and `install.sh:61–69` copy SKILL, references, scripts and assets into the installed bundle. By contrast `evals\agent\live.mjs:25–32` stages only SKILL and references. **INFERENCE:** the live bundle does not by itself supply the skill's scripts, so a guarded-command evaluation cannot assume that existing staging already mirrors all production executable assets.

### E22 — What the live harness really verifies

**FACT:** `evals\agent\live.mjs:60–73`, `observeProcess(ws, seedBranch, seedSha)`, reads branch/commits/seed advancement and returns `scoreProcess` of four booleans. `evals\agent\process.mjs:16–21,30–31` rewards commit/branch/conventional subject and hard-zeroes a commit to the seed/default branch. There is no review, design, due-check, metrics completeness, source-freshness or producer-context inspection.

**FACT:** `evals\agent\live.mjs:99–137`, `runOnce(arm)`, prepares a new workspace, initializes/seeds Git, either copies a reference plus own tests for dry-run or invokes pi, scores an existing deliverable, optionally observes Git hygiene and deletes/retains the workspace. Dry-run sets `proc = null`. `buildPrompt` is not used in dry-run. `evals\agent\live.mjs:140–164` prints repeated-run composite statistics; it does not persist a workflow evidence transition report.

**FACT:** `evals\agent\pi.mjs:13–23` requests `-p --no-session -nc -ne -np -ns`, adding `--skill` for bulletproof. `invokePi` at lines 29–45 calls shell `spawnSync` with wall-clock timeout and returns status/time/output. No resume operation, subagent dispatch contract or child-identity attestation is implemented by this adapter.

**INFERENCE:** v2 is genuine agent-in-the-loop **production of a deliverable** when not dry-run, but not evidence that the full Bulletproof workflow passed. A new workspace per sample is not changed-prerequisite resume from durable artifacts. Documentation of prior live scores is not a current run or proof of causal effectiveness for the requested changes.

### E23 — Held-out and neutral-input conventions

**FACT:** `evals\agent\workspace.mjs:15–29`, `prepWorkspace({projectAbs,agent})`, copies `agent.seed`, writes SPEC from inline requirement or file, and returns ws/armDir. The convention is to omit oracle. It does not validate every arbitrary `agent.seed` path to guarantee no oracle could ever be copied.

**FACT:** `evals\agent\workspace.mjs:35–47`, `buildPrompt({arm,armFile})`, specifies the deliverable, explicit TS imports and arm-limited edits; the difference is the bulletproof directive. `evals\agent\agent.test.mjs:41–45,49–60` asserts neutrality and withheld oracle for its shared-only seed. This is a bounded tested seam for separating participant inputs from grader inputs, not a general sandbox.

**FACT:** `evals\tasks\paginator\task.json:4–18` labels the task `bugfix` but its live seed is only `shared`, output `arm/index.ts`, and dry-run reference is bulletproof/index.ts. **INFERENCE:** that label alone does not establish a live seeded-defect diagnosis or resume experiment.

### E24 — Oracle protocol, proof commands and conventions

**FACT:** `benchmark\projects\median-backfill\oracle\oracle.test.ts:8–32` uses `ARM_PATH` and `SUBJECT_PATH`, strips `NODE_TEST_CONTEXT`, tests correct-subject success and planted-mutant failure. It is a held-out **test-suite grader**, not a diagnosis evaluator. Its `r.status === 0` predicate does not by itself distinguish every behavioral/setup failure.

**FACT:** `CONTRIBUTING.md:11–15,31–44` requires existing unit/eval gates; lines 77–91 make SKILL canonical, phase triggers mandatory, and warn that regression checks do not establish prompt-effectiveness improvement. `evals\README.md:89–92` explains JSON is used to stay dependency-free rather than add YAML parsing. `references\code-clarity.md:14–29,95–103` preserves visible flow/useful responsibilities, explicit state/failures and no framework/size-metric gaming.

**FACT:** `references\testing-and-e2e.md:22–33` requires an observed relevant behavioral red before implementation and says “A syntax error, missing dependency, or broken fixture is not the intended red signal.” `references\diagnosis.md:20–35,59–75` requires exact reproduction context, symptom-specific failure or explicit blocker, supported cause, and rerunning the original case. These are the existing procedural contracts behind the requested setup-as-red and diagnosis evaluations.

**FACT — verified command definitions, all NOT RUN here:**

| Existing command | Definition / prerequisites | Meaning and side effects |
|---|---|---|
| `node evals\run.mjs` | `CONTRIBUTING.md:31–44`; `evals\run.mjs:15–46,103–113`; Node >=22, UI task needs benchmark Playwright setup | Fixed-corpus regression; writes eval reports and scorer scratch/workspaces. Not procedural workflow proof. |
| `node --test evals\lib\*.test.mjs evals\agent\agent.test.mjs` | `CONTRIBUTING.md:35–38` | Scoring/mutation/host adapter tests. Some tests create/delete copied workspaces; prohibited in this research assignment. |
| `node evals\agent\live.mjs --task paginator --dry-run` | `evals\agent\live.mjs:7,36–47,106–113`; `CONTRIBUTING.md:38` | Copies reference; initializes Git/workspace; no model invocation and no process adherence observation. |
| `node evals\agent\live.mjs --task paginator --arms bulletproof` | `evals\agent\live.mjs:8,115–118`; `evals\agent\pi.mjs:29–45` | External pi prerequisite; creates/mutates isolated workspace and invokes model. Not run or availability-checked. |
| `node examples\team-planner\scripts\check.mjs all` | `examples\team-planner\scripts\check.mjs:5–14`; package engines Node >=24 | Current example native tests; tests create app data and may start HTTP/children. |
| `node examples\team-planner\scripts\check.mjs coverage` | same file lines 12–13 | Coverage includes `src/**`, not full changed-line/browser coverage. |
| `node examples\team-planner\scripts\diagnose.mjs` / `mutation.mjs` | respective CLI guards at line 8 | Controlled copy/mutate/evidence exercises under app `.work`; not permitted during research. |
| managed Python `-B scripts\run.py --idle 30 --max 45 -- node --version` | `scripts\run.py:143–219` | **Executed** read-only version inspection; returned v24.11.1. Same wrapper used for branch/status/tracked-file inspections. |

**FACT:** `scripts\probe.py:409–418`, `evals\lib\score.mjs:115–153`, `evals\agent\workspace.mjs:16` and `evals\agent\live.mjs:28` create temporary/worktree state. These were read, not invoked. Existing commands' scratch policy must be reconciled with any later execution authorization; this research does not authorize temp-directory writes or changing the old case study.

### E25 — Communication, rubric and report consumers

**FACT:** `references\communication.md:26–29` says progress uses verified state, blocker reports retain cause uncertainty, completion names incomplete delivery. Lines 73–77 require consistency with evidence/current state; lines 79–90 explicitly call its cases illustrative, not real-run claims. There is no gate-state query implemented there.

**FACT:** `references\final-report.md:20–23,35–40,107–113` requires truthful gate rows, actual AC verdicts from traceability, unavailable measurements, assumptions and exact finishing commands, then a concise matching chat summary. `references\review-and-pr.md:153–157` consumes metrics and requires regeneration after changes. `SKILL.md:391–399` combines due independent verification, probe, review, report and publication state.

**FACT:** `README.md:142–157,173–185` and `docs\architecture.md:57–66` describe the probe/mutation and report chain. README's fallback “cold self re-read” at lines 173–176 contradicts current mandatory fresh-context/no-inline-review policy in `SKILL.md:357–365` and `references\delegation.md:19–24`. This is a directly relevant consumer inconsistency, not authority to weaken independence.

**INFERENCE:** these human-facing consumers currently depend on agent-maintained state/traceability/metric summaries; no inspected executable producer supplies a single authoritative readiness result (S2). AC08's requested source of truth must not be mistaken for the already-existing presentation guidance.

### E26 — Historical observations and what they do not prove

**FACT (historical record):** `.ai\workflow-app-verification\review.json:3–18` identifies an independent final review dated 2026-09-16 with its own earlier base/review snapshot. It says `qualityVerdict: "NOT-MET"`, `fullWorkflowCompliance: "NOT-VERIFIED"` and expressly describes a case study rather than an all-gates/causal-effectiveness claim.

**FACT (historical record):** `.ai\workflow-app-verification\review.json:106–115` states seven test-first cycles, missing per-slice independent gates and migration browser-before-retirement, plus bounded handoff/checkpoint observations. Lines 294–302 list historical temporal deficits including same-context re-anchoring rather than fresh-context resume and unavailable metrics.

**INFERENCE:** these observations motivate this task but cannot prove either present script correctness or a newly executed workflow scenario. Current findings E01–E25 come from reopened source, not treating old review conclusions as current implementation. No historical record was edited or retroactively upgraded.

## Gaps and search evidence

All searches below were scoped to this worktree. No Agency source, main checkout, external repositories, remote publication API or installed host implementation was inspected. Search absence is bounded by the listed scope; a naming search alone was followed by reading the actual entry points.

| ID | Search / inventory | Observed result and limit |
|---|---|---|
| **S1** | `rg 'probe\.py\|mutate\.py\|run\.py\|run_capture\|metrics\.json\|mutation\.json' evals benchmark examples -g '*.{mjs,js,cjs,ts,py,json}'`; read all three scripts and eval library/agent tests; list `scripts`/`evals` files | **FACT:** no executable references to the generic Python scripts/report paths in that scope. Scripts contain their own calls; docs/launchers reference them. No generic Python regression test found there. This does not claim no historical/manual test ever ran. |
| **S2** | `rg 'due_checks\|producer_id\|context_id\|source_hash\|contract_hash\|gate\.json\|gate_record\|guarded\|resume\|retirement\|missing.review\|stale.evidence' scripts evals launchers assets -g '*.{py,mjs,js,cjs,json,md}'`; read run.py, live/pi/process/workspace and artifact JSON export | **FACT:** only launcher prose matched resume. No durable source/contract/producer-bound readiness evaluator or guarded transition admission was found in these executable surfaces. Different possible spellings elsewhere and external hosts are not disproven. |
| **S3** | reference file inventory; `rg 'current.design\|current.contract\|design.current\|supersed\|retire\|earlier\|compatib' references\design-doc.md references\planning.md references\workspace.md references\research.md SKILL.md`; filename glob for migration/resume/workflow/probe/run/mutate tests in scripts/evals/benchmark/examples | **FACT:** generic migration guidance and supersession/resume prose exist; no standalone migration reference/current-design artifact contract found. Test-name hits were eval textual mutation and example migration. Source-read validation is E16–E20, not filename inference alone. |
| **S4** | broader `rg 'missing.?review\|setup.as.red\|stale.?evidence\|fresh.context\|resume\|retire\|migration\|diagnos\|gate'` across scripts/evals/benchmark/launchers/references/docs, followed by example diagnosis/migration reads | **FACT:** inspected evals expose fixed task scoring and Git-hygiene live scoring, not procedural negative transition/resume/retirement tests. Example diagnosis is explicitly cause-disclosed. No held-out diagnosis evaluation was found in these sources. Existing held-out acceptance/mutation oracles are not being described as absent. |
| **S5** | recursive worktree instruction-name inventory for `AGENTS.md`, `CLAUDE.md`, `copilot-instructions.md`, `*.instructions.md`, `.cursorrules`; read CONTRIBUTING/SKILL/profile and relevant references | **FACT:** no matching additional instruction file was returned. CONTRIBUTING/SKILL and the user assignment constrain this work. No claim is made about external inherited host instructions. |

## Risks, unknowns and handoff

1. **UNKNOWN — new runtime outcomes (AC01–AC06, AC09):** static failures above were not reproduced, and no changed code exists in this assignment. The next authorized verifier needs actual subprocess/fixture evidence, including wrong-reason failures, positive executed checks, stale artifacts, non-dispatched commands, and fresh-process resume. Relevant causal sources: E01–E09, E14, E16–E24. This is a validation boundary, not an unverified design API.
2. **UNKNOWN — external analyzer behavior/availability (AC02):** this pass did not install or run jscpd/lizard/madge/semgrep/knip/mutmut/Stryker. Their executable coverage cannot be inferred solely from filename support in Python or old availability logs (`scripts\probe.py:66–81,129–250`). Required missing proof must remain visibly missing.
3. **UNKNOWN — host capabilities/identity (AC03–AC06):** actual host session creation, permissions and identity verification are outside this repository. The pi adapter only demonstrates the flags/command it sends (`evals\agent\pi.mjs:13–45`), not successful installed pi execution or independent subagent attestation. A parent-host fresh-context exercise and a deterministic protocol test prove different things; neither should be relabeled as authenticated independence.
4. **FACT — intentionally unresolved design choices:** which measurements are required in which task, exact new record interfaces, transition vocabulary and migration/current-design representation belong to the next design phase. This report provides existing facts and gaps, not a speculative framework or new file-layout proposal (`references\research.md:3–6,29–40`).
5. **FACT — parent acceptance remains separate:** `references\research.md:175–189` requires reading this artifact, sampling three citations plus applicable cross-component/not-found claims, resolving design-changing unknowns and passing the handoff onward. No source changes, test passes, historical gate repairs or publication success are claimed.

**Handoff reading order:** state.md → E01–E10 (generic tooling semantics) → E15–E18/E21–E23 (durability and actual dispatch boundaries) → E11–E14/E19–E24 (existing proof and reuse) → AC table/S1–S5 → consumer E25 and historical limits E26.

**Artifact:** `.ai\workflow-reliability\research.md`. Source citations refer to the stated snapshot; the task state and artifact directories are explicitly worktree evidence. Re-anchor affected citations if the parent changes source before design or implementation.

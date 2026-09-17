# C3 canonical/documentation integration — frozen local handoff

## Outcome and authority

**FACT:** implemented only the approved C3 documentation/canonical wiring and normal CLI
regression discovery, after checkpoint `dadce66ff7d9a7494db0af5f8124009d7b132cb9`.
This resumes the existing full-tier task; it does not restart research/design, establish
human approval, adopt this task's runtime contract, or close a release gate.

Authority read: `state.md`, `research.md`, `design.html`, `design-contracts.json`,
`plan.html`/`tasks.json` I3.T1 and C-DOCS, and `continuation-plan.html` C3/AC10.
The accepted ordinary-five-verb boundary and current source supersede historical six-verb
proposals as implementation claims. Human approval remains **unconfirmed** under the user's
explicit autonomous continuation. No new material model, interface, schema or flag was needed.

The parent owns independent verification/review, shared state/report/traceability, commits
and later work. No agent/factory, install, privilege change, commit, push or publication was
performed. This handoff is the C3-owned progress/resume record; shared task records were not
edited by this worker.

## Changes and AC mapping

| Scope | Delivered | Local proof / source re-anchor |
|---|---|---|
| **AC07 — current design and canonical triggers** | SKILL resume/phase/plan/verification/review triggers resolve current-design authority after adoption; workspace/design/planning/delegation distinguish retained history from proposals. Stage immutable candidate/review, ordinary adopt publishes event → workflow → pointer. Initial procedural research/design/plan precede adoption. No direct live overwrite/backfilled approval. | `workflow.py:_adopt`, `workflow_state.py:validate_design_binding`; CLI33 adoption/failure/history tests. See final seal's current definition ranges and document headings. |
| **AC07 — temporal compatibility** | Planning/testing/review require accepted before-action compatibility and exact consumption while legacy coexists; post-retirement green is distinct. | `workflow_state.py:validate_contract`, `workflow_gate.py:_receipt`; actual compatibility CLI pair passed and replayed through native entry. |
| **AC08 — research corrections** | Research/operator guidance preserves superseded claims, scoped absence, source section/file hashes, researcher/acceptance ownership and current acceptance. Explains what validators do not establish about prose/search adequacy. | `workflow_state.py:_claim`, `_section_hash`, `_validate_claim_files`; `workflow_gate.py:claims`. This is source-grounded documentation, not a new successful claim-production workflow or newly executed core research test. |
| **AC08 — authoritative communication** | SKILL/workspace/planning/communication/review/final-report and guides derive adopted readiness from actual status, not another optimistic ledger. Distinguish ready/executed/accepted/closed and procedural pre-adoption evidence. | `workflow.py:main`, `workflow_gate.py:evaluate`; CLI33 current/stale/missing-status cases. |
| **AC10 — main overview and guides** | Preserved banner and existing feature-group layout; added feature subnavigation, operator navigation, guard/current-design/research-correction features and truthful boundaries. User/operator/architecture guidance explains installation paths, complete runtime payload, metric/recovery/host limits and historical statistics. | 15-file local link check; 12 final light/dark desktop/mobile views and three actual README navigation checks through agent-browser. |
| **Direct normal test wiring** | Added `scripts/tests/test_workflow_cli_boundaries.py`, importing only existing `CliFixture`; ports three historic genuine cases without inheriting the original 30 methods. CONTRIBUTING includes the existing native failure entry and its Python requirement, not a new CI framework. | Standard unittest discovery: 278 distinct methods, selected CLI33 passes. Native contributor inventory: 70 passing entries, **five are replays of CLI33**, not additional independent runtime features. |

Normal ports preserve the historical method names and assertions:

1. Exact registered environment set/remove/inherited values through actual child output.
2. Actual committed membership and executable-mode mismatches reject closure, without a closed event.
3. An actually pending handoff cannot be reclassified as executable by revised adoption; ledger unchanged.

Historical `joint-cli-binding-tests.py` and its custom loader
`joint-cli-binding-verify.py` remain unchanged. The port is ordinary regression integration,
not three new independent scenarios or an observed new production red/green fix.

## Proof inventory

| Artifact | Result and scope |
|---|---|
| `c3-integration-cli-tests.log` / `.json` | **33/33 passed**, 316.539s unittest time; zero failures/errors/skips. All 278 ordinary-discovered IDs and 245 unexecuted IDs are recorded. The selected pattern is `test_workflow_cli*.py`; no inherited duplicate test methods. Before/after Python source/test pins have no changes during execution. |
| `c3-integration-native.log` / `.json` | **70/70 native entries passed**, zero failures/cancellations/skips/todos; 67.490s Node duration. Includes 65 other native entries and five Python workflow replays already counted in CLI33. Native test-file pins unchanged. Experimental native TypeScript warnings are retained, not suppressed. |
| `c3-integration-r2-docs.json` | Final-byte local links for 15 files; 12 views (README/user/operator × 1280/390 × light/dark), loaded images, real theme backgrounds, no document-wide horizontal overflow, no browser errors/console messages. README feature/build-resume anchors and operator-guide navigation actually clicked. |
| `c3-integration-r2-*.png` | Final screenshots, including narrow dark feature navigation. Local marked 18.0.12 GitHub-like preview, **not github.com rendering** or general accessibility certification. |
| `c3-integration-docs.json`, earlier untagged screenshots | Earlier successful development rendering, retained. Subsequently clarified SKILL cleanup wording and removed an operator backlink to unbundled docs; final r2 supersedes affected earlier document hashes. Do not add the two runs together as more independent proof. |
| `c3-integration-seal.json` | Exact SHA-256 for every owned source and C3 evidence artifact present at seal, live definition/heading anchors, current dependency reconciliation, exact Git-blob/byte checks for historic CLI evidence, banner preservation and scoped whitespace/status checks. The seal does not recursively hash itself. |

Test helpers are additive under `evidence/c3-integration-*`; production tests use the ordinary
existing `scripts/tests` layout. Raw logs are present on disk but matched by existing Git
ignore rules; parent preservation must explicitly include them if committing the bundle.
No historic q2/cli report or `evals/report.md` was rewritten.

## Reproduction and environment

Actual working directory: this repository root. Python 3.14.2 managed interpreter:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:BULLETPROOF_PYTHON = $py
$env:PYTHONIOENCODING = 'utf-8'
```

Actual bounded development executions (helpers preserve raw records and refuse overwriting
existing result JSON/logs):

```powershell
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B .ai/workflow-reliability/evidence/c3-integration-checks.py
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B .ai/workflow-reliability/evidence/c3-integration-native.py
$env:C3_EVIDENCE_TAG = '-r2'
& $py -B scripts/run.py --idle 120 --max 1200 -- node .ai/workflow-reliability/evidence/c3-integration-docs.mjs
& $py -B scripts/run.py --idle 120 --max 300 -- $py -u -B .ai/workflow-reliability/evidence/c3-integration-seal.py
```

For a fresh independent CLI replay, use the ordinary documented discovery command, with
new owned short OS-temp storage and a separate evidence destination:

```powershell
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B -m unittest discover -s scripts/tests -p 'test_workflow_cli*.py' -v
```

Native argv expands the current `evals/lib/*.test.mjs` inventory once, then
`evals/agent/agent.test.mjs` and `evals/workflow/failures.test.mjs`; exact argv is in its JSON.
There is no `.github` CI tree in this checkout; only the existing contributor command omitted
the native failure entry. No new CI scaffold was added. Existing installer functions and
`stageSkillBundle` already copy SKILL/references/scripts/assets, and the native bundle test
passed; no installer or runtime-copy production change was needed.

Browser helper reuses the existing report helper's marked/theme/link procedure and existing
agent-browser binary. `C3_DOC_HELPERS`/`C3_AGENT_BROWSER` optionally locate those already
installed tools. No tool installation ran. Only Chromium launch/close uses the existing
Playwright library; **all page operations use agent-browser**, individually wrapped by
managed Python/run.py. Each completed browser operation and each actual test result was
streamed; there was no heartbeat or buffered-timeout retry.

Owned short temp roots were empty and removed nonrecursively after CLI/native tests.
Owned browser contexts were closed and their scratch removed. **Old timeout cleanup remains
UNKNOWN**; no unowned lock, directory or process was removed.

## Self-review, limitations and parent gate

**FACT:** final scoped whitespace checks pass; no production workflow/state/gate/runner/
measurement/native-result code or existing Python test was changed. README banner unchanged.
Self-review corrected a draft contributor reporter path before execution (the actual reporter
test is already in `evals/lib/*.test.mjs`) and removed a link that would not resolve in the
installed bundle. The final render/link pass validates the corrected bytes.

One overly broad read-only `rg` search for tool paths hit the tool's 20s limit and returned
partial output; it was not used as absence proof or retried unchanged. Existing rendering
helpers were then located from the specific historical documentation record. No test or
browser execution timed out. Early image-view attempts returned the tool's image limit;
the final narrow feature-navigation screenshot was actually viewed, and objective layout
checks cover all 12 views. No manual viewing of every screenshot is claimed.

**Still open, not promises or exemptions:**

- Successful guarded metrics need the later **producer-owned admitted ID, registered argv,
  source projection and raw-validation bridge**. Commands run unchanged; there is no accepted
  metric receipt. All nine metrics remain required. Positive quality closure is unavailable.
- Configured collection at the accepted boundary covers the **Python graph plus qualified
  tool-binding smoke**, not complete shared-JS/scalar/coverage/mutation. Q2 ownership is
  separate; concurrent work is not declared supported merely because files appear.
- No recover parser, reset, orphan-lock steal or qualified positive process recovery.
  Ordinary metadata publication retry after unwind is not process recovery.
- `test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects` remains explicitly in
  the **unexecuted inventory**, environment-unverified by the prior actual `WinError 1314`.
  It was not skipped or hidden by this worker. Old timeout cleanup remains UNKNOWN.
- Root full suite, corpus/dry-run, current root metrics/coverage/mutation, cross-platform/
  host matrix, actual fresh-agent resume/held-out diagnosis and release acceptance were
  **not** executed here. The known `evals/report.md` date delta was not touched.
- Hashes are not a sandbox; self-declared contexts are not authenticated independence.
  Historical planner 37-test/coverage and 29-feature evaluation figures remain historical.
- Human approval remains unconfirmed. Publication remains parent-owned and constrained by
  the existing recorded access blocker; no retry or workaround was attempted.

**Gate disposition:** resume/approved-design/planning authority consumed, bounded implementation
and local proof complete; independent Phase 5/6 acceptance and overall task gates remain
with the parent. Freeze the owned paths listed in the seal, jointly freeze relevant Q2 inputs,
then independently verify/review this slice. Parent reconciles source-bound AC07/08/10 evidence
into shared state/report/traceability and decides preservation. **No commit or whole-task
completion is claimed.**

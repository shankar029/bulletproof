# C3 independent Phase 5 verification

## Disposition

**VERIFIED-WITH-LIMITATIONS for the frozen C3 functional boundary.**
No blocking C3 source/documentation discrepancy was found. This is independent
functional proof, **not** Phase 6 review, complete AC01–AC10 acceptance, quality
approval, host qualification, release approval or permission to publish.

Date: 2026-09-17. Worktree:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.
Observed HEAD: `dadce66ff7d9a7494db0af5f8124009d7b132cb9`;
branch: `shbs-microsoft-workflow-app-verification`.

This verifier did not implement C3. It read the frozen handoff/seal first, then
accepted research, design/contracts, continuation C3/AC10, applicable canonical
instructions, current implementation and relevant test assertions. Historical
six-verb design proposals are not the current five-verb implementation.
No redesign, delegation, factory, tool installation, production/docs/test edits,
commit, push or host installation was performed. All new retained files use
`evidence/c3-independent-*`. The shared task state and owner artifacts were not edited.

## Per-AC independent verdicts

| AC | Verdict in C3 scope | Fresh evidence and source reconciliation | Limits |
|---|---|---|---|
| **AC07** | **VERIFIED-WITH-LIMITATIONS** | Canonical resume/design/plan/build/verification/review guidance resolves the retained current design after adoption, while initial procedural research/design/plan precede adoption. `workflow.py:425–560` validates immutable candidates and publishes adoption event → workflow → pointer; `workflow_state.py:760–809` checks retained bytes, review and history. CLI33 actually exercises adoption/idempotency, ordinary-unwind publication retry, preserved old bytes, conflicting authority, pending handoff classification and earlier exact receipt consumption. `workflow_state.py:479–482,489–493` and `workflow_gate.py:289–353` enforce before-action compatibility and legacy coexistence. | Synthetic fixture actor metadata is not human approval or authenticated independence. Metadata retry is not process recovery. No new live-host resume/held-out exercise is claimed. |
| **AC08** | **VERIFIED-WITH-LIMITATIONS** | Research/operator guidance agrees with `_claim` (`workflow_state.py:401–410`), retained supersession/cycle checks (`449–506`), Markdown section/whole-file/line bindings (`902–929`) and attributed current acceptance (`workflow_gate.py:372–397`). It explicitly does not claim validators prove prose, snippets or search adequacy. Communication/workspace/planning/review/report guidance derives runtime status instead of another ledger. `workflow.py:589–643` and `workflow_gate.py:489–546` produce actual readiness; fresh CLI cases exercise current status, stale affected proof, preserved unrelated proof and malformed/missing authority refusal. | The research-binding portion is independently source-verified documentation, not a newly executed successful claim-production or real researcher acceptance workflow. No new core research test run, producer-authentication proof or model-behavior improvement claim is made. |
| **AC10** | **VERIFIED-WITH-LIMITATIONS** | README preserves the banner, adds navigable feature groups and guides, and distinguishes procedural instructions, routed tooling and host capabilities. Fresh local link checks cover 15 C3 documents; real browser scenarios cover README/user/operator × 1280/390 × light/dark, plus three actual README navigation actions. Actual `stageSkillBundle` produces installed-layout bytes: 11 C3 skill/reference documents and their 20 local links resolve inside the bundle; nine runtime/theme files also match source bytes. Installer source agrees with the payload and documented host destinations. | Existing marked 18.0.12 GitHub-like local preview, not github.com rendering. External URLs, downloaded installers and actual host installation were not exercised. No accessibility certification or exhaustive visual review is claimed. |

**FACT:** No unsupported metric attachment, positive quality closure, process
recovery, authenticated identity, sandbox or general model-effectiveness claim
was found in the inspected C3 changes. In particular:

- `workflow.py:22–24,162–164,173–181,304–305,361–378` explicitly refuses metric
  attachment/closure; CLI tests include both nonzero and exit-zero metric producers,
  rejected returned scores and no accepted/closed event.
- `workflow.py:563–586` registers exactly five verbs, not `recover`; all verb help
  and unsupported-command cases ran in CLI33. Unknown lifetime remains blocked.
- The required policy remains nine metrics; no collector qualification is counted
  as complete metric collection. Current shared-JS/scalar/parser work is not
  promoted from proposal to supported production by this report.
- Retained planner 37-test/coverage and 29-feature observations are labeled
  historical, not this worktree's current quality dashboard.

Current definition ranges/headings and hashes are preserved in
`c3-independent-source-checks.json`; these are source observations, not extra tests.

## Fresh execution inventory — do not add replays

| Scope | Observed result | Retained evidence |
|---|---|---|
| Ordinary Python discovery | **278 distinct IDs discovered; 33 selected and passed**, 307.103s unittest duration, no failures/errors/skips. Original30 + three ported independent cases, no inherited duplicates. Remaining **245 not executed**. | `c3-independent-discovery.json`, `c3-independent-cli.json`, `c3-independent-cli.log` |
| Current native contributor inventory | **70/70 entries passed**, 64.7726607s Node duration, zero failures/cancellations/skips/todos. **Five entries replay cases already in CLI33**; not five extra runtime features. Experimental native TypeScript warnings retained. | `c3-independent-native.json`, `c3-independent-native.log` |
| Browser | **12/12 views and 3/3 navigation actions passed**; 110 agent-browser operations including close, all exit 0. No document-wide horizontal overflow, images loaded, expected theme colors, zero browser errors/console messages. | `c3-independent-docs.json`, 13 `c3-independent-*.png` screenshots, `c3-independent-browser-help.json` |
| Repository and installed-layout links | **15 documents checked locally**. Separately, **11 installed C3 documents, 20 local links**, plus nine runtime/theme byte comparisons passed. No link to an unbundled repository doc is required by the checked installed C3 links. | `c3-independent-bundle.json`, `c3-independent-docs.json` |
| Historical port integration | Three test method ASTs match retained independent cases after only hoisting the `Path` import. Existing assertions and method names preserved. Scoped whitespace check exit 0. | `c3-independent-source-checks.json`, `c3-independent-whitespace.json` |

The native mutation/reporter tests remain ordinary regression tests; their fixture
results are not a current whole-change mutation score. No owner execution result
has been relabeled as fresh proof. No aggregate count adds CLI33 to native70.

The browser helper was fully inspected before reuse. The independent wrapper pins
its owner hash and changes only output prefix, unique session/temp naming and
per-operation timeout bounds. It adds disposable installed-bundle link/byte
verification without touching a host installation. Existing Playwright is used
only to launch/close the owned Chromium context; all page operations use
agent-browser. The actual installed README/help was inspected.

The desktop-light README screenshot was successfully viewed. Earlier image-view
calls returned the tool's image-limit message; not every screenshot was visually
inspected. The 12-view layout/theme/image/error assertions are actual browser
observations, independent of screenshot viewing.

## Exact replay commands and environment

Repository root is the working directory. Actual runs used:

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH
$env:BULLETPROOF_PYTHON = $py
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'

& $py -B scripts/run.py --idle 30 --max 120 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py before
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py cli
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py native
& $py -B scripts/run.py --idle 120 --max 1800 -- node .ai/workflow-reliability/evidence/c3-independent-docs.mjs
& $py -B scripts/run.py --idle 30 --max 120 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py inspect
& $py -B scripts/run.py --idle 30 --max 120 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py after
& $py -B scripts/run.py --idle 30 --max 120 -- $py -u -B .ai/workflow-reliability/evidence/c3-independent-verify.py seal
```

The test wrappers create separate short, uniquely owned OS-temp TEMP/TMP roots,
stream actual child output and retain argv/exit/logs. Their actual child commands:

```powershell
& $py -B scripts/run.py --idle 120 --max 1800 -- $py -u -B -m unittest discover -s scripts/tests -p 'test_workflow_cli*.py' -v

& $py -B scripts/run.py --idle 120 --max 1800 -- node --test `
  evals/lib/mutate.test.mjs evals/lib/native_result.test.mjs evals/lib/score.test.mjs `
  evals/agent/agent.test.mjs evals/workflow/failures.test.mjs
```

The expanded absolute argv is in each result JSON. Native five-case replay uses
the existing `evals/workflow/helpers.mjs` inner idle120/max180 bound; no production
helper was changed. The independent outer runners use idle120/max1800.

Evidence destinations are intentionally exclusive-create. **Do not rerun into this
sealed prefix**: copy/adapt the independent helpers to a new owned prefix/tag,
including the browser prefix and every generated destination. Do not delete
failure records or old temp roots to enable a replay.

## Hash reconciliation and concurrency

**FACT:** all **217/217 before/after input pins matched**, with zero changed or
added files inside the pinned inventory. It includes C3 owned16, relevant Python
and native sources/tests, packaging/runtime/theme dependencies, accepted design
inputs, every original `c3-integration-*` artifact including the owner seal, and
seven retained historical CLI artifacts. All owner seal SHA-256 values reconciled
at entry. All seven retained Git blob IDs independently matched the checkpoint.
The final seal rechecks the 217 inputs again and hashes all independent evidence
except itself.

Key unchanged source SHA-256:

| File | SHA-256 |
|---|---|
| `scripts/workflow.py` | `a740bdc3325f86293341b7099010b8edba30062f7ddc2a2acef1012bc1b1e1a1` |
| `scripts/workflow_state.py` | `fe30290e61d319c76546c31acd454bc7c642fc83ad55126e368fa44ab4b57a6e` |
| `scripts/workflow_gate.py` | `f7ff2c1ac229a88f39be6ddc6000f060afc545dbf5dd47b5bf3ddcc4ff43f23d` |
| `scripts/tests/test_workflow_cli_boundaries.py` | `16c7cae48fb86ad47e5122abf79c592997628da51ed8cdacaecffc53858dc528` |

Full hashes: `c3-independent-before.json`, `c3-independent-after.json` and
`c3-independent-seal.json`. The README banner hash still matches the owner seal.

The full Git status acquired new **unowned, unpinned** evidence during this run:
`c3-code-review.md`, `q2-js-execution-amendment.json` and
`q2-js-execution-rationale.md`. These were not created, edited, consumed as proof
or reviewed by this verifier. They do not change the 217-file functional snapshot.
Existing shared state and `evals/report.md` deltas remain outside this verifier's
writes and are not declared globally unchanged. No concurrent production write
was observed in the pinned scope.

## Limitations and stop

- No test/browser command timed out; no retry was needed. Expected negative-path
  child failures are assertions inside passing tests, not hidden outer failures.
- Owned CLI/native temp roots were empty and removed nonrecursively
  (`c3-independent-cli-temp.json`, `c3-independent-native-temp.json`). The owned
  browser context, scratch and disposable bundle were closed/removed. **Earlier
  timeout cleanup remains UNKNOWN**; no old process/temp tree was touched.
- `test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects` remains in the
  unexecuted inventory: **environment-unverified by the retained WinError1314,
  not skipped or passed**. This run did not retry privilege-dependent creation.
  To finish that separate proof on an authorized capable environment, from
  `scripts/tests` run:
  `& $py -B ../run.py --idle 120 --max 1800 -- $py -u -B -m unittest test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects -v`.
- Root full suite/corpus/dry-run, complete current root-quality/coverage/mutation,
  fresh-host/held-out exercises, successful metric binding, parser/scalar
  collection, positive process recovery and release acceptance remain open.
  They require their separately accepted work; rerunning this bounded slice
  cannot close them.
- Human design approval remains unconfirmed. Publication remains parent-owned;
  no access retry or workaround occurred.

**Stop:** independent Phase 5 report and seal only. Parent reconciles this bounded
proof into shared task records and separately adjudicates Phase 6/release gates.

# Continuation design/plan review

## Verdict: APPROVE — bounded sequencing and implementation projection only

Reviewed 2026-09-17 at `aaec9b9851a9ce8f778943c5c088d6c4442e36f8`, feature branch
`shbs-microsoft-workflow-app-verification`. This is a design/plan review, not
implementation, runtime verification, a release verdict, or human approval.

The parent may adopt the scheduling correction and start C1 after the C0 handoff
below. I1.T4 remains **BLOCKED**. No missing metric, threshold, mandatory fresh role,
temporal requirement or final AC is waived. C1–C4 functional acceptance does not
close I1.T4, I2.T4 or I3.T3. Their outstanding quality/final obligations survive.

**Authorization supplied to this reviewer:** the parent asked whether to revise
the sequence, and the user answered: “The user is not available to respond and
will review your work later. Work autonomously and make good decisions.”
The parent chooses the recommended sequence under that authorization. This is
not evidence of human approval of the design, README UX, or metrics. Retain
`human_approval=unconfirmed`; use an attributed unattended-authorization reference
when adoption is eventually implemented. Do not manufacture a human receipt.

## Evidence and diagnosis

FACT, inspected:

- `state.md`: qualified I1 functional acceptance; separate review r2 approval;
  I1.T4 quality blocked; guard/resume/current-contract work not implemented.
  Preserve the qualified 97/98-input manifest plus separately reviewed
  `.gitattributes` hash, not a new “98 unchanged” claim.
- `design.html` and `design-contracts.json`: r2 DR1–DR7, interfaces, records,
  admission/closure distinction, lifecycle uncertainty, temporal consumption,
  scoped reopening, document bindings and separate host experiments.
- `tasks.json`: I1.T3 excludes collector implementation; I1.T4 requires C-PROBE;
  I2.T1 depends on I1.T4; I3.T1 depends on I2.T4. The current graph therefore
  blocks work on an unscheduled capability. Existing task/check IDs remain
  historical references, not evidence that their gates passed.
- `evidence/continuation-measurement-research.md`: required collection is a
  mixed-language implementation problem, not just missing installations.
  Coverage/architecture collectors and policy, complete analyzer inventories,
  classified Python mutation and syntax-aware JS candidates need their own
  bounded design. Current metrics are historical incomplete/fail, not fresh
  quality for aaec9b9.
- Actual `scripts/evidence.py`: standalone snapshot/atomic-write/lexical-lock
  mechanisms with no workflow dependency. `scripts/run.py`: current
  `run_capture(cmd, cwd=None, idle=300.0, max_total=0.0, *, env=None)` returns a
  tuple; no observer. `scripts/workflow*.py` discovery returned no files.
  `scripts/tests/helpers.py` supplies real owned Git fixtures and bounded
  `run_capture` calls. Guard names below are approved **planned** APIs.
- README and CONTRIBUTING: canonical skill/reference ownership, existing
  install/eval paths and main features; README still has over-broad introductory
  and toolchain claims. These are AC10 correction targets, not supported claims
  to repeat in new marketing prose.

INFERENCE: this is a scheduling missing-prerequisite dead end, not a code-level
cycle or a technical need to finish metrics before developing the guard.
Functional continuation is defensible only as an explicit scheduling revision.
The quality gap is real and grows to include new code; it cannot disappear
behind a successful protocol fixture.

### Input hashes (SHA-256)

| Input under `.ai/workflow-reliability/` | Hash |
|---|---|
| `state.md` | `654927be0faf9b5d6e44129aa14aa5ebdcac3644256270bd65bc27b3c23f1640` |
| `design.html` | `44d254d978c22a0be07313112295fc87ee34eb5843f3035e5ba8b52e1f3776e8` |
| `design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |
| `tasks.json` | `66cd79905ce48cc64145b1b311e132f63ddd7a6d6e9cc3b42eaade84185a43b7` |
| `evidence/continuation-measurement-research.md` | `6b83d0a65aa4bf690345db1c543ec0420ccd463aed44a4beb9570d221ea70fdb` |

The research note was already untracked on entry. This review does not own it.
Source citations here are file/symbol scoped at the above HEAD, not republished
old line numbers as fresh implementation evidence.

## Scheduling correction and ownership

This addendum alone replaces the **implementation-dispatch** dependencies
I1.T4 → I2.T1 and I2.T4 → I3.T1 with the functional acceptance boundaries below.
It does not rewrite historical files or change quality closure semantics.
`continuation-plan.html` is the overview; this review owns continuation task
detail. Existing `tasks.json` owns the referenced command/check definitions until
the parent registers an accepted executable workflow revision.

### C0 — parent acceptance and handoff, before any production edit

Parent owns the next state/traceability entry (not this bounded reviewer):

1. Record the authorization, this APPROVE verdict, exact sequencing delta,
   input hashes, AC10 and explicit outstanding I1.T4/release blockers.
2. Recheck source/contracts against accepted I1 functional evidence. Reopen
   affected verification if changed; do not relabel an archived probe as fresh.
3. Assign a single production implementer per slice, fresh verifier, and
   different fresh read-only reviewer. Parent accepts/disposes, never edits
   another role's raw findings into approval.
4. Walk C1 inputs/checks from artifacts alone. If the old edge is still treated
   as controlling dispatch, return REVISE; do not simply ignore it.

When the real guard is adopted, `workflow.json` alone owns runtime forward edges
and registered argv. Reflect this accepted scheduling revision explicitly:
continuation actions depend on appropriate functional check/action evidence,
not a fabricated closed I1 prerequisite increment. Retain all mandatory
verification/review/metrics checks on each closure and include every closure
in ship. No waiver target, skip flag, alternate optimistic status or second
mutable graph. Adoption is present-time only: historical I1 reviews can
establish the parent's implementation-readiness decision, not retrospective
guard admissions, red/compatibility chronology or metrics receipts. Re-run
required checks under actual admission when guarded proof is needed.

### C1 — persisted state and pure decisions (I2.T1 scope)

**Owner:** one guard implementer. **Predecessor:** C0.

Exclusive write set:
`scripts/workflow_state.py`, `scripts/workflow_gate.py`,
`scripts/tests/test_workflow_state.py`, `scripts/tests/test_workflow_gate.py`.
Shared helper changes require parent serialization; no unilateral `evidence.py`
API change. Native measurement modules remain independent.

Build in this order:

1. Strict record/path/hash validation and current-design/history bindings;
   immutable artifacts, atomic ledger and expected sequence.
2. Pure `evaluate(contract, ledger, inputs, target) -> Readiness`: action
   admission versus closure, due/future, independence, receipt freshness and
   reverse dependency reopening from the single graph.
3. Temporal before-action consumption and research supersession semantics.
   Preserve unrelated receipt IDs/bytes and historical consumed proof.

Use the accepted `load_workspace(root, slug)`, `bind_inputs(root, contract,
target)` and `append_event(workspace, event, expected_seq)` responsibilities.
No runtime DSL, framework, new authentication or external host service.
Local checks and then independent C1 verification/review are required before
C2. C1 is deliberately a small internal slice, not a claimed runnable CLI.

### C2 — actual guarded execution and failure/resume proof (I2.T2/T3)

**Owner:** one guard implementer, next bounded increment.
**Predecessor:** accepted C1 functional verification and separate review.

Exclusive write set:
`scripts/workflow.py`, `scripts/run.py`, `scripts/tests/test_run.py`,
`scripts/tests/test_workflow_cli.py`, `evals/workflow/failures.test.mjs`,
`evals/workflow/helpers.mjs`, `references/workflow-gates.md`.
Earlier state/gate files may be corrected only with affected C1 proof reopened.

Build order: observer seam and tests → visible CLI admission/record flow →
all six verbs → real crash/lock/no-spawn cases → five negative/positive
failure pairs → artifact-only fresh-process resume → operator guide.
If this no longer fits one context, stop after a coherent tested sub-slice and
obtain fresh verification/review before the next; do not compact a large
unverified guard into a claimed complete increment.

Approved public seam:
`run_capture(cmd, cwd=None, idle=300.0, max_total=0.0, *, env=None, observe=None)`
retains `(rc, stdout, stderr)`. Observer receives actual `launch-failed`,
`spawned`, `direct-exited` facts; missing creation identity is explicitly null.
`workflow.py main(argv=None)` exposes status, next, record, close, adopt, recover
using exactly `design-contracts.json.cli.workflow`, not new options.

**Mandatory seam check before dispatch integration:** `exclusive_lock` currently
unlinks in `finally`, including exception exit. A lexical mutex is not durable
process-lifetime proof. Validate unresolved ledger state even if no mutex file
remains; retain the admitted ownership/run/token evidence required by recovery.
Do not change standalone measurement lock semantics to make guard recovery work.
The implementer must demonstrate this with a real observer-persistence failure,
guard death and a subsequent public `next`. If retained ownership cannot be
represented by the accepted records without a new schema/API, stop for a bounded
design amendment before coding that change, rather than inventing one here.

No-spawn on block; synchronous persisted intent before Popen; callback persistence
failure attempts only owned best-effort cleanup and never issues success.
Direct child exit/root absence/old lock/dead guard cannot prove descendant death.
Unsupported termination evidence remains `RECOVERY_UNVERIFIED`, exit 3, no replay.
Do not invent a Windows process-tree identity or reset API to make a positive pass.

### C3 — canonical integration and AC10 documentation

**Canonical owner:** one document integrator.
**Predecessor for final integration:** accepted C2 functional verification/review.
Write set: `SKILL.md`, `references/planning.md`, `workspace.md`,
`review-and-pr.md`, `delegation.md`, `testing-and-e2e.md`, `design-doc.md`,
`research.md`, `communication.md`, `final-report.md` (all names after the first
are under `references/`). Integrator also owns any necessary reconciliation in
`references/workflow-gates.md`, `references/quality-metrics.md`,
`references/quality-bar.md`, `docs/architecture.md`, `evals/README.md`.
Do not concurrently edit C2's operator guide.

Wire current-design resolution at actual design/planning/resume/delegation
consumers; before-action red and compatibility before retirement; scoped claims
and explicit supersedes/correction/acceptance owners; status/messages/reports
derived from Readiness. Direct `run.py` remains diagnostic and unbound.
Fixed procedural source assertions alone are not evidence of an agent following
these branches: C4 supplies the actual fresh-context exercise.

`evals/agent/live.mjs` and `evals/agent/agent.test.mjs` are conditional
**integrator-owned** changes only if actual harness guard invocation requires
scripts/assets staging. Inspect that path first; otherwise record N/A and
leave unchanged. No host adapter or unrelated scratch rewrite.

**AC10 document owner:** one file-disjoint README/user-guide writer, who may
draft during C1/C2, but may not claim proposed guard behavior is available.
Exclusive write set: `README.md`, proposed `docs/user-guide.md`. The canonical
operator guide is `references/workflow-gates.md`, not a duplicate new protocol.
Final reconciliation waits for C2/C3 interfaces and their actual help.

### AC10 acceptance contract

An attractive, accurate README covering all main features, with working links
to user and operator guides:

- Clear, restrained value proposition, concise quick start, contents/navigation,
  grouped feature overview, evidence and limitations, contribution/license links.
  Native Markdown rather than a dashboard, ornamental dependency, or unsupported
  status badges. Judge scanability on both wide and narrow rendered views.
- Feature-to-source checklist covers: six phases and right-sizing; grounded
  research; diagnosis and test-first execution; program design and UX/human or
  explicit unattended gates; session-sized planning; durable workspace/resume;
  code clarity; focused communication; real E2E by surface; deterministic quality
  versus completeness; classified diff mutation; independent research/verifier/
  reviewer roles; evidence-bound scorecard/final report; HTML review controls;
  app-scale/production guidance; file-disjoint parallel work; installers/launchers;
  fixed-corpus versus agent-loop evaluation; and new guarded admission/recovery,
  current-design history, temporal compatibility and scoped research corrections.
- User guide: choosing an entry point, providing requirements, reading/reviewing
  artifacts, approvals/unattended policy, resume and interpreting partial results.
  Operator guide: registration/adoption, exact verbs, receipt/role provenance,
  failed/stale/blocked checks, recovery evidence and quality/host limitations.
  README links authoritative guidance rather than maintaining a second protocol.
- Label **procedural skill contract**, **executable tooling**, **host capability**
  and **not yet available/unverified** distinctly. CLI routing is not a sandbox;
  self-declared context is not authenticated independence; `next` does not spawn
  an agent; fixed fixtures/dry-run are not held-out live efficacy proof.
- Reconcile installation/version examples with actual install/help sources at
  execution; no installs required for this review. Do not claim installing
  diff-cover creates a coverage collector, all languages are mutation-supported,
  Node 22 was tested here, or missing metrics permit a successful quality gate.
- Reviewer maps each feature to its canonical source or passing runtime evidence,
  checks local links/anchors, inspects rendering and performs safe documented CLI
  invocations on owned fixtures. Reject stale headings/layout omissions as well
  as factual exaggeration. Human aesthetic approval remains unconfirmed.

### C4 — actual host exercises, then independent reconciliation

**Owners:** parent dispatches; fresh participant acts; independent evaluator
owns oracle/grading; final verifier and distinct reviewer reconcile all evidence.
**Predecessor:** C3 functional acceptance including document review.

Reuse C-HOST-RESUME and C-HOST-DIAGNOSIS exactly. Resume receives only workspace
path and neutral instruction, not changed-ID hints or prior reasoning; evaluator
checks first status, affected/unaffected receipt sets and no blocked dispatch.
Diagnosis instructions are frozen before selecting a new defect, with neutral
seed/history and withheld cause/oracle outside participant inputs. Grade original
and minimized symptom plus regression assertions only after completion.
Capture actual host calls, input hashes, transcripts and available access records.
Shared storage is not isolation. Exposure or insufficient records leaves
blindness not-verified; missing host capability remains blocked. Neither check
may be replaced with a subprocess, self-resume after compaction or fixed fixture.

No host exercises, agents or new installations are authorized by this *review*
assignment. These are later parent-owned execution tasks.

## Checks

### Exact expansion, not a new command authority

Reuse literal `tasks.json.commands` argv, idle/max values and environment; old
`availability=PLANNED` labels are historical, not proof a new file exists now.
For every referenced command run in the repository root:

```text
P = C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe
N = C:\Program Files\nodejs\node.exe
[P, "-B", "scripts/run.py", "--idle", str(idle), "--max", str(max), "--"] + argv
```

Apply `PYTHONDONTWRITEBYTECODE=1`, unset `NODE_TEST_CONTEXT`, and set
`BP_TEST_PYTHON=P` for the planned Node fixture helper. No shell splitting or
unexpanded file globs. All tests non-interactive. Preserve expanded argv/cwd,
runtime version, bounds, output/exit, test inventory, assertion identity,
source/contract/artifact hashes and actual producer context.

| Boundary | Due functional commands / checks | Bounds (idle/max seconds) |
|---|---|---|
| C1 local | CMD-WORKFLOW-PY → C-STATE-GATE; CMD-EVIDENCE | 120/900; 60/180 |
| C2 local | CMD-WORKFLOW-PY, CMD-RUN, CMD-WORKFLOW-NODE → C-CLI/C-WORKFLOW-EVAL | 120/900; 60/240; 120/900 |
| Every integrated runtime slice | CMD-ALL-PY, CMD-NATIVE-BASE, CMD-NATIVE-RESULT, CMD-EVAL, CMD-DRY-RUN, CMD-DIFF-CHECK | 120/1800; 120/600; 120/600; 120/1200; 120/600; 30/45 |
| C3 | C-DOCS plus AC10 checklist, CMD-DIFF-CHECK; same integrated regression set after integration | As above |
| C4 | C-HOST-RESUME, C-HOST-DIAGNOSIS and final integrated regression set | 900 per participant using actual supported host control; grader 30/120 |
| Quality observation, frozen inputs only | CMD-PROBE → C-PROBE | 120/1800 |

Exact existing Python discovery patterns are `test_workflow_*.py` and
`test_run.py` under `scripts/tests`; the former must discover a positive inventory
of then-existing suites (C1 state/gate, C2 also CLI), not pass with zero tests.
Full Python discovery is `[P,"-B","-m","unittest","discover","-s","scripts\\tests","-v"]`.
Native base explicitly lists `evals/lib/mutate.test.mjs`, `evals/lib/score.test.mjs`,
`evals/agent/agent.test.mjs`; native-result adds `evals/lib/native_result.test.mjs`
and reruns scorer. Workflow native command is `[N,"--test",
"evals\\workflow\\failures.test.mjs"]` once implemented.
Corpus is `[N,"evals\\run.mjs"]`; dry-run is `[N,"evals\\agent\\live.mjs",
"--task","paginator","--dry-run"]`. Check corpus/browser prerequisites rather
than silently skip. Prior 705-second Python execution justifies retaining the
1800-second full-suite bound, not reusing the research 90-second budget.

C-STATE-GATE must cover malformed/duplicate/unknown/nonfinite data, cycles,
missing mandatory closure checks, distinct roles, relevant receipt/contract/source
hashes, temporal sequence, changed claims and preserved unrelated receipt bytes.
C-CLI must cover all verbs and outcome/exit collisions, real registered argv/cwd/
env/sentinel effects, no-spawn on block, concurrency, observer failures and crash
gap, conservative recovery, commit/source mismatch and unadmitted receipts.
C-WORKFLOW-EVAL pairs **each** absent review, setup-as-red, stale evidence,
unavailable metric and premature retirement with a real passing counterpart.
Do not count new-module import failure as behavioral red.

Functional test success requires actual relevant assertions and positive
inventory, not rc=0 alone. Timeout 124/125, setup errors, ungraded mutation and
unavailable metrics are never kills or quality success. Record owned fixture
cleanup and no unexplained edits. On a hang: one concrete bounded remedy/retry;
a second hang stops that check, not repeated reruns.

Each slice gets a fresh verifier distinct from all implementers, then a
different fresh read-only reviewer; both inspect the integrated snapshot.
Verifier may add missing tests, not production fixes. Any correction reopens
affected proof and both independent verdicts. Parent self-review is additional,
not a substitute. Prior source hashes preserve only genuinely unaffected proof.

Formatting/static/build: retain CMD-DIFF-CHECK and native tests; re-profile the
final tree for real configured format/lint/type/build commands and record exact
commands or source-backed N/A. There is no root package/build configuration
established here; do not invent `npm run build` or call whitespace a type check.
New guard tests, documents and collector code remain in final proof scope.

## Q — explicit release prerequisite, not scheduled-away debt

**Owner:** parent for design/scope decision, a later measurement implementer for
collectors, then fresh verifier and separate reviewer.

1. Q0: before collector implementation, approve a bounded design supplement for
   language/tool inventories, version/config ownership, subprocess/branch coverage
   and an explicit coverage bar, architecture rule identities/comparison policy,
   Python classified assertions and parser-backed JS mutation. Research suggestions
   are inputs, not already accepted APIs or an authorized install list.
2. Q1: implement and test those approved adapters on actual positive/negative
   language fixtures, including omitted and zero-finding files. Keep analyzer
   failure and unsupported scope incomplete. Retain existing mutation 60%,
   eval 0.9 and compare tolerances. No imported corpus score as root quality.
3. Q2: freeze the entire observed source/contract tree; serialize **all** source,
   docs and evidence writers. Use a clean authorized candidate for mutation,
   predeclare only exact invocation-owned output exclusions, preserve raw base/head
   inventories/results, run actual whole-change classified mutation, investigate
   survivors and resolve measured regressions. New collectors/guard code are not
   exempt. A capped sample is disclosed as a sample, not exhaustive mutation.
4. Q3: independently verify provenance/completeness and review final actual
   results. Only this accepted complete proof can resolve I1.T4's remaining quality
   obligation and subsequent closure checks. Re-run required checks under guard
   admission if the final workflow requires guarded receipts.

Q0 planning can proceed independently; Q1 is not authorized merely by this
sequencing review. Do not repeat the old dead end by omitting its owner or hiding
it behind a generic final-check box. Until a supported collection path exists,
the concrete finishing prerequisite is that design/implementation, not an
invented CLI. CMD-PROBE remains useful to observe honest incomplete/fail, but
running it repeatedly without changed capabilities cannot satisfy Q.

Final release requires all AC01–AC10, all required actual metrics and mutation,
due independent gates, actual host experiments, source/commit match and honest
version/recovery limitations. Limited local preservation on the existing feature
branch may follow functional independent acceptance, explicitly labeled partial.
Never commit to main. GitHub 403/EMU publication remains blocked; no retry,
remote/credential workaround or publication action in this assignment.

## Rejected alternatives

- **Unchanged sequence:** demands unscheduled implementation before any next task.
- **Mark I1.T4 complete or waive metrics:** false quality claim.
- **Build a mixed-language collector system inside guard work:** unreviewed scope
  expansion, larger context risk, no necessary runtime dependency.
- **Add guard bypass/import old reports:** destroys admission and temporal proof.
- **Final-only review or parallel measurement writers:** loses per-slice
  independence or source freshness; reintroduces reviewed evidence problems.
- **README-only feature list:** does not satisfy linked user/operator guidance
  or distinguish actual tooling from procedural/host contracts.

## Reviewer execution and stop

Only bounded reads, provenance checks and artifact validation are in scope.
No production changes, full tests, metrics/mutation, subagents, installations,
main checkout, commit or publication. Only `continuation-plan.html` and this
file may be written. Original state/design/contracts/tasks and historical
evidence remain untouched; parent owns additive operational state updates.

Artifact validation results are recorded below after the bounded check.
The review stops after handing off C0 → C1, not after implementing any guard.

### Bounded artifact validation observed

- Managed Python `P -B scripts/run.py --idle 30 --max 90 -- node -e <inline
  renderer>` used the already installed `benchmark/node_modules/playwright`
  and its Chromium. `agent-browser` was not found by the bounded PATH lookup;
  no installation or claim of agent-browser execution. This is document
  validation only, not product E2E or a host exercise.
- Final HTML: **3 A4 pages**, 12 mm margins, shared print theme; PDF generated
  in memory only and page objects counted, no additional artifact written.
  Wide viewport 1280×900 and narrow 390×844 had no document/content overflow.
  Shared review toolbar loaded; five section headings; zero page/console errors.
  Light/dark body colors resolved respectively to `rgb(35,40,46)` on
  `rgb(251,250,247)` and `rgb(223,227,231)` on `rgb(20,23,26)`.
  These checks are layout/contrast observations, not human aesthetic approval.
- Initial render found an overlong inline signature on narrow screens; split
  the prose into separate code names and rerendered successfully. One combined
  validation invocation failed at PowerShell parsing before either child ran;
  corrected quoting used in-memory script strings. Neither was a product failure
  or a test pass.
- A separate `P -B scripts/run.py --idle 30 --max 90 -- P -B -c <inline check>`
  confirmed all five recorded input hashes unchanged, every local HTML link/
  asset target exists, no authored style block/inline styling, and no trailing
  whitespace in either new file. The Markdown `#checks` target names this file's
  Checks section.
- Final scope observation: no tracked diff; only the two permitted new files
  plus the pre-existing untracked research note. No tests, metrics, mutation,
  installation, subagents, checkout, commits or publication performed.

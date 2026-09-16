# I1 independent Phase 5 verification

**Verdict: NOT-VERIFIED for I1 closure. Actual quality gate: INCOMPLETE / FAIL.**

This is a fresh-context verifier return, not an implementer summary, independent review,
approval to commit, or permission to begin I2. Due scope is AC01, AC02 and I1 AC09;
AC03–AC08 future obligations were not executed or credited.

## Provenance and scope

- **FACT:** cwd was `C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`.
  HEAD was `dde2b491bf5981f86baac41473e7b73faa5ee363`, branch
  `shbs-microsoft-workflow-app-verification`; comparison base
  `bcc971d3b64559127dfc43eb0bfd4348c42803ca`.
- **FACT:** Python **3.14.2**, Node **24.11.1**, Git **2.53.0.windows.4** were invoked.
  No Node 22 execution claim. `i1-independent-*-version.{json,log}` contains observations.
- Producer: self-declared independent verifier context `i1-independent-20260916T194610Z`,
  Windows Copilot session; model identity unknown. This is not authenticated independence.
- Read the requested state, design, contract (including precise shared-output clarification),
  tasks and traceability, then the actual measurement/scorer sources and relevant tests/docs.
- Verifier edits are only `scripts/tests/test_measurement_e2e.py` and prefixed evidence.
  No production implementation, delegation, worktree commit, install, publication or I2 work.
  Existing real-Git fixtures create their own temporary commits; they do not commit this branch.
- Each command record contains expanded argv, cwd, nonsecret environment delta, UTC start/end,
  bounds, actual exit code and output hash. Outer commands used the supplied Python with
  `-B scripts/run.py --idle 120 --max 900 -- …`. Existing suites retain their own bounded
  fixture subprocess helpers. New CLI fixtures capture every expanded child command/output.

## Actual runs

| Evidence prefix `i1-independent-` | Observed result | Interpretation |
|---|---|---|
| `python` | 49 tests, 49 pass; rc 0; 337.940 s | Full requested discovery at initial inventory. Concurrent probe edits mean this is not an atomic final-tree pass. |
| `probe-tests-current` | 19 tests, 19 pass; rc 0; 58.333 s | Affected suite replay after detecting concurrent production/test changes; includes the added malformed-static-inventory case. |
| `measurement-e2e-retry` | 2 tests: 1 pass, 1 assertion failure; rc 1; 67.865 s | Genuine parent freshness counterexample. Passing method covers both ESM and CJS via subtests, not two extra top-level tests. |
| `native` | 62 tests, 62 pass, 0 fail/skip/cancel/todo; rc 0; 10.166 s | Actual four-file native command requested by caller. |
| `eval` | 10 tasks / 20 arms; all 10 bulletproof arms pass; rc 0; 54.719 s | Bulletproof functional inventory 79/79. Six measurable mutation lanes kill 44/44 graded mutants; 25 candidates skipped. Four lanes retain existing null semantics. Not all-language project mutation proof. |
| `dry-run` | rc 0; 11.670 s | Paginator baseline/reference and bulletproof/reference each accuracy, test-realness and composite 1.00. Plumbing only, not a model run. |
| `diff-check` | rc 2; 1,601 whitespace findings | Required command is not green; see F2. |
| `probe` | rc 1; 12.680 s | Correct expected failure handling, **not quality success**. |

Counts above must not be summed: reruns overlap. The final tree contains additional tests
relative to the initial discovery, and the added freshness regression is red. No full
final-tree all-green Python claim is made.

Capture-only failures are retained as limitations, not product failures or behavioral red:
the first native/corpus/dry-run/whitespace capture attempts hit the verifier wrapper's
cp1252 stdout encoding. Its sinks were corrected to UTF-8 and each command replayed once.
No previous matching native/corpus command remained in the observed process listing before
replay. The first new-test run passed policy but errored writing an overlong Windows
evidence filename; `measurement-e2e.{json,log}` retains that 2-test/1-error run. Shorter
evidence names fixed the verifier helper, yielding the genuine assertion failure above.
No timeout was counted as a test pass or mutation kill.

## Findings

### F1 — Blocking AC02: parent probe omits unrelated evidence from freshness binding

**FACT:** `scripts/probe.py:474–478` excludes `.ai/<slug>/evidence` recursively, as well as
both display aliases. The approved clarification instead limits exclusions to exact
same-run generated reports; unrelated evidence must remain observed.

The new public CLI test at `scripts/tests/test_measurement_e2e.py:120–136` creates an
existing `.ai/freshness/evidence/contract-note.json`, invokes real `probe.py`, verifies
that publishing reports preserves freshness, changes `required:true` to `required:false`,
and recomputes the **reported** source scope. Its assertion at line 134 fails:

```
before = 231e00b4f07bff164b84e30964939800e3c07dcdc42d91407c04e44b3ceedccc
after  = 231e00b4f07bff164b84e30964939800e3c07dcdc42d91407c04e44b3ceedccc
```

**INFERENCE:** a changed unrelated evidence input can still appear fresh under the
parent's binding. The currently incomplete overall verdict does not repair this
freshness-contract failure. The child mutation producer's exact exclusions do work;
the defect is in the parent snapshot, not justification for weakening the test.

Evidence: `i1-independent-scope-bda69dbaffc7-{commands,freshness-metrics,freshness-observation}.json`,
`i1-independent-measurement-e2e-retry.log`. Exact replay from the recorded cwd:

```powershell
$py='C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
& $py -B scripts\run.py --idle 120 --max 900 -- $py -B -m unittest discover -s scripts\tests -p test_measurement_e2e.py -v
```

Parent owns remediation of snapshot output ownership under the existing contract, followed
by affected fresh verification and separate review. No production fix was made here.

### F2 — Whitespace check fails on existing workflow artifacts

**FACT:** `git --no-pager diff --check bcc971d3b64559127dfc43eb0bfd4348c42803ca`
returns 2 with 1,601 trailing-whitespace diagnostics across ten workflow artifact paths,
beginning `.ai/workflow-reliability/.gitattributes:1–2` and
`.ai/workflow-reliability/design-contracts.json:1`.
The exact list is in `i1-independent-diff-check.log`; these are not production test failures.
CRLF artifact bytes and `* -text` are consistent with the diagnostics. Do not blindly
rewrite historical evidence/hashes or call this command passing.

### R1 — Concurrent source drift limits integrated-run provenance

**FACT:** another writer changed `scripts/probe.py` and `scripts/tests/test_probe.py`
during this verification and added three report artifacts. The probe change adds
malformed static-inventory handling; the new test is at `test_probe.py:99`.
I did not make or revert these changes.

The original full suite's affected evidence was treated as stale, the current source was
reopened, and its 19-test probe suite was rerun. `i1-independent-checkpoint.json` and
`i1-independent-after.json` match exactly (712 files); the actual repository probe and
affected-suite replay ran in that stable ending interval. The full initial run remains
historical/mixed rather than being relabeled final-tree proof.

## Public behavior / due AC reconciliation

| AC | Functional verdict | Independently observed evidence |
|---|---|---|
| AC01 | **VERIFIED-WITH-LIMITATIONS** | Real ESM/CJS kill + survivor reports, byte/BOM/CRLF restoration, nested cwd and spaced argv; discovery/operators; syntax preflight; setup/import/empty/skip/todo/cancel/timeout/quoted-log rejection; conflicting/legacy/custom runner behavior. Existing `test_mutate.py` and native/scorer tests passed. Runtime scope is Windows / Node 24.11.1, not Node 22 or unsupported languages. |
| AC02 | **NOT-VERIFIED** | Completeness/policy, stale latest-score refusal, missing/unknown baseline and conservative language handling pass their exercised cases. New real ESM/CJS probe cases each measure 50% (1 kill, 1 survivor): measured failure AND incomplete required proof. Child and parent hashes remain fresh after normal publication. **F1 violates unrelated-evidence freshness.** |
| AC09 (I1 only) | **NOT-VERIFIED for closure** | Native/corpus regressions and dry-run pass; affected probe replay passes. New regression is red, whitespace check fails, actual quality remains incomplete, and separate review is still the parent's next independent role. Later AC obligations are not credited. |

Existing coverage is preferred over duplication: `test_mutate.py` covers all named wrong-reason
classes, dirty untracked contracts, unsupported changed Python, competing source/report edits,
source restoration, precise child-output exclusions and run-ID reuse refusal.
`test_probe.py` covers stale high-score alias refusal and real 100% native mutation while
overall proof is incomplete. Native tests cover mixed setup/assertion and container handling.
The two added tests close missing **public** low-score policy and parent-scope boundaries.
Pure collector failure tests use controlled outputs; they are not installed-analyzer proof.
No numeric diff-coverage or architecture proof, independent review, or exhaustive command/
policy tampering acceptance matrix is claimed.

## Actual repository quality gate

Run ID **`6d94877e22814a258639717d1c5b3749`**:
`measurement_status=unavailable`, `completeness=incomplete`, `verdict=fail`,
`baseline=compared`, detected analyzer versions `{}`.
All nine required metrics are unavailable:
architecture rules, diff coverage, duplication, maximum/average complexity, cycles,
dead exports, static findings, mutation score.

The current mutation child returns 2 on dirty input
`.ai/workflow-reliability/design-contracts.json`; source and score are null, with no
executed mutants. No dirty work was stashed, committed or mutated to force a measurement.
Missing collectors and unsupported broader-language proof remain real blockers.

`i1-independent-probe.json` records the actual CMD-PROBE argv, with Windows-equivalent
forward slashes and caller-mandated outer max 900 rather than the plan's 1800; no skip,
force, collector installation or policy relaxation was added. Raw metrics and mutation
are preserved byte-for-byte under
`i1-independent-probe-run-6d94877e22814a258639717d1c5b3749/`.
The pre-existing metrics alias was restored and the newly owned run moved into this
allowed evidence namespace; original paths in the captured report remain execution facts.
`i1-independent-probe-freshness.json` observes matching post-publication source hashes
`51dd107341c8df2cfa1da0684ccd4d984ce35d54fda2d615f2b34c3dc46817fd`.
This is freshness **within its declared scope**, not a waiver of F1's omitted inputs.
Generated corpus reports were likewise copied into prefixed evidence and the pre-existing
`evals/report.md` and `evals/report.json` bytes restored.

## Hashes, handoff and stop

Full before/checkpoint/after inventories and changes are in
`i1-independent-{before,checkpoint,after,reconciliation}.json`.
Key source hashes:

| File | Initial SHA-256 | Final SHA-256 |
|---|---|---|
| `scripts/probe.py` | `71d5846a1ac01a1691742a4c7aca3848cfadf23a869f79990c5f2339d2b84929` | `f2d966571e6061f41a9985eb21463ece56c1d6b2153dd21f4fdba26455c3604a` |
| `scripts/tests/test_probe.py` | `bf8105a49ee3a7cfd3d99e82d7b86147b128177ccae14a865c33f46290c21e23` | `3269a43f95c0596eb1d77671e70905897dde1c0505d1975cdfa5c23a84d0887b` |
| `scripts/mutate.py` | unchanged | `32634d3b0a4ad2331f30d362f6b04c837b9458039882fb1cae72f7970da37fc3` |
| `scripts/native_result.mjs` | unchanged | `528aeec659fde03cab9edd3167a8b2bc184b7194a3f534dd13a4e0a0c38163e0` |
| `scripts/tests/test_measurement_e2e.py` | new verifier test | `9a10ddc8d4d9a9840645b5b3d7196493667d03f2776cdf113a67f9042d6f68bf` |

No own fixture directory remains after cleanup. Before/after inventories exclude `.git`
administrative directories, `node_modules`, `__pycache__`, `.venv` and this verifier's
evidence; the worktree's `.git` pointer file itself remains hashed.

**Stop here:** retain I1 blocked and I2 pending. Parent must disposition F1/F2, obtain
the separate review, and rerun affected checks on a frozen corrected tree. Exact suite
and probe replays are in the command JSON files. There is no executable command that
manufactures the absent diff-coverage/architecture collectors; a real supported collector
and configuration is a prerequisite, not a waiver. A limited local preservation commit
is a separate parent decision only after independent verification plus review; none is
authorized by this failing report. Publication was not attempted (known EMU403 retained).

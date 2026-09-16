# Bounded re-review: **REVISE**

**R1 and R2 are resolved.** The remaining blocker is a post-verification change to the supplied preservation snapshot—not a newly identified production-code defect.

## R1/R2 dispositions

| Finding | Disposition | Current evidence |
|---|---|---|
| **R1 — malformed outcomes accepted** | **RESOLVED** | `scripts/mutate.py:384–444` regenerates canonical candidates, checks identities/bytes, reconciles native/process evidence against the baseline, and validates counters/score. `scripts/probe.py:365` invokes it before accepting the measurement. |
| **R2 — discovery expansion rejected** | **RESOLVED** | `scripts/probe.py:353–356` reuses `select_test_run()` and compares the complete canonical command and test-file inventory. It does not permit arbitrary suffixes. The producer and consumer explicitly share the default 20-mutant budget. |

I inspected the corrected source and tests and verified the recorded executions:

- Full Python: **54/54**, matching raw-log hash.
- Separate E2E: **4/4**, matching raw-log hash; these four are included in the 54.
- Both corruption matrices: **one accepted genuine control and 30 rejected corruptions**.
- Discovery positive passes; extra argv and mismatched `test_files` are specifically rejected.
- Retained native: **62/62**, matching raw-log hash.
- Retained corpus: **10 bulletproof tasks, 79/79 functional assertions**.
- All **85 retained Node/corpus input hashes** match the original execution manifest and current files.

The consumer-reconciliation clarification at contract hash **`5b3eb1ac…78335bf`** matches the implementation. The documentation re-anchor also matches current bytes, hash **`cec506cd…f6e161`**.

## R3 — Medium: preservation snapshot differs from verified manifest

**Location:** `.ai/workflow-reliability/.gitattributes:3–5`

**FACT:** Of the final manifest’s 98 inputs, **97 match**. The attributes file differs:

```text
Manifest: 1fd44f434ed6352c44f6833a238f193e9a1336ad9d319622eabbcc1913a1bde9
Current:  0e7d5e05cc8ad01c2ba3c4cc811cbcd06af6784be92265043e735929b753a2c6
```

The first two current lines exactly reproduce the manifest hash. These lines were subsequently appended:

```gitattributes
# Raw process transcripts preserve intentional whitespace; review their recorded hashes.
evidence/*.log -diff
evidence/i1-quality-stdout.json -diff
```

This changes Git diff treatment of evidence files and is outside the stated report/state/traceability-only update allowance. The earlier ordinary whitespace-check result therefore cannot be presented as verification of the exact current attribute configuration.

**Required disposition:** Either restore the manifest-bound attributes, or obtain a narrow independent re-anchor of the attribute change and affected evidence/diff checks. Preserve the original manifest and execution records. **No full functional-suite rerun is requested solely for this attribute delta.**

I am not alleging altered raw logs or a production regression; their checked hashes remain valid.

## Per-AC reconciliation

| AC | Verdict | Limits |
|---|---|---|
| **AC01** | **VERIFIED-WITH-LIMITATIONS** | R2 resolved; ESM/CJS discovery, routing and classification proof accepted. Windows/Node 24 execution only. |
| **AC02** | **VERIFIED — functional semantics** | R1 resolved; malformed-proof rejection, command binding, freshness and honest completeness behavior accepted. Not a project-quality pass. |
| **AC09** | **BLOCKED for closure/preservation snapshot acceptance** | Functional regressions reconciled and separate code re-review completed. R3 requires snapshot reconciliation; required quality proof remains missing. |

AC03–AC08 remain planned. **I2 stays pending.**

## Quality and trust limitations

Actual probe **`72f1ccc1a361421999706176c4ab7dc4`** remains:

```text
exit 1 · measurement_status=unavailable
completeness=incomplete · verdict=fail
nine required measurements missing
```

Coverage and architecture collectors remain unimplemented; other collectors lack complete proof; actual project mutation refused dirty inputs. Fixture results do not substitute for these measurements.

The exact shared-output exclusions remain unchanged and acceptable. Structural consistency checks do not authenticate producers or provide isolation. Eval retains **0.9** and its ungraded/null semantics; standalone probe retains **60%** and required completeness.

Metric-dependent scorecard dimensions—duplication/reuse, complexity/cycles, static robustness, mutation/diff-coverage test quality—remain **unverified**, not promoted by this re-review.

**Stop:** No writes, agents, installations, commits or publication were performed. R1/R2 need no further correction identified here; reconcile R3 before accepting the current local-preservation snapshot. EMU403 remains untouched.

---

# Re-review: **APPROVE for limited local functional preservation**

**R3 is resolved by this narrow packaging review. R1/R2 remain resolved.** No outstanding blocking finding remains within this bounded review.

### Packaging checks
- Read the justification in `review.md:40–44`.
- Independently ran ordinary **`git diff --cached --check`**: **exit 0**, empty diagnostic output.
- Checked staged attributes: `-diff` applies to current-task `evidence/*.log` and the exact `evidence/i1-quality-stdout.json` transcript. Inspected source, tests, authored documentation and structured verification JSON retain ordinary diff/whitespace treatment.
- Rechecked proof bytes: Python, E2E, native and corpus raw-log hashes match their recorded executions. `i1-quality-stdout.json` matches the initial snapshot.

**Provenance remains explicitly qualified:** **97/98 manifest inputs match**. The sole delta is the now-reviewed `.gitattributes`, current SHA-256:

```text
0e7d5e05cc8ad01c2ba3c4cc811cbcd06af6784be92265043e735929b753a2c6
```

Retain the original manifest and this supplemental disposition; do not relabel it “98 unchanged.”

### Cumulative due-AC verdicts

| AC | Verdict |
|---|---|
| **AC01** | **VERIFIED-WITH-LIMITATIONS** — corrected discovery/routing/classification; Windows/Node 24 execution only. |
| **AC02** | **VERIFIED — functional semantics** — corrected result reconciliation, canonical command binding, freshness and completeness behavior. |
| **AC09** | **Functional regression and independent review components VERIFIED; quality closure BLOCKED.** |

Accepted evidence remains **54 Python tests**, the separately repeated **4-method E2E suite** already included in those 54, **62 native tests**, and **10 corpus tasks / 79 functional assertions**.

### Unchanged stop boundary
Actual probe **`72f1ccc1a361421999706176c4ab7dc4`** remains **incomplete/fail with nine missing required metrics**. This approval does **not** close I1.T4, waive metric-dependent scorecard proof, authorize I2, or authorize publication. AC03–AC08 remain planned; Node 22 remains unverified; EMU403 remains untouched.

No writes, agents, installations, commits or publication were performed. Review stops here.

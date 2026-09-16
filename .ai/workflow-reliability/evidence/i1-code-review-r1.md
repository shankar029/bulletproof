# Phase 6 review: **REVISE**

**Verdict applies to limited local functional preservation only.** Two reproduced functional defects remain. This is not approval to close I1, begin I2, or publish.

Reviewed staged + unstaged implementation against **`dde2b491bf5981f86baac41473e7b73faa5ee363`**. No repository files were written, no agents spawned, and no installation or publication attempted. Targeted execution used an owned OS-temporary Git fixture, subsequently removed; source restoration was confirmed.

## Findings

### R1 — High: malformed mutation outcomes can become measured/ok
**Location:** `scripts/probe.py:339–344, 359–371`

`mutation_entry()` validates summary counters and their arithmetic, but never validates or reconciles `results`. Consequently, the accepted “classified outcomes” need not exist or agree with the score.

**FACT — reproduced against the current code:**

Using a genuine successful mutation producer, with real native tests, valid current source/command binding and verified restoration:

| Modification after producer completion | Consumer result |
|---|---|
| None — positive control | `measured`, `100.0`, `ok` |
| Remove `results` entirely | **`measured`, `100.0`, `ok`** |
| Change the sole result outcome from `killed-assertion` to `setup-error`, leaving summary counters unchanged | **`measured`, `100.0`, `ok`** |

The replay intercepted only the completed disposable report; it did not fabricate command exits or substitute a test runner. This is the same report-corruption boundary exercised by the existing independent schema tests.

**Impact:** Required mutation proof is accepted despite missing or contradictory classified evidence. Other currently missing metrics still make the overall probe fail, but that does not make this falsely accepted measurement correct.

**Required correction:** Validate the complete result structure and reconcile inventory, outcomes, counters and score before acceptance. Missing results or any ungraded result must be unavailable. Add these cases alongside the existing real-producer corruption tests.

This is structural evidence validation—not an authentication or sandbox requirement.

### R2 — Medium: probe rejects its producer’s valid native discovery expansion
**Location:** `scripts/probe.py:351–358`; producer expansion at `scripts/mutate.py:209–214`

The producer supports explicit `node --test` without filenames by appending discovered native files. The consumer instead demands that reported argv equal the original argv plus only the reporter option.

**FACT — public CLI replay:**

A clean temporary repository contained:

- `value.mjs`, changed from `flag = false` to `flag = true`;
- `value.test.mjs`, asserting `flag === true`;
- no workflow initialization.

Invocation:

```text
python -B scripts/probe.py --slug discovery --base <fixture-base> -- node --test
```

Observed:

```text
child complete: true
child score_pct: 100.0
child argv: node --test-reporter=<native reporter> --test value.test.mjs

parent mutation state: unavailable
reason: Current mutation proof rejected:
        Mutation argv does not match the requested command
```

Run ID: **`c51c7e4c4ce74b04a0895ee98d42b6b1`**.

**Impact:** Supported discovery executes correctly but its genuine measurement is discarded at integration.

**Required correction:** Bind acceptance to the same canonical command-selection result used by the producer, including discovered concrete files. Do not fix this by accepting arbitrary argv suffixes or weakening command matching.

## Shared-output clarification: **accepted**

**FACT:** `probe._snapshot()` at `scripts/probe.py:474–481` now excludes only:

- `.git`;
- the slug’s metrics display alias;
- this run’s `metrics.json`;
- this run’s `mutation.json`.

The mutation producer uses the corresponding exact report paths. There is no blanket evidence-directory exclusion or legacy mutation-alias exemption.

The preserved independent F1 regression distinguishes report publication from unrelated evidence edits. This matches the clarified invariant and resolves the previous broad-exclusion defect. It does not make later evidence archival invisible or imply authenticated ownership.

## Independent proof reconciliation

I checked raw log hashes and current source hashes rather than accepting headline counts:

- **53 Python tests:** raw log hash matches; `Ran 53 tests` / `OK`.
- **62 native tests:** raw log hash matches; 62 passed, zero failures, skips, cancellations or todos.
- **10 corpus tasks:** summed the archived bulletproof rows to **79/79 functional assertions**.
- **21 current implementation/test/design/attribute hashes** match the final verifier manifest.
- **82 recorded Node/corpus source/config files** match the earlier before/after manifests and current tree.

These are verified historical executions on matching source—not full suites rerun by this reviewer. The new counterexamples expose coverage gaps; they do not falsify those recorded passes.

The CSV regression adds a meaningful trailing-empty-field assertion. Its result is **9 graded kills, 0 survivors, 7 ungraded**, not 16 kills. Eval retains **0.9**, excludes ungraded outcomes from its denominator, and preserves null normalization. Standalone mutation retains **60%** and treats ungraded candidates as incomplete. Those deliberately different semantics must remain explicit.

## Per-due-AC verdict

| AC | Review verdict | Reconciliation |
|---|---|---|
| **AC01** | **NOT-VERIFIED in full** | Direct ESM/CJS discovery, explicit-file routing and native classification have substantial matching proof. R2 leaves the integrated discovery route defective. Execution evidence covers Windows/Node 24 only. |
| **AC02** | **NOT-VERIFIED** | Completeness separation, stale-alias refusal and the shared-output correction are supported. R1 accepts malformed classified proof; R2 rejects valid current proof. |
| **AC09** | **BLOCKED for closure** | Existing regression executions are reconciled and preserved. This independent review now has two unresolved findings; actual quality proof also remains incomplete. |

**AC03–AC08 remain planned**, not current passes. No I2 dispatch is warranted.

## Actual quality limitations—separate from findings

The archived current actual probe, run **`9c28b908eb764dcaa1421a580e2fb8f5`**, reports:

```text
exit 1
measurement_status: unavailable
completeness: incomplete
verdict: fail
missing required metrics: 9
```

Diff-coverage and architecture collectors are unimplemented. Other static collectors supplied no complete proof; project mutation refused dirty inputs. The top-level `metrics.json` is an older display report, not the latest authoritative execution.

**No project mutation score, coverage pass, all-language measurement, or quality-gate pass is established.** Node 22 execution, broader platform compatibility, and adversarial isolation are not verified. EMU403 remains a publication blocker with no retry or workaround.

## Scorecard

- **Correctness: 3/5** — reproduced R1/R2.
- **Design fidelity: 3/5** — required malformed-proof rejection and normalized command agreement are incomplete.
- **Scope fidelity: 4/5** — reviewed changes remain within I1 and directly coupled regressions/docs.
- **Maintainability: 3/5** — duplicated command normalization already disagrees at the consumer boundary.
- **Unverified:** exhaustive grounding audit; reuse/duplication; design complexity/cycles; robustness/static findings; test-quality mutation/diff coverage. Missing measurements cannot be replaced by prose scores.

**Handoff:** preserve this review unchanged, disposition R1/R2 separately, and obtain affected verification/review after corrections. Keep I1.T4 blocked and I2 pending.

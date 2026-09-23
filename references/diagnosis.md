# Reference: Evidence-Driven Bug Diagnosis

For a reported defect or performance regression, load this procedure during Phase 1, before
proposing a fix. The output is evidence in the existing task research/state and evidence
directory, not a new report or phase. Diagnose the user's symptom, not a nearby failure.

Research remains source-read-only under `research.md`. Run only authorized, non-mutating
reproductions. If a new harness, regression test, instrumentation, or scratch environment is
needed, return that need to the parent; the parent or an explicitly write-scoped worker prepares
it. A researcher does not acquire write permission or recursively delegate through this procedure.
Temporary experiments do not authorize production changes or bypass design approval.

## 1. Establish a useful failing signal

Read enough source and existing tests to find the entry point and construct the reproduction.
Choose the smallest appropriate interface that still reaches the real failure: an existing test,
CLI invocation, API request, browser flow, or authorized replay/harness. Keep the original input
and scenario so a smaller reproduction cannot become the only thing the fix proves. For a
**browser or front-end defect**, reproduce and inspect it interactively with a live debugger
(on pi, `pi-browser-debug` — console, network, DOM, JS via CDP; see `e2e-agent-browser.md`),
capturing the console/network evidence — then prove the eventual fix with agent-browser.

Record the exact command/steps, working directory, prerequisites, source/configuration snapshot,
expected outcome, observed outcome, and evidence location. The assertion must distinguish this
bug from correct behavior; "did not crash" or a failure in setup is not the reported symptom.
Run it and confirm the failure is relevant before treating the reproduction as established.
Use existing tools, redacted fixtures, environment-based credentials, and isolated test data.

Shorten setup and narrow scope where practical without removing the causal path. Pin time,
randomness, or dependencies where appropriate, but do not require every real reproduction to
run in seconds. For intermittent failures, record attempts and failures under stated conditions;
use a bounded, authorized repeat/stress experiment rather than claiming a single green run
proves absence. Do not stress shared or production systems without authorization.

**Checkpoint:** a symptom-specific reproduction has actually failed, or the task explicitly
records what was tried, the access/tooling gap, and the next diagnostic action. A proposed
command is not execution evidence. An unresolved cause remains a hypothesis; it cannot pass
Gate 1 as an established root cause.

## 2. Minimize without changing the bug

Reduce input, setup, configuration, or callers one change at a time, rerunning the check after
each change. Keep the smallest practical scenario that retains the same failure and relevant
interactions. Do not replace a multi-caller, timing, or integration failure with a passing test
of an isolated helper and call it a reproduction. Stop minimizing when further reductions lose
the symptom or cost more than they clarify; preserve the original case separately.

## 3. Distinguish causes with experiments

When the cause is ambiguous, rank plausible explanations and state the observation each predicts.
Choose probes that discriminate between them; vary one relevant factor at a time. An obvious
cause with direct evidence does not need an artificial quota of alternative explanations.
Record observations separately from inferences and update the hypotheses when evidence disagrees.

Prefer a debugger or targeted boundary measurements to broad logging. Any temporary
instrumentation has an identifiable marker, an owner, and a cleanup step; keep secrets and
personal data out of captured evidence. Performance investigations start with a baseline:
record workload, environment, measurement method, and relevant distribution/sample details.
Use differential checks, profiling, query plans, or bisection when they help isolate the cause.
Run history experiments in an isolated worktree; preserve the user's current work.

**Checkpoint:** the proposed cause is supported by source and observations that distinguish it
from competing explanations. Otherwise return a named blocker and the next useful probe,
not a speculative production patch. Record the supported cause in research for the design.

## 4. Fix through the normal gates, then verify both cases

Phase 2 designs the root-cause correction; Phase 3 plans changes and checks; Phase 4 follows the
test-first cycles in `testing-and-e2e.md`. Turn the reproduction into a regression test that fails
for the right reason before applying the fix. If the available test boundary cannot capture the
failure, raise that testability gap for a bounded design change or state the proof blocker;
do not substitute an insensitive test or silently waive regression coverage.

After the fix, rerun the minimized check, the original reported scenario, and affected regressions.
For performance/intermittent defects, compare against the recorded baseline under comparable
conditions and the required acceptance criteria; state residual uncertainty honestly.
The independent verifier must be able to rerun the original case from the recorded evidence.
If it remains inaccessible or fails, delivery remains blocked/limited under the existing gates.

Remove owned temporary instrumentation and harness files not needed for durable regression
coverage; retain the regression test and required redacted evidence. Check for the recorded
markers. Put the cause and correction in the commit/PR, not an inline source change journal.

## Inspiration

Original adaptation of Matt Pocock's
[diagnosing-bugs](https://github.com/mattpocock/skills/blob/959a8e9f1edc3adbe2f7e3054bb6fbefa6696260/skills/engineering/diagnosing-bugs/SKILL.md).
Bulletproof retains its own permission boundaries, approval gates, and independent verification;
there is no mandatory hypothesis count, universal timing target, or new tool dependency.

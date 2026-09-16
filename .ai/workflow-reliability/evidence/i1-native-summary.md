# I1.T2 implementation handoff

## Status and ownership

FACT: the native mutation lane is implemented and targeted checks are green.
Only the eight authorized source/test paths were changed. No workflow observer,
state/tasks/docs, helper primitives, probe, commit, push, PR, agent, or factory work
was performed. Parent integration, fresh independent verification/review, probe,
full native/eval regression, and publication remain outstanding.

## Proof

Authoritative initial final evidence: `i1-native-final-checks.json`. It records command argv,
bounds, return codes, full stdout/stderr, and SHA-256 of all eight owned files;
the ending source-unchanged check passed. The subsequent mixed-language completeness
fix is source-pinned in `i1-native-mixed-language-green.json`; its 13/13 CLI run
supersedes the earlier 12/12 mutation check. Other implementation files are unchanged.
The final shared-directory integration fix is source-pinned in
`i1-native-shared-run-green.json`: **15/15 CLI tests pass**, retaining all prior
safety tests. `i1-native-shared-run-targeted.json` also captures the direct
shared-directory, competing-output, and existing-report refusal checks.

| Check | Observed result |
| --- | --- |
| `node --test evals/lib/native_result.test.mjs evals/lib/score.test.mjs` | 38/38 pass |
| Python `-m unittest discover -s scripts/tests -p test_mutate.py -v` | 15/15 pass |
| Python `-m unittest discover -s scripts/tests -p test_run.py -v` | 4/4 pass |
| `git diff --check -- <owned files>` | exit 0 |

Python: `C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`.
Actual Node: **v24.11.1**. Node 22's reporter contract is documented in source;
**Node 22 execution is not verified**.

Later bounded integration follow-up: `i1-native-followup-summary.md`.
CLI sink encoding is fixed and the expanded capture/CLI suite is **5/5** green
(`i1-native-cli-encoding-green.json`, current run.py/test_run.py hashes).
The unchanged CSV corpus has a real uncovered final-empty-field case; its gate
remains 8/9 until the parent applies the exact assertion documented there.
That assertion is proven on an owned temp copy, not applied to repository fixtures.

The tests use real native subprocesses and owned Git repositories. They cover both
ESM and CJS kills/survivors, a complete 50% score returning 0, no-package discovery,
nested package/default test cwd, spaced argv and regex parameters, native context
removal, CRLF/BOM restoration, stale nonce refusal, a competing source edit,
exclusive measurement lock, untracked contract dirtiness, strict/arrow/shift
operators, unsupported lexical scope, custom runner refusal, baseline
zero/import/syntax/skip/todo failures, mutant setup/log-spoof/missing/skip failures,
timeout, native TS syntax preflight, and scorer zero/null compatibility.

Pre-existing reds are preserved in the parent's `p0-reproductions.json`.
`i1-native-capture-red.json` additionally executes the original base runner against
a real UTF-8 subprocess: decoding was wrong and two ResourceWarnings identified
unclosed streams. This is behavioral red, not a missing-module/import error.
Its captured-source hash reflects the source text executed after newline
normalization, not a claim about raw Git blob bytes.

Earlier `*-first.json`, `*-second.json`, and
`i1-native-scorer-capture-green.json` are iterative evidence, not final verdicts.
The last of those includes a subsequently corrected legacy-newline test failure.
`i1-native-capture-green.json` and the authoritative final bundle supersede it.

## Implementation details

- `scripts/mutate.py:169`: native selection preserves Git root versus test cwd,
  argv, option parameters, and the existing manifest priority. Unknown/custom
  runners run unchanged but cannot produce assertion kills.
- `scripts/mutate.py:226,272`: ESM/CJS discovery and token-boundary operators.
  CJS export assignments are declarations, not statement-deletion candidates.
  Regex/template/multiline-comment ambiguity is conservatively exposed through
  `unsupported_scope`, not represented as measured proof.
- `scripts/native_result.mjs:40,76,96`: real leaf events, explicit assertion
  causes, excluded containers/file pseudo-tests, quoted logs, positive baseline
  inventory, and fail-closed parsing/grading. `parseTap` remains unchanged.
- `scripts/native_result.mjs:114`: shared `checkSyntax(file)` is a small
  implementation helper for mutation and the scorer. Observed Node 24
  `--check file.ts` accepted malformed TS; the helper also asks the native TS
  parser, without importing/executing product code. Missing TS-parser support
  is unavailable, not green. Native experimental warnings are retained.
- `scripts/mutate.py:447,551`: full source snapshot, Git provenance, exclusive
  lock, preflight, original-byte restoration, competing-edit preservation,
  fresh atomic report, and exit 2 for incomplete proof.
  Unsupported recognized changed languages are detected before candidate sampling:
  a Python change with no operator, or omitted by `--max-mutants`, still populates
  `unsupported_scope` and forces incomplete/exit 2. Real mixed JS/Python fixtures
  prove this even with one JS kill and `ungraded=0`.
- `scripts/run.py:67,82`: optional `env` only (no observer), UTF-8 incremental
  decoding, legacy universal-newline behavior, byte-progress capture, and
  reader-owned stream closure. Existing tuple/positional signature remains valid.
- `evals/lib/score.mjs:111`: shared parser/classifier/preflight; the existing
  paginator integration passes and zero/null semantics are retained. The full
  fixed-corpus eval was intentionally left to parent integration.

## Exact producer/probe integration

Invoke a fresh measurement, for example:

```text
python scripts/mutate.py --repo REPO --slug SLUG --base BASE --run-id UNIQUE_ID --timeout 300 --max-mutants 20 --test-cwd TEST_CWD -- node --test "test/math case.test.mjs"
```

Omit remainder argv for discovery. `--test-cwd` defaults to the original `--repo`
directory before Git-root normalization. `--run-id` defaults to a fresh UUID hex.
`--test-cmd` retains only simple unquoted whitespace-separated legacy commands;
quoting/backslash ambiguity errors with guidance to use remainder argv. It is
mutually exclusive with remainder argv. Native reporter overrides are rejected.

The **only report** is:

```text
<Git root>/.ai/<slug>/evidence/runs/<run_id>/mutation.json
```

Probe may preallocate the shared nonce directory. Mutation claims **only
`mutation.json`**, using exclusive file creation (`scripts/mutate.py:404`).
An existing report or interrupted reservation is rejected, never reused.
Before atomic publication, file identity and reservation bytes are checked
(`scripts/mutate.py:416`); a detected competing output is preserved and exits 2.
The transient reservation is not a completed report and must not be consumed.
The global mutation lock and exact output exclusions are unchanged. There is no
latest alias. `i1-native-report-example.json` is an actual copied fixture report;
`i1-native-report-example-invocation.json` gives its actual argv/nonce/return code.
The owned temp fixture was cleaned afterward. These example copies are for schema
inspection, **not substitutes for fresh producer evidence**.

Required top-level fields:

```text
schema_version=2
run_id
source: SourceSnapshot|null
test_run: TestRun|null
baseline: NativeResult|null
results: [{file,line,operator,before_sha256,after_sha256,outcome,artifacts}]
score_pct: number|null
complete: boolean
reason: string
restored_sha256: hex|null
generated: UTC ISO timestamp
killed, survived, total, ungraded: integers
```

Additional explanatory fields are `unsupported_scope` and `baseline_artifacts`.
Before/after hashes identify whole-file bytes. Outcomes are
`killed-assertion`, `survived`, `invalid-syntax`, `setup-error`, `timeout`, and
`unclassified`. `artifacts` contains syntax/execution return codes/stdout/stderr
and the parsed native result; recovery retains `original_base64` when a competing
edit must not be overwritten.

`source` comes from the shared primitive, with full resolved merge-base/HEAD
filled in. Its scope is repository directory `.` with precisely these exclusions:

- `.git` administrative metadata.
- `.ai/<slug>/evidence/runs/<run_id>/mutation.json`.
- `.ai/<slug>/evidence/runs/<run_id>/metrics.json` (same invocation's probe output).
- `.ai/<slug>/metrics.json` (the probe's generated display alias).

The exact shared output family is also the dirty-tree ownership allowlist.
There is no arbitrary exclusion flag, blanket evidence/.ai exclusion, or mutation
latest alias. `.ai/<slug>/mutation.json` remains observed input, since this
producer does not write it. `restored_sha256` must equal `source.scope_sha256`,
including after the parent publishes both designated metrics outputs.

`i1-native-shared-output-freshness-green.json` source-pins the integration fix:
four targeted tests pass (freshness/shared publication, contract dirtiness,
ESM/CJS restoration plus nonce refusal, and competing source preservation).
The fresh test also proves existing contract and unrelated evidence edits still
invalidate the snapshot, and an existing generated metrics alias does not block
the next invocation. Earlier source-scope examples are superseded by this
explicit shared-output clarification.

`test_run.command` contains actual resolved `argv` (including the absolute native
reporter URI), repository-relative `cwd`, `runtime.executable`,
`runtime.observed_version`, `idle_seconds`, `max_seconds`, and
`environment: {"NODE_TEST_CONTEXT": null}` for native Node.
`test_run.runner` is `node-native` or `process`; it also contains `test_files` and
`assertions` (empty for standalone automatic inventory). The positive native
baseline records the required leaf identities.

`score_pct = 100*killed/(killed+survived)` rounded to one decimal; no graded
mutants means null. Any ungraded candidate, unsupported scope, failed baseline,
source mismatch, or recovery condition prevents completeness. **Exit 0 means
complete classified measurement, regardless of score. Exit 2 means
incomplete/unavailable/invalid invocation. The 60% threshold remains probe policy.**

Probe should require this exact nonce report, successful producer return code,
matching source/test invocation, complete=true, and verified restoration; it
must never fall back to an older artifact.

## Limits

Native Node only currently supplies classified mutation proof. Other language
targets/custom runners and ambiguous lexical spans explicitly remain unmeasured.
TS syntax preflight depends on a runtime exposing Node's native TS parser.
Source hashing/locks detect covered edits; they are not a filesystem sandbox or
an authenticated defense against deliberately forged child/runtime evidence.
The full quality gate and independent consumer adjudication remain the parent's.

# Q2 shared-JS native-core checkpoint — independent code review

## Preliminary verdict: APPROVE; independent proof acceptance PENDING

**APPROVE the bounded source checkpoint for preservation, conditional on the
parent's separate fresh-verifier reconciliation.** No high-confidence substantive
code defect requiring correction was identified in the five owned paths.
This is an independent fresh-context code review, **not independent execution
proof, complete shared-JS acceptance, Q2 completion, or a Phase 6 ship pass**.
Overall delivery remains incomplete.

Scope is the user's explicitly partial native library checkpoint against
`fdc6af09a48cbdb21959698453ed2769eec224f4`. Future serialization, command,
manifest, replay, graph/probe and candidate work is not imposed on this checkpoint.
The review does not reopen qualification or treat the library's documented
Python-qualified-input precondition as a promised authentication/sandbox boundary.

## Source and authority reconciliation

FACT: review-time HEAD is `fdc6af09a48cbdb21959698453ed2769eec224f4`.
Both tracked working-tree changes and the three untracked owned JS/test files
were reviewed; this was not a committed-only diff.

FACT: `q2-js-seal.json` SHA-256 is exactly
`7befec79cce53797b158d62f80f412b2efdf05080c1e7c28a8b2cd48f9e1f0fa`.
At initial and final reconciliation, **all 28 owned-file records and all 10
unchanged-input records** matched their actual byte lengths and hashes.
The owner's `before.json` and `after.json` are byte-identical and agree with
the current five owned source/test/document pins:

| Owned path | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `b5a824cd84a4a63bb1a6ec5cb6d2e09426614006b12f0b9ef867f040439c4db9` |
| `scripts/measure_js.mjs` | `bc1467eaf8666dcb162525cb78d25feb3672f28eac10af45745feec731522b23` |
| `scripts/tests/test_measure_js.py` | `ed0463f8ee6b0c3de382369a6b1762793467b755d4f0ac68d19e2be44cae8ebc` |
| `scripts/tests/measure_js.test.mjs` | `aa15edc62252fd86043e9e759196d8a86f5560ffdc9314ad86f1f14281f48e3f` |
| `references/quality-metrics.md` | `4706eee4c2ba142eec951bbc3a26cb1df846ba7595d5414d813814ebdd8a37a5` |

FACT: authorities read include the necessary original acceptance, adapter and
record definitions in `measurement-enablement-contracts.json`; the root
amendment; revision-3 inventory/controller, host, census, diagnostic, byte and
test definitions; and the relevant original and second focused design-review
determinations. Their sealed hashes remain unchanged. In particular revision 3
remains `887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e`.
Design approval is not represented as implementation proof.

FACT: inspected the actual existing qualification producer and callers
(`measure.py:570–682`, `tests/test_measure_source_bindings.py:20–45`), actual
inventory/controller consumers, Git fixture and native-capture harness, and
the relevant installed qualified TypeScript API declarations/implementation.
The two library files read match the existing extracted-resource pins:

| Qualified resource | Bytes | SHA-256 |
| --- | ---: | --- |
| `lib/typescript.js` | 9,112,572 | `3ae902c92cc44dace175c0e69e13a4b0899f6983c6121d76b9ab8dd5795e7675` |
| `lib/typescript.d.ts` | 588,085 | `e134052a6b1ded61693b4037f615dc72f14e2881e79c1ddbff6c514c8a516b05` |

These are read-file identity checks, not a new qualification cycle.

## Findings and bounded source assessment

**Blocking findings: none. Nonblocking substantive findings: none.**
No speculative cleanup or future-integration request is raised as a defect.
The following are source-grounded review determinations, not claims that this
reviewer executed the behaviors.

1. **Compiler admission and resource consistency — acceptable within its
   explicit internal precondition.** `measure_js.mjs:141–186` checks the fixed
   API/version/runtime/settings and preload inputs, exact module/runtime
   locators, executable bytes, every supplied resource hash/length, and actual
   CommonJS cache paths before/after loading. The sole nonbuiltin require is
   the explicit qualified TypeScript module. `absolute`/`readRegular`
   (`48–74`) reject linked/aliased or nonindependent files and detect changes
   during reads. This does not independently authenticate the incoming
   qualification, establish R1 admission, or promise native-DLL closure.

2. **Controlled Program/checker — acceptable.**
   `parseProgram` accepts only its own opened compiler handles (`193–197`).
   It reads the explicit source/metadata set, checks pins, records missing
   code/decode failures separately and rejects metadata read/decode failures
   (`204–243`). Its host explicitly supplies source reads, existence,
   directories, cwd, realpath and library paths in the two virtual namespaces
   (`245–284`); it does not create the ambient default compiler host.
   The actual qualified `createProgram` uses the supplied host for its normal
   resolution path (`typescript.js:126976–127082`) and passes
   `CreateSourceFileOptions` to `getSourceFile` (`128674–128685`), which the
   adapter forwards to `createSourceFile`. No subject execution or ambient
   package-loading path was found in the delivered code. Admitting a complete
   source-bound metadata set remains the explicitly deferred composition task.

3. **Bytes, diagnostics and census — acceptable for this core.**
   `SourceBytes` copies the input, fatal-decodes UTF-8 without dropping BOM,
   builds UTF-16-to-byte boundaries, retains CRLF/line separators and rejects
   split-surrogate boundaries; ranges support genuine zero-width/EOF while
   spans require nonempty content (`76–138`). Diagnostic projection retains
   actual compiler chains, categories, locations and related information,
   including source-less records (`286–308`). The qualified
   `getPreEmitDiagnostics` includes option/global/syntactic/semantic diagnostics
   (`typescript.js:126391–126402`); the census deliberately uses syntactic
   diagnostics, not all type errors, to decide parsing success (`309–334`).
   It counts actual non-EOF tokens and body-bearing function-like nodes,
   excluding JSDoc traversal; failed entries retain null counts. Resource
   and source bytes are rechecked before return (`335–348`).
   No inaccurate count/span rule or fabricated success was identified.

4. **Legacy compatibility — acceptable by source inspection.**
   `_walk` and `inventory` enforce a real bool; only enabled JSX/TSX labels
   change before hashing (`measure.py:215–218,263–273,295–325`).
   `code_files` still uses the same default discovery (`280–284`).
   `controller_digest` preserves the five-name/default byte-hash formula,
   while True requires all six independent regular files (`1226–1239`).
   There is no mode salt or missing-sixth-file fallback. Existing probe
   creation (`probe.py:555–568`) and producer rederivation
   (`measure.py:1190–1212`) still use the legacy defaults; this is an explicit
   integration limit, not accidental evidence of JS acceptance.

5. **Unsupported surfaces and documentation — truthful.**
   Direct library execution throws an explicit no-command error
   (`measure_js.mjs:354–356`). Returned live Program/checker objects stay in
   native code (`349–351`); the test transport selects plain proof records
   rather than serializing these objects (`tests/measure_js.test.mjs:209–219`).
   The existing graph keeps non-Python receipts unsupported
   (`measure_graph.py:365–390`), and scalar collectors stay unavailable
   (`measure.py:388–405`). `quality-metrics.md:72–80` accurately describes a
   native-core checkpoint without configured collection, serialization,
   replay, graph or complete-metrics support.

6. **Tests — real and relevant, but bounded.**
   The Python harness validates the existing binding, copies and hashes the
   controller, launches real Node under bounded capture, and checks actual
   results/bytes (`tests/test_measure_js.py:20–77`). The native tests exercise
   actual files, AST/checker objects, six-suffix failures/zeros, byte slices,
   aliases, diagnostics, changed/missing inputs and a source-execution
   sentinel (`tests/measure_js.test.mjs:37–203`). The two-revision fixture
   creates actual Git revisions and changed metadata, not claimed replay.
   No mocked parser/runner, skipped case or fake production result was found
   in the owned tests. The imported fixture's trivial Python example is
   repository setup, not asserted as JS parser proof.
   Advanced diagnostic/serialization/lifecycle scenarios remain unproven as
   disclosed; the tests do not establish complete accepted IDs.

## Recorded owner proof, not independent verification

FACT: the sealed owner final log ends with **15 Python methods passed in
879.393 seconds**. Nine are the new core methods; six are selected existing
regressions. The seven `test_native_*.json` records each contain returncode 0,
empty stderr, idle 30 / max 90, the corresponding native case, and the exact
sealed copied-controller hash. These are **nested executions, not seven
additional methods**. The six base/head TypeScript/lizard/Vulture command
records likewise contain returncode 0 and empty stderr; they are nested in
the existing binding regression, not six additional tests.

FACT: the owner six-suffix capture contains exactly 30 rows: 18 processed and
12 failed. Earlier development failure/correction records remain sealed
history, not added final coverage. This reviewer ran no suites, test cases,
mutants or compiler qualification.

UNKNOWN/PENDING: fresh independent execution acceptance. No final verifier
handoff/seal has been supplied for reconciliation in this context. A verifier
directory visible in Git status is not a completed proof. It was not polled
or treated as final. Parent should provide the final independent report/seal
for a narrow same-context reconciliation against the source pins above.

## Accepted test-ID limits

All seven complete accepted IDs remain **NOT-VERIFIED as complete IDs**.
The bounded code fragments below are accepted by inspection, with independent
execution proof still pending:

| Accepted ID | Delivered fragment reviewed | Still outside this checkpoint |
| --- | --- | --- |
| JS-LIFE-01 | Real two-revision core/census fixture and changed metadata | Complete base-only Python scenario, reservations, execution-before-graph, manifests/archive |
| JS-LIFE-02 | None claimed | Producer-owned fresh replay, purposes, semantic/failed-tuple acceptance |
| JS-OWN-01 | Pins, private handle, source/settings/path rejection, six-file digest checks | R1/phase ownership, tamper/no-launch and actual command-failure/archive policy |
| JS-PARSE-01 | Six suffixes, byte boundaries, syntax forms and counts | Serialized SyntaxEvidence, candidate operations, enabled composition/rederivation |
| JS-SYMBOL-01 | Live checker alias/reexport assertion | Versioned symbol identities, complete references/origins and tamper replay |
| JS-DIAG-01 | Multiple type/unresolved diagnostics, source-less missing input, EOF projection | Full bad-options/related/library scenarios and producer transport validation |
| JS-COMPAT-01 | Default/False behavior, True classification and digest primitives, root syntax reads | Enabled validator/graph/probe composition, candidate API calls and full regression acceptance |

Source/functional preservation is not full quality closure. Full suite, coverage,
mutation, scalar proof, all seven complete IDs and overall delivery remain open.
Human approval and publication are not newly established here.

## Review operations and errors retained

Only this review artifact was authored. No production/test/reference edits,
agents/factories, installs, suites, commits/pushes, host experiments,
privilege/symlink retries, root mutants or old cleanup were performed.
External read-only commands used the supplied managed Python with `-B` through
`scripts/run.py --idle 30 --max 120`, and the supplied qualified Git executable
or PATH. Searches and file reads were read-only.

The first combined inspection command (shell 511) returned exit 1 after its
optional instruction-file lookup; its large raw Git diff was retained by the
tool in temporary output. The explicitly checked instruction files were absent.
No product test failed in this review. A subsequent bounded
`git diff --ignore-space-at-eol` exposed the small logical tracked delta;
raw byte hashes, not whitespace-normalized diffs, governed all seal checks.
The remaining reconciliation commands exited 0. No error was silently
converted into passing execution proof.

Final status also showed parent-owned `state.md`, the unrelated `evals/report.md`,
and independent-verifier evidence activity. None was edited or used to enlarge
this review's source acceptance. No whole-worktree freeze is claimed.

**Disposition: preliminary APPROVE for this bounded native-core source
checkpoint; final preservation proof acceptance remains PENDING the separately
running verifier's final evidence and narrow reconciliation.**

# Q2 outstanding tool qualification: CHECK-TOOLS qualified

**TypeScript 5.9.3, lizard 1.24.0 and Vulture 2.16 are qualified for the bounded
APIs below.** Together with retained jscpd 5.2.1/Ruff 0.16.8 qualification, this
closes CHECK-TOOLS only. It does **not** complete Q2, implement adapters, produce
root quality metrics or alter earlier functional acceptance. Coverage 7.16.1
remains deferred to Q3.

The parent-approved provenance amendment permits the official TypeScript release
package and unaltered exact-commit Python sources, not wheel equivalence.
Human approval remains unconfirmed; the approval is the parent's decision under
the existing user-authorized autonomy.

## Executed gate

| Tool | Result | Genuine observations |
|---|---|---|
| TypeScript 5.9.3 | QUALIFIED | CLI version/help; 41 synthetic files; 18 clean/zero-function/invalid suffix cases plus six nested/arrow/async/template/regex/JSX shape cases. Six clean programs have zero diagnostics; all 18 empty/comment/functionless inputs remain in explicit program census. Four positive diagnostics: 6133 twice, 2322, 7027. |
| lizard 1.24.0 | QUALIFIED, strict text API only | CLI version/help; 44 calls across seven suffixes, plus a narrow strict-decoding follow-up. Seven branch controls each produce one function with CCN=2; 21 empty/comment/functionless controls return no functions. Nested Python/JS/TS and JSX callbacks are recognized. Real 1,200-level nested JS produces swallowed RecursionError diagnostics, which are rejection evidence, not success. |
| Vulture 2.16 | QUALIFIED | CLI version/help; 17 cases, 23 assertions. Main positive has two findings (unused import confidence90; unreachable code confidence100), nested async has one. Six explicit negative/empty/comment/functionless/Python3.14-template/noqa controls have zero findings at confidence80. Syntax, null bytes, bad encoding, missing paths and mixed error/finding inputs are distinguished. |
| jscpd 5.2.1 / Ruff 0.16.8 | QUALIFIED, retained | No rerun. Original schemas, exact 158-rule E/F/B/S list, py314/configuration and failure evidence remain authoritative; executable hashes are rechecked. |

`q2-tools-source-summary.json` contains compact per-case names/counts/spans.
Full raw API objects, diagnostics and receipts are in
`q2-tools-source-{typescript,lizard,vulture}-results.json`.
Command JSON captures exact argv, wrapper argv, cwd, exit and log hashes.
The runner merges child stderr into stdout and normalizes newlines; those logs
are **wrapper captures**, not separate untouched child streams. In-process
Python case records separately retain the actual captured diagnostic strings.

## Exact provenance and executor bindings

Owned root:
`C:\Users\shbs\.copilot\session-state\c154cbfc-3b1d-4163-b8dd-5f0b43af3095\files\q2-tools-20260917\source-qualified-1`

| Distribution / license | Official origin and immutable commit | Retained archive SHA-256 |
|---|---|---|
| TypeScript 5.9.3 / Apache-2.0 | `microsoft/TypeScript` release `v5.9.3`, `c63de15a992d37f0d6cec03ac7631872838602cb` | `10e108c9cf7d5f2879053dff18515fb405abf2ccef63eaaf017d9c571687a1d3` |
| lizard 1.24.0 / MIT | `terryyin/lizard`, `308b1c3efd8c1c69bcc3eb82deeaec64fd3662ec` | `a55057a0589e0c0230eff798752d621f2e3c646b54354b4b37501b32f433c611` |
| Vulture 2.16 / MIT | `jendrikseipp/vulture`, `b0f67ba0044693aa9ec0d38fe460590facc98004` | `53b37a8bfe9204458cf1bda786df5bd082312f3d2a9f02aacc8879e9b91e11cf` |
| Pygments 2.21.0 / BSD-2-Clause | `pygments/pygments`, `a43b45dcf081b6010c6ab4428f149f7f6d2499c4` | `fdffdcdab90d4e022e825902e2ad1f9a546b568eb949d2ef117f3d7054594743` |
| pathspec 1.1.1 / MPL-2.0 | `cpburnz/python-pathspec`, `ecf71a99ca739479d450b9830f43416ea0c519c7` | `6a27200bec6146a0b0833b4201e058b73109ccd09a9ea8255667278414487de6` |

Full official acquisition URLs and retained archive paths remain in the unchanged
route report/manifest. TypeScript's hash matches the publisher release digest;
Python archive hashes are observed official-HTTPS archive hashes plus commit
pins, **not publisher wheel digests**.

After rehashing, extracted all five archives into new exclusive directories:
links, nonregular entries, traversal and case-insensitive collisions rejected.
All 3,348 extracted files, including runtime resources, compiler default libs and
licenses, are hashed in `q2-tools-source-extracted-pins.json`. No setup.py,
backend, installer, build, dependency download or new network request ran.

Actual entrypoints (all beneath that root; full absolute paths in roots/summary):

* `typescript\package\lib\typescript.js`:
  `3ae902c92cc44dace175c0e69e13a4b0899f6983c6121d76b9ab8dd5795e7675`.
* `lizard\terryyin-lizard-308b1c3\lizard.py`:
  `d0807a33d38976a5e5756b37d637e35aa8d2018dee0b87f059d003f3154a07af`.
* `vulture\jendrikseipp-vulture-b0f67ba\vulture\core.py`:
  `bbbb778365c044188b89d69c6f77dbf23a7b1477a8f419019c4f71a4f56c7faa`.

Python is managed 3.14.2 at
`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`,
SHA-256 `5829a9ef2930e10a965503ea0f96248bd4b19faf4177fdfd061f1d484448bb03`.
Every source-tool invocation used `-I -S -B`; only approved roots were added to
stdlib paths. Actual module files/hashes are recorded per invocation; optional
re2/hyperscan/typing_extensions/colorama/jinja2/tomli are absent. No installed
distributions/entry-point plugins were discovered; pathspec uses `simple`.
Pygments/pathspec versions are asserted, not inferred from archive names.

Node 24.11.1 is `C:\Program Files\nodejs\node.EXE`,
SHA-256 `8f3e33fa1f67843a320d2200ed1a5d40cc59766715a7a02728b8213c2167a084`.
Its retained PE identity is ARM64; Python and the retained native analyzers are
x64. No claim that Node itself is an x64 binary. TypeScript was required by
absolute path; loaded JS/default-lib files are recorded. No project package
resolution, plugin, auto type acquisition, source execution or generated output.

## Reader mappings and mandatory boundaries

**TypeScript:** exercised `createSourceFile`, recursive `forEachChild`,
`createProgram`, `getTypeChecker`, `getPreEmitDiagnostics`, symbol lookup,
module exports and reexport alias resolution. `.js/.mjs/.cjs` use JS,
`.ts` TS, `.tsx` TSX, `.jsx` JSX. Compiler settings include noEmit/allowJs/checkJs/
strict/noUnusedLocals/noUnusedParameters and allowUnreachableCode=false.
Default libs are real; external types are explicitly empty for these fixtures.
Unresolved local and bare imports produce two real 2307 diagnostics. Missing
root input produces source-less 6053; invalid options also yield source-less
diagnostics. Empty inventory produces zero diagnostics but remains zero files.
Raw shape: code/category/source/file/start/length/message; source-less spans
are null. API offsets are UTF-16, verified against UTF-8 bytes and CRLF. Namespace
computed access is outside-model, not proof that exports are unused. JSX parser
support is not JSX runtime/coverage qualification.

**lizard:** `FileAnalyzer(get_extensions([])).analyze_source_code(filename, text)`.
PythonReader / JavaScriptReader / TypeScriptReader / TSXReader are verified;
TSXReader handles both tsx and jsx. MJS/CJS native mappings and reversible
in-memory `.js` aliases agree on branch controls; no files were renamed.
FileInformation exposes filename/nloc/token_count/function_list; functions expose
name/long_name/start_line/end_line/cyclomatic_complexity/nloc/token_count/
parameters and related lexical fields. Line spans are 1-based inclusive.
Python nested function names include `outer.inner`; JSX callbacks may be named
`view`. These are upstream lexical identities, not stable IDs or AST equivalence.

**Important discovered limit:** initial lizard run exited **1**, because assertion
39 incorrectly expected the convenience file API to emit a decode diagnostic.
`auto_read` actually retries UTF-8 with `errors="ignore"` and returns plausible
zero-function output. The original failure/result remain unchanged. A separate
successful boundary qualification proves strict decoding rejects the same bytes
before the selected text API; valid UTF-8/CRLF still yields CCN=2. The convenience
file API is **not qualified**. This enforces the already-approved text-input
contract, not a replacement analyzer or policy change.

Reject missing reader (otherwise silent C fallback), invalid syntax, any error/
skip diagnostic, GENERATED CODE and forgive directives. The genuine recursion
case returns partial FileInformation with stderr: never count it as successful
census. A valid empty/functionless file instead has a successful explicit call.
Complexity is lizard's lexical cyclomatic model, not cognitive complexity.

**Vulture:** `scan` returns None; explicit successful scan receipts provide census.
`get_unused_code(min_confidence=80)` returns Items with confidence/filename/
first_lineno/last_lineno/message/name/typ; size is inclusive line count.
`scavenge` also loads retained whitelist resources, successfully exercised.
Exit values: clean=0, invalid input=1, invalid CLI=2, findings=3. Missing path
raises SystemExit with an error string. Crucially, `report` changes invalid-input
exit1 to findings exit3 in a mixed invalid/positive scan: preserve pre-report
status **and** stderr. Neither final exit3 nor nonempty findings proves success.
Confidence60 function findings are excluded at 80; noqa and bundled whitelists
affect results. Reflection remains outside its static model; no dynamic deadness
claim.

Retained native limits still apply: jscpd census comes from JSON summary.files,
not clone pairs; omitted empty files need shared parser receipts, omitted
nonempty/invalid inputs are errors. Ruff uses its frozen 158 rules, py314,
isolated/no-cache/no-fix flags and actual JSON schema; zero findings are not file
census and noqa can suppress findings.

## Preservation, incidents and handoff

Final manifest rehashes all pre-existing Q2 evidence, retained archives, extracted
source trees, actual external imports and required executor/contract pins.
Earlier TLS failures, route evidence and native qualifications are untouched.
Source-bootstrap help/API stages have different recorded helper hashes; official
tool/dependency bytes did not change.

One pre-tool orchestration typo invoked `source-helper.py typescript`, producing
`KeyError: 'typescript'`/exit1 before Node started. Correct invocation
`typescript_cases` succeeded. This and the lizard assertion failure are disclosed;
no tool-output rewriting, TLS retry, timeout recovery or masked successful rerun.
Initial finalization also stopped before writing a manifest because Python's
cp1252 default decoded Node's UTF-8 JSON path incorrectly. The bounded encoding
probe records default-path failure versus explicit-UTF-8 success; finalization
now reads evidence JSON explicitly as UTF-8. The source fixtures and TypeScript
results were not altered or rerun. Future artifact readers must also specify
their encoding rather than inherit the Windows locale.

Tracked-context capture includes concurrent parent changes in workflow_state.py
and parent-owned reports/state. HEAD remains the accepted d971634... at capture.
There is **no whole-source-freeze claim**. This work wrote only additive
`q2-tools-source-*` evidence and its exclusive external source/fixture tree.
No adapters, project dependencies, repository tests/docs/shared state, agents,
commits, OS settings or project-code uploads were made by this workstream.
No processes remain running; no bytecode was generated. Retain owned toolchains,
fixtures and licenses as pinned qualification evidence; no cleanup is pending.

**Parent next step:** review this reconciled tool gate, then separately authorize
adapter implementation using these exact bindings and error/census boundaries.
Source/module/helper hashes, provenance and finite limitations must travel into
that future tool binding. Do not promote this prerequisite into Q2 completion or
a quality-pass claim.

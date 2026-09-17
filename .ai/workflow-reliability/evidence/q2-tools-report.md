# Q2 CHECK-TOOLS handoff — partial qualification, blocked prerequisite

17 September 2026. **Not Q2 completion, not a root quality pass.**
Accepted HEAD remains `d971634219a633cc4401fb7dcba9685e672978aa`.
No production, tests, project dependencies/configuration, docs, workflow state,
commits, publication, agents, browsers, or OS settings were changed by this worker.
Only new `q2-tools-*` evidence and the exclusively owned external directory were written.

## Verdicts

| Tool | Result | Executed evidence |
|---|---|---|
| jscpd **5.2.1**, released Windows x64 MSVC | **QUALIFIED**, bounded CLI/JSON contract below | Version/help/list/debug; seven positive clone pairs and seven independent no-clone scans, all seven suffixes; seven additional syntax-shaped clone pairs; short/comment/empty/zero/missing/invalid-encoding census |
| Ruff **0.16.8**, released Windows x64 MSVC | **QUALIFIED**, bounded CLI/JSON contract below | Version/help/check-help/rule-help; 158 exact stable E/F/B/S rule IDs; eight explicit Python file cases, missing file, zero-file directory, Unicode coordinates, exact-rule/config reconciliation |
| TypeScript **5.9.3** | **BLOCKED — TS-PACKAGE-TLS** | Actual required compiler-module import failed; npm registry metadata TLS negotiation failed through Python and Windows curl. Official tagged source package metadata independently confirms 5.9.3, Apache-2.0 and `lib/typescript.js`; no installed compiler/API qualification claimed |
| lizard **1.24.0** | **BLOCKED — LIZARD-WHEEL-TLS** | Import, version and help attempted: module absent. Exact non-yanked wheel exists in PyPI metadata; wheel download failed TLS negotiation through Python and curl |
| Vulture **2.16** | **BLOCKED — VULTURE-WHEEL-TLS** | Import, version and help attempted: module absent. Exact non-yanked wheel exists in PyPI metadata; wheel download failed TLS negotiation through Python and curl |
| coverage.py **7.16.1** | **DEFERRED — Q3** | Not installed, run or instrumented; not needed for this qualification |

“Qualified” means the observed tool interface is usable with the listed fail-closed
conditions, not that a production adapter, all-language syntax owner, independent
verification, or full measurement exists. Three unmet tool prerequisites block CHECK-TOOLS
as a whole. No source-distribution substitution or alternative analyzer was implemented.

## Ownership, sources and binary pins

Owned root (abbreviated **O** below):

`C:\Users\shbs\.copilot\session-state\c154cbfc-3b1d-4163-b8dd-5f0b43af3095\files\q2-tools-20260917`

| Identity | Absolute path relative to O | SHA-256 |
|---|---|---|
| jscpd executable | `O\jscpd\jscpd.exe` | `c0bbbe8f3fea28395e08e60abcfe703dca0e39c0a393aa4a7fc602f816ad8670` |
| jscpd release archive | `O\jscpd-windows-x64-msvc.tar.gz` | `b4941605a87dc0e4957fcf727d2c92e68b8ed92aaac5c378a86a9636357654cb` |
| Ruff executable | `O\ruff-native\ruff.exe` | `22b93aa554f2c3ec969fa83c5d77da3d61a4a54c61cbca70f5eeec63eef28e48` |
| Ruff release archive | `O\ruff-x86_64-pc-windows-msvc.zip` | `7985e06caf14b0077cb68da41edbf812e1d9654fe4c144d72b71138e96350129` |

Both archive hashes matched their actual GitHub release-asset SHA-256 metadata.
Both executables identify as PE machine `0x8664` and actually ran on this Windows host.
Sources: [jscpd v5.2.1](https://github.com/kucherenko/jscpd/releases/tag/v5.2.1)
and [Ruff 0.16.8](https://github.com/astral-sh/ruff/releases/tag/0.16.8).
Both are MIT licensed; tagged license bytes/hashes are retained outside the repository.
No signature/Sigstore verification is claimed.

`q2-tools-runtime-bindings.json` records absolute executor paths, Python/Node/binary
hashes, Python DLL, runner hash and native PE imports with hashes of existing local
dependency candidates. Embedded Rust code is bound by the binary hash. PE imports are
**not** a loaded-module/forwarder attestation: Windows API-set imports have no fabricated
file hash. Node is `C:\Program Files\nodejs\node.EXE`, observed **v24.11.1**.
Python is the explicitly requested managed **3.14.2** interpreter. Neither was upgraded.

Install action was exact-release download, hash verification and archive extraction
inside O, as preserved in `q2-tools-qualify.py:ruff_release` and `provision`.
There was **no successful Python package installation and no venv creation**.
The attempted wheel route was stopped before its offline uv install because downloads
failed. No npm install, global installation, manifest/lockfile, or root analyzer config
was created. uv help/version were inspected only.

## jscpd schema, mapping and census

Use the **final** `q2-tools-jscpd-final-debug` / resolved-config records, not an initial
default-limited command. Settings: 40 tokens, 5 lines, mild; no ignore patterns,
no gitignore, no cross-format groups, similarity 1, max-gap 0, no identifier/literal
normalization, one worker, explicit config/input arguments, JSON plus summary.
`summary-top` must cover the entire inventory.

The executable defaults to **1 MiB max-size**, despite the tagged Rust documentation's
“no limit” table. Final qualified argv explicitly sets decimal
`--max-size 18446744073709551615`, observed as `u64::MAX` in merged settings.
The inspected walker compares a `u64` file length against this bound, so it cannot
exclude a representable file by size. Do not inherit the initial 1 MiB default.
No huge-file runtime/performance qualification is claimed.

Actual JSON:

* `summary.files[]`: `path`, `format`, `lines`, `tokens`, `bytes`, `complexity`,
  `duplicatedLines`, `duplicatedTokens`.
* `summary.totalFiles` is the pre-top-N source count; require equality with the
  validated census rows, not just a nonzero total.
* `duplicates[]`: `firstFile` / `secondFile` each carry `name`, `start`, `end`,
  `startLoc`, `endLoc`; records also carry `format`, `kind`, `fragment`, `lines`,
  `tokens`, `isNew`. Use inclusive `start`/`end` line ranges and union both locations.
* `statistics.total` and `.formats` are aggregates, **not file receipts**.
  Do not import their duplication percentages or duplicated-line sums as the approved
  union-based metric. Summary `complexity` is not lizard complexity.

Observed mapping: `.py → python`; `.js/.mjs/.cjs → javascript` via the explicit
format extension mapping; `.ts → typescript`; `.tsx → tsx`; `.jsx → jsx`.
Reports use Windows canonical `\\?\C:\...` paths. Normalize that prefix only after
checking exact owned input identity; preserve source bytes separately. Fragment
text is newline-normalized and is not the source hash. Byte offsets from `startLoc`
were not qualified as canonical source offsets; the duplication adapter only needs
the qualified inclusive line fields.

Seven per-suffix positive cases each produced **one clone, two census rows**.
Seven independent no-clone cases each produced **zero clones, one census row**.
Python rows had 40 tokens / 9 lines; the initial equivalent JS-family control rows
had 53 tokens / 11 lines. Additional genuine async/nested/arrow/template-interpolation,
regex/division, typed TS and JSX/TSX element fixtures each produced positive clones.
Those scans are lexical duplicate detection, **not TypeScript parse/type acceptance**.

The low-window 1-token/1-line census reconciled **28/28 nonempty inputs**, including
seven short and seven comment-only files, out of **35 declared inputs**. All seven
zero-byte files were absent from the tool summary. These need the approved shared
parser's actual successful empty-file receipts; no fabricated jscpd scan receipt.
Comment-only rows were observed in mild-mode output: do not rewrite their observed
line/token values to zero. Low-window clones are census-only and cannot become metric
findings. A global empty denominator remains unavailable.

Missing path: exit **1**. Empty directory/empty files: exit **0**, empty census.
Invalid UTF-8: also exit **0**, empty census despite a nonempty supplied file.
This is a demonstrated reason to reject source-decoding failure or omitted nonempty
inputs even on exit zero. The inspected walker also skips some walk/read failures:
the future adapter must require the full input/census partition and shared parser
success. jscpd alone cannot certify syntax, readability or exhaustive discovery.

## Ruff rules, census and output

`q2-tools-ruff-rules.json` contains all **158 exact IDs**. They were extracted from
installed `--show-settings` for E/F/B/S, then passed back as the explicit `--select`
list and re-resolved to the identical set. This freezes stable rules with
`--no-preview`, not all future rules under those prefixes.

Qualified controls: `--isolated --no-cache --no-fix --no-preview
--no-respect-gitignore --no-force-exclude --target-version py314
--select <exact IDs> --output-format json`, with explicit files and owned cwd.
Help advertises py314; a genuine Python 3.14 template string parsed with no finding.
No cache directory appeared; every fixture hash remained unchanged.

Eight-file census matched `--show-files` exactly. Six files produced zero findings:
clean UTF-8/CRLF functionless source, comment-only, empty, nested async, py314, and
an explicit existing `noqa` example. One positive file produced **four findings**
(`F401`, `S101`, `B006`, `E701`). One malformed source produced **two
`invalid-syntax` records**, exit 1; it is not valid AST-dependent metric input.
The missing file produced `E902` / exit 1: infrastructure failure, not an ordinary
lint count. An empty directory exited 0 with a no-Python-files warning and `[]`;
that is zero inputs, not successful processing of requested files.

JSON is an array. Record keys actually observed:
`cell`, `code`, `end_location`, `filename`, `fix`, `location`, `message`, `name`,
`noqa_row`, `severity`, `url`. Location/end-location have 1-based `row`/`column`.
A supplementary-character fixture distinguished coordinates: `F821` starts at
column **14 Unicode codepoints**, not byte column 18 or UTF-16 column 15; end
column 26 is exclusive. Convert against the exact UTF-8/CRLF source.
That additional fixture produced three findings (`E702`, `B018`, `F821`).
`fix` can contain suggestions even though no fix is applied.

Existing `# noqa: F401` suppressed its finding. The eventual adapter must inventory
directives as approved, never silently treat their presence as absence of suppression.
No directives were added to project source. These are finite lint/type/safety
diagnostics, not exhaustive security analysis.

## Blocked tools and bounded next actions

TLS failures were `SSLV3_ALERT_HANDSHAKE_FAILURE` in managed Python and
curl exit **35**, Schannel `SEC_E_ILLEGAL_MESSAGE`. They are not package absence or
version unavailability. No authentication, HTTP downgrade, certificate disabling,
alternate unapproved mirror, account, or OS-policy workaround was attempted.

Exact wheels verified in inbound PyPI metadata:

* lizard 1.24.0, MIT, `lizard-1.24.0-py2.py3-none-any.whl`,
  SHA-256 `a688bc607a891ff4a7836826f25742dc9c1bf648da3075dbd495e199e8848602`.
  Declared dependencies are Pygments and pathspec; their candidate metadata/download
  failures are recorded, **not accepted executor bindings**.
* Vulture 2.16, MIT, `vulture-2.16-py3-none-any.whl`,
  SHA-256 `6e0f1c312cef1c87856957e5c2ca9608834a7c794c2180477f30bf0e4cc58eee`.
  Its conditional tomli dependency does not apply to Python 3.14.

Parent options: authorize an accessible approved distribution route for these exact
wheels/TypeScript package, or bounded-review an exact-tag official-source provisioning
alternative. The latter has **not** been implemented or qualified. Do not substitute
global TypeScript 7.x or a new analyzer.

After obtaining packages, first read installed APIs. TypeScript needs its actual
5.9.3 compiler API, source/checker/diagnostic and suffix/Unicode/CRLF fixtures.
lizard needs explicit Python/JS/TS readers and reversible MJS/CJS JS aliases, with
zero-function receipts, nested/arrow/async/TS outputs, GENERATED CODE controls,
fallback-reader rejection and actual recursion-error detection. Vulture needs
native 3.14 scan/report records, confidence **80**, complete explicit-file parsing,
positive/negative/no-finding/error cases, and static—not dynamic-deadness—semantics.
None of those outstanding APIs or schemas is inferred as qualified.

## Evidence integrity, limits and cleanup

Every recorded child command has exact argv/cwd/bounds/exit and hashed stdout/stderr
capture files. All commands were routed through the existing bounded runner.
These are **raw wrapper bytes**: the runner CLI merges child stderr into stdout and
normalizes newlines. Thus warnings can precede JSON in a wrapper log. They are not
claimed as byte-exact separate child streams. Native JSON report files are separately
hashed and decoded. Future adapters should use separate output channels.

Initial helper incidents are disclosed rather than called a clean aggregate:
the first upstream/download phase raised TLS exceptions; four census commands
incorrectly repeated scalar CLI flags and returned parser exit 2; a later helper
syntax error stopped before execution. The census flags/helper were corrected and
new captures retained. Initial outer tracebacks are in session tool output, not
fabricated as separate raw artifact files. No timeout occurred, so no timeout retry
budget was consumed.

Only synthetic tool inputs were used. Downloads were inbound upstream
metadata/docs/releases; no project code was transmitted. jscpd's documented
`--no-tips` was used; no tool update, baseline-history, MCP/server, remote rule,
autoconfig, or auto-fix mode was invoked. Neither native help exposes a telemetry
switch. No invented telemetry environment variable, complete network-isolation
claim, or packet-capture claim is made.

All six initial accepted source/contract pins matched at the final boundary check;
HEAD matched before/after. Parent-owned document/status changes were already present
and are not attributed to this worker. Current Q1 `validate_config` deliberately
rejects nonempty tools/JS entrypoints, Context's toolset binds its Python parser,
and scalar collectors remain unavailable. This evidence is **not** a configuration
accepted by that production code.

No background process was started and no PID cleanup was needed. Owned native
binaries, archives, fixtures and reports remain under O for replay; no package or
binary is stored in the repository. No root deletion or main-checkout cleanup ran.
`q2-tools-manifest.json` binds the final evidence set and tool statuses. Parent must
resolve the three blockers, review the bounded handoff, then choose adapter work.

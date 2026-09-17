# Q2 secure acquisition follow-up: BLOCKED pending route approval

**The one same-host compatibility route is exhausted.** No new tool qualification,
installation, source execution, or CHECK-TOOLS completion is claimed. Prior jscpd/Ruff
qualification was not rerun. Original `q2-tools-report.md`, manifests and failure
captures remain unchanged.

## Secure probes and disposition

Inspected actual **curl 8.21.0 / Schannel** version and full help. Made exactly one
request each to `registry.npmjs.org` and `files.pythonhosted.org`, using
`--disable --tlsv1.2 --tls-max 1.2 --proto =https --proto-redir =https --retry 0`,
normal certificate verification and a 60-second transfer ceiling. The latter request
targeted the already-pinned lizard wheel and serves as the one shared PyPI file-host
probe for lizard, Vulture and declared dependencies; no separate retries for each wheel.

Both returned **curl 35 / SEC_E_ILLEGAL_MESSAGE**, HTTP **000**, no response body.
`ssl_verify_result=0` does not establish successful peer verification after a failed
handshake. No insecure option, certificate/root-CA edit, mirror, downgrade, credential,
or policy workaround was used. No explicit organization-policy response was observed;
the underlying TLS failure's cause remains unknown. No further package-host retry.
Existing owned archive/cache inspection found no exact requested package bytes.

Evidence: `q2-tools-route-probes.json`, `q2-tools-route-probe-*.json` and raw logs.
Subsequent official GitHub metadata/source requests succeeded normally. All downloaded
archives remain **data-only**, unextracted and unexecuted, under:

`C:\Users\shbs\.copilot\session-state\c154cbfc-3b1d-4163-b8dd-5f0b43af3095\files\q2-tools-20260917\route-1`

## Exact official candidates

| Tool / license | Exact tag and resolved commit | Distribution/API feasibility |
|---|---|---|
| TypeScript **5.9.3**, Apache-2.0 | `microsoft/TypeScript`, `v5.9.3`, `c63de15a992d37f0d6cec03ac7631872838602cb` | Official release includes `typescript-5.9.3.tgz`, already-built compiler, declarations, default libs and CLI; no runtime package dependencies, Node >=14.17. No bootstrap/build needed. |
| lizard **1.24.0**, MIT | `terryyin/lizard`, `1.24.0`, `308b1c3efd8c1c69bcc3eb82deeaec64fd3662ec` | Release has no attached wheel. Complete pure-Python source candidate; committed version is 1.24.0. Requires Pygments and pathspec; no dependency version constraints in `setup.py`. |
| Vulture **2.16**, MIT | `jendrikseipp/vulture`, `v2.16`, `b0f67ba0044693aa9ec0d38fe460590facc98004` | Release has no attached wheel. Complete Python package candidate with committed version and bundled whitelist resources; tomli conditional only below Python 3.11, so no required external runtime dependency on managed 3.14.2. |
| Pygments **2.21.0**, BSD-2-Clause | `pygments/pygments`, `2.21.0`, `a43b45dcf081b6010c6ab4428f149f7f6d2499c4` | Same exact dependency candidate inspected previously, not newly selected latest. Complete Python package with committed version; no required runtime dependencies. |
| pathspec **1.1.1**, MPL-2.0 | `cpburnz/python-pathspec`, `v1.1.1`, `ecf71a99ca739479d450b9830f43416ea0c519c7` | Same exact dependency candidate inspected previously. Complete Python package, committed `_version.py`; no required runtime dependencies, optional native accelerators must remain absent. |

Vulture and Pygments annotated tag objects were independently resolved to the table's
commits. All five releases were observed non-draft/non-prerelease. These are candidate
source/runtime bindings, **not installed-version or compatibility proof**.

Official origins and acquired SHA-256:

| Artifact | Origin | SHA-256 |
|---|---|---|
| TypeScript published package | `https://github.com/microsoft/TypeScript/releases/download/v5.9.3/typescript-5.9.3.tgz` | `10e108c9cf7d5f2879053dff18515fb405abf2ccef63eaaf017d9c571687a1d3` |
| lizard commit source archive | `https://api.github.com/repos/terryyin/lizard/tarball/308b1c3efd8c1c69bcc3eb82deeaec64fd3662ec` | `a55057a0589e0c0230eff798752d621f2e3c646b54354b4b37501b32f433c611` |
| Vulture commit source archive | `https://api.github.com/repos/jendrikseipp/vulture/tarball/b0f67ba0044693aa9ec0d38fe460590facc98004` | `53b37a8bfe9204458cf1bda786df5bd082312f3d2a9f02aacc8879e9b91e11cf` |
| Pygments commit source archive | `https://api.github.com/repos/pygments/pygments/tarball/a43b45dcf081b6010c6ab4428f149f7f6d2499c4` | `fdffdcdab90d4e022e825902e2ad1f9a546b568eb949d2ef117f3d7054594743` |
| pathspec commit source archive | `https://api.github.com/repos/cpburnz/python-pathspec/tarball/ecf71a99ca739479d450b9830f43416ea0c519c7` | `6a27200bec6146a0b0833b4201e058b73109ccd09a9ea8255667278414487de6` |

TypeScript's archive hash **matches the publisher's release-asset digest**.
NPM registry integrity was unavailable, so NPM-byte identity is not claimed.
The four source archive hashes are locally observed HTTPS download hashes, **not**
publisher-issued package digests or matches to PyPI wheels. Their commit pins plus
full runtime-file SHA-256 inventories are recorded in `*-archive-inspection.json`.
Those inventories contain 69 lizard, 23 Vulture, 343 Pygments and 32 pathspec runtime
files; Python AST inspection found no syntax errors. This is static inspection,
not importing those packages or qualifying their behavior.

## Source/API and build comparison

**TypeScript:** inspected the published archive's `typescript.d.ts` declarations for
`createSourceFile`, `createProgram`, `forEachChild`, `getTypeChecker`,
`getPreEmitDiagnostics`, `getSymbolAtLocation` and `getAliasedSymbol`. No API calls ran.
Unexpected but useful: the exact tag also contains built `lib/typescript.js` and
`lib/typescript.d.ts`; both match the release package byte-for-byte:

* Compiler JS: `3ae902c92cc44dace175c0e69e13a4b0899f6983c6121d76b9ab8dd5795e7675`.
* Declarations: `e134052a6b1ded61693b4037f615dc72f14e2881e79c1ddbff6c514c8a516b05`.

Prefer the complete released package, retaining default libs and notices. Do not
assemble a partial compiler from raw files. Source package build scripts use
`hereby local` and development dependencies including TypeScript ^5.7.3, esbuild
and many test/lint tools, with some floating ranges. **No rebuild or development
dependency installation is proposed**; existing Node 24.11.1 satisfies runtime engines.

**lizard:** `FileAnalyzer.analyze_source_code(filename, code)` exists at source line
613. It selects `get_reader_for(filename) or CLikeReader`, catches `RecursionError`,
writes `[skip]` to stderr, then returns partial `fileinfo`. `__call__` can return
empty `FileInformation` after I/O/decode failure. Comment processing stops at
`GENERATED CODE`; forgive directives also exist. These remain mandatory fail-closed
qualification cases, not acceptable zero-function successes.

All reader modules are imported, including Erlang's unconditional Pygments imports:
**Pygments cannot be omitted merely because Q2 uses Python/JS/TS**. pathspec is a
declared dependency; lizard can otherwise silently fall back on import failure.
Keep it present even though exact-input API use avoids recursive discovery.
jinja2 is imported only inside the optional HTML-output function; HTML reporting is
outside the proposed route. No jinja2 installation. `setup.py` imports setuptools
and rewrites `lizard_ext/version.py` from CHANGELOG: **do not execute setup.py**.

**Vulture:** `scan(code, filename)`, `get_unused_code(min_confidence=...)`, `report`
and `scavenge` are present. `Item` stores name/type/file/first and last lines/message/
confidence. Syntax and null-byte errors set `ExitCode.InvalidInput`; empty findings
alone cannot establish successful scanning. Preserve bundled whitelist bytes
and existing noqa handling, use confidence **80**, and retain static-not-dynamic
deadness semantics. `config.py` uses stdlib tomllib on 3.14. Source build would
need `setuptools>=68` and `wheel`; neither is needed for the proposed source execution.

**Declared dependencies:** Pygments source wheel builds require `hatchling>=1.27`;
pathspec builds require `flit_core>=3.2,<5`. No such build tools are proposed.
pathspec's own pure-Python `simple` backend is always available; optional re2/
hyperscan imports and typing_extensions fallbacks must not accidentally bind ambient
packages. Pygments can discover installed entry-point plugins. Qualification must use
an isolated interpreter path and record actual imported modules, not assume isolation
from package versions alone. No accelerator, plugin, colorama, Pillow or documentation
dependency is required for the proposed bounded executor.

## Proposed route — parent approval required before implementation

1. Approve the **official TypeScript release package** plus **unaltered exact-commit
   Python source execution** and explicit Pygments 2.21.0/pathspec 1.1.1 bindings.
   This changes distribution/binding provenance, not analyzer versions or policy.
   No source alternative was provisioned in this follow-up.
2. Recheck the retained archive hashes, then safely extract only into a new owned
   external toolchain directory. Reject links/traversal/collisions; retain complete
   runtime package trees and licenses. Do not compare GitHub archive hashes with
   wheel hashes, synthesize wheel metadata, run setup.py, or install build backends.
3. Launch TypeScript with the already-pinned Node executable and absolute packaged
   `bin/tsc`/`lib/typescript.js`. For Python, propose managed Python `-I -S -B`
   plus an owned, hashed qualification bootstrap that adds only these exact source
   roots and invokes the unchanged upstream module entrypoints. No persistent
   PYTHONPATH/site-packages/.pth edits, environment upgrades, or framework.
   Retain standard-library paths; assert every actual nonstdlib import belongs to
   the approved source roots. Stop rather than install anything if an unexpected
   dependency or packaging-resource requirement appears.
4. Execute the outstanding exact-version help/API and genuine CHECK-TOOLS cases,
   independently per tool, with existing 30/90 light and 120/1200 qualification
   bounds. TypeScript: all six JS/TS suffixes, syntax/checker/diagnostics, module
   aliases, no-findings and Unicode/CRLF. lizard: explicit reader identities,
   reversible MJS/CJS aliases, positive/zero-function/nested/arrow/async/TS,
   real reader failures and recursion diagnostics. Vulture: native 3.14, explicit
   all-file census, confidence 80 positives/negatives/errors and resources.
   Preserve all failures and no synthetic success counts.
5. Rehash source/runtime/dependency imports and produce additive qualification
   captures. Stop for parent tool-gate review; do not implement adapters or mark Q2
   complete. Keep jscpd/Ruff evidence and coverage's Q3 deferral unchanged.

This route appears feasible **without project dependencies, OS changes, new build
tools or substituted analyzers**, subject to actual execution qualification.
Source-origin approval and Python dependency pins are the remaining decision,
not a request to bypass the failed TLS hosts.

## Preservation and limits

Only additive `q2-tools-route-*` repository evidence and owned external inspection
files were written. No source package import, extraction, installer, new child
qualification fixture, agent, commit, browser, OS setting, or project upload.
All shell commands used the existing runner. GitHub reads used standard verified
HTTPS; signed redirect query parameters were removed from this follow-up's metadata.
Original qualification/TLS evidence was not edited.

One helper indentation defect prevented five parallel metadata commands from
starting; corrected before any of those requests ran. The original two TLS probes
were **not rerun**. Their errors and the pre-network helper failures remain in the
session transcript. No timeout occurred. Archives and raw source inspections are
retained for parent review; no background processes or cleanup actions are pending.

`q2-tools-route-manifest.json` records final file hashes, prior-evidence preservation,
bounded runtime/source pin checks and the per-tool **BLOCKED-PENDING-ROUTE-APPROVAL**
status. The earlier CHECK-TOOLS verdict is unchanged.

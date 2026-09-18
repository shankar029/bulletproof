# Independent preliminary review — native JS serialization/candidates

**Verdict: REVISE.** Two substantive native-serialization correctness findings, both P2. These are source-grounded findings, not newly executed reproductions. The concurrent independent verifier's completed report has not been supplied; reconciliation remains pending.

## Scope and identity

Reviewed the frozen increment against HEAD `8881a7e667695345328852ab39157988f9fd868d`, after first reading its handoff and seal. HEAD matches that baseline; Git ancestry confirms preserved native core `886d699a9b8523f2846c65b21fcfd56fc5b3e0dc`. Reviewed the four owned changed files, their native API callers, the Python inventory/canonical-JSON/fixture collaborators, and targeted sections of the actual qualified TypeScript implementation and accepted contracts.

This review covers the native API only: `parserDigest`, `settingsDigest`, `serializeProgram`, and `candidatesForProgram`. It does **not** demand or credit an accepting Context, fixed JSRequest command, R1 ownership/manifests, graph projection, replay, configured JS measurement, scalar collection, or C4 work.

### R1 — Namespace destructuring loses the referenced export

**Location:** `scripts/measure_js.mjs:689–708`, `serializeProgram`'s reference visitor; also the discovery pass at `477–504`.

Consider ordinary, valid source with an inventoried ESM target:

```js
// origin.mjs
export const value = 1;

// use.mjs
import * as ns from "./origin.mjs";
const { value } = ns;
export const answer = value;
```

The binding's `value` is an Identifier whose parent is a BindingElement. It is not a ShorthandPropertyAssignment; `parent.name === node` therefore makes `declarationName` true, and the visitor emits no reference for it. The later use of `value` resolves to the **local binding**, not `origin.mjs`'s export. The `ns` identifier resolves to the module symbol, not its `value` member. No other branch emits the missing property-use relationship, nor does this destructuring produce an outside-model uncertainty site.

This is grounded in the real collaborator, not an assumed checker behavior: qualified TypeScript `lib/typescript.js:91882–91900` returns a declaration's own symbol for declaration names, and has a separate property lookup for a BindingElement's explicit `propertyName`. `isDeclarationName` at `19356–19357` likewise recognizes the binding name. Simply retaining the binding identifier as an ordinary reference would still resolve the wrong symbol.

The related literal-key form `const { "value": local } = ns` is also missed: its StringLiteral property name is neither an ElementAccessExpression nor an identifier handled by the reference-emission branch.

**Impact:** The returned symbol/reference evidence omits an actual namespace member read in a processed file, without disclosing uncertainty. This violates the accepted full-census lexical/property-reference semantics (`q2-js-execution-amendment.json`, `identity_and_projection.dead_symbols`, and JSReference/JSResolution). No claim is made that a current scalar consumer already produces a false dead-export metric; that consumer is not implemented here. The defect is in the native records themselves.

**Remediation:** Handle object BindingElement property reads explicitly using the same checker and the bound object's type. Resolve shorthand and literal-key selections to the source property symbol while retaining the distinct local binding identity. For genuinely computed/unsupported selections, emit explicit dynamic/outside-model evidence rather than silently omitting the relationship. Add focused real-source assertions that the property-use target equals the exported declaration's ID, not merely that all emitted IDs exist.

**Existing-test gap:** `scripts/tests/measure_js.test.mjs:101–113` checks an object-literal shorthand, `ns['café']`, and computed element access. `scripts/tests/test_measure_js.py`'s `references.ts` fixture supplies those forms, not namespace destructuring. Those successful checks do not exercise this branch.

### R2 — A literal dynamic import becomes “computed” when it has options

**Location:** `scripts/measure_js.mjs:625–634,656–659`, `moduleReference` and its CallExpression dispatch.

For a valid call such as:

```js
export const load = () => import("./origin.mjs", {});
```

the caller passes `null` instead of the first argument because `node.arguments.length !== 1`. `moduleReference` consequently emits `specifier: null`, `resolution: "dynamic"`, no targets, and a `computed-import` site whose reason is “Computed module specifier”. It also omits the literal SyntaxEvidence import. The specifier is nevertheless a literal, and the empty options object does not make it computed.

Qualified TypeScript explicitly supports this distinction: `lib/typescript.js:82205–82236`, `checkImportCallExpression`, reads argument zero as the specifier, checks argument one as import options, and resolves the module from the specifier. Thus the adapter is discarding information available from its own Program/checker and NodeNext resolution model.

**Impact:** Known literal dependency evidence is lost and an incorrect outside-model reason is returned. The accepted JSModuleReference invariants and `identity_and_projection` require literal syntax sites and their module-reference records to retain the literal target; the presence of an options argument is not a computed specifier.

**Remediation:** Separate dynamic-import argument handling from the `require` arity rule. For supported import calls with an options argument, pass the actual first argument through literal resolution. Preserve any separately justified options limitation without changing a known literal specifier into a computed one. Add a real two-argument literal-import fixture asserting the matching SyntaxEvidence import and local module-reference target, alongside a genuinely computed-specifier control.

**Existing-test gap:** Neither owned native fixture file exercises dynamic `import()` with an options argument. The test harness's own `import()` calls load the controller; they are not serialized subject-source coverage.

## Other reviewed behavior and test relevance

- Candidate enumeration uses the saved Program and a private serialized-syntax copy, checks matching inventory/source identities, and uses AST operator tokens rather than source-text regexes. Operator-family order matches the existing JS families in `scripts/mutate.py:49–67`. It selects by family and byte location per changed line, without sampling or mutant execution.
- Type nodes, import/export declarations, declaration files, ambient declarations, comments, regex bodies, and literal template text are excluded from candidate operators; executable interpolation and JSX/TSX expressions are traversed. Return/expression replacement uses an empty statement rather than deleting the syntactic parent slot. No additional high-confidence candidate-generation defect was found. Invalid generated operator syntax is explicitly allowed to become a later ungraded result by the original contract's `candidate_generation.invalid`; its possible existence is not itself a defect here.
- SourceBytes preserves BOM/CRLF and converts UTF-16 boundaries to UTF-8 byte coordinates with split-surrogate rejection. Candidate whole-file hashes and IDs use the original bytes/span plus replacement. The Python harness independently reconstructs the fixture candidate identities with `evidence._json_bytes`, rather than merely comparing two JS assertions.
- Parser identity binds adapter bytes, qualified compiler/resource locators and bytes, runtime identity, and fixed settings while excluding controller-copy location. Serialization/candidates recheck compiler and subject bytes before and after work. Private census/diagnostic copies avoid accepting edits to those public result arrays. These native checks are not authentication of a Context, config Artifact ownership, or a future measurement lifecycle.
- Alias/reexport resolution, namespace element access, merged-declaration ID construction, lexical descriptors/occurrences, external/unresolved classification, package/config/suite root origins, and suppression/diagnostic serialization were inspected. No additional high-confidence finding is asserted for those branches. Explicit merged declarations, import-equals, and namespace-reexport fixtures remain absent from the owned suite, as the handoff already acknowledges; their coverage is not inferred from alias-cycle tests.
- Public roots are derived from supplied source-bound config/package/suite data. Unsupported package conditions remain explicit outside-model sites. This is not validation of future staged input ownership or proof of package-metadata admission completeness.
- Real collaborators matter here: `Q1Fixture` creates and materializes real Git revisions with baseline Python files, and the tests obtain inventories through `measure.inventory(..., include_js=True)`. Its Q1 graph/controller artifacts do not establish staged JS ownership. `measure.validate_config` still rejects nonempty JS entrypoints; native fixture configuration bypasses that unsupported integrated path deliberately.

The retained final console records **15 Python methods passing in 383.070 seconds**, with **13 nested native invocations**, not 28 tests. The actual-source-copy counts of **56** (`evals/lib/score.mjs`) and **68** (`scripts/native_result.mjs`) are candidate enumeration, not executed root mutants. The fixture candidate loop reconstructs bytes/IDs and syntax-preflights three selected fixture edits; it is not an execution proof for every candidate.

The development failures, failed `final-01` timeout, one bounded smaller-scope retry, and successful `final-02` remain distinct. Full descendant cleanup remains UNKNOWN; the historical symlink limitation remains unverified. Planner **37+4/126** is separate app-regression evidence, not this review's proof or a fresh-agent full-workflow exercise.

## Hash reconciliation

Seal SHA-256 independently matches the expected value:

`c43769d83411dd41063be59a77e87918991673f360ec8b759f1a22558bc528da`

All **59** entries across `authorities` and `owned_files` matched their declared byte lengths and SHA-256 values at initial inspection and again immediately before writing this report. No new pin archive was created.

| Authority | Unchanged SHA-256 |
|---|---|
| Original measurement contract | `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12` |
| Root amendment | `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1` |
| JS revision 3 | `887c8a3ba5dd9f8efd32081b3c3e20fbea8a0fada67349a1555bcda34f7b4c9e` |

| Owned changed file | Reviewed SHA-256 |
|---|---|
| `scripts/measure_js.mjs` | `35acb58ccd11dce9daa601e640c47b763e8625c84919158610cf33107f4b46bc` |
| `scripts/tests/measure_js.test.mjs` | `cc9a6476f570195e37d03f57c82dca29dc26c2472be61e66af0006714d48967e` |
| `scripts/tests/test_measure_js.py` | `42a1c60aafc131598c1dde2294edc135a375ad60b479ce516920809d63fb806f` |
| `references/quality-metrics.md` | `f3bdb0f7d6c6089fd24989230d56a5e1b5fbe19cf65edcb772c30cccff984eb5` |

All 13 final invocation records' executing-source hashes were reconciled against **12 unique current files**, without rerunning their commands. In particular:

| Unchanged collaborator | Current/final-record SHA-256 |
|---|---|
| `scripts/measure.py` | `b5a824cd84a4a63bb1a6ec5cb6d2e09426614006b12f0b9ef867f040439c4db9` |
| `scripts/measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |
| `scripts/probe.py` | `d7be5050cf70cb836e46f0b661632b2d426d6bdc4684f1b54aa9061d61948904` |

Git's baseline diff lists the four owned files plus unrelated `evals/report.md`; the latter was not reviewed or modified. The three collaborators above have no baseline diff.

## Disposition and execution limits

**Revise R1 and R2 within the native serializer and reconcile focused real-source evidence before preliminary approval.** No redesign or future-layer implementation is requested by this verdict.

This assignment ran no tests/suites, qualification, installers, agents, mutations, commits, or pushes. External read-only Git commands were bounded through the managed Python `scripts/run.py --idle 30 --max 120`; other inspection used read/search tools and built-in PowerShell hashing. No verifier in-progress file was consumed or polled. The only authored file is this report.

Human sign-off remains **unconfirmed** and publication remains **403-blocked**, as provided by the parent; neither was independently exercised or cleared. Stop here pending the parent's completed verifier report for reconciliation in this same review context.

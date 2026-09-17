# Q1 implementation checkpoint

## Status

**Blocked on one concrete API clarification; no implementation or tests yet.**
Resumed the parent acceptance state and independently accepted revision-2 Q1
design. This is not a new design rejection, functional pass, Q pass or release
claim. Parent owns `state.md`; it was read, not modified.

Read CONTRIBUTING, the complete measurement HTML/contracts, r2 review and
correction dispositions, and existing probe, evidence, runner and test helpers/
probe tests. The codebase uses standard-library Python with real Git/process
fixtures. Existing lower-layer discovery ownership and raw reconciliation need
implementation; missing APIs were not executed or described as behavioral red.
Concurrent guard files were neither read nor edited.

## Clarification requested

**FACT:** `records.Context.fields` has `output_manifest: Artifact`, but neither an
artifact/run root nor an `OwnedArtifactManifest` value. `Artifact.path` is
relative to an owned run root. `parse_files(context, inventory, config)` must
produce persisted `SyntaxEvidence` artifacts, yet receives no manifest or root
against which to resolve/write them. `OwnedArtifactManifest.root` becomes an
explicit input only at the later validation boundary. The existing probe
constructs its run directory from repository, slug and run ID, but Context
does not carry slug and its target/controller roots are not artifact roots.

**Recommended smallest clarification:** add `run_root: AbsoluteRoot` to Context.
It is an existing, uniquely owned external scratch directory, separate from
base/head/controller source roots. `Context.output_manifest.path` and generated
syntax/raw Artifact paths resolve only beneath `run_root`. Require
`OwnedArtifactManifest.root == Context.run_root` and matching run IDs. Preserve
strict paths, exact reserved-output ownership and source/output disjointness;
probe archives exact individually reserved output paths, never a broad excluded
subtree. No parser signature change, reverse import, Q2 adapter or implicit cwd
fallback is needed.

**Pending:** explicit acceptance of this clarification before implementation.
Do not silently invent a root, embed raw records in a field typed Artifact, or
write artifacts into source directories. No parent-owned design file changed.

## Planned bounded acceptance after clarification

1. One lower-layer census with explicit revision/root/source identity; exhaustive
   pending/unsupported entries, exclusions and enumeration errors.
2. Shared Python AST parse receipts and syntax artifacts; literal local/external
   edges, unresolved and outside-model sites, canonical elementary cycles and
   the five compiled architecture rules.
3. Source/raw recomputation rejects omissions, stale/revised identities, receipt,
   graph and aggregate corruption; no count-only identity comparison.
4. Configured public CLI on real Git fixtures exposes graph observations while
   all nine metrics remain required, JS stays unsupported and absent adapters
   remain incomplete/fail.
5. Targeted regressions and self-review only, followed by parent verification/
   independent review. No external dependencies, broad root probe, mutation,
   native/guard edits, commit or publication.

## Executed commands and results

Working directory:
`C:\Users\shbs\.copilot\repos\copilot-worktrees\bulletproof\shbs-microsoft-crispy-system`

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 30 --max 90 -- git --no-pager status --short --branch
```

Exit **0**. Observed branch `shbs-microsoft-workflow-app-verification`, no
measurement source edits, and existing parent/guard-owned changes. Those changes
were preserved; no whole-tree cleanliness/freshness claim.

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 30 --max 90 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -c "import hashlib,pathlib; names=['.ai/workflow-reliability/measurement-enablement.html','.ai/workflow-reliability/measurement-enablement-contracts.json','.ai/workflow-reliability/evidence/measurement-design-review-r2.md','scripts/probe.py','scripts/evidence.py','scripts/run.py','scripts/tests/helpers.py']; [(print(n,hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest())) for n in names]"
```

Exit **0**. Exact input SHA-256:

| Path | SHA-256 |
| --- | --- |
| `.ai/workflow-reliability/measurement-enablement.html` | `fa7b33541c2952c67e62d5675531de8b0daaa6e00716c8c0909f3e283e1cee2c` |
| `.ai/workflow-reliability/measurement-enablement-contracts.json` | `3eea18cc11522426559c9890e1a4ac7a9de8716495131018b3ce2454691dbff5` |
| `.ai/workflow-reliability/evidence/measurement-design-review-r2.md` | `02a86a471880ac6e220f188b73c06dd645b937205f8e55303bc46c6fcb96ec8d` |
| `scripts/probe.py` | `993d41638aeb0bb8b62ef0084b58f309139a3b1af11a113a159bd35c90466a82` |
| `scripts/evidence.py` | `da55b3ef252c69e9027413e5efe2f35ed9e50a112ad4312c1f3233d141c5f3c4` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |
| `scripts/tests/helpers.py` | `2694cd24dd07b1a6e3ceff7ac2addb7d4fc8bc40ee197f6d3c4206d281bf2068` |

Tests executed: **0**. No numerical measurement or coverage proof produced.

---

# Q1 implementation result — after the approved clarification

The section above is the preserved **pre-code** checkpoint, not current status.

## Current disposition

**FACT: local Q1 functional implementation and targeted regressions are green.**
Parent approved `Context.run_root` and updated the normative contract. This worker
implemented only the assigned inventory/Python-graph/probe slice and its tests.
Parent still owns independent verification, independent review, state/docs
integration and acceptance. **No Q pass, final quality gate, coverage score,
mutation-on-changed-lines result, release or publication is claimed.**

Final writes:

- `scripts/measure.py`
- `scripts/measure_graph.py`
- `scripts/probe.py`
- `scripts/tests/test_measure_inventory.py`
- `scripts/tests/test_measure_graph.py`
- `scripts/tests/test_measure_q1_integration.py`
- This evidence file only under `.ai/`.

No agents, installations, dependency/framework/global-config additions, broad
root measurement, guard edits, native/mutation/evidence/runner edits, commits or
publication. Git identity settings used by the existing helper belong only to
its temporary fixture repositories.

## Delivered behavior and observed proof

| Requirement | Implemented behavior | Persisted test proof |
| --- | --- | --- |
| Canonical lower-layer census | `measure` owns constants and one walker; `probe.code_files is measure.code_files`. Inventories bind explicit revision, Git root and broad source hashes. Entries remain immutable/pending; all parser outcomes live separately. | `InventoryTests`: standalone imports; ignored-looking tracked source; Python/MJS/CJS/Go; examples/packages; renamed/deleted/untracked files; omission/revision/changed-map rejection. |
| Failure-aware paths/census | Strict file paths versus root-capable directory paths, linked-path rejection, deliberate encountered exclusions, explicit walk/stat/read diagnostics. `code_files` raises rather than returning shortened success. | Real Windows junction, mandatory-sharing file-read failure and directory-enumeration failure; traversal/root-file/absolute/alias inputs and case-fold source-root collision. No mocked successful census. |
| Shared parsed Python inventory | AST parse plus compile without execution, source-bound syntax artifacts and exactly one receipt per entry including empty/zero-import files. Unsupported MJS/CJS/other languages remain present. | Python source that would raise if executed is not executed; contextual invalid Python fails; zero-import receipts, UTF-8/CRLF inputs and mixed-language receipts are retained. |
| Literal graph and identities | Absolute/relative/function-local/conditional imports, package/child/namespace resolution, external terminals, unresolved local imports and dynamic-site disclosure. SCC-pruned bounded elementary directed cycles retain direction and self loops. | Actual Git fixtures for missing/ambiguous/escaping imports, directed cycles, equal-count replacement, and real dense-graph budget exhaustion. Exhaustion is unavailable/null, not a truncated zero. |
| Architecture | All five compiled rules; compare prohibited-relation identities, not just totals. Foundation runtime commands are disclosed, not falsely resolved or counted as dynamic-loader violations. | All five rule IDs observed from actual parsed fixture source; new violation replaces two old violations and still fails; aliased builtin/importlib loading is disclosed. |
| Producer-owned validation | Re-enumerate immutable base and current head, reparse exact source, reconcile raw syntax/graph and receipts, verify owned manifests, config/approval/controller/tool/source binding, then recompute observations and all nine metric decisions. | Rehashed graph and syntax forgeries fail; missing/duplicate manifest records, escaping reservations, receipt/run/revision/tool/policy/source corruption, omitted files, changed-map tampering, scalar-status fabrication and 16 report-summary corruptions fail. |
| Public probe | `--measurement-config` exercises real private Git subjects, graph collection, validation-before-publication, and individually reserved raw archives. Legacy default entry points use common census/policy helpers. | Actual public CLI from nested cwd: Python graph values measured, seven remaining required metrics unavailable, incomplete/fail exit 1. Mixed MJS/CJS root retains every unsupported receipt and all nine missing requirements. Replaced cycle fails at equal count. Invalid config/policy and input/output overlap exit 2 without overwriting input. |
| No optimistic proof | All nine metric IDs remain required. No scalar/coverage adapter is fabricated. Configured mixed-suite mutation is unavailable in Q1; legacy strict native mutation remains unchanged. | Public CLI asserts exact nine-metric set, explicit missing set and incomplete/fail. Existing native fixture still produces a genuine measured 100% native assertion-kill result while its overall report stays incomplete; this is fixture regression evidence, not a root mutation score. |

## Implementation decisions within the accepted boundary

- **Accepted clarification used:** `Context.run_root` is external, owned, canonical
  and disjoint from subject/controller inputs. Manifest root must match it.
- **Private materialization:** local Git clones with `--no-hardlinks`, detached
  at the immutable IDs; head overlays the observed working tree, including
  untracked/ignored normative bytes and deletions. Base must remain its clean
  immutable Git tree. The controller bundle is copied separately and checked
  against the actual executing measurement modules.
- **Exact config binding:** Context contract artifacts include the actual config
  file and approval artifact. The normalized config must decode from exactly one
  hashed source artifact; approval bytes and the full source snapshot record are
  reconciled. This is consistency/source binding, not authenticated approval.
- **Compiled cycle bounds:** 100,000 enumeration steps, 10,000 cycle outputs,
  five seconds. A reached bound makes dependent graph proof incomplete; no result
  tail is dropped into a passing count.
- **Identity semantics:** cycles hash canonical rotation of ordered paths.
  Architecture identities are unique prohibited rule/source/target relations;
  moving or repeating the same relation does not create a new violation merely
  because its line number changed.
- **Q1 config support:** requires the full declared profile, all five rules,
  source roots, real suite file/cwd references, approval and unchanged floors/cap.
  Tools and JS entrypoints are empty in this slice; Q1 does not qualify or execute
  configured mixed suites. It has no scalar/coverage/mixed-mutation importer.
  Unconfigured native-only behavior and its strict validator remain intact.
- **Archive mapping:** raw `Artifact.path` names resolve in the external live run
  root during production/validation and identically beneath
  `.ai/<slug>/evidence/runs/<run_id>/measurement` after archival. The archived
  manifest retains its historical external invocation root. It is not a live
  input root or reusable score for another run. Public CLI tests independently
  read each archived artifact's exact bytes/hash.
- Source exclusions reserve individual possible syntax outputs plus graph and
  manifest files before snapshotting; they do not exclude an evidence subtree.
  Tests prove publishing does not immediately stale the source snapshot, and
  adding an unrelated evidence file does change it.
- A failure before a valid source snapshot/private subject can be established
  aborts the configured CLI with exit 2, rather than inventing source proof.
  Inventory-level I/O failures preserve explicit failed census diagnostics;
  parse/unresolved/unsupported/budget failures on valid subjects yield
  incomplete/fail measurements. No failed census establishes greenfield.

## Self-review and red/green record

Initial Q1 inventory/graph check: **17 tests passed in 224.568 seconds**.
After public-CLI integration and baseline/controller checks:
**23 Q1 tests passed in 371.456 seconds**; legacy probe **19 passed in
58.183 seconds**. These are intermediate, superseded checkpoints.

Self-review found two real gaps:

1. The approved policy/config object was compared but was not required to decode
   from its actual source config bytes.
2. Source validation compared files/hash but not the complete normalized source
   record, so a substituted binding mode was accepted.

The persisted `test_config_bytes_and_source_binding_mode_cannot_be_substituted`
reproduced **two assertion failures** (`ValueError not raised`), exit **1**,
one test in **16.757 seconds**. This was real behavior under implemented APIs,
not a missing-API/import failure. The source-artifact and full-record fixes
described above close both gaps. Final regression includes those assertions plus
config/output overlap, changed-map/manifest corruption, aliased loaders and the
actual cycle bound.

**Final result: 28 Q1 tests passed in 442.243 seconds; 19 legacy probe tests
passed in 58.009 seconds. Both commands exited 0.** No source/test edits were
made during these final runs. No skipped test outcomes, retries or timeout kills
were reported. The six owned Python files compile without bytecode output and
have no trailing whitespace. Tracked probe `git diff --check` exited 0.

## Exact final commands

Working directory is the repository root recorded in the pre-code checkpoint.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -m unittest discover -s scripts/tests -p 'test_measure_*.py' -v
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -m unittest discover -s scripts/tests -p 'test_probe.py' -v
```

The intermediate 17/23 and 19 checks used these same commands before the
subsequent corrections/additional tests. The focused behavioral-red command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 120 --max 900 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -m unittest discover -s scripts/tests -p 'test_measure_q1_integration.py' -k binding -v
```

Compile/hash/whitespace check, exit 0:

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 30 --max 90 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B -c "import pathlib,hashlib; names=['scripts/measure.py','scripts/measure_graph.py','scripts/probe.py','scripts/tests/test_measure_inventory.py','scripts/tests/test_measure_graph.py','scripts/tests/test_measure_q1_integration.py']; [(compile(pathlib.Path(n).read_bytes(),n,'exec'),print(n,hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest())) for n in names]; bad=[(n,i) for n in names for i,l in enumerate(pathlib.Path(n).read_text().splitlines(),1) if l.rstrip()!=l]; print('trailing whitespace:',bad); assert not bad"
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts\run.py --idle 30 --max 90 -- git --no-pager diff --check -- scripts/probe.py
```

## Final owned-file SHA-256

| Path | SHA-256 |
| --- | --- |
| `scripts/measure.py` | `4754fe05621b81a8d499c38dbb913619dd43af50782d07b058849d50994ef8ed` |
| `scripts/measure_graph.py` | `17f50ca7b304bba114131d7578d0250979df3d113201593d99b67e8479fa5245` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/tests/test_measure_inventory.py` | `62fcf7a14bbc9dda36a5a6a2497935e9d8fca51f7265afa73d906f495fb0c2fe` |
| `scripts/tests/test_measure_graph.py` | `875d19c96f404ff3ca41a0644de759c8fc0a5f485194773b9869d3e5c5b74c74` |
| `scripts/tests/test_measure_q1_integration.py` | `889e5ab71f3e8d9cb16b9ded4dc9327fcf1d5f4820426e0773f17c8f1b4976a9` |

Parent-amended HTML hash:
`f26b65924ab0cc4cadd1d0cde43fb68a804729f7d4200498902834097d5846c2`.
Parent-amended contracts hash:
`a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12`.
Independent r2 review hash remains
`02a86a471880ac6e220f188b73c06dd645b937205f8e55303bc46c6fcb96ec8d`.

Untouched boundary hashes rechecked: `mutate.py`, `evidence.py`, `run.py` and
`tests/helpers.py` match the recorded input hashes above/original accepted
design correction. Native reporter hash is
`528aeec659fde03cab9edd3167a8b2bc184b7194a3f534dd13a4e0a0c38163e0`.
No whole-tree freshness statement is made while parent/C1 writers are active.

## Handoff limits

Stop here as assigned. Parent performs independent verification/review and
records acceptance in its state. Q2 tool qualification/scalars/JS parser,
Q3 coverage, Q4 configured classified mutation and Q5 final frozen-tree proof
remain open. Full repository Python/native/corpus regressions, actual root
quality/mutation measurements and release acceptance were not run by this worker.

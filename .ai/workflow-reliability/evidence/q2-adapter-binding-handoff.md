# Q2 adapter preimplementation stop: original artifact locator

## Result

**BLOCKED before production changes.** This is a concrete input/staging contract
gap, not a renewed design/workflow exercise, missing-tool claim, Q1 regression,
or objection to the disjoint CLI writer. Q2 implementation and its acceptance
checks remain unfinished. No metric observations or passing quality scores exist
from this work.

Observed HEAD: `ee6e0e34e78b70fcb672074af0a76f51fe937e1a`, branch
`shbs-microsoft-workflow-app-verification`. Existing `state.md` and `evals/report.md`
changes were present before this work and were not edited here. No commit,
push, install, nested agent, mutation or tool-source change occurred.

## Exact gap

1. **FACT — normative input paths:** measurement-enablement-contracts.json:226
   says artifact paths are owned-run relative, except source approval_artifact.
   ToolBinding:241-248 has executable, module_path, observed_version, sha256,
   qualified_api, help, configuration and qualification. It has no locator for
   the original help/configuration/qualification artifact root.
2. **FACT — original authority is required:** the same contract:337 requires
   approval/tool artifacts to be checked against approved originals, not trusted
   merely because they occur in the run manifest.
3. **FACT — actual qualified locations:** q2-tools-manifest.json's jscpd and Ruff
   bindings use absolute paths to existing qualification evidence. Their ten
   help/configuration/qualification artifacts are real and hash-match. All ten
   paths are rejected by the existing canonical relative-path validator.
   These are historical qualification locators, not valid production Artifact
   paths. Translating a locator is necessary; weakening Artifact path validation
   is not an acceptable solution.
4. **FACT — actual configured flow:** scripts/probe.py:507-558 loads the source
   config, then creates fresh scratch/controller/raw directories and constructs
   Context. Its only configuration-location argument is --measurement-config.
   No original-artifact root or original-to-owned artifact mapping enters this
   flow. The raw directory starts empty. Existing measure.validate_config
   takes `(config, root)`; this expected Q1 interface is not itself a defect.
5. **INFERENCE — bounded blocker:** the existing configuration Artifact can
   describe qualified roots/resources/settings *after its bytes are located*,
   but cannot locate its own original bytes. Implementing current public probe
   integration requires deciding that input resolution seam. Resolving paths
   against the repository instead would contradict item 1; deriving them from
   executable/module parents would invent an unapproved directory convention;
   embedding the session evidence/helper path would violate portability and the
   assignment. No such fallback was implemented.

This does **not** claim that direct callers cannot populate Context.run_root.
They can. It identifies the missing original-input authority in the fresh public
probe flow and subsequent validation; prepopulating arbitrary bytes alone does
not satisfy item 2.

## Bounded amendment requested

Recommended: approve **one explicit read-only original-tool-artifact root,
persisted in the source-bound Q2 configuration**, with a defined resolution rule:

- configuration input ToolBinding help/configuration/qualification refs resolve
  strictly under that canonical external root;
- stage only those exact hash/length-checked files into the uniquely owned run
  root, using deterministic relative paths and exact manifest ownership;
- validators recheck originals and owned copies; the locator/configuration and
  tool/resource bytes participate in the same base/head freshness binding;
- retain all current traversal/link/collision checks, tool-specific settings
  validation, empty Q1 mode, public core compatibility and all nine metrics;
- no callback, executable import hook, exemption, threshold or policy override.

This needs parent acceptance of the narrowly changed configuration/path
semantics before code. A documented source-relative ToolBinding-input exception
analogous to approval_artifact is another possible decision, but it is **not**
assumed: it changes the stated root semantics and must respect the restriction
on repository-hosted tool resources/manifests.

No proposal to change the graph/Observation/RawMetricEvidence schema, frozen
baseline policy, workflow core, runner, coverage or mutation is made.

## Actual diagnostic evidence

Replay (working directory: this worktree; use the actual managed Python):

```powershell
& 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -B scripts/run.py --idle 30 --max 90 -- 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe' -I -S -B -u .ai/workflow-reliability/evidence/q2-adapter-binding-check.py
```

The diagnostic is intentionally single-use: it refuses to overwrite its original
results. A later replay must receive a separately owned evidence destination,
not delete the historical result.

Observed exit **0** means the diagnostic completed, **not Q2 passed**:

- Read and hashed all nine required qualification report/manifest/root/summary
  documents; decoded all six JSON documents with duplicate-key rejection.
- Rehashed **3,348/3,348** extracted source/resource files against the existing
  complete pins; both retained native executable hashes also match.
- Verified ten native original artifact hashes/lengths and observed ten absolute
  path rejections.
- Copied those ten actual artifact bytes into a short new owned OS-temp directory,
  verified each copy, then removed that owned directory. No deep worktree TEMP,
  installation, tool invocation, timeouts or process cleanup was needed.
- Rehashed the three relevant production files and normative contract before
  and after; all four unchanged. No whole-source-freeze claim is made.

Raw result: `q2-adapter-binding-check-results.json`.
Diagnostic source: `q2-adapter-binding-check.py`.
No unit/integration suite or CHECK-SCALARS/CHECK-GRAPH/CHECK-JS-PARSER/
CHECK-RECONCILE acceptance run occurred. Installed analyzer definitions were not
used to implement or invoke an adapter; their required implementation-time reads
remain pending. Prior tool qualification is retained, not relabeled as a fresh
API qualification run.

## Handoff and resume

Only the diagnostic, its results and this additive handoff were written.
Parent owns state/report updates. No production files were created or changed.
All Q2 production work remains pending: strict bindings/entrypoints, shared JS
syntax/symbol/candidate adapter, scalar collectors, integration and raw
reconciliation, actual two-revision tests. Q3/Q4 remain deferred.

After the parent resolves the single original-artifact locator, resume the
approved Q2 implementation and read the exact installed definitions/help before
their use. No full workflow restart or new tool acquisition is needed.

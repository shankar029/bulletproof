# Q2 original tool artifacts — bounded amendment rationale

**Proposed; awaiting focused independent review and parent release.**
Normative amendment: `q2-tool-input-root-amendment.json`, bound to contract SHA-256
`a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12`.

## One change

Add `MeasurementConfig.tool_artifact_root`, a canonical existing absolute
read-only **data** directory, required exactly when `tools` is nonempty.
Empty Q1 configs omit it. Keep `validate_config(config, root)`, Context,
Artifact/manifest/report shapes, metric policy and runner/guard interfaces.
“Read-only” means no adapter writes to originals, not an ACL change.

## Reuse originals, including task evidence

**FACT:** `probe._snapshot` includes the repository broadly and excludes only
exact outputs (`probe.py:372–380`). `_copy_subject` copies observed ignored
normative inputs and verifies bytes (`463–481`). The configured flow reserves
archive paths before snapshot/publication (`507–580`). Consequently an existing
`.ai/.../evidence` directory is suitable: its qualification JSON/logs are
provenance, not package manifests. Requiring duplicate external originals would
add a provenance copy without an isolation benefit. Packages/binaries/resources
remain external. Referenced original files must not overlap any output; an
evidence directory merely **containing** the later run directory is not overlap.
No new source exclusion or whole-directory staging is permitted.

## Unambiguous roots and ownership

At intake, ToolBinding artifact `path` resolves only under `tool_artifact_root`.
After strict byte-copy staging, the **same unchanged relative path/hash/length**
resolves under `Context.run_root`. Original rechecks explicitly use the original
root; staged consumers require manifest ownership. Neither can fall back to the
other. The locator persists in the source config, including its copied head
version; both revisions use that same authority, not historical-base tool config.

Reserve the exact selected path set before snapshot/tools. Use existing manifest
role `qualification`, revision `null`, with one row per unique artifact.
Protect `manifest.json`, `base/**`, `head/**` and every generated path.
Reject traversal, links/junctions, hardlink aliases, nonregular files, conflicting
or case/prefix-colliding paths, existing destinations and source/output overlap.
Identical cross-tool references share one row; duplicate qualification-list
entries reject. Fresh staged copies must have independent physical identities.

Recheck original/copy hashes and lengths before execution and during/after raw
validation, then before publication. Bind config/locator, originals/copies and
actual qualified tool/runtime/resources into the same base/head toolset digest.
Repository originals additionally remain in the broad source snapshot; external
originals require live access at validation. Hashes establish consistency, not
authenticated provenance or a filesystem lock.

## Failure, proof and release

Invalid configuration, overlap or changed proof rejects through the existing
library/exit-2 boundary. Genuine collector unavailability remains explicit,
incomplete/fail and exit 1; missing coverage/mutation still block Q.
The amendment specifies five smallest test groups: Q1 compatibility, real
two-revision staging, filesystem collisions, original/copy/resource tampering,
and configured-probe freshness/error behavior. **None ran in this amendment.**

Successful guarded metric attachment is separately deferred. No ad-hoc run-ID,
registered-command, source-projection or report-validation bridge is added.
Only these two documents are delivered; implementation awaits parent release.

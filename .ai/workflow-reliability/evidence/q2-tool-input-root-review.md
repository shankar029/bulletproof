# Q2 tool-input root: focused independent review

## APPROVE

No material design gap found in the pinned amendment. No correction is required before parent release to the original Q2 implementation owner. This approves only the one configuration locator and its specified staging/revalidation semantics, not an implementation or passing quality result.

Reviewed against the supplied HEAD `ee6e0e34e78b70fcb672074af0a76f51fe937e1a`; no Git command was executed to independently attest HEAD. Reviewed production-file hashes are recorded below. Concurrent CLI/shared-state work is outside these pins.

## Independently checked grounding

- **Conditional configuration and root flow:** `scripts\measure.py:411–421,474` currently accepts the exact Q1 field set, rejects nonempty tools, and returns the same config. Amendment `configuration_extension` and `integration` add the conditional locator without changing `validate_config(config, root)` or the empty-tool binding. `scripts\probe.py:507–512,545–564` actually loads config from source before creating the empty raw root and constructing Context. The absolute original locator can survive the unchanged head-config copy; the same Artifact-relative path subsequently denotes the staged file under `run_root`. Explicit original rechecks retain the original root. There is no fallback or baseline-config dependency.
- **Actual locators/formats:** `q2-tools-manifest.json:9–42,80–113` has absolute historical help/configuration/qualification locators, including plain-text `.stdout.log` files. All ten referenced local originals were independently checked for exact locator, SHA-256 and byte length. Their common existing evidence directory permits a single root and canonical relative refs without moving originals or modifying historical records. `q2-tools-source-manifest.json:186–216` independently distinguishes external package/resource roots from repository evidence locators; it is not itself a production ToolBinding. No root-wide staging is implied.
- **Existing primitives are compatible, not a complete staging implementation:** `scripts\measure_graph.py:28–87` provides duplicate-key/nonfinite JSON rejection, strict relative names, canonical root/component checks and byte-based Artifact hashing. `read_owned` at `480–487` checks ownership but then **decodes JSON**: it cannot directly consume text help/log artifacts. Use its ownership checks with byte reads for those formats, as amendment `integration.reuse` permits; do not reinterpret text as JSON. `persist` at `90–96` is likewise a JSON writer, not the required exclusive byte-copy staging API. The amendment already explicitly requires fresh exclusive copies, regular-file/link checks and identity checks beyond these primitives.
- **No shape change is needed:** the contract's `OwnedArtifactManifest` at `measurement-enablement-contracts.json:330–337` already permits `role: qualification`, `revision: null`. Existing `make_manifest(context, base, head)` at `scripts\measure.py:477–487` reconstructs sorted owned inputs, and `validate_observations` at `571–576` compares the whole reconstructed manifest and its file. Adding the unique selected qualification set fits that shape; originals remain independent authority, not manifest assertions.
- **Repository evidence remains source-bound:** `scripts\probe.py:372–380,463–481` and `scripts\evidence.py:40–115` really perform broad source observation and copied-head byte verification. Snapshot exclusions also suppress descendants (`evidence.py:66–67`), so the amendment correctly requires original/config/source versus exact-output and prefix/alias checks **before** exclusions/snapshot. An ancestor evidence directory is not itself a conflicting selected file. `probe.py:532–542,566–580` supplies the existing reservation, final freshness and archive-publication seams. The amendment preserves them while reserving all selected/generated paths and protecting `manifest.json`, `base`, and `head`; it adds no evidence-directory exclusion.
- **Identity and producer validation:** `scripts\measure.py:490–522` observes regular-file physical identities across the four Context roots; it does not supply all proposed same-root hardlink checks. The amendment expressly adds those local checks without incorrectly making the original evidence ancestor a fifth disjoint root. `validate_observations:539–590` binds source config, policy/tool/controller, revisions, immutable base, head snapshot, manifest and producer-derived observations. Amendment `integration:62–65` explicitly extends these seams to rehash originals/copies/resources before each revision and during/after raw reconciliation, then before publication. Both revisions share the source-bound locator/config and toolset, while the historical base stays unmodified.

Read-only denotes adapter access intent, not an ACL or sandbox guarantee. Hash/identity observations are not locking or authenticated provenance. Required metrics, exclusions, thresholds, incomplete-versus-invalid failure behavior and Q1 baseline/frozen-import semantics remain unchanged.

## Verification limits and hashes

**Executed:** read-only source/design inspection, SHA-256 pin checks, and ten original-locator/hash/length checks using native PowerShell. Both requested document pins matched. **Not executed:** tests, probes, collectors, staging, filesystem alias experiments, external tool/resource requalification or Git commands. Qualification records are real producer qualification evidence, not actual metric observations. Full Q2 and root quality remain unimplemented. Successful guarded-probe attachment, its run-ID/source/raw-Context gap, coverage reporting and recovery are separately deferred/out of scope; this review approves no flag, projection or bridge changes. Only this review file was written.

SHA-256:

| File | Hash |
| --- | --- |
| `q2-tool-input-root-amendment.json` | `36514a684b8b1323c752a3559cb49f30be8db61b865435f47682dfd824cda1c1` |
| `measurement-enablement-contracts.json` | `a9a75df36241dc2578ff627703154a2750212c385a163332fe2ccbb47af9bd12` |
| `q2-adapter-tool-input-root-rationale.md` | `2c0be52bff91bc850bd6d481c2a8feb1072e6ebc3dd64b806e8f906f5d77ea67` |
| `q2-adapter-binding-handoff.md` | `d68a525219dc3e42bf28846ffbf9071e79fe08fbb468a3e9d52ffaa08566dc04` |
| `q2-tools-manifest.json` | `7e257ed9f054c33d36bccb32bd6623f3adb9b20521d49d812eecf9903ff777dd` |
| `q2-tools-source-manifest.json` | `95d8cbe19cc03184812c04066ae95c0a10fd806675803c76ac5ead8d018c3f98` |
| `scripts\measure.py` | `5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084` |
| `scripts\probe.py` | `668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083` |
| `scripts\measure_graph.py` | `6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391` |

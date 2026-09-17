# Q1 correction round 1 — pre-code decisions

Parent accepted independent F1/F2 as bugs within the existing Q1 design.
Original verifier evidence and tests are pinned in
`q1-correction-preserved-before.json`; neither will be edited.

## Grounded causes and bounded design

- **FACT — F1:** `_resolve` in `measure_graph.py` consults repository candidates
  before interpreter-owned imports. The original verifier's real CPython
  process and public-CLI fixture disagree. The installed
  `BuiltinImporter.find_spec` and `FrozenImporter.find_spec` were inspected:
  they query runtime tables without importing/executing repository modules.
- **Correction:** query those standard pre-filesystem finders only for absolute
  imports before local lookup. Never classify all stdlib names as unshadowable.
  Keep explicit relative imports local; reject a dotted child of a nonpackage
  runtime module as unresolved. A runtime-owned package remains external.
  Bind interpreter import options/table identity into the parser digest and
  version the corrected static profile. No custom meta-path/path hooks,
  runtime `sys.modules` replacement or arbitrary module execution is modeled.
- **FACT — F2:** common validation compares canonical path ancestry and content,
  not physical file identity. The original fresh-producer counterexample proves
  two distinct paths share writable storage.
- **Correction:** a private common-binding helper enumerates materialized files
  in the supplied base/head/controller/run roots, excluding only top-level Git
  metadata from source roots. Use `(st_dev, st_ino)`, the installed `samestat`
  identity semantics, to reject cross-root aliases even under different names,
  including non-code normative files. Do not reject independent equal-content
  copies. Reject unknown identities, links and enumeration/stat failures.
  Check before consumption and after recomputation. This establishes observed
  root independence, not an atomic filesystem lease or adversarial sandbox.

## Acceptance and tests

F1: real clean interpreter versus actual produced graph for multiple builtin
names and frozen modules; a shadowable stdlib name still resolves locally;
explicit package-relative namesakes remain local. Original F1 test unchanged.

F2: fresh recollection after actual hard links across base/head, base/controller
and head/controller, with different file names and non-code inputs; independent
copies validate and actual head writes leave the other roots unchanged.
Original F2 test unchanged.

Then pin actual discovered/imported runtime dependencies and run targeted Q1,
the unchanged verifier tests, and legacy probe regressions through the existing
bounded runner. Capture original stdout/stderr bytes, exact argv and before/
after hashes via the additive correction harness. No source edits during those
runs. Final source freeze goes to the parent for original-verifier replay and
separate review; no Q2, quality/release acceptance, agents or publication.

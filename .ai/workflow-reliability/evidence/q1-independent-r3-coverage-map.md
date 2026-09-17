# Bounded r3 correction coverage

The actual correction now derives a complete effective frozen-name table from
the installed CPython runtime, rather than inferring the mode from raw settings.
Read `_frozen_import_binding`, `parser_digest`, the correction result/freeze and
the new owned ten-mode test before replay.

No additional test file is necessary for this bounded replay:

- Unchanged original verifier: real builtin-resolution CLI counterexample,
  fresh base/head hardlink counterexample, relative imports, invalid package
  imports, complete greenfield baseline, ignored/untracked normative census.
- Unchanged r2 verifier: actual environment-on/off native and configured-probe
  resolution with distinct parser/tool fingerprints; fresh hidden non-code
  alias rejection.
- Owned added test: ten actual child modes (default, env on/off, CLI override
  both ways, last CLI setting both ways, -E with both env values, -I with env
  off), second frozen package namesake, effective table/native origin,
  equivalent/different digests and unchanged effective identity after raw
  settings are changed post-start.
- Existing Q1 inventory/graph/reconciliation/CLI tests and scoped legacy probe
  regression cover preserved behavior, including all-nine missing-as-fail.

This does not re-open design or conduct an open-ended defect hunt. No private
API monkeypatching or fabricated census is used. Qualification is bounded to
the available managed CPython runtime, not all Python implementations/builds.

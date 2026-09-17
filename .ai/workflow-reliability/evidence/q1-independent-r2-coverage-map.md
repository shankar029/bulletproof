# Correction verification coverage map

Read the correction result and complete freeze data, actual updated `_resolve`,
`parser_digest`, root-independence scan and validation calls, and added tests.
All 321 owner freeze inputs match preflight. The original verifier file and
297 original evidence/test files are pinned without editing them.

- **Original F1/F2:** all six unchanged original verifier tests are included in
  the independently launched 39-test Q1 discovery. New fixture output directory
  and fresh tag only; production inputs/assertions are unchanged.
- **F1 owner coverage:** actual builtin `sys`/`time`, frozen `os.path`, shadowable
  `fractions`, explicit relative `pkg.sys`, invalid builtin `time.child`.
- **F2 owner coverage:** fresh cross-root aliases with different names/non-code
  source, base/controller and head/controller identities, artifact/source alias,
  independent equal-content write control.
- **Added correction boundary:** installed `--help-xoptions` explicitly supports
  both `-X frozen_modules` and `PYTHON_FROZEN_MODULES`. Check two *actual process*
  modes from the environment: native CPython resolution and configured probe
  must agree, and different effective resolution must have different tool
  fingerprints. No mutated module cache or custom import hook is used.
- **Added correction boundary:** freshly collected shared non-code source in an
  analyzer-excluded hidden directory must still fail physical root independence.
  This distinguishes analyzer exclusions from source-ownership exclusions.

No new Q2 adapter, blanket stdlib classification, scope redesign, mock-success
test, production fix, agent or complete-quality claim.

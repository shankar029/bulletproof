# Q1 fresh-context coverage map (before added regression tests)

Scope: existing accepted Q1 continuation, not new design or Q2 implementation.
Production remains frozen. No shared state writes.

| Contract/check | Existing actual coverage read | Uncovered adversarial boundary selected |
| --- | --- | --- |
| CHECK-INVENTORY | 7 `InventoryTests`: common discovery owner/standalone imports; suffixes and deliberate exclusions; paths/config validation; omitted/revised receipts; rename/delete/untracked; real junction and mandatory-sharing read/walk errors | Ignored **untracked** normative source plus tests/examples/benchmarks in an actual configured CLI; actual <3-file complete baseline |
| CHECK-GRAPH | 12 `GraphTests`: empty inputs; conditional/function/relative imports; equal-count cycle replacement; directed/self cycles; ambiguous/missing/escaping locals; syntax/mixed failure; all five rules; decreased-count architecture replacement; raw/receipt corruption; cycle budget; aliased dynamic disclosure | Actual CPython builtin precedence; module-vs-package import failure; distinguish real runtime resolution from parser self-consistency |
| CHECK-RECONCILE | Graph rehashed raw/syntax corruption; 16 summary mutations; policy/root/controller/config/source/map/manifest corruption in integration | Distinct path roots that still share mutable subject bytes through hard links; transitive controller dependency binding examined separately |
| CHECK-PARTIAL-PROBE | 9 `Q1IntegrationTests`: nested cwd Python CLI, raw archive hashes, mixed MJS/CJS, equal-count replacement, malformed config, config/output overlap, real producer validation | Preserve actual raw CLI stdout/stderr bytes and all fixture inputs/archive files; observe greenfield, ignored/untracked source, and failing resolution boundaries without claiming reusable archival validation |
| AC02 | Nine required metric fields, incomplete/fail, unsupported receipts, aggregate forgery tests | Additional public-CLI failure-sensitive checks above |
| AC09 (Q1 portion) | 28 Q1 + 19 legacy probe claimed by implementer; independently rerunning | Before/after runtime/source/test-input pins and bounded independent negative tests |

Legacy `test_probe.py` contains mocked collector-shape checks and synthetic policy
unit inputs; they are regression coverage only, **not real external-analyzer
qualification or complete Q1 proof**. Its native CLI test runs a real fixture
assertion kill. No full root sweep or Q2+ acceptance is authorized.

The new tests use production public measurement APIs and configured probe CLI on
owned real Git fixtures. Native CPython resolution is a separate oracle, not a
copy of `_resolve`. None mocks successful parsing/enumeration/measurement.

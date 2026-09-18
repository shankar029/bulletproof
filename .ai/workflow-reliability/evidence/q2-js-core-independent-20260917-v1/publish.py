"""Assemble a scoped report/seal from actual completed independent evidence."""
import datetime
import hashlib
import html
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture


def load(name):
    return json.loads((OUT / name).read_bytes())


def write(name, value):
    with (OUT / name).open("x", encoding="utf-8") as stream:
        stream.write(value)


def pin(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


data = load("reconciliation.json")
before, after = load("before.json"), load("after.json")
owner = json.loads((OUT.parent / "q2-js-seal.json").read_bytes())
assert before["pins"] == after["pins"]
for index, item in enumerate(before["pins"], 1):
    actual = Path(item["path"])
    content = actual.read_bytes()
    info = actual.stat()
    assert (hashlib.sha256(content).hexdigest(), len(content), info.st_dev, info.st_ino, info.st_nlink) == (
        item["sha256"], item["bytes"], item["dev"], item["ino"], item["nlink"]), item["path"]
    if index % 500 == 0:
        print("Publication: rechecked actual input pins:", index, flush=True)
print("Publication: all input pins matched:", len(before["pins"]), flush=True)
write("publication-pin-recheck.json", json.dumps({
    "attempt": 2, "completed_input_pins": len(before["pins"]), "all_matched": True,
    "idle_seconds": 30, "max_seconds": 90,
    "progress": "Actual completed-pin counts emitted after every 500 files",
}, indent=2))
for item in data["boundary_test_pins"]:
    assert pin(ROOT / item["path"])["sha256"] == item["sha256"]
git = before["baseline"]["git"]["path"]
code, stdout, stderr = run_capture([git, "--no-pager", "status", "--porcelain", "--untracked-files=all"],
                                   cwd=str(ROOT), idle=30, max_total=90)
assert code == 0, stderr
write("final-status.json", json.dumps({"argv": [git, "--no-pager", "status", "--porcelain",
                                                "--untracked-files=all"],
                                      "returncode": code, "stdout": stdout, "stderr": stderr}, indent=2))
main, extra = data["frozen_method_replay"], data["additional_boundary_tests"]
rows = "\n".join("| `" + row["method"] + "` | PASS |" for row in main["methods"])
extra_rows = "\n".join("| `" + row["method"] + "` | PASS |" for row in extra["methods"])
five = [item for item in owner["owned_files"] if item["path"] in {
    "scripts/measure.py", "scripts/measure_js.mjs", "scripts/tests/test_measure_js.py",
    "scripts/tests/measure_js.test.mjs", "references/quality-metrics.md"}]
pin_rows = "\n".join("| `" + row["path"] + "` | `" + row["sha256"] + "` |" for row in five)
report = f"""# Independent Phase 5 — frozen partial Q2 JS parser core

## Verdict and scope

**INDEPENDENT PARTIAL CORE VERIFIED WITH LIMITATIONS. Stop on the frozen handoff.**

FACT: HEAD `fdc6af09a48cbdb21959698453ed2769eec224f4`; owner seal SHA-256
`{before['seal_sha256']}` matched before, after, and immediately before publication.
Original contracts, root amendment, accepted revision 3 and approving second review
remain frozen. Their eventual component requirements were not replaced by this checkpoint.
This verifier resumed Phase 5; it did not reimplement, requalify tools or redesign.

FACT: the exact requested **15 Python methods passed in {main['unittest_seconds']:.3f}s**,
exit 0. The two additional ordinary-discoverable methods passed separately in
**{extra['unittest_seconds']:.3f}s**, exit 0. No test skips, expected failures, timeouts,
failures, harness corrections or test retries occurred. No behavioral-red/implementation
correction is claimed. Outer capture wall time is separately recorded in each result JSON.

FACT: the first post-test publication helper hit idle30 (exit 124) while silently
rehashing the recorded 3,593 input pins; it wrote no report/seal or other exclusive
publication outputs. This actual capture failure is preserved in publication-timeout.json.
The one bounded retry emits actual completed-pin progress every 500 files, retaining
idle30/max90. It does not rerun tests, weaken assertions, change production or increase
timeouts. This report/seal exists only after that retry completed all pin assertions.
The runner attempted PID-tree cleanup; descendant termination remains UNKNOWN.

The seven owner native cases are nested inside seven of the nine core Python methods.
The six TypeScript/lizard/Vulture base/head binding smokes are nested inside ONE selected
regression method. They are not extra Python methods. The added native boundary invocation
and direct-command negative invocation are nested inside the two added methods.

No complete accepted JS check ID, serialization, Candidate API, measurement command,
manifest lifecycle, semantic replay, graph integration, full Q2, metrics, quality gate,
release, root mutation or task completion is claimed.

## What was inspected before replay

FACT: read `q2-js-handoff.md` and `q2-js-seal.json` first, then actual implementation,
owner Python/native assertions, selected regression bodies, fixture/helper bounds,
capture environment destinations, qualification resolution and accepted core contracts.
The project uses Python stdlib unittest and native Node/TypeScript tools; these checks
reuse those real facilities and existing external qualified distributions.

- `scripts/measure_js.mjs:76`: SourceBytes owns a copied Buffer, strict UTF-8 text,
  explicit UTF-16/UTF-8 mapping and line boundaries; it is not serialized SyntaxEvidence.
- `scripts/measure_js.mjs:141`: openCompiler checks the provided Python-qualified
  description, exact Node/TS/settings/resources and loaded CommonJS paths. This is
  native consistency, not independent ToolBinding qualification, authenticated producer
  provenance or R1 execution admission.
- `scripts/measure_js.mjs:193`: parseProgram requires its own WeakMap-registered handle
  and explicit pinned code/metadata. It builds a real controlled-host Program/checker,
  not a supplied callback, ambient package lookup or source execution.
- `scripts/measure.py:215,295,1226`: strict boolean defaulted inventory/controller
  keywords. JSX/TSX pending classification is not configured measurement support.
- `scripts/measure.py:1041`: current nonempty js_entrypoints still rejects.
- `references/quality-metrics.md:72-79`: native-core-only support statement is accurate
  within this observed boundary.

INFERENCE: the frozen checkpoint's advertised core behavior is supported by the actual
assertions and fresh results below, not by historical owner pass counts alone.

## Exact frozen method inventory

| Python method | Fresh result |
| --- | --- |
{rows}

## Minimal added ordinary-discoverable gap tests

| Python method | Fresh result |
| --- | --- |
{extra_rows}

FACT: added only `scripts/tests/test_measure_js_core_independent.py` and its
`measure_js_core_independent.test.mjs` collaborator. Python discovery found exactly
two methods, with no owner-class inheritance/recount. No mocks, fake positive support,
skips or test/production limit changes. These fill missing boundaries rather than
duplicate the already covered census/default/binding suite:

1. Delete an admitted package.json and observe `Unreadable admitted metadata` with
   cause **ENOENT**, rather than implicit absence.
2. Physically create unadmitted.js but supply only use.ts: obtain actual **2307**,
   no Program source file/read for the unadmitted path, and a processed syntax census
   for use.ts. No second discovery or ambient fallback.
3. Supply a forged callback-bearing compiler object: reject before either callback runs.
4. Create a real source hardlink: reject as not an independent regular file.
5. Invoke the actual copied native library as a command: exit **1**, empty stdout,
   explicit no-measurement-command error and no generated output.
6. Validate existing default config successfully, then reject nonempty js_entrypoints
   with the actual not-implemented error.

## Scenario evidence and partial accepted-check coverage

FACT: seven native captures each have returncode 0, empty stderr, actual runtime
Node v24.11.1 / ARM64 and the unchanged copied-controller hash. Each of the six
binding smokes has returncode 0 and empty stderr. All children retain idle30/max90.

| Accepted ID | Proven core fragment | Remaining / not established |
| --- | --- | --- |
| JS-PARSE-01 — PARTIAL ONLY | Six actual suffixes: 30 inputs = 18 processed + 12 failed; each suffix has empty, comment-only, functionless, invalid syntax and invalid UTF-8. BOM/CRLF, emoji/split-surrogate, UTF-16/byte/line/point/EOF checks; regex vs division, template interpolation, arrows/type syntax, body-bearing counts, JSDoc token exclusion. | SyntaxEvidence serialization/ParsedInventory integration; candidate generation, deletion, IDs and invalid-candidate scenarios. |
| JS-SYMBOL-01 — PARTIAL ONLY | Actual checker export/reexport alias identity across .js-to-.ts resolution and unresolved local/external diagnostics. Added unadmitted-file exclusion uses real compiler resolution. | Serialized symbol/reference tables, lexical IDs, cycles, merged declarations, namespaces, dynamic/runtime sites, source-backed entrypoint origins and semantic tamper replay. |
| JS-DIAG-01 — PARTIAL ONLY | Actual 2322/2307 and source-less 6053; EOF zero-length and byte projection; type errors do not automatically fail syntax census. Empty Program remains empty. | Bad-options, related-information/library-diagnostic scenarios, full producer transport/raw validation. |
| JS-OWN-01 — PARTIAL ONLY | Changed source/settings, missing compiler resource, malformed paths/reader/handle, missing code, invalid metadata and controller missing/change/hardlink rejection. Added missing metadata, real source hardlink and callback-handle rejection. | R1/predecessor ownership, rehashed controls/symbol tamper, no-launch audit, absent/partial/valid-looking nonzero producer outputs, timeout fixture commands, strict invalid/zero-stderr branches and opaque archive policy. Direct library rejection is NOT this future failure table. |
| JS-LIFE-01 — PARTIAL ONLY | Distinct actual Git revisions, base-only JS, changed source bytes and package metadata; independent copied native controller. | Base-only Python correction, full reservation/collision audit, before-graph execution, three manifests and archive. |
| JS-LIFE-02 — NOT IMPLEMENTED / NOT VERIFIED | No original/replay producer proof. Two revisions are not replay. | Fixed produce/validate core, private fresh replay Context/copies, purpose-swap rejection, semantic and failed-tuple comparison. |
| JS-COMPAT-01 — PARTIAL ONLY | Omitted/False inventory equality, True pending JSX/TSX and legacy wrong-mode rejection, strict bool rejection, unchanged no-mode-salt digest, actual five/six-file controller formula and physical independence; source nonexecution; selected import/graph/binding regressions; current unsupported config/command rejection. | JS-enabled validated-mode composition/rederivation, real-root Candidate calls, full integration regression and parent acceptance of the eventual component. |

Owner assertion anchors: `scripts/tests/measure_js.test.mjs:37,65,94,123,150,177,189`;
`scripts/tests/test_measure_js.py:123,164`. Selected graph assertions explicitly keep
mixed-language JS/Go unsupported and missing required metrics incomplete; rehashed
graph content is rejected. Actual root score.mjs/native_result.mjs parse without
executing source, and the CJS side-effect sentinel is absent. These are native/core
and selected regression claims, not complete graph/import behavior across all scenarios.

## Exact invocation and capture

All actual absolute argv/cwd/environment records are preserved, not reconstructed
from historical receipts:

- `invocation.json`: frozen replay full argv, all 15 explicit methods, environment,
  selected Git PATH, idle120/max1800 outer bounds. Explicit method names avoid
  accidentally including newly added tests.
- `test_native_*.json`: seven real Node argv/cwd, case/request locators, removed
  environment names, controller hashes, qualified binding/source description,
  stdout/stderr and native observations.
- `two-revisions.json` and `raw-f9df00e58d91.json`: all six actual binding commands,
  request/result provenance and raw captures; exact commands also in reconciliation.json.
- `boundary-invocation.json`: actual `unittest discover -s scripts/tests -p
  test_measure_js_core_independent.py -v`, idle120/max300 outer capture.
- The two added per-method JSON records retain exact argv/cwd and actual positive
  native boundary / negative command outputs. New child bounds remain idle30/max90.

Managed Python: `{before['python']['executable']}`.
PYTHONDONTWRITEBYTECODE=1; PYTHONIOENCODING=utf-8; PYTHONPATH is scripts/tests plus
scripts. Qualified Git cmd PATH prefix was explicitly set. Actual temp fixtures
were unique direct children of OS temp (qj-/ji-/q1-evidence-/bulletproof-git- and
existing helper prefixes), not nested under the long evidence path. No old tree
was touched; tests used only their own normal cleanup. New captures used this
exclusive independent destination, not an owner evidence prefix.

Exact outer replay argv:

```json
{json.dumps(data['main_invocation']['argv'], ensure_ascii=False, indent=2)}
```

Exact additional discovery argv:

```json
{json.dumps(data['boundary_invocation']['argv'], ensure_ascii=False, indent=2)}
```

## Pin reconciliation

FACT: **3,593 distinct input-file hash/length/physical-identity records agree**
before and after; the same set was read again immediately before sealing.
Qualified input descriptions and baseline Git binding also agree. This includes all
**28 owner-owned artifact pins** (including the five files below and handoff),
**10 owner unchanged-input pins**, owner seal, selected tests/helpers/root samples,
qualification artifacts, full declared TS/Python package resource sets, managed
runtime imports, executables and relevant declared PE dependency files, Git core/
bundled DLLs and PATH launcher. No installation or requalification was performed.
Existing PE provenance is not a full loaded-module/API-set forwarding attestation.

| Frozen source/doc/test | SHA-256 (before = after = pre-seal) |
| --- | --- |
{pin_rows}

`before.json` and `after.json` contain every full pin, actual qualified description
and Git/status capture. The new test hashes also matched before/after their own
execution and were rechecked at sealing. Final git status is separately captured.
The only observed concurrent additional path was the permitted reviewer-owned
`q2-js-core-code-review.md`; it was not authored, altered or treated as this
verifier's evidence. No owner artifact was overwritten. Existing unrelated
evals/report.md remained outside this verification's scope.

## Limitations, gates and stop

- UNKNOWN / environment-unverified: root symlink creation from historical WinError
  1314. No privilege retry, skip-as-pass or new host qualification. Real hardlink
  rejection does not prove root symlink behavior.
- UNKNOWN: old temporary-tree cleanup and descendant termination; no cleanup,
  broad profiling or process-name kill was attempted. New tests returned normally;
  that is not an OS cleanup attestation.
- Not exercised: EACCES/EPERM-specific permission denial, concurrent source/resource
  races, all Unicode/path spellings or every native error branch. ENOENT is a real
  read failure, not proof of every failure mode.
- No full suite, broad probe, coverage, mutation, performance benchmark, metric
  collector, scalar, reporter, release or publication proof. Durations are this
  invocation's timings, not a performance claim.
- G1-G3: prior approved scope resumed, not regraded. G4: frozen owner development,
  independently replayed only as scoped here. **G5: bounded core proof passes with
  named limitations; full component gate stays open. G6: not authorized/executed.**
- Human full-design sign-off remains unconfirmed as recorded in the handoff.
- No production/docs/helper edits, agents/factories, root commits/pushes or source
  mutations. Fixture Git commits are solely the required temporary real-revision
  tests. Added test files remain uncommitted for parent disposition.

Next action: parent reviews this report/seal and the separate code review, then
decides preservation/continuation. Completing the missing component needs future
implementation and the retained handoff scenarios; no command over this partial
checkpoint can honestly close them. To replay the present proof, use the exact
argv above with NEW exclusive Q2_JS_RECORDS/Q2_SOURCE_RECORDS/
Q2_JS_INDEPENDENT_RECORDS destinations; do not rerun into this sealed directory.
"""
write("report.md", report)
write("report.html", """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Independent partial Q2 JS core verification</title>
<link rel="stylesheet" href="../../../assets/artifact.css"></head><body><main>
<h1>Independent partial Q2 JS core verification</h1>
<p>15 frozen methods and 2 additional boundary methods passed. 3,593 input pins unchanged.
No full JS/Q2 acceptance or release claim.</p>
<p><a href="report.md">Markdown report</a> · <a href="reconciliation.json">Structured reconciliation</a></p>
<pre style="white-space:pre-wrap;overflow-wrap:anywhere">""" + html.escape(report) +
      "</pre></main></body></html>\n")
owned = [pin(path) for path in sorted(OUT.iterdir()) if path.is_file()]
owned.extend(pin(ROOT / item["path"]) for item in data["boundary_test_pins"])
seal = {
    "schema_version": 1,
    "status": "INDEPENDENT_PARTIAL_CORE_VERIFIED_WITH_LIMITATIONS",
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "head": owner["head"], "owner_seal_sha256": before["seal_sha256"],
    "scope": "Frozen native parser core and defaulted inventory/controller primitives only",
    "frozen_method_results": main, "additional_method_results": extra,
    "exact_argv": {"frozen": data["main_invocation"]["argv"],
                   "additional": data["boundary_invocation"]["argv"]},
    "nested_not_additive": {"owner_native_cases": 7, "binding_smokes": 6,
                            "additional_native_invocations": 2},
    "source_doc_test_pins": five,
    "owner_owned_artifacts": owner["owned_files"],
    "owner_unchanged_inputs": owner["unchanged_inputs"],
    "before_after_pin_count": len(before["pins"]),
    "before_after_pins_equal": True,
    "preseal_pin_recheck_equal": True,
    "input_pin_manifests": [pin(OUT / name) for name in ("before.json", "after.json")],
    "owned_files": owned,
    "accepted_checks": owner["accepted_checks"],
    "test_corrections": [], "test_retries": 0,
    "publication_correction": load("publication-timeout.json"),
    "publication_retries": 1,
    "limitations": data["limitations"],
    "self_binding": "Does not hash itself; SHA-256 is returned separately to caller.",
}
write("seal.json", json.dumps(seal, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"seal": pin(OUT / "seal.json"), "report": pin(OUT / "report.md"),
                  "owned_file_count": len(owned), "input_pin_count": len(before["pins"])}, indent=2))

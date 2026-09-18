"""Read-only reconciliation of completed independent captures; exclusive output."""
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent


def load(name):
    return json.loads((OUT / name).read_bytes())


def results(name, expected_count):
    text = (OUT / name).read_text(encoding="utf-8")
    matches = list(re.finditer(r"^test_\w+ \((test_[^)]+)\) \.\.\. ", text, re.M))
    rows = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        output = text[match.end():end]
        assert re.search(r"^ok$", output, re.M), (match[1], output)
        rows.append({"method": match[1], "outcome": "pass"})
    assert len(rows) == expected_count
    summary = re.search(r"Ran (\d+) tests in ([\d.]+)s\n\nOK\s*$", text)
    assert summary and int(summary[1]) == expected_count
    return {"methods": rows, "count": expected_count, "unittest_seconds": float(summary[2])}


before, after = load("before.json"), load("after.json")
assert before["pins"] == after["pins"]
assert before["qualified"] == after["qualified"]
assert before["baseline"] == after["baseline"]
assert load("replay-result.json")["returncode"] == 0
assert load("boundary-result.json")["returncode"] == 0
assert load("boundary-result.json")["test_pins_unchanged"] is True
main = results("unittest.log", 15)
extra = results("boundary-unittest.log", 2)
assert [row["method"] for row in main["methods"]] == load("invocation.json")["methods"]
native = []
for row in main["methods"]:
    name = row["method"].split(".")[-1]
    if not name.startswith("test_native_"):
        continue
    record = load(name + ".json")
    assert record["returncode"] == 0 and record["stderr"] == ""
    assert (record["idle_seconds"], record["max_seconds"]) == (30, 90)
    assert record["native"]["runtime"] == {"version": "v24.11.1", "architecture": "arm64"}
    assert record["request"]["controller_sha256"] == record["native"]["controller_sha256"]
    native.append({"method": row["method"], "case": record["case"],
                   "argv": record["argv"], "cwd": record["cwd"], "returncode": record["returncode"],
                   "controller_sha256": record["native"]["controller_sha256"]})
assert len(native) == 7
smokes = load("two-revisions.json")
assert len(smokes) == 6
smoke_results = []
for smoke in smokes:
    command = smoke["raw_command"]
    assert command["returncode"] == 0 and command["stderr"] == ""
    smoke_results.append({"revision": smoke["revision"], "tool": smoke["observed"]["tool"],
                          "command": command})
assert {(item["revision"], item["tool"]) for item in smoke_results} == {
    (revision, tool) for revision in ("base", "head") for tool in ("typescript", "lizard", "vulture")}
census = load("test_native_six_suffix_census.json")["native"]["proofs"][0]["census"]
assert len(census) == 30
suffixes = {}
for suffix in (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"):
    rows = [row for row in census if row["suffix"] == suffix]
    states = {state: sum(row["state"] == state for row in rows) for state in ("processed", "failed")}
    assert states == {"processed": 3, "failed": 2}
    suffixes[suffix] = states
result = {"status": "INDEPENDENT_PARTIAL_CORE_VERIFIED_WITH_LIMITATIONS",
          "frozen_method_replay": main, "additional_boundary_tests": extra,
          "main_invocation": load("invocation.json"), "boundary_invocation": load("boundary-invocation.json"),
          "native_cases_nested_not_additive": native, "binding_smokes_nested_not_additive": smoke_results,
          "census": {"inputs": 30, "processed": 18, "failed": 12, "suffixes": suffixes},
          "before_after_identical_pins": len(before["pins"]),
          "owner_artifacts_matched": 28, "owner_unchanged_inputs_matched": 10,
          "owner_seal_sha256": before["seal_sha256"],
          "boundary_test_pins": load("boundary-result.json")["test_pins"],
          "corrections": [], "retries": 0,
          "limitations": [
              "No complete accepted JS test ID, full Q2, metrics or release verified.",
              "Native core consistency is not producer admission, authenticated provenance or semantic replay.",
              "Root symlink WinError1314 remains environment-unverified; old cleanup remains UNKNOWN.",
              "PE dependency pins retain original qualification limits; no new loaded-module attestation.",
              "No full suite, coverage, mutation, installation, requalification, commit or push.",
          ]}
with (OUT / "reconciliation.json").open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
print(json.dumps({"frozen": main, "additional": extra, "pins": len(before["pins"]),
                  "native_nested": len(native), "smokes_nested": len(smokes)}, indent=2))

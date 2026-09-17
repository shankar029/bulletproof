"""Read-only qualification pin/staging diagnostic, not a Q2 acceptance test."""

import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import measure_graph as graph
from evidence import write_json_atomic


def pin(path):
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main():
    evidence = Path(__file__).resolve().parent
    names = [
        "q2-tools-report.md", "q2-tools-manifest.json",
        "q2-tools-source-report.md", "q2-tools-source-manifest.json",
        "q2-tools-source-summary.json", "q2-tools-source-roots.json",
        "q2-tools-source-extracted-pins.json",
        "q2-tools-route-report.md", "q2-tools-route-manifest.json",
    ]
    records = {name: pin(evidence / name) for name in names}
    decoded = {name: graph.load_json((evidence / name).read_bytes())
               for name in names if name.endswith(".json")}
    source_names = [
        "scripts/measure.py", "scripts/measure_graph.py", "scripts/probe.py",
        ".ai/workflow-reliability/measurement-enablement-contracts.json",
    ]
    source_before = {name: pin(ROOT / name) for name in source_names}
    extracted = decoded["q2-tools-source-extracted-pins.json"]
    for index, expected in enumerate(extracted):
        if pin(Path(expected["path"])) != expected:
            raise ValueError("Changed extracted input: " + expected["path"])
        if (index + 1) % 500 == 0:
            print("Verified extracted input bytes:", index + 1, flush=True)

    staged, rejected = [], []
    native = decoded["q2-tools-manifest.json"]["tools"]
    with tempfile.TemporaryDirectory(prefix="q2a-") as temporary:
        scratch = Path(temporary).resolve()
        if list(scratch.iterdir()):
            raise ValueError("Expected fresh staging directory")
        for tool in ("jscpd", "ruff"):
            binding = native[tool]["binding"]
            binary = pin(Path(binding["executable"]))
            if binary["sha256"] != binding["sha256"]:
                raise ValueError("Changed native binary: " + tool)
            refs = [binding["help"], binding["configuration"], *binding["qualification"]]
            for index, ref in enumerate(refs):
                original = Path(ref["path"])
                if pin(original) != ref:
                    raise ValueError("Changed original qualification artifact")
                try:
                    graph.relative_name(ref["path"])
                except ValueError as error:
                    rejected.append({"tool": tool, "original": ref, "reason": str(error)})
                else:
                    raise ValueError("Expected absolute qualification locator, not run-relative Artifact")
                name = "qualification/" + tool + "/" + str(index) + original.suffix
                destination = graph.input_path(scratch, name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, destination)
                copied = graph.artifact(scratch, name)
                if copied["sha256"] != ref["sha256"] or copied["bytes"] != ref["bytes"]:
                    raise ValueError("Staging changed bytes")
                staged.append({"original": ref, "owned": copied,
                               "destination_characters": len(str(destination))})
        temporary_name = str(scratch)
    source_after = {name: pin(ROOT / name) for name in source_names}
    if source_after != source_before:
        raise ValueError("Affected source changed during diagnostic")
    result = {
        "scope": "Pin and actual temporary-artifact staging diagnostic only; no Q2 metrics or test pass",
        "qualification_documents": records,
        "decoded_manifest_fields": {name: sorted(value) if isinstance(value, dict)
                                    else {"records": len(value)}
                                    for name, value in decoded.items()},
        "extracted_input_count": len(extracted),
        "extracted_inputs_all_match": True,
        "absolute_binding_artifacts_rejected": rejected,
        "actual_staging": staged,
        "temporary_root": temporary_name,
        "temporary_root_removed": not Path(temporary_name).exists(),
        "affected_source_before": source_before,
        "affected_source_after": source_after,
        "blocker": "No approved original-artifact locator is supplied to fresh probe run-root staging",
        "not_blockers": ["Q1 deliberately rejects nonempty tools", "Disjoint concurrent CLI changes"],
    }
    output = evidence / "q2-adapter-binding-check-results.json"
    if output.exists():
        raise ValueError("Refusing to overwrite historical diagnostic evidence")
    write_json_atomic(output, result)
    print("Verified", len(extracted), "extracted pins;", len(staged),
          "actual artifact copies; temporary directory removed.", flush=True)
    print("BLOCKED: approve original-artifact locator/staging semantics before production edits.",
          flush=True)


if __name__ == "__main__":
    main()

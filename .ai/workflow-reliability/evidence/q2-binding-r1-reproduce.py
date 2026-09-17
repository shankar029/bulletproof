"""Execute the reviewed R1 counterexample on the pinned, unfixed source only."""

import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/tests"))
sys.path.insert(0, str(ROOT / "scripts"))

import measure
import measure_graph as graph
from test_measure_source_bindings import SourceBindingTests


def main():
    source = ROOT / "scripts/measure.py"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    if before != "1acf798f411b62fc757a8c78fb675a6b5a66b68bbf92f620757d4a12b5b3c6f4":
        raise ValueError("Reproduction requires the original reviewed source bytes")
    output = Path(__file__).with_name("q2-binding-r1-repro")
    output.mkdir(exist_ok=False)
    os.environ["Q2_SOURCE_RECORDS"] = str(output)
    case = SourceBindingTests()
    events, active = [], [False]

    def audit(event, args):
        if active[0] and event == "subprocess.Popen":
            events.append({"event": event, "executable": str(args[0]),
                           "argv": args[1], "cwd": str(args[2])})

    sys.addaudithook(audit)
    try:
        fixture = case.fixture(("typescript",))
        measure.validate_config(fixture.config, fixture.git.root)
        context = case.context(fixture)
        original = graph.load_json((Path(context["run_root"]) / "manifest.json").read_bytes())
        broken = graph.load_json(json.dumps(original))
        removed = broken["inputs"].pop(0)
        broken["reserved_outputs"].append("r1-missing-row.json")
        context["output_manifest"] = graph.persist(context, "r1-missing-row.json", broken)
        active[0] = True
        try:
            observed = measure.inspect_source_binding(context, fixture.config, "typescript", "head")
        finally:
            active[0] = False
        command = graph.load_json((Path(context["run_root"]) / observed["command"]["path"]).read_bytes())
        assert command["returncode"] == 0 and len(events) == 1
        assert observed["observed"]["smoke"]["symbol"] == "answer"
        after = hashlib.sha256(source.read_bytes()).hexdigest()
        assert before == after
        record = {"reproduced": True, "scope": "R1 actual malformed-file child execution, not a passing test",
                  "before": before, "after": after, "original_manifest": original,
                  "malformed_manifest": broken, "removed_row": removed, "context": context,
                  "audited_launches": events, "observed": observed, "command": command}
        with (output / "reproduction.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
        print("R1 reproduced: missing qualification row, rehashed manifest, actual Node exit 0.",
              flush=True)
    finally:
        case.doCleanups()


if __name__ == "__main__":
    main()

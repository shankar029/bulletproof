"""Approved external source distribution qualification, never a metric producer."""
import importlib.util
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import sys
import tarfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("q2_harness", HERE / "q2-tools-qualify.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
ROOT = q.OWNED / "source-qualified-1"
BOOTSTRAP = HERE / "q2-tools-source-python.py"
TS_HELPER = HERE / "q2-tools-source-typescript.cjs"


def save(name, value):
    q.save("source-" + name, value)


def command(name, argv, install=False):
    return q.command("source-" + name, argv, cwd=ROOT, install=install)


def extract(archive, target):
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        seen = set()
        for item in members:
            path = PurePosixPath(item.name)
            if (path.is_absolute() or ".." in path.parts or "\\" in item.name or ":" in item.name
                    or any(part.endswith((" ", ".")) for part in path.parts)
                    or not (item.isfile() or item.isdir())):
                raise ValueError("Unsafe archive member " + item.name)
            key = "/".join(path.parts).casefold()
            if key in seen:
                raise ValueError("Archive collision " + item.name)
            seen.add(key)
        target.mkdir()
        bundle.extractall(target, filter="data")
    roots = list(target.iterdir())
    assert len(roots) == 1 and roots[0].is_dir()
    return roots[0].resolve()


def provision():
    os.chdir(q.OWNED)
    Path(ROOT.name).mkdir()
    prior = [{"path": str(p), "sha256": q.sha(p)} for p in sorted(HERE.glob("q2-tools-*"))
             if p.is_file() and not p.name.startswith("q2-tools-source-")]
    save("prior-pins", prior)
    route = json.loads((HERE / "q2-tools-route-manifest.json").read_text())
    roots = {}
    for tool, item in route["tools"].items():
        download = item["acquired_data_only"]
        path = Path(download["path"])
        assert q.sha(path) == download["sha256"]
        roots[tool] = str(extract(path, ROOT / tool))
    save("roots", roots)
    pins = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
            for root in roots.values() for p in sorted(Path(root).rglob("*")) if p.is_file()]
    save("extracted-pins", pins)
    old = json.loads((HERE / "q2-tools-runtime-bindings.json").read_text())
    contracts = [q.REPO / "scripts" / "run.py",
                 q.REPO / ".ai" / "workflow-reliability" / "measurement-enablement-contracts.json",
                 q.REPO / ".ai" / "workflow-reliability" / "evidence" / "measurement-design-review-r2.md"]
    save("required-pins", {"executors": {name: old["executors"][name] for name in ("python", "node")},
                           "python_dll": old["python_dll"],
                           "contracts": [{"path": str(p), "sha256": q.sha(p)} for p in contracts],
                           "concurrent_disjoint_writer": "Parent-authorized C2 workflow_state.py; not in qualification pins"})
    print("Extracted", len(pins), "files from five verified archives; no setup or build invoked")


def helps():
    roots = json.loads((HERE / "q2-tools-source-roots.json").read_text())
    node = json.loads((HERE / "q2-tools-runtime-bindings.json").read_text())["executors"]["node"]["path"]
    command("typescript-version", [node, Path(roots["typescript"]) / "bin" / "tsc", "--version"])
    command("typescript-help", [node, Path(roots["typescript"]) / "bin" / "tsc", "--help", "--all"])
    for tool in ("lizard", "vulture"):
        for flag in ("--version", "--help"):
            command(tool + "-" + flag[2:], [q.PYTHON, "-I", "-S", "-B", BOOTSTRAP,
                                           "cli", tool, flag], install=True)


def python_cases(tool):
    command(tool + "-api", [q.PYTHON, "-I", "-S", "-B", BOOTSTRAP, tool], install=True)


def typescript_cases():
    node = json.loads((HERE / "q2-tools-runtime-bindings.json").read_text())["executors"]["node"]["path"]
    command("typescript-api", [node, TS_HELPER], install=True)


if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])

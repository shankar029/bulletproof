"""Independent additive capture; reuses the inspected byte-stream transport only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-final-verification-"
spec = importlib.util.spec_from_file_location("transport", HERE / "q1-resumed-correction-capture.py")
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)
transport.__file__ = __file__
transport.prior.__file__ = __file__
transport.prior.PREFIX = PREFIX
original = transport.prior.original
original.INPUTS += [str(Path(__file__).resolve()),
                   "scripts/tests/test_measure_q1_final_verification.py"]


def save(name, value):
    with (HERE / (PREFIX + name + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def inventory(suite):
    return [case.id() for item in suite
            for case in (inventory_cases(item) if isinstance(item, unittest.TestSuite) else [item])]


def inventory_cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from inventory_cases(item)
        else:
            yield item


def preflight(label):
    owner = json.loads((HERE / "q1-resumed-correction-final-freeze.json").read_bytes())
    frozen = owner["frozen_inputs"]
    changed = [name for name, ref in frozen.items()
               if original.hashes([Path(name)]).get(name) != ref]
    protected = [p for p in HERE.rglob("*") if p.is_file()
                 and not p.relative_to(HERE).parts[0].startswith(PREFIX)]
    paths = [ROOT / p for p in original.INPUTS]
    paths += list((ROOT / "scripts/tests").glob("test_measure*.py"))
    paths += [ROOT / "scripts/tests/test_probe.py", Path(sys.executable)]
    paths += list(Path(sys.executable).parent.glob("*.dll"))
    allowed = [str(ROOT / ".ai/workflow-reliability/state.md")]
    unexpected = [name for name in changed if name not in allowed]
    save(label, {"owner_inputs": frozen, "owner_changed": changed,
                       "allowed_parent_status_changes": allowed, "unexpected_changes": unexpected,
                       "inputs": original.hashes(paths), "protected": original.hashes(protected),
                       "python": sys.version, "executable": sys.executable})
    assert not unexpected, unexpected
    print(json.dumps({"owner_pins": len(frozen), "owner_changed": changed,
                      "protected": len(protected)}))


def worker(pattern, label):
    sys.path.insert(0, str(ROOT / "scripts/tests"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "scripts/tests"), pattern=pattern)
    names = inventory(suite)
    save(label + "-inventory", {"pattern": pattern, "tests": names, "count": len(names)})
    # Preserve real owned test trees before normal cleanup. No fixtures, producers,
    # assertions, subprocess behavior, or cleanup semantics are replaced.
    import tempfile
    owned = set()
    archived = set()
    records = []
    destination = HERE / (PREFIX + "a-" + label)
    destination.mkdir(exist_ok=False)

    def audit(event, args):
        transport.native_progress(event, args)
        if event == "tempfile.mkdtemp":
            path = Path(args[0]).resolve()
            if path.name.startswith(("bulletproof-git-", "q1-evidence-", "q1-resumed-tests-",
                                     "q1-final-tests-")):
                # Materializer scratch directories are not test source trees.
                if not path.name.startswith(("bulletproof-git-policy-", "bulletproof-git-tree-")):
                    owned.add(path)
        if event != "shutil.rmtree":
            return
        path = Path(args[0]).resolve()
        if path not in owned or path in archived or not path.exists():
            return
        archived.add(path)
        target = destination / ("%03d.zip" % len(archived))
        files, links = {}, []
        with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for base, dirs, names in os.walk(path, followlinks=False):
                for name in list(dirs):
                    child = Path(base) / name
                    if child.is_symlink() or child.is_junction():
                        links.append(str(child.relative_to(path)))
                        dirs.remove(name)
                for name in names:
                    child = Path(base) / name
                    if child.is_symlink():
                        links.append(str(child.relative_to(path)))
                        continue
                    data = child.read_bytes()
                    relative = child.relative_to(path).as_posix()
                    archive.writestr(relative, data)
                    files[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        records.append({"source": str(path), "archive": str(target), "files": files,
                        "links_not_followed": links})
        save(label + "-archive-%03d" % len(archived), records[-1])

    sys.addaudithook(audit)
    code = transport.prior.worker(pattern, label)
    save(label + "-archives", {"archives": records,
                              "owned_remaining": [str(p) for p in owned if p.exists()]})
    return code


if __name__ == "__main__":
    action, *args = sys.argv[1:]
    if action == "preflight":
        preflight(args[0] if args else "preflight")
    else:
        sys.exit(worker(*args) if action == "worker" else transport.capture(*args))

"""Narrow actual-Git qualification: cached --all distinguishes absence from values."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/tests"))
from helpers import GitFixture
import measure


def hashes(paths):
    return {str(path): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bytes": path.stat().st_size}
            for path in sorted(set(paths)) if path.is_file()}


protected = [path for path in HERE.rglob("*") if path.is_file() and not path.name.startswith("q1-attr-")]
protected += list((ROOT / "scripts/tests").glob("test_measure*.py"))
protected += [ROOT / "scripts" / name for name in ("measure.py", "measure_graph.py", "probe.py")]
with (HERE / "q1-attr-before.json").open("x", encoding="utf-8") as stream:
    json.dump(hashes(protected), stream, indent=2)

binding = measure.baseline_binding()
fixture = GitFixture()
commands = []
try:
    with tempfile.TemporaryDirectory(prefix="q1-attr-qualification-") as temporary:
        owned = Path(temporary).resolve()
        empty = owned / "empty"
        empty.mkdir()
        env = measure._git_environment(empty)
        executable = binding["git"]["path"]
        options = ["-c", "core.autocrlf=false", "-c", "core.eol=lf",
                   "-c", "core.attributesFile=" + __import__("os").devnull,
                   "-c", "core.hooksPath=" + str(empty)]

        def command(label, args, cwd, allowed=(0,)):
            argv = [executable, *args]
            result = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=30)
            raw = {}
            for key, data in (("stdout", result.stdout), ("stderr", result.stderr)):
                path = HERE / ("q1-attr-qual-" + label + "." + key + ".bin")
                with path.open("xb") as stream:
                    stream.write(data)
                raw[key] = {"path": str(path), **hashes([path])[str(path)]}
            commands.append({"argv": argv, "cwd": str(cwd), "exit": result.returncode, "raw": raw})
            assert result.returncode in allowed, commands[-1]
            return result.stdout

        command("help", ["check-attr", "-h"], owned, (0, 129))
        names = ["absent.py", "disabled.py", "literal-unset.py", "literal-unspecified.py",
                 "macro.py", "reset.py"]
        for name in names:
            fixture.write(name, "pass\n")
        fixture.write(".gitattributes",
                      "[attr]danger filter=unset\n"
                      "disabled.py -filter\nliteral-unset.py filter=unset\n"
                      "literal-unspecified.py filter=unspecified\nmacro.py danger\n"
                      "reset.py filter=earlier\nreset.py !filter\n")
        revision = fixture.commit("attribute state/value qualification")
        target = owned / "cached"
        command("clone", options + ["clone", "--quiet", "--no-hardlinks", "--no-checkout",
                "--template=" + str(empty), str(fixture.root), str(target)], owned)
        command("read", options + ["read-tree", revision], target)
        explicit = command("explicit", options + ["check-attr", "--cached", "-z", "filter", "--", *names], target)
        all_attributes = command("all", options + ["check-attr", "--cached", "--all", "-z", "--", *names], target)
        result = {"binding": binding, "commands": commands,
                  "environment": {key: env[key] for key in (
                      "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_ATTR_NOSYSTEM",
                      "GIT_NO_REPLACE_OBJECTS", "GIT_TERMINAL_PROMPT", "HOME", "USERPROFILE", "XDG_CONFIG_HOME")},
                  "explicit": explicit.decode(), "all": all_attributes.decode(),
                  "no_checkout_files": all(not (target / name).exists() for name in names),
                  "binding_unchanged": measure.baseline_binding() == binding}
finally:
    fixture.close()
with (HERE / "q1-attr-qualification.json").open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
print(json.dumps({key: result[key] for key in ("explicit", "all", "no_checkout_files", "binding_unchanged")}, indent=2))

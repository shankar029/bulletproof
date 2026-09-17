"""Installed Git qualification, using only disposable repositories/configuration."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/tests"))
from helpers import GitFixture

GIT = str(Path(shutil.which("git")).resolve())
records = []


def command(label, args, cwd, env=None, allowed=(0,)):
    argv = [GIT, *args]
    print(label, flush=True)
    proc = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=30)
    raw = {}
    for key, data in (("stdout", proc.stdout), ("stderr", proc.stderr)):
        path = HERE / ("q1-review-correction-qualification-" + label + "." + key + ".bin")
        with path.open("xb") as stream:
            stream.write(data)
        raw[key] = {"path": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    records.append({"argv": argv, "cwd": str(cwd), "exit": proc.returncode, "raw": raw})
    assert proc.returncode in allowed, (label, proc.returncode, proc.stderr)
    return proc.stdout


with tempfile.TemporaryDirectory(prefix="q1-git-qualification-") as temporary:
    owned = Path(temporary).resolve()
    empty = owned / "empty"
    empty.mkdir()
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_ATTR_NOSYSTEM="1", GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0",
               HOME=str(empty), USERPROFILE=str(empty), XDG_CONFIG_HOME=str(empty))
    options = ["-c", "core.autocrlf=false", "-c", "core.eol=lf",
               "-c", "core.attributesFile=" + os.devnull, "-c", "core.hooksPath=" + str(empty)]
    for name, args in (
            ("version", ["--version"]), ("clone-help", ["clone", "-h"]),
            ("attributes-help", ["check-attr", "-h"]), ("tree-help", ["ls-tree", "-h"]),
            ("read-tree-help", ["read-tree", "-h"]), ("checkout-index-help", ["checkout-index", "-h"]),
            ("update-ref-help", ["update-ref", "-h"])):
        command(name, args, owned, env, (0, 129))
    fixture = GitFixture()
    try:
        fixture.write(".gitattributes", "*.py text eol=crlf\nlf.txt text eol=lf\n")
        fixture.write("module.py", b"value = 1\n")
        fixture.write("lf.txt", b"value\n")
        fixture.write("neutral.txt", b"neutral\n")
        fixture.write("executable.py", b"pass\n")
        fixture.run("git", "add", "--all")
        fixture.run("git", "update-index", "--chmod=+x", "executable.py")
        fixture.run("git", "commit", "--quiet", "-m", "qualified attributes")
        revision = fixture.run("git", "rev-parse", "HEAD")[1].strip()
        target = owned / "expected"
        command("clone-neutral", options + ["clone", "--quiet", "--no-hardlinks", "--no-checkout",
                "--template=" + str(empty), str(fixture.root), str(target)], owned, env)
        command("detach-neutral", options + ["update-ref", "--no-deref", "HEAD", revision], target, env)
        command("read-neutral", options + ["read-tree", revision], target, env)
        tree = command("list-neutral", options + ["ls-tree", "-r", "-z", "--full-tree", revision], target, env)
        names = [part.split(b"\t", 1)[1].decode() for part in tree.split(b"\0") if part]
        attrs = command("attrs-neutral", options + ["check-attr", "--cached", "-z", "filter", "ident",
                        "working-tree-encoding", "text", "eol", "crlf", "--", *names], target, env)
        assert b"module.py\0eol\0crlf\0" in attrs
        assert b"100755 blob" in tree
        command("checkout-neutral", options + ["checkout-index", "--all", "--force"], target, env)
        assert (target / "module.py").read_bytes() == b"value = 1\r\n"
        assert (target / "lf.txt").read_bytes() == b"value\n"
        assert (target / "neutral.txt").read_bytes() == b"neutral\n"
        assert (target / ".git/HEAD").read_text().strip() == revision
        # Versioned attribute macros must be interpreted by Git, not a new parser.
        fixture.write(".gitattributes", "[attr]danger filter=tripwire\n*.py danger\n")
        filtered_revision = fixture.commit("declared external filter")
        blocked = owned / "blocked"
        command("clone-filter", options + ["clone", "--quiet", "--no-hardlinks", "--no-checkout",
                "--template=" + str(empty), str(fixture.root), str(blocked)], owned, env)
        command("read-filter", options + ["read-tree", filtered_revision], blocked, env)
        blocked_attrs = command("attrs-filter", options + ["check-attr", "--cached", "-z",
                                "filter", "--", "module.py"], blocked, env)
        assert blocked_attrs == b"module.py\0filter\0tripwire\0"
        assert not (blocked / "module.py").exists()
        sentinel = owned / "sentinel"
        program = owned / "filter.py"
        program.write_text("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('EXECUTED')\n"
                           "sys.stdout.buffer.write(sys.stdin.buffer.read())\n")
        driver = '"%s" -B "%s" "%s"' % (Path(sys.executable).as_posix(), program.as_posix(), sentinel.as_posix())
        assert not sentinel.exists()
        # Positive control ONLY: intentionally execute the driver in another private
        # checkout after proving the rejection boundary stops before checkout-index.
        positive = owned / "positive"
        command("clone-positive", options + ["clone", "--quiet", "--no-hardlinks", "--no-checkout",
                "--template=" + str(empty), str(fixture.root), str(positive)], owned, env)
        command("read-positive", options + ["read-tree", filtered_revision], positive, env)
        command("sentinel-positive", options + ["-c", "filter.tripwire.smudge=" + driver,
                "checkout-index", "--all", "--force"], positive, env)
        assert sentinel.read_text() == "EXECUTED"
        result = {"git": {"path": GIT, "sha256": hashlib.sha256(Path(GIT).read_bytes()).hexdigest()},
                  "environment": {key: env[key] for key in (
                      "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_ATTR_NOSYSTEM",
                      "GIT_NO_REPLACE_OBJECTS", "GIT_TERMINAL_PROMPT", "HOME", "USERPROFILE",
                      "XDG_CONFIG_HOME")},
                  "removed_environment_keys": [key for key in os.environ if key.upper().startswith("GIT_")],
                  "commands": records, "tree": tree.decode(),
                  "qualified": ["neutral LF", "versioned text/eol", "cached attribute macro expansion",
                                "no-checkout/read-tree/attribute-check before filter execution",
                                "detached HEAD via update-ref", "immutable executable tree mode"],
                  "unqualified_reject": ["ident", "working-tree-encoding", "legacy crlf attribute"],
                  "status": "PASS", "sentinel_positive": True}
    finally:
        fixture.close()
with (HERE / "q1-review-correction-qualification.json").open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
print(json.dumps({"status": result["status"], "git": result["git"], "commands": len(records)}))

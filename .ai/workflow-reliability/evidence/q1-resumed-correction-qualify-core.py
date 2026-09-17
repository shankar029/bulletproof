"""Replay the preserved Git qualification against its actual packaged core.

Only the executable selection and additive output prefix differ. The original
qualification program and its saved output are never changed.
"""
from pathlib import Path
import hashlib
import json
import shutil

core = Path(shutil.which("git")).resolve().parents[1] / "clangarm64/bin/git.exe"


def pins():
    return {str(path): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bytes": path.stat().st_size}
            for path in sorted([core, *core.parent.glob("*.dll")])}


before = pins()

original = Path(__file__).with_name("q1-review-correction-qualify.py")
program = original.read_text(encoding="utf-8")
selection = 'GIT = str(Path(shutil.which("git")).resolve())'
assert program.count(selection) == 1
program = program.replace(selection,
    'GIT = str(Path(shutil.which("git")).resolve().parents[1] / "clangarm64/bin/git.exe")')
program = program.replace("q1-review-correction-qualification-", "q1-resumed-correction-core-qualification-")
program = program.replace("q1-review-correction-qualification.json", "q1-resumed-correction-core-qualification.json")
exec(compile(program, str(original), "exec"))
after = pins()
with Path(__file__).with_name("q1-resumed-correction-core-dependencies.json").open("x", encoding="utf-8") as stream:
    json.dump({"before": before, "after": after, "unchanged": before == after}, stream, indent=2)
assert before == after

from pathlib import Path
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from run import run_capture


class GitFixture:
    """An owned repository with bounded commands and byte-stable fixture files."""

    def __init__(self):
        self.directory = tempfile.TemporaryDirectory(prefix="bulletproof-git-")
        self.root = Path(self.directory.name)
        try:
            self.run("git", "init", "--quiet")
            self.run("git", "config", "user.name", "Test fixture")
            self.run("git", "config", "user.email", "fixture@example.invalid")
            self.run("git", "config", "core.autocrlf", "false")
        except BaseException:
            self.directory.cleanup()
            raise

    def write(self, name, content):
        path = self.root / name
        if not path.resolve().is_relative_to(self.root):
            raise ValueError("Fixture path escapes its owned directory")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def run(self, *argv, expected=0, timeout=60, cwd=None):
        result = run_capture(list(argv), cwd=str(cwd or self.root),
                             idle=min(30, timeout), max_total=timeout)
        if expected is not None and result[0] != expected:
            raise AssertionError("%r returned %s\n%s\n%s" % (argv, *result))
        return result

    def commit(self, message="fixture: capture input"):
        self.run("git", "add", "--all")
        self.run("git", "commit", "--quiet", "-m", message)
        return self.run("git", "rev-parse", "HEAD")[1].strip()

    def close(self):
        self.directory.cleanup()

"""Real standalone caller seam smoke, not whole probe/mutation qualification."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import mutate
import probe


class CallerSmoke(unittest.TestCase):
    def test_mutate_run_preserves_cwd_env_argv_and_exit(self):
        with tempfile.TemporaryDirectory(prefix="c2a-mutate-") as directory:
            env = dict(os.environ, C2A_VALUE="caller-env")
            argv = [sys.executable, "-B", "-c",
                    "import os,sys;from pathlib import Path;"
                    "Path(sys.argv[1]).write_text(os.environ['C2A_VALUE']);"
                    "sys.stdout.write('out');sys.stderr.write('err');sys.exit(9)",
                    "owned file.txt"]
            result = mutate.run(argv, cwd=directory, timeout=15, env=env)
            self.assertEqual(result, (9, "out", "err"))
            self.assertEqual((Path(directory) / "owned file.txt").read_text(), "caller-env")
            print("mutate.run:", json.dumps({"argv": argv, "cwd": directory,
                                            "timeout": 15, "result": result}))

    def test_probe_run_preserves_capture_and_real_trace(self):
        with tempfile.TemporaryDirectory(prefix="c2a-probe-") as directory:
            trace = []
            token = probe.TRACE.set(trace)
            argv = [sys.executable, "-B", "-c",
                    "import sys;from pathlib import Path;"
                    "Path('proof').write_text('executed');"
                    "sys.stdout.write('probe-out');sys.stderr.write('probe-err');sys.exit(6)"]
            try:
                result = probe.run(argv, cwd=directory, timeout=15)
            finally:
                probe.TRACE.reset(token)
            self.assertEqual(result, (6, "probe-out", "probe-err"))
            self.assertEqual((Path(directory) / "proof").read_text(), "executed")
            self.assertEqual(trace, [{
                "argv": argv, "cwd": str(Path(directory).resolve()),
                "idle_seconds": 15.0, "max_seconds": 15,
                "code": 6, "stdout": "probe-out", "stderr": "probe-err"}])
            print("probe.run:", json.dumps(trace))

    def test_standalone_callers_preserve_launch_failure(self):
        with tempfile.TemporaryDirectory(prefix="c2a-missing-") as directory:
            argv = [str(Path(directory) / "missing")]
            for call in (mutate.run, probe.run):
                with self.subTest(caller=call.__module__):
                    self.assertEqual(call(argv, cwd=directory, timeout=15),
                                     (127, "", "not found"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

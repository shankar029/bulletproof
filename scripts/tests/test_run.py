import gc
import os
import sys
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import run_capture


class CaptureTests(unittest.TestCase):
    def test_utf8_env_and_stream_cleanup(self):
        env = dict(os.environ, NATIVE_CAPTURE_TEST="é_日本")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ResourceWarning)
            rc, out, err = run_capture(
                [sys.executable, "-c",
                 "import os,sys; v=os.environ['NATIVE_CAPTURE_TEST'].encode('utf-8'); "
                 "sys.stdout.buffer.write(v); sys.stderr.buffer.write(v)"],
                env=env, idle=10, max_total=15)
            gc.collect()
        self.assertEqual((rc, out, err), (0, "é_日本", "é_日本"))
        self.assertFalse([w for w in caught if issubclass(w.category, ResourceWarning)])

    def test_legacy_signature_and_missing_program(self):
        self.assertEqual(run_capture([sys.executable, "-c", "print('ok')"], None, 10, 15),
                         (0, "ok\n", ""))
        self.assertEqual(run_capture(["bulletproof-no-such-command"])[0], 127)

    def test_cli_forwards_unicode_with_cp1252_parent_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "run.py"),
                   "--idle", "10", "--max", "15", "--", sys.executable, "-c",
                   "import sys;sys.stdout.buffer.write(bytes.fromhex('e29c9320ce9420e697a5e69cac0a'));"
                   "sys.stdout.buffer.write(b'finished\\n')"]
        rc, out, err = run_capture(command, env=env, idle=20, max_total=25)
        self.assertEqual(rc, 0, err)
        self.assertEqual(out, "✓ Δ 日本\nfinished\n")
        self.assertEqual(err, "")

    def test_partial_lines_count_as_progress(self):
        rc, out, _ = run_capture(
            [sys.executable, "-c",
             "import sys,time\nfor _ in range(8):\n sys.stdout.write('x');sys.stdout.flush();time.sleep(.2)"],
            idle=.6, max_total=10)
        self.assertEqual((rc, out), (0, "xxxxxxxx"))

    def test_idle_and_total_timeouts(self):
        for idle, ceiling, code in [(.2, 10, 124), (10, .2, 125)]:
            with self.subTest(code=code):
                result = run_capture([sys.executable, "-c", "import time;time.sleep(30)"],
                                     idle=idle, max_total=ceiling)
                self.assertEqual(result[0], code)
                self.assertIn("timeout", result[2])


if __name__ == "__main__":
    unittest.main()

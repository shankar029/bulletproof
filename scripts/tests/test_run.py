import gc
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import run_capture


class ProcessWitness:
    """Inspect the real owned PID (retain its Windows handle against PID reuse)."""

    def __init__(self, pid):
        self.pid = pid
        self.handle = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            self.kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            self.kernel.OpenProcess.restype = wintypes.HANDLE
            self.kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            self.kernel.WaitForSingleObject.restype = wintypes.DWORD
            self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            self.kernel.CloseHandle.restype = wintypes.BOOL
            self.handle = self.kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
            if not self.handle:
                raise ctypes.WinError(ctypes.get_last_error())

    def alive(self):
        if self.handle is not None:
            status = self.kernel.WaitForSingleObject(self.handle, 0)
            if status not in (0, 258):  # signalled / WAIT_TIMEOUT
                raise AssertionError(f"unexpected process wait status: {status}")
            return status == 258
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        return True

    def close(self):
        if self.handle is not None:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


class CaptureTests(unittest.TestCase):
    def owned_child(self):
        directory = tempfile.TemporaryDirectory(prefix="bulletproof-run-")
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        # Files provide a real rendezvous: the child cannot finish until the
        # observer releases it. The deadline only bounds broken test cleanup.
        code = (
            "import os,sys,time\nfrom pathlib import Path\n"
            "Path('ready').write_text(str(os.getpid()))\n"
            "limit=time.monotonic()+15\n"
            "while not Path('release').exists():\n"
            " if time.monotonic()>limit: sys.exit(88)\n"
            " time.sleep(.01)\n"
            "Path('completed').write_text('finished')\n"
            "sys.stdout.write('exact');sys.stderr.write('error')\n"
        )
        return root, [sys.executable, "-B", "-c", code]

    def await_ready(self, root, event):
        limit = time.monotonic() + 10
        ready = root / "ready"
        while not ready.exists() or not ready.read_text():
            self.assertLess(time.monotonic(), limit, "child did not rendezvous")
            time.sleep(.01)
        self.assertEqual(int(ready.read_text()), event["pid"])
        witness = ProcessWitness(event["pid"])
        self.addCleanup(witness.close)
        self.assertTrue(witness.alive())
        return witness

    def assert_observation(self, event, phase, cleanup="not-attempted"):
        self.assertEqual(set(event), {
            "phase", "pid", "process_group", "start_identity", "identity_evidence",
            "returncode", "cleanup", "error"})
        self.assertEqual(event["phase"], phase)
        self.assertEqual(event["cleanup"], cleanup)
        self.assertIsNone(event["start_identity"])
        self.assertIsNone(event["identity_evidence"])
        if phase == "launch-failed":
            self.assertIsNone(event["pid"])
            self.assertIsNone(event["process_group"])
        else:
            self.assertIs(type(event["pid"]), int)
            self.assertGreater(event["pid"], 0)
            self.assertEqual(event["process_group"], None if os.name == "nt" else event["pid"])

    def test_observer_success_preserves_exact_result(self):
        events = []
        result = run_capture(
            [sys.executable, "-B", "-c",
             "import sys;sys.stdout.write('exact');sys.stderr.write('error')"],
            idle=10, max_total=15, observe=events.append)
        self.assertEqual(result, (0, "exact", "error"))
        self.assertEqual([event["phase"] for event in events],
                         ["spawned", "direct-exited"])
        self.assertIsNone(events[0]["returncode"])
        self.assertEqual(events[1]["returncode"], 0)

    def test_spawn_observer_error_is_not_success(self):
        def reject(event):
            raise OSError("receipt unavailable")

        result = run_capture([sys.executable, "-B", "-c", "print('done')"],
                             idle=10, max_total=15, observe=reject)
        self.assertEqual(result[0], 125)
        self.assertIn("[observer-error]", result[2])
        self.assertIn("receipt unavailable", result[2])

    def test_spawn_is_synchronous_while_owned_pid_alive(self):
        root, command = self.owned_child()
        events, witnesses = [], []
        caller_thread = threading.get_ident()

        def observe(event):
            self.assertEqual(threading.get_ident(), caller_thread)
            events.append(event)
            self.assert_observation(event, event["phase"])
            self.assertIsNone(event["error"])
            if event["phase"] == "spawned":
                witnesses.append(self.await_ready(root, event))
                if os.name != "nt":
                    self.assertEqual(os.getpgid(event["pid"]), event["process_group"])
                self.assertFalse((root / "completed").exists())
                (root / "release").write_text("go")
            else:
                self.assertFalse(witnesses[0].alive())
                self.assertEqual((root / "completed").read_text(), "finished")

        result = run_capture(command, cwd=root, idle=10, max_total=20, observe=observe)
        self.assertEqual(result, (0, "exact", "error"))
        self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
        self.assertEqual(events[0]["pid"], events[1]["pid"])
        self.assertIsNone(events[0]["returncode"])
        self.assertEqual(events[1]["returncode"], 0)
        print("live-rendezvous:", json.dumps(events))

    def test_nonzero_exit_is_a_direct_child_fact(self):
        events = []
        result = run_capture(
            [sys.executable, "-B", "-c",
             "import sys;print('out');sys.stderr.write('err');sys.exit(23)"],
            idle=10, max_total=15, observe=events.append)
        self.assertEqual(result, (23, "out\n", "err"))
        self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
        self.assert_observation(events[1], "direct-exited")
        self.assertEqual(events[1]["returncode"], 23)
        self.assertIsNone(events[1]["error"])

    def test_launch_failure_has_no_fabricated_pid_or_exit(self):
        root, _ = self.owned_child()
        events = []
        result = run_capture([str(root / "missing-executable")], idle=10, max_total=15,
                             observe=events.append)
        self.assertEqual(result, (127, "", "not found"))
        self.assertEqual(len(events), 1)
        self.assert_observation(events[0], "launch-failed")
        self.assertIsNone(events[0]["returncode"])
        self.assertTrue(events[0]["error"])

    def test_other_launch_error_is_observed(self):
        root, _ = self.owned_child()
        not_directory = root / "file"
        not_directory.write_text("not a working directory")
        events = []
        result = run_capture([sys.executable, "-B", "-c", "print('not reached')"],
                             cwd=not_directory, idle=10, max_total=15, observe=events.append)
        self.assertEqual(result[0], 125)
        self.assertEqual(result[1], "")
        self.assertEqual(len(events), 1)
        self.assert_observation(events[0], "launch-failed")
        self.assertEqual(events[0]["error"], result[2])

    def test_launch_failure_observer_error_is_explicit(self):
        root, _ = self.owned_child()
        events = []

        def reject(event):
            events.append(event)
            raise OSError("launch journal unavailable")

        result = run_capture([str(root / "missing")], idle=10, max_total=15, observe=reject)
        self.assertEqual(result[0:2], (125, ""))
        self.assertIn("not found", result[2])
        self.assertIn("[observer-error] launch-failed: OSError: launch journal unavailable", result[2])
        self.assertEqual(len(events), 1)
        self.assert_observation(events[0], "launch-failed")

    def test_spawn_observer_failure_cleans_up_specific_live_pid(self):
        root, command = self.owned_child()
        events, witnesses = [], []

        def reject_spawn(event):
            events.append(event)
            if event["phase"] == "spawned":
                witnesses.append(self.await_ready(root, event))
                raise OSError("spawn journal unavailable")
            self.assertFalse(witnesses[0].alive())

        result = run_capture(command, cwd=root, idle=10, max_total=20, observe=reject_spawn)
        self.assertEqual(result[0], 125)
        self.assertIn("[observer-error] spawned: OSError: spawn journal unavailable", result[2])
        self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
        self.assert_observation(events[1], "direct-exited", "best-effort-attempted")
        self.assertEqual(events[1]["pid"], witnesses[0].pid)
        self.assertFalse(witnesses[0].alive())
        self.assertNotEqual(events[1]["returncode"], 0)
        self.assertIn("[observer-error]", events[1]["error"])
        self.assertFalse((root / "completed").exists())
        print("spawn-error-owned-cleanup:", json.dumps(events))

    def test_direct_exit_observer_failure_never_returns_success(self):
        root, command = self.owned_child()
        events, witnesses = [], []

        def reject_exit(event):
            events.append(event)
            if event["phase"] == "spawned":
                witnesses.append(self.await_ready(root, event))
                (root / "release").write_text("go")
            else:
                self.assertFalse(witnesses[0].alive())
                raise OSError("exit journal unavailable")

        result = run_capture(command, cwd=root, idle=10, max_total=20, observe=reject_exit)
        self.assertEqual(result[0:2], (125, "exact"))
        self.assertIn("error\n[observer-error] direct-exited: OSError: exit journal unavailable", result[2])
        self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
        self.assert_observation(events[1], "direct-exited")
        self.assertEqual(events[1]["returncode"], 0)
        self.assertFalse(witnesses[0].alive())
        self.assertEqual((root / "completed").read_text(), "finished")
        print("exit-error-owned-pid-already-dead:", json.dumps(events))

    def test_timeout_observations_report_actual_exit_and_cleanup_attempt(self):
        for idle, ceiling, code, marker in [(.2, 10, 124, "[idle-timeout]"),
                                            (10, .2, 125, "[max-timeout]")]:
            with self.subTest(code=code):
                root, command = self.owned_child()
                events, witnesses = [], []

                def observe(event):
                    events.append(event)
                    if event["phase"] == "spawned":
                        witnesses.append(self.await_ready(root, event))
                    else:
                        self.assertFalse(witnesses[0].alive())

                result = run_capture(command, cwd=root, idle=idle, max_total=ceiling,
                                     observe=observe)
                self.assertEqual(result, (code, "", marker))
                self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
                self.assert_observation(events[1], "direct-exited", "best-effort-attempted")
                self.assertEqual(events[1]["error"], marker)
                self.assertIs(type(events[1]["returncode"]), int)
                self.assertNotIn(events[1]["returncode"], (0, 124, 125))
                self.assertFalse(witnesses[0].alive())
                self.assertFalse((root / "completed").exists())
                print("timeout-owned-cleanup:", json.dumps(events))

    def test_explicit_none_retains_env_and_positional_compatibility(self):
        env = dict(os.environ, NATIVE_CAPTURE_TEST="specific")
        command = [sys.executable, "-B", "-c",
                   "import os,sys;sys.stdout.write(os.environ['NATIVE_CAPTURE_TEST']);sys.exit(7)"]
        self.assertEqual(run_capture(command, None, 10, 15, env=env, observe=None),
                         (7, "specific", ""))

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

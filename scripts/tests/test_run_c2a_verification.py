"""Independent C2a boundary proof; complements rather than repeats test_run."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from scripts.tests.test_run import ProcessWitness

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import run_capture


class ObserverBoundaryTests(unittest.TestCase):
    def wait_for(self, predicate, message):
        deadline = time.monotonic() + 10
        while not predicate():
            self.assertLess(time.monotonic(), deadline, message)
            time.sleep(.01)

    def witness(self, pid):
        witness = ProcessWitness(pid)
        self.addCleanup(witness.close)
        return witness

    def test_timeout_and_exit_callback_failure_preserve_both_diagnostics(self):
        events = []
        witnesses = []

        def observe(event):
            events.append(event)
            if event["phase"] == "spawned":
                witnesses.append(self.witness(event["pid"]))
                self.assertTrue(witnesses[0].alive())
            else:
                self.assertFalse(witnesses[0].alive())
                raise OSError("timeout exit receipt unavailable")

        result = run_capture(
            [sys.executable, "-B", "-c", "import time;time.sleep(15)"],
            idle=.2, max_total=5, observe=observe)
        self.assertEqual(result[0], 125)
        self.assertEqual(result[1], "")
        self.assertEqual(result[2], "[idle-timeout]\n[observer-error] direct-exited: "
                         "OSError: timeout exit receipt unavailable")
        self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
        self.assertEqual(events[1]["error"], "[idle-timeout]")
        self.assertEqual(events[1]["cleanup"], "best-effort-attempted")
        self.assertNotIn(events[1]["returncode"], (None, 0, 124, 125))
        print("independent-timeout-observer-composition:", json.dumps(events))

    def test_synchronous_callback_is_explicitly_outside_capture_timeout(self):
        with tempfile.TemporaryDirectory(prefix="c2a-independent-callback-") as directory:
            root = Path(directory)
            witnesses, events = [], []
            code = (
                "from pathlib import Path\nimport time,sys\n"
                "deadline=time.monotonic()+15\n"
                "while not Path('release').exists():\n"
                " if time.monotonic()>deadline: sys.exit(88)\n"
                " time.sleep(.01)\n"
                "Path('completed').write_text('actual completion')\n"
            )

            def observe(event):
                events.append(event)
                if event["phase"] == "spawned":
                    witnesses.append(self.witness(event["pid"]))
                    # Exceed both .1-second capture bounds while in this callback.
                    time.sleep(.7)
                    self.assertTrue(witnesses[0].alive())
                    self.assertFalse((root / "completed").exists())
                    (root / "release").write_text("go")
                    self.wait_for(lambda: not witnesses[0].alive(), "owned child did not exit")
                else:
                    self.assertFalse(witnesses[0].alive())

            result = run_capture([sys.executable, "-B", "-c", code], cwd=root,
                                 idle=.1, max_total=.1, observe=observe)
            self.assertEqual(result, (0, "", ""))
            self.assertEqual((root / "completed").read_text(), "actual completion")
            self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
            self.assertEqual(events[1]["returncode"], 0)
            print("independent-synchronous-timeout-boundary:", json.dumps(events))

    def test_direct_exit_failure_does_not_claim_or_kill_surviving_descendant(self):
        with tempfile.TemporaryDirectory(prefix="c2a-independent-descendant-") as directory:
            root = Path(directory)
            descendant_code = (
                "from pathlib import Path\nimport os,time,sys\n"
                "Path('descendant-ready').write_text(str(os.getpid()))\n"
                "deadline=time.monotonic()+15\n"
                "while not Path('descendant-release').exists():\n"
                " if time.monotonic()>deadline: sys.exit(88)\n"
                " time.sleep(.01)\n"
                "Path('descendant-completed').write_text('released by verifier')\n"
            )
            direct_code = (
                "import subprocess,sys,time\nfrom pathlib import Path\n"
                f"subprocess.Popen([sys.executable,'-B','-c',{descendant_code!r}],"
                "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
                "deadline=time.monotonic()+15\n"
                "while not Path('direct-release').exists():\n"
                " if time.monotonic()>deadline: sys.exit(88)\n"
                " time.sleep(.01)\n"
            )
            events, witnesses, launches = [], [], []
            active = [True]
            command = [sys.executable, "-B", "-c", direct_code]

            def audit(name, args):
                if active[0] and name == "subprocess.Popen":
                    launches.append(args[1])

            # Observe real attempted launches; no substituted Popen/kill behavior.
            sys.addaudithook(audit)

            def observe(event):
                events.append(event)
                if event["phase"] == "spawned":
                    witnesses.append(self.witness(event["pid"]))
                    ready = root / "descendant-ready"
                    self.wait_for(lambda: ready.exists() and ready.stat().st_size > 0,
                                  "descendant did not rendezvous")
                    witnesses.append(self.witness(int(ready.read_text())))
                    self.assertTrue(witnesses[0].alive())
                    self.assertTrue(witnesses[1].alive())
                    (root / "direct-release").write_text("go")
                else:
                    self.assertFalse(witnesses[0].alive())
                    self.assertTrue(witnesses[1].alive())
                    raise OSError("direct exit persistence failure")

            try:
                result = run_capture(command, cwd=root,
                                     idle=10, max_total=20, observe=observe)
                self.assertEqual(result, (125, "", "[observer-error] direct-exited: "
                                         "OSError: direct exit persistence failure"))
                self.assertEqual([event["phase"] for event in events], ["spawned", "direct-exited"])
                self.assertEqual(events[1]["returncode"], 0)
                self.assertEqual(events[1]["cleanup"], "not-attempted")
                self.assertIsNone(events[1]["error"])
                self.assertFalse(witnesses[0].alive())
                self.assertTrue(witnesses[1].alive())
                self.assertFalse((root / "descendant-completed").exists())
                audited_command = subprocess.list2cmdline(command) if os.name == "nt" else command
                self.assertEqual(launches, [audited_command],
                                 "No taskkill/reaped-PID cleanup command may be launched")
                print("independent-surviving-descendant:", json.dumps({
                    "events": events, "descendant_pid": witnesses[1].pid,
                    "descendant_alive_after_return": witnesses[1].alive(), "launches": launches}))
            finally:
                active[0] = False
                (root / "direct-release").write_text("go")
                (root / "descendant-release").write_text("go")
                for witness in witnesses:
                    self.wait_for(lambda: not witness.alive(), "owned process failed to release")
            self.assertEqual((root / "descendant-completed").read_text(), "released by verifier")
            print("independent-descendant-cleanup: cooperative release; retained handles signalled")


if __name__ == "__main__":
    unittest.main()

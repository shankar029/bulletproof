"""Additive resumed-owner captures; preserve all predecessor and verifier files."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("prior_capture", HERE / "q1-review-correction-capture.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.PREFIX = "q1-resumed-correction-"
_save = prior.save


def save(label, value):
    if label.endswith("-command"):
        value["outer_bounds"] = {"idle": 120, "max": 1200}
    _save(label, value)


prior.save = save
prior.original.INPUTS += [
    str(Path(__file__).resolve()),
    "scripts/tests/test_measure_q1_resumed.py",
    ".ai/workflow-reliability/baseline-materialization-contract.json",
    ".ai/workflow-reliability/evidence/q1-review-correction-qualification.json",
]
dependencies = HERE / "q1-resumed-correction-core-dependencies.json"
if dependencies.exists():
    prior.original.INPUTS += list(json.loads(dependencies.read_bytes())["before"])
    prior.original.INPUTS += [str(dependencies)]


def native_progress(event, args):
    if event == "subprocess.Popen":
        # Actual process creation, not a timer/heartbeat or simulated progress.
        print("[native-start] " + str(args[0]), file=sys.stderr, flush=True)
    elif event == "tempfile.mkdtemp":
        print("[owned-temp] " + str(args[0]), file=sys.stderr, flush=True)


def capture(pattern, label):
    """Flush real raw streams during execution so even a tree kill retains them."""
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", pattern, label]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", Q1_VERIFICATION_TAG="resumed-" + label)
    start = time.monotonic()
    paths = {key: HERE / (prior.PREFIX + label + "." + key + ".bin")
             for key in ("stdout", "stderr")}
    streams = {key: path.open("xb") for key, path in paths.items()}
    try:
        proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        metadata = {"argv": argv, "cwd": str(ROOT), "worker_pid": proc.pid,
                    "capture_pid": os.getpid(), "outer_bounds": {"idle": 120, "max": 1200},
                    "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1",
                                          "Q1_VERIFICATION_TAG": env["Q1_VERIFICATION_TAG"]}}
        prior.save(label + "-launch", metadata)

        def pump(key):
            pipe = getattr(proc, key)
            while data := pipe.read1(65536):
                streams[key].write(data)
                streams[key].flush()
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
            pipe.close()

        threads = [threading.Thread(target=pump, args=(key,)) for key in streams]
        for thread in threads:
            thread.start()
        code = proc.wait()
        for thread in threads:
            thread.join()
    finally:
        for stream in streams.values():
            stream.close()
    raw = {key: {"path": str(path), **prior.original.hashes([path])[str(path)]}
           for key, path in paths.items()}
    prior.save(label + "-command", {**metadata, "exit_code": code,
                                   "seconds": time.monotonic() - start, "raw": raw})
    return code


def preserve():
    paths = [path for path in HERE.rglob("*") if path.is_file()
             and not path.name.startswith(prior.PREFIX)]
    paths += list((ROOT / "scripts/tests").glob("test_measure*.py"))
    paths += [ROOT / "scripts" / name for name in ("measure.py", "measure_graph.py", "probe.py")]
    pins = prior.original.hashes(paths)
    qualification = json.loads((HERE / "q1-review-correction-qualification.json").read_bytes())
    for command in qualification["commands"]:
        for raw in command["raw"].values():
            actual = prior.original.hashes([Path(raw["path"])])[raw["path"]]
            assert actual == {key: raw[key] for key in ("bytes", "sha256")}, raw
    prior.save("initial-pins", pins)
    print(json.dumps({"pins": len(pins), "qualification": qualification["status"],
                      "source": {name: ref for name, ref in pins.items()
                                 if Path(name).parent == ROOT / "scripts"}}, indent=2))


if __name__ == "__main__":
    action, *args = sys.argv[1:]
    if action == "preserve":
        preserve()
    else:
        # Point the wrapper's child back here, retaining unique fixture destinations.
        prior.__file__ = __file__
        if action == "worker":
            sys.addaudithook(native_progress)
        sys.exit(prior.worker(*args) if action == "worker" else capture(*args))

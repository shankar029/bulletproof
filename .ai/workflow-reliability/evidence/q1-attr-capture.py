"""Short, additive capture namespace for the final attribute-boundary correction."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("resumed_capture", HERE / "q1-resumed-correction-capture.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
capture.prior.PREFIX = "q1-attr-"
capture.prior.original.INPUTS += [str(Path(__file__).resolve()), "scripts/tests/test_measure_q1_attr.py"]
capture.__file__ = __file__
capture.prior.__file__ = __file__

if __name__ == "__main__":
    action, *args = sys.argv[1:]
    if action == "worker":
        sys.addaudithook(capture.native_progress)
    sys.exit(capture.prior.worker(*args) if action == "worker" else capture.capture(*args))

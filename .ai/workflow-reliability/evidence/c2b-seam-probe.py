"""Bounded frozen-interface diagnosis; synthetic protocol, NOT recovery proof.

No child, platform reset, independent review, metric or CLI execution is
represented by these records. Real persistence and the pure gate are exercised.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/tests"))
from workflow_fixtures import WorkflowFixture
from evidence import exclusive_lock
from workflow_gate import evaluate
from workflow_state import target, validate_event


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isalnum():
        raise SystemExit("usage: c2b-seam-probe.py UNIQUEALPHANUMERICTAG")
    output = Path(__file__).with_name("c2b-seam-" + sys.argv[1] + ".json")
    if output.exists():
        raise SystemExit("Refusing to overwrite prior evidence")
    files = [
        "scripts/workflow_state.py", "scripts/workflow_gate.py",
        "scripts/evidence.py", "scripts/run.py",
        "scripts/tests/workflow_fixtures.py",
        ".ai/workflow-reliability/design-contracts.json",
        ".ai/workflow-reliability/guard-resolution-contract.json",
    ]

    def hashes():
        return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in files}

    before = hashes()
    fixture = WorkflowFixture()
    try:
        item = target("action", "A-work")
        snapshot = fixture.inputs(item).target
        run = "synthetic-unknown-run"
        admission = fixture.event("admitted", item, run, snapshot)
        fixture.append(admission)
        fixture.append(fixture.event("launch-intent", item, run, snapshot,
                                     spawned="unknown"))
        lock = fixture.workspace / "owned-seam.lock"
        owner = {"token": "synthetic-lock-token", "guard_pid": os.getpid(),
                 "created_at": datetime.now(timezone.utc).isoformat(),
                 "run_id": run, "workspace": str(fixture.workspace.resolve())}
        try:
            with exclusive_lock(lock, owner):
                raise OSError("Deliberate lexical-exit probe, not observer failure")
        except OSError:
            pass
        lock_removed = not lock.exists()
        rejected = {}
        for field, value in (("lock_owner", owner),
                             ("recovery_evidence", {"path": "proof.json", "sha256": "a" * 64})):
            candidate = deepcopy(admission)
            candidate.update(seq=2)
            candidate[field] = value
            try:
                validate_event(candidate)
            except ValueError as error:
                rejected[field] = str(error)

        def readiness():
            contract, _, ledger = fixture.load()
            return evaluate(contract, ledger, fixture.inputs(item), item)

        prior = readiness()
        for kind in ("interrupted", "recovered"):
            fixture.append(fixture.event(kind, item, run, snapshot,
                                         outcome="interrupted", spawned="unknown"))
        after = readiness()
        result = {
            "classification": "synthetic protocol diagnosis; no actual recovery or CLI proof",
            "argv": sys.orig_argv, "cwd": os.getcwd(),
            "python": sys.version, "generated": datetime.now(timezone.utc).isoformat(),
            "lexical_lock_removed_after_exception": lock_removed,
            "rejected_additional_event_fields": rejected,
            "before_recovery_events": prior,
            "after_synthetic_interrupted_recovered_events": after,
            "ledger": fixture.load()[2].document,
            "before_hashes": before, "after_hashes": hashes(),
        }
        assert lock_removed
        assert set(rejected) == {"lock_owner", "recovery_evidence"}
        assert any(b["code"] == "RECOVERY_UNVERIFIED" for b in prior["blockers"])
        assert any(b["code"] == "RECOVERY_UNVERIFIED" for b in after["blockers"])
        assert before == result["after_hashes"]
    finally:
        fixture.close()
    result["owned_fixture_removed"] = not fixture.root.exists()
    assert result["owned_fixture_removed"]
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

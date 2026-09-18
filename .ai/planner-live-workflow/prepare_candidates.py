"""Prepare task artifacts only; never adopt, execute work, or generate approval."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TASK = Path(__file__).resolve().parent
PREFIX = ".ai/planner-live-workflow/"
APP = "examples/team-planner/"
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_state import (
    canonical_hash, read_json, safe_path, validate_command, validate_contract,
    validate_design, validate_producer,
)

ACS = ["AC1", "AC2", "AC3", "AC4", "AC5"]
METRICS = [
    "duplication_pct", "complexity_max", "complexity_avg", "cycles",
    "dead_exports", "static_findings", "mutation_score_pct",
    "diff_coverage_pct", "architecture_rules",
]
EXISTING_TESTS = [
    "api", "command", "diagnosis", "lifecycle", "migration", "query",
    "rules", "schema", "store",
]
NEW_TESTS = ["archive", "archive-api", "csv"]
NATIVE_CHANGES = [APP + "test/" + name + ".test.mjs" for name in NEW_TESTS]
NATIVE_CHANGES.append(APP + "test/schema.test.mjs")
PRODUCTION_CHANGES = [
    APP + name for name in (
        "src/schema.mjs", "src/csv.mjs", "src/planner.mjs", "src/server.mjs",
        "public/app.mjs", "public/index.html", "scripts/e2e.mjs", "README.md",
    )
]


def relative(path):
    return path.relative_to(ROOT).as_posix()


def artifact(path):
    path = Path(path)
    return {"path": relative(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def publish(outputs):
    for path, content in outputs.items():
        if not path.is_relative_to(TASK):
            raise ValueError("Output outside assigned task")
        if path.exists() and path.read_bytes() != content:
            raise ValueError("Different retained artifact exists: " + relative(path))
    for path, content in outputs.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(content)


def guard_no_live_authority():
    for name in ("workflow.json", "current-design.json", "evidence/ledger.json",
                 "evidence/workflow.lock"):
        if (TASK / name).exists():
            raise ValueError("Preparation refuses live/runtime authority: " + name)


def command(argv, cwd=".", idle=60, maximum=180):
    return {
        "argv": argv, "cwd": cwd,
        "runtime": {"executable": argv[0], "observed_version": "v24.11.1"},
        "idle_seconds": idle, "max_seconds": maximum,
        "environment": {"NODE_TEST_CONTEXT": None},
    }


def initialize():
    """Capture observed task inputs, not invented actors, assertions, or work."""
    node = r"C:\Program Files\nodejs\node.exe"
    reporter = str(ROOT / "scripts" / "native_result.mjs")
    native = [node, "--test", "--test-timeout=30000", "--test-reporter=" + reporter]
    tests = lambda names: ["test\\" + name + ".test.mjs" for name in names]
    app_dir = APP.rstrip("/")
    commands = {
        "baseline": command(native + tests(EXISTING_TESTS), app_dir),
        "red": command(native + tests(["archive-api"]), app_dir),
        "green": command(native + tests(EXISTING_TESTS + NEW_TESTS), app_dir),
        "coverage": command(
            native + ["--experimental-test-coverage", "--test-coverage-include=src/**"]
            + tests(EXISTING_TESTS + NEW_TESTS), app_dir),
        "browser_all": command([node, "scripts\\e2e.mjs", "--flow", "all"],
                               app_dir, 120, 1800),
        "browser_archive": command([node, "scripts\\e2e.mjs", "--flow", "archive"],
                                   app_dir, 120, 900),
    }
    inventory = []
    for folder in ("src", "public", "scripts", "test"):
        inventory.extend(relative(p) for p in (ROOT / app_dir / folder).rglob("*") if p.is_file())
    inventory.extend(APP + p for p in ("package.json", "README.md", ".gitignore", ".gitattributes"))
    inventory = sorted(set(inventory + NATIVE_CHANGES + PRODUCTION_CHANGES))
    source_hashes = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if (ROOT / name).is_file() else None for name in inventory
    }
    components = read_json(TASK / "contracts/r1.json")
    inputs = {name: artifact(TASK / name) for name in (
        "research.md", "clarifications.md", "state.md", "design.html", "ux.html",
        "contracts/r1.json", "design-review.md", "evidence/doc-render-verification.md",
    )}
    preparation = {
        "artifact_type": "pending-candidate-preparation-not-workflow-authority",
        "planning_revision": 1, "design_revision": "r1",
        "baseline": "c6095e7a8242cb1794fe78ca8fb8ea97e1fb9478",
        "inputs": inputs, "source_inventory": inventory, "source_sha256": source_hashes,
        "component_hashes": {key: canonical_hash(value) for key, value in components.items()},
        "commands": commands, "required_metrics": METRICS,
        "bindings_required": {
            "roles": {name: None for name in
                      ("parent", "researcher", "design_reviewer", "verifier", "reviewer")},
            "work_commands": {"A-I1-tests": None, "A-I1-implement": None},
            "red_assertions": [],
        },
        "blockers": [
            "Null-command work is forbidden by _action; no ordinary manual-edit handoff.",
            "Real red test source/hash/lines absent; test-only bootstrap requires parent decision.",
            "Actual role metadata must be supplied, never inferred from fixture actors.",
            "Existing independent report is REVISE and did not review this workflow candidate.",
            "Qualified required metrics collection/attachment unavailable; closure stays blocked.",
        ],
    }
    pending = {
        "artifact_type": "pending-review-inputs-not-DesignReview",
        "producer": None, "designer": None,
        "candidate_hashes": {
            "document": inputs["design.html"]["sha256"],
            "components": preparation["component_hashes"], "workflow_contract": None,
        },
        "verdict": "REVISE", "artifact": inputs["design-review.md"],
        "disposition_refs": [
            {"finding_id": finding, "path": PREFIX + "design-history/r1.parent-disposition.md",
             "sha256": inputs["state.md"]["sha256"]} for finding in ("DR1", "DR2")
        ],
        "human_approval": "unconfirmed",
        "unattended_authorization": {
            "path": PREFIX + "design-history/r1.unattended-authorization.md",
            "sha256": inputs["clarifications.md"]["sha256"],
        },
        "follow_up": "Actual independent candidate-bound review required; never infer APPROVE.",
    }
    publish({
        TASK / "design-history/r1.preparation.json": encoded(preparation),
        TASK / "design-history/r1.review.pending.json": encoded(pending),
        TASK / "design-history/r1.html": (TASK / "design.html").read_bytes(),
        TASK / "design-history/r1.parent-disposition.md": (TASK / "state.md").read_bytes(),
        TASK / "design-history/r1.unattended-authorization.md": (TASK / "clarifications.md").read_bytes(),
    })
    print("PREPARATION_RETAINED: no strict workflow, approval, adoption or execution created")


def check_bindings(preparation, bindings):
    if bindings is None:
        raise ValueError("BLOCKED: supply real roles, executable work commands and red assertion bytes")
    required = preparation["bindings_required"]
    if set(bindings) != set(required):
        raise ValueError("Bindings require exactly roles, work_commands, red_assertions")
    roles = bindings["roles"]
    expected = {"parent": "implementer", "researcher": "researcher",
                "design_reviewer": "reviewer", "verifier": "verifier", "reviewer": "reviewer"}
    if set(roles) != set(expected):
        raise ValueError("All five actual role records required")
    for name, role in expected.items():
        validate_producer(roles[name])
        if roles[name]["role"] != role:
            raise ValueError("Wrong actual role: " + name)
    if len({p["context_id"] for p in roles.values()}) != len(expected):
        raise ValueError("Parent/research/design-review/verification/review contexts must be distinct")
    if set(bindings["work_commands"]) != set(required["work_commands"]):
        raise ValueError("Both real executable work commands are required")
    for value in bindings["work_commands"].values():
        if value is None:
            raise ValueError("Null work is unsupported; do not disguise implementation as a check")
        validate_command(value)
    if not bindings["red_assertions"]:
        raise ValueError("Actual behavioral-red assertions required")
    for assertion in bindings["red_assertions"]:
        if assertion["test_file"] != APP + "test/archive-api.test.mjs":
            raise ValueError("Red assertion must belong to registered native red test")
        content = safe_path(ROOT, assertion["test_file"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != assertion["source_sha256"]:
            raise ValueError("Red source hash mismatch")
        if any(type(line) is not int or not 1 <= line <= len(content.splitlines())
               for line in assertion["assertion_lines"]):
            raise ValueError("Red assertion line outside actual test bytes")


def build(preparation, bindings):
    roles = bindings["roles"]
    components = list(preparation["component_hashes"])
    scope = {"files": preparation["source_inventory"], "directories": [], "excluded_outputs": []}
    contract = {
        "schema_version": 1, "slug": "planner-live-workflow", "design_revision": "r1",
        "increments": {"I1": {"id": "I1", "acs": ACS, "components": components,
                               "requires": [], "implementers": [roles["parent"]]}},
        "actions": {}, "checks": {}, "claims": {},
        "revision_reason": "One integrated archive/read-only/CSV increment; candidate review pending",
    }
    ref = lambda kind, name: {"kind": kind, "id": name}

    def action(name, kind, owner, cmd, requires, changes=None):
        contract["actions"][name] = {
            "id": name, "increment": "I1", "kind": kind, "requires": requires,
            "command": cmd, "owner": owner, "inputs": scope, "components": components,
            "claims": [], "declared_changes": changes or [], "retirement": None,
        }

    def check(suffix, kind, role, command_key, requires, condition, *,
              temporal=False, assertions=None, steps=None):
        action_id, check_id = "A-I1-" + suffix, "C-I1-" + suffix
        action(action_id, "check", roles[role],
               preparation["commands"][command_key] if command_key else None, requires)
        contract["checks"][check_id] = {
            "id": check_id, "action_id": action_id, "acs": ACS, "kind": kind,
            "owner_role": roles[role]["role"],
            "context_rule": "independent" if role in ("verifier", "reviewer") else "same-allowed",
            "validity": "before-action" if temporal else "current",
            "assertions": assertions or [], "pass_condition": condition,
            "handoff_steps": steps or [],
        }

    check("baseline", "test", "parent", "baseline", [],
          "Existing nine app suites execute real leaf tests; complete native pass, no skips/cancellations.",
          temporal=True)
    action("A-I1-tests", "work", roles["parent"], bindings["work_commands"]["A-I1-tests"],
           [ref("check", "C-I1-baseline")], NATIVE_CHANGES)
    check("red", "behavioral-red", "parent", "red", [ref("action", "A-I1-tests")],
          "Registered feature assertion fails behaviorally on unchanged production, not setup/import.",
          temporal=True, assertions=bindings["red_assertions"])
    action("A-I1-implement", "work", roles["parent"], bindings["work_commands"]["A-I1-implement"],
           [ref("check", "C-I1-red")], PRODUCTION_CHANGES)
    check("green", "test", "parent", "green", [ref("action", "A-I1-implement")],
          "All existing/new native tests pass with relevant leaf inventory; no skipped/cancelled tests.")
    check("browser", "verification", "verifier", None, [ref("check", "C-I1-green")],
          "Every AC scenario in tasks.md T5/T6 independently verified against real browser/app/data.",
          steps=["Parent dispatches actual registered verifier with admitted snapshot and receipt refs.",
                 "Run commands.browser_all using agent-browser; capture actual downloads and failures.",
                 "Return per-AC FindingResult and hash-bound complete Receipt; never edit production."])
    check("metrics", "metrics", "parent", None, [ref("check", "C-I1-green")],
          "All REQUIRED metrics complete and qualified: " + ", ".join(METRICS)
          + "; nonregression, no new cycles, mutation >=60%, diff coverage >=80%. "
          "Current collector/producer bridge unavailable; closure BLOCKED.",
          steps=["Collect only genuine source-bound measurements if qualified facilities exist.",
                 "Missing collector/bridge blocks acceptance; do not forge or submit passing metrics."])
    check("review", "review", "reviewer", None,
          [ref("check", "C-I1-green"), ref("check", "C-I1-browser")],
          "Independent exact-diff/design/test review and per-AC reconciliation; real findings dispositioned. "
          "Disclose unavailable metrics; review cannot satisfy the separate mandatory metric check.",
          steps=["Parent dispatches actual fresh reviewer; supply real metrics evidence or blocker.",
                 "Reviewer writes actual independent findings/per-AC report without production edits.",
                 "Return original attribution and declared hash-bound report/dispositions in Receipt."])
    contract["increments"]["I1"]["requires"] = [
        ref("check", "C-I1-" + name) for name in ("green", "browser", "metrics", "review")
    ]
    pending = read_json(TASK / "design-history/r1.review.pending.json")
    review = {key: pending[key] for key in (
        "candidate_hashes", "verdict", "artifact", "disposition_refs",
        "human_approval", "unattended_authorization",
    )}
    review["producer"] = roles["design_reviewer"]
    review["designer"] = roles["parent"]
    review["candidate_hashes"]["workflow_contract"] = canonical_hash(contract)
    design = {
        "schema_version": 1, "revision": "r1",
        "document": artifact(TASK / "design-history/r1.html"),
        "contract": artifact(TASK / "contracts/r1.json"),
        "components": preparation["component_hashes"], "supersedes": None, "review": review,
        "history": [], "reason": "Pending exact-candidate independent review; human unconfirmed",
    }
    validate_contract(contract)
    validate_design(design)
    return contract, design, review


def verify_inputs(preparation):
    for ref in preparation["inputs"].values():
        if artifact(safe_path(ROOT, ref["path"])) != ref:
            raise ValueError("Planning input changed; re-anchor before preparing: " + ref["path"])
    for name, expected in preparation["source_sha256"].items():
        if name == APP + "test/archive-api.test.mjs":
            continue  # Only this red-suite bootstrap is allowed before the original baseline.
        path = safe_path(ROOT, name)
        observed = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if observed != expected:
            raise ValueError("Production/regression input changed before red: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--initialize", action="store_true")
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--stage", action="store_true")
    parser.add_argument("--bindings", help="Task-local JSON with actual roles, commands, assertions")
    args = parser.parse_args()
    guard_no_live_authority()
    if args.initialize:
        initialize()
        return
    preparation = read_json(TASK / "design-history/r1.preparation.json")
    verify_inputs(preparation)
    bindings = None
    if args.bindings:
        path = safe_path(ROOT, args.bindings)
        if not path.is_relative_to(TASK):
            raise ValueError("Bindings must be inside the assigned task")
        bindings = read_json(path)
    check_bindings(preparation, bindings)
    contract, design, review = build(preparation, bindings)
    if args.stage:
        publish({
            TASK / "design-history/r1.workflow.json": encoded(contract),
            TASK / "design-history/r1.current-design.json": encoded(design),
            TASK / "evidence/review-r1.json": encoded(review),
        })
    print("STRICT_SHAPES_VALID; review=REVISE; adoption BLOCKED; no workflow execution performed")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)

"""Adoption-binding protocol tests, not independent approval or quality proof.

Use actual owned Git repositories and hashed files. Design identities and
adoption records are explicitly synthetic policy inputs; no process or metric
events are used to claim execution.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import unittest

from helpers import GitFixture
from workflow_fixtures import WorkflowFixture
from evidence import write_json_atomic
from workflow_gate import evaluate
import workflow_state as state


class AdoptionBindingTests(unittest.TestCase):
    def setUp(self):
        self.git = GitFixture()
        self.addCleanup(self.git.close)
        self.root = self.git.root
        self.protocol = WorkflowFixture()
        self.addCleanup(self.protocol.close)
        shutil.copytree(self.protocol.root, self.root, dirs_exist_ok=True)
        self.workspace = self.root / ".ai/demo"
        self.contract, self.design, resolved = state.load_workspace(self.root, "demo")
        self.ledger = resolved.document
        self.node = state.target("action", "A-work")

    def test_shared_validator_accepts_coherent_explicit_triple(self):
        self.assertEqual(
            state.validate_design_binding(self.root, self.contract, self.design, self.ledger),
            self.design)

    def test_explicit_binding_matches_default(self):
        nodes = [state.target(kind, name)
                 for kind in ("action", "check", "increment")
                 for name in self.contract[kind + "s"]]
        nodes.append(state.target("ship", "ship"))
        before = self.file_bytes()
        inputs = deepcopy((self.contract, self.design, self.ledger))
        for node in nodes:
            with self.subTest(node=node):
                explicit = state.bind_inputs(self.root, self.contract, node,
                                             design=self.design, ledger=self.ledger)
                self.assertEqual(explicit, state.bind_inputs(self.root, self.contract, node))
                self.assertEqual(explicit.target["contract"]["binding_mode"], "guarded")
                self.assertEqual(explicit.target["source"]["binding_mode"], "standalone-source")
        self.assertEqual(inputs, (self.contract, self.design, self.ledger))
        self.assertEqual(self.file_bytes(), before)

    def file_bytes(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for base in (self.workspace, self.root / "src")
                for p in base.rglob("*") if p.is_file()}

    def assert_invalid(self, contract, design, ledger, message):
        before = self.file_bytes()
        inputs = deepcopy((contract, design, ledger))
        with self.assertRaisesRegex(ValueError, message):
            state.validate_design_binding(self.root, contract, design, ledger)
        with self.assertRaisesRegex(ValueError, message):
            state.bind_inputs(self.root, contract, self.node, design=design, ledger=ledger)
        self.assertEqual(inputs, (contract, design, ledger))
        self.assertEqual(self.file_bytes(), before)

    def test_optional_pair_is_required_and_keyword_only(self):
        before = self.file_bytes()
        for kwargs in ({"design": self.design}, {"ledger": self.ledger},
                       {"design": self.design, "ledger": None},
                       {"design": None, "ledger": self.ledger}):
            with self.subTest(kwargs=tuple(kwargs)), self.assertRaisesRegex(ValueError, "together"):
                state.bind_inputs(self.root, self.contract, self.node, **kwargs)
        with self.assertRaises(TypeError):
            state.bind_inputs(self.root, self.contract, self.node, self.design, self.ledger)
        self.assertEqual(
            state.bind_inputs(self.root, self.contract, self.node, design=None, ledger=None),
            state.bind_inputs(self.root, self.contract, self.node))
        self.assertEqual(self.file_bytes(), before)

    def test_prospective_triple_validates_without_live_authority(self):
        expected = state.bind_inputs(self.root, self.contract, self.node)
        for name in ("current-design.json", "workflow.json", "evidence/ledger.json"):
            (self.workspace / name).unlink()
        before = self.file_bytes()
        self.assertEqual(
            state.validate_design_binding(self.root, self.contract, self.design, self.ledger),
            self.design)
        self.assertEqual(
            state.bind_inputs(self.root, self.contract, self.node,
                              design=self.design, ledger=self.ledger), expected)
        with self.assertRaises(FileNotFoundError):
            state.load_workspace(self.root, "demo")
        with self.assertRaises(FileNotFoundError):
            state.bind_inputs(self.root, self.contract, self.node)
        self.assertEqual(self.file_bytes(), before)

    def test_explicit_basis_does_not_fall_back_to_invalid_or_missing_live_pointer(self):
        expected = state.bind_inputs(self.root, self.contract, self.node)
        pointer = self.workspace / "current-design.json"
        for content, error in ((b'{"schema_version":1,"schema_version":1}', ValueError),
                               (None, FileNotFoundError)):
            if content is None:
                pointer.unlink()
            else:
                pointer.write_bytes(content)
            before = self.file_bytes()
            self.assertEqual(
                state.bind_inputs(self.root, self.contract, self.node,
                                  design=self.design, ledger=self.ledger), expected)
            with self.assertRaises(error):
                state.bind_inputs(self.root, self.contract, self.node)
            with self.assertRaises(error):
                state.load_workspace(self.root, "demo")
            self.assertEqual(self.file_bytes(), before)

    def test_partial_revision_uses_old_basis_without_rewriting_actual_authority(self):
        old = state.bind_inputs(self.root, self.contract, state.target("ship", "ship"))
        self.protocol.components["a"]["signature"] = "a(value: int) -> int"
        self.protocol.adopt()
        shutil.copytree(self.protocol.root, self.root, dirs_exist_ok=True)
        new_contract, new_design, new_ledger = state.load_workspace(self.root, "demo")
        self.assertEqual(new_design["revision"], "r2")
        self.assertEqual(len(new_ledger.document["events"]), 2)
        write_json_atomic(self.workspace / "current-design.json", self.design)
        before = self.file_bytes()
        with self.assertRaisesRegex(ValueError, "revision disagree"):
            state.load_workspace(self.root, "demo")
        with self.assertRaisesRegex(ValueError, "revision disagree"):
            state.bind_inputs(self.root, new_contract, self.node)
        explicit = state.bind_inputs(self.root, self.contract, state.target("ship", "ship"),
                                     design=self.design, ledger=self.ledger)
        self.assertEqual(explicit, old)
        self.assertEqual(
            state.validate_design_binding(self.root, new_contract, new_design, new_ledger.document),
            new_design)
        self.assertEqual(self.file_bytes(), before)

    def test_explicit_schema_slug_and_guarded_binding_rejections(self):
        cases = [
            ("contract-version", lambda c, d, l: c.update(schema_version=2), "schema version"),
            ("contract-fields", lambda c, d, l: c.update(unapproved=True), "record fields"),
            ("ledger-version", lambda c, d, l: l.update(schema_version=2), "schema version"),
            ("ledger-fields", lambda c, d, l: l.update(unapproved=True), "record fields"),
            ("slug", lambda c, d, l: l.update(slug="other"), "slug mismatch"),
            ("design-version", lambda c, d, l: d.update(schema_version=2), "schema version"),
            ("sequence", lambda c, d, l: l["events"][0].update(seq=2), "contiguous"),
            ("guarded-mode", lambda c, d, l: l["events"][0]["inputs"]["contract"].pop("binding_mode"),
             "record fields"),
            ("source-hash", lambda c, d, l: l["events"][0]["inputs"]["source"].update(scope_sha256="0" * 64),
             "snapshot hash mismatch"),
        ]
        for name, mutate, message in cases:
            c, d, l = deepcopy((self.contract, self.design, self.ledger))
            mutate(c, d, l)
            with self.subTest(name=name):
                self.assert_invalid(c, d, l, message)
        for value in ({}, [], False):
            with self.subTest(malformed=value):
                self.assert_invalid(self.contract, value, self.ledger, "record fields")
                self.assert_invalid(self.contract, self.design, value, "record fields")

    def test_default_binding_also_rejects_ledger_slug_mismatch(self):
        ledger = dict(self.ledger, slug="other")
        write_json_atomic(self.workspace / "evidence/ledger.json", ledger)
        before = self.file_bytes()
        with self.assertRaisesRegex(ValueError, "slug mismatch"):
            state.bind_inputs(self.root, self.contract, self.node)
        with self.assertRaisesRegex(ValueError, "slug mismatch"):
            state.load_workspace(self.root, "demo")
        self.assertEqual(self.file_bytes(), before)

    def test_review_revision_and_history_policy_rejections_are_shared(self):
        cases = [
            ("revision", lambda d: d.update(revision="r2"), "revision disagree"),
            ("history", lambda d: d.update(supersedes="r0"), "supersedes/history"),
            ("path", lambda d: d["document"].update(path=".ai/demo/design-history/other.html"),
             "retained revision path"),
            ("document-hash", lambda d: d["document"].update(sha256="0" * 64), "Artifact changed"),
            ("review", lambda d: d["review"].update(verdict="REJECT"), "approved independent review"),
            ("role", lambda d: d["review"]["producer"].update(role="human"), "approved independent review"),
            ("designer-context", lambda d: d["review"]["producer"].update(context_id="implementer"),
             "not independent"),
            ("authorization", lambda d: d["review"].update(unattended_authorization=None),
             "unattended authorization"),
            ("candidate", lambda d: d["review"]["candidate_hashes"].update(workflow_contract="0" * 64),
             "candidate mismatch"),
        ]
        pointer = self.workspace / "current-design.json"
        original = pointer.read_bytes()
        for name, mutate, message in cases:
            design = deepcopy(self.design)
            mutate(design)
            with self.subTest(name=name):
                self.assert_invalid(self.contract, design, self.ledger, message)
                write_json_atomic(pointer, design)
                before = self.file_bytes()
                with self.assertRaisesRegex(ValueError, message):
                    state.load_workspace(self.root, "demo")
                with self.assertRaisesRegex(ValueError, message):
                    state.bind_inputs(self.root, self.contract, self.node)
                self.assertEqual(self.file_bytes(), before)
                pointer.write_bytes(original)

    def test_reviewer_must_differ_from_other_increment_implementers(self):
        design = deepcopy(self.design)
        design["review"]["designer"]["context_id"] = "different-designer"
        design["review"]["producer"]["context_id"] = "implementer"
        self.assert_invalid(self.contract, design, self.ledger, "not independent")

    def test_artifact_bytes_missing_review_authorization_and_dispositions_reject(self):
        refs = [self.design["document"], self.design["contract"],
                self.design["review"]["artifact"], self.design["review"]["unattended_authorization"]]
        disposition = self.root / ".ai/demo/evidence/disposition.txt"
        disposition.write_bytes(b"Synthetic disposition, not independent approval\n")
        self.design["review"]["disposition_refs"] = [{
            "finding_id": "finding-1", "path": disposition.relative_to(self.root).as_posix(),
            "sha256": hashlib.sha256(disposition.read_bytes()).hexdigest()}]
        refs.extend(self.design["review"]["disposition_refs"])
        self.assertEqual(
            state.validate_design_binding(self.root, self.contract, self.design, self.ledger), self.design)
        for ref in refs:
            path = self.root / ref["path"]
            original = path.read_bytes()
            with self.subTest(path=ref["path"]):
                path.write_bytes(original + b"tampered")
                self.assert_invalid(self.contract, self.design, self.ledger, "Artifact changed")
                path.unlink()
                before = self.file_bytes()
                with self.assertRaises(FileNotFoundError):
                    state.validate_design_binding(self.root, self.contract, self.design, self.ledger)
                with self.assertRaises(FileNotFoundError):
                    state.bind_inputs(self.root, self.contract, self.node,
                                      design=self.design, ledger=self.ledger)
                self.assertEqual(self.file_bytes(), before)
                path.write_bytes(original)

    def test_normative_component_and_adoption_bindings_cannot_be_substituted(self):
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        d["components"]["a"] = "0" * 64
        d["review"]["candidate_hashes"]["components"] = deepcopy(d["components"])
        self.assert_invalid(c, d, l, "Normative component hashes")
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        c["increments"]["A"]["components"].append("missing-component")
        d["review"]["candidate_hashes"]["workflow_contract"] = state.canonical_hash(c)
        self.assert_invalid(c, d, l, "Missing normative component")
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        l["events"] = []
        self.assert_invalid(c, d, l, "history/adoption mismatch")
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        l["events"][0]["inputs"]["contract"]["adopted_contract_sha256"] = "0" * 64
        self.assert_invalid(c, d, l, "adopted contract mismatch")
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        l["events"][0]["inputs"]["contract"]["components"]["a"] = "0" * 64
        self.assert_invalid(c, d, l, "adopted contract mismatch")
        c, d, l = deepcopy((self.contract, self.design, self.ledger))
        source = l["events"][0]["inputs"]["source"]
        source["files"][d["document"]["path"]]["sha256"] = "0" * 64
        source["scope_sha256"] = state.canonical_hash({"scope": source["scope"], "files": source["files"]})
        self.assert_invalid(c, d, l, "Adoption does not bind retained design bytes")

    def test_retained_history_stays_hash_checked_in_explicit_mode(self):
        self.protocol.adopt()
        shutil.copytree(self.protocol.root, self.root, dirs_exist_ok=True)
        c, d, ledger = state.load_workspace(self.root, "demo")
        self.assertEqual(len(d["history"]), 1)
        path = self.root / d["history"][0]["document"]["path"]
        path.write_bytes(path.read_bytes() + b"changed history")
        self.assert_invalid(c, d, ledger.document, "Artifact changed")

    def test_scope_materialization_uses_current_files_and_preserves_blocked_dependencies(self):
        self.protocol.contract["actions"]["A-work"]["inputs"] = {
            "files": ["missing.txt"], "directories": ["src"], "excluded_outputs": []}
        self.protocol.contract["actions"]["B-work"]["requires"] = [state.target("check", "A-test")]
        self.protocol.adopt()
        shutil.copytree(self.protocol.root, self.root, dirs_exist_ok=True)
        c, d, ledger = state.load_workspace(self.root, "demo")
        first = state.bind_inputs(self.root, c, self.node, design=d, ledger=ledger.document)
        self.assertEqual(first.target["source"]["files"]["missing.txt"]["mode"], "missing")
        self.git.write("src/added.py", "ADDED = 2\n")
        second = state.bind_inputs(self.root, c, self.node, design=d, ledger=ledger.document)
        self.assertEqual(second, state.bind_inputs(self.root, c, self.node))
        self.assertNotEqual(first.target["source"]["scope_sha256"], second.target["source"]["scope_sha256"])
        self.assertEqual(second.target["source"]["files"]["src/added.py"]["sha256"],
                         hashlib.sha256(b"ADDED = 2\n").hexdigest())
        # Reuse the existing snapshot failure path, not a permissive old-source fallback.
        (self.root / "src/A.py").unlink()
        (self.root / "src/A.py").mkdir()
        node = state.target("action", "A-test-run")
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            state.bind_inputs(self.root, c, node, design=d, ledger=ledger.document)
        node = state.target("action", "B-work")
        resolved = state.bind_inputs(self.root, c, node,
                                     design=d, ledger=ledger.document)
        self.assertIsInstance(resolved.targets["action:A-test-run"], state.BlockedInput)
        self.assertEqual(resolved, state.bind_inputs(self.root, c, node))
        self.assertEqual(evaluate(c, ledger, resolved, node)["status"], "blocked")

    def test_explicit_prefix_does_not_remove_unresolved_admission_from_gate(self):
        snapshot = state.bind_inputs(self.root, self.contract, self.node).target
        ledger = deepcopy(self.ledger)
        event = self.protocol.event("admitted", self.node, "synthetic-pending", snapshot,
                                    spawned="unknown")
        ledger["events"].append(dict(event, seq=len(ledger["events"]) + 1))
        state.validate_ledger(ledger)
        write_json_atomic(self.workspace / "evidence/ledger.json", ledger)
        (self.workspace / "current-design.json").write_bytes(b"incomplete publication")
        before = self.file_bytes()
        node = state.target("ship", "ship")
        resolved = state.bind_inputs(self.root, self.contract, node,
                                     design=self.design, ledger=ledger)
        readiness = evaluate(self.contract, state.ResolvedLedger(ledger, {}), resolved, node)
        self.assertEqual(readiness["status"], "blocked")
        self.assertIn("RECOVERY_UNVERIFIED", {b["code"] for b in readiness["blockers"]})
        self.assertIsNone(readiness["next_command"])
        self.assertEqual(self.file_bytes(), before)

    def test_fresh_process_reads_explicit_old_basis_without_publication(self):
        self.git.commit("fixture: synthetic adoption documents")
        before = self.file_bytes()
        scripts = Path(__file__).resolve().parents[1]
        code = """
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from workflow_state import read_json, validate_design_binding, bind_inputs, target
root = Path(sys.argv[2])
workspace = root / '.ai/demo'
c = read_json(workspace / 'workflow.json')
d = read_json(workspace / 'current-design.json')
l = read_json(workspace / 'evidence/ledger.json')
validate_design_binding(root, c, d, l)
print(json.dumps(bind_inputs(root, c, target('action', 'A-work'), design=d, ledger=l).target))
"""
        rc, stdout, stderr = self.git.run(sys.executable, "-B", "-c", code, str(scripts), str(self.root))
        self.assertEqual(rc, 0, stderr)
        self.assertEqual(json.loads(stdout), state.bind_inputs(self.root, self.contract, self.node).target)
        self.assertEqual(self.file_bytes(), before)
        self.assertEqual(self.git.run("git", "status", "--porcelain")[1], "")


if __name__ == "__main__":
    unittest.main()

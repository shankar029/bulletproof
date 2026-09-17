"""Adoption-binding protocol tests, not independent approval or quality proof.

Use actual owned Git repositories and hashed files. Design identities and
adoption records are explicitly synthetic policy inputs; no process or metric
events are used to claim execution.
"""

from copy import deepcopy
import shutil
import unittest

from helpers import GitFixture
from workflow_fixtures import WorkflowFixture
import workflow_state as state


class AdoptionBindingTests(unittest.TestCase):
    def setUp(self):
        self.git = GitFixture()
        self.addCleanup(self.git.close)
        self.root = self.git.root
        fixture = WorkflowFixture()
        try:
            shutil.copytree(fixture.root, self.root, dirs_exist_ok=True)
        finally:
            fixture.close()
        self.workspace = self.root / ".ai/demo"
        self.contract, self.design, resolved = state.load_workspace(self.root, "demo")
        self.ledger = resolved.document
        self.node = state.target("action", "A-work")

    def test_shared_validator_accepts_coherent_explicit_triple(self):
        self.assertEqual(
            state.validate_design_binding(self.root, self.contract, self.design, self.ledger),
            self.design)

    def test_explicit_binding_matches_default(self):
        self.assertEqual(
            state.bind_inputs(self.root, self.contract, self.node,
                              design=self.design, ledger=self.ledger),
            state.bind_inputs(self.root, self.contract, self.node))


if __name__ == "__main__":
    unittest.main()

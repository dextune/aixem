"""Hierarchical composition routes, documentation linkage, and release evidence tests."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "docs"))

import aixem_docs  # noqa: E402


class HierarchicalAuthoringRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.documents = aixem_docs.load_documents()
        self.routes = aixem_docs.load_routes()
        self.by_route = {route["id"]: route for route in self.routes}

    def test_hierarchical_routes_are_bounded_and_resolvable(self) -> None:
        result = aixem_docs.validate_routes(self.routes, self.documents)
        self.assertTrue(result["valid"], result["errors"])
        for route_id in ("compose-project", "route-project-nets"):
            route = self.by_route[route_id]
            self.assertLessEqual(len(route["steps"]), 7)
            self.assertLessEqual(route["_computedBytes"], 96 * 1024)
            self.assertLessEqual(route["budget"]["max_depth"], 3)
            resolved = aixem_docs.route_query(route_id.replace("-", " "))
            self.assertFalse(resolved["fallbackUsed"], resolved)
            self.assertEqual(route_id, resolved["route"]["id"])

    def test_compose_project_route_reads_authority_before_examples(self) -> None:
        route = self.by_route["compose-project"]
        docs = [step["document"] for step in route["steps"]]
        self.assertEqual("AIXEM-SPEC-PROJECT-COMPOSITION-001", docs[0])
        self.assertIn("AIXEM-SPEC-INTERFACE-PORT-001", docs)
        self.assertIn("AIXEM-CONCEPT-PROJECT-NET-001", docs)
        self.assertIn("AIXEM-CONF-HIERARCHICAL-PROJECT-001", docs)

    def test_project_route_cannot_own_semantic_membership(self) -> None:
        route = self.by_route["route-project-nets"]
        docs = [step["document"] for step in route["steps"]]
        self.assertEqual("AIXEM-CONCEPT-PROJECT-NET-001", docs[0])
        self.assertIn("AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001", docs)
        self.assertIn("AIXEM-AGENT-ROUTING-001", docs)
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for rule in (
            "Project -> Sheet -> Layer",
            "A layer is not a schematic sheet",
            "Same names never imply cross-sheet electrical connectivity",
            "route-project-nets",
            "interface summaries",
        ):
            self.assertIn(rule.lower(), text.lower())

    def test_document_graph_has_no_hierarchical_linkage_gap(self) -> None:
        result = aixem_docs.validate_documents(self.documents)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual([], aixem_docs.detect_dependency_cycles(self.documents))
        ids = {doc.meta["id"] for doc in self.documents}
        for required in (
            "AIXEM-SPEC-INTERFACE-PORT-001",
            "AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001",
            "AIXEM-SPEC-PROJECT-COMPOSITION-001",
            "AIXEM-CONCEPT-PROJECT-NET-001",
            "AIXEM-CONF-HIERARCHICAL-PROJECT-001",
        ):
            self.assertIn(required, ids)

    def test_three_pass_release_evidence(self) -> None:
        for index in range(1, 4):
            path = ROOT / "validation" / "evidence" / f"pass-{index:02d}" / "hierarchical-verification.json"
            self.assertTrue(path.is_file(), path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(index, payload["pass"])
            self.assertEqual("PASS", payload["status"])
            self.assertTrue(payload["documentLinkage"]["valid"])
            self.assertEqual([], payload["documentLinkage"]["errors"])
            self.assertTrue(payload["checks"])
            self.assertTrue(all(check["status"] == "PASS" for check in payload["checks"]), payload)


if __name__ == "__main__":
    unittest.main()

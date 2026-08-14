"""Simple/composite authoring route and task-packet tests."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "docs"))

import aixem_docs  # noqa: E402


class AuthoringRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.documents = aixem_docs.load_documents()
        self.routes = aixem_docs.load_routes()
        self.by_route = {route["id"]: route for route in self.routes}

    def test_composite_route_chain(self) -> None:
        route = self.by_route["author-component-circuit"]
        self.assertEqual(route.get("kind"), "composite")
        self.assertEqual(
            [stage["route"] for stage in route["stages"]],
            ["create-symbol", "create-schematic", "route-nets", "render-review", "validate-project"],
        )
        result = aixem_docs.validate_routes(self.routes, self.documents)
        self.assertTrue(result["valid"], result["errors"])

    def test_authoring_route_budgets(self) -> None:
        result = aixem_docs.validate_routes(self.routes, self.documents)
        self.assertTrue(result["valid"], result["errors"])
        for route_id in ("create-symbol", "create-schematic", "route-nets", "render-review", "validate-project"):
            route = self.by_route[route_id]
            self.assertLessEqual(len(route["steps"]), 7)
            self.assertLessEqual(route["_computedBytes"], 96 * 1024)
            self.assertLessEqual(route["budget"]["max_depth"], 3)

    def test_agents_policy_contains_source_inspection_gate(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("do not inspect renderer implementation code before reading", text.lower())
        self.assertIn("author-component-circuit", text)
        self.assertIn("task-packets", text)

    def test_task_packets_match_route_sources(self) -> None:
        aixem_docs.compile_generated()
        index = json.loads((ROOT / "docs" / "_meta" / "generated" / "task-packet-index.json").read_text(encoding="utf-8"))
        self.assertEqual({item["id"] for item in index["packets"]}, set(self.by_route))
        for item in index["packets"]:
            packet_path = ROOT / item["path"]
            self.assertTrue(packet_path.is_file())
            self.assertEqual(item["digest"], aixem_docs.sha256_file(packet_path))
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["id"], item["id"])
            self.assertTrue(packet["sourceDigest"])
            schema = ROOT / "docs" / "_meta" / "schema" / "task-packet.schema.json"
            self.assertEqual([], aixem_docs.validate_json_schema(packet, schema, packet_path.relative_to(ROOT).as_posix()))
        index_schema = ROOT / "docs" / "_meta" / "schema" / "task-packet-index.schema.json"
        self.assertEqual([], aixem_docs.validate_json_schema(index, index_schema, "task-packet-index.json"))


if __name__ == "__main__":
    unittest.main()

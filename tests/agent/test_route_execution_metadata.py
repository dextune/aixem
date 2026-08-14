from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.diagnostics import RECOMMENDED_P0_CODES  # noqa: E402


class RouteExecutionMetadataTests(unittest.TestCase):
    AUTHORING_ROUTES = {
        "create-symbol", "create-schematic", "route-nets", "compose-project",
        "route-project-nets", "render-review", "validate-project",
    }

    def test_canonical_authoring_routes_have_scope_and_remediation_metadata(self) -> None:
        route_dir = ROOT / "docs/_meta/routes"
        routes = {path.stem: yaml.safe_load(path.read_text(encoding="utf-8")) for path in route_dir.glob("*.yaml")}
        for route_id in self.AUTHORING_ROUTES:
            with self.subTest(route=route_id):
                route = routes[route_id]
                self.assertIn("writes", route)
                self.assertIn("remediation", route)
                self.assertIn("authority", route["writes"])
                self.assertIn("artifacts", route["writes"])
        composite = routes["author-component-circuit"]
        self.assertFalse((composite.get("writes") or {}).get("authority"))
        self.assertFalse((composite.get("writes") or {}).get("artifacts"))

    def test_task_packets_expose_active_child_scope(self) -> None:
        packet_dir = ROOT / "docs/_meta/generated/task-packets"
        composite = json.loads((packet_dir / "author-component-circuit.json").read_text(encoding="utf-8"))
        self.assertNotIn("writes", composite)
        for stage in composite["stages"]:
            with self.subTest(stage=stage["route"]):
                self.assertIn("writes", stage)
                child = json.loads((packet_dir / f"{stage['route']}.json").read_text(encoding="utf-8"))
                self.assertEqual(child["writes"], stage["writes"])
                self.assertEqual(child["remediation"], stage["remediation"])

    def test_all_recommended_diagnostics_are_accepted_by_an_existing_route(self) -> None:
        accepted = set()
        routes = set()
        for path in (ROOT / "docs/_meta/routes").glob("*.yaml"):
            route = yaml.safe_load(path.read_text(encoding="utf-8")); routes.add(route["id"])
            accepted.update(route.get("remediation", {}).get("acceptsDiagnostics", []))
        self.assertEqual(set(), RECOMMENDED_P0_CODES - accepted)
        for path in (ROOT / "docs/_meta/generated/task-packets").glob("*.json"):
            packet = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(packet["id"], routes)


if __name__ == "__main__":
    unittest.main()

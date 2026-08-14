from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import build_change_set, snapshot_workspace  # noqa: E402
from agent.diagnostics import assign_diagnostic_ids, make_diagnostic  # noqa: E402
from agent.run_record import build_run_record, detect_loop_state, make_iteration_record  # noqa: E402


class AgentRunRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        schema_root = ROOT / "docs/specifications/schemas/agent"
        self.diag_schema = json.loads((schema_root / "aixem-agent-diagnostic-1.schema.json").read_text())
        self.change_schema = json.loads((schema_root / "aixem-agent-change-set-1.schema.json").read_text())
        self.run_schema = json.loads((schema_root / "aixem-agent-run-record-1.schema.json").read_text())
        self.validator = Draft202012Validator(
            self.run_schema,
            resolver=RefResolver.from_schema(
                self.run_schema,
                store={self.diag_schema["$id"]: self.diag_schema, self.change_schema["$id"]: self.change_schema},
            ),
        )

    def _snapshots(self, root: Path):
        path = root / "x.aixlayout.json"
        path.write_text('{}\n', encoding="utf-8")
        before = snapshot_workspace(root)
        path.write_text('{"layout":1}\n', encoding="utf-8")
        after = snapshot_workspace(root)
        return before, after

    def test_closed_record_is_schema_valid_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            before, after = self._snapshots(Path(td))
            change_set = build_change_set(
                before, after, route="route-nets",
                scope={"authority":["layout"],"artifacts":["**/*.aixlayout.json"],"derived":[],"prohibited":[]},
                iteration=1,
            )
            iteration = make_iteration_record(
                iteration=1, route="route-nets", stage="VALIDATED", diagnostics_before=[],
                change_set=change_set, diagnostics_after=[], validators=["schematic.route_closure"],
            )
            kwargs = dict(
                release="AIXEM-SRP-0.5.5-2026-08-11", task_id="closed", entry_route="route-nets",
                active_route="route-nets", task_packet_digest="sha256:" + "0"*64,
                baseline_snapshot=before, final_snapshot=after, route_chain=["route-nets"],
                iterations=[iteration], final_diagnostics=[], render_artifacts={"render/drawing.svg":"sha256:"+"1"*64},
                determinism={"valid":True,"repeatCount":3,"projectRuns":3,"changed":[]},
            )
            first = build_run_record(**kwargs); second = build_run_record(**kwargs)
            self.validator.validate(first)
            self.assertEqual(first, second)
            self.assertEqual("CLOSED", first["final"]["status"])
            self.assertTrue(first["final"]["conformant"])
            self.assertFalse(first["execution"]["liveExternalAgentExecuted"])

    def test_blocking_diagnostic_prevents_closure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            before, after = self._snapshots(Path(td))
            change_set = build_change_set(
                before, after, route="route-nets",
                scope={"authority":["layout"],"artifacts":["**/*.aixlayout.json"],"derived":[],"prohibited":[]}, iteration=1,
            )
            diagnostic = assign_diagnostic_ids([
                make_diagnostic("AIXEM-DIAG-ROUTE-NON-ORTHOGONAL", "diagonal", artifact="x.aixlayout.json")
            ])[0].to_dict()
            iteration = make_iteration_record(
                iteration=1, route="route-nets", stage="DIAGNOSED", diagnostics_before=[], change_set=change_set,
                diagnostics_after=[diagnostic], validators=[],
            )
            record = build_run_record(
                release="AIXEM-SRP-0.5.5-2026-08-11", task_id="blocked", entry_route="route-nets",
                active_route="route-nets", task_packet_digest="sha256:" + "0"*64,
                baseline_snapshot=before, final_snapshot=after, route_chain=["route-nets"], iterations=[iteration],
                final_diagnostics=[diagnostic], render_artifacts={},
                determinism={"valid":False,"repeatCount":0,"projectRuns":0,"changed":[]},
            )
            self.validator.validate(record)
            self.assertEqual("BLOCKED", record["final"]["status"])
            self.assertFalse(record["final"]["conformant"])

    def test_stalled_and_oscillating_state_detection(self) -> None:
        stalled = [{
            "iteration": 1, "blockingAfter": 1, "diagnosticStateBefore": "sha256:"+"a"*64,
            "diagnosticStateAfter": "sha256:"+"a"*64, "authoritativeDigestBefore": "sha256:"+"1"*64,
            "authoritativeDigestAfter": "sha256:"+"1"*64,
        }]
        self.assertTrue(detect_loop_state(stalled)["stalled"])
        oscillating = [
            {"iteration":1,"blockingAfter":1,"diagnosticStateBefore":"d0","diagnosticStateAfter":"d1","authoritativeDigestBefore":"a0","authoritativeDigestAfter":"a1"},
            {"iteration":2,"blockingAfter":1,"diagnosticStateBefore":"d1","diagnosticStateAfter":"d2","authoritativeDigestBefore":"a1","authoritativeDigestAfter":"a2"},
            {"iteration":3,"blockingAfter":1,"diagnosticStateBefore":"d2","diagnosticStateAfter":"d1","authoritativeDigestBefore":"a2","authoritativeDigestAfter":"a1"},
        ]
        self.assertTrue(detect_loop_state(oscillating)["oscillating"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.observation import ObservationError, make_event, validate_events, write_events  # noqa: E402

SCHEMA = ROOT / "docs/specifications/schemas/agent/aixem-agent-observation-event-1.schema.json"


class ObservationEventContractTests(unittest.TestCase):
    def test_observable_stream_is_sequence_checked_and_digest_addressed(self) -> None:
        events = [
            make_event(1, "task-open", target="task/agent-task.json", result="opened"),
            make_event(2, "route-resolve", route="create-symbol", target="reference/docs/_meta/generated/task-packets/create-symbol.json"),
            make_event(3, "validator", tool="agent_authoring.check", result="passed"),
            make_event(4, "completion", result="closed"),
        ]
        result = validate_events(events, SCHEMA, declared_coverage={"fileReads": True, "searches": False, "commands": True, "writes": False, "routeActions": True})
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(4, result["events"])
        self.assertTrue(result["digest"].startswith("sha256:"))
        with tempfile.TemporaryDirectory() as td:
            written = write_events(Path(td) / "observations.jsonl", events)
            self.assertEqual(result["digest"], written["digest"])

    def test_private_reasoning_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(ObservationError, "private reasoning"):
            make_event(1, "command", details={"reasoning": "private chain of thought"})
        invalid = make_event(1, "command", tool="x")
        invalid["scratchpad"] = "must not be retained"
        result = validate_events([invalid], SCHEMA)
        self.assertFalse(result["valid"])
        self.assertIn("private reasoning", " ".join(result["errors"]))

    def test_path_traversal_and_sequence_gaps_are_rejected(self) -> None:
        with self.assertRaisesRegex(ObservationError, "unsafe observation target"):
            make_event(1, "file-read", target="../secret")
        result = validate_events([make_event(2, "task-open", target="task/agent-task.json")], SCHEMA)
        self.assertFalse(result["valid"])
        self.assertIn("expected sequence 1", " ".join(result["errors"]))


if __name__ == "__main__":
    unittest.main()

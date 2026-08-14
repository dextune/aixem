from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.task_contract import TaskContractError, resolve_task_route, validate_task_document  # noqa: E402


class AgentTaskContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(
            (ROOT / "validation/agent-evals-3/cases/L008/agent-task.json").read_text(encoding="utf-8")
        )

    def test_valid_task_resolves_route_bounded_write_scope(self) -> None:
        validated = validate_task_document(self.task, ROOT)
        resolution = resolve_task_route(validated, ROOT)
        self.assertEqual("create-symbol", resolution["activeRoute"])
        self.assertEqual(["create-symbol"], resolution["routeChain"])
        self.assertEqual("derived-execution-only", resolution["authority"])
        self.assertEqual(
            sorted(self.task["writeConstraints"]["writablePaths"]),
            resolution["effectiveWriteScope"]["artifacts"],
        )
        self.assertTrue(resolution["taskDigest"].startswith("sha256:"))
        self.assertTrue(resolution["resolutionDigest"].startswith("sha256:"))

    def test_task_cannot_widen_route_authority(self) -> None:
        task = deepcopy(self.task)
        task["writeConstraints"]["writableAuthorities"].append("semantic")
        with self.assertRaisesRegex(TaskContractError, "widen route authority"):
            resolve_task_route(task, ROOT)

    def test_task_cannot_escape_workspace_or_write_prohibited_output(self) -> None:
        task = deepcopy(self.task)
        task["writeConstraints"]["writablePaths"] = ["../outside.aixsym.json"]
        with self.assertRaises(TaskContractError):
            resolve_task_route(task, ROOT)

        task = deepcopy(self.task)
        task["writeConstraints"]["writablePaths"] = ["render/drawing.svg"]
        with self.assertRaises(TaskContractError):
            resolve_task_route(task, ROOT)

    def test_simple_route_cannot_select_an_unrelated_active_route(self) -> None:
        task = deepcopy(self.task)
        task["activeRoute"] = "route-nets"
        with self.assertRaisesRegex(TaskContractError, "simple entry route"):
            resolve_task_route(task, ROOT)


if __name__ == "__main__":
    unittest.main()

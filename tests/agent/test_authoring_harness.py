from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tools/agent_authoring.py"
FIXTURE = ROOT / "examples/authoring/01-two-pin-passive"


class AuthoringHarnessTests(unittest.TestCase):
    def _run(self, *args: str, expected: int = 0) -> dict:
        proc = subprocess.run(
            ["python", str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(expected, proc.returncode, msg=f"stdout={proc.stdout}\nstderr={proc.stderr}")
        return json.loads(proc.stdout)

    def test_prepare_check_close_valid_project(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; state = root / "state"
            shutil.copytree(FIXTURE, workspace)
            prepared = self._run(
                "prepare", "--workspace", str(workspace), "--route", "author-component-circuit",
                "--stage-route", "create-symbol", "--task-id", "harness-valid",
                "--project", "project.aixproj.json", "--state-dir", str(state),
            )
            self.assertEqual("PREPARED", prepared["status"])
            self.assertEqual(["author-component-circuit", "create-symbol"], prepared["executionPacket"]["routeChain"])
            checked = self._run("check", "--state-dir", str(state))
            self.assertTrue(checked["valid"])
            closed = self._run("close", "--state-dir", str(state))
            self.assertTrue(closed["valid"])
            self.assertTrue(closed["summary"]["determinism"]["valid"])
            record = json.loads((state / "authoring-run-record.json").read_text(encoding="utf-8"))
            self.assertEqual("CLOSED", record["final"]["status"])
            self.assertFalse(record["execution"]["liveExternalAgentExecuted"])

    def test_generated_output_hand_edit_blocks_check(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; state = root / "state"
            shutil.copytree(FIXTURE, workspace)
            self._run(
                "prepare", "--workspace", str(workspace), "--route", "route-nets",
                "--task-id", "harness-generated", "--project", "project.aixproj.json", "--state-dir", str(state),
            )
            svg = workspace / "render/drawing.svg"
            svg.write_text(svg.read_text(encoding="utf-8") + "<!-- hand edit -->\n", encoding="utf-8")
            checked = self._run("check", "--state-dir", str(state), expected=2)
            self.assertFalse(checked["valid"])
            codes = {item["code"] for item in checked["diagnostics"]}
            self.assertIn("AIXEM-DIAG-AGENT-GENERATED-OUTPUT-EDIT", codes)

    def test_wrong_authority_edit_blocks_route(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; state = root / "state"
            shutil.copytree(FIXTURE, workspace)
            self._run(
                "prepare", "--workspace", str(workspace), "--route", "route-nets",
                "--task-id", "harness-scope", "--project", "project.aixproj.json", "--state-dir", str(state),
            )
            source = workspace / "two_pin_passive.aixem"
            source.write_text(source.read_text(encoding="utf-8") + "\n# unauthorized semantic edit\n", encoding="utf-8")
            checked = self._run("check", "--state-dir", str(state), expected=2)
            self.assertIn("AIXEM-DIAG-AGENT-SCOPE-VIOLATION", {item["code"] for item in checked["diagnostics"]})


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "validation/agent-evals-2"
RUNNER = ROOT / "tools/run_agent_evals_2.py"


class AgentEvaluation2Tests(unittest.TestCase):
    def test_manifest_contains_exact_a001_a012_inventory(self) -> None:
        manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([f"A{i:03d}" for i in range(1, 13)], [item["id"] for item in manifest["cases"]])
        for item in manifest["cases"]:
            task = ROOT / item["task"]
            self.assertTrue(task.is_file())
            case = json.loads(task.read_text(encoding="utf-8"))
            self.assertEqual(item["id"], case["id"])
            self.assertEqual("deterministic-harness-replay", case["tierA"]["mode"])
            self.assertFalse(case["tierB"]["eligible"])

    def test_tier_a_results_are_complete_and_pass(self) -> None:
        result = json.loads((CORPUS / "results/tier-a-results.json").read_text(encoding="utf-8"))
        self.assertTrue(result["valid"])
        self.assertEqual({"cases": 12, "failed": 0, "passed": 12}, result["summary"])
        self.assertFalse(result["liveExternalAgentExecuted"])
        for case in result["cases"]:
            self.assertEqual("pass", case["status"])
            self.assertTrue(all(case["passConditions"].values()))
            self.assertTrue((CORPUS / "results" / case["retainedRunRecord"]).is_file())

    def test_tier_status_never_conflates_replay_and_live_execution(self) -> None:
        tier_a = json.loads((CORPUS / "results/tier-a-results.json").read_text(encoding="utf-8"))
        tier_b = json.loads((CORPUS / "results/tier-b-status.json").read_text(encoding="utf-8"))
        self.assertEqual("deterministic-harness-replay", tier_a["executionMode"])
        self.assertFalse(tier_a["liveExternalAgentExecuted"])
        self.assertEqual("live-external-agent", tier_b["executionMode"])
        self.assertFalse(tier_b["executed"])
        self.assertFalse(tier_b["liveExternalAgentExecuted"])
        self.assertIn("No live external agent execution", tier_b["claim"])

    def test_runner_rejects_live_mode_without_separate_cold_start_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                ["python", str(RUNNER), "--results", td, "--tier-b-command", "fake-agent"],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
        self.assertEqual(2, proc.returncode)
        self.assertIn("cold-start corpus", proc.stderr)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import canonical_json_bytes  # noqa: E402
from agent.live_run import LiveRunError, build_attempt_set, build_live_run_evidence, validate_live_run  # noqa: E402

SCHEMA = ROOT / "docs/specifications/schemas/agent/aixem-agent-live-run-1.schema.json"


def digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_bytes(canonical_json_bytes(value))


class LiveRunEvidenceContractTests(unittest.TestCase):
    def _files(self, root: Path, *, evaluation_passed: bool, conformant: bool) -> dict[str, Path]:
        task = root / "agent-task.json"
        stage = root / "stage-manifest.json"
        executor = root / "executor.json"
        observation = root / "observation-log.jsonl"
        evaluation = root / "evaluator-result.json"
        record = root / "authoring-run-record.json"
        write_json(task, {"id": "L999"})
        write_json(stage, {"attemptId": "L999-attempt-01", "stageDigest": digest("stage")})
        write_json(executor, {
            "id": "external-reference", "agentClass": "external-ai",
            "identity": {"provider": "Provider", "model": "Model", "tool": "Tool", "toolVersion": "1", "configLabel": "test"},
        })
        observation.write_text('{"sequence":1,"kind":"task-open"}\n', encoding="utf-8")
        write_json(evaluation, {"passed": evaluation_passed, "summary": {"required": 1}, "resultDigest": digest("evaluation")})
        write_json(record, {"final": {"conformant": conformant}, "recordDigest": digest("record")})
        return {"task": task, "stage": stage, "executor": executor, "observation": observation, "evaluation": evaluation, "record": record}

    def test_live_pass_requires_evaluation_and_conformant_authoring_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            files = self._files(Path(td), evaluation_passed=True, conformant=True)
            execution = {
                "status": "COMPLETED", "processStarted": True, "liveExternalAgentExecuted": True,
                "observation": {"valid": True, "events": 1, "coverage": {}},
            }
            evidence = build_live_run_evidence(
                release="AIXEM-SRP-0.5.6-2026-08-12", generated_at="2026-08-12T00:00:00Z",
                task_path=files["task"], stage_manifest_path=files["stage"],
                executor_descriptor_path=files["executor"], observation_log_path=files["observation"],
                execution=execution, evaluation_path=files["evaluation"], run_record_path=files["record"],
                stage_validation={"valid": True},
            )
        self.assertEqual("PASS", evidence["terminalStatus"])
        self.assertTrue(evidence["liveExternalAgentExecuted"])
        self.assertTrue(evidence["claimEligible"])
        self.assertTrue(validate_live_run(evidence, SCHEMA)["valid"])

    def test_failed_or_non_live_attempt_remains_in_denominator(self) -> None:
        descriptor = {"id": "external-reference", "agentClass": "external-ai", "identity": {"provider": "P", "model": "M"}}
        attempts = [
            {"caseId": "L001", "attemptId": "L001-01", "terminalStatus": "PASS", "liveExternalAgentExecuted": True, "evidenceDigest": digest("1")},
            {"caseId": "L002", "attemptId": "L002-01", "terminalStatus": "FAIL", "liveExternalAgentExecuted": True, "evidenceDigest": digest("2")},
            {"caseId": "L003", "attemptId": "L003-01", "terminalStatus": "EXECUTOR_ERROR", "liveExternalAgentExecuted": False, "evidenceDigest": digest("3")},
        ]
        result = build_attempt_set(
            release="AIXEM-SRP-0.5.6-2026-08-12", executor_descriptor=descriptor,
            attempts=attempts, expected_attempt_ids=["L001-01", "L002-01", "L003-01"],
        )
        self.assertTrue(result["denominatorIntegrity"])
        self.assertEqual(3, result["summary"]["attempts"])
        self.assertEqual(1, result["summary"]["passed"])
        self.assertEqual(1, result["summary"]["failed"])
        self.assertEqual(1, result["summary"]["executorErrors"])
        self.assertIn("1 of 3 retained", result["claim"])

    def test_cherry_picked_or_duplicate_attempt_set_fails_closed(self) -> None:
        descriptor = {"id": "x", "agentClass": "external-ai"}
        one = {"caseId": "L001", "attemptId": "L001-01", "terminalStatus": "PASS", "liveExternalAgentExecuted": True, "evidenceDigest": digest("x")}
        with self.assertRaisesRegex(LiveRunError, "denominator integrity"):
            build_attempt_set(release="x", executor_descriptor=descriptor, attempts=[one], expected_attempt_ids=["L001-01", "L002-01"])
        with self.assertRaises(LiveRunError):
            build_attempt_set(release="x", executor_descriptor=descriptor, attempts=[one, one], expected_attempt_ids=["L001-01"])

    def test_evidence_digest_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            files = self._files(Path(td), evaluation_passed=False, conformant=False)
            evidence = build_live_run_evidence(
                release="x", generated_at="2026-08-12T00:00:00Z",
                task_path=files["task"], stage_manifest_path=files["stage"], executor_descriptor_path=files["executor"],
                observation_log_path=files["observation"], execution={"status": "FAILED", "processStarted": True, "liveExternalAgentExecuted": False, "observation": {"valid": True, "events": 1, "coverage": {}}},
                evaluation_path=files["evaluation"], run_record_path=files["record"], stage_validation={"valid": True},
            )
        evidence["terminalStatus"] = "PASS"
        self.assertFalse(validate_live_run(evidence, SCHEMA)["valid"])


if __name__ == "__main__":
    unittest.main()

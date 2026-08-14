from __future__ import annotations

import hashlib
import json
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.cold_start_stage import build_stage  # noqa: E402
from agent.live_executor import LiveExecutorError, execute_subprocess, validate_executor_descriptor  # noqa: E402

SCHEMAS = ROOT / "docs/specifications/schemas/agent"
EXECUTOR_SCHEMA = SCHEMAS / "aixem-agent-executor-1.schema.json"
OBSERVATION_SCHEMA = SCHEMAS / "aixem-agent-observation-event-1.schema.json"
FIXTURE = ROOT / "tests/fixtures/agents/observable_fixture_agent.py"


def digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def descriptor(command: list[str], *, agent_class: str = "test-fixture", event_limit: int = 1000, wall_time: int = 120, output_bytes: int = 1048576) -> dict:
    return {
        "schema": "https://schemas.aixem.org/agent/executor/1",
        "formatVersion": "1.0",
        "id": "observable-fixture",
        "adapterVersion": "1.0",
        "agentClass": agent_class,
        "command": command,
        "workingDirectoryPolicy": "stage-root",
        "inputMode": "task-path-argument",
        "observationCapability": {"fileReads": False, "searches": False, "commands": True, "writes": False, "routeActions": True},
        "networkPolicy": {"mode": "deny", "enforcement": "descriptor-only"},
        "limits": {"wallTimeSeconds": wall_time, "outputBytes": output_bytes, "observationEvents": event_limit},
        "identity": {"provider": "AIXEM", "model": "none", "tool": "observable-fixture", "toolVersion": "1.0", "configLabel": "tier-a-only"},
        "redactedConfigurationDigest": digest("fixture-config-v1"),
    }


class LiveExecutorProtocolTests(unittest.TestCase):
    def _stage(self, root: Path, name: str = "stage") -> Path:
        stage = root / name
        build_stage(ROOT, ROOT / "validation/agent-evals-3/cases/L008", "L008-executor-01", stage)
        return stage

    def test_missing_executable_is_retained_as_executor_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stage = self._stage(Path(td))
            result = execute_subprocess(
                descriptor(["definitely-not-an-aixem-agent", "--task", "{task}"]),
                stage,
                executor_schema_file=EXECUTOR_SCHEMA,
                observation_schema_file=OBSERVATION_SCHEMA,
            )
        self.assertEqual("EXECUTOR_ERROR", result["status"])
        self.assertFalse(result["processStarted"])
        self.assertFalse(result["liveExternalAgentExecuted"])

    def test_non_ai_protocol_fixture_proves_execution_but_never_a_live_ai_claim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stage = self._stage(Path(td))
            command = [sys.executable, str(FIXTURE), "--task", "{task}", "--workspace", "{workspace}", "--reference", "{reference}", "--state", "{state}", "--observation-log", "{observationLog}"]
            result = execute_subprocess(
                descriptor(command), stage,
                executor_schema_file=EXECUTOR_SCHEMA,
                observation_schema_file=OBSERVATION_SCHEMA,
            )
        self.assertTrue(result["processStarted"])
        self.assertTrue(result["observation"]["valid"], result["observation"]["errors"])
        self.assertTrue(result["executionProof"]["taskOpenObserved"])
        self.assertTrue(result["executionProof"]["observableActionObserved"])
        self.assertFalse(result["liveExternalAgentExecuted"])
        self.assertFalse(result["secretRedactionApplied"])
        self.assertIn("sha256:", result["stdout"])

    def test_observation_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            stage = self._stage(temp)
            writer = temp / "writer.py"
            writer.write_text(
                """import json, os\nfrom pathlib import Path\np=Path(os.environ['AIXEM_OBSERVATION_LOG'])\ne=[]\nfor i,k in enumerate(['task-open','command'],1):\n e.append({'schema':'https://schemas.aixem.org/agent/observation-event/1','formatVersion':'1.0','sequence':i,'kind':k})\np.write_text(''.join(json.dumps(x,separators=(',',':'))+'\\n' for x in e),encoding='utf-8')\n""",
                encoding="utf-8",
            )
            result = execute_subprocess(
                descriptor([sys.executable, str(writer)], event_limit=1), stage,
                executor_schema_file=EXECUTOR_SCHEMA,
                observation_schema_file=OBSERVATION_SCHEMA,
            )
        self.assertFalse(result["observation"]["valid"])
        self.assertIn("event limit exceeded", " ".join(result["observation"]["errors"]))
        self.assertFalse(result["liveExternalAgentExecuted"])

    def test_inherited_secret_value_is_redacted_without_serializing_it(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            stage = self._stage(temp)
            writer = temp / "secret_writer.py"
            writer.write_text(
                """import json, os\nfrom pathlib import Path\np=Path(os.environ['AIXEM_OBSERVATION_LOG'])\ne=[{'schema':'https://schemas.aixem.org/agent/observation-event/1','formatVersion':'1.0','sequence':1,'kind':'task-open'}]\np.write_text(json.dumps(e[0])+'\\n',encoding='utf-8')\nprint(os.environ['AIXEM_TEST_API_KEY'])\n""",
                encoding="utf-8",
            )
            value = descriptor([sys.executable, str(writer)])
            value["inheritEnvironment"] = ["AIXEM_TEST_API_KEY"]
            secret = "sk-live-super-secret-1234567890"
            with patch.dict(os.environ, {"AIXEM_TEST_API_KEY": secret}):
                result = execute_subprocess(
                    value, stage, executor_schema_file=EXECUTOR_SCHEMA, observation_schema_file=OBSERVATION_SCHEMA,
                )
        self.assertNotIn(secret, json.dumps(result))
        self.assertIn("[REDACTED]", result["stdout"])
        self.assertTrue(result["secretRedactionApplied"])
        self.assertEqual(["AIXEM_TEST_API_KEY"], result["inheritedEnvironmentNames"])

    def test_wall_time_and_output_limits_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            stage = self._stage(temp, "timeout-stage")
            timeout_result = execute_subprocess(
                descriptor([sys.executable, "-c", "import time; time.sleep(2)"], wall_time=1),
                stage, executor_schema_file=EXECUTOR_SCHEMA, observation_schema_file=OBSERVATION_SCHEMA,
            )
            stage = self._stage(temp, "output-stage")
            output_result = execute_subprocess(
                descriptor([sys.executable, "-c", "print('x'*4096)"], output_bytes=1024),
                stage, executor_schema_file=EXECUTOR_SCHEMA, observation_schema_file=OBSERVATION_SCHEMA,
            )
        self.assertEqual("TIMEOUT", timeout_result["status"])
        self.assertTrue(timeout_result["timedOut"])
        self.assertTrue(output_result["outputTruncated"])
        self.assertLessEqual(len(output_result["stdout"].encode("utf-8")), 1024)

    def test_descriptor_rejects_serialized_credentials(self) -> None:
        value = descriptor([sys.executable, "-c", "pass"])
        value["environment"] = {"API_KEY": "sk-test-secret-1234567890"}
        with self.assertRaises(LiveExecutorError):
            validate_executor_descriptor(value, EXECUTOR_SCHEMA)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.cold_start_stage import build_stage, capture_immutable_stage, verify_immutable_stage  # noqa: E402
from agent.invariant_scorer import audit_invariant_basis  # noqa: E402
from agent.live_executor import execute_subprocess  # noqa: E402
from agent.observation import read_events, reconcile_observation_writes, sanitize_observation_log  # noqa: E402
from tools import run_agent_evals_3 as readiness  # noqa: E402

SCHEMAS = ROOT / "docs/specifications/schemas/agent"
CASE = ROOT / "validation/agent-evals-3/cases/L008"
REPORT = ROOT / "validation/agent-evals-3/results/readiness/readiness-report.json"


class PreLiveReadinessHardeningTests(unittest.TestCase):
    def _stage(self, root: Path, name: str) -> Path:
        stage = root / name
        build_stage(ROOT, CASE, f"{name}-attempt", stage)
        return stage

    def test_results_and_work_roots_are_location_independent_and_space_safe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem results with spaces ") as rd, tempfile.TemporaryDirectory(prefix="aixem work with spaces ") as wd:
            results = readiness.prepare_output_root(Path(rd), "results")
            work = readiness.prepare_output_root(Path(wd), "work")
            retained = results / "nested/live-run-evidence.json"
            retained.parent.mkdir(parents=True)
            retained.write_text("{}\n", encoding="utf-8")
            self.assertEqual("nested/live-run-evidence.json", readiness.safe_relative(retained, results))
            self.assertTrue(work.is_dir())

    def test_repository_corpus_protocol_identity_and_clock_modes_are_separate(self) -> None:
        identity = readiness.corpus_identity()
        self.assertEqual("agent-evals-3", identity["id"])
        self.assertEqual("1.1", identity["revision"])
        self.assertNotEqual(readiness.repository_release(), identity["baselineRelease"])
        actual = readiness.utc_now()
        self.assertRegex(actual, r"^20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertNotEqual(readiness.FIXED_TIME, actual)

    def test_task_reference_manifest_and_symlink_tampering_fail_postflight(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stage = self._stage(root, "task")
            baseline = capture_immutable_stage(stage)
            task = stage / "task/agent-task.json"
            task.write_text(task.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertFalse(verify_immutable_stage(stage, baseline)["valid"])

            stage = self._stage(root, "reference")
            baseline = capture_immutable_stage(stage)
            ref = next(path for path in (stage / "reference").rglob("*.md") if path.is_file())
            ref.write_text(ref.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertFalse(verify_immutable_stage(stage, baseline)["valid"])

            stage = self._stage(root, "manifest")
            baseline = capture_immutable_stage(stage)
            manifest = stage / "stage-manifest.json"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertFalse(verify_immutable_stage(stage, baseline)["valid"])

            if hasattr(os, "symlink"):
                stage = self._stage(root, "symlink")
                baseline = capture_immutable_stage(stage)
                os.symlink(stage / "task/TASK.md", stage / "reference/executor-added-link")
                result = verify_immutable_stage(stage, baseline)
                self.assertFalse(result["valid"])
                self.assertIn("symlink", " ".join(result["errors"]).lower())

    @unittest.skipUnless(os.name == "posix", "process-group lifecycle proof is POSIX-specific")
    def test_timeout_terminates_spawned_child_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stage = self._stage(root, "timeout")
            canary = root / "child-survived.txt"
            descriptor = readiness.readiness_descriptor(
                "timeout-after-mutation", descriptor_id="timeout-child-test", writes=True,
                wall_time=1, child_canary=canary,
            )
            result = execute_subprocess(
                descriptor, stage,
                executor_schema_file=SCHEMAS / "aixem-agent-executor-1.schema.json",
                observation_schema_file=SCHEMAS / "aixem-agent-observation-event-1.schema.json",
            )
            time.sleep(2.2)
            self.assertEqual("TIMEOUT", result["status"])
            self.assertTrue(result["processLifecycle"]["groupTerminationSupported"])
            self.assertFalse(canary.exists())

    def test_nested_observation_secrets_are_sanitized_before_retention(self) -> None:
        secret = "sk-readiness-secret-1234567890"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "observation.jsonl"
            path.write_text(json.dumps({
                "schema": "https://schemas.aixem.org/agent/observation-event/1",
                "formatVersion": "1.0", "sequence": 1, "kind": "completion",
                "result": f"bearer {secret}", "details": {"nested": {"token": secret}},
            }) + "\n", encoding="utf-8")
            result = sanitize_observation_log(path, [secret])
            retained = path.read_text(encoding="utf-8")
            events = read_events(path)
        self.assertTrue(result["valid"])
        self.assertTrue(result["redactionApplied"])
        self.assertNotIn(secret, retained)
        self.assertEqual("[REDACTED]", events[0]["details"]["nested"]["token"])

    def test_observation_consistency_preserves_change_set_authority(self) -> None:
        record = {"iterations": [{"changeSet": {"changed": [{"path": "workspace/a.txt"}]}}]}
        matching = [{"kind": "file-write", "target": "workspace/a.txt"}]
        missing = []
        extra = [{"kind": "file-write", "target": "workspace/b.txt"}]
        self.assertTrue(reconcile_observation_writes(matching, record, writes_declared=True)["consistent"])
        self.assertEqual(["a.txt"], reconcile_observation_writes(missing, record, writes_declared=True)["missingObservedWrites"])
        self.assertEqual(["b.txt"], reconcile_observation_writes(extra, record, writes_declared=True)["unmatchedObservedWrites"])
        unavailable = reconcile_observation_writes(missing, record, writes_declared=False)
        self.assertEqual("UNAVAILABLE", unavailable["status"])
        self.assertEqual("change-set", unavailable["authority"])

    def test_invariant_basis_rejects_missing_task_and_nonstaged_document(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stage = self._stage(Path(td), "fairness")
            task = json.loads((stage / "task/agent-task.json").read_text(encoding="utf-8"))
            manifest = json.loads((CASE / "evaluator/invariants.json").read_text(encoding="utf-8"))
            valid = audit_invariant_basis(task, manifest, reference_root=stage / "reference", schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json")
            self.assertTrue(valid["valid"])

            missing_task = deepcopy(manifest)
            missing_task["invariants"][0]["basis"] = [{"type": "task", "pointer": "/missing"}]
            result = audit_invariant_basis(task, missing_task, reference_root=stage / "reference", schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json")
            self.assertFalse(result["valid"])

            missing_doc = deepcopy(manifest)
            missing_doc["invariants"][0]["basis"] = [{"type": "document", "documentId": "AIXEM-NOT-STAGED-001", "requirementId": "AIXEM-REQ-NOT-STAGED-001"}]
            result = audit_invariant_basis(task, missing_doc, reference_root=stage / "reference", schema_file=SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json")
            self.assertFalse(result["valid"])

    def test_generated_readiness_report_closes_all_pre_live_gates(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["preLiveReadiness"])
        self.assertEqual({"fixtures": 4, "passed": 4, "failed": 0}, report["subprocessSuccessMatrix"]["summary"])
        self.assertEqual({"faults": 10, "passed": 10, "failed": 0}, report["subprocessFaultMatrix"]["summary"])
        routes = [item["route"] for item in report["routeReadiness"]["routes"]]
        self.assertEqual(len(routes), len(set(routes)))
        self.assertEqual(set(readiness.AUTHORING_ROUTES), set(routes))
        self.assertFalse(report["referencePackClosure"]["sourceRepositoryPythonPathUsed"])
        self.assertFalse(report["externalTierBExecuted"])
        self.assertFalse(report["liveExternalAgentExecuted"])
        self.assertFalse(report["liveClaimAuthorized"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.validator_adapter import validate_workspace  # noqa: E402

CORPUS = ROOT / "validation/agent-evals-3"
SCHEMAS = ROOT / "docs/specifications/schemas/agent"


class AgentEvaluation3CorpusTests(unittest.TestCase):
    def test_manifest_contains_exact_l001_l012_creation_and_repair_inventory(self) -> None:
        manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([f"L{i:03d}" for i in range(1, 13)], [item["id"] for item in manifest["cases"]])
        self.assertEqual(7, sum(item["category"] == "creation" for item in manifest["cases"]))
        self.assertEqual(5, sum(item["category"] == "repair" for item in manifest["cases"]))
        self.assertFalse(manifest["liveExternalAgentExecuted"])
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        current_release = f"AIXEM-SRP-{version}-2026-08-12"
        self.assertEqual(current_release, manifest["release"])
        self.assertEqual(current_release, manifest["repositoryRelease"])
        self.assertEqual("AIXEM-SRP-0.5.8.1-2026-08-12", manifest["baselineRelease"])

    def test_tasks_and_evaluator_manifests_are_schema_valid_and_separated(self) -> None:
        task_validator = Draft202012Validator(json.loads((SCHEMAS / "aixem-agent-task-1.schema.json").read_text(encoding="utf-8")))
        invariant_validator = Draft202012Validator(json.loads((SCHEMAS / "aixem-agent-evaluation-invariant-1.schema.json").read_text(encoding="utf-8")))
        for case in sorted((CORPUS / "cases").glob("L[0-9][0-9][0-9]")):
            with self.subTest(case=case.name):
                task = json.loads((case / "agent-task.json").read_text(encoding="utf-8"))
                invariants = json.loads((case / "evaluator/invariants.json").read_text(encoding="utf-8"))
                metadata = json.loads((case / "case.json").read_text(encoding="utf-8"))
                task_validator.validate(task)
                invariant_validator.validate(invariants)
                self.assertFalse(metadata["completedTargetBundled"])
                self.assertFalse((case / "start/evaluator").exists())
                self.assertFalse(any(path.name == "invariants.json" for path in (case / "start").rglob("*")))
                self.assertFalse((case / "start/render").exists())
                self.assertFalse((case / "start/evidence").exists())

    def test_declared_initial_diagnostics_match_the_actual_incomplete_start_state(self) -> None:
        for case in sorted((CORPUS / "cases").glob("L[0-9][0-9][0-9]")):
            with self.subTest(case=case.name):
                task = json.loads((case / "agent-task.json").read_text(encoding="utf-8"))
                metadata = json.loads((case / "case.json").read_text(encoding="utf-8"))
                result = validate_workspace(case / "start", task["activeRoute"], project=Path(task["project"]))
                observed = {item["code"] for item in result["diagnostics"] if item.get("severity") == "error"}
                self.assertTrue(set(metadata["expectedInitialDiagnostics"]).issubset(observed))
                if metadata["expectedInitialDiagnostics"]:
                    self.assertFalse(result["valid"])

    def test_corpus_builder_is_byte_reproducible(self) -> None:
        before = subprocess.run(
            [sys.executable, str(ROOT / "tools/build_agent_evals_3.py")], cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, before.returncode, before.stderr)
        first = (CORPUS / "manifest.json").read_bytes()
        after = subprocess.run(
            [sys.executable, str(ROOT / "tools/build_agent_evals_3.py")], cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, after.returncode, after.stderr)
        self.assertEqual(first, (CORPUS / "manifest.json").read_bytes())

    def test_corpus_readme_links_every_registered_task(self) -> None:
        manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
        readme = (CORPUS / "README.md").read_text(encoding="utf-8")
        for item in manifest["cases"]:
            with self.subTest(case=item["id"]):
                self.assertIn(f"(cases/{item['id']}/TASK.md)", readme)

    def test_tier_b_status_never_claims_an_execution_that_did_not_happen(self) -> None:
        path = CORPUS / "results/tier-b-status.json"
        self.assertTrue(path.is_file())
        result = json.loads(path.read_text(encoding="utf-8"))
        if not result["executed"]:
            self.assertFalse(result["liveExternalAgentExecuted"])
            self.assertFalse(result["claimAuthorized"])
            self.assertEqual(0, result["attempts"])


if __name__ == "__main__":
    unittest.main()

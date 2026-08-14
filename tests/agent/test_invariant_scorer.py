from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.cold_start_stage import build_stage  # noqa: E402
from agent.invariant_scorer import InvariantError, score_invariants, validate_invariant_manifest  # noqa: E402
from tools.build_agent_evals_3 import refresh_locks  # noqa: E402

SCHEMA = ROOT / "docs/specifications/schemas/agent/aixem-agent-evaluation-invariant-1.schema.json"
CASE = ROOT / "validation/agent-evals-3/cases/L008"


class EvaluationInvariantContractTests(unittest.TestCase):
    def test_exact_completed_source_oracle_is_prohibited(self) -> None:
        manifest = json.loads((CASE / "evaluator/invariants.json").read_text(encoding="utf-8"))
        invalid = deepcopy(manifest)
        invalid["invariants"][0]["arguments"]["exactSource"] = "completed answer"
        with self.assertRaisesRegex(InvariantError, "hidden exact-source equality"):
            validate_invariant_manifest(invalid, SCHEMA)

    def test_scorer_checks_actual_incomplete_workspace_without_self_repair(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stage = Path(td) / "stage"
            stage_manifest = build_stage(ROOT, CASE, "L008-score-incomplete", stage)
            before = (stage / "workspace/library/electronics/authoring/repaired-resistor.aixsym.json").read_bytes()
            result = score_invariants(
                stage / "workspace",
                json.loads((CASE / "evaluator/invariants.json").read_text(encoding="utf-8")),
                stage_manifest,
                schema_file=SCHEMA,
            )
            after = (stage / "workspace/library/electronics/authoring/repaired-resistor.aixsym.json").read_bytes()
        self.assertFalse(result["passed"])
        self.assertEqual(before, after)
        self.assertTrue(result["authoritativeWorkspaceUnchangedByEvaluator"])
        self.assertIn("L008-VALID", {item["id"] for item in result["results"] if not item["passed"]})

    def test_semantically_repaired_workspace_passes_hidden_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stage = Path(td) / "stage"
            stage_manifest = build_stage(ROOT, CASE, "L008-score-repaired", stage)
            shutil.copy2(
                ROOT / "examples/authoring/08-visual-repair/library/electronics/authoring/repaired-resistor.aixsym.json",
                stage / "workspace/library/electronics/authoring/repaired-resistor.aixsym.json",
            )
            refresh_locks(stage / "workspace")
            result = score_invariants(
                stage / "workspace",
                json.loads((CASE / "evaluator/invariants.json").read_text(encoding="utf-8")),
                stage_manifest,
                schema_file=SCHEMA,
            )
        self.assertTrue(result["passed"], result["results"])
        self.assertEqual(4, result["summary"]["passedRequired"])
        self.assertTrue(result["authoritativeWorkspaceUnchangedByEvaluator"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.cold_start_stage import StageContractError, build_stage, validate_stage  # noqa: E402


class ColdStartStageContractTests(unittest.TestCase):
    def test_all_l001_l012_stages_are_deterministic_valid_and_oracle_free(self) -> None:
        cases = sorted((ROOT / "validation/agent-evals-3/cases").glob("L[0-9][0-9][0-9]"))
        self.assertEqual(12, len(cases))
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            for case in cases:
                with self.subTest(case=case.name):
                    first = temp / f"{case.name}-a"
                    second = temp / f"{case.name}-b"
                    attempt_id = f"{case.name}-determinism-01"
                    manifest_a = build_stage(ROOT, case, attempt_id, first)
                    manifest_b = build_stage(ROOT, case, attempt_id, second)
                    self.assertEqual(manifest_a["stageDigest"], manifest_b["stageDigest"])
                    self.assertEqual(manifest_a["referencePack"]["digest"], manifest_b["referencePack"]["digest"])
                    self.assertEqual(manifest_a["startWorkspace"]["snapshotDigest"], manifest_b["startWorkspace"]["snapshotDigest"])
                    self.assertTrue(validate_stage(first, ROOT)["valid"])
                    visible = [item["path"].lower() for item in manifest_a["visibleFiles"]]
                    self.assertFalse(any("evaluator/" in path or path.endswith("invariants.json") for path in visible))
                    self.assertFalse((first / "validation").exists())
                    self.assertEqual([], list((first / "state").iterdir()))
                    self.assertTrue(manifest_a["targetLeakageCheck"]["valid"])

    def test_fresh_attempt_destination_must_be_empty(self) -> None:
        case = ROOT / "validation/agent-evals-3/cases/L008"
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "stage"
            output.mkdir()
            (output / "unexpected.txt").write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(StageContractError, "not empty"):
                build_stage(ROOT, case, "L008-occupied", output)

    def test_symlinks_in_start_state_fail_closed(self) -> None:
        source_case = ROOT / "validation/agent-evals-3/cases/L008"
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            case = temp / "case"
            shutil.copytree(source_case, case)
            target = case / "start" / "target.txt"
            target.write_text("x", encoding="utf-8")
            (case / "start" / "unsafe-link").symlink_to(target)
            with self.assertRaisesRegex(StageContractError, "symlink is prohibited"):
                build_stage(ROOT, case, "L008-symlink", temp / "stage")


if __name__ == "__main__":
    unittest.main()

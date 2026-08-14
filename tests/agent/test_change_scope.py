from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.change_scope import (  # noqa: E402
    UnsafeWorkspaceError,
    build_change_set,
    snapshot_workspace,
)


ROUTE_SCOPE = {
    "authority": ["layout", "project"],
    "artifacts": ["**/*.aixlayout.json", "**/*.aixproj.json"],
    "derived": ["render/**", "evidence/**"],
    "prohibited": ["render/**", "evidence/**", "**/*.svg", "**/viewer.html"],
    "constraints": [{"pattern": "**/*.aixproj.json", "policy": "digest-only"}],
}


class AgentChangeScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        schema_path = ROOT / "docs/specifications/schemas/agent/aixem-agent-change-set-1.schema.json"
        self.validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))

    def _base(self, root: Path) -> None:
        (root / "sheet.aixlayout.json").write_text('{"schema":"x","layout":{"connections":[]}}\n', encoding="utf-8")
        (root / "project.aixproj.json").write_text(
            '{"schema":"x","project":{"source":{"digest":"sha256:' + '0' * 64 + '"}}}\n', encoding="utf-8"
        )
        (root / "sheet.aixem").write_text("project: t\n", encoding="utf-8")
        (root / "render").mkdir()
        (root / "render/drawing.svg").write_text("<svg/>\n", encoding="utf-8")

    def test_allowed_layout_and_digest_only_project_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self._base(root)
            before = snapshot_workspace(root)
            (root / "sheet.aixlayout.json").write_text('{"schema":"x","layout":{"connections":[1]}}\n', encoding="utf-8")
            project = json.loads((root / "project.aixproj.json").read_text())
            project["project"]["source"]["digest"] = "sha256:" + "1" * 64
            (root / "project.aixproj.json").write_text(json.dumps(project) + "\n", encoding="utf-8")
            after = snapshot_workspace(root)
            change_set = build_change_set(before, after, route="route-nets", scope=ROUTE_SCOPE, iteration=1)
            self.validator.validate(change_set)
            self.assertTrue(change_set["valid"])
            self.assertEqual(2, len(change_set["changed"]))
            self.assertEqual([], change_set["scopeViolations"])
            project_change = next(item for item in change_set["changed"] if item["path"].endswith(".aixproj.json"))
            self.assertEqual(["/project/source/digest"], project_change["changedPointers"])

    def test_wrong_authority_and_non_digest_project_change_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self._base(root)
            before = snapshot_workspace(root)
            (root / "sheet.aixem").write_text("project: changed\n", encoding="utf-8")
            project = json.loads((root / "project.aixproj.json").read_text())
            project["project"]["title"] = "not a digest-only update"
            (root / "project.aixproj.json").write_text(json.dumps(project) + "\n", encoding="utf-8")
            after = snapshot_workspace(root)
            change_set = build_change_set(before, after, route="route-nets", scope=ROUTE_SCOPE, iteration=1)
            self.validator.validate(change_set)
            self.assertFalse(change_set["valid"])
            kinds = {item["kind"] for item in change_set["scopeViolations"]}
            self.assertIn("authority-scope", kinds)
            self.assertIn("write-constraint", kinds)

    def test_generated_output_edit_is_detected_and_schema_valid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self._base(root)
            before = snapshot_workspace(root)
            (root / "render/drawing.svg").write_text("<svg><path/></svg>\n", encoding="utf-8")
            after = snapshot_workspace(root)
            change_set = build_change_set(before, after, route="route-nets", scope=ROUTE_SCOPE, iteration=1)
            self.validator.validate(change_set)
            self.assertFalse(change_set["valid"])
            self.assertEqual(["render/drawing.svg"], [item["path"] for item in change_set["generatedOutputEdits"]])
            self.assertEqual("generated-output-edit", change_set["scopeViolations"][0]["kind"])


    def test_new_library_artifact_must_use_canonical_path(self) -> None:
        scope = {
            "authority": ["component-library", "symbol"],
            "artifacts": ["**/*.aixlib.json", "**/*.aixsym.json"],
            "derived": [],
            "prohibited": [],
            "constraints": [
                {"pattern": "**/*.aixlib.json", "policy": "new-library-artifact-canonical"},
                {"pattern": "**/*.aixsym.json", "policy": "new-library-artifact-canonical"},
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before = snapshot_workspace(root)
            valid = root / "library/electronics/passive/resistor"
            valid.mkdir(parents=True)
            (valid / "resistors.aixlib.json").write_text('{"library":{}}\n', encoding="utf-8")
            (valid / "resistor-iec.aixsym.json").write_text('{"symbol":{}}\n', encoding="utf-8")
            after = snapshot_workspace(root)
            change_set = build_change_set(before, after, route="create-symbol", scope=scope, iteration=1)
            self.assertTrue(change_set["valid"], change_set["scopeViolations"])

    def test_new_legacy_library_root_fails_but_existing_repair_passes(self) -> None:
        scope = {
            "authority": ["component-library", "symbol"],
            "artifacts": ["**/*.aixlib.json", "**/*.aixsym.json"],
            "derived": [],
            "prohibited": [],
            "constraints": [
                {"pattern": "**/*.aixlib.json", "policy": "new-library-artifact-canonical"},
                {"pattern": "**/*.aixsym.json", "policy": "new-library-artifact-canonical"},
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "libraries").mkdir()
            legacy = root / "libraries/existing.aixlib.json"
            legacy.write_text('{"library":{"version":1}}\n', encoding="utf-8")
            before = snapshot_workspace(root)
            legacy.write_text('{"library":{"version":2}}\n', encoding="utf-8")
            after = snapshot_workspace(root)
            repair = build_change_set(before, after, route="create-symbol", scope=scope, iteration=1)
            self.assertTrue(repair["valid"], repair["scopeViolations"])

            before = after
            (root / "libraries/new-part.aixlib.json").write_text('{"library":{}}\n', encoding="utf-8")
            after = snapshot_workspace(root)
            creation = build_change_set(before, after, route="create-symbol", scope=scope, iteration=2)
            self.assertFalse(creation["valid"])
            self.assertIn("AIXEM-DIAG-LIBRARY-PATH-NONCANONICAL", creation["scopeViolations"][0]["message"])

    def test_symlink_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target"; target.write_text("x", encoding="utf-8")
            (root / "link").symlink_to(target)
            with self.assertRaises(UnsafeWorkspaceError):
                snapshot_workspace(root)


if __name__ == "__main__":
    unittest.main()

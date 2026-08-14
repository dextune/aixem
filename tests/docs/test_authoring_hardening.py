"""AIXEM 0.5.9 task-guide, path, and retrieval-chain conformance tests."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GUIDES = ROOT / "docs" / "authoring" / "guides"
GUIDE_NAMES = (
    "create-library-part.md",
    "select-library-part.md",
    "create-schematic.md",
    "place-components.md",
    "route-nets.md",
    "compose-project.md",
    "modify-existing-schematic.md",
    "author-component-circuit.md",
    "render-review.md",
    "validate-project.md",
)
REQUIRED_SECTIONS = tuple(f"## {index}." for index in range(1, 16))
CANONICAL_ROOT = "library/electronics"


class AuthoringHardeningDocumentationTests(unittest.TestCase):
    def test_guide_inventory_and_size_budget(self) -> None:
        observed = sorted(path.name for path in GUIDES.glob("*.md") if path.name != "index.md")
        self.assertEqual(observed, sorted(GUIDE_NAMES))
        for name in GUIDE_NAMES:
            path = GUIDES / name
            self.assertLessEqual(path.stat().st_size, 12 * 1024, name)
            text = path.read_text(encoding="utf-8")
            for heading in REQUIRED_SECTIONS:
                self.assertIn(heading, text, f"{name}: missing template section {heading}")
            self.assertIn("docs/_meta/routes/", text, name)
            self.assertIn("docs/_meta/generated/task-packets/", text, name)

    def test_guide_index_links_each_guide_exactly_once(self) -> None:
        text = (GUIDES / "index.md").read_text(encoding="utf-8")
        for name in GUIDE_NAMES:
            self.assertEqual(text.count(f"({name})"), 1, name)

    def test_guides_do_not_own_normative_requirements(self) -> None:
        for path in sorted(GUIDES.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            self.assertIn("requirements: []", frontmatter, path.name)
            self.assertNotIn("AIXEM-REQ-AUTHORING-GUIDE", text, path.name)

    def test_root_and_local_retrieval_chain(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        reference = (ROOT / "REFERENCE.md").read_text(encoding="utf-8")
        authoring = (ROOT / "docs" / "authoring" / "index.md").read_text(encoding="utf-8")
        library = (ROOT / "library" / "README.md").read_text(encoding="utf-8")
        target = "docs/authoring/guides/index.md"
        self.assertIn(target, agents)
        self.assertIn(target, reference)
        self.assertIn("guides/index.md", authoring)
        self.assertIn("create-library-part", library)
        self.assertIn("library-layout-contract", library)
        self.assertIn("electronics", library)
        self.assertIn("architecture", library)

    def test_create_library_part_exposes_required_decisions(self) -> None:
        text = (GUIDES / "create-library-part.md").read_text(encoding="utf-8")
        for token in (
            CANONICAL_ROOT,
            "library/architecture",
            ".aixlib.json",
            ".aixsym.json",
            "datasheet-backed",
            "generic-template",
            "placeholder",
            "sourceUri",
            "G = 2.5 mm",
            "P = 5.0 mm",
            "M = 10 mm",
            "(N - 1)P + 2G",
            "render PASS",
            "copying geometry",
        ):
            self.assertIn(token, text)

    def test_route_visibility_and_budgets(self) -> None:
        expected = {
            "create-symbol.yaml": {"AIXEM-SPEC-LIBRARY-LAYOUT-001", "AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001", "AIXEM-SPEC-SYMBOL-DESIGN-001"},
            "create-schematic.yaml": {"AIXEM-SCHEM-PLACEMENT-001", "AIXEM-SCHEM-GRID-001"},
            "route-nets.yaml": {"AIXEM-SCHEM-GRID-001", "AIXEM-ROUTE-CONSTRAINT-001"},
            "validate-project.yaml": {"AIXEM-SPEC-LIBRARY-LAYOUT-001", "AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001"},
        }
        for filename, ids in expected.items():
            text = (ROOT / "docs" / "_meta" / "routes" / filename).read_text(encoding="utf-8")
            for document_id in ids:
                self.assertIn(document_id, text, filename)
            self.assertIn("max_documents: 7", text, filename)
            self.assertIn("max_bytes: 98304", text, filename)
            self.assertIn("max_depth: 3", text, filename)

    def test_agent_visible_examples_use_canonical_library_tree(self) -> None:
        for project_path in sorted((ROOT / "examples" / "authoring").glob("[0-9][0-9]-*/project.aixproj.json")):
            project = json.loads(project_path.read_text(encoding="utf-8"))["project"]
            for reference in project.get("libraries", []):
                self.assertTrue(reference["path"].startswith("library/electronics/"), project_path)
                self.assertNotIn("libraries/", reference["path"])
            root = project_path.parent
            libraries = list((root / "library").rglob("*.aixlib.json"))
            symbols = list((root / "library").rglob("*.aixsym.json"))
            self.assertTrue(libraries, project_path)
            self.assertTrue(symbols, project_path)
            for library_path in libraries:
                library = json.loads(library_path.read_text(encoding="utf-8"))["library"]
                for component in library["components"]:
                    provenance = component.get("metadata", {}).get("partProvenance", {})
                    self.assertEqual(provenance.get("status"), "generic-template", library_path)
                    for presentation in component["presentations"]:
                        self.assertTrue(presentation["asset"]["path"].startswith("library/electronics/"), library_path)

    def test_legacy_path_compatibility_fixture_remains_explicit(self) -> None:
        test_text = (ROOT / "tests" / "schematic" / "test_authoring_integrity.py").read_text(encoding="utf-8")
        self.assertIn("test_lby005_existing_legacy_repair", test_text)
        self.assertIn("libraries/authoring.aixlib.json", test_text)


if __name__ == "__main__":
    unittest.main()

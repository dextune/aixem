"""Repository-level conformance tests for AIXEM 0.5.1."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools" / "docs"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import aixem_docs  # noqa: E402

CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".js", ".css", ".html", ".svg", ".txt", ".sh", ".aixem"}


class RepositoryConformanceTests(unittest.TestCase):
    """End-to-end tests referenced by normative requirement metadata."""

    @classmethod
    def setUpClass(cls) -> None:
        aixem_docs.compile_generated()
        aixem_docs.build_legacy_reference()
        aixem_docs.build_site()

    def test_documentation_integrity(self) -> None:
        documents = aixem_docs.load_documents()
        routes = aixem_docs.load_routes()
        docs_result = aixem_docs.validate_documents(documents)
        route_result = aixem_docs.validate_routes(routes, documents)
        self.assertTrue(docs_result["valid"], docs_result["errors"])
        self.assertTrue(route_result["valid"], route_result["errors"])
        repository_docs = aixem_docs.audit_repository_documents(documents, require_redirects=True)
        self.assertTrue(repository_docs["valid"], repository_docs["errors"])
        self.assertEqual(0, repository_docs["orphans"])
        self.assertEqual(0, repository_docs["unknownRoles"])
        self.assertEqual([], aixem_docs.detect_dependency_cycles(documents))
        self.assertTrue(aixem_docs.validate_site()["valid"], aixem_docs.validate_site()["errors"])
        self.assertTrue(aixem_docs.validate_migration_inventory()["valid"], aixem_docs.validate_migration_inventory()["errors"])
        trace = json.loads((ROOT / "docs" / "_meta" / "generated" / "requirement-traceability.json").read_text(encoding="utf-8"))
        self.assertEqual(0, trace["summary"]["silentGaps"])
        self.assertGreaterEqual(trace["summary"]["requirements"], 100)

    def test_route_integrity(self) -> None:
        corpus = json.loads((ROOT / "tests" / "docs" / "retrieval-corpus.json").read_text(encoding="utf-8"))
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                result = aixem_docs.route_query(case["query"])
                if "expectedRoute" in case:
                    self.assertIsNotNone(result.get("route"), result)
                    self.assertEqual(case["expectedRoute"], result["route"]["id"])
                    self.assertEqual(case.get("expectedFallback", False), result.get("fallbackUsed", False))
                    budget = result["route"]["budget"]
                    computed = result["route"]["computed"]
                    self.assertLessEqual(computed["documents"], budget["max_documents"])
                    self.assertLessEqual(computed["bytes"], budget["max_bytes"])
                    self.assertLessEqual(computed["maxDepth"], budget["max_depth"])
                else:
                    self.assertTrue(result.get("fallbackUsed"), result)
                    returned = {item["id"] for item in result.get("documents", [])}
                    expected = set(case.get("expectedDocuments", []))
                    self.assertTrue(expected.issubset(returned), {"expected": expected, "returned": returned})
                    self.assertLessEqual(len(result.get("documents", [])), 7)

    def test_schematic_example(self) -> None:
        result = aixem_docs.check_render_determinism()
        self.assertTrue(result["valid"], result)
        report = json.loads((ROOT / "examples" / "electronics-grid-controller" / "evidence" / "project-validation.json").read_text(encoding="utf-8"))
        self.assertTrue(report["valid"], report["diagnostics"])
        self.assertEqual(17, report["statistics"]["entities"])
        self.assertEqual(20, report["statistics"]["nets"])
        self.assertEqual(2.5, report["gridValidation"]["snap"])
        self.assertEqual(126, report["gridValidation"]["orthogonalSegments"])
        self.assertTrue(report["checks"]["geometryDoesNotCreateConnectivity"])
        self.assertTrue(report["checks"]["remoteAssetsDenied"])

    def test_agent_policy(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in ("route-index.json", "maximum documents: **7**", "96 KiB", "maximum reference depth: **3**", "Do not invent"):
            self.assertIn(required, agents)
        route_index = json.loads((ROOT / "docs" / "_meta" / "generated" / "route-index.json").read_text(encoding="utf-8"))
        self.assertTrue(route_index["policy"]["exactRouteFirst"])
        self.assertEqual(7, route_index["policy"]["defaultMaxDocuments"])
        self.assertEqual(98304, route_index["policy"]["defaultMaxBytes"])
        self.assertEqual(3, route_index["policy"]["defaultMaxDepth"])
        self.assertEqual("deny", route_index["policy"]["remoteFetch"])

    def test_review_evidence(self) -> None:
        review_dir = ROOT / "validation" / "evidence" / "reviews"
        expected = {
            "architecture-review.md",
            "vendor-neutrality-review.md",
            "accessibility-review.md",
            "visual-review.md",
            "compatibility-review.md",
        }
        self.assertEqual(expected, {path.name for path in review_dir.glob("*.md")})
        for path in review_dir.glob("*.md"):
            self.assertIn("Status: **PASS**", path.read_text(encoding="utf-8"), path)

    def test_english_only_release_text(self) -> None:
        violations = []
        excluded_prefixes = {"legacy/0.4-inventory.csv", "legacy/0.4-inventory.json"}
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            # Inventory records contain only file paths, hashes, and Boolean language audit results.
            # They are still scanned; the exclusion set is reserved for future raw provenance fields.
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if CJK_RE.search(text):
                violations.append(rel)
        self.assertEqual([], violations)

    def test_requirement_evidence(self) -> None:
        trace_path = ROOT / "docs" / "_meta" / "generated" / "requirement-traceability.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        missing = []
        invalid = []
        for record in trace["requirements"]:
            for rel in record["coverage"].get("evidence", []):
                path = ROOT / rel
                if not path.is_file():
                    missing.append(rel)
                    continue
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("requirement") != record["id"] or data.get("status") != "pass":
                    invalid.append(rel)
        self.assertEqual([], missing)
        self.assertEqual([], invalid)

    def test_release_manifest_when_present(self) -> None:
        manifest = ROOT / "release" / "manifest.json"
        if manifest.exists():
            result = aixem_docs.verify_release_manifest()
            self.assertTrue(result["valid"], result["errors"])


if __name__ == "__main__":
    unittest.main()

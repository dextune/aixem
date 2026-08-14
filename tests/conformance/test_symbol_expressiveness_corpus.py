"""AIXEM 0.5.2 symbol-expressiveness and Static 2D Block conformance tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
SCHEMATIC = ROOT / "implementation" / "schematic"
for path in (TOOLS, SCHEMATIC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import validate_symbol_corpus as corpus  # noqa: E402

SYMBOL_ROOT = ROOT / "validation" / "corpus" / "symbol-expressiveness-1"
B2D_ROOT = ROOT / "validation" / "corpus" / "static-2d-block-1"
SYMBOL_SCHEMA = ROOT / "docs" / "specifications" / "schemas" / "component-graphics-1" / "aixem-symbol-asset-1.schema.json"
BASELINE_SYMBOL_SCHEMA_DIGEST = "ba4d442591f6e53daf07f9d8f85e2026043f4e93ae0710e2578447dd3c466831"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SymbolCorpusConformanceTests(unittest.TestCase):
    def test_inventory_is_exact_and_complete(self) -> None:
        symbol_manifest = read_json(SYMBOL_ROOT / "manifest.json")
        b2d_manifest = read_json(B2D_ROOT / "manifest.json")
        symbol_counts = Counter(item["tier"] for item in symbol_manifest["cases"])
        self.assertEqual({"core": 24, "extended": 5, "probe": 1}, dict(symbol_counts))
        self.assertEqual(30, len(symbol_manifest["cases"]))
        self.assertEqual(6, len(b2d_manifest["cases"]))
        self.assertEqual([f"S{i:03d}" for i in range(1, 31)], [item["id"] for item in symbol_manifest["cases"]])
        self.assertEqual([f"B{i:03d}" for i in range(1, 7)], [item["id"] for item in b2d_manifest["cases"]])
        for root, manifest in ((SYMBOL_ROOT, symbol_manifest), (B2D_ROOT, b2d_manifest)):
            for entry in manifest["cases"]:
                case_path = root / entry["path"]
                self.assertTrue(case_path.is_file(), case_path)
                case = read_json(case_path)
                self.assertTrue((case_path.parent / case["symbolPath"]).is_file())

    def test_all_case_contracts_symbols_digests_and_reviews_are_closed(self) -> None:
        for root in (SYMBOL_ROOT, B2D_ROOT):
            manifest = read_json(root / "manifest.json")
            case_schema = (root / manifest["caseSchema"]).resolve()
            approved = read_json(root / "expected" / "approved-render-digests.json")["cases"]
            reviews = read_json(root / "results" / "visual-review.json")["cases"]
            self.assertEqual({item["id"] for item in manifest["cases"]}, set(approved))
            self.assertEqual({item["id"] for item in manifest["cases"]}, set(reviews))
            for entry in manifest["cases"]:
                case_path = root / entry["path"]
                case = corpus.validate_case_contract(case_path, case_schema)
                symbol_path = case_path.parent / case["symbolPath"]
                symbol_doc = read_json(symbol_path)
                static = corpus.static_assertions(case, symbol_doc, symbol_path)
                self.assertEqual(static["symbolDigest"], approved[case["id"]]["sourceDigest"])
                self.assertEqual(static["geometrySignatureDigest"], approved[case["id"]]["geometrySignatureDigest"])
                review = reviews[case["id"]]
                self.assertEqual("PASS", review["result"])
                self.assertEqual(static["symbolDigest"], review["sourceDigest"])
                self.assertTrue(all(review["checks"].values()), case["id"])

    def test_current_symbol_schema_is_unchanged_from_0_5_1(self) -> None:
        self.assertEqual(BASELINE_SYMBOL_SCHEMA_DIGEST, sha256_hex(SYMBOL_SCHEMA))

    def test_full_corpus_runs_through_production_renderer(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-corpus-test-") as temporary:
            output = Path(temporary) / "result.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "validate_symbol_corpus.py"),
                    "--all",
                    "--repeat",
                    "1",
                    "--json-out",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, proc.returncode, proc.stdout + "\n" + proc.stderr)
            payload = read_json(output)
            self.assertEqual("PASS", payload["summary"]["S-Core"]["status"])
            self.assertEqual("PASS", payload["summary"]["S-Extended"]["status"])
            self.assertEqual("PASS", payload["summary"]["B2D"]["status"])
            self.assertEqual("NOT_SUPPORTED", payload["summary"]["MU"]["result"])
            self.assertEqual(36, len(payload["cases"]))
            self.assertTrue(all(item["render"]["renderer"]["id"] == corpus.RENDERER_ID for item in payload["cases"]))

    def test_dimension_label_regression_is_explicit_and_deterministic(self) -> None:
        manifest = read_json(B2D_ROOT / "manifest.json")
        entry = next(item for item in manifest["cases"] if item["id"] == "B005")
        case_path = B2D_ROOT / entry["path"]
        case = read_json(case_path)
        symbol_path = case_path.parent / case["symbolPath"]
        with tempfile.TemporaryDirectory(prefix="aixem-b005-") as temporary:
            output = Path(temporary) / "render"
            result = corpus.render_repeated(case, symbol_path, 3, output)
            svg = (output / "drawing.svg").read_text(encoding="utf-8")
            self.assertEqual(3, result["repeat"])
            self.assertIn('class="dimension-label"', svg)
            self.assertIn('font-size="3"', svg)
            self.assertIn("50.0mm", svg)
            self.assertIn("30.0mm", svg)
            self.assertNotIn('class="dimension-label" font-size="16"', svg)

    def test_multi_unit_probe_rejects_simulated_shared_identity(self) -> None:
        manifest = read_json(SYMBOL_ROOT / "manifest.json")
        entry = next(item for item in manifest["cases"] if item["id"] == "S030")
        case_path = SYMBOL_ROOT / entry["path"]
        case = read_json(case_path)
        symbol_path = case_path.parent / case["symbolPath"]
        symbol_doc = read_json(symbol_path)
        static = corpus.static_assertions(case, symbol_doc, symbol_path)
        with tempfile.TemporaryDirectory(prefix="aixem-s030-") as temporary:
            render = corpus.render_repeated(case, symbol_path, 1, Path(temporary) / "render")
        result = {
            "id": "S030",
            "automatedStatus": "PASS",
            "static": static,
            "render": render,
        }
        probe = corpus.multi_unit_probe(result, case, symbol_path)
        self.assertEqual("NOT_SUPPORTED", probe["result"])
        self.assertTrue(probe["valid"])
        self.assertEqual("PASS", probe["graphicalMonolith"])
        self.assertFalse(probe["requiredSemanticProperties"]["independentlyPlaceableUnits"])
        self.assertIn("duplicate placement entity", probe["negativeTest"]["observed"].lower())
        self.assertIn("variants were not misused", probe["interpretation"].lower())


if __name__ == "__main__":
    unittest.main()

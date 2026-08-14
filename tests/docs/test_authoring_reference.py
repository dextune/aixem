"""Schema-to-document and executable-snippet coverage for AIXEM 0.5.1."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "docs"))

from authoring_validation import validate_reference_coverage, validate_snippet_blocks  # noqa: E402


class AuthoringReferenceTests(unittest.TestCase):
    def test_schema_reference_coverage(self) -> None:
        result = validate_reference_coverage()
        self.assertTrue(result["valid"], result["issues"])
        self.assertEqual(result["coverage"], 1.0)
        self.assertEqual(result["covered"], result["total"])

    def test_source_backed_snippets(self) -> None:
        result = validate_snippet_blocks()
        self.assertTrue(result["valid"], result["issues"])
        self.assertGreaterEqual(result["snippets"], 12)


if __name__ == "__main__":
    unittest.main()

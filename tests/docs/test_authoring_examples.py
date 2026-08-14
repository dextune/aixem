"""Executable authoring fixtures and visual-repair checks for AIXEM 0.5.1."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "docs"))

from authoring_validation import AUTHORING, lint_symbol, validate_all_authoring_examples  # noqa: E402


class AuthoringExampleTests(unittest.TestCase):
    def test_symbol_design_profile(self) -> None:
        checked = 0
        for symbol in sorted(AUTHORING.glob("[0-9][0-9]-*/library/**/*.aixsym.json")):
            result = lint_symbol(symbol)
            self.assertTrue(result["valid"], f"{symbol}: {result['issues']}")
            checked += 1
        self.assertGreaterEqual(checked, 8)

    def test_authoring_golden_examples(self) -> None:
        result = validate_all_authoring_examples(check_determinism=True)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["examples"], 8)
        self.assertTrue(all(item["valid"] for item in result["results"]))

    def test_visual_repair_fixture(self) -> None:
        broken = AUTHORING / "08-visual-repair" / "fixtures" / "broken-lead-port.aixsym.json"
        fixed = AUTHORING / "08-visual-repair" / "library" / "electronics" / "authoring" / "repaired-resistor.aixsym.json"
        broken_result = lint_symbol(broken)
        fixed_result = lint_symbol(fixed)
        self.assertFalse(broken_result["valid"])
        self.assertIn("lead-port-mismatch", {item["code"] for item in broken_result["issues"]})
        self.assertTrue(fixed_result["valid"], fixed_result["issues"])


if __name__ == "__main__":
    unittest.main()

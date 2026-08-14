"""Focused tests for the read-only deterministic placement assistant."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from implementation.schematic.placement_assist import snap_point, snap_scalar, suggest_placement

ROOT = Path(__file__).resolve().parents[2]


class PlacementAssistTests(unittest.TestCase):
    def test_g001_already_legal(self) -> None:
        result = suggest_placement([62.5, 42.5], [])
        self.assertEqual([62.5, 42.5], result["selectedCoordinate"])
        self.assertEqual("none", result["alignment"])

    def test_g002_quantized(self) -> None:
        result = suggest_placement([63.1, 42.2], [])
        self.assertEqual([62.5, 42.5], result["baseSnappedCoordinate"])

    def test_positive_midpoint_is_away_from_zero(self) -> None:
        self.assertEqual(2.5, snap_scalar(1.25, 0, 2.5))

    def test_negative_midpoint_is_away_from_zero(self) -> None:
        self.assertEqual(-2.5, snap_scalar(-1.25, 0, 2.5))

    def test_nonzero_origin(self) -> None:
        self.assertEqual([12.5, 7.5], snap_point([11.3, 8.7], [2.5, 2.5], 5))

    def test_snap_is_idempotent(self) -> None:
        point = [62.5, 42.5]
        self.assertEqual(point, snap_point(point, [0, 0], 2.5))

    def test_g003_magnetic_row(self) -> None:
        result = suggest_placement([63.1, 42.2], [[20, 40]])
        self.assertEqual([62.5, 40], result["selectedCoordinate"])
        self.assertEqual("y", result["alignment"])

    def test_magnetic_column(self) -> None:
        result = suggest_placement([63.1, 42.2], [[60, 80]])
        self.assertEqual([60, 42.5], result["selectedCoordinate"])
        self.assertEqual("x", result["alignment"])

    def test_xy_alignment_wins(self) -> None:
        result = suggest_placement([63.1, 42.2], [[60, 10], [100, 40]])
        self.assertEqual([60, 40], result["selectedCoordinate"])
        self.assertEqual("xy", result["alignment"])

    def test_g004_outside_window_not_acquired(self) -> None:
        result = suggest_placement([63.1, 42.2], [[57.5, 80], [100, 35]])
        self.assertEqual("none", result["alignment"])

    def test_at_window_boundary_is_acquired(self) -> None:
        result = suggest_placement([63.1, 42.2], [[60, 40]])
        self.assertEqual("xy", result["alignment"])

    def test_illegal_existing_origin_is_ignored(self) -> None:
        result = suggest_placement([63.1, 42.2], [[60.1, 40.1]])
        self.assertEqual("none", result["alignment"])

    def test_candidate_count_is_bounded(self) -> None:
        result = suggest_placement([63.1, 42.2], [[60, 10], [100, 40], [65, 200], [200, 45]])
        self.assertLessEqual(result["candidateCount"], 4)

    def test_input_order_does_not_change_result(self) -> None:
        origins = [[60, 10], [100, 40], [65, 200], [200, 45]]
        first = suggest_placement([63.1, 42.2], origins)
        second = suggest_placement([63.1, 42.2], reversed(origins))
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_no_mutation_of_inputs(self) -> None:
        proposed = [63.1, 42.2]
        origins = [[60, 10], [100, 40]]
        proposed_before = copy.deepcopy(proposed)
        origins_before = copy.deepcopy(origins)
        result = suggest_placement(proposed, origins)
        self.assertEqual(proposed_before, proposed)
        self.assertEqual(origins_before, origins)
        self.assertFalse(result["mutated"])
        self.assertEqual("derived-advisory-only", result["authority"])

    def test_invalid_coordinate_fails(self) -> None:
        with self.assertRaises(ValueError):
            suggest_placement([float("nan"), 0], [])
        with self.assertRaises(ValueError):
            suggest_placement([0, 0], [], grid=0)

    def test_cli_emits_read_only_payload(self) -> None:
        process = subprocess.run(
            [sys.executable, "tools/placement_assist.py", "suggest", "--point", "63.1,42.2", "--existing", "60,40"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual([60, 40], payload["selectedCoordinate"])
        self.assertFalse(payload["mutated"])


if __name__ == "__main__":
    unittest.main()

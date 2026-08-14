"""Regression tests for the isolated library-part authoring backlog."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import library_backlog  # noqa: E402


class LibraryBacklogTests(unittest.TestCase):
    def write(self, root: Path, rel: str, content: str) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")

    def scaffold(self, root: Path, *, index_rows: list[str], shards: dict[str, str]) -> None:
        self.write(root, "README.md", "# Test Workspace")
        self.write(root, "index.md", "# Index\n\n" + "\n".join(index_rows))
        for rel, content in shards.items():
            self.write(root, rel, content)

    def test_repository_scaffold_is_valid_and_empty(self) -> None:
        workspace = ROOT / "planning" / "library-parts"
        self.assertEqual([], library_backlog.validate_workspace(workspace))
        shards, errors = library_backlog.backlog_shards(workspace)
        self.assertEqual([], errors)
        self.assertEqual(9, len(shards))
        items, errors = library_backlog.all_items(workspace)
        self.assertEqual([], errors)
        self.assertEqual([], items)

    def test_next_selection_uses_index_order_not_lexical_path_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-backlog-order-") as temporary:
            root = Path(temporary)
            self.scaffold(
                root,
                index_rows=[
                    "- [Passive](backlog/passive/001.md)",
                    "- [Analog](backlog/analog/001.md)",
                ],
                shards={
                    "backlog/passive/001.md": "# Passive — 001\n\n- [ ] `library/electronics/passive/resistors` — Resistor IEC",
                    "backlog/analog/001.md": "# Analog — 001\n\n- [ ] `library/electronics/analog/op-amps` — Generic Op Amp",
                },
            )
            self.assertEqual([], library_backlog.validate_workspace(root))
            selected = library_backlog.select_next(root, limit=2)
            self.assertEqual(["Resistor IEC", "Generic Op Amp"], [item.name for item in selected])
            self.assertEqual(["passive", "analog"], [item.category for item in selected])

    def test_invalid_target_duplicate_and_shard_overflow_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-backlog-invalid-") as temporary:
            root = Path(temporary)
            overflow = "\n".join(
                f"- [ ] `library/electronics/passive/resistors` — R-{index:03d}" for index in range(101)
            )
            self.scaffold(
                root,
                index_rows=[
                    "- [One](backlog/passive/001.md)",
                    "- [Two](backlog/passive/002.md)",
                ],
                shards={
                    "backlog/passive/001.md": "# Passive — 001\n\n- [ ] `libraries/passive` — Wrong Root\n- [ ] `library/electronics/passive/resistors` — Duplicate",
                    "backlog/passive/002.md": "# Passive — 002\n\n- [ ] `library/electronics/passive/resistors` — Duplicate\n" + overflow,
                },
            )
            errors = library_backlog.validate_workspace(root)
            self.assertTrue(any("target must be below library/electronics" in error for error in errors), errors)
            self.assertTrue(any("duplicate backlog item" in error for error in errors), errors)
            self.assertTrue(any("exceeds shard limit 100" in error for error in errors), errors)

    def test_completed_item_requires_matching_generation_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-backlog-pass-") as temporary:
            root = Path(temporary)
            self.scaffold(
                root,
                index_rows=["- [Passive](backlog/passive/001.md)"],
                shards={
                    "backlog/passive/001.md": "# Passive — 001\n\n- [x] `library/electronics/passive/resistors` — Resistor IEC",
                },
            )
            errors = library_backlog.validate_workspace(root)
            self.assertTrue(any("has no matching generation PASS" in error for error in errors), errors)

            self.write(
                root,
                "logs/2026/2026-08-14.md",
                "# Library Part Generation Log — 2026-08-14\n\n## Resistor IEC\n\n- Backlog: `backlog/passive/001.md`\n- Target: `library/electronics/passive/resistors`\n- Result: PASS",
            )
            self.write(
                root,
                "index.md",
                "# Index\n\n- [Passive](backlog/passive/001.md)\n- [2026-08-14 generation](logs/2026/2026-08-14.md)",
            )
            self.assertEqual([], library_backlog.validate_workspace(root))
            created = library_backlog.created_for_date(root, "2026-08-14")
            self.assertEqual(["Resistor IEC"], [record.name for record in created])

    def test_generation_fail_may_remain_unchecked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-backlog-fail-") as temporary:
            root = Path(temporary)
            self.scaffold(
                root,
                index_rows=[
                    "- [Passive](backlog/passive/001.md)",
                    "- [Generation](logs/2026/2026-08-14.md)",
                ],
                shards={
                    "backlog/passive/001.md": "# Passive — 001\n\n- [ ] `library/electronics/passive/resistors` — Resistor IEC",
                },
            )
            self.write(
                root,
                "logs/2026/2026-08-14.md",
                "# Library Part Generation Log — 2026-08-14\n\n## Resistor IEC\n\n- Backlog: `backlog/passive/001.md`\n- Target: `library/electronics/passive/resistors`\n- Result: FAIL\n- Note: source review incomplete",
            )
            self.assertEqual([], library_backlog.validate_workspace(root))
            self.assertEqual(["Resistor IEC"], [item.name for item in library_backlog.select_next(root)])

    def test_review_pending_requires_independent_review_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aixem-backlog-review-") as temporary:
            root = Path(temporary)
            self.scaffold(
                root,
                index_rows=[
                    "- [Passive](backlog/passive/001.md)",
                    "- [Generation](logs/2026/2026-08-14.md)",
                    "- [Review](reviews/2026/2026-08-15.md)",
                ],
                shards={
                    "backlog/passive/001.md": "# Passive — 001\n\n- [x] `library/electronics/passive/resistors` — Resistor IEC\n- [x] `library/electronics/passive/capacitors` — Capacitor IEC",
                },
            )
            self.write(
                root,
                "logs/2026/2026-08-14.md",
                "# Library Part Generation Log — 2026-08-14\n\n## Resistor IEC\n\n- Backlog: `backlog/passive/001.md`\n- Target: `library/electronics/passive/resistors`\n- Result: PASS\n\n## Capacitor IEC\n\n- Backlog: `backlog/passive/001.md`\n- Target: `library/electronics/passive/capacitors`\n- Result: PASS",
            )
            self.write(
                root,
                "reviews/2026/2026-08-15.md",
                "# Library Part Review Log — 2026-08-15\n\n## Resistor IEC\n\n- Generation Log: `logs/2026/2026-08-14.md`\n- Backlog: `backlog/passive/001.md`\n- Target: `library/electronics/passive/resistors`\n- Result: PASS",
            )
            self.assertEqual([], library_backlog.validate_workspace(root))
            pending = library_backlog.review_pending_for_date(root, "2026-08-14")
            self.assertEqual(["Capacitor IEC"], [record.name for record in pending])


if __name__ == "__main__":
    unittest.main()

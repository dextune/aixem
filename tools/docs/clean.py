#!/usr/bin/env python3
"""Remove reproducible AIXEM build products while preserving canonical sources and authored evidence."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    ROOT / "site",
    ROOT / "reference",
    ROOT / "docs" / "_meta" / "generated",
    ROOT / "validation" / "evidence" / "requirements",
    ROOT / "validation" / "evidence" / "validator-results.json",
    ROOT / "validation" / "evidence" / "requirement-evidence-summary.json",
    ROOT / "validation" / "test-results.json",
    ROOT / "release" / "manifest.json",
    ROOT / "release" / "archive-verification.json",
]


def main() -> int:
    removed = 0
    for path in TARGETS:
        if path.is_dir():
            shutil.rmtree(path)
            removed += 1
        elif path.exists():
            path.unlink()
            removed += 1
    for cache in sorted(ROOT.rglob("__pycache__"), reverse=True):
        if cache.is_dir():
            shutil.rmtree(cache)
            removed += 1
    for path in ROOT.rglob("*.pyc"):
        path.unlink(missing_ok=True)
        removed += 1
    print(f"Removed {removed} reproducible build targets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

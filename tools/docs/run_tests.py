#!/usr/bin/env python3
"""Run the AIXEM documentation, route, schematic, and review conformance suite."""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = "2026-08-12T00:00:00Z"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--verbosity", type=int, default=2)
    parser.add_argument("--output", type=Path, default=ROOT / "validation" / "test-results.json")
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern=args.pattern, top_level_dir=str(ROOT))
    buffer = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=buffer, verbosity=args.verbosity).run(suite)
    duration = time.perf_counter() - start
    transcript = buffer.getvalue()
    sys.stdout.write(transcript)

    payload = {
        "schema": "https://schemas.aixem.org/validation/test-run/1",
        "formatVersion": "1.0",
        "release": f"AIXEM-SRP-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}-2026-08-12",
        "generatedAt": FIXED_TIME,
        "successful": result.wasSuccessful(),
        "testsRun": result.testsRun,
        "failures": [{"test": str(test), "message": message} for test, message in result.failures],
        "errors": [{"test": str(test), "message": message} for test, message in result.errors],
        "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
        "durationSeconds": round(duration, 6),
        "transcript": transcript,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0 if result.wasSuccessful() else 2


if __name__ == "__main__":
    raise SystemExit(main())

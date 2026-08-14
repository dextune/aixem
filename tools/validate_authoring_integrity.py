#!/usr/bin/env python3
"""Validate AIXEM 0.5.9 library-part authoring integrity without network access."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from implementation.schematic.authoring_integrity import validate_library_document  # noqa: E402


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--operation", choices=("added", "modified"), default="modified")
    parser.add_argument("--review-records", type=Path)
    parser.add_argument("--intent-records", type=Path)
    args = parser.parse_args()
    try:
        library = read_json(args.library)
        reviews = read_json(args.review_records) if args.review_records else None
        intents = read_json(args.intent_records) if args.intent_records else None
        try:
            artifact_path = args.library.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            artifact_path = args.library.as_posix()
        result = validate_library_document(
            library,
            artifact_path=artifact_path,
            operation=args.operation,
            review_records=reviews,
            intent_records=intents,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

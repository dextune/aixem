#!/usr/bin/env python3
"""Read-only CLI for deterministic AIXEM placement suggestions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from implementation.schematic.placement_assist import suggest_placement  # noqa: E402


def _point(value: str) -> list[float]:
    try:
        parts = [float(item.strip()) for item in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("point must be x,y") from exc
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("point must contain exactly x,y")
    return parts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    suggest = sub.add_parser("suggest", help="suggest a legal snap/alignment coordinate without writing files")
    suggest.add_argument("--point", type=_point, required=True, help="proposed x,y coordinate")
    suggest.add_argument("--existing", type=_point, action="append", default=[], help="existing legal x,y origin; repeatable")
    suggest.add_argument("--grid", type=float, default=2.5)
    suggest.add_argument("--pin-pitch", type=float, default=5.0)
    suggest.add_argument("--major-grid", type=float, default=10.0)
    suggest.add_argument("--origin", type=_point, default=[0.0, 0.0])
    args = parser.parse_args()
    try:
        payload = suggest_placement(
            args.point,
            args.existing,
            grid=args.grid,
            pin_pitch=args.pin_pitch,
            major_grid=args.major_grid,
            origin=args.origin,
        )
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

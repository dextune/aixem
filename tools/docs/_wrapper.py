"""Shared entrypoint helper for the small AIXEM documentation command wrappers."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import aixem_docs  # noqa: E402


def run(command: str, argv: list[str] | None = None) -> int:
    return aixem_docs.main([command, *(argv if argv is not None else sys.argv[1:])])

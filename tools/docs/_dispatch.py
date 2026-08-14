"""Small command wrappers for the AIXEM documentation toolchain."""
from __future__ import annotations

from aixem_docs import main


def run(command: str, extra: list[str] | None = None) -> int:
    return int(main([command, *(extra or [])]))

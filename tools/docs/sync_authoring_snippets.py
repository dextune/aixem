#!/usr/bin/env python3
"""Synchronize source-backed JSON snippets in canonical Markdown documents."""
from __future__ import annotations

import json
from pathlib import Path

from authoring_validation import ROOT, SNIPPET_RE, json_pointer, read_json


def render_block(source: str, pointer: str | None, value: object) -> str:
    target = f"{source}{pointer or ''}"
    literal = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return f"<!-- aixem-snippet: {target} -->\n```json\n{literal}\n```\n<!-- /aixem-snippet -->"


def sync() -> tuple[int, int]:
    changed = 0
    snippets = 0
    for doc in sorted((ROOT / "docs").rglob("*.md")):
        original = doc.read_text(encoding="utf-8")

        def replace(match):  # type: ignore[no-untyped-def]
            nonlocal snippets
            snippets += 1
            rel_source, pointer, _literal = match.groups()
            source = (ROOT / rel_source).resolve()
            source.relative_to(ROOT.resolve())
            value = json_pointer(read_json(source), pointer)
            return render_block(rel_source, pointer, value)

        updated = SNIPPET_RE.sub(replace, original)
        if updated != original:
            doc.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed, snippets


def main() -> int:
    changed, snippets = sync()
    print(f"synchronized snippets: {snippets}; changed documents: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Inventory the exact AIXEM 0.5.0 baseline and compare it with the 0.5.1 worktree."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "validation" / "evidence" / "pass-01"
FIXED_TIME = "2026-08-11T00:00:00Z"
RELEASE = "AIXEM-SRP-0.5.1-2026-08-11"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def normalize_archive_name(name: str, top: str | None) -> str:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe baseline member: {name}")
    parts = list(pure.parts)
    if top and parts and parts[0] == top:
        parts = parts[1:]
    return PurePosixPath(*parts).as_posix() if parts else ""


def inventory_zip(path: Path) -> tuple[list[dict[str, Any]], str]:
    files: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        tops = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
        top = next(iter(tops)) if len(tops) == 1 else None
        seen: set[str] = set()
        for item in sorted((x for x in archive.infolist() if not x.is_dir()), key=lambda x: x.filename):
            rel = normalize_archive_name(item.filename, top)
            if not rel or rel in seen:
                raise ValueError(f"duplicate or empty baseline path: {rel!r}")
            seen.add(rel)
            data = archive.read(item)
            files.append({"path": rel, "bytes": len(data), "digest": digest(data), "suffix": Path(rel).suffix.lower()})
    return files, f"zip:{path.name}"


def inventory_directory(path: Path) -> tuple[list[dict[str, Any]], str]:
    files: list[dict[str, Any]] = []
    for item in sorted(path.rglob("*")):
        if not item.is_file() or "__pycache__" in item.parts or item.suffix == ".pyc":
            continue
        rel = item.relative_to(path).as_posix()
        data = item.read_bytes()
        files.append({"path": rel, "bytes": len(data), "digest": digest(data), "suffix": item.suffix.lower()})
    return files, f"directory:{path.name}"


def inventory_baseline(path: Path) -> tuple[list[dict[str, Any]], str]:
    if path.is_file() and zipfile.is_zipfile(path):
        return inventory_zip(path)
    if path.is_dir():
        return inventory_directory(path)
    raise ValueError(f"baseline must be a ZIP or directory: {path}")


def current_inventory() -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for item in sorted(ROOT.rglob("*")):
        if not item.is_file() or "__pycache__" in item.parts or item.suffix == ".pyc":
            continue
        rel = item.relative_to(ROOT).as_posix()
        data = item.read_bytes()
        files.append({"path": rel, "bytes": len(data), "digest": digest(data), "suffix": item.suffix.lower()})
    return files


def read_version(records: list[dict[str, Any]], path: Path) -> str | None:
    if path.is_dir():
        target = path / "VERSION"
        return target.read_text(encoding="utf-8").strip() if target.is_file() else None
    with zipfile.ZipFile(path) as archive:
        candidates = [x for x in archive.namelist() if PurePosixPath(x).name == "VERSION" and not x.endswith("/")]
        if len(candidates) != 1:
            return None
        return archive.read(candidates[0]).decode("utf-8").strip()


def category(rel: str) -> str:
    if rel == "AGENTS.md" or rel.startswith("docs/agent/") or rel.startswith("docs/_meta/routes/") or "task-packet" in rel:
        return "agent-routing"
    if rel.startswith("docs/symbols/") or "aixsym" in rel or "/symbols/" in rel:
        return "symbol-authoring"
    if rel.startswith("docs/routing/"):
        return "routing"
    if rel.startswith("docs/schematic/") or rel.endswith(".aixem") or rel.endswith(".aixlayout.json"):
        return "schematic-authoring"
    if rel.startswith("implementation/schematic/"):
        return "renderer"
    if rel.startswith("docs/specifications/schemas/") or rel.startswith("docs/_meta/schema/"):
        return "schemas"
    if rel.startswith("examples/"):
        return "examples"
    if rel.startswith("validation/") or rel.startswith("tests/"):
        return "validation"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    baseline_path = args.baseline.resolve()
    baseline, source = inventory_baseline(baseline_path)
    baseline_version = read_version(baseline, baseline_path)
    if baseline_version != "0.5.0":
        raise SystemExit(f"Expected baseline VERSION 0.5.0, observed {baseline_version!r}")
    current = current_inventory()
    old = {item["path"]: item for item in baseline}
    new = {item["path"]: item for item in current}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    common = sorted(set(old) & set(new))
    modified = [rel for rel in common if old[rel]["digest"] != new[rel]["digest"]]
    unchanged = [rel for rel in common if old[rel]["digest"] == new[rel]["digest"]]
    focused = sorted(
        rel for rel in set(old) | set(new)
        if category(rel) in {"agent-routing", "symbol-authoring", "routing", "schematic-authoring", "renderer", "schemas", "examples", "validation"}
    )
    baseline_payload = {
        "schema": "https://schemas.aixem.org/validation/baseline-inventory/1",
        "formatVersion": "1.0",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "valid": True,
        "baselineVersion": baseline_version,
        "source": source,
        "sourceDigest": digest(baseline_path.read_bytes()) if baseline_path.is_file() else None,
        "summary": {
            "files": len(baseline),
            "bytes": sum(item["bytes"] for item in baseline),
            "byCategory": dict(sorted(Counter(category(item["path"]) for item in baseline).items())),
            "bySuffix": dict(sorted(Counter(item["suffix"] or "<none>" for item in baseline).items())),
        },
        "files": baseline,
    }
    diff_payload = {
        "schema": "https://schemas.aixem.org/validation/baseline-diff/1",
        "formatVersion": "1.0",
        "release": RELEASE,
        "generatedAt": FIXED_TIME,
        "valid": not removed,
        "baselineVersion": baseline_version,
        "summary": {
            "baselineFiles": len(baseline),
            "currentFiles": len(current),
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed),
            "unchanged": len(unchanged),
            "focusedAuthoringPaths": len(focused),
        },
        "added": added,
        "modified": modified,
        "removed": removed,
        "unchanged": unchanged,
        "focusedAuthoringPaths": [
            {
                "path": rel,
                "category": category(rel),
                "baselineDigest": old.get(rel, {}).get("digest"),
                "currentDigest": new.get(rel, {}).get("digest"),
                "disposition": "added" if rel in added else "modified" if rel in modified else "removed" if rel in removed else "unchanged",
            }
            for rel in focused
        ],
    }
    write_json(args.output / "baseline-0.5.0-inventory.json", baseline_payload)
    write_json(args.output / "baseline-0.5.0-diff.json", diff_payload)
    print(json.dumps({"inventory": baseline_payload["summary"], "diff": diff_payload["summary"], "valid": diff_payload["valid"]}, indent=2, sort_keys=True))
    return 0 if diff_payload["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

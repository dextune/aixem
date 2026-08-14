#!/usr/bin/env python3
"""Validate and query the isolated AIXEM library-part authoring backlog."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE = REPO_ROOT / "planning" / "library-parts"
MAX_ITEMS_PER_SHARD = 100

ITEM_RE = re.compile(r"^- \[(?P<state>[ x])\] `(?P<target>[^`]+)` — (?P<name>\S(?:.*\S)?)$")
SHARD_RE = re.compile(r"^backlog/(?P<category>[a-z0-9]+(?:-[a-z0-9]+)*)/(?P<number>[0-9]{3})\.md$")
GEN_LOG_RE = re.compile(r"^logs/(?P<year>[0-9]{4})/(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})\.md$")
REVIEW_LOG_RE = re.compile(r"^reviews/(?P<year>[0-9]{4})/(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})\.md$")
SEGMENT_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FIELD_RE = re.compile(r"^- (?P<key>[A-Za-z][A-Za-z ]+): (?P<value>.+)$")


@dataclass(frozen=True)
class BacklogItem:
    shard: str
    line: int
    done: bool
    target: str
    name: str

    @property
    def category(self) -> str:
        return PurePosixPath(self.shard).parts[1]

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.shard, self.target, self.name)


@dataclass(frozen=True)
class LogRecord:
    path: str
    line: int
    day: str
    name: str
    backlog: str
    target: str
    result: str
    generation_log: str | None = None

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.backlog, self.target, self.name)


def _strip_code(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def _safe_rel(value: str) -> str | None:
    if "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.as_posix()


def _index_links(workspace: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    index = workspace / "index.md"
    if not index.is_file():
        return [], ["missing planning/library-parts/index.md"]
    links: list[str] = []
    for raw in LINK_RE.findall(index.read_text(encoding="utf-8")):
        target = raw.split("#", 1)[0]
        if not target or ":" in target.split("/", 1)[0]:
            continue
        rel = _safe_rel(target)
        if rel is None:
            errors.append(f"index.md: unsafe relative link {raw!r}")
            continue
        links.append(rel)
    return links, errors


def _actual_markdown(workspace: Path, folder: str) -> set[str]:
    root = workspace / folder
    if not root.exists():
        return set()
    return {path.relative_to(workspace).as_posix() for path in root.rglob("*.md") if path.is_file()}


def _validate_target(target: str) -> str | None:
    rel = _safe_rel(target)
    if rel is None:
        return "target must be a safe project-relative POSIX folder path"
    parts = PurePosixPath(rel).parts
    if len(parts) < 3 or parts[0] != "library" or parts[1] not in {"electronics", "architecture"}:
        return "target must be below library/electronics or library/architecture"
    invalid = [part for part in parts[2:] if not SEGMENT_RE.fullmatch(part)]
    if invalid:
        return f"target segments must be lower-kebab: {invalid[0]!r}"
    return None


def backlog_shards(workspace: Path) -> tuple[list[str], list[str]]:
    links, errors = _index_links(workspace)
    ordered = [link for link in links if link.startswith("backlog/")]
    actual = _actual_markdown(workspace, "backlog")
    indexed = set(ordered)
    for rel in ordered:
        if not SHARD_RE.fullmatch(rel):
            errors.append(f"index.md: invalid shard path {rel}")
        elif not (workspace / rel).is_file():
            errors.append(f"index.md: linked shard does not exist: {rel}")
    for rel in sorted(actual - indexed):
        errors.append(f"unindexed backlog shard: {rel}")
    for rel in sorted(indexed - actual):
        errors.append(f"indexed backlog shard missing: {rel}")
    if len(ordered) != len(set(ordered)):
        errors.append("index.md: duplicate backlog shard link")
    return ordered, errors


def _parse_shard(workspace: Path, rel: str) -> tuple[list[BacklogItem], list[str]]:
    errors: list[str] = []
    match = SHARD_RE.fullmatch(rel)
    if not match:
        return [], [f"invalid shard path: {rel}"]
    path = workspace / rel
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[BacklogItem] = []
    for number, line in enumerate(lines, 1):
        if line.startswith("- ["):
            item_match = ITEM_RE.fullmatch(line)
            if not item_match:
                errors.append(f"{rel}:{number}: invalid backlog item grammar")
                continue
            target = item_match.group("target")
            target_error = _validate_target(target)
            if target_error:
                errors.append(f"{rel}:{number}: {target_error}")
            name = item_match.group("name")
            if "`" in name:
                errors.append(f"{rel}:{number}: part name must not contain backticks")
            items.append(
                BacklogItem(
                    shard=rel,
                    line=number,
                    done=item_match.group("state") == "x",
                    target=target,
                    name=name,
                )
            )
    if len(items) > MAX_ITEMS_PER_SHARD:
        errors.append(f"{rel}: {len(items)} items exceeds shard limit {MAX_ITEMS_PER_SHARD}")
    return items, errors


def all_items(workspace: Path) -> tuple[list[BacklogItem], list[str]]:
    shards, errors = backlog_shards(workspace)
    result: list[BacklogItem] = []
    seen: dict[tuple[str, str], BacklogItem] = {}
    for shard in shards:
        items, item_errors = _parse_shard(workspace, shard)
        errors.extend(item_errors)
        for item in items:
            duplicate_key = (item.target.casefold(), item.name.casefold())
            prior = seen.get(duplicate_key)
            if prior is not None:
                errors.append(
                    f"duplicate backlog item: {item.shard}:{item.line} duplicates {prior.shard}:{prior.line}"
                )
            else:
                seen[duplicate_key] = item
            result.append(item)
    return result, errors


def _log_paths(workspace: Path, folder: str, pattern: re.Pattern[str]) -> tuple[list[str], list[str]]:
    links, errors = _index_links(workspace)
    indexed = [link for link in links if link.startswith(folder + "/")]
    actual = _actual_markdown(workspace, folder)
    indexed_set = set(indexed)
    for rel in indexed:
        match = pattern.fullmatch(rel)
        if not match:
            errors.append(f"index.md: invalid {folder} path {rel}")
            continue
        if match.group("year") != match.group("day")[:4]:
            errors.append(f"{rel}: year directory must match date")
        try:
            date.fromisoformat(match.group("day"))
        except ValueError:
            errors.append(f"{rel}: invalid calendar date")
        if not (workspace / rel).is_file():
            errors.append(f"index.md: linked {folder} file does not exist: {rel}")
    for rel in sorted(actual - indexed_set):
        errors.append(f"unindexed {folder} file: {rel}")
    for rel in sorted(indexed_set - actual):
        errors.append(f"indexed {folder} file missing: {rel}")
    if len(indexed) != len(indexed_set):
        errors.append(f"index.md: duplicate {folder} link")
    return indexed, errors


def _parse_log(workspace: Path, rel: str, *, review: bool) -> tuple[list[LogRecord], list[str]]:
    errors: list[str] = []
    pattern = REVIEW_LOG_RE if review else GEN_LOG_RE
    match = pattern.fullmatch(rel)
    if not match:
        return [], [f"invalid log path: {rel}"]
    day = match.group("day")
    lines = (workspace / rel).read_text(encoding="utf-8").splitlines()
    expected_title = f"# Library Part {'Review' if review else 'Generation'} Log — {day}"
    if not lines or lines[0] != expected_title:
        errors.append(f"{rel}: first line must be {expected_title!r}")

    records: list[LogRecord] = []
    current_name: str | None = None
    current_line = 0
    fields: dict[str, str] = {}

    def flush() -> None:
        nonlocal current_name, current_line, fields
        if current_name is None:
            return
        required = {"Backlog", "Target", "Result"}
        if review:
            required.add("Generation Log")
        missing = sorted(required - set(fields))
        if missing:
            errors.append(f"{rel}:{current_line}: missing fields: {', '.join(missing)}")
        else:
            result = fields["Result"]
            if result not in {"PASS", "FAIL"}:
                errors.append(f"{rel}:{current_line}: Result must be PASS or FAIL")
            backlog = _strip_code(fields["Backlog"])
            target = _strip_code(fields["Target"])
            generation_log = _strip_code(fields["Generation Log"]) if review else None
            records.append(
                LogRecord(
                    path=rel,
                    line=current_line,
                    day=day,
                    name=current_name,
                    backlog=backlog,
                    target=target,
                    result=result,
                    generation_log=generation_log,
                )
            )
        current_name = None
        current_line = 0
        fields = {}

    for number, line in enumerate(lines[1:], 2):
        if line.startswith("## "):
            flush()
            current_name = line[3:].strip()
            current_line = number
            if not current_name:
                errors.append(f"{rel}:{number}: empty record heading")
        elif current_name is not None:
            field_match = FIELD_RE.fullmatch(line)
            if field_match:
                key = field_match.group("key")
                if key in fields:
                    errors.append(f"{rel}:{number}: duplicate field {key}")
                fields[key] = field_match.group("value").strip()
    flush()
    return records, errors


def all_generation_records(workspace: Path) -> tuple[list[LogRecord], list[str]]:
    paths, errors = _log_paths(workspace, "logs", GEN_LOG_RE)
    records: list[LogRecord] = []
    for rel in paths:
        parsed, parsed_errors = _parse_log(workspace, rel, review=False)
        records.extend(parsed)
        errors.extend(parsed_errors)
    return records, errors


def all_review_records(workspace: Path) -> tuple[list[LogRecord], list[str]]:
    paths, errors = _log_paths(workspace, "reviews", REVIEW_LOG_RE)
    records: list[LogRecord] = []
    for rel in paths:
        parsed, parsed_errors = _parse_log(workspace, rel, review=True)
        records.extend(parsed)
        errors.extend(parsed_errors)
    return records, errors


def validate_workspace(workspace: Path = DEFAULT_WORKSPACE) -> list[str]:
    errors: list[str] = []
    if not (workspace / "README.md").is_file():
        errors.append("missing planning/library-parts/README.md")
    items, item_errors = all_items(workspace)
    errors.extend(item_errors)
    generation, generation_errors = all_generation_records(workspace)
    reviews, review_errors = all_review_records(workspace)
    errors.extend(generation_errors)
    errors.extend(review_errors)

    by_key = {item.key: item for item in items}
    generation_pass: set[tuple[str, str, str]] = set()
    generation_pass_by_log: set[tuple[str, tuple[str, str, str]]] = set()
    for record in generation:
        item = by_key.get(record.key)
        if item is None:
            errors.append(f"{record.path}:{record.line}: generation record does not match a backlog item")
            continue
        if record.result == "PASS":
            generation_pass.add(record.key)
            generation_pass_by_log.add((record.path, record.key))
            if not item.done:
                errors.append(f"{record.path}:{record.line}: PASS generation record requires [x] backlog item")

    for item in items:
        if item.done and item.key not in generation_pass:
            errors.append(f"{item.shard}:{item.line}: [x] item has no matching generation PASS record")

    for record in reviews:
        if record.generation_log is None or not GEN_LOG_RE.fullmatch(record.generation_log):
            errors.append(f"{record.path}:{record.line}: review Generation Log path is invalid")
            continue
        if not (workspace / record.generation_log).is_file():
            errors.append(f"{record.path}:{record.line}: review Generation Log does not exist")
            continue
        if (record.generation_log, record.key) not in generation_pass_by_log:
            errors.append(f"{record.path}:{record.line}: review does not bind a matching generation PASS")

    return errors


def select_next(
    workspace: Path = DEFAULT_WORKSPACE,
    *,
    category: str | None = None,
    limit: int = 1,
) -> list[BacklogItem]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    items, _ = all_items(workspace)
    return [item for item in items if not item.done and (category is None or item.category == category)][:limit]


def progress_rows(workspace: Path = DEFAULT_WORKSPACE) -> list[dict[str, int | str]]:
    items, _ = all_items(workspace)
    order: list[str] = []
    totals: dict[str, list[int]] = {}
    for item in items:
        if item.category not in totals:
            order.append(item.category)
            totals[item.category] = [0, 0]
        totals[item.category][0] += 1
        totals[item.category][1] += int(item.done)
    return [
        {
            "category": category,
            "total": totals[category][0],
            "completed": totals[category][1],
            "remaining": totals[category][0] - totals[category][1],
        }
        for category in order
    ]


def created_for_date(workspace: Path, day: str) -> list[LogRecord]:
    records, _ = all_generation_records(workspace)
    return [record for record in records if record.day == day and record.result == "PASS"]


def review_pending_for_date(workspace: Path, day: str) -> list[LogRecord]:
    created = created_for_date(workspace, day)
    reviews, _ = all_review_records(workspace)
    passed = {
        (record.generation_log, record.key)
        for record in reviews
        if record.result == "PASS" and record.generation_log is not None
    }
    return [record for record in created if (record.path, record.key) not in passed]


def _ensure_valid(workspace: Path) -> None:
    errors = validate_workspace(workspace)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)


def _print_items(items: Iterable[BacklogItem], *, as_json: bool) -> None:
    rows = [
        {
            "backlog": item.shard,
            "line": item.line,
            "target": item.target,
            "partName": item.name,
            "category": item.category,
        }
        for item in items
    ]
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    elif not rows:
        print("No matching unchecked backlog items.")
    else:
        for row in rows:
            print(f"{row['backlog']}:{row['line']} | {row['target']} | {row['partName']}")


def _valid_day(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_WORKSPACE, help="library backlog workspace root")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="validate backlog structure, logs, and completion traceability")

    next_parser = sub.add_parser("next", help="select the next unchecked items in index order")
    next_parser.add_argument("--category")
    next_parser.add_argument("--limit", type=int, default=1)
    next_parser.add_argument("--json", action="store_true")

    progress_parser = sub.add_parser("progress", help="show derived checkbox progress by category")
    progress_parser.add_argument("--json", action="store_true")

    created_parser = sub.add_parser("created", help="list generation PASS records for a date")
    created_parser.add_argument("--date", required=True, type=_valid_day)
    created_parser.add_argument("--json", action="store_true")

    review_parser = sub.add_parser("review-pending", help="list date-created parts without a matching review PASS")
    review_parser.add_argument("--date", required=True, type=_valid_day)
    review_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    workspace = args.root.resolve()
    _ensure_valid(workspace)

    if args.command == "validate":
        shards, _ = backlog_shards(workspace)
        items, _ = all_items(workspace)
        print(f"PASS library backlog workspace: {len(shards)} shards, {len(items)} items")
        return 0
    if args.command == "next":
        _print_items(select_next(workspace, category=args.category, limit=args.limit), as_json=args.json)
        return 0
    if args.command == "progress":
        rows = progress_rows(workspace)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print("| Category | Total | Completed | Remaining |")
            print("|---|---:|---:|---:|")
            for row in rows:
                print(f"| {row['category']} | {row['total']} | {row['completed']} | {row['remaining']} |")
        return 0
    if args.command in {"created", "review-pending"}:
        records = (
            created_for_date(workspace, args.date)
            if args.command == "created"
            else review_pending_for_date(workspace, args.date)
        )
        payload = [
            {
                "generationLog": record.path,
                "backlog": record.backlog,
                "target": record.target,
                "partName": record.name,
            }
            for record in records
        ]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif not payload:
            print("No matching records.")
        else:
            for row in payload:
                print(f"{row['generationLog']} | {row['backlog']} | {row['target']} | {row['partName']}")
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())

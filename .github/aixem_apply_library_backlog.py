#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{rel}: expected one replacement anchor, found {count}: {old[:100]!r}")
    write(rel, text.replace(old, new, 1))


def refresh_estimated_tokens(rel: str) -> None:
    text = read(rel)
    marker = text.find("\n---\n", 4)
    if not text.startswith("---\n") or marker < 0:
        raise RuntimeError(f"{rel}: canonical front matter not found")
    body = text[marker + 5 :]
    estimate = max(1, (len(body.encode("utf-8")) + 3) // 4)
    updated, count = re.subn(
        r"(?m)^  estimated_tokens: [0-9]+$",
        f"  estimated_tokens: {estimate}",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"{rel}: estimated_tokens field not found exactly once")
    write(rel, updated)


# Repository operating guidance.
replace_once(
    "AGENTS.md",
    "For common authoring operations, start at [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md), select one task guide, and then follow its authored route and canonical references. New reusable component/symbol artifacts belong below `project-root/library/<electronics|architecture>/`; do not create ordinary reusable parts under `examples/`.\n\nUse the active route.",
    "For common authoring operations, start at [`docs/authoring/guides/index.md`](docs/authoring/guides/index.md), select one task guide, and then follow its authored route and canonical references. New reusable component/symbol artifacts belong below `project-root/library/<electronics|architecture>/`; do not create ordinary reusable parts under `examples/`.\n\n### Library-Part Backlog Wrapper\n\nWhen a request consumes queued library-part work, first read [`planning/library-parts/README.md`](planning/library-parts/README.md). Validate the queue with `python tools/library_backlog.py validate`, select only the requested number of unchecked items with `python tools/library_backlog.py next`, and then run the normal `create-symbol` route independently for each selected item. The queue supplies only target folder and part name; it never supplies component ID, pins, provenance, electrical semantics, geometry, or readiness evidence.\n\nClose a queued item atomically: successful required part-creation validation -> append a dated `PASS` generation record -> change that one checkbox to `[x]` -> add the new dated log link to the workspace index when needed. A failed attempt appends `FAIL` and leaves the item unchecked. Independent review uses the dated generation record and writes a separate review log; `[x]` is workflow completion state, not semantic-review authority. Parallel Agents must operate on disjoint shards or be externally serialized.\n\nUse the active route.",
)

replace_once(
    "REFERENCE.md",
    "- Implementation intent: [`planning/README.md`](planning/README.md)\n- Historical plan registry: [`planning/index.yaml`](planning/index.yaml)",
    "- Implementation intent: [`planning/README.md`](planning/README.md)\n- Operational library-part authoring queue: [`planning/library-parts/README.md`](planning/library-parts/README.md) — mutable scheduling, generation-log, and review-log state that never replaces production-library authority.\n- Historical plan registry: [`planning/index.yaml`](planning/index.yaml)",
)

replace_once(
    "planning/README.md",
    "This directory preserves release-scoped implementation intent. Plans explain why and how a change was proposed; they are historical records and never override current canonical technical documentation under `docs/`.\n\nThe machine-readable lifecycle owner is [`index.yaml`](index.yaml). Completed plans are read-only except for explicit errata that preserve the original decision record.\n",
    "This directory preserves noncanonical planning state. Release-scoped implementation plans explain why and how a change was proposed; operational authoring queues coordinate future work. Neither class overrides current canonical technical documentation under `docs/` or authoritative production artifacts.\n\nThe machine-readable lifecycle owner for release plans is [`index.yaml`](index.yaml). Completed release plans are read-only except for explicit errata that preserve the original decision record. Operational queue lifecycle and discoverability are owned by their local workspace.\n\n## Operational Authoring Queue\n\n- [Library Part Authoring Backlog](library-parts/README.md) — isolated Markdown queue for bounded AI part creation, dated generation history, and independent review. Its checkboxes and logs are workflow state only; actual `.aixlib.json` / `.aixsym.json` content and canonical review evidence remain authoritative.\n",
)

# Add repository document roles for the operational queue.
replace_once(
    "docs/_meta/repository-document-policy.yaml",
    "- id: implementation-plan\n  lifecycle: historical\n  status: immutable\n  humanAuthored: true\n  discoverabilityOwner: planning/index.yaml\n  include:\n  - planning/releases/*/*.md\n",
    "- id: library-authoring-workspace-entrypoint\n  lifecycle: current\n  status: active\n  humanAuthored: true\n  discoverabilityOwner: planning/README.md\n  include:\n  - planning/library-parts/README.md\n  allowedFilenames:\n  - README.md\n- id: library-authoring-backlog-index\n  lifecycle: current\n  status: active\n  humanAuthored: true\n  discoverabilityOwner: planning/library-parts/README.md\n  include:\n  - planning/library-parts/index.md\n  allowedFilenames:\n  - index.md\n- id: library-authoring-backlog-shard\n  lifecycle: current\n  status: active\n  humanAuthored: true\n  discoverabilityOwner: planning/library-parts/index.md\n  include:\n  - planning/library-parts/backlog/*/*.md\n- id: library-authoring-generation-log\n  lifecycle: historical\n  status: retained\n  humanAuthored: true\n  discoverabilityOwner: planning/library-parts/index.md\n  include:\n  - planning/library-parts/logs/*/*.md\n- id: library-authoring-review-log\n  lifecycle: historical\n  status: retained\n  humanAuthored: true\n  discoverabilityOwner: planning/library-parts/index.md\n  include:\n  - planning/library-parts/reviews/*/*.md\n- id: library-authoring-progress-report\n  lifecycle: generated\n  status: generated\n  humanAuthored: false\n  discoverabilityOwner: tools/library_backlog.py\n  include:\n  - planning/library-parts/reports/*.md\n- id: implementation-plan\n  lifecycle: historical\n  status: immutable\n  humanAuthored: true\n  discoverabilityOwner: planning/index.yaml\n  include:\n  - planning/releases/*/*.md\n",
)

# Keep canonical document-governance truth aligned with the new declared roles.
replace_once(
    "docs/specifications/documentation/document-governance-contract.md",
    "| Implementation plan | Version-scoped historical intent under `planning/releases/`. |\n| Validation release index/report | Version-scoped immutable human evidence under `validation/releases/`. |",
    "| Implementation plan | Version-scoped historical intent under `planning/releases/`. |\n| Library authoring workspace/backlog | Mutable operational scheduling under `planning/library-parts/`; generation and review logs are retained history, and none of these files are component or semantic authority. |\n| Validation release index/report | Version-scoped immutable human evidence under `validation/releases/`. |",
)
replace_once(
    "docs/specifications/documentation/document-governance-contract.md",
    "- plans are registered in `planning/index.yaml` and linked from `planning/README.md`;\n- human validation reports are linked from their release `README.md`;",
    "- plans are registered in `planning/index.yaml` and linked from `planning/README.md`;\n- the library-authoring workspace is linked from `planning/README.md`, and `planning/library-parts/index.md` links every current backlog shard plus every created dated generation/review log;\n- human validation reports are linked from their release `README.md`;",
)

# Define the non-authoritative queue boundary in the existing library contract.
replace_once(
    "docs/specifications/components/library-layout-contract.md",
    "A path assists retrieval. It never replaces the IDs and digests inside the authoritative files. Symbol provenance describes the graphic asset; it does not independently prove the pinout of each component that uses that asset.\n\n## Canonical Authoring Root",
    "A path assists retrieval. It never replaces the IDs and digests inside the authoritative files. Symbol provenance describes the graphic asset; it does not independently prove the pinout of each component that uses that asset.\n\n## Operational Backlog Boundary\n\n`planning/library-parts/` is permitted as noncanonical operational scheduling state for future reusable-part work. A backlog entry contains only a target folder and a human-readable part name. It does not define component IDs, endpoint inventories, provenance, properties, electrical semantics, symbol geometry, or readiness.\n\nA checked backlog item means the required part-creation workflow completed successfully and a matching generation `PASS` record exists. That checkbox is never a substitute for authoritative `.aixlib.json` / `.aixsym.json` content or source-bound semantic review evidence. A failed attempt remains unchecked and is retained as a `FAIL` generation record. Independent review is recorded separately and may later fail even when the original creation transaction passed.\n\nWhen queued work is selected, normal authoring starts from this contract: resolve provenance, semantic identity, ports, presentation, binding, digests, and separated validation claims from authoritative evidence. If an equivalent valid production part already exists, validate that exact identity and target before closing the queue item; do not manufacture a duplicate merely to satisfy a checkbox.\n\n## Canonical Authoring Root",
)
replace_once(
    "docs/specifications/components/library-layout-contract.md",
    "## Authoring and Validation Procedure\n\n1. Resolve the active project or authoring root.",
    "## Authoring and Validation Procedure\n\nFor backlog-driven work, validate the operational queue and select only the requested unchecked item set before entering this procedure. Queue text narrows requested scope but never supplies semantic truth.\n\n1. Resolve the active project or authoring root.",
)

# Make the existing create-library-part guide the bounded execution façade for queue items.
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "Use it for a new resistor class, sourced MCU, connector family, architectural symbol, or reusable component presentation. Use [Select a Library Part](select-library-part.md) when a suitable component already exists. Do not use this guide to edit generated SVG, Viewer, evidence, or corpus output directly.",
    "Use it for a new resistor class, sourced MCU, connector family, architectural symbol, or reusable component presentation. When the request originates from `planning/library-parts/`, first validate/select the bounded queue item as defined by that workspace; its target folder and part name are request scope only. Use [Select a Library Part](select-library-part.md) when a suitable component already exists. Do not use this guide to edit generated SVG, Viewer, evidence, or corpus output directly.",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "- active project or authoring root;\n- requested functional identity and domain;",
    "- active project or authoring root;\n- optional originating backlog shard/item when executing queued production work;\n- requested functional identity and domain;",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "## 9. Short Execution Sequence\n\n1. Resolve the project root and inspect the selected domain subtree for an existing accurate namespace.",
    "## 9. Short Execution Sequence\n\nFor queued work, first run `python tools/library_backlog.py validate` and select only the requested count with `python tools/library_backlog.py next` (optionally scoped by category). Never infer pins, IDs, or provenance from the queue line.\n\n1. Resolve the project root and inspect the selected domain subtree for an existing accurate namespace.",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "9. Record part semantic review separately from structural render. A placeholder remains non-semantic-ready.\n\n## 10. Canonical Reference Table",
    "9. Record part semantic review separately from structural render. A placeholder remains non-semantic-ready.\n10. For queued work only, append the dated generation result. On `PASS`, mark exactly that backlog item `[x]`; on `FAIL`, leave it unchecked. If a dated log file is created, link it from `planning/library-parts/index.md` in the same change.\n\n## 10. Canonical Reference Table",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "- `python tools/validate_authoring_integrity.py <library-file> --artifact-path <project-relative-path> --operation added`",
    "- `python tools/library_backlog.py validate` when work originates from the operational queue\n- `python tools/validate_authoring_integrity.py <library-file> --artifact-path <project-relative-path> --operation added`",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "The new files are canonical and digest-locked; the component has a complete semantic contract; all required ports map to visible symbol endpoints; the symbol follows the active sizing rhythm; structural result and part semantic result are explicit; any placeholder remains `semanticReady=false`.",
    "The new files are canonical and digest-locked; the component has a complete semantic contract; all required ports map to visible symbol endpoints; the symbol follows the active sizing rhythm; structural result and part semantic result are explicit; any placeholder remains `semanticReady=false`. For queued work, completion additionally requires a matching dated generation `PASS` record and exactly one corresponding `[x]` backlog mutation.",
)
replace_once(
    "docs/authoring/guides/create-library-part.md",
    "Retain authoritative library and symbol files, digest changes, validator outputs, deterministic render evidence, source-bound part review, placeholder state where applicable, and circuit-intent review only when the part is actually used in a schematic.",
    "Retain authoritative library and symbol files, digest changes, validator outputs, deterministic render evidence, source-bound part review, placeholder state where applicable, and circuit-intent review only when the part is actually used in a schematic. A queue generation log is operational history and never replaces those technical evidence layers.",
)

# Do not duplicate guide links; broaden the existing guide-index row instead.
replace_once(
    "docs/authoring/guides/index.md",
    "| create or repair a reusable component and symbol | [Create a Library Part](create-library-part.md) | `create-symbol` |",
    "| create or repair a reusable component and symbol, including a queued backlog item | [Create a Library Part](create-library-part.md) | `create-symbol` |",
)

# Current-release narrative and chronological summary.
replace_once(
    "docs/releases/0.5.9.md",
    "## Grid, Symbol Sizing, and Placement",
    "## Scalable Library-Part Production Queue\n\n- Added an operational `planning/library-parts/` workspace that is explicitly isolated from production `library/` authority.\n- Added minimal Markdown checkbox items containing only target folder and part name, fixed three-digit category shards, and a 100-item shard ceiling for bounded Agent context.\n- Added deterministic queue validation, next-item selection, category progress, date-created enumeration, and review-pending inspection through `tools/library_backlog.py`.\n- Added dated generation logs and separate independent review logs so a specific day's successful work can be re-opened and checked without relying on conversation history.\n- Queue completion never promotes semantic claims: each selected item still executes the normal provenance, semantic, symbol, binding, render, and separated-validation workflow.\n\n## Grid, Symbol Sizing, and Placement",
)
replace_once(
    "CHANGELOG.md",
    "- Added canonical `library/<electronics|architecture>/...` authoring paths with lower-kebab naming, new-vs-existing compatibility, and Agent Change-Set enforcement.\n",
    "- Added canonical `library/<electronics|architecture>/...` authoring paths with lower-kebab naming, new-vs-existing compatibility, and Agent Change-Set enforcement.\n- Added an isolated Markdown library-part production backlog with numbered shards, deterministic Agent selection/progress commands, dated generation/review logs, and fail-closed completion semantics.\n",
)

# Operational workspace. No actual part entries are invented by this infrastructure change.
write(
    "planning/library-parts/README.md",
    """# Library Part Authoring Backlog

This workspace is the mutable operational queue for large-scale AIXEM reusable-part production. It is intentionally isolated from the production `library/` tree.

Current technical authority remains in canonical documentation and the actual `.aixlib.json`, `.aixsym.json`, project locks, and review evidence. A checkbox or log entry here never defines pins, provenance, electrical semantics, geometry, or semantic readiness.

## 1. Start Here

1. Read this file.
2. Open [`index.md`](index.md).
3. Run `python tools/library_backlog.py validate`.
4. Select bounded work with `python tools/library_backlog.py next --limit <N>`; add `--category <name>` when the request names a category.
5. For each selected item, execute the canonical [Create a Library Part](../../docs/authoring/guides/create-library-part.md) procedure and its `create-symbol` route.
6. Record the attempt in the date-scoped generation log.
7. Mark the item `[x]` only after required creation validation passes.

The canonical reusable-part boundary remains the [Library Layout and Part Integrity Contract](../../docs/specifications/components/library-layout-contract.md).

## 2. Workspace Layout

```text
planning/library-parts/
├── README.md
├── index.md
├── backlog/
│   └── <category>/
│       ├── 001.md
│       ├── 002.md
│       └── ...
├── logs/
│   └── YYYY/
│       └── YYYY-MM-DD.md
├── reviews/
│   └── YYYY/
│       └── YYYY-MM-DD.md
└── reports/
    └── progress.md        # optional generated output
```

Git does not retain empty directories. `logs/`, `reviews/`, and `reports/` appear only when a real record or generated report exists.

## 3. Backlog Item Grammar

A backlog entry contains exactly the target folder and part name:

```text
- [ ] `library/electronics/<semantic-folder>` — <Part Name>
```

or:

```text
- [ ] `library/architecture/<semantic-folder>` — <Part Name>
```

Do not add component IDs, pinouts, source URIs, package data, symbol geometry, electrical attributes, implementation notes, or status prose to the item line. Those facts are resolved by the normal authoring workflow from authoritative evidence.

The target is a folder, not a filename. Every target segment below `library/electronics` or `library/architecture` uses lower-kebab case.

## 4. Checkbox Semantics

- `[ ]` — no successfully completed creation transaction is recorded yet.
- `[x]` — the required creation workflow passed and at least one matching generation `PASS` record exists.

Creating a file, rendering an SVG, or attempting authoring is not enough to check an item. A failed attempt stays `[ ]` and is retained in the generation log.

A later independent review may fail without rewriting the historical fact that the original creation transaction passed. Repair and re-review are separate operations.

## 5. Sharding Rule

Backlog files use:

```text
backlog/<lower-kebab-category>/<NNN>.md
```

`NNN` is a fixed three-digit sequence beginning at `001`. Each shard may contain at most **100** backlog items. Create the next numbered shard before an existing shard would exceed that limit.

The order of backlog links in [`index.md`](index.md) defines deterministic global work priority. Item order inside each shard defines priority within that shard.

When a new shard is created, link it from `index.md` in the same change.

## 6. Generation Log

Every creation attempt is appended to:

```text
logs/YYYY/YYYY-MM-DD.md
```

Required format:

```markdown
# Library Part Generation Log — 2026-08-14

## Resistor IEC

- Backlog: `backlog/passive/001.md`
- Target: `library/electronics/passive/resistors`
- Result: PASS
```

A failed attempt uses `Result: FAIL` and may add `- Note: ...`.

Generation logs are retained history. Do not rewrite a prior failed attempt merely because a later attempt passes. When a date log is first created, link it from `index.md` in the same change.

## 7. Independent Review Log

A review is separate from creation. Review a date's successful creation set with:

```bash
python tools/library_backlog.py created --date YYYY-MM-DD
python tools/library_backlog.py review-pending --date YYYY-MM-DD
```

Write review results to:

```text
reviews/YYYY/YYYY-MM-DD.md
```

Required format:

```markdown
# Library Part Review Log — 2026-08-14

## Resistor IEC

- Generation Log: `logs/2026/2026-08-14.md`
- Backlog: `backlog/passive/001.md`
- Target: `library/electronics/passive/resistors`
- Result: PASS
```

A review failure uses `Result: FAIL` and may add `- Reason: ...`. `review-pending` treats an item as closed only after a matching review `PASS` exists.

When a review log is first created, link it from `index.md` in the same change.

## 8. Existing-Part and Duplicate Rule

Before creating a selected item, inspect the target production namespace for an equivalent valid part. If the intended part already exists, validate that exact identity, presentation binding, provenance status, and target relationship. A validated existing part may close the queue item with a generation `PASS` record; do not mint a duplicate identity just to satisfy the checklist.

## 9. Agent Transaction

For each selected item:

```text
validate queue
-> select bounded unchecked item
-> inspect production namespace / prevent duplicate
-> execute create-symbol authoring route
-> run required part validation
-> append generation PASS or FAIL
-> PASS only: mark exactly that item [x]
-> validate queue again
```

Do not batch-mark checkboxes before individual validation. Do not infer semantic facts from neighboring backlog entries.

## 10. Parallel Agents

This Markdown queue is intentionally simple and does not implement a distributed lock. Parallel Agents must either:

- be assigned disjoint shards, or
- be externally serialized by the caller/orchestrator.

Two Agents must not mutate the same shard concurrently. Re-read the shard immediately before closing an item so an externally completed checkbox is not overwritten.

## 11. Commands

```bash
python tools/library_backlog.py validate
python tools/library_backlog.py next --limit 1
python tools/library_backlog.py next --category passive --limit 10
python tools/library_backlog.py progress
python tools/library_backlog.py created --date 2026-08-14
python tools/library_backlog.py review-pending --date 2026-08-14
```

`progress` is derived information. Backlog checkboxes remain the operational completion state.

## 12. Initial Scaffold

The initial category shards are empty intentionally. This infrastructure change does not invent a production part list. Populate backlog lines only from an explicit cataloging task, then process them incrementally through this contract.
""",
)

write(
    "planning/library-parts/index.md",
    """# Library Part Backlog Index

This index is the discovery and priority owner for the operational library-part queue. See [README.md](README.md) for execution rules.

## Backlog Shards

Process shards in this listed order unless the caller explicitly narrows the category or shard.

| Category | Shard |
|---|---|
| Passive | [passive/001.md](backlog/passive/001.md) |
| Diodes | [diodes/001.md](backlog/diodes/001.md) |
| Transistors | [transistors/001.md](backlog/transistors/001.md) |
| Analog | [analog/001.md](backlog/analog/001.md) |
| Logic | [logic/001.md](backlog/logic/001.md) |
| Connectors | [connectors/001.md](backlog/connectors/001.md) |
| Microcontrollers | [microcontrollers/001.md](backlog/microcontrollers/001.md) |
| FPGA | [fpga/001.md](backlog/fpga/001.md) |
| Electromechanical | [electromechanical/001.md](backlog/electromechanical/001.md) |

## Generation Logs

No generation logs have been created yet. Add each real `logs/YYYY/YYYY-MM-DD.md` file here in the same change that creates it.

## Review Logs

No review logs have been created yet. Add each real `reviews/YYYY/YYYY-MM-DD.md` file here in the same change that creates it.

## Generated Reports

No generated progress report is retained initially. Use `python tools/library_backlog.py progress` for the current derived summary.
""",
)

categories = {
    "passive": "Passive",
    "diodes": "Diodes",
    "transistors": "Transistors",
    "analog": "Analog",
    "logic": "Logic",
    "connectors": "Connectors",
    "microcontrollers": "Microcontrollers",
    "fpga": "FPGA",
    "electromechanical": "Electromechanical",
}
for slug, title in categories.items():
    write(
        f"planning/library-parts/backlog/{slug}/001.md",
        f"# {title} — 001\n\n<!-- Entries only: - [ ] `library/electronics/<folder>` — <Part Name> -->\n",
    )

# Deterministic queue helper. Standard-library only so it remains available before release dependencies are installed.
write(
    "tools/library_backlog.py",
    r'''#!/usr/bin/env python3
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
''',
)

write(
    "tests/docs/test_library_backlog.py",
    r'''"""Regression tests for the isolated library-part authoring backlog."""
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
''',
)

# Canonical token estimates are deterministic body byte counts / 4.
for canonical in (
    "docs/specifications/documentation/document-governance-contract.md",
    "docs/specifications/components/library-layout-contract.md",
    "docs/authoring/guides/create-library-part.md",
    "docs/authoring/guides/index.md",
    "docs/releases/0.5.9.md",
):
    refresh_estimated_tokens(canonical)

print("Applied library-part authoring backlog implementation.")

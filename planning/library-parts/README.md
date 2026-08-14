# Library Part Authoring Backlog

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

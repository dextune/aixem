# L004 — Parameterized variant instance

Repair the invalid placement selection by using the existing IEC variant for R2 with body-height 12.5. Do not alter the reusable symbol, component library, or semantic source.

## Supplied facts

- **entity:** `"R2"`
- **variant:** `"iec"`
- **parameters:** `{"body-height": 12.5}`
- **precedence:** `"placement overrides variant defaults"`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

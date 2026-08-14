# L010 — Off-grid non-orthogonal route

Repair the non-orthogonal route using grid-aligned layout geometry. Do not change semantic net membership or component presentation.

## Supplied facts

- **diagnostic:** `"AIXEM-DIAG-ROUTE-NON-ORTHOGONAL"`
- **gridMm:** `2.5`
- **net:** `"signal"`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

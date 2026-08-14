# L009 — Correct-looking route on wrong semantic net

Remove the contradictory semantic membership misbound_l009 while preserving the valid signal net and existing layout geometry.

## Supplied facts

- **diagnostic:** `"AIXEM-DIAG-SEMANTIC-NET-CLOSURE"`
- **validNet:** `"signal"`
- **invalidNet:** `"misbound_l009"`
- **members:** `["T1.1", "T2.1"]`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

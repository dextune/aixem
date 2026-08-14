# L011 — Duplicate project-net member

Remove the duplicated project-net member without changing any leaf circuit, sheet layout, or other project-net membership.

## Supplied facts

- **diagnostic:** `"AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER"`
- **projectNet:** `"vcc_5v"`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

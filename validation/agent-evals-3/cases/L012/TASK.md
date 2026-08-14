# L012 — Field and body overlap

Move reference and value fields outside the body according to the symbol design profile. Preserve all endpoint semantics and route geometry.

## Supplied facts

- **diagnostic:** `"AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP"`
- **fields:** `["reference", "value"]`
- **symbol:** `"library/electronics/authoring/repaired-resistor.aixsym.json"`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

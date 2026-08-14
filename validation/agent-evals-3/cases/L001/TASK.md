# L001 — New two-pin passive

Create the missing two-pin passive symbol and presentation binding for the supplied RX41/RX42 divider skeleton. Preserve the supplied semantic endpoint intent.

## Supplied facts

- **componentType:** `"live:resistor-l001"`
- **ports:** `["1", "2"]`
- **references:** `["RX41", "RX42"]`
- **values:** `["13k", "47k"]`
- **semanticNet:** `"synth_link_41"`
- **gridMm:** `2.5`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

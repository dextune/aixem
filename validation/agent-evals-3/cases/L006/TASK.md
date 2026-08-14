# L006 — Two-sheet hierarchical composition

Create the three missing explicit project nets for the existing power and control leaf sheets. Use the supplied interface memberships; never connect by equal names or geometry.

## Supplied facts

- **projectNets:** `{"rail_live_56": ["power@VCC", "control@VCC"], "return_live_56": ["power@GND", "control@GND"], "command_live_56": ["power@OUT", "control@IN"]}`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

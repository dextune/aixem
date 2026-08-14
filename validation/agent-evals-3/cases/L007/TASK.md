# L007 — Same-name local nets

Add only the explicit common_return_77 project net between alpha.GND and beta.GND. Keep the same-name local vcc nets namespace-isolated and do not create a VCC project net.

## Supplied facts

- **projectNet:** `"common_return_77"`
- **members:** `["alpha@GND", "beta@GND"]`
- **mustRemainLocal:** `["alpha:vcc", "beta:vcc"]`

## Required closure

- Use AGENTS.md and the compiled route packet before editing.
- Edit only the authoritative files allowed by the active route.
- Run prepare, check, authority-local repair, and close.
- Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.

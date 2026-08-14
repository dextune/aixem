# AIXEM 0.4 Migration Records

This directory contains audit records for the exact AIXEM 0.4 archive used by the 0.5 migration.

- `0.4-inventory.json` and `.csv` record every baseline path, byte count, extension, digest, and language-scan result.
- `0.4-migration-map.json` and `.csv` assign each baseline path exactly one disposition, target set, canonical document identity, and rationale.
- `0.4-declared-artifact-audit.json` records paths declared by the 0.4 reference root, including historical omissions and their 0.5 resolution.

These are provenance and compatibility records. Canonical 0.5 rules remain under `docs/`; the generated `reference/` tree is a compatibility product rather than an independent authority.

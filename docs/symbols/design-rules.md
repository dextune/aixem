---
id: AIXEM-SYMBOL-DESIGN-RULES-001
title: Symbol Design Rules Entry Point
status: informative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Provides a short route-friendly entry point to the normative symbol design profile and its mechanical checks.
authority:
- symbol-design-guidance
aliases:
- symbol design rules
- symbol grid rules
- pin lead rules
agent:
  priority: high
  estimated_tokens: 312
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-SPEC-SYMBOL-DESIGN-001
related:
- AIXEM-SYMBOL-LINT-001
navigation:
  group: symbols
  order: 44
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Symbol Design Rules Entry Point

The normative rules are owned by the [Symbol Design Profile](../specifications/symbols/symbol-design-profile.md). Use this page as a compact preflight.

## Required Construction Rules

- Put electrical port coordinates on the active 2.5 mm authoring grid.
- Use a 5 mm visible pin lead unless an approved profile says otherwise.
- Use 5 mm pin pitch for standard repeated pin groups.
- Make the visible lead endpoint coincide exactly with its electrical port.
- Keep reference and value fields outside body geometry.
- Group multi-pin devices by engineering function and preserve ordinary left-to-right signal flow.
- Prefer simple lines, rectangles, circles, arcs, and text over decorative compound paths.
- Keep graphics, semantics, and layout ownership separate.

## Mechanical Check

Run:

```bash
python tools/docs/authoring_validation.py
```

The validator checks schema coverage, executable snippets, authoring examples, grid-aligned ports, lead/port coincidence, binding totality, renderer precedence, and deterministic golden renders.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

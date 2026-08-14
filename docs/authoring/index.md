---
id: AIXEM-AUTHORING-INDEX-001
title: Authoring
status: informative
version: '1.0'
language: en
domain: authoring
kind: index
summary: Provides the shortest official path from a component contract to a drawn, routed, rendered, inspected, and validated AIXEM schematic.
authority:
- authoring-navigation
aliases:
- authoring
- drawing manual
- create component circuit
agent:
  priority: critical
  estimated_tokens: 698
  intents:
  - create-symbol
  - create-schematic
  - route-nets
  - render-review
  - author-component-circuit
depends_on:
- AIXEM-AGENT-AUTHORING-001
related:
- AIXEM-SPEC-RENDERER-001
- AIXEM-SPEC-SYMBOL-DESIGN-001
navigation:
  group: authoring
  order: 0
artifacts:
  owns: []
  consumes:
  - docs/_meta/generated/task-packets/
requirements: []
---

# Authoring

Use this section when the task is to create or repair actual AIXEM drawing artifacts. Start with `AGENTS.md`, resolve the task route, then read only the listed canonical sections.

For a direct job-oriented entrypoint, open the [Task-Oriented Authoring Guides](guides/index.md). It selects one compact task guide before the authored route, generated packet, and canonical owners.

## Create a Component Symbol

Follow the [Symbol Authoring Cookbook](../symbols/symbol-authoring-cookbook.md), then use the [AIXSYM Field Reference](../symbols/aixsym-field-reference.md) and [Component to Symbol Binding](../symbols/component-symbol-binding.md) for exact serialization and mapping.

## Create a Schematic

Use the [Schematic Authoring Cookbook](../schematic/schematic-authoring-cookbook.md) to keep `.aixem` semantic facts separate from `.aixlayout.json` placement and route geometry.

## Route Nets

Use the [Routing Cookbook](../routing/routing-cookbook.md) for straight, bent, multi-terminal, junction, and crossing patterns.

## Render and Review

Use the [Visual QA and Repair Loop](../agent/visual-qa-loop.md). Inspect validation data, `resolved-scene.json`, SVG, and workbench output before editing the authoritative owner.

## Troubleshooting

Use [Symbol Lint](../symbols/symbol-lint.md) for schema, grid, lead/port, field, mapping, and deterministic-render diagnostics. For precedence or renderer failures, consult the [Renderer Contract](../specifications/renderer/renderer-contract.md).

## End-to-End Route

```text
create-symbol
→ create-schematic
→ route-nets
→ render-review
→ validate-project
```

The compiled route is `author-component-circuit`; its compact derived packet is `docs/_meta/generated/task-packets/author-component-circuit.json`.

## Complete Section Map

This list is the complete authored link surface for the `authoring` navigation section. The navigation registry remains the machine-readable membership owner.

- [Symbol Authoring Cookbook](../symbols/symbol-authoring-cookbook.md) — `AIXEM-SYMBOL-COOKBOOK-001`
- [AIXSYM Field Reference](../symbols/aixsym-field-reference.md) — `AIXEM-SYMBOL-AIXSYM-REF-001`
- [Component to Symbol Binding](../symbols/component-symbol-binding.md) — `AIXEM-SYMBOL-BINDING-001`
- [Schematic Authoring Cookbook](../schematic/schematic-authoring-cookbook.md) — `AIXEM-SCHEM-COOKBOOK-001`
- [Routing Cookbook](../routing/routing-cookbook.md) — `AIXEM-ROUTE-COOKBOOK-001`
- [Visual QA and Repair Loop](../agent/visual-qa-loop.md) — `AIXEM-AGENT-VISUAL-QA-001`
- [Symbol Lint](../symbols/symbol-lint.md) — `AIXEM-SYMBOL-LINT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

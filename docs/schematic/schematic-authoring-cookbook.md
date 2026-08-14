---
id: AIXEM-SCHEM-COOKBOOK-001
title: Schematic Authoring Cookbook
status: informative
version: '1.0'
language: en
domain: schematic
kind: cookbook
summary: Shows how to author semantic entities and nets separately from placements and route geometry using complete executable examples.
authority:
- schematic-authoring-recipes
aliases:
- schematic cookbook
- create circuit recipe
- aixem layout recipe
agent:
  priority: critical
  estimated_tokens: 1102
  intents:
  - create-schematic
  - author-component-circuit
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-SYMBOL-BINDING-001
- AIXEM-FORMAT-AIXEM-001
- AIXEM-FORMAT-AIXLAYOUT-001
related:
- AIXEM-ROUTE-COOKBOOK-001
- AIXEM-AGENT-VISUAL-QA-001
navigation:
  group: schematic
  order: 15
artifacts:
  owns: []
  consumes:
  - examples/authoring/
requirements: []
---

# Schematic Authoring Cookbook

A schematic project has two independent but linked authoring sources:

```text
.aixem            owns entities, semantic endpoint membership, nets, no-connect intent
.aixlayout.json   owns placement, orientation, route paths, junction markers, labels
```

Coincident geometry never creates semantic connectivity, and layout must not redefine a net.

## End-to-End Sequence

1. Resolve each component type from a locked `.aixlib.json` library.
2. Create every semantic entity in `.aixem` and assign its component `type`.
3. Add entity attributes used by `fieldMap` or renderer identity fields.
4. Declare each net as explicit endpoint membership.
5. Declare every deliberate no-connect with `noconn`.
6. Add exactly one placement for each semantic entity.
7. Select optional placement `variant`, `parameters`, and `fields` overrides.
8. Add one layout connection record for every semantic net.
9. Route every semantic endpoint at least once and add explicit junction coordinates where branches connect.
10. Lock source, layout, library, and symbol digests in the project manifest.
11. Render, inspect, and validate.

## Minimal Semantic Source

```aixem
aixem 1.0
model two_pin_passive title="Two-pin passive"
feature component.graphics@1 required=true
feature explicit.layout@1 required=true

component R1 type=authoring:resistor refdes=R1 value=10k
component R2 type=authoring:resistor refdes=R2 value=22k

net link = R1.2 R2.1

noconn R1.1
noconn R2.2
```

The semantic file does not contain X/Y positions or bend points.

## Placement and Route Geometry

A placement may choose `variant`, `parameters`, and displayed `fields` without changing semantic identity. Route endpoints refer to semantic endpoint names, while `via` contains only geometric bend points.

<!-- aixem-snippet: examples/authoring/06-two-terminal-route/two_terminal_route.aixlayout.json#/layout/connections/0 -->
```json
{
  "labels": [
    {
      "text": "SIGNAL",
      "x": 82.5,
      "y": 32.5
    }
  ],
  "layer": "connections",
  "net": "signal",
  "paths": [
    {
      "from": {
        "endpoint": "T1.1"
      },
      "to": {
        "endpoint": "T2.1"
      },
      "via": [
        [
          80,
          35
        ],
        [
          80,
          60
        ]
      ]
    }
  ],
  "style": "signal"
}
```
<!-- /aixem-snippet -->

## Semantic and Layout Responsibility Table

| Fact | `.aixem` | `.aixlayout.json` |
|---|---:|---:|
| Component/entity identity | owns | references |
| Component type | owns | does not redefine |
| Net membership | owns | references net name |
| No-connect intent | owns | may display derived mark |
| Instance X/Y and rotation | no | owns |
| Variant/parameter/field instance override | no | owns presentation override |
| Wire bends and labels | no | owns |
| Electrical branch connection | owns endpoint membership | shows explicit junction geometry |

## Complete Multi-Component Pattern

For each net, create one semantic statement and one layout connection object. A two-terminal path may connect endpoint to endpoint directly. A multi-terminal path normally uses point endpoints and an explicit junction so all branches share one visible coordinate.

Do not encode an accidental crossing as a semantic connection. Do not add a junction marker to make two different semantic nets appear joined.

## Validation Checkpoints

- Every entity type resolves through a loaded library.
- Every semantic endpoint exists in the component port contract.
- No endpoint occurs in more than one semantic net or in both a net and `noconn`.
- Placement keys exactly close over semantic entities.
- Layout connections exactly close over semantic nets.
- Every route endpoint belongs to the named semantic net.
- All free bends are grid-aligned and every segment is orthogonal.
- Project and asset digests match.
- Rendered evidence contains the expected entities, ports, nets, paths, and junctions.

## Handoff to Routing

When entities, types, semantic nets, and placements are stable, continue with the [Routing Cookbook](../routing/routing-cookbook.md). Routing is a geometry stage and must preserve the semantic source unchanged unless a genuine connectivity correction is required.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

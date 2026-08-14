---
id: AIXEM-ROUTE-COOKBOOK-001
title: Routing Cookbook
status: informative
version: '1.0'
language: en
domain: routing
kind: cookbook
summary: Provides executable orthogonal routing patterns for two-terminal, multi-bend, multi-terminal, crossing,
  and junction cases.
authority:
- routing-recipes
aliases:
- routing cookbook
- wire recipes
- explicit junction examples
agent:
  priority: critical
  estimated_tokens: 1354
  intents:
  - route-nets
  - create-schematic
  - author-component-circuit
  - route-project-nets
depends_on:
- AIXEM-ROUTE-NETS-001
- AIXEM-ROUTE-CROSSING-001
- AIXEM-FORMAT-AIXLAYOUT-001
related:
- AIXEM-SCHEM-COOKBOOK-001
- AIXEM-AGENT-ROUTING-001
- AIXEM-CONCEPT-PROJECT-NET-001
navigation:
  group: routing
  order: 15
artifacts:
  owns: []
  consumes:
  - examples/authoring/06-two-terminal-route/
  - examples/authoring/07-multi-terminal-junction/
requirements: []
---

# Routing Cookbook

Routing materializes semantic net membership as readable orthogonal geometry. The semantic net must already exist. A route is never permission to infer, merge, split, or rename connectivity.

## Straight Two-Terminal Route

Use one path whose `from` and `to` directly name the two semantic endpoints. Omit `via` when both resolved endpoint positions share X or Y.

```json
{
  "net": "link",
  "paths": [
    {"from": {"endpoint": "R1.2"}, "to": {"endpoint": "R2.1"}}
  ]
}
```

## One-Bend and Multi-Bend Route

Add the smallest sequence of grid-aligned `via` points that makes every segment horizontal or vertical. Reject diagonal segments and zero-length segments. Keep each free segment at least 2.5 mm unless it is an exact pin escape permitted by the active profile.

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

## Three-Terminal Net with Explicit Junction

Use multiple paths that terminate at one shared point, and list that point in `junctions`. Every semantic endpoint must appear in at least one route side.

<!-- aixem-snippet: examples/authoring/07-multi-terminal-junction/multi_terminal_junction.aixlayout.json#/layout/connections -->
```json
[
  {
    "junctions": [
      [
        75,
        50
      ]
    ],
    "labels": [
      {
        "text": "BUS",
        "x": 77.5,
        "y": 47.5
      }
    ],
    "layer": "connections",
    "net": "bus",
    "paths": [
      {
        "from": {
          "endpoint": "T1.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        }
      },
      {
        "from": {
          "endpoint": "T2.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        },
        "via": [
          [
            75,
            25
          ]
        ]
      },
      {
        "from": {
          "endpoint": "T3.1"
        },
        "to": {
          "point": [
            75,
            50
          ]
        }
      }
    ],
    "style": "signal"
  },
  {
    "labels": [
      {
        "text": "CROSS / NO JUNCTION",
        "x": 95,
        "y": 42.5
      }
    ],
    "layer": "connections",
    "net": "cross",
    "paths": [
      {
        "from": {
          "endpoint": "T4.1"
        },
        "to": {
          "endpoint": "T5.1"
        }
      }
    ],
    "style": "signal"
  }
]
```
<!-- /aixem-snippet -->

The `bus` branches connect at `[75, 50]` because the semantic net contains all three endpoints and the layout carries an explicit junction there.

## Crossing Without Connection

Two paths from different semantic nets may geometrically intersect. They remain disconnected because semantic membership differs and no shared-net junction exists. Do not insert a junction merely because lines cross.

## Crossing With Connection

A connected branch intersection must satisfy both layers:

1. all participating endpoints belong to the same semantic net; and
2. the layout uses branch paths meeting at the same coordinate and records an explicit junction there.

Geometry alone is insufficient.

## Route Labels

A label has `text`, `x`, `y`, and optional `rotation`. Labels explain a route; they do not define the net. Keep labels away from junction dots, pin names, and dense bends. Use the semantic net name unless a presentation-specific alias is intentional.

## Reroute After Component Movement

1. Recompute resolved endpoint positions from the new placement transform.
2. Preserve semantic net membership.
3. Retain only still-valid shared channels and junction coordinates.
4. Remove zero-length or redundant jogs.
5. Revalidate endpoint closure, orthogonality, grid alignment, and crossing semantics.

## Completion Checklist

- [ ] Every connection names an existing semantic net.
- [ ] Every route endpoint belongs to that net.
- [ ] Every semantic endpoint is referenced by layout geometry.
- [ ] Every segment is orthogonal.
- [ ] Every free bend lies on the active snap grid.
- [ ] Multi-terminal branch points have explicit junction markers.
- [ ] Different-net crossings have no false junction.
- [ ] Labels do not alter or obscure connectivity.
## Component-to-Sheet-Port Recipe

1. Confirm `@PORT` is declared and belongs to the intended local net.
2. Confirm one `sheetPorts[]` anchor exists on a valid side/layer.
3. Route `entity.port` to `@PORT` orthogonally on the active grid.
4. Cover every semantic endpoint; do not use a visible label as a substitute.
5. Validate the leaf independently before composing project routes.
6. Use `route-project-nets` only after project-net membership is closed.

Project routing may improve trunks and bends, but it must never change which interface members belong to a project net.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

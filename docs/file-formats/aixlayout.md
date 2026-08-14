---
id: AIXEM-FORMAT-AIXLAYOUT-001
title: .aixlayout.json Explicit Layout
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents sheets, placements, route connections, path endpoints, via points, junctions, labels, annotations,
  and title blocks.
authority:
- aixlayout-format
aliases:
- .aixlayout
- layout JSON
- explicit layout file
agent:
  priority: high
  estimated_tokens: 2125
  intents:
  - create-schematic
  - route-nets
  - inspect-artifact
  - route-project-nets
depends_on:
- AIXEM-SPEC-LAYOUT-001
related:
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-SPEC-GRID-PROFILE-001
- AIXEM-SCHEM-PLACEMENT-001
- AIXEM-ROUTE-NETS-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
navigation:
  group: file-formats
  order: 50
artifacts:
  owns:
  - '*.aixlayout.json'
  consumes: []
requirements: []
---

# .aixlayout.json Explicit Layout

Documents sheets, placements, route connections, path endpoints, via points, junctions, labels, annotations, and title blocks.

> **Document ID:** `AIXEM-FORMAT-AIXLAYOUT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `aixlayout-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Entity and net IDs bind geometry to semantics.
- Paths are explicit and deterministic.
- Junction records disambiguate joins.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `*.aixlayout.json`

## Operational Rules

- Preserve entity and net ids bind geometry to semantics as an explicit, reviewable part of the task.
- Preserve paths are explicit and deterministic as an explicit, reviewable part of the task.
- Preserve junction records disambiguate joins as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Active Grid and Advisory Placement

`coordinateSystem.grid` records the layout grid but does not create an independent authority. Under Grid Schematic Profile 1 it agrees with the active style profile's `grid.snap`; mismatch fails closed. Component origins and free route bends remain finite and grid legal.

Placement-assist output is derived advisory data. It may report base/X/Y/XY legal candidates, alignment references, and warnings, but it never writes this format or moves neighboring components. An Agent explicitly edits `.aixlayout.json`, records the change set, and reruns closure, collision, route, and render validation.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Explicit Layout Contract 1](../specifications/layout/layout-contract.md) — `AIXEM-SPEC-LAYOUT-001`
- [Component Placement](../schematic/placement.md) — `AIXEM-SCHEM-PLACEMENT-001`
- [Semantic Net Routing](../routing/net-routing.md) — `AIXEM-ROUTE-NETS-001`

<a id="0-5-3-hierarchical-form-aixlayout-2"></a>
## Hierarchical Form (`aixlayout/2`)

`aixlayout/2` preserves v1 placement/layer/connection behavior and adds `sheetPorts[]`. A route endpoint may resolve either `entity.port` or `@PORT`. Every semantic interface port has exactly one presentation record, and the route for its local net must cover the endpoint.

Coordinates, side, label, and layer are presentation data only. See [Hierarchical Sheet-Port Layout Contract 2](../specifications/layout/hierarchical-sheet-port-contract.md).

<a id="0-5-1-placement-and-connection-serialization"></a>
## Placement and Connection Serialization

`.aixlayout.json` owns explicit instance presentation and route geometry. It references semantic entities and nets but cannot create or redefine them.

### Placement Fields

| Field | Meaning |
|---|---|
| `entity` | Semantic entity key; exactly one placement is required for each presented entity. |
| `x`, `y` | World insertion coordinate. |
| `unit` | Coordinate unit when explicitly declared. |
| `rotation` | Clockwise placement rotation under the active coordinate system. |
| `mirrorX`, `mirrorY` | Local mirroring before final translation. |
| `scaleX`, `scaleY` | Presentation scale; use ordinary unit scale for schematic symbols. |
| `variant` | Explicit symbol variant, highest in variant-selection precedence. |
| `parameters` | Instance parameter overrides, highest in parameter precedence. |
| `fields` | Instance displayed-field overrides, highest in field precedence. |
| `bodyStyle` | Instance body style override where supported by the renderer contract. |
| `state` | Presentation state metadata. |
| `layer` | Placement display layer. |
| `zIndex` | Deterministic draw ordering. |
| `locked` | Editing-state lock; it does not strengthen semantic authority. |
| `metadata` | Extension data that must not redefine placement or semantics. |

Complete placement field index: `bodyStyle`, `entity`, `fields`, `layer`, `locked`, `metadata`, `mirrorX`, `mirrorY`, `parameters`, `rotation`, `scaleX`, `scaleY`, `state`, `unit`, `variant`, `x`, `y`, `zIndex`.

### Connection Fields

| Field | Meaning |
|---|---|
| `net` | Existing semantic net name. |
| `paths` | One or more route paths that geometrically cover all net endpoints. |
| `junctions` | Explicit branch-join coordinates for that net. |
| `labels` | Presentation labels; they do not define membership. |
| `style` | Route style reference. |
| `layer` | Route presentation layer. |
| `metadata` | Extension metadata. |

Complete connection field index: `junctions`, `labels`, `layer`, `metadata`, `net`, `paths`, `style`.

Each path has `from` and `to`, optional grid-aligned `via` points, optional `style`, and optional `metadata`. Complete path field index: `from`, `metadata`, `style`, `to`, `via`.

A route side is either a semantic endpoint reference or an explicit point. Endpoint references resolve through the component presentation and transformed symbol port. Points and `via` coordinates own geometry only.

### Multi-Terminal and Crossing Example

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

The `bus` net branches at one listed junction. The separate `cross` net may intersect its geometry without connectivity because semantic net membership differs and no shared-net junction is declared.

### Topology/Geometry Separation

- `.aixem` answers **which endpoints are connected**.
- `.aixlayout.json` answers **where the already-declared connection is drawn**.
- a junction coordinate is valid only within a connection for the corresponding semantic net;
- a line crossing is not a semantic join;
- moving a component requires route endpoint re-resolution and usually rerouting, but not a semantic model edit.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

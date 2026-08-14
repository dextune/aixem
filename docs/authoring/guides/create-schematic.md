---
id: AIXEM-AUTHORING-GUIDE-CREATE-SCHEMATIC-001
title: Create a Schematic
status: informative
version: '1.0'
language: en
domain: authoring
kind: guide
summary: Guides creation of semantic entities and nets separately from grid-authoritative component placement and route geometry.
authority:
- authoring-guide-create-schematic
aliases:
- create schematic guide
- draw circuit guide
- author semantic circuit
agent:
  priority: critical
  estimated_tokens: 1309
  intents:
  - create-schematic
  - author-component-circuit
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-FORMAT-AIXEM-001
- AIXEM-FORMAT-AIXLAYOUT-001
related:
- AIXEM-SCHEM-PLACEMENT-001
- AIXEM-SCHEM-GRID-001
navigation:
  group: authoring-guides
  order: 3
artifacts:
  owns: []
  consumes:
  - docs/_meta/routes/create-schematic.yaml
  - docs/_meta/generated/task-packets/create-schematic.json
  - tools/placement_assist.py
requirements: []
---

# Create a Schematic

## 1. Task

Create closed semantic entities and nets in `.aixem`, then create one legal placement for every presented entity in `.aixlayout.json` before handing closed endpoints to routing.

## 2. Use This Guide When / Do Not Use It When

Use it for a new leaf schematic or a substantial new functional region. For a local edit to a validated drawing, start with [Modify an Existing Schematic](modify-existing-schematic.md). For library creation, use [Create a Library Part](create-library-part.md).

## 3. Primary Route ID

`create-schematic`

## 4. Authored Route and Generated Task Packet

- Authored route: `docs/_meta/routes/create-schematic.yaml`
- Generated task packet: `docs/_meta/generated/task-packets/create-schematic.json`

## 5. Required Inputs

Circuit intent, selected component IDs and locked libraries, semantic endpoint contracts, active style profile, page constraints, and explicit user-fixed placements.

## 6. Authority Allowed to Change

`.aixem` owns entities, semantic nets, attributes, interface ports, and no-connect intent. `.aixlayout.json` owns placement and route geometry. `.aixproj.json` owns safe references and digests. Derived render and Viewer artifacts are never authored directly.

## 7. Canonical Output Location

Use the project-owned source paths declared by the manifest. New reusable parts remain under `library/<electronics|architecture>/...`; schematic instance identity belongs in `.aixem`, not in reusable symbol filenames.

## 8. Important Default Profile Values

```text
G = 2.5 mm  active placement and free-bend snap
P = 5.0 mm  standard pin/spacing rhythm
M = 10 mm   major alignment rhythm
```

The active style profile is schematic snap authority. `layout.coordinateSystem.grid` is a serialized declaration that agrees with it; symbol-local grid metadata cannot override it.

## 9. Short Execution Sequence

1. Select or create all required reusable components and resolve their endpoint identities.
2. Author entities, semantic net memberships, explicit interface ports, attributes, and deliberate no-connects in `.aixem`.
3. Validate semantic endpoint and component-type closure before placing anything.
4. Use [Place Components](place-components.md) to identify anchors, preserve fixed/existing authority, form evidence-backed regions, and reserve routing channels.
5. Use the read-only placement assistant for deterministic snap/alignment suggestions where useful.
6. Write one placement per presented entity and verify active-profile grid coherence.
7. Validate placement closure and prepare explicit semantic endpoints for [Route Nets](route-nets.md).

## 10. Canonical Reference Table

| Document | Stable ID | Why this task needs it | Role |
|---|---|---|---|
| [Authority Model](../../concepts/authority-model.md) | `AIXEM-CONCEPT-AUTHORITY-001` | separate semantic, layout, and derived authority | informative |
| [Schematic Authoring Cookbook](../../schematic/schematic-authoring-cookbook.md) | `AIXEM-SCHEM-COOKBOOK-001` | complete source sequence | informative |
| [Component Placement](../../schematic/placement.md) | `AIXEM-SCHEM-PLACEMENT-001` | placement legality and canonical requirements | informative |
| [Grid and Snap System](../../schematic/grid-system.md) | `AIXEM-SCHEM-GRID-001` | active snap and route grid | informative |
| [`.aixem` Semantic Schematic](../../file-formats/aixem.md) | `AIXEM-FORMAT-AIXEM-001` | entity/net serialization | normative |
| [`.aixlayout.json` Layout](../../file-formats/aixlayout.md) | `AIXEM-FORMAT-AIXLAYOUT-001` | placement/route serialization | normative |
| [Place Components](place-components.md) | `AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001` | evidence-based strategy | informative |

## 11. Validators and Tools

Run semantic closure, component-type closure, binding, placement closure, active-grid coherence, route-scope, and diagnostics validators. Placement suggestions are available through `python tools/placement_assist.py suggest ...`; the command reports `mutated=false`.

## 12. Completion Criteria

All intended entities and endpoints resolve; every semantic net is explicit; no-connect intent is explicit; every presented entity has one grid-legal placement; semantic and layout authority remain separate; route-nets has a closed handoff.

## 13. Stop / Fail-Closed Conditions

Stop when a component identity is unresolved, a semantic connection is being inferred from geometry or labels, the layout grid conflicts with the active profile, or a required placement would force hidden overlap or an unacknowledged broad rewrite.

## 14. Common Mistakes

Do not place a component to decide what it connects to, duplicate semantic facts into layout geometry, use symbol metadata as endpoint truth, compress components before reserving route channels, or edit derived SVG to fix authoritative placement.

## 15. Evidence / Outputs

Retain closed `.aixem`, grid-coherent `.aixlayout.json`, locked project references, placement-assist records used for decisions, scope-valid Change-Set evidence, and the routing handoff.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

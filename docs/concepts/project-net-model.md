---
id: AIXEM-CONCEPT-PROJECT-NET-001
title: Project Net Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Explains the relationship between local semantic nets, sheet interface ports, project nets, equivalence closure, and project routing.
authority:
- project-net-model
aliases:
- cross-sheet net
- project semantic graph
- local net versus project net
agent:
  priority: critical
  estimated_tokens: 804
  intents:
  - compose-project
  - route-project-nets
  - validate-project
depends_on:
- AIXEM-CONCEPT-NET-001
- AIXEM-SPEC-INTERFACE-PORT-001
related:
- AIXEM-SPEC-PROJECT-COMPOSITION-001
- AIXEM-CONCEPT-LAYOUT-001
navigation:
  group: concepts
  order: 55
artifacts:
  owns: []
  consumes:
  - validation/corpus/hierarchical-project-1/results/capability-matrix.json
requirements: []
---

# Project Net Model

AIXEM distinguishes **local nets** from **project nets** so many circuits can be composed without flattening their semantic sources or treating visual routing as connectivity authority.

## Local Net

A local net is owned by one leaf `.aixem` model. Its members may include component endpoints and top-level interface endpoints:

```aixem
net vcc = U1.VCC C1.1 @VCC
```

The leaf source decides that these endpoints are electrically equivalent. Neither the project manifest nor layout can alter that decision.

## Interface Port

The interface port is the semantic boundary object that exposes the local net to project composition. Its qualified identity is:

```text
interface:<sheet-id>:<port-id>
```

A visible sheet-port glyph is only the layout representation of this semantic object.

## Project Net

A project net is owned by `aixproj/2`. It declares equivalence among interface ports from two or more sheets:

```text
project-net:vcc_5v
├── interface:power:VOUT
├── interface:control:VCC
└── interface:io:VCC
```

The transitive project connectivity is the union of each member interface's owning local net. Resolved graph queries can therefore identify all participating leaf endpoints without producing a canonical mega-source.

## Equivalence Collision

Two interface ports may already be equivalent because they belong to the same local net. Assigning those ports to different project-net IDs would falsely split one electrical equivalence class:

```text
local-net:bridge:shared = @A @B U1.1
project-net:X includes bridge:@A
project-net:Y includes bridge:@B
```

This is rejected as `PROJECT_NET_EQUIVALENCE_COLLISION`. The resolver does not silently merge X and Y and does not infer which authored name should win.

## Name Isolation

Text equality is never project connectivity. `power:gnd` and `control:gnd` remain separate local nets unless explicit interface members connect them. This rule protects namespace clarity and prevents accidental global-net behavior.

## Routing Separation

Local route geometry is owned by the leaf layout and reaches `@PORT`. Project route geometry is derived in overview/composite coordinates from explicit project-net membership and transformed interface anchors.

```text
local routing:   entity.port <-> @PORT
project routing: sheet:@PORT <-> sheet:@PORT
```

A crossing between project routes does not connect them. Junctions exist only within one declared project net.

## Repair Ownership

A diagnostic should identify the smallest authoritative owner:

- missing `@PORT` declaration -> leaf `.aixem`;
- missing port coordinate -> leaf `.aixlayout.json`;
- unknown project member -> `aixproj/2`;
- route intersection -> project router or project presentation;
- transformed anchor defect -> renderer.

## Related Documents

- [Net Model](net-model.md)
- [Project Composition Contract 2](../specifications/project/project-composition-contract.md)
- [Hierarchical Sheet-Port Layout Contract 2](../specifications/layout/hierarchical-sheet-port-contract.md)

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

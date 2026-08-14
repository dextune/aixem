---
id: AIXEM-AUTHORING-GUIDES-INDEX-001
title: Task-Oriented Authoring Guides
status: informative
version: '1.0'
language: en
domain: authoring
kind: index
summary: Provides one-hop task selection for reusable part creation, schematic placement, routing, rendering, modification, composition, and validation.
authority:
- authoring-guide-navigation
aliases:
- authoring task guides
- how to author
- agent authoring guides
agent:
  priority: critical
  estimated_tokens: 605
  intents:
  - create-symbol
  - create-schematic
  - route-nets
  - compose-project
  - render-review
  - validate-project
  - author-component-circuit
depends_on:
- AIXEM-AUTHORING-INDEX-001
related:
- AIXEM-AGENT-ROUTES-001
- AIXEM-AGENT-AUTHORING-001
navigation:
  group: authoring-guides
  order: 0
artifacts:
  owns: []
  consumes: []
requirements: []
---

# Task-Oriented Authoring Guides

Select the guide that matches the immediate job. Each guide is an informative execution façade: it names the active route, output authority, shortest sequence, canonical owners, validators, completion conditions, and fail-closed boundaries. Normative rules remain in the linked specifications and file-format references.

## Task Map

| Task | Start here | Primary route |
|---|---|---|
| create or repair a reusable component and symbol | [Create a Library Part](create-library-part.md) | `create-symbol` |
| select an existing reusable component | [Select a Library Part](select-library-part.md) | `create-schematic` |
| create semantic entities, nets, and initial layout | [Create a Schematic](create-schematic.md) | `create-schematic` |
| decide component positions from explicit circuit evidence | [Place Components](place-components.md) | `create-schematic` |
| materialize semantic nets as route geometry | [Route Nets](route-nets.md) | `route-nets` |
| register sheets, interfaces, and project nets | [Compose a Project](compose-project.md) | `compose-project` |
| make a minimal change to a validated schematic | [Modify an Existing Schematic](modify-existing-schematic.md) | `create-schematic` |
| perform part-to-circuit authoring end to end | [Author a Component Circuit](author-component-circuit.md) | `author-component-circuit` |
| inspect deterministic render and Viewer evidence | [Render and Review](render-review.md) | `render-review` |
| close structural, semantic, compatibility, and intent evidence | [Validate a Project](validate-project.md) | `validate-project` |

## Stable Authoring Chain

```text
create/select library part
-> create semantic schematic
-> place components
-> route nets
-> render and review
-> validate and close
```

For an existing drawing, use the modification guide before changing coordinates or routes. For a new concrete part, resolve its source-backed or placeholder status before authoring pins or geometry.

## Retrieval Rule

Open this index, one selected task guide, the route packet named by that guide, and only the canonical owners listed in its reference table. Do not perform repository-wide discovery when the route already resolves the required authority.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

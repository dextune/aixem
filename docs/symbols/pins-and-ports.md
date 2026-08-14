---
id: AIXEM-SYMBOL-PORTS-001
title: Pins, Ports, and Endpoint Mapping
status: normative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Defines pin orientation, electrical role, number and name placement, connection points, and semantic endpoint
  mapping.
authority:
- symbol-port-presentation
aliases:
- pins
- ports
- pin mapping
- endpoint mapping
agent:
  priority: critical
  estimated_tokens: 3047
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-CONCEPT-COMPONENT-001
- AIXEM-SYMBOL-ANATOMY-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SCHEM-ANNOTATION-001
- AIXEM-FORMAT-AIXSYM-001
navigation:
  group: symbols
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0004
  title: Unique port IDs
  level: MUST
  statement: Port IDs MUST be unique within a symbol asset.
  validator: schematic.symbol_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0004.json
- id: AIXEM-REQ-SYMBOL-0005
  title: Connection-point authority
  level: MUST
  statement: The declared port connection point MUST be the geometric endpoint used by routing.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0005.json
- id: AIXEM-REQ-SYMBOL-0006
  title: Stable number and name
  level: MUST
  statement: Pin number and pin name MUST remain associated with the same semantic endpoint across compatible symbol
    variants.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0006.json
---

# Pins, Ports, and Endpoint Mapping

Defines pin orientation, electrical role, number and name placement, connection points, and semantic endpoint mapping.

> **Document ID:** `AIXEM-SYMBOL-PORTS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-port-presentation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Orientation describes the outward wire direction.
- Electrical role assists validation but does not replace endpoint identity.
- Hidden power pins require explicit semantic policy.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-SYMBOL-0004"></a>

### AIXEM-REQ-SYMBOL-0004 — Unique port IDs

**MUST.** Port IDs MUST be unique within a symbol asset.

- Verification mode: `automated`
- Validator: `schematic.symbol_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0004.json`

<a id="AIXEM-REQ-SYMBOL-0005"></a>

### AIXEM-REQ-SYMBOL-0005 — Connection-point authority

**MUST.** The declared port connection point MUST be the geometric endpoint used by routing.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0005.json`

<a id="AIXEM-REQ-SYMBOL-0006"></a>

### AIXEM-REQ-SYMBOL-0006 — Stable number and name

**MUST.** Pin number and pin name MUST remain associated with the same semantic endpoint across compatible symbol variants.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0006.json`

## Electrical and Presentation Semantic Axes

Stable component port IDs are endpoint authority. `port.type` owns basic electrical behavior; optional component-port `metadata.pinSemantics` owns orthogonal signal class, function, polarity, differential pairing, power-domain hints, capabilities, and alternate functions. Terminal labels and pin names support review but do not replace identity.

Symbol ports own graphic location, orientation, and presentation-local IDs. A symbol-side `semanticType`, label, or visual position is presentation evidence only and cannot override component-port semantics. Alternate functions remain capabilities of one physical terminal and never create additional endpoints.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Component Model](../concepts/component-model.md) — `AIXEM-CONCEPT-COMPONENT-001`
- [Symbol Anatomy](symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [Annotations and Fields](../schematic/annotations.md) — `AIXEM-SCHEM-ANNOTATION-001`
- [.aixsym.json Symbol Asset](../file-formats/aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`

<a id="0-5-1-port-serialization-and-drawing-contract"></a>
## Port Serialization and Drawing Contract

A semantic component port, a symbol port, and a visible pin lead are three linked but distinct objects:

```text
component port ID ──portMap──> symbol port ID at (x,y)
                                      ↑
                     visible graphic lead endpoint
```

The component port owns semantic endpoint identity. The symbol port owns the electrical attachment coordinate. A graphic `line`, `polyline`, or other node owns the visible lead. Standard recipes associate the lead with `metadata.port` and choose `metadata.portEndpoint` as `start` or `end`; lint then proves exact coincidence.

### Complete Symbol Port Field Reference

| Field | Required | Meaning and renderer effect |
|---|---:|---|
| `id` | yes | Stable symbol-local port ID and target of `.aixlib.json` `portMap`. |
| `kind` | yes | Port role such as electrical; it does not replace component electrical type. |
| `x` | yes | Local X attachment coordinate; number or numeric expression. |
| `y` | yes | Local Y attachment coordinate; number or numeric expression. |
| `orientation` | yes | Direction in local symbol coordinates. Standard values are 0 right, 90 down, 180 left, 270 up under the default clockwise/down-positive system. |
| `name` | no | Human-readable pin/signal name used by automatic overlays when visible. |
| `number` | no | Distinct physical/logical pin number string. |
| `labelVisible` | no | Enables the automatic name overlay; it does not draw a lead. |
| `numberVisible` | no | Enables the automatic number overlay; it does not draw a lead. |
| `leadLength` | no | Declared presentation lead length metadata. The actual graphic must still be authored and checked. |
| `snapRadius` | no | Local selection/snap tolerance around the exact electrical coordinate. It does not move the port. |
| `visibleWhen` | no | Parameter predicate controlling port visibility. Required mapped ports must resolve visible. |
| `metadata` | no | Extension data; standard recipes use associated graphic-node metadata for machine-verifiable lead ownership. |

### Executable Multi-Side Port Set

<!-- aixem-snippet: examples/authoring/03-multi-pin-ic/library/electronics/authoring/controller-12.aixsym.json#/symbol/ports -->
```json
[
  {
    "id": "1",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "input"
    },
    "name": "AIN0",
    "number": "1",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -20,
    "y": -7.5
  },
  {
    "id": "2",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "input"
    },
    "name": "AIN1",
    "number": "2",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -20,
    "y": -2.5
  },
  {
    "id": "3",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "bidirectional"
    },
    "name": "SCL",
    "number": "3",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -20,
    "y": 2.5
  },
  {
    "id": "4",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "bidirectional"
    },
    "name": "SDA",
    "number": "4",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -20,
    "y": 7.5
  },
  {
    "id": "5",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "output"
    },
    "name": "PWM0",
    "number": "5",
    "numberVisible": true,
    "orientation": 0,
    "snapRadius": 1.25,
    "x": 20,
    "y": -7.5
  },
  {
    "id": "6",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "output"
    },
    "name": "PWM1",
    "number": "6",
    "numberVisible": true,
    "orientation": 0,
    "snapRadius": 1.25,
    "x": 20,
    "y": -2.5
  },
  {
    "id": "7",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "output"
    },
    "name": "TX",
    "number": "7",
    "numberVisible": true,
    "orientation": 0,
    "snapRadius": 1.25,
    "x": 20,
    "y": 2.5
  },
  {
    "id": "8",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "input"
    },
    "name": "RX",
    "number": "8",
    "numberVisible": true,
    "orientation": 0,
    "snapRadius": 1.25,
    "x": 20,
    "y": 7.5
  },
  {
    "id": "9",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "power-input"
    },
    "name": "VDD",
    "number": "9",
    "numberVisible": true,
    "orientation": 270,
    "snapRadius": 1.25,
    "x": -5,
    "y": -20
  },
  {
    "id": "10",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "power-input"
    },
    "name": "AVDD",
    "number": "10",
    "numberVisible": true,
    "orientation": 270,
    "snapRadius": 1.25,
    "x": 5,
    "y": -20
  },
  {
    "id": "11",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "power-input"
    },
    "name": "GND",
    "number": "11",
    "numberVisible": true,
    "orientation": 90,
    "snapRadius": 1.25,
    "x": -5,
    "y": 20
  },
  {
    "id": "12",
    "kind": "electrical",
    "labelVisible": true,
    "metadata": {
      "semanticType": "power-input"
    },
    "name": "AGND",
    "number": "12",
    "numberVisible": true,
    "orientation": 90,
    "snapRadius": 1.25,
    "x": 5,
    "y": 20
  }
]
```
<!-- /aixem-snippet -->

### Orientation Examples

```text
left signal pin:    port (-20, 0), orientation 180, lead from (-20,0) to (-15,0)
right signal pin:   port ( 20, 0), orientation   0, lead from ( 15,0) to ( 20,0)
top supply pin:     port (  0,-20), orientation 270, lead from (0,-20) to (0,-15)
bottom return pin:  port (  0, 20), orientation  90, lead from (0, 15) to (0, 20)
```

For a vertical power pin, the electrical port is the outer endpoint. Do not reverse the association merely because the visible line can be traversed in either direction.

### Visibility and Conditional Ports

`labelVisible` and `numberVisible` affect only automatic text overlays. `visibleWhen` affects the port itself. A selected variant may change presentation metadata through `portOverrides`, but it must not silently change semantic component endpoint identity. A required component port may not map to a symbol port that resolves hidden.

### Placement Transform

The renderer resolves the local symbol port first, then applies placement scale, mirror, rotation, and translation. `resolved-scene.json` exposes the final routed coordinate under the **semantic component port ID**, not the symbol-local target ID. Route endpoints therefore remain stable even when the symbol is rotated or mirrored.

### Mapping Diagnostics

- Missing `portMap` key: incomplete semantic component presentation.
- Unknown map target: library references a symbol port ID that does not exist.
- Hidden map target: parameters or selected variant made a required mapped port invisible.
- Wire misses visible lead: lead endpoint and symbol port differ, or the layout endpoint resolved from the wrong semantic port.
- Wrong pin text: inspect `name`, `number`, `labelVisible`, and `numberVisible`; do not edit connectivity to fix a label.
- Off-grid target: repair the symbol port expression/default, then regenerate locked output.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

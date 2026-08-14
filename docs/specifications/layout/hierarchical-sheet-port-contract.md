---
id: AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
title: Hierarchical Sheet-Port Layout Contract 2
status: normative
version: '2.0'
language: en
domain: specifications
kind: specification
summary: Defines aixlayout/2 sheetPorts presentation, interface route endpoint resolution, and the separation between local and project routing.
authority:
- hierarchical-interface-presentation
- leaf-route-geometry
aliases:
- aixlayout 2
- sheetPorts
- interface port placement
agent:
  priority: critical
  estimated_tokens: 1063
  intents:
  - route-nets
  - route-project-nets
  - validate-project
depends_on:
- AIXEM-SPEC-LAYOUT-001
- AIXEM-SPEC-INTERFACE-PORT-001
related:
- AIXEM-CONCEPT-PROJECT-NET-001
- AIXEM-FORMAT-AIXLAYOUT-001
- AIXEM-ROUTE-NETS-001
navigation:
  group: specifications
  order: 75
artifacts:
  owns:
  - docs/specifications/schemas/component-graphics-2/aixem-explicit-layout-2.schema.json
  consumes:
  - validation/corpus/hierarchical-project-1/manifest.json
requirements:
- id: AIXEM-REQ-HIER-0004
  title: Total sheet-port presentation
  level: MUST
  statement: Every semantic interface port in a hierarchical leaf MUST have exactly one valid sheetPorts presentation in aixlayout/2, and no unknown presentation may exist.
  validator: schematic.layout_closure
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_complete_corpus_runner
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0004.json
- id: AIXEM-REQ-HIER-0005
  title: Local route closure to interface endpoints
  level: MUST
  statement: Local route paths MUST cover every connected @PORT endpoint using the semantic net that owns the endpoint.
  validator: schematic.route_closure
  verification_mode: automated
  test: tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven
  evidence: validation/evidence/requirements/AIXEM-REQ-HIER-0005.json
---

# Hierarchical Sheet-Port Layout Contract 2

`aixlayout/2` adds one presentation structure to the v1 explicit-layout model: `sheetPorts[]`. It supplies coordinates and visual orientation for semantic interface ports while preserving the rule that geometry never creates connectivity.

## Required Shape

```json
{
  "schema": "https://schemas.aixem.org/component-graphics/aixlayout/2",
  "formatVersion": "2.0",
  "layout": {
    "designId": "control",
    "sheetPorts": [
      {
        "port": "VCC",
        "x": 10,
        "y": 40,
        "side": "left",
        "layer": "connections",
        "label": "VCC"
      }
    ]
  }
}
```

`port` resolves to a top-level semantic port in the owning `.aixem` model. Coordinates use the layout coordinate system. `side` is one of `left`, `right`, `top`, or `bottom` and controls deterministic glyph orientation and project anchor escape behavior.

## Presentation Closure

For a hierarchical leaf:

- every semantic interface port has exactly one `sheetPorts[]` record;
- every record resolves to a semantic interface port;
- the declared layer exists;
- coordinates lie within the sheet;
- IDs remain unique;
- presentation changes never alter local or project net ownership.

The v1 layout schema remains immutable and does not accept `sheetPorts[]`.

## Route Endpoint Resolution

The route endpoint grammar in v2 accepts both:

```text
entity.port
@PORT
```

Example:

```json
{
  "net": "vcc",
  "paths": [
    {
      "from": {"endpoint": "U1.VCC"},
      "to": {"endpoint": "@VCC"},
      "via": [[40, 40]]
    }
  ]
}
```

The path is valid only when both endpoints belong to local semantic net `vcc`. The renderer resolves `@VCC` from `sheetPorts[]`; it does not infer a net from the route.

## Interface Glyph

The reference renderer draws an original, grid-aligned boundary glyph using existing SVG vector operations. The glyph is not a component, does not require an `.aixsym` asset, and carries qualified inspection metadata.

Stable properties are limited to anchor, side, label offset, stroke class, and selected state. The glyph remains presentation-only.

## Local and Project Routing

A leaf layout owns routes within one sheet. Project-level overview/composite routes are derived separately after leaf resolution:

```text
.aixlayout/2 -> local paths to @PORT
project router -> transformed paths between sheet ports
```

Improving project geometry must not edit project-net membership. Improving local geometry must not change semantic local-net membership.

## Determinism

All free bends follow the active grid and orthogonal profile. Port anchors, side orientation, labels, and route endpoints must resolve identically from the same locked inputs.

## Evidence

H006 proves entity-to-interface route closure. N005 and N006 prove unknown and missing `sheetPorts[]` failures. H007 and H008 prove that the same semantic anchor can drive overview and composite routing without authority leakage.


## Normative Requirements

<a id="AIXEM-REQ-HIER-0004"></a>

### AIXEM-REQ-HIER-0004 — Total sheet-port presentation

**MUST.** Every semantic interface port in a hierarchical leaf MUST have exactly one valid sheetPorts presentation in aixlayout/2, and no unknown presentation may exist.

- Verification mode: `automated`
- Validator: `schematic.layout_closure`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_complete_corpus_runner`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0004.json`

<a id="AIXEM-REQ-HIER-0005"></a>

### AIXEM-REQ-HIER-0005 — Local route closure to interface endpoints

**MUST.** Local route paths MUST cover every connected @PORT endpoint using the semantic net that owns the endpoint.

- Verification mode: `automated`
- Validator: `schematic.route_closure`
- Test reference: `tests/conformance/test_hierarchical_project.py::HierarchicalProjectConformanceTests.test_multi_view_render_outputs_and_workbench_are_data_driven`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-HIER-0005.json`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

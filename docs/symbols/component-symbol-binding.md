---
id: AIXEM-SYMBOL-BINDING-001
title: Component to Symbol Binding
status: normative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Defines how semantic component ports and properties bind through AIXLIB presentations into AIXSYM ports and text fields.
authority:
- component-symbol-binding
aliases:
- component symbol binding
- portmap fieldmap
- library presentation binding
agent:
  priority: critical
  estimated_tokens: 1780
  intents:
  - create-symbol
  - create-schematic
  - author-component-circuit
depends_on:
- AIXEM-CONCEPT-COMPONENT-001
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-SPEC-RENDERER-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SYMBOL-PORTS-001
- AIXEM-SYMBOL-FIELDS-001
navigation:
  group: symbols
  order: 42
artifacts:
  owns: []
  consumes:
  - examples/authoring/05-field-and-port-binding/
requirements:
- id: AIXEM-REQ-SYMBOL-BINDING-0001
  title: Total semantic port map
  level: MUST
  statement: Every active component presentation MUST map every semantic component port exactly once to an existing visible symbol port.
  validator: schematic.authoring_binding
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_port_map_direction_totality_and_visibility
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-BINDING-0001.json
- id: AIXEM-REQ-SYMBOL-BINDING-0002
  title: Directed field map
  level: MUST
  statement: A component presentation fieldMap MUST map symbol field names to semantic component property or entity attribute names.
  validator: schematic.renderer_contract
  verification_mode: automated
  test: tests/docs/test_renderer_contract.py::RendererContractTests.test_field_precedence
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-BINDING-0002.json
---

# Component to Symbol Binding

The component library bridges semantic identity and graphic presentation. The direction of each map is part of the public contract.

```text
.aixlib component ports/properties
        ↓ presentation
asset + portMap + fieldMap + defaultVariant
        ↓
.aixsym graphics/ports/text fields
        ↓
.aixem entity attributes + .aixlayout placement overrides
        ↓
renderer binding and resolved scene
```

## Component Object

A component has `id`, `kind`, `displayName`, `ports`, `properties`, and `presentations`. Optional component fields are `description`, `classification`, `models`, and `metadata`.

A semantic component port has `id`, `name`, `type`, and optional `description`, `terminal`, `required`, and `metadata`. A component property has `id`, `type`, and optional `default`, `description`, `required`, `unit`, and `values`.

## Presentation Object

Each presentation has `purpose`, `asset`, and `portMap`. Optional fields are `fieldMap`, `parameterMap`, `defaultVariant`, and `metadata`.

The `asset` object has `path`, `digest`, `symbolId`, and `revision`. All four values are verified. The path must be project-local, and the digest must match the loaded file.

## Port Map Direction

`portMap` is always:

```text
semantic component port ID → symbol port ID
```

It is not symbol-to-component. The map keys must exactly equal the component's semantic port IDs. Every target must exist in the selected symbol and remain visible after parameters and variant port overrides resolve.

<a id="AIXEM-REQ-SYMBOL-BINDING-0001"></a>

### AIXEM-REQ-SYMBOL-BINDING-0001 — Total semantic port map

**MUST.** Every active component presentation MUST map every semantic component port exactly once to an existing visible symbol port.

- Verification mode: `automated`
- Validator: `schematic.authoring_binding`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_port_map_direction_totality_and_visibility`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-BINDING-0001.json`

## Field Map Direction

`fieldMap` is always:

```text
symbol text field name → semantic component property/entity attribute name
```

For example, `{ "value": "rating" }` means a symbol text node with `field: "value"` receives the semantic entity attribute `rating` before later placement overrides are applied.

<a id="AIXEM-REQ-SYMBOL-BINDING-0002"></a>

### AIXEM-REQ-SYMBOL-BINDING-0002 — Directed field map

**MUST.** A component presentation fieldMap MUST map symbol field names to semantic component property or entity attribute names.

- Verification mode: `automated`
- Validator: `schematic.renderer_contract`
- Test reference: `tests/docs/test_renderer_contract.py::RendererContractTests.test_field_precedence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-BINDING-0002.json`

## Complete Binding Example

<!-- aixem-snippet: examples/authoring/05-field-and-port-binding/library/electronics/authoring/authoring-components.aixlib.json#/library/components/0 -->
```json
{
  "classification": [],
  "description": "Bound sensor",
  "displayName": "Bound sensor",
  "id": "authoring:sensor",
  "kind": "sensor",
  "metadata": {
    "partProvenance": {
      "status": "generic-template"
    },
    "semanticReady": true
  },
  "ports": [
    {
      "id": "in",
      "metadata": {
        "pinSemantics": {
          "capabilities": [],
          "functionalTags": [],
          "polarity": "unspecified",
          "profile": "aixem-pin-semantics-1",
          "signalClass": "digital"
        }
      },
      "name": "Input",
      "required": false,
      "terminal": "in",
      "type": "input"
    },
    {
      "id": "out",
      "metadata": {
        "pinSemantics": {
          "capabilities": [],
          "functionalTags": [],
          "polarity": "unspecified",
          "profile": "aixem-pin-semantics-1",
          "signalClass": "digital"
        }
      },
      "name": "Output",
      "required": false,
      "terminal": "out",
      "type": "output"
    }
  ],
  "presentations": [
    {
      "asset": {
        "digest": "sha256:334056e981bd1741e42f034fbbeb3547dc5f7b1025b8d8c05d449d86da0e2e71",
        "path": "library/electronics/authoring/sensor.aixsym.json",
        "revision": "1.0.0",
        "symbolId": "authoring:sensor"
      },
      "fieldMap": {
        "deviceLabel": "label",
        "reference": "refdes",
        "value": "rating"
      },
      "portMap": {
        "in": "p-left",
        "out": "p-right"
      },
      "purpose": "primary-diagram"
    }
  ],
  "properties": [
    {
      "id": "refdes",
      "required": false,
      "type": "string"
    },
    {
      "id": "rating",
      "required": false,
      "type": "string"
    },
    {
      "id": "label",
      "required": false,
      "type": "string"
    }
  ]
}
```
<!-- /aixem-snippet -->

The semantic entity supplies `refdes`, `rating`, and `label`. The placement then overrides the resolved `value` field:

<!-- aixem-snippet: examples/authoring/05-field-and-port-binding/field_port_binding.aixlayout.json#/layout/placements/0 -->
```json
{
  "entity": "S1",
  "fields": {
    "value": "5V_OVERRIDE"
  },
  "layer": "symbols",
  "x": 80,
  "y": 50
}
```
<!-- /aixem-snippet -->

## Field Resolution

The renderer resolves field values in this order:

```text
renderer identity/default fields
→ presentation fieldMap-derived values
→ all semantic entity attributes
→ placement fields overrides
```

Later layers win. A symbol text node then reads the final value through its `field` property.

## Variant and Parameter Handoff

The presentation may supply `defaultVariant`. The placement may supply `variant`, `parameters`, and `fields`. A presentation `parameterMap` is reserved in the schema but is not used by the 0.5.1 reference renderer; authoring workflows must not depend on undocumented behavior.

## Binding Diagnostics

| Failure | Meaning |
|---|---|
| `portMap is not total` | map keys do not equal semantic component ports |
| `maps to unknown symbol port` | map target is absent from the asset |
| `mapped symbol port is hidden` | selected parameters/variant made a required target invisible |
| symbol identity mismatch | asset `symbolId` or `revision` differs from loaded asset |
| symbol digest mismatch | locked content changed without updating the library reference |
| wrong displayed value | inspect `fieldMap`, semantic attributes, then placement `fields` in precedence order |

## Semantic Authority and Canonical Asset Paths

New presentation paths resolve project-root relatively inside the canonical tree, for example `library/electronics/passive/resistor/resistor-iec.aixsym.json`. Safe historical paths remain compatible for explicit repair. Path and filename aid retrieval; component ID, symbol ID/revision, and digest lock remain identity authority.

`portMap` maps stable component endpoints to symbol-local graphic endpoints. The component port owns `type` and `metadata.pinSemantics`; symbol metadata cannot override either. A shared symbol digest is valid for multiple components only when each component retains its own complete semantic and provenance contract.

## Validation Procedure

1. Validate library and symbol schemas.
2. Verify asset path, digest, symbol ID, and revision.
3. Compare component port IDs with `portMap` keys.
4. Resolve the selected variant and parameters.
5. Verify every target symbol port exists and is visible.
6. Resolve fields and inspect rendered text plus `resolved-scene.json`.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

---
id: AIXEM-SYMBOL-PRIMITIVES-001
title: Graphic Primitives
status: normative
version: '1.0'
language: en
domain: symbols
kind: reference
summary: Defines the permitted vector primitives, path features, text, dimensions, definitions, and locked raster
  images.
authority:
- symbol-primitives
aliases:
- graphic primitives
- vector primitives
- symbol drawing commands
agent:
  priority: critical
  estimated_tokens: 3016
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-SYMBOL-ANATOMY-001
related:
- AIXEM-FORMAT-AIXSYM-001
- AIXEM-SPEC-SYMBOL-001
navigation:
  group: symbols
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0007
  title: Supported features
  level: MUST
  statement: A symbol asset MUST declare every required graphic feature and a renderer MUST reject unsupported required
    features.
  validator: schematic.feature_support
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0007.json
- id: AIXEM-REQ-SYMBOL-0008
  title: Locked raster content
  level: MUST
  statement: Any raster image referenced by a symbol MUST be digest-locked and locally resolvable.
  validator: schematic.remote_assets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0008.json
---

# Graphic Primitives

Defines the permitted vector primitives, path features, text, dimensions, definitions, and locked raster images.

> **Document ID:** `AIXEM-SYMBOL-PRIMITIVES-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-primitives`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Lines and rectangles cover most engineering symbols.
- Path primitives support curves and complex shapes.
- Definition-use reduces duplication without changing port identity.

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

<a id="AIXEM-REQ-SYMBOL-0007"></a>

### AIXEM-REQ-SYMBOL-0007 — Supported features

**MUST.** A symbol asset MUST declare every required graphic feature and a renderer MUST reject unsupported required features.

- Verification mode: `automated`
- Validator: `schematic.feature_support`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0007.json`

<a id="AIXEM-REQ-SYMBOL-0008"></a>

### AIXEM-REQ-SYMBOL-0008 — Locked raster content

**MUST.** Any raster image referenced by a symbol MUST be digest-locked and locally resolvable.

- Verification mode: `automated`
- Validator: `schematic.remote_assets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0008.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Anatomy](symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [.aixsym.json Symbol Asset](../file-formats/aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`
- [Symbol Asset Contract 1](../specifications/symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`

<a id="0-5-1-complete-primitive-serialization-reference"></a>
## Complete Primitive Serialization Reference

Every node may use the common fields documented below when permitted by its schema branch. Numeric coordinates accept either a number or a declared numeric-expression object. Prefer the simplest primitive that communicates engineering function.

### Common Node Fields

| Field | Meaning |
|---|---|
| `type` | Selects exactly one primitive schema branch. |
| `id` | Stable node-local identifier used by suppression, review, and diagnostics. |
| `role` | Semantic visual role such as `body`, `pin-lead`, or `reference-field`; it does not create circuit semantics. |
| `classes` | Presentation classes available to style resolution. |
| `layer` | Named symbol layer; the layer must exist when one is referenced. |
| `style` | Named symbol fallback style. |
| `transform` | Six-number affine matrix `[a,b,c,d,e,f]` applied locally. |
| `visibleWhen` | Boolean/predicate evaluated from resolved parameters. |
| `metadata` | Extension metadata that must not redefine standardized behavior. |

### `group`

Nest nodes under one transform/visibility boundary.

**Required:** `type`, `children`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "group",
  "children": [
    {
      "type": "line",
      "x1": 0,
      "y1": 0,
      "x2": 5,
      "y2": 0
    }
  ]
}
```

### `use`

Instantiate a reusable named definition with local parameters.

**Required:** `type`, `definition`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `parameters`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "use",
  "definition": "pin-shape",
  "parameters": {
    "length": 5
  }
}
```

### `line`

Draw pin leads, body edges, polarity marks, and simple indicators.

**Required:** `type`, `x1`, `y1`, `x2`, `y2`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "line",
  "x1": -10,
  "y1": 0,
  "x2": -5,
  "y2": 0
}
```

### `polyline`

Draw an ordered open or optionally closed segmented shape.

**Required:** `type`, `points`.

**Optional:** `classes`, `closed`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "polyline",
  "points": [
    [
      -5,
      0
    ],
    [
      0,
      -2.5
    ],
    [
      5,
      0
    ]
  ],
  "closed": false
}
```

### `polygon`

Draw a closed filled or stroked polygon.

**Required:** `type`, `points`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "polygon",
  "points": [
    [
      -5,
      5
    ],
    [
      0,
      -5
    ],
    [
      5,
      5
    ]
  ]
}
```

### `rect`

Draw ordinary IC, connector, passive, and functional-block bodies.

**Required:** `type`, `x`, `y`, `width`, `height`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `rx`, `ry`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "rect",
  "x": -10,
  "y": -5,
  "width": 20,
  "height": 10
}
```

### `circle`

Draw inversion bubbles, terminals, or circular functional marks.

**Required:** `type`, `cx`, `cy`, `r`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "circle",
  "cx": 0,
  "cy": 0,
  "r": 2.5
}
```

### `ellipse`

Draw an elliptical mark only when a circle is insufficient.

**Required:** `type`, `cx`, `cy`, `rx`, `ry`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "ellipse",
  "cx": 0,
  "cy": 0,
  "rx": 5,
  "ry": 2.5
}
```

### `arc`

Draw a bounded elliptical arc with explicit start and sweep angles.

**Required:** `type`, `cx`, `cy`, `rx`, `ry`, `startAngle`, `sweepAngle`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "arc",
  "cx": 0,
  "cy": 0,
  "rx": 5,
  "ry": 5,
  "startAngle": 0,
  "sweepAngle": 180
}
```

### `path`

Draw a shape that cannot be represented economically by simpler primitives.

**Required:** `type`, `commands`.

**Optional:** `classes`, `fillRule`, `id`, `layer`, `metadata`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "path",
  "commands": [
    {
      "cmd": "M",
      "x": -5,
      "y": 0
    },
    {
      "cmd": "L",
      "x": 0,
      "y": -5
    },
    {
      "cmd": "L",
      "x": 5,
      "y": 0
    },
    {
      "cmd": "Z"
    }
  ]
}
```

### `text`

Draw literal text or a renderer-bound semantic field.

**Required:** `type`, `x`, `y`.

**Optional:** `anchor`, `baseline`, `classes`, `field`, `id`, `layer`, `maxWidth`, `metadata`, `preserveUpright`, `role`, `rotation`, `style`, `text`, `transform`, `visibleWhen`.

```json
{
  "type": "text",
  "x": 0,
  "y": -7.5,
  "anchor": "middle",
  "field": "reference"
}
```

### `image`

Reference a locked local raster asset; never use it for electrical semantics.

**Required:** `type`, `x`, `y`, `width`, `height`, `source`.

**Optional:** `classes`, `id`, `layer`, `metadata`, `opacity`, `preserveAspectRatio`, `role`, `style`, `transform`, `visibleWhen`.

```json
{
  "type": "image",
  "x": -5,
  "y": -5,
  "width": 10,
  "height": 10,
  "source": {
    "path": "assets/mark.png",
    "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "mediaType": "image/png"
  }
}
```

### `dimension`

Render an informative measurement annotation, not a connectivity element.

**Required:** `type`, `from`, `to`, `offset`.

**Optional:** `arrowSize`, `classes`, `field`, `id`, `layer`, `metadata`, `precision`, `role`, `style`, `text`, `transform`, `unit`, `visibleWhen`.

```json
{
  "type": "dimension",
  "from": [
    -5,
    0
  ],
  "to": [
    5,
    0
  ],
  "offset": 2.5,
  "unit": "mm",
  "precision": 1
}
```

### Complete Property Index

The union of all primitive properties is listed here for schema-to-document coverage. A property is legal only on the primitive branches shown above:

`anchor`, `arrowSize`, `baseline`, `children`, `classes`, `closed`, `commands`, `cx`, `cy`, `definition`, `field`, `fillRule`, `from`, `height`, `id`, `layer`, `maxWidth`, `metadata`, `offset`, `opacity`, `parameters`, `points`, `precision`, `preserveAspectRatio`, `preserveUpright`, `r`, `role`, `rotation`, `rx`, `ry`, `source`, `startAngle`, `style`, `sweepAngle`, `text`, `to`, `transform`, `type`, `unit`, `visibleWhen`, `width`, `x`, `x1`, `x2`, `y`, `y1`, `y2`.

### Expression and Reuse Rules

- Coordinate and size fields use the schema numeric-expression grammar; undefined parameters and invalid arithmetic fail closed.
- `definitions` hold reusable node trees. A `use` node selects one by `definition`, then applies its local `parameters` and `transform`.
- `visibleWhen` is evaluated after parameters resolve. Do not map a required semantic endpoint to a port that can become hidden in the selected state.
- `path` commands support `M`, `L`, `Q`, `C`, `A`, and `Z`. Use paths only when ordinary primitives cannot represent the form clearly.
- `image` sources must be local and digest-locked. Raster appearance must never be the sole carrier of electrical meaning.
- `dimension` is informative presentation. It never creates an endpoint, net, or layout constraint.

### Authoring Misuse to Avoid

- Do not draw a pin lead with a decorative unassociated line and assume the renderer can infer its electrical target.
- Do not use color, fill, or image content to distinguish electrical connectivity.
- Do not encode an entire ordinary symbol body as one opaque `path` when lines/rectangles/circles are inspectable and sufficient.
- Do not make a reusable `definition` depend on undeclared parameters.
<a id="0-5-2-composition-and-dimension-notes"></a>
## Composition and Dimension Notes

The expressiveness corpus confirmed that the current primitive inventory is sufficient for all S-Core, S-Extended, and Static 2D Block fixtures. No new primitive was added in 0.5.2.

Prefer composition, definitions and `use`, and finally `path` before proposing a primitive. A proposal must identify a blocked case and pass the extension gate in `AIXEM-CONF-SYMBOL-EXP-001`.

The `dimension` primitive renders its internal measurement label with an explicit deterministic `dimension-label` style. Authors should not depend on browser-default SVG text sizing. B005 and the dimension-label regression test are the released evidence for this behavior.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

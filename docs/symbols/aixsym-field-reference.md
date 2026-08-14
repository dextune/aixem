---
id: AIXEM-SYMBOL-AIXSYM-REF-001
title: AIXSYM Field Reference
status: informative
version: '1.0'
language: en
domain: symbols
kind: reference
summary: Describes every top-level AIXSYM authoring field, parameter field, and renderer-relevant interaction in agent-readable form.
authority:
- aixsym-agent-reference
aliases:
- aixsym field reference
- symbol json fields
- symbol asset reference
agent:
  priority: critical
  estimated_tokens: 1951
  intents:
  - create-symbol
  - inspect-artifact
  - validate-project
depends_on:
- AIXEM-SPEC-SYMBOL-001
related:
- AIXEM-SYMBOL-PRIMITIVES-001
- AIXEM-SPEC-RENDERER-001
navigation:
  group: symbols
  order: 40
artifacts:
  owns: []
  consumes:
  - docs/specifications/schemas/component-graphics-1/aixem-symbol-asset-1.schema.json
requirements: []
---

# AIXSYM Field Reference

This page is an authoring companion to the normative JSON Schema. The schema remains the structural authority; this reference explains meaning, renderer effect, precedence, and failure modes.

## Document Envelope

| Field | Type | Required | Authoring meaning |
|---|---|---:|---|
| `schema` | URI string | yes | Selects the symbol-asset schema. Use `https://schemas.aixem.org/component-graphics/aixsym/1`. |
| `formatVersion` | string | yes | Serialization format version. The current value is `1.0`. |
| `symbol` | object | yes | The complete symbol asset. |

## Top-Level Symbol Object

Every active top-level field is listed below so an agent does not need to discover routine fields from raw schema source.

| Field | Required | Renderer effect and interaction |
|---|---:|---|
| `id` | yes | Stable symbol identity; must match the library asset reference `symbolId`. |
| `revision` | yes | Asset revision; must match the library asset reference `revision`. |
| `title` | yes | Human-readable asset title. |
| `description` | no | Authoring description; no connectivity effect. |
| `purpose` | no | Declares intended use such as `schematic-symbol`. |
| `coordinateSystem` | yes | Defines `unit`, `yAxis`, `angleUnit`, `angleDirection`, and optional `grid`. |
| `bounds` | yes | Declares deterministic asset extent through `x`, `y`, `width`, and `height`. |
| `anchors` | no | Named insertion, rotation, or alignment points. |
| `layers` | yes | Ordered symbol-local visibility and print groups. |
| `styles` | yes | Named fallback styles referenced by graphic nodes. |
| `graphics` | yes | Base graphic-node list rendered before selected-variant graphics. |
| `ports` | yes | Electrical attachment coordinates and pin metadata. |
| `parameters` | no | Typed values used by numeric expressions and predicates. |
| `variants` | no | Named graphical alternatives with parameter defaults and port overrides. |
| `defaultVariant` | no | Symbol fallback when neither placement nor presentation selects a variant. |
| `definitions` | no | Reusable graphic-node definitions expanded by `use`. |
| `paintServers` | no | Local vector patterns or gradients. |
| `requiredFeatures` | no | Renderer capabilities that must be supported or cause rejection. |
| `metadata` | no | Extension metadata; it must not redefine standardized semantics. |
| `provenance` | yes | Local origin, license, author, and creation record. |

## Coordinate System

`coordinateSystem.unit` is normally `mm`. `coordinateSystem.yAxis` controls local Y direction. `coordinateSystem.angleUnit` is `deg`, and `coordinateSystem.angleDirection` defines positive rotation. `coordinateSystem.grid` declares the asset's authoring grid but does not replace the active schematic design profile.

Placement transformation is deterministic: local symbol coordinates are adapted to layout axis direction, then scale/mirror and rotation are applied, and finally the instance is translated to placement `x`/`y`.

## Bounds, Anchors, Layers, and Styles

`bounds` must contain the intended visible asset and provide stable fit/selection behavior. An `anchor` has `id`, `kind`, `x`, `y`, optional `orientation`, and optional `metadata`. A `layer` has `id`, `order`, `purpose`, `defaultVisible`, and optional `locked` and `printable` flags.

Each entry in `styles` may use `stroke`, `strokeWidth`, `strokeLinecap`, `strokeLinejoin`, `strokeMiterlimit`, `dashArray`, `dashOffset`, `fill`, `fillRule`, `opacity`, `fontFamily`, `fontSize`, `fontWeight`, `fontStyle`, `textDecoration`, `letterSpacing`, and `pointerEvents`. Symbol styles are deterministic fallbacks; the renderer/style precedence contract controls project-level presentation overrides.

## Graphics

`graphics` contains nodes with a mandatory `type`. Common node fields include `id`, `layer`, `style`, `role`, `classes`, `metadata`, `transform`, and `visibleWhen`. The complete node-type and property reference is in [Graphic Primitives](primitives.md).

`definitions` maps a reusable name to one node. A `use` node selects a definition and can pass local `parameters`. `paintServers` maps a name to a vector pattern, linear gradient, or radial gradient. Any renderer-dependent mechanism used by the asset should be declared in `requiredFeatures`.

## Ports

`ports` is an array of electrical or other attachment points. Every port has `id`, `x`, `y`, `orientation`, and `kind`. Optional display and interaction fields are `name`, `number`, `labelVisible`, `numberVisible`, `leadLength`, `snapRadius`, `visibleWhen`, and `metadata`. Detailed lead/port rules are owned by [Pins, Ports, and Endpoint Mapping](pins-and-ports.md).

## Parameter Definitions

Each entry in `parameters` uses the following fields:

| Field | Meaning |
|---|---|
| `type` | One of the schema-defined parameter kinds, including numeric, integer, boolean, string, and enum forms. |
| `default` | Required base value used before variant and placement overrides. |
| `description` | Optional authoring explanation. |
| `minimum` | Optional lower bound for numeric values. |
| `maximum` | Optional upper bound for numeric values. |
| `step` | Optional recommended increment. |
| `unit` | Optional unit label. |
| `values` | Allowed values for an enum parameter. |

Numeric geometry fields may contain a literal number, `{ "param": "name" }`, or an operation object. Supported operations are `add`, `sub`, `mul`, `div`, `min`, `max`, `clamp`, `neg`, and `abs`.

Parameter resolution is:

```text
symbol parameter default
→ selected variant parameterDefaults
→ placement parameters override
```

Unknown parameters, invalid types, out-of-range values, and division by zero are renderer failures.

## Variants

A variant has `id` and may define `title`, `selector`, `graphics`, `parameterDefaults`, `portOverrides`, `suppress`, and `metadata`. `defaultVariant` is only the symbol-level fallback. See [Symbol Parameters and Variants](variants.md) for full precedence and invariants.

## Provenance

`provenance` requires `origin`, `license`, `author`, and `created`. Optional fields are `sourceUri`, `sourceDigest`, and `notes`. Provenance is not a license substitute: the asset must still be independently authored and legally distributable.

## Minimal Skeleton

```json
{
  "schema": "https://schemas.aixem.org/component-graphics/aixsym/1",
  "formatVersion": "1.0",
  "symbol": {
    "id": "example:device",
    "revision": "1.0.0",
    "title": "Example device",
    "coordinateSystem": {
      "unit": "mm",
      "yAxis": "down",
      "angleUnit": "deg",
      "angleDirection": "clockwise",
      "grid": 2.5
    },
    "bounds": {"x": -20, "y": -15, "width": 40, "height": 30},
    "layers": [],
    "styles": {},
    "ports": [],
    "graphics": [],
    "provenance": {
      "origin": "Independent AIXEM authoring",
      "license": "CC0-1.0",
      "author": "Example author",
      "created": "2026-08-11"
    }
  }
}
```

## Validation Failure Modes

- Missing required top-level fields fail JSON Schema.
- A library reference with a different `id` or `revision` fails asset binding.
- A required feature not supported by the renderer causes fail-closed rejection.
- A referenced style, layer, definition, field, parameter, or symbol port that cannot be resolved is a contract error.
- A schema-valid symbol can still fail the design profile when ports are off-grid, fields collide, or visible leads do not meet ports.

## Related Documents

- [Symbol Authoring Cookbook](symbol-authoring-cookbook.md)
- [Graphic Primitives](primitives.md)
- [Renderer Contract](../specifications/renderer/renderer-contract.md)

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

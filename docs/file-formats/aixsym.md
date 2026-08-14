---
id: AIXEM-FORMAT-AIXSYM-001
title: .aixsym.json Symbol Asset
status: normative
version: '1.0'
language: en
domain: file-formats
kind: reference
summary: Documents symbol metadata, coordinate system, bounds, definitions, primitives, ports, fields, variants,
  and feature requirements.
authority:
- aixsym-format
aliases:
- .aixsym
- symbol JSON
- symbol asset format
agent:
  priority: high
  estimated_tokens: 3007
  intents:
  - create-symbol
  - inspect-artifact
  - validate-project
depends_on:
- AIXEM-SPEC-SYMBOL-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SYMBOL-PRIMITIVES-001
- AIXEM-FORMAT-AIXLIB-001
navigation:
  group: file-formats
  order: 40
artifacts:
  owns:
  - '*.aixsym.json'
  consumes: []
requirements: []
---

# .aixsym.json Symbol Asset

Documents symbol metadata, coordinate system, bounds, definitions, primitives, ports, fields, variants, and feature requirements.

> **Document ID:** `AIXEM-FORMAT-AIXSYM-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The format is interpreted together with its declared schema, feature set, and project lock.

The declared authority scopes are `aixsym-format`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Assets are portable and independently authored.
- Port maps bind graphics to endpoints.
- Required features are negotiated explicitly.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `*.aixsym.json`

## Operational Rules

- Preserve assets are portable and independently authored as an explicit, reviewable part of the task.
- Preserve port maps bind graphics to endpoints as an explicit, reviewable part of the task.
- Preserve required features are negotiated explicitly as an explicit, reviewable part of the task.
- Follow any normative dependencies before claiming conformance.
- Do not duplicate a binding rule that already has a canonical owner.

## Graphic Provenance and Semantic Boundary

Symbol provenance describes the origin and licensing of graphic presentation assets. It does not independently prove the identity, pinout, ratings, or circuit suitability of a component bound to that symbol. Several valid component IDs may share one locked symbol asset, but copying geometry never creates a new semantic component identity.

Electrical behavior and extended pin meaning remain owned by component ports in `.aixlib.json`; symbol ports own presentation geometry and symbol-local endpoint IDs. `portMap` is the only binding bridge. Symbol metadata may support review and rendering but cannot override a component port's `type` or `metadata.pinSemantics`.

## Validation and Evidence

Use the related normative documents to select validators. Informative guidance is considered complete only after the authoritative artifacts and their generated products pass the relevant checks.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Asset Contract 1](../specifications/symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`
- [Graphic Primitives](../symbols/primitives.md) — `AIXEM-SYMBOL-PRIMITIVES-001`
- [.aixlib.json Component Library](aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`

<a id="0-5-1-annotated-format-skeleton"></a>
## Annotated Format Skeleton

`.aixsym.json` is the authoritative symbol-graphics asset. It owns local geometry, symbol ports, fields, parameters, variants, reusable definitions, and deterministic fallback styles. It does not own semantic component port identity, instance placement, or net membership.

<!-- aixem-snippet: examples/authoring/01-two-pin-passive/library/electronics/authoring/resistor.aixsym.json#/symbol -->
```json
{
  "anchors": [
    {
      "id": "origin",
      "kind": "insertion",
      "x": 0,
      "y": 0
    }
  ],
  "bounds": {
    "height": 25,
    "width": 40,
    "x": -20,
    "y": -12.5
  },
  "coordinateSystem": {
    "angleDirection": "clockwise",
    "angleUnit": "deg",
    "grid": 2.5,
    "unit": "mm",
    "yAxis": "down"
  },
  "definitions": {},
  "description": "Two-pin passive symbol with explicit lead-to-port coincidence.",
  "graphics": [
    {
      "id": "lead-1",
      "layer": "body",
      "metadata": {
        "port": "1",
        "portEndpoint": "start"
      },
      "role": "pin-lead",
      "style": "line",
      "type": "line",
      "x1": {
        "args": [
          {
            "args": [
              {
                "args": [
                  {
                    "param": "body-length"
                  },
                  2
                ],
                "op": "div"
              },
              {
                "param": "lead-length"
              }
            ],
            "op": "add"
          }
        ],
        "op": "neg"
      },
      "x2": {
        "args": [
          {
            "args": [
              {
                "param": "body-length"
              },
              2
            ],
            "op": "div"
          }
        ],
        "op": "neg"
      },
      "y1": 0,
      "y2": 0
    },
    {
      "id": "lead-2",
      "layer": "body",
      "metadata": {
        "port": "2",
        "portEndpoint": "end"
      },
      "role": "pin-lead",
      "style": "line",
      "type": "line",
      "x1": {
        "args": [
          {
            "param": "body-length"
          },
          2
        ],
        "op": "div"
      },
      "x2": {
        "args": [
          {
            "args": [
              {
                "param": "body-length"
              },
              2
            ],
            "op": "div"
          },
          {
            "param": "lead-length"
          }
        ],
        "op": "add"
      },
      "y1": 0,
      "y2": 0
    },
    {
      "height": {
        "param": "body-height"
      },
      "id": "body-iec",
      "layer": "body",
      "role": "body",
      "style": "body",
      "type": "rect",
      "width": {
        "param": "body-length"
      },
      "x": {
        "args": [
          {
            "args": [
              {
                "param": "body-length"
              },
              2
            ],
            "op": "div"
          }
        ],
        "op": "neg"
      },
      "y": {
        "args": [
          {
            "args": [
              {
                "param": "body-height"
              },
              2
            ],
            "op": "div"
          }
        ],
        "op": "neg"
      }
    },
    {
      "anchor": "middle",
      "baseline": "middle",
      "field": "reference",
      "id": "field-reference",
      "layer": "fields",
      "role": "reference-field",
      "style": "field",
      "type": "text",
      "x": 0,
      "y": -7.5
    },
    {
      "anchor": "middle",
      "baseline": "middle",
      "field": "value",
      "id": "field-value",
      "layer": "fields",
      "role": "value-field",
      "style": "value",
      "type": "text",
      "x": 0,
      "y": 7.5
    }
  ],
  "id": "authoring:resistor",
  "layers": [
    {
      "defaultVisible": true,
      "id": "body",
      "locked": true,
      "order": 10,
      "printable": true,
      "purpose": "symbol body and pin leads"
    },
    {
      "defaultVisible": true,
      "id": "fields",
      "locked": false,
      "order": 20,
      "printable": true,
      "purpose": "bound text fields"
    }
  ],
  "metadata": {
    "recipe": "two-pin-passive"
  },
  "paintServers": {},
  "parameters": {
    "body-height": {
      "default": 7.5,
      "maximum": 12.5,
      "minimum": 5,
      "type": "length",
      "unit": "mm"
    },
    "body-length": {
      "default": 20,
      "maximum": 30,
      "minimum": 10,
      "type": "length",
      "unit": "mm"
    },
    "lead-length": {
      "default": 5,
      "maximum": 10,
      "minimum": 2.5,
      "type": "length",
      "unit": "mm"
    }
  },
  "ports": [
    {
      "id": "1",
      "kind": "electrical",
      "labelVisible": false,
      "name": "1",
      "number": "1",
      "numberVisible": false,
      "orientation": 180,
      "snapRadius": 1.25,
      "x": {
        "args": [
          {
            "args": [
              {
                "args": [
                  {
                    "param": "body-length"
                  },
                  2
                ],
                "op": "div"
              },
              {
                "param": "lead-length"
              }
            ],
            "op": "add"
          }
        ],
        "op": "neg"
      },
      "y": 0
    },
    {
      "id": "2",
      "kind": "electrical",
      "labelVisible": false,
      "name": "2",
      "number": "2",
      "numberVisible": false,
      "orientation": 0,
      "snapRadius": 1.25,
      "x": {
        "args": [
          {
            "args": [
              {
                "param": "body-length"
              },
              2
            ],
            "op": "div"
          },
          {
            "param": "lead-length"
          }
        ],
        "op": "add"
      },
      "y": 0
    }
  ],
  "provenance": {
    "author": "AIXEM project",
    "created": "2026-08-11",
    "license": "CC0-1.0",
    "notes": "Two-pin passive symbol with explicit lead-to-port coincidence.",
    "origin": "AIXEM 0.5.1 authoring documentation"
  },
  "purpose": "schematic-symbol",
  "requiredFeatures": [],
  "revision": "1.0.0",
  "styles": {
    "body": {
      "fill": "#fffef8",
      "stroke": "#0c7772",
      "strokeLinecap": "square",
      "strokeLinejoin": "miter",
      "strokeWidth": 0.65
    },
    "detail": {
      "fill": "none",
      "stroke": "#0c7772",
      "strokeLinecap": "square",
      "strokeLinejoin": "miter",
      "strokeWidth": 0.5
    },
    "field": {
      "fill": "#17231d",
      "fontFamily": "Arial, sans-serif",
      "fontSize": 3.5,
      "fontWeight": 600,
      "stroke": "none"
    },
    "line": {
      "fill": "none",
      "stroke": "#0c7772",
      "strokeLinecap": "square",
      "strokeLinejoin": "miter",
      "strokeWidth": 0.65
    },
    "value": {
      "fill": "#4f5e56",
      "fontFamily": "Arial, sans-serif",
      "fontSize": 3.0,
      "fontWeight": 400,
      "stroke": "none"
    }
  },
  "title": "Authoring resistor",
  "variants": []
}
```
<!-- /aixem-snippet -->

The complete field semantics are maintained in the [AIXSYM Field Reference](../symbols/aixsym-field-reference.md); primitive serialization is maintained in [Graphic Primitives](../symbols/primitives.md).

### Version and Locking

- `schema` identifies the structural contract.
- `formatVersion` selects serialization version `1.0`.
- symbol `id` and `revision` must match the consuming library asset reference.
- the library stores the exact SHA-256 digest of the file.
- any authoritative asset change requires a digest update in consuming locks.
- deterministic serialization uses UTF-8 JSON, stable keys in generated fixtures, and no remote resources.

### Authority Boundary

| Belongs here | Does not belong here |
|---|---|
| body and pin-lead graphics | semantic component port type/identity |
| symbol-local electrical attachment coordinates | instance world position |
| field anchors and literal body labels | instance field values except defaults represented by binding |
| parameter and variant graphics | net membership and no-connect intent |
| fallback style roles/tokens | project route geometry |

### Validation Order

1. JSON parse and schema validation.
2. required-feature support.
3. numeric-expression and variant/parameter validation.
4. grid, lead/port, pitch, field, and bounds lint.
5. component presentation mapping and digest checks.
6. deterministic render and visual inspection.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

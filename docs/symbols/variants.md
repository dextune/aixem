---
id: AIXEM-SYMBOL-VARIANTS-001
title: Symbol Variants
status: normative
version: '1.0'
language: en
domain: symbols
kind: concept
summary: Defines compatible graphic variants, default selection, feature negotiation, and endpoint-preserving substitutions.
authority:
- symbol-variants
aliases:
- symbol variants
- alternate symbol
- unit symbol
agent:
  priority: critical
  estimated_tokens: 1934
  intents:
  - create-symbol
  - create-schematic
depends_on:
- AIXEM-SYMBOL-PORTS-001
related:
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-SPEC-SYMBOL-001
navigation:
  group: symbols
  order: 70
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0013
  title: Endpoint-preserving compatibility
  level: MUST
  statement: A compatible graphic variant MUST preserve the declared semantic endpoint set and endpoint IDs.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0013.json
- id: AIXEM-REQ-SYMBOL-0014
  title: Deterministic selection
  level: MUST
  statement: Project and library policy MUST select a symbol variant deterministically.
  validator: schematic.deterministic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0014.json
---

# Symbol Variants

Defines compatible graphic variants, default selection, feature negotiation, and endpoint-preserving substitutions.

> **Document ID:** `AIXEM-SYMBOL-VARIANTS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-variants`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Variants may change body arrangement and field placement.
- A changed endpoint contract requires a new component or compatibility version.
- Default selection is locked by the project build.

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

<a id="AIXEM-REQ-SYMBOL-0013"></a>

### AIXEM-REQ-SYMBOL-0013 — Endpoint-preserving compatibility

**MUST.** A compatible graphic variant MUST preserve the declared semantic endpoint set and endpoint IDs.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0013.json`

<a id="AIXEM-REQ-SYMBOL-0014"></a>

### AIXEM-REQ-SYMBOL-0014 — Deterministic selection

**MUST.** Project and library policy MUST select a symbol variant deterministically.

- Verification mode: `automated`
- Validator: `schematic.deterministic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0014.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Pins, Ports, and Endpoint Mapping](pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [.aixlib.json Component Library](../file-formats/aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`
- [Symbol Asset Contract 1](../specifications/symbols/symbol-contract.md) — `AIXEM-SPEC-SYMBOL-001`

<a id="0-5-1-complete-parameter-and-variant-contract"></a>
## Complete Parameter and Variant Contract

### Variant Field Reference

| Field | Required | Meaning |
|---|---:|---|
| `id` | yes | Stable selectable variant ID. |
| `title` | no | Human-readable variant title. |
| `selector` | no | Declarative selection metadata; it does not override explicit renderer precedence. |
| `graphics` | no | Additional selected-variant graphics rendered with base graphics. |
| `parameterDefaults` | no | Values applied after symbol parameter defaults. |
| `portOverrides` | no | Presentation overrides for existing symbol port IDs. |
| `suppress` | no | IDs of base graphic nodes omitted in this variant. |
| `metadata` | no | Extension metadata with no independent authority. |

### Selection Precedence

```text
placement.variant
→ presentation.defaultVariant
→ symbol.defaultVariant
```

The first defined value wins. An unknown selected variant is a renderer error; the renderer must not silently fall back to an unrelated style.

### Parameter Precedence

```text
symbol parameter default
→ selected variant parameterDefaults
→ placement.parameters override
```

A parameter definition uses `type` and `default`, with optional `description`, `minimum`, `maximum`, `step`, `unit`, and `values`. Values must conform to type, enum, bounds, and expression rules before geometry is rendered.

### Executable Variant Set

<!-- aixem-snippet: examples/authoring/04-parameterized-variant/library/electronics/authoring/resistor-variant.aixsym.json#/symbol/variants -->
```json
[
  {
    "graphics": [
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
      }
    ],
    "id": "iec",
    "parameterDefaults": {
      "body-length": 20
    },
    "title": "IEC rectangular body"
  },
  {
    "graphics": [
      {
        "id": "body-ansi",
        "layer": "body",
        "points": [
          [
            -12.5,
            0
          ],
          [
            -10,
            -3.75
          ],
          [
            -5,
            3.75
          ],
          [
            0,
            -3.75
          ],
          [
            5,
            3.75
          ],
          [
            10,
            -3.75
          ],
          [
            12.5,
            0
          ]
        ],
        "role": "body",
        "style": "line",
        "type": "polyline"
      }
    ],
    "id": "ansi",
    "parameterDefaults": {
      "body-length": 25
    },
    "title": "ANSI zig-zag body"
  }
]
```
<!-- /aixem-snippet -->

The golden fixture proves presentation default selection, placement override, variant defaults, and placement parameter override in one deterministic scene.

### Endpoint Invariants

A graphical variant may alter body form, add or suppress identified graphics, and override display metadata of an existing symbol port. It must not:

- add a semantic component endpoint;
- remove or rename a semantic component endpoint;
- map a component port to a different semantic meaning;
- hide a required mapped symbol port;
- change net membership;
- make the same component ID represent an incompatible endpoint contract.

Use separate component definitions or a formally versioned compatible presentation when endpoint identity changes.

### Conditional Visibility

`visibleWhen` is evaluated from resolved parameters. Apply it to optional graphic detail carefully. A condition that hides a mapped required port is invalid even if the underlying JSON remains schema-valid.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

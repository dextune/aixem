---
id: AIXEM-SYMBOL-COOKBOOK-001
title: Symbol Authoring Cookbook
status: informative
version: '1.0'
language: en
domain: symbols
kind: cookbook
summary: Provides executable, schema-valid recipes for drawing common AIXEM schematic symbols without renderer-code discovery.
authority:
- symbol-authoring-recipes
aliases:
- symbol cookbook
- drawing recipes
- create component graphics
agent:
  priority: critical
  estimated_tokens: 4920
  intents:
  - create-symbol
  - author-component-circuit
depends_on:
- AIXEM-SPEC-SYMBOL-DESIGN-001
- AIXEM-SYMBOL-AIXSYM-REF-001
- AIXEM-SYMBOL-PORTS-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SYMBOL-BINDING-001
- AIXEM-AGENT-VISUAL-QA-001
navigation:
  group: symbols
  order: 45
artifacts:
  owns: []
  consumes:
  - examples/authoring/
requirements: []
---

# Symbol Authoring Cookbook

This cookbook converts a component endpoint contract into a compact, deterministic `.aixsym.json` asset. The recipes are backed by executable fixtures under `examples/authoring/` and are intended to be followed directly by an authoring agent.

## Inputs and Outputs

**Inputs** are the semantic component ID, complete component port set, port names and electrical types, required displayed fields, preferred variant policy, and the active symbol design profile.

**Outputs** are one schema-valid symbol asset, one presentation binding in `.aixlib.json`, a passing symbol-design lint result, and rendered evidence. Symbol geometry never creates or changes semantic connectivity.

## Recipe Selection

| Component class | Start from | Body strategy | Port strategy |
|---|---|---|---|
| Two-pin passive | `01-two-pin-passive` | centered body with two 5 mm leads | left port at 180°, right port at 0° |
| Connector | `02-connector` | body height derived from pin count | repeated ports on 5 mm pitch |
| Multi-pin IC | `03-multi-pin-ic` | rectangular body sized by largest side group | signals left/right, supplies top/bottom |
| Parameterized or variant symbol | `04-parameterized-variant` | geometry driven by typed parameters | endpoint identity remains invariant |
| Custom semantic-to-graphic mapping | `05-field-and-port-binding` | ordinary body and field nodes | explicit `portMap` and `fieldMap` |

Do not create a new symbol when an existing locked asset already satisfies the same endpoint and presentation contract.

## Coordinate and Origin Strategy

Use millimetres, a down-positive Y axis, clockwise degrees, and the active 2.5 mm authoring grid. Put the insertion anchor at `(0, 0)` unless a package-specific convention has been approved. Center ordinary bodies around the origin so placement, mirroring, and rotation remain predictable.

Derive the body before drawing details:

1. Group ports by left, right, top, and bottom side.
2. Compute the largest group span as `(count - 1) × pinPitch`.
3. Add body padding above and below the group.
4. Place every visible lead between the body edge and its electrical port.
5. Place `reference` and `value` fields outside the body and outside pin-name channels.

## Recipe: Two-Pin Passive

The electrical connection point is the symbol `port`. The visible lead is an explicit `line` node. The associated lead endpoint and port coordinate must resolve to the same point.

<!-- aixem-snippet: examples/authoring/01-two-pin-passive/library/electronics/authoring/resistor.aixsym.json#/symbol/ports -->
```json
[
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
]
```
<!-- /aixem-snippet -->

The body and lead geometry are independently serialized:

<!-- aixem-snippet: examples/authoring/01-two-pin-passive/library/electronics/authoring/resistor.aixsym.json#/symbol/graphics -->
```json
[
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
]
```
<!-- /aixem-snippet -->

The standard construction sequence is:

1. Declare typed body and lead parameters.
2. Draw the left and right leads with `role: "pin-lead"`.
3. Associate each lead with `metadata.port` and `metadata.portEndpoint` for machine-checkable coincidence.
4. Draw the body between lead inner endpoints.
5. Add bound text nodes for `reference` and `value`.
6. Validate the symbol, bind it through the component library, render it, and inspect the port targets.

## Recipe: Connector

Use a deterministic ordering rule: port `1` is the first visible position and later ports progress in increasing numerical order. Keep names and numbers distinct, even when both are displayed.

<!-- aixem-snippet: examples/authoring/02-connector/library/electronics/authoring/connector-6.aixsym.json#/symbol/ports -->
```json
[
  {
    "id": "1",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P1",
    "number": "1",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": -12.5
  },
  {
    "id": "2",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P2",
    "number": "2",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": -7.5
  },
  {
    "id": "3",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P3",
    "number": "3",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": -2.5
  },
  {
    "id": "4",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P4",
    "number": "4",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": 2.5
  },
  {
    "id": "5",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P5",
    "number": "5",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": 7.5
  },
  {
    "id": "6",
    "kind": "electrical",
    "labelVisible": true,
    "name": "P6",
    "number": "6",
    "numberVisible": true,
    "orientation": 180,
    "snapRadius": 1.25,
    "x": -10,
    "y": 12.5
  }
]
```
<!-- /aixem-snippet -->

For `N` pins on one side, use a body span of at least `(N - 1) × 5 mm` plus one pitch of vertical padding. Never compress pin pitch merely to reduce symbol area.

## Recipe: Multi-Pin IC

Group pins by engineering function before assigning sides. A default signal-flow layout places inputs on the left and outputs on the right. Put power inputs at the top and return/ground ports at the bottom when that does not conceal the component's functional grouping.

The twelve-pin fixture demonstrates all four sides:

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

Body dimensions must leave room for automatic pin names and numbers. Increase the body; do not shorten the standard lead or reduce pitch to solve a label collision.

## Recipe: Parameters and Variants

Use parameters for dimensions or visibility that vary without changing component identity. Use variants for recognized graphical alternatives. A variant may add graphics, set parameter defaults, override presentation metadata for an existing symbol port, or suppress named graphics. It must not silently add, remove, or rename semantic component endpoints.

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

The renderer resolves parameters as symbol defaults, then selected-variant defaults, then placement overrides. The selected variant resolves as placement, then library presentation default, then symbol default.

## Semantic Contract Before Geometry

For reusable-part work, establish the component identity, provenance status, complete port inventory, distinguishing properties, and optional source-reviewed pin semantics before creating or copying graphics. Reusing one symbol asset across multiple legitimate components is encouraged. Changing only an ID or display label around copied geometry is not legitimate component generation.

Apply the reference rhythm `G=2.5 mm`, `P=5 mm`, `M=10 mm`, standard lead `L=5 mm`. Required body spans are rounded outward to `G`; a repeated group of `N` pins reserves at least `(N - 1)P + 2G` before extra label and field clearance. Never compress pin pitch or lead length to force content into a preferred box.

## Common Failure Patterns

| Defect | Cause | Repair owner |
|---|---|---|
| Wire reaches a point beyond the visible lead | lead endpoint and port coordinate differ | `.aixsym.json` graphics/port |
| Correct-looking symbol cannot bind | `portMap` is incomplete or reversed | `.aixlib.json` presentation |
| Pin name overlaps body | body too small or orientation wrong | symbol geometry/port metadata |
| Reference/value text sits inside the body | field anchor violates the design profile | symbol text node |
| Variant changes endpoint identity | variant used as a semantic substitute | component model and symbol variant |
| Off-grid pin target | parameter expression resolves outside the profile grid | symbol parameter/default/port expression |
| Decorative path obscures function | excessive primitive complexity | symbol graphics |

## Author, Render, Inspect, Repair

1. Validate JSON Schema and feature declarations.
2. Run symbol-design lint, including grid and lead/port coincidence.
3. Validate total component-to-symbol port mapping.
4. Render SVG and `resolved-scene.json` from locked inputs.
5. Inspect body proportions, pin groups, field clearance, and visible connection targets.
6. Classify any defect by authority layer before editing.
7. Modify only the owning source, rerender, and compare deterministic output.

## Completion Checklist

- [ ] The semantic endpoint contract is known and unchanged.
- [ ] The asset validates against the active `.aixsym` schema.
- [ ] Every mapped symbol port exists and remains visible.
- [ ] Every visible lead endpoint coincides with its electrical port.
- [ ] Ports, body dimensions, and field anchors follow the active grid/design profile.
- [ ] `reference`, `value`, and custom fields resolve through documented precedence.
- [ ] Parameters and variants preserve endpoint identity.
- [ ] Rendered SVG and resolved-scene evidence were inspected.

## Related Documents

- [AIXSYM Field Reference](aixsym-field-reference.md)
- [Component to Symbol Binding](component-symbol-binding.md)
- [Symbol Design Profile](../specifications/symbols/symbol-design-profile.md)
- [Visual QA Loop](../agent/visual-qa-loop.md)

<a id="0-5-2-nearest-corpus-pattern"></a>
## Nearest Corpus Pattern

Use the nearest validated corpus construction before designing a new structure. The corpus remains informative; the actual component endpoint contract controls the new symbol.

| Target class | Cases | Preferred pattern | Primary risk |
|---|---|---|---|
| Two-pin passive | S001-S005 | Straight composition, then reuse or path for repeated detail. | Lead endpoint and electrical port diverge. |
| Diode/transistor | S006-S010, S025 | Grouped body details with explicit external leads. | Arrow, bubble, or internal mark suggests false connectivity. |
| Analog/electromechanical | S011-S016 | Separate conductive geometry from mechanical association. | Mechanical detail is interpreted as a net. |
| Logic | S017-S018 | Curved path body plus explicit bubble/mark. | Endpoint identity changes with presentation. |
| Connector | S019-S021 | Stable pitch, repeated leads, deterministic numbering. | Dense labels or off-grid ports. |
| MCU/high-pin IC | S022-S024 | Functional side grouping and protected field zones. | Pin density exceeds readable pitch. |
| Complex/custom | S026-S029 | Compose first; compound path only for irregular contours. | Self-intersection or undocumented renderer dependence. |
| Multi-unit FPGA | S030 | Semantic capability probe only. | Variants or duplicated entities falsely simulate units. |

Run `python tools/validate_symbol_corpus.py --case <ID>` while adapting a pattern, then run the target tier and the full release gate.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

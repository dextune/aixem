---
id: AIXEM-SPEC-SYMBOL-DESIGN-001
title: Symbol Design Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines measurable grid, lead, pitch, field-clearance, grouping, and primitive-economy rules for AIXEM schematic symbols.
authority:
- symbol-design-profile
aliases:
- symbol design profile
- schematic symbol dimensions
- pin lead coincidence
agent:
  priority: critical
  estimated_tokens: 1669
  intents:
  - create-symbol
  - validate-project
depends_on:
- AIXEM-SPEC-GRID-PROFILE-001
- AIXEM-SPEC-VISUAL-PROFILE-001
related:
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-SYMBOL-DESIGN-RULES-001
- AIXEM-SYMBOL-LINT-001
navigation:
  group: specifications
  order: 72
artifacts:
  owns:
  - profiles/aixem-grid-schematic-style-1.aixstyle.json
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-DESIGN-0001
  title: Grid-aligned electrical ports
  level: MUST
  statement: Electrical symbol port coordinates for the active grid-light profile MUST resolve to the 2.5 millimetre authoring grid.
  validator: schematic.symbol_design
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0001.json
- id: AIXEM-REQ-SYMBOL-DESIGN-0002
  title: Visible lead and port coincidence
  level: MUST
  statement: The visible pin lead endpoint associated with an electrical symbol port MUST coincide with that port coordinate within renderer tolerance.
  validator: schematic.symbol_design
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0002.json
- id: AIXEM-REQ-SYMBOL-DESIGN-0003
  title: Standard pin pitch and lead length
  level: SHOULD
  statement: Standard connector and integrated-circuit recipes SHOULD use 5 millimetre pin pitch and 5 millimetre visible lead length.
  validator: schematic.symbol_design
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0003.json
- id: AIXEM-REQ-SYMBOL-DESIGN-0004
  title: External identity fields
  level: MUST
  statement: Default reference and value field anchors MUST remain outside the component body and clear of ordinary pin-name channels.
  validator: schematic.symbol_design
  verification_mode: automated
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0004.json
- id: AIXEM-REQ-SYMBOL-DESIGN-0005
  title: Functional pin grouping
  level: SHOULD
  statement: Multi-pin symbols SHOULD group ports by engineering function and preserve a left-to-right signal-flow reading where applicable.
  validator: manual.symbol_visual_review
  verification_mode: review
  test: tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_authoring_golden_examples
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0005.json
- id: AIXEM-REQ-SYMBOL-DESIGN-0006
  title: Grid-proportional body sizing
  level: MUST
  statement: Required symbol body dimensions MUST be rounded outward to the active grid and repeated pin groups MUST reserve at least (N - 1)P + 2G in the group axis.
  validator: schematic.authoring_integrity
  verification_mode: automated
  test: tests/schematic/test_authoring_integrity.py::SizingAndGridTests.test_repeated_pin_group_span
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0006.json
---

# Symbol Design Profile 1

This profile turns AIXEM's grid-first visual language into measurable authoring rules. It complements the symbol serialization contract; it does not change semantic endpoint identity.

## Profile Values

| Token | Value | Use |
|---|---:|---|
| snap grid | 2.5 mm | port coordinates, body quantization, field channels |
| standard pin lead | 5 mm | body edge to electrical port |
| standard pin pitch | 5 mm | repeated connector and IC pins |
| body corner policy | square | ordinary functional blocks |
| field placement | outside | default reference and value fields |
| route relationship | orthogonal | pin orientations and downstream routing |

## Grid and Port Rules

<a id="AIXEM-REQ-SYMBOL-DESIGN-0001"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0001 — Grid-aligned electrical ports

**MUST.** Electrical symbol port coordinates for the active grid-light profile MUST resolve to the 2.5 millimetre authoring grid.

- Verification mode: `automated`
- Validator: `schematic.symbol_design`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0001.json`

Port orientation must be one of 0, 90, 180, or 270 degrees for standard schematic use.

<a id="AIXEM-REQ-SYMBOL-DESIGN-0002"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0002 — Visible lead and port coincidence

**MUST.** The visible pin lead endpoint associated with an electrical symbol port MUST coincide with that port coordinate within renderer tolerance.

- Verification mode: `automated`
- Validator: `schematic.symbol_design`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0002.json`

The port owns electrical attachment. The lead owns visible geometry. Their coordinates coincide, but their responsibilities remain distinct.

<a id="AIXEM-REQ-SYMBOL-DESIGN-0003"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0003 — Standard pin pitch and lead length

**SHOULD.** Standard connector and integrated-circuit recipes SHOULD use 5 millimetre pin pitch and 5 millimetre visible lead length.

- Verification mode: `automated`
- Validator: `schematic.symbol_design`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0003.json`

A documented application profile may select another pitch, but all pins in one repeated group must remain consistent.

## Body and Text Clearance

Body width and height should be quantized to the active grid. For a side with `N` pins, reserve at least `(N - 1) × pinPitch` for the pin centers, then add one pitch of body padding in that axis.

<a id="AIXEM-REQ-SYMBOL-DESIGN-0004"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0004 — External identity fields

**MUST.** Default reference and value field anchors MUST remain outside the component body and clear of ordinary pin-name channels.

- Verification mode: `automated`
- Validator: `schematic.symbol_design`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_symbol_design_profile`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0004.json`

Reference and value text should use separate vertical channels. Custom internal function labels may be inside the body when they do not collide with pins or identity fields.

## Functional Grouping

<a id="AIXEM-REQ-SYMBOL-DESIGN-0005"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0005 — Functional pin grouping

**SHOULD.** Multi-pin symbols SHOULD group ports by engineering function and preserve a left-to-right signal-flow reading where applicable.

- Verification mode: `review`
- Validator: `manual.symbol_visual_review`
- Test reference: `tests/docs/test_authoring_examples.py::AuthoringExampleTests.test_authoring_golden_examples`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0005.json`

Inputs normally appear on the left, outputs on the right, supply inputs at the top, and returns at the bottom. Functional coherence takes priority over numerical pin order when the two conflict.

## Primitive Economy

Use the smallest set of primitives that communicates function. Prefer `line`, `rect`, `circle`, `arc`, and `text`. Use `path`, raster `image`, gradients, patterns, and dimensions only when their meaning cannot be expressed more simply. Decorative geometry must never resemble an electrical pin, junction, or no-connect mark.

## Deterministic Bounds

Declared bounds must contain expected base and variant graphics at supported parameter limits. Authors should keep selection/fit bounds stable across non-semantic variants whenever practical.

## Grid-Proportional Sizing Rhythm

The reference construction rhythm is:

```text
G = 2.5 mm  active snap and body quantization unit
P = 5.0 mm  standard repeated pin pitch = 2G
M = 10 mm   major grid = 4G
L = 5.0 mm  standard visible lead = 2G
```

Authors determine content and pin-group span first, add the required text and end-clearance channels, and then round the body outward to the next legal `G` multiple. The body must never be shrunk, nor may `P` or `L` be compressed, merely to fit a preferred nominal size.

<a id="AIXEM-REQ-SYMBOL-DESIGN-0006"></a>

### AIXEM-REQ-SYMBOL-DESIGN-0006 — Grid-proportional body sizing

**MUST.** Required symbol body dimensions MUST be rounded outward to the active grid and repeated pin groups MUST reserve at least `(N - 1) × P + 2G` in the group axis.

- Verification mode: `automated`
- Validator: `schematic.authoring_integrity`
- Test reference: `tests/schematic/test_authoring_integrity.py::SizingAndGridTests.test_repeated_pin_group_span`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-DESIGN-0006.json`

For the reference profile, `2G = P`, so the minimum repeated-pin body span is `N × P`. Additional room for pin names, numbers, internal labels, grouping separators, and identity fields is added in `G` increments. Class-specific dimensions remain validated cookbook or corpus precedents rather than a universal fixed-size table.

## Validation

Automated lint covers schema, port grid, lead association, lead/port coincidence, standard pitch, and basic field/body overlap. Functional grouping, legibility, and decorative ambiguity remain review-mode checks backed by rendered evidence.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

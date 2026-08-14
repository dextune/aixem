---
id: AIXEM-SYMBOL-FIELDS-001
title: Field Layout
status: normative
version: '1.0'
language: en
domain: symbols
kind: guide
summary: Defines reference, value, pin-name, pin-number, and auxiliary field anchors, visibility, alignment, and
  clearance.
authority:
- symbol-field-layout
aliases:
- field layout
- symbol text fields
- reference and value anchors
agent:
  priority: critical
  estimated_tokens: 1592
  intents:
  - create-symbol
  - create-schematic
depends_on:
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-SCHEM-ANNOTATION-001
related:
- AIXEM-SYMBOL-LINT-001
navigation:
  group: symbols
  order: 80
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0015
  title: Declared field anchors
  level: MUST
  statement: Required symbol fields MUST use declared deterministic anchors and alignment rules.
  validator: schematic.annotation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0015.json
- id: AIXEM-REQ-SYMBOL-0016
  title: Field clearance
  level: MUST
  statement: Visible fields MUST respect the declared symbol-body, pin, and route clearance rules.
  validator: schematic.annotation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0016.json
---

# Field Layout

Defines reference, value, pin-name, pin-number, and auxiliary field anchors, visibility, alignment, and clearance.

> **Document ID:** `AIXEM-SYMBOL-FIELDS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-field-layout`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Reference and value fields remain independently positionable.
- Pin names and numbers use role-specific anchors.
- Optional fields declare visibility rather than disappearing implicitly.

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

<a id="AIXEM-REQ-SYMBOL-0015"></a>

### AIXEM-REQ-SYMBOL-0015 — Declared field anchors

**MUST.** Required symbol fields MUST use declared deterministic anchors and alignment rules.

- Verification mode: `automated`
- Validator: `schematic.annotation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0015.json`

<a id="AIXEM-REQ-SYMBOL-0016"></a>

### AIXEM-REQ-SYMBOL-0016 — Field clearance

**MUST.** Visible fields MUST respect the declared symbol-body, pin, and route clearance rules.

- Verification mode: `automated`
- Validator: `schematic.annotation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0016.json`

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
- [Annotations and Fields](../schematic/annotations.md) — `AIXEM-SCHEM-ANNOTATION-001`
- [Symbol Lint](symbol-lint.md) — `AIXEM-SYMBOL-LINT-001`

<a id="0-5-1-field-binding-and-placement-overrides"></a>
## Field Binding and Placement Overrides

A graphic text node becomes a bound field when it declares `field`. The symbol owns the anchor and style; the library and semantic entity provide values; the placement may apply the final instance-specific override.

### Resolution Contract

```text
renderer identity/default fields
→ presentation.fieldMap-derived values
→ semantic entity attributes
→ placement.fields overrides
→ text node field lookup
→ rendered text
```

Later layers win. A literal text node with `text` and no `field` is fixed symbol artwork. A field node should not also be used as the sole source of semantic identity.

### Standard Field Roles

| Field | Typical source | Placement guidance |
|---|---|---|
| `reference` | entity `refdes` / renderer identity field | centered above or left-above the body, outside pin channels |
| `value` | mapped rating/value property | centered below or right-below the body, outside pin channels |
| custom field | `fieldMap` to a declared component property/attribute | place according to function; document intentional internal fields |

A text primitive uses `x`, `y`, optional `rotation`, `anchor`, `baseline`, `preserveUpright`, `maxWidth`, and either `field` or `text`. The default grid-light profile keeps `reference` and `value` anchors outside body geometry.

### Placement Override Example

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

The semantic `rating` value reaches the symbol `value` field through `fieldMap`, then this placement's `fields.value` wins. That override changes only displayed presentation; it does not change component type, endpoint identity, or net membership.

### Collision and Rotation Rules

- Reserve a distinct text channel above and below the body before adding pin names.
- Increase body size or move fields; do not shorten standard leads or compress pin pitch to resolve collisions.
- Keep field anchors on the active sub-grid where practical.
- Set `preserveUpright` when readable orientation is required under placement rotation/mirroring.
- A rotated field must remain clear of the transformed body and automatic pin overlays.
- Use `maxWidth` only as a layout constraint; do not rely on clipping to hide incorrect values.

### Diagnosis Order for Wrong Text

1. Verify the text node `field` name.
2. Verify `presentation.fieldMap` direction: symbol field → semantic property/attribute.
3. Verify the semantic entity attribute value.
4. Verify whether `placement.fields` overrides it.
5. Inspect the resolved fields in `resolved-scene.json`.
6. Edit the layer that owns the wrong value or anchor; do not hard-code a workaround into reusable symbol graphics.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

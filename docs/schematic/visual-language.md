---
id: AIXEM-SCHEM-VISUAL-001
title: Grid-First Visual Language
status: normative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Defines the compact, high-contrast, original AIXEM schematic drawing language independently from Viewer application
  chrome.
authority:
- schematic-visual-language
aliases:
- visual language
- schematic style
- CAD drawing language
- schematic appearance
agent:
  priority: critical
  estimated_tokens: 1744
  intents:
  - create-schematic
  - change-architecture
  - inspect-artifact
depends_on:
- AIXEM-SCHEM-GRID-001
- AIXEM-CONCEPT-SYMBOL-001
related:
- AIXEM-SPEC-VISUAL-PROFILE-001
- AIXEM-ARCH-ADR-0003
- AIXEM-SPEC-VIEWER-001
navigation:
  group: schematic
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-UI-0001
  title: Original assets
  level: MUST
  statement: AIXEM drawing and presentation assets MUST use original code, icons, visual tokens, and symbol assets.
  validator: manual.vendor_neutral
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-UI-0001.json
- id: AIXEM-REQ-UI-0002
  title: Vendor-neutral drawing presentation
  level: MUST
  statement: AIXEM schematic presentation MUST use original functional grouping and drawing tokens without copying a
    vendor product pixel-for-pixel.
  validator: schematic.workbench
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-UI-0002.json
- id: AIXEM-REQ-UI-0003
  title: Semantic color independence
  level: MUST
  statement: Color and stroke choices MUST NOT be the sole carrier of semantic connectivity or endpoint identity.
  validator: manual.accessibility
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-UI-0003.json
---

# Grid-First Visual Language

Defines the compact, high-contrast, original AIXEM schematic drawing language independently from Viewer application chrome.

> **Document ID:** `AIXEM-SCHEM-VISUAL-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scope is `schematic-visual-language`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Straight orthogonal wires.
- Compact rectangular functional symbols.
- Clear pin rows.
- Low-distraction grid.
- Original neutral iconography.

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

<a id="AIXEM-REQ-UI-0001"></a>

### AIXEM-REQ-UI-0001 — Original assets

**MUST.** AIXEM drawing and presentation assets MUST use original code, icons, visual tokens, and symbol assets.

- Verification mode: `review`
- Validator: `manual.vendor_neutral`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-UI-0001.json`

<a id="AIXEM-REQ-UI-0002"></a>

### AIXEM-REQ-UI-0002 — Vendor-neutral drawing presentation

**MUST.** AIXEM schematic presentation MUST use original functional grouping and drawing tokens without copying a vendor product pixel-for-pixel.

- Verification mode: `automated`
- Validator: `schematic.workbench`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-UI-0002.json`

<a id="AIXEM-REQ-UI-0003"></a>

### AIXEM-REQ-UI-0003 — Semantic color independence

**MUST.** Color and stroke choices MUST NOT be the sole carrier of semantic connectivity or endpoint identity.

- Verification mode: `review`
- Validator: `manual.accessibility`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-UI-0003.json`

### Implementation notes

- Conventional CAD spatial patterns are not proprietary by themselves; AIXEM nevertheless avoids vendor logos, bundled fonts, screenshots, icon artwork, and proprietary libraries.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic drawing and compare it with machine-readable evidence.

## Related Documents

- [Grid and Snap System](grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Symbol Presentation Model](../concepts/symbol-model.md) — `AIXEM-CONCEPT-SYMBOL-001`
- [Schematic Presentation Profile 1](../specifications/schematic/visual-profile.md) — `AIXEM-SPEC-VISUAL-PROFILE-001`
- [ADR-0003: Vendor-Neutral Engineering Workbench](../architecture/adr/0003-vendor-neutral-ui.md) — `AIXEM-ARCH-ADR-0003`

<a id="0-5-1-measurable-authoring-guidance"></a>
## Measurable Authoring Guidance

### Signal Flow and Grouping

- Prefer left-to-right primary signal flow.
- Place inputs on the left and outputs on the right when functional meaning allows.
- Place supplies above and returns below ordinary functional blocks when that improves recognition.
- Group components by functional stage, not merely by insertion order.
- Align related symbols on shared grid rows/columns and keep comparable stages visually consistent.

### Spacing and Density

- Preserve at least one 5 mm pin-pitch channel between unrelated symbol bodies and adjacent route channels.
- Keep route labels away from pin names, field anchors, bends, and junction dots.
- Avoid a bend immediately adjacent to another bend when one orthogonal segment can express the route.
- Increase whitespace before shrinking symbols or suppressing useful pin text.
- Keep ordinary body dimensions and placement coordinates on the 2.5 mm grid.

### Wires and Junctions

- Minimize jog count while preserving clear grouping and avoiding symbol bodies.
- Use explicit junction dots only where one semantic net branches.
- A crossing of different nets must remain visually unjoined.
- Do not route through text or use color as the only indication of a net distinction.
- Keep branch trunks and taps visually legible; avoid multiple nearly coincident parallel wires that cannot be distinguished at normal zoom.

### Fields and Labels

- Keep reference and value fields outside the body by default.
- Preserve consistent field channels across a functional group.
- Use literal internal labels sparingly for function, not decoration.
- A displayed label may clarify a net or pin but never substitutes for semantic identity.

### Visual Review Questions

1. Can the principal signal path be read without relying on color?
2. Are power, return, and functional signal groups immediately recognizable?
3. Are all pin targets visibly coincident with their leads?
4. Are crossings and explicit joins unambiguous?
5. Do reference, value, pin name, and pin number remain readable at the default workbench zoom?
6. Does every visual defect map cleanly to one authority owner?
<a id="0-5-4-application-chrome-boundary"></a>
## Application-Chrome Boundary

This document owns the drawing language: symbol geometry, wire/junction legibility, grid treatment, labels, and color-independent semantic cues. It does not own Viewer mode controls, panels, search, inspector behavior, DOM identity, keyboard mappings, or diagnostic regions. Those behaviors are defined by [Reference Viewer Contract 1](../specifications/viewer/reference-viewer-contract.md).

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

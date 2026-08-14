---
id: AIXEM-SPEC-VISUAL-PROFILE-001
title: Schematic Presentation Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: profile
summary: Defines AIXEM schematic drawing presentation tokens, local-resource rules, readability cues, and the boundary
  that prevents presentation from changing circuit authority.
authority:
- schematic-presentation-profile
aliases:
- schematic presentation profile
- visual profile
- drawing presentation
agent:
  priority: critical
  estimated_tokens: 1483
  intents:
  - inspect-artifact
  - change-architecture
depends_on:
- AIXEM-SCHEM-VISUAL-001
related:
- AIXEM-ARCH-ADR-0003
- AIXEM-EXAMPLE-CONTROLLER-001
- AIXEM-SPEC-VIEWER-001
- AIXEM-SPEC-VIEWER-A11Y-001
navigation:
  group: specifications
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-UI-0004
  title: Local presentation assets
  level: MUST
  statement: The schematic presentation profile MUST use local or embedded presentation resources and MUST NOT require
    remote fonts, scripts, styles, or images.
  validator: schematic.remote_assets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-UI-0004.json
- id: AIXEM-REQ-UI-0005
  title: Responsive inspection
  level: MUST
  statement: Schematic evidence MUST remain visually inspectable at declared desktop and narrow review sizes without
    changing authoritative geometry or connectivity.
  validator: docs.visual_review
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-UI-0005.json
---

# Schematic Presentation Profile 1

Defines AIXEM schematic drawing presentation tokens, local-resource rules, readability cues, and the boundary that prevents presentation from changing circuit authority.

> **Document ID:** `AIXEM-SPEC-VISUAL-PROFILE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scope is `schematic-presentation-profile`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Drawing colors, strokes, joins, caps, fonts, and grid treatment remain vendor-neutral.
- Presentation resources are local or embedded.
- Presentation changes cannot move drawing authority or redefine connectivity.

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

<a id="AIXEM-REQ-UI-0004"></a>

### AIXEM-REQ-UI-0004 — Local presentation assets

**MUST.** The schematic presentation profile MUST use local or embedded presentation resources and MUST NOT require remote fonts, scripts, styles, or images.

- Verification mode: `automated`
- Validator: `schematic.remote_assets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-UI-0004.json`

<a id="AIXEM-REQ-UI-0005"></a>

### AIXEM-REQ-UI-0005 — Responsive inspection

**MUST.** Schematic evidence MUST remain visually inspectable at declared desktop and narrow review sizes without changing authoritative geometry or connectivity.

- Verification mode: `review`
- Validator: `docs.visual_review`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-UI-0005.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Grid-First Visual Language](../../schematic/visual-language.md) — `AIXEM-SCHEM-VISUAL-001`
- [ADR-0003: Vendor-Neutral Engineering Workbench](../../architecture/adr/0003-vendor-neutral-ui.md) — `AIXEM-ARCH-ADR-0003`
- [Example: Grid Controller and Sensor Interface](../../examples/grid-controller.md) — `AIXEM-EXAMPLE-CONTROLLER-001`

<a id="0-5-1-relationship-to-symbol-local-style"></a>
## Relationship to Symbol-Local Style

Style resolution follows the renderer contract and ADR 0004:

```text
renderer safe defaults
→ symbol-local deterministic fallback style
→ active project/profile role overrides
→ narrowly scoped documented instance state where supported
```

The symbol owns geometry, graphic roles/classes, and a deterministic fallback appearance. The active schematic style profile owns approved project-wide presentation tokens and role overrides. Neither layer may move a port, alter endpoint identity, change net membership, or convert a crossing into a junction.

### Schematic-Profile-Owned Presentation

The active profile may govern approved colors, stroke widths, font families/sizes, joins/caps, grid visibility and drawing-role presentation. Profile overrides should target stable roles/classes rather than opaque node IDs where possible.

### Symbol-Owned Intrinsic Facts

The symbol continues to own body shape, lead geometry, field anchors, port coordinates, visibility predicates, reusable definitions, and parameter/variant graphics. A style profile cannot repair bad geometry; the symbol must be corrected.

### Compatibility

A 0.5.0 symbol using only existing fallback style mechanisms remains valid in 0.5.1. When no profile override matches, renderer-safe and symbol-local values produce deterministic output. Any future precedence change requires a new ADR, compatibility analysis, and renderer-contract test.
<a id="0-5-4-viewer-boundary"></a>
## Viewer Boundary

This profile owns schematic drawing appearance only. Reference Viewer application chrome, state, selection behavior, viewport controls, security, and responsive panel behavior are owned by the Viewer specification family. Viewer CSS may add selection/focus presentation or hide a declared layer, but it may not move a port, component, field, route, junction, or project connection.

- [Reference Viewer Contract 1](../viewer/reference-viewer-contract.md) — `AIXEM-SPEC-VIEWER-001`
- [Viewer Accessibility Profile 1](../viewer/viewer-accessibility-profile.md) — `AIXEM-SPEC-VIEWER-A11Y-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

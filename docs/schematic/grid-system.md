---
id: AIXEM-SCHEM-GRID-001
title: Grid and Snap System
status: normative
version: '1.0'
language: en
domain: schematic
kind: guide
summary: Defines the default 2.5 mm snap grid, 10 mm major grid, coordinate precision, and permitted exceptions.
authority:
- layout-grid
- render-grid
aliases:
- grid
- snap grid
- major grid
- grid system
agent:
  priority: critical
  estimated_tokens: 1110
  intents:
  - create-schematic
  - place-component
  - route-nets
  - validate-project
depends_on:
- AIXEM-SPEC-COORD-001
related:
- AIXEM-AUTHORING-GUIDE-PLACE-COMPONENTS-001
- AIXEM-SPEC-GRID-PROFILE-001
- AIXEM-SCHEM-PLACEMENT-001
- AIXEM-ROUTE-ORTHO-001
navigation:
  group: schematic
  order: 20
artifacts:
  owns:
  - profiles/aixem-grid-schematic-style-1.aixstyle.json#/styleProfile/grid
  consumes: []
requirements:
- id: AIXEM-REQ-SCHEM-0001
  title: Default snap grid
  level: MUST
  statement: The reference schematic profile MUST use a 2.5 mm snap grid.
  validator: schematic.grid
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0001.json
- id: AIXEM-REQ-SCHEM-0002
  title: Default major grid
  level: MUST
  statement: The reference schematic profile MUST use a 10 mm major grid.
  validator: schematic.style_profile
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0002.json
- id: AIXEM-REQ-SCHEM-0003
  title: Free bend alignment
  level: MUST
  statement: Every free route bend MUST align to the permitted snap grid.
  validator: schematic.grid
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SCHEM-0003.json
---

# Grid and Snap System

Defines the default 2.5 mm snap grid, 10 mm major grid, coordinate precision, and permitted exceptions.

> **Document ID:** `AIXEM-SCHEM-GRID-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

These rules prioritize a compact, grid-aligned engineering drawing that remains unambiguous when printed or viewed without color.

The declared authority scopes are `layout-grid`, `render-grid`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The minor grid controls placement and routing.
- The major grid supports visual grouping.
- Legacy pin escapes may preserve an endpoint axis but may not introduce arbitrary free bends.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `profiles/aixem-grid-schematic-style-1.aixstyle.json#/styleProfile/grid`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-SCHEM-0001"></a>

### AIXEM-REQ-SCHEM-0001 — Default snap grid

**MUST.** The reference schematic profile MUST use a 2.5 mm snap grid.

- Verification mode: `automated`
- Validator: `schematic.grid`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0001.json`

<a id="AIXEM-REQ-SCHEM-0002"></a>

### AIXEM-REQ-SCHEM-0002 — Default major grid

**MUST.** The reference schematic profile MUST use a 10 mm major grid.

- Verification mode: `automated`
- Validator: `schematic.style_profile`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0002.json`

<a id="AIXEM-REQ-SCHEM-0003"></a>

### AIXEM-REQ-SCHEM-0003 — Free bend alignment

**MUST.** Every free route bend MUST align to the permitted snap grid.

- Verification mode: `automated`
- Validator: `schematic.grid`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SCHEM-0003.json`

## Active Grid Authority and Deterministic Snap

The active style profile `grid.snap` is schematic placement and free-route-bend authority. `layout.coordinateSystem.grid` is a serialized declaration that agrees with that value under Grid Schematic Profile 1. Symbol-local coordinate-grid metadata cannot override schematic placement or routing legality.

The reference deterministic snap uses round-half-away-from-zero relative to the declared origin. Advisory magnetic alignment has a one-`G` acquisition window and considers at most base, X, Y, and XY candidates with stable ranking. It returns a suggestion only; authoritative files are never mutated by the helper.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Coordinate and Unit System](../specifications/core/coordinate-system.md) — `AIXEM-SPEC-COORD-001`
- [Component Placement](placement.md) — `AIXEM-SCHEM-PLACEMENT-001`
- [Orthogonal Routing](../routing/orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

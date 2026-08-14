---
id: AIXEM-CONCEPT-LAYOUT-001
title: Explicit Layout Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines placement, orientation, route geometry, junction positions, labels, and annotations without changing
  circuit meaning.
authority:
- explicit-layout
aliases:
- layout model
- schematic geometry
- explicit layout
agent:
  priority: critical
  estimated_tokens: 914
  intents:
  - create-schematic
  - route-nets
  - validate-project
  - route-project-nets
depends_on:
- AIXEM-CONCEPT-SEMANTIC-001
related:
- AIXEM-FORMAT-AIXLAYOUT-001
- AIXEM-SCHEM-GRID-001
- AIXEM-SPEC-HIERARCHICAL-PORT-LAYOUT-001
navigation:
  group: concepts
  order: 70
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0022
  title: Placement closure
  level: MUST
  statement: Every semantic entity selected for presentation MUST have one valid layout placement.
  validator: schematic.placement_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0022.json
- id: AIXEM-REQ-CORE-0023
  title: Layout non-authority
  level: MUST
  statement: Layout data MUST NOT redefine entity, endpoint, or net membership.
  validator: schematic.geometry_isolation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0023.json
---

# Explicit Layout Model

Defines placement, orientation, route geometry, junction positions, labels, and annotations without changing circuit meaning.

> **Document ID:** `AIXEM-CONCEPT-LAYOUT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `explicit-layout`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Coordinates are expressed in millimetres.
- Routes bind to semantic net IDs.
- Junctions and no-connect graphics reflect explicit source intent.

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

<a id="AIXEM-REQ-CORE-0022"></a>

### AIXEM-REQ-CORE-0022 — Placement closure

**MUST.** Every semantic entity selected for presentation MUST have one valid layout placement.

- Verification mode: `automated`
- Validator: `schematic.placement_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0022.json`

<a id="AIXEM-REQ-CORE-0023"></a>

### AIXEM-REQ-CORE-0023 — Layout non-authority

**MUST.** Layout data MUST NOT redefine entity, endpoint, or net membership.

- Verification mode: `automated`
- Validator: `schematic.geometry_isolation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0023.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Semantic Circuit Model](semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [.aixlayout.json Explicit Layout](../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`
- [Grid and Snap System](../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`

## Local and Project Route Geometry

Local route geometry belongs to one `aixlayout/2` leaf and may terminate at `@PORT`. Project route geometry is derived after composition from transformed sheet-port anchors for Overview and Composite views. Neither geometry layer owns net membership, and layers remain presentation subdivisions of one sheet.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

---
id: AIXEM-SPEC-LAYOUT-001
title: Explicit Layout Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines serialized placements, connections, paths, junctions, labels, annotations, and sheet geometry.
authority:
- layout-serialization-contract
aliases:
- layout contract
- aixlayout contract
- layout specification
agent:
  priority: critical
  estimated_tokens: 954
  intents:
  - create-schematic
  - route-nets
  - validate-project
depends_on:
- AIXEM-CONCEPT-LAYOUT-001
- AIXEM-SPEC-COORD-001
related:
- AIXEM-FORMAT-AIXLAYOUT-001
navigation:
  group: specifications
  order: 80
artifacts:
  owns:
  - docs/specifications/schemas/component-graphics-1/aixem-explicit-layout-1.schema.json
  consumes: []
requirements:
- id: AIXEM-REQ-LAYOUT-0010
  title: Layout schema
  level: MUST
  statement: Every explicit layout document MUST validate against its declared schema version.
  validator: schematic.layout_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0010.json
- id: AIXEM-REQ-LAYOUT-0011
  title: Semantic binding
  level: MUST
  statement: Every placement and connection record MUST bind to an existing semantic entity or net.
  validator: schematic.layout_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0011.json
- id: AIXEM-REQ-LAYOUT-0012
  title: Explicit route geometry
  level: MUST
  statement: Every rendered wire path MUST be reproducible from stored endpoint and via geometry.
  validator: schematic.deterministic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-LAYOUT-0012.json
---

# Explicit Layout Contract 1

Defines serialized placements, connections, paths, junctions, labels, annotations, and sheet geometry.

> **Document ID:** `AIXEM-SPEC-LAYOUT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `layout-serialization-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Placements reference entity IDs.
- Connections reference net IDs.
- Paths reference declared endpoints and via points.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/specifications/schemas/component-graphics-1/aixem-explicit-layout-1.schema.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-LAYOUT-0010"></a>

### AIXEM-REQ-LAYOUT-0010 — Layout schema

**MUST.** Every explicit layout document MUST validate against its declared schema version.

- Verification mode: `automated`
- Validator: `schematic.layout_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0010.json`

<a id="AIXEM-REQ-LAYOUT-0011"></a>

### AIXEM-REQ-LAYOUT-0011 — Semantic binding

**MUST.** Every placement and connection record MUST bind to an existing semantic entity or net.

- Verification mode: `automated`
- Validator: `schematic.layout_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0011.json`

<a id="AIXEM-REQ-LAYOUT-0012"></a>

### AIXEM-REQ-LAYOUT-0012 — Explicit route geometry

**MUST.** Every rendered wire path MUST be reproducible from stored endpoint and via geometry.

- Verification mode: `automated`
- Validator: `schematic.deterministic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-LAYOUT-0012.json`

## Instance Transform and Route-Geometry Boundary

Placement scale is presentation authority. It may transform a selected symbol instance and its mapped semantic port coordinates, but it cannot change component identity, port mapping, or connectivity. The base explicit-layout schema preserves general `scaleX` / `scaleY` affine capability; the grid circuit-schematic renderer applies the narrower finite-positive-uniform policy for component instances.

A route side bound by semantic endpoint reference is resolved from the current transformed port position. Explicit point endpoints and `via` coordinates remain stored geometry. Resizing a component therefore moves the referenced endpoint deterministically without rewriting authored bends. Existing grid, endpoint-axis, and orthogonality validation determines whether those bends remain legal; an Agent reroutes only the affected geometry when they do not.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Explicit Layout Model](../../concepts/layout-model.md) — `AIXEM-CONCEPT-LAYOUT-001`
- [Coordinate and Unit System](../core/coordinate-system.md) — `AIXEM-SPEC-COORD-001`
- [.aixlayout.json Explicit Layout](../../file-formats/aixlayout.md) — `AIXEM-FORMAT-AIXLAYOUT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

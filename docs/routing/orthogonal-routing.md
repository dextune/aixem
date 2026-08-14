---
id: AIXEM-ROUTE-ORTHO-001
title: Orthogonal Routing
status: normative
version: '1.0'
language: en
domain: routing
kind: guide
summary: Defines horizontal and vertical route segments, bend placement, channel alignment, and deterministic path
  ordering.
authority:
- orthogonal-route-geometry
aliases:
- orthogonal routing
- Manhattan routing
- right-angle wires
agent:
  priority: critical
  estimated_tokens: 954
  intents:
  - route-nets
  - validate-project
depends_on:
- AIXEM-SCHEM-GRID-001
- AIXEM-ROUTE-NETS-001
related:
- AIXEM-ROUTE-CONSTRAINT-001
- AIXEM-ROUTE-CROSSING-001
navigation:
  group: routing
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ROUTE-0004
  title: Orthogonal segments
  level: MUST
  statement: Every reference-profile route segment MUST be horizontal or vertical.
  validator: schematic.orthogonal
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0004.json
- id: AIXEM-REQ-ROUTE-0005
  title: Non-zero segments
  level: MUST
  statement: A route path MUST NOT contain a zero-length segment.
  validator: schematic.orthogonal
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0005.json
- id: AIXEM-REQ-ROUTE-0006
  title: Deterministic point order
  level: MUST
  statement: Route points MUST preserve deterministic endpoint-to-endpoint ordering.
  validator: schematic.deterministic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0006.json
---

# Orthogonal Routing

Defines horizontal and vertical route segments, bend placement, channel alignment, and deterministic path ordering.

> **Document ID:** `AIXEM-ROUTE-ORTHO-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `orthogonal-route-geometry`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Two-bend and channel routes are preferred.
- Pin escape stubs align the first segment.
- Parallel buses use consistent spacing.

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

<a id="AIXEM-REQ-ROUTE-0004"></a>

### AIXEM-REQ-ROUTE-0004 — Orthogonal segments

**MUST.** Every reference-profile route segment MUST be horizontal or vertical.

- Verification mode: `automated`
- Validator: `schematic.orthogonal`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0004.json`

<a id="AIXEM-REQ-ROUTE-0005"></a>

### AIXEM-REQ-ROUTE-0005 — Non-zero segments

**MUST.** A route path MUST NOT contain a zero-length segment.

- Verification mode: `automated`
- Validator: `schematic.orthogonal`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0005.json`

<a id="AIXEM-REQ-ROUTE-0006"></a>

### AIXEM-REQ-ROUTE-0006 — Deterministic point order

**MUST.** Route points MUST preserve deterministic endpoint-to-endpoint ordering.

- Verification mode: `automated`
- Validator: `schematic.deterministic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0006.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Grid and Snap System](../schematic/grid-system.md) — `AIXEM-SCHEM-GRID-001`
- [Semantic Net Routing](net-routing.md) — `AIXEM-ROUTE-NETS-001`
- [Route Constraints](route-constraints.md) — `AIXEM-ROUTE-CONSTRAINT-001`
- [Crossings and Junctions](crossings-and-junctions.md) — `AIXEM-ROUTE-CROSSING-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

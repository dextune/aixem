---
id: AIXEM-ROUTE-CONSTRAINT-001
title: Route Constraints
status: normative
version: '1.0'
language: en
domain: routing
kind: reference
summary: Defines grid, obstacle, clearance, crossing, endpoint, and route-quality constraints.
authority:
- route-constraints
aliases:
- routing constraints
- wire rules
- route rules
agent:
  priority: critical
  estimated_tokens: 973
  intents:
  - route-nets
  - validate-project
depends_on:
- AIXEM-ROUTE-ORTHO-001
- AIXEM-SCHEM-JUNCTION-001
related:
- AIXEM-ROUTE-BEHAVIOR-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: routing
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ROUTE-0007
  title: Obstacle clearance
  level: MUST
  statement: A route MUST respect symbol body and annotation clearance constraints declared by the active profile.
  validator: schematic.route_clearance
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0007.json
- id: AIXEM-REQ-ROUTE-0008
  title: Controlled crossing
  level: MUST
  statement: A route crossing MUST have an unambiguous junction or non-junction interpretation.
  validator: schematic.junction
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0008.json
- id: AIXEM-REQ-ROUTE-0009
  title: Endpoint access
  level: MUST
  statement: A route terminal MUST meet the declared symbol port connection point without an unbound gap.
  validator: schematic.route_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-ROUTE-0009.json
---

# Route Constraints

Defines grid, obstacle, clearance, crossing, endpoint, and route-quality constraints.

> **Document ID:** `AIXEM-ROUTE-CONSTRAINT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Routing records present semantic nets; they never create net membership through geometry.

The declared authority scopes are `route-constraints`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Hard constraints determine validity.
- Soft costs improve readability.
- The route record retains explicit geometry for deterministic rendering.

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

<a id="AIXEM-REQ-ROUTE-0007"></a>

### AIXEM-REQ-ROUTE-0007 — Obstacle clearance

**MUST.** A route MUST respect symbol body and annotation clearance constraints declared by the active profile.

- Verification mode: `automated`
- Validator: `schematic.route_clearance`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0007.json`

<a id="AIXEM-REQ-ROUTE-0008"></a>

### AIXEM-REQ-ROUTE-0008 — Controlled crossing

**MUST.** A route crossing MUST have an unambiguous junction or non-junction interpretation.

- Verification mode: `automated`
- Validator: `schematic.junction`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0008.json`

<a id="AIXEM-REQ-ROUTE-0009"></a>

### AIXEM-REQ-ROUTE-0009 — Endpoint access

**MUST.** A route terminal MUST meet the declared symbol port connection point without an unbound gap.

- Verification mode: `automated`
- Validator: `schematic.route_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ROUTE-0009.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Orthogonal Routing](orthogonal-routing.md) — `AIXEM-ROUTE-ORTHO-001`
- [Junctions and Connectivity Cues](../schematic/junctions.md) — `AIXEM-SCHEM-JUNCTION-001`
- [Router Behavior](router-behavior.md) — `AIXEM-ROUTE-BEHAVIOR-001`
- [Validation Architecture](../conformance/validation.md) — `AIXEM-CONF-VALIDATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

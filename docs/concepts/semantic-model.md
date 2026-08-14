---
id: AIXEM-CONCEPT-SEMANTIC-001
title: Semantic Circuit Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines the semantic circuit as entities, endpoints, nets, and explicit no-connect intent, independent
  of geometry.
authority:
- semantic-connectivity
aliases:
- semantic model
- circuit semantics
- connectivity model
agent:
  priority: critical
  estimated_tokens: 1021
  intents:
  - create-schematic
  - validate-project
  - change-architecture
  - compose-project
depends_on: []
related:
- AIXEM-CONCEPT-NET-001
- AIXEM-FORMAT-AIXEM-001
- AIXEM-SPEC-INTERFACE-PORT-001
navigation:
  group: concepts
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0001
  title: Semantic authority
  level: MUST
  statement: Semantic source data MUST be the authority for entity, endpoint, net, and no-connect identity.
  validator: schematic.semantic
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0001.json
- id: AIXEM-REQ-CORE-0002
  title: Geometry isolation
  level: MUST
  statement: Coincident or crossing geometry MUST NOT create semantic connectivity.
  validator: schematic.geometry_isolation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0002.json
- id: AIXEM-REQ-CORE-0003
  title: Endpoint closure
  level: MUST
  statement: Every endpoint referenced by a net or no-connect declaration MUST resolve to a declared semantic endpoint.
  validator: schematic.endpoint_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0003.json
---

# Semantic Circuit Model

Defines the semantic circuit as entities, endpoints, nets, and explicit no-connect intent, independent of geometry.

> **Document ID:** `AIXEM-CONCEPT-SEMANTIC-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `semantic-connectivity`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Entity IDs are stable within a source model.
- Endpoint references use explicit entity and port identity.
- No-connect is a semantic declaration rather than a drawn mark.

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

<a id="AIXEM-REQ-CORE-0001"></a>

### AIXEM-REQ-CORE-0001 — Semantic authority

**MUST.** Semantic source data MUST be the authority for entity, endpoint, net, and no-connect identity.

- Verification mode: `automated`
- Validator: `schematic.semantic`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0001.json`

<a id="AIXEM-REQ-CORE-0002"></a>

### AIXEM-REQ-CORE-0002 — Geometry isolation

**MUST.** Coincident or crossing geometry MUST NOT create semantic connectivity.

- Verification mode: `automated`
- Validator: `schematic.geometry_isolation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0002.json`

<a id="AIXEM-REQ-CORE-0003"></a>

### AIXEM-REQ-CORE-0003 — Endpoint closure

**MUST.** Every endpoint referenced by a net or no-connect declaration MUST resolve to a declared semantic endpoint.

- Verification mode: `automated`
- Validator: `schematic.endpoint_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Net Model](net-model.md) — `AIXEM-CONCEPT-NET-001`
- [.aixem Semantic Source](../file-formats/aixem.md) — `AIXEM-FORMAT-AIXEM-001`

## Interface Boundary Semantics

Under `hierarchical.interface@1`, a top-level interface port is a first-class semantic endpoint owned by one leaf model. The project may compose that endpoint with another sheet, but it cannot change the local net that owns it. Resolved identity is qualified as `interface:<sheet-id>:<port-id>`. See [Interface Port Contract 1](../specifications/core/interface-port-contract.md).

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

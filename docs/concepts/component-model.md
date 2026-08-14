---
id: AIXEM-CONCEPT-COMPONENT-001
title: Component Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Defines component types, instances, properties, endpoints, and presentation bindings.
authority:
- component-definition
aliases:
- component model
- component type
- component instance
agent:
  priority: critical
  estimated_tokens: 1108
  intents:
  - create-schematic
  - create-symbol
  - validate-project
depends_on:
- AIXEM-CONCEPT-SEMANTIC-001
related:
- AIXEM-SPEC-PIN-ELECTRICAL-SEMANTICS-001
- AIXEM-SPEC-LIBRARY-LAYOUT-001
- AIXEM-FORMAT-AIXLIB-001
- AIXEM-CONCEPT-SYMBOL-001
navigation:
  group: concepts
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0010
  title: Type closure
  level: MUST
  statement: Every semantic component instance MUST resolve to exactly one component type in a locked library.
  validator: schematic.component_type_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0010.json
- id: AIXEM-REQ-CORE-0011
  title: Endpoint identity
  level: MUST
  statement: Component endpoint IDs MUST be stable and MUST NOT be inferred from visual pin order.
  validator: schematic.endpoint_closure
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0011.json
- id: AIXEM-REQ-CORE-0012
  title: Presentation binding
  level: MUST
  statement: Every presentation port MUST map deterministically to a semantic endpoint.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0012.json
---

# Component Model

Defines component types, instances, properties, endpoints, and presentation bindings.

> **Document ID:** `AIXEM-CONCEPT-COMPONENT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `component-definition`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Component types own electrical interfaces.
- Instances own reference and property values.
- Symbols render component endpoints but do not redefine them.

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

<a id="AIXEM-REQ-CORE-0010"></a>

### AIXEM-REQ-CORE-0010 — Type closure

**MUST.** Every semantic component instance MUST resolve to exactly one component type in a locked library.

- Verification mode: `automated`
- Validator: `schematic.component_type_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0010.json`

<a id="AIXEM-REQ-CORE-0011"></a>

### AIXEM-REQ-CORE-0011 — Endpoint identity

**MUST.** Component endpoint IDs MUST be stable and MUST NOT be inferred from visual pin order.

- Verification mode: `automated`
- Validator: `schematic.endpoint_closure`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0011.json`

<a id="AIXEM-REQ-CORE-0012"></a>

### AIXEM-REQ-CORE-0012 — Presentation binding

**MUST.** Every presentation port MUST map deterministically to a semantic endpoint.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0012.json`

## Identity, Path, and Pin-Semantics Boundary

A component ID and its locked library identity are semantic authority. A filesystem path is a retrieval and packaging location; moving a file does not silently redefine the component. New authored assets use the canonical `library/<domain>/...` tree, while safe legacy paths remain readable and explicitly repairable.

For each component port, `type` describes basic electrical connection behavior. Optional `metadata.pinSemantics` describes orthogonal function, signal class, polarity, pair membership, power-domain hints, capabilities, and alternate functions. Symbol position and display labels never replace stable component-port IDs or redefine these semantics.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Semantic Circuit Model](semantic-model.md) — `AIXEM-CONCEPT-SEMANTIC-001`
- [.aixlib.json Component Library](../file-formats/aixlib.md) — `AIXEM-FORMAT-AIXLIB-001`
- [Symbol Presentation Model](symbol-model.md) — `AIXEM-CONCEPT-SYMBOL-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

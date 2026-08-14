---
id: AIXEM-SYMBOL-ANATOMY-001
title: Symbol Anatomy
status: normative
version: '1.0'
language: en
domain: symbols
kind: concept
summary: Defines symbol coordinate space, body bounds, ports, labels, fields, anchors, variants, and reusable definitions.
authority:
- symbol-structure
aliases:
- symbol anatomy
- symbol structure
- symbol parts
agent:
  priority: critical
  estimated_tokens: 951
  intents:
  - create-symbol
depends_on:
- AIXEM-CONCEPT-SYMBOL-001
related:
- AIXEM-SYMBOL-PORTS-001
- AIXEM-SYMBOL-PRIMITIVES-001
navigation:
  group: symbols
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SYMBOL-0001
  title: Declared bounds
  level: MUST
  statement: Every symbol asset MUST declare deterministic bounds and an origin.
  validator: schematic.symbol_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0001.json
- id: AIXEM-REQ-SYMBOL-0002
  title: Port closure
  level: MUST
  statement: Every visible symbol port MUST have a unique port ID and a valid endpoint binding.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0002.json
- id: AIXEM-REQ-SYMBOL-0003
  title: Grid-compatible anchors
  level: MUST
  statement: Port and field anchors MUST be compatible with the active schematic grid profile.
  validator: schematic.symbol_grid
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SYMBOL-0003.json
---

# Symbol Anatomy

Defines symbol coordinate space, body bounds, ports, labels, fields, anchors, variants, and reusable definitions.

> **Document ID:** `AIXEM-SYMBOL-ANATOMY-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Symbol graphics are presentation assets. Endpoint identity remains owned by the component and semantic layers.

The declared authority scopes are `symbol-structure`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Local coordinates make symbols reusable.
- The origin is a placement anchor.
- Bounds support collision and field placement checks.

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

<a id="AIXEM-REQ-SYMBOL-0001"></a>

### AIXEM-REQ-SYMBOL-0001 — Declared bounds

**MUST.** Every symbol asset MUST declare deterministic bounds and an origin.

- Verification mode: `automated`
- Validator: `schematic.symbol_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0001.json`

<a id="AIXEM-REQ-SYMBOL-0002"></a>

### AIXEM-REQ-SYMBOL-0002 — Port closure

**MUST.** Every visible symbol port MUST have a unique port ID and a valid endpoint binding.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0002.json`

<a id="AIXEM-REQ-SYMBOL-0003"></a>

### AIXEM-REQ-SYMBOL-0003 — Grid-compatible anchors

**MUST.** Port and field anchors MUST be compatible with the active schematic grid profile.

- Verification mode: `automated`
- Validator: `schematic.symbol_grid`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SYMBOL-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated schematic or workbench and compare it with machine-readable evidence.

## Related Documents

- [Symbol Presentation Model](../concepts/symbol-model.md) — `AIXEM-CONCEPT-SYMBOL-001`
- [Pins, Ports, and Endpoint Mapping](pins-and-ports.md) — `AIXEM-SYMBOL-PORTS-001`
- [Graphic Primitives](primitives.md) — `AIXEM-SYMBOL-PRIMITIVES-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

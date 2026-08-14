---
id: AIXEM-CONCEPT-SYMBOL-001
title: Symbol Presentation Model
status: normative
version: '1.0'
language: en
domain: concepts
kind: concept
summary: Explains symbol assets as deterministic graphic presentations of component endpoints and fields.
authority:
- symbol-presentation
aliases:
- symbol model
- schematic symbol
- graphic symbol
agent:
  priority: critical
  estimated_tokens: 823
  intents:
  - create-symbol
  - create-schematic
depends_on:
- AIXEM-CONCEPT-COMPONENT-001
related:
- AIXEM-SYMBOL-ANATOMY-001
- AIXEM-FORMAT-AIXSYM-001
navigation:
  group: concepts
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-CORE-0020
  title: Independent symbol assets
  level: MUST
  statement: Symbol geometry MUST be authored independently from proprietary vendor libraries and screenshots.
  validator: manual.vendor_neutral
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0020.json
- id: AIXEM-REQ-CORE-0021
  title: Deterministic port map
  level: MUST
  statement: A symbol port map MUST resolve each visible port to exactly one semantic endpoint.
  validator: schematic.port_mapping
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-CORE-0021.json
---

# Symbol Presentation Model

Explains symbol assets as deterministic graphic presentations of component endpoints and fields.

> **Document ID:** `AIXEM-CONCEPT-SYMBOL-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The model described here is independent from any particular renderer or workbench implementation.

The declared authority scopes are `symbol-presentation`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Body primitives are separate from ports.
- Fields have deterministic anchors.
- Variants preserve endpoint identity unless explicitly versioned.

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

<a id="AIXEM-REQ-CORE-0020"></a>

### AIXEM-REQ-CORE-0020 — Independent symbol assets

**MUST.** Symbol geometry MUST be authored independently from proprietary vendor libraries and screenshots.

- Verification mode: `review`
- Validator: `manual.vendor_neutral`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0020.json`

<a id="AIXEM-REQ-CORE-0021"></a>

### AIXEM-REQ-CORE-0021 — Deterministic port map

**MUST.** A symbol port map MUST resolve each visible port to exactly one semantic endpoint.

- Verification mode: `automated`
- Validator: `schematic.port_mapping`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CORE-0021.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.

## Related Documents

- [Component Model](component-model.md) — `AIXEM-CONCEPT-COMPONENT-001`
- [Symbol Anatomy](../symbols/symbol-anatomy.md) — `AIXEM-SYMBOL-ANATOMY-001`
- [.aixsym.json Symbol Asset](../file-formats/aixsym.md) — `AIXEM-FORMAT-AIXSYM-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

---
id: AIXEM-ARCH-SYSTEM-001
title: System Overview
status: normative
version: '1.0'
language: en
domain: architecture
kind: architecture
summary: Defines the major bounded components and the interfaces between documentation authoring, agent retrieval,
  schematic rendering, conformance, and release packaging.
authority:
- system-architecture
aliases:
- system overview
- architecture overview
- AIXEM components
agent:
  priority: critical
  estimated_tokens: 897
  intents:
  - change-architecture
  - inspect-artifact
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
related:
- AIXEM-ARCH-PIPELINE-001
- AIXEM-ARCH-ARTIFACT-001
navigation:
  group: architecture
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ARCH-0001
  title: Bounded components
  level: MUST
  statement: The platform MUST separate canonical authoring, compilation, validation, publication, and consumption
    responsibilities.
  validator: manual.architecture
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0001.json
- id: AIXEM-REQ-ARCH-0002
  title: Static consumer outputs
  level: MUST
  statement: The official documentation site and compiled agent indexes MUST be consumable without a runtime database
    or required remote service.
  validator: docs.site
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0002.json
---

# System Overview

Defines the major bounded components and the interfaces between documentation authoring, agent retrieval, schematic rendering, conformance, and release packaging.

> **Document ID:** `AIXEM-ARCH-SYSTEM-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `system-architecture`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Docs compiler owns derived indexes.
- Renderer owns deterministic schematic presentation.
- Validators consume authoritative sources and emit evidence.
- Release packaging occurs only after integrity checks.

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

<a id="AIXEM-REQ-ARCH-0001"></a>

### AIXEM-REQ-ARCH-0001 — Bounded components

**MUST.** The platform MUST separate canonical authoring, compilation, validation, publication, and consumption responsibilities.

- Verification mode: `review`
- Validator: `manual.architecture`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0001.json`

<a id="AIXEM-REQ-ARCH-0002"></a>

### AIXEM-REQ-ARCH-0002 — Static consumer outputs

**MUST.** The official documentation site and compiled agent indexes MUST be consumable without a runtime database or required remote service.

- Verification mode: `automated`
- Validator: `docs.site`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0002.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority Model](../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Build and Authoring Pipeline](pipeline.md) — `AIXEM-ARCH-PIPELINE-001`
- [Artifact Ownership and Storage](artifact-store.md) — `AIXEM-ARCH-ARTIFACT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

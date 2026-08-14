---
id: AIXEM-ARCH-ARTIFACT-001
title: Artifact Ownership and Storage
status: normative
version: '1.0'
language: en
domain: architecture
kind: architecture
summary: Defines repository locations, artifact ownership metadata, generated boundaries, and content-addressed
  integrity relationships.
authority:
- artifact-storage
aliases:
- artifact store
- artifact ownership
- repository layout
agent:
  priority: critical
  estimated_tokens: 861
  intents:
  - inspect-artifact
  - change-architecture
  - publish-release
depends_on:
- AIXEM-SPEC-AUTHORITY-001
related:
- AIXEM-FORMAT-INDEX-001
- AIXEM-SPEC-RELEASE-001
navigation:
  group: architecture
  order: 40
artifacts:
  owns:
  - docs/_meta/generated/artifact-map.json
  consumes: []
requirements:
- id: AIXEM-REQ-ARCH-0010
  title: Canonical location
  level: MUST
  statement: Authored documentation rules MUST reside under docs/ or an explicitly declared root governance file.
  validator: docs.canonical_root
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0010.json
- id: AIXEM-REQ-ARCH-0011
  title: Generated boundary
  level: MUST
  statement: Generated indexes, compatibility references, site pages, evidence, and manifests MUST reside in declared
    generated locations.
  validator: docs.generated_locations
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0011.json
---

# Artifact Ownership and Storage

Defines repository locations, artifact ownership metadata, generated boundaries, and content-addressed integrity relationships.

> **Document ID:** `AIXEM-ARCH-ARTIFACT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `artifact-storage`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Paths communicate lifecycle.
- Stable IDs decouple identity from path.
- SHA-256 records close release integrity.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/_meta/generated/artifact-map.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-ARCH-0010"></a>

### AIXEM-REQ-ARCH-0010 — Canonical location

**MUST.** Authored documentation rules MUST reside under docs/ or an explicitly declared root governance file.

- Verification mode: `automated`
- Validator: `docs.canonical_root`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0010.json`

<a id="AIXEM-REQ-ARCH-0011"></a>

### AIXEM-REQ-ARCH-0011 — Generated boundary

**MUST.** Generated indexes, compatibility references, site pages, evidence, and manifests MUST reside in declared generated locations.

- Verification mode: `automated`
- Validator: `docs.generated_locations`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0011.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority and Precedence](../specifications/core/authority-precedence.md) — `AIXEM-SPEC-AUTHORITY-001`
- [File Formats](../file-formats/index.md) — `AIXEM-FORMAT-INDEX-001`
- [Documentation Release Integrity 1](../specifications/documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

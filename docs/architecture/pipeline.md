---
id: AIXEM-ARCH-PIPELINE-001
title: Build and Authoring Pipeline
status: normative
version: '1.0'
language: en
domain: architecture
kind: architecture
summary: Defines the ordered pipeline from canonical changes through compilation, validation, visual review, evidence,
  manifest, and archive.
authority:
- build-pipeline
aliases:
- pipeline
- build pipeline
- authoring pipeline
agent:
  priority: critical
  estimated_tokens: 866
  intents:
  - build-documentation
  - publish-release
  - change-architecture
depends_on:
- AIXEM-ARCH-SYSTEM-001
- AIXEM-CONCEPT-DETERMINISM-001
related:
- AIXEM-CONF-RELEASE-001
- AIXEM-GOV-RELEASE-001
navigation:
  group: architecture
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ARCH-0003
  title: Ordered generation
  level: MUST
  statement: Canonical validation MUST precede generated-index compilation, site publication, and release manifest
    creation.
  validator: docs.pipeline
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0003.json
- id: AIXEM-REQ-ARCH-0004
  title: Manifest last
  level: MUST
  statement: The internal release manifest MUST be created after all covered release artifacts and evidence are
    finalized.
  validator: docs.manifest
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0004.json
---

# Build and Authoring Pipeline

Defines the ordered pipeline from canonical changes through compilation, validation, visual review, evidence, manifest, and archive.

> **Document ID:** `AIXEM-ARCH-PIPELINE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `build-pipeline`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Build pipeline.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Edit canonical source
2. Validate metadata and relationships
3. Compile agent and compatibility indexes
4. Build the static site
5. Render executable examples
6. Run conformance tests
7. Review presentation
8. Write evidence and reports
9. Create and verify the release manifest
10. Create and verify the archive

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-ARCH-0003"></a>

### AIXEM-REQ-ARCH-0003 — Ordered generation

**MUST.** Canonical validation MUST precede generated-index compilation, site publication, and release manifest creation.

- Verification mode: `automated`
- Validator: `docs.pipeline`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0003.json`

<a id="AIXEM-REQ-ARCH-0004"></a>

### AIXEM-REQ-ARCH-0004 — Manifest last

**MUST.** The internal release manifest MUST be created after all covered release artifacts and evidence are finalized.

- Verification mode: `automated`
- Validator: `docs.manifest`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0004.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [System Overview](system-overview.md) — `AIXEM-ARCH-SYSTEM-001`
- [Deterministic Builds](../concepts/deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`
- [Release Gates](../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
- [Release Process](../governance/release-process.md) — `AIXEM-GOV-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

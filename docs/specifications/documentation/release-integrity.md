---
id: AIXEM-SPEC-RELEASE-001
title: Documentation Release Integrity 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines generated-index freshness, link closure, requirement evidence, static-site integrity, manifests,
  and archive verification.
authority:
- documentation-release-integrity
aliases:
- release integrity
- documentation release gate
- manifest rules
agent:
  priority: critical
  estimated_tokens: 1241
  intents:
  - publish-release
  - build-documentation
  - validate-project
depends_on:
- AIXEM-CONCEPT-DETERMINISM-001
- AIXEM-SPEC-METADATA-001
related:
- AIXEM-CONF-RELEASE-001
- AIXEM-GOV-RELEASE-001
navigation:
  group: specifications
  order: 120
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-DOCS-0020
  title: Generated freshness
  level: MUST
  statement: Generated indexes, compatibility references, and site pages MUST match the current canonical source
    digest.
  validator: docs.generated_freshness
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0020.json
- id: AIXEM-REQ-DOCS-0021
  title: Link closure
  level: MUST
  statement: Canonical Markdown and generated static-site internal links MUST resolve to an existing target and
    anchor.
  validator: docs.links
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0021.json
- id: AIXEM-REQ-DOCS-0022
  title: Traceability coverage
  level: MUST
  statement: Every normative requirement MUST have a validator, test reference, and release evidence artifact.
  validator: docs.requirements
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0022.json
- id: AIXEM-REQ-DOCS-0023
  title: Release manifest
  level: MUST
  statement: Every shipped file covered by the release policy MUST appear in a verified SHA-256 manifest.
  validator: docs.manifest
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0023.json
- id: AIXEM-REQ-DOCS-0024
  title: Declared artifact existence
  level: MUST
  statement: A release MUST fail when an authored document declares an artifact path that is absent from the package.
  validator: docs.artifact_existence
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0024.json
---

# Documentation Release Integrity 1

Defines generated-index freshness, link closure, requirement evidence, static-site integrity, manifests, and archive verification.

> **Document ID:** `AIXEM-SPEC-RELEASE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `documentation-release-integrity`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The site and agent indexes share the same source digest.
- Manifest verification runs after all generated evidence is written.
- The archive has a separate external checksum.

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

<a id="AIXEM-REQ-DOCS-0020"></a>

### AIXEM-REQ-DOCS-0020 — Generated freshness

**MUST.** Generated indexes, compatibility references, and site pages MUST match the current canonical source digest.

- Verification mode: `automated`
- Validator: `docs.generated_freshness`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0020.json`

<a id="AIXEM-REQ-DOCS-0021"></a>

### AIXEM-REQ-DOCS-0021 — Link closure

**MUST.** Canonical Markdown and generated static-site internal links MUST resolve to an existing target and anchor.

- Verification mode: `automated`
- Validator: `docs.links`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0021.json`

<a id="AIXEM-REQ-DOCS-0022"></a>

### AIXEM-REQ-DOCS-0022 — Traceability coverage

**MUST.** Every normative requirement MUST have a validator, test reference, and release evidence artifact.

- Verification mode: `automated`
- Validator: `docs.requirements`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0022.json`

<a id="AIXEM-REQ-DOCS-0023"></a>

### AIXEM-REQ-DOCS-0023 — Release manifest

**MUST.** Every shipped file covered by the release policy MUST appear in a verified SHA-256 manifest.

- Verification mode: `automated`
- Validator: `docs.manifest`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0023.json`

<a id="AIXEM-REQ-DOCS-0024"></a>

### AIXEM-REQ-DOCS-0024 — Declared artifact existence

**MUST.** A release MUST fail when an authored document declares an artifact path that is absent from the package.

- Verification mode: `automated`
- Validator: `docs.artifact_existence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0024.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Deterministic Builds](../../concepts/deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`
- [Documentation Metadata Contract 1](metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Release Gates](../../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
- [Release Process](../../governance/release-process.md) — `AIXEM-GOV-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

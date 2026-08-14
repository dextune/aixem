---
id: AIXEM-SPEC-DOCUMENT-001
title: Canonical Document Model
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines canonical document identity, metadata, status, language, authority, dependencies, aliases, agent
  intents, and navigation order.
authority:
- canonical-document-contract
aliases:
- document model
- canonical docs
- front matter contract
agent:
  priority: critical
  estimated_tokens: 933
  intents:
  - build-documentation
  - change-architecture
  - publish-release
depends_on: []
related:
- AIXEM-SPEC-METADATA-001
- AIXEM-GOV-VERSIONING-001
navigation:
  group: specifications
  order: 20
artifacts:
  owns:
  - docs/_meta/schema/document-metadata.schema.json
  consumes: []
requirements:
- id: AIXEM-REQ-DOCS-0001
  title: Metadata presence
  level: MUST
  statement: Every canonical Markdown document MUST contain front matter that validates against the active document
    metadata schema.
  validator: docs.metadata
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0001.json
- id: AIXEM-REQ-DOCS-0002
  title: Stable unique ID
  level: MUST
  statement: Every canonical document MUST have a repository-unique stable ID.
  validator: docs.unique_ids
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0002.json
- id: AIXEM-REQ-DOCS-0003
  title: English release language
  level: MUST
  statement: Every 0.5 canonical document and generated documentation page MUST be written in English.
  validator: docs.english
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0003.json
---

# Canonical Document Model

Defines canonical document identity, metadata, status, language, authority, dependencies, aliases, agent intents, and navigation order.

> **Document ID:** `AIXEM-SPEC-DOCUMENT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `canonical-document-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Paths may change while IDs remain stable.
- Status separates normative and informative material.
- Dependencies are stable-ID edges.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/_meta/schema/document-metadata.schema.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-DOCS-0001"></a>

### AIXEM-REQ-DOCS-0001 — Metadata presence

**MUST.** Every canonical Markdown document MUST contain front matter that validates against the active document metadata schema.

- Verification mode: `automated`
- Validator: `docs.metadata`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0001.json`

<a id="AIXEM-REQ-DOCS-0002"></a>

### AIXEM-REQ-DOCS-0002 — Stable unique ID

**MUST.** Every canonical document MUST have a repository-unique stable ID.

- Verification mode: `automated`
- Validator: `docs.unique_ids`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0002.json`

<a id="AIXEM-REQ-DOCS-0003"></a>

### AIXEM-REQ-DOCS-0003 — English release language

**MUST.** Every 0.5 canonical document and generated documentation page MUST be written in English.

- Verification mode: `automated`
- Validator: `docs.english`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Documentation Metadata Contract 1](../documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Versioning Policy](../../governance/versioning.md) — `AIXEM-GOV-VERSIONING-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

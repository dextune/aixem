---
id: AIXEM-SPEC-METADATA-001
title: Documentation Metadata Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines the JSON Schema and semantic rules for canonical Markdown front matter.
authority:
- documentation-metadata-contract
aliases:
- metadata contract
- front matter schema
- document schema
agent:
  priority: critical
  estimated_tokens: 1183
  intents:
  - build-documentation
  - publish-release
depends_on:
- AIXEM-SPEC-DOCUMENT-001
related:
- AIXEM-AGENT-ROUTES-001
- AIXEM-SPEC-DOC-GOVERNANCE-001
navigation:
  group: specifications
  order: 110
artifacts:
  owns:
  - docs/_meta/schema/document-metadata.schema.json
  consumes: []
requirements:
- id: AIXEM-REQ-DOCS-0010
  title: Required metadata fields
  level: MUST
  statement: Document metadata MUST include identity, status, version, language, domain, kind, summary, authority,
    aliases, agent policy, relationships, navigation, artifacts, and requirements.
  validator: docs.metadata
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0010.json
- id: AIXEM-REQ-DOCS-0011
  title: Resolvable relationships
  level: MUST
  statement: Every depends_on and related document ID MUST resolve to a canonical document.
  validator: docs.dependencies
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0011.json
- id: AIXEM-REQ-DOCS-0012
  title: Unique requirements
  level: MUST
  statement: Every normative requirement ID MUST be unique across the repository.
  validator: docs.requirements
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0012.json
---

# Documentation Metadata Contract 1

Defines the JSON Schema and semantic rules for canonical Markdown front matter.

> **Document ID:** `AIXEM-SPEC-METADATA-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `documentation-metadata-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Metadata is authored with the document.
- The compiler extracts graph edges.
- Schema validity is necessary but semantic checks are also applied.

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

<a id="AIXEM-REQ-DOCS-0010"></a>

### AIXEM-REQ-DOCS-0010 — Required metadata fields

**MUST.** Document metadata MUST include identity, status, version, language, domain, kind, summary, authority, aliases, agent policy, relationships, navigation, artifacts, and requirements.

- Verification mode: `automated`
- Validator: `docs.metadata`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0010.json`

<a id="AIXEM-REQ-DOCS-0011"></a>

### AIXEM-REQ-DOCS-0011 — Resolvable relationships

**MUST.** Every depends_on and related document ID MUST resolve to a canonical document.

- Verification mode: `automated`
- Validator: `docs.dependencies`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0011.json`

<a id="AIXEM-REQ-DOCS-0012"></a>

### AIXEM-REQ-DOCS-0012 — Unique requirements

**MUST.** Every normative requirement ID MUST be unique across the repository.

- Verification mode: `automated`
- Validator: `docs.requirements`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0012.json`

## Controlled Classification Vocabulary

`domain` identifies the durable information-architecture area and `kind` identifies the document's semantic role. Both values are closed enumerations in the metadata schema. A new value requires an information-architecture review, navigation ownership, and a durable category; it cannot be introduced for one file.

The controlled `kind` set is `index`, `specification`, `contract`, `profile`, `policy`, `reference`, `guide`, `cookbook`, `concept`, `architecture`, `adr`, `conformance`, `release-note`, and `example`. Legacy near-synonyms are normalized to these values according to actual authority, not by filename alone.

`agent.estimated_tokens` is an authored retrieval hint checked against a deterministic UTF-8 body-size estimate. Route byte limits remain authoritative; the estimate is not a claim about any vendor tokenizer.

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Canonical Document Model](../core/document-model.md) — `AIXEM-SPEC-DOCUMENT-001`
- [Task Routes](../../agent/task-routing.md) — `AIXEM-AGENT-ROUTES-001`
- [Repository Document Governance Contract 1](document-governance-contract.md) — `AIXEM-SPEC-DOC-GOVERNANCE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

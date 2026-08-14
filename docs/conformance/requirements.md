---
id: AIXEM-CONF-REQUIREMENTS-001
title: Requirement Model
status: normative
version: '1.0'
language: en
domain: conformance
kind: reference
summary: Defines requirement IDs, levels, statements, verification modes, validator and test references, evidence
  paths, and status.
authority:
- requirement-model
aliases:
- requirements
- requirement IDs
- normative rules
agent:
  priority: critical
  estimated_tokens: 934
  intents:
  - validate-project
  - build-documentation
  - publish-release
depends_on: []
related:
- AIXEM-SPEC-METADATA-001
- AIXEM-CONF-VALIDATION-001
navigation:
  group: conformance
  order: 20
artifacts:
  owns:
  - docs/_meta/generated/requirement-traceability.json
  consumes: []
requirements:
- id: AIXEM-REQ-CONF-0001
  title: Stable requirement ID
  level: MUST
  statement: A normative requirement MUST have a stable repository-unique AIXEM-REQ-* identifier.
  validator: docs.requirements
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0001.json
- id: AIXEM-REQ-CONF-0002
  title: Verification declaration
  level: MUST
  statement: A requirement MUST declare a verification mode, validator, test reference, and evidence path.
  validator: docs.requirements
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0002.json
- id: AIXEM-REQ-CONF-0003
  title: Body presence
  level: MUST
  statement: The canonical body MUST expose every requirement ID declared in front matter.
  validator: docs.requirement_body
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-CONF-0003.json
---

# Requirement Model

Defines requirement IDs, levels, statements, verification modes, validator and test references, evidence paths, and status.

> **Document ID:** `AIXEM-CONF-REQUIREMENTS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Conformance is demonstrated by observed evidence from a specific release build, not by a prose claim alone.

The declared authority scopes are `requirement-model`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- MUST requirements are release gates.
- Review-mode evidence is distinguished from automated evidence.
- Traceability output links the full chain.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/_meta/generated/requirement-traceability.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-CONF-0001"></a>

### AIXEM-REQ-CONF-0001 — Stable requirement ID

**MUST.** A normative requirement MUST have a stable repository-unique AIXEM-REQ-* identifier.

- Verification mode: `automated`
- Validator: `docs.requirements`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0001.json`

<a id="AIXEM-REQ-CONF-0002"></a>

### AIXEM-REQ-CONF-0002 — Verification declaration

**MUST.** A requirement MUST declare a verification mode, validator, test reference, and evidence path.

- Verification mode: `automated`
- Validator: `docs.requirements`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0002.json`

<a id="AIXEM-REQ-CONF-0003"></a>

### AIXEM-REQ-CONF-0003 — Body presence

**MUST.** The canonical body MUST expose every requirement ID declared in front matter.

- Verification mode: `automated`
- Validator: `docs.requirement_body`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-CONF-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Documentation Metadata Contract 1](../specifications/documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [Validation Architecture](validation.md) — `AIXEM-CONF-VALIDATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

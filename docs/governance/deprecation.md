---
id: AIXEM-GOV-DEPRECATION-001
title: Deprecation Policy
status: normative
version: '1.0'
language: en
domain: governance
kind: policy
summary: Defines deprecated status, replacement pointers, warning periods, compatibility output, and eventual removal
  criteria.
authority:
- deprecation-policy
aliases:
- deprecation
- obsolete documents
- replacement policy
agent:
  priority: critical
  estimated_tokens: 832
  intents:
  - change-architecture
  - migrate-baseline
depends_on:
- AIXEM-GOV-VERSIONING-001
related:
- AIXEM-CONF-COMPAT-001
navigation:
  group: governance
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-GOV-0020
  title: Replacement or rationale
  level: MUST
  statement: A deprecated canonical document MUST identify a replacement document ID or a terminal deprecation rationale.
  validator: docs.deprecation
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0020.json
- id: AIXEM-REQ-GOV-0021
  title: Discoverability
  level: MUST
  statement: Deprecated IDs and aliases MUST remain resolvable during the declared compatibility window.
  validator: route.aliases
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0021.json
---

# Deprecation Policy

Defines deprecated status, replacement pointers, warning periods, compatibility output, and eventual removal criteria.

> **Document ID:** `AIXEM-GOV-DEPRECATION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `deprecation-policy`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Deprecation is not silent deletion.
- Status is machine-readable.
- Migration maps preserve historical lookup.

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

<a id="AIXEM-REQ-GOV-0020"></a>

### AIXEM-REQ-GOV-0020 — Replacement or rationale

**MUST.** A deprecated canonical document MUST identify a replacement document ID or a terminal deprecation rationale.

- Verification mode: `automated`
- Validator: `docs.deprecation`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0020.json`

<a id="AIXEM-REQ-GOV-0021"></a>

### AIXEM-REQ-GOV-0021 — Discoverability

**MUST.** Deprecated IDs and aliases MUST remain resolvable during the declared compatibility window.

- Verification mode: `automated`
- Validator: `route.aliases`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0021.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Versioning Policy](versioning.md) — `AIXEM-GOV-VERSIONING-001`
- [Compatibility and Migration Conformance](../conformance/compatibility-conformance.md) — `AIXEM-CONF-COMPAT-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

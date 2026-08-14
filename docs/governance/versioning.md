---
id: AIXEM-GOV-VERSIONING-001
title: Versioning Policy
status: normative
version: '1.0'
language: en
domain: governance
kind: policy
summary: Defines release, document, schema, profile, route-index, and artifact compatibility versioning.
authority:
- versioning-policy
aliases:
- versioning
- semantic versioning
- document versions
agent:
  priority: critical
  estimated_tokens: 1113
  intents:
  - change-architecture
  - publish-release
depends_on: []
related:
- AIXEM-GOV-COMPAT-001
- AIXEM-GOV-DEPRECATION-001
navigation:
  group: governance
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-GOV-0001
  title: Release version
  level: MUST
  statement: A published release MUST have one explicit numeric release version using two to four dot-separated components and one immutable release identifier.
  validator: docs.release_metadata
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0001.json
- id: AIXEM-REQ-GOV-0002
  title: Stable document identity
  level: MUST
  statement: Moving or renaming a published canonical document MUST NOT change its stable document ID.
  validator: docs.unique_ids
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0002.json
- id: AIXEM-REQ-GOV-0003
  title: Breaking format version
  level: MUST
  statement: An incompatible serialized-format change MUST increment the declared format or schema version and provide migration guidance.
  validator: manual.compatibility
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0003.json
---
# Versioning Policy

Defines release, document, schema, profile, route-index, and artifact compatibility versioning.

> **Document ID:** `AIXEM-GOV-VERSIONING-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `versioning-policy`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Repository release version and format versions are separate.
- Document versions track normative content.
- Generated index formats declare their own schema identifiers.

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

<a id="AIXEM-REQ-GOV-0001"></a>

### AIXEM-REQ-GOV-0001 — Release version

**MUST.** A published release MUST have one explicit numeric release version using two to four dot-separated components and one immutable release identifier.

- Verification mode: `automated`
- Validator: `docs.release_metadata`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0001.json`

### Repository release version form

Repository release identity uses `major.minor`, `major.minor.patch`, or `major.minor.patch.maintenance`. The optional fourth component is reserved for a compatible correction or hardening release that does not imply a serialized-format revision. Format, schema, profile, protocol, and document versions remain independently governed and must not be inferred from the repository release component count.

A release directory, canonical release note, validation directory, release metadata record, and immutable release identifier must use the exact same version string.

<a id="AIXEM-REQ-GOV-0002"></a>

### AIXEM-REQ-GOV-0002 — Stable document identity

**MUST.** Moving or renaming a published canonical document MUST NOT change its stable document ID.

- Verification mode: `automated`
- Validator: `docs.unique_ids`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0002.json`

<a id="AIXEM-REQ-GOV-0003"></a>

### AIXEM-REQ-GOV-0003 — Breaking format version

**MUST.** An incompatible serialized-format change MUST increment the declared format or schema version and provide migration guidance.

- Verification mode: `review`
- Validator: `manual.compatibility`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_review_evidence`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Compatibility Policy](compatibility-policy.md) — `AIXEM-GOV-COMPAT-001`
- [Deprecation Policy](deprecation.md) — `AIXEM-GOV-DEPRECATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

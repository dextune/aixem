---
id: AIXEM-SPEC-AUTHORITY-001
title: Authority and Precedence
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines artifact ownership, normative precedence, conflict handling, generated-file policy, and migration-bearing
  changes.
authority:
- authority-precedence
aliases:
- precedence
- authority specification
- source ownership
agent:
  priority: critical
  estimated_tokens: 1013
  intents:
  - inspect-artifact
  - change-architecture
  - publish-release
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
related:
- AIXEM-ARCH-ARTIFACT-001
- AIXEM-AGENT-FAILURE-001
navigation:
  group: specifications
  order: 40
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-DOCS-0004
  title: Resolvable ownership
  level: MUST
  statement: Every release artifact declared in authored metadata MUST resolve to one canonical owner or an explicitly
    generated owner class.
  validator: docs.artifact_ownership
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0004.json
- id: AIXEM-REQ-DOCS-0005
  title: Fail-closed conflict
  level: MUST
  statement: A build or agent MUST stop when active normative authorities conflict and no explicit precedence resolves
    the conflict.
  validator: docs.authority_conflict
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0005.json
- id: AIXEM-REQ-DOCS-0006
  title: Generated edit prohibition
  level: MUST
  statement: Generated documentation and reference files MUST be regenerated from canonical sources rather than
    maintained as independent authored rules.
  validator: docs.generated_freshness
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-DOCS-0006.json
---

# Authority and Precedence

Defines artifact ownership, normative precedence, conflict handling, generated-file policy, and migration-bearing changes.

> **Document ID:** `AIXEM-SPEC-AUTHORITY-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `authority-precedence`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Normative canonical documents precede informative guides.
- Schemas and validators implement rather than replace requirements.
- Compatibility output is derived.

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

<a id="AIXEM-REQ-DOCS-0004"></a>

### AIXEM-REQ-DOCS-0004 — Resolvable ownership

**MUST.** Every release artifact declared in authored metadata MUST resolve to one canonical owner or an explicitly generated owner class.

- Verification mode: `automated`
- Validator: `docs.artifact_ownership`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0004.json`

<a id="AIXEM-REQ-DOCS-0005"></a>

### AIXEM-REQ-DOCS-0005 — Fail-closed conflict

**MUST.** A build or agent MUST stop when active normative authorities conflict and no explicit precedence resolves the conflict.

- Verification mode: `automated`
- Validator: `docs.authority_conflict`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0005.json`

<a id="AIXEM-REQ-DOCS-0006"></a>

### AIXEM-REQ-DOCS-0006 — Generated edit prohibition

**MUST.** Generated documentation and reference files MUST be regenerated from canonical sources rather than maintained as independent authored rules.

- Verification mode: `automated`
- Validator: `docs.generated_freshness`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-DOCS-0006.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority Model](../../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Artifact Ownership and Storage](../../architecture/artifact-store.md) — `AIXEM-ARCH-ARTIFACT-001`
- [Fail-Closed Policy](../../agent/failure-policy.md) — `AIXEM-AGENT-FAILURE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

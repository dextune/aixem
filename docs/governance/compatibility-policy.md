---
id: AIXEM-GOV-COMPAT-001
title: Compatibility Policy
status: normative
version: '1.0'
language: en
domain: governance
kind: policy
summary: Defines backward, forward, source, schema, renderer, documentation, and agent-route compatibility claims.
authority:
- compatibility-policy
aliases:
- compatibility
- backward compatibility
- migration policy
agent:
  priority: critical
  estimated_tokens: 853
  intents:
  - migrate-baseline
  - change-architecture
  - publish-release
depends_on:
- AIXEM-GOV-VERSIONING-001
related:
- AIXEM-CONF-COMPAT-001
navigation:
  group: governance
  order: 30
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-GOV-0010
  title: Explicit compatibility claim
  level: MUST
  statement: A release MUST state which prior release artifacts or interfaces it preserves, migrates, replaces,
    or drops.
  validator: docs.release_metadata
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0010.json
- id: AIXEM-REQ-GOV-0011
  title: Migration guidance
  level: MUST
  statement: Every intentional breaking change MUST include a migration path or an explicit unsupported rationale.
  validator: docs.legacy_inventory
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-GOV-0011.json
---

# Compatibility Policy

Defines backward, forward, source, schema, renderer, documentation, and agent-route compatibility claims.

> **Document ID:** `AIXEM-GOV-COMPAT-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

This policy controls long-lived identity and release behavior across documentation, schemas, and implementations.

The declared authority scopes are `compatibility-policy`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Compatibility is scoped by artifact class.
- Generated 0.4 reference output preserves navigation consumers.
- Canonical 0.5 documents replace duplicated authored cards.

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

<a id="AIXEM-REQ-GOV-0010"></a>

### AIXEM-REQ-GOV-0010 — Explicit compatibility claim

**MUST.** A release MUST state which prior release artifacts or interfaces it preserves, migrates, replaces, or drops.

- Verification mode: `automated`
- Validator: `docs.release_metadata`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0010.json`

<a id="AIXEM-REQ-GOV-0011"></a>

### AIXEM-REQ-GOV-0011 — Migration guidance

**MUST.** Every intentional breaking change MUST include a migration path or an explicit unsupported rationale.

- Verification mode: `automated`
- Validator: `docs.legacy_inventory`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-GOV-0011.json`

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

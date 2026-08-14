---
id: AIXEM-ARCH-CACHE-001
title: Cache and Incremental Compilation
status: normative
version: '1.0'
language: en
domain: architecture
kind: architecture
summary: Defines source digests, dependency invalidation, route cache keys, deterministic cache content, and safe
  incremental rebuilds.
authority:
- documentation-cache
aliases:
- cache
- incremental build
- digest cache
agent:
  priority: critical
  estimated_tokens: 866
  intents:
  - build-documentation
  - change-architecture
depends_on:
- AIXEM-CONCEPT-DETERMINISM-001
related:
- AIXEM-AGENT-RETRIEVAL-001
- AIXEM-ARCH-PIPELINE-001
navigation:
  group: architecture
  order: 50
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-ARCH-0020
  title: Content-derived invalidation
  level: MUST
  statement: An incremental compiler cache MUST invalidate an output when its canonical content or declared dependency
    digest changes.
  validator: docs.source_digest
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0020.json
- id: AIXEM-REQ-ARCH-0021
  title: Cache non-authority
  level: MUST
  statement: A cache hit MUST NOT bypass canonical validation or change source authority.
  validator: docs.generated_freshness
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-ARCH-0021.json
---

# Cache and Incremental Compilation

Defines source digests, dependency invalidation, route cache keys, deterministic cache content, and safe incremental rebuilds.

> **Document ID:** `AIXEM-ARCH-CACHE-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `documentation-cache`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Document IDs are graph nodes.
- Dependency edges scope invalidation.
- Route results include the source manifest digest.

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

<a id="AIXEM-REQ-ARCH-0020"></a>

### AIXEM-REQ-ARCH-0020 — Content-derived invalidation

**MUST.** An incremental compiler cache MUST invalidate an output when its canonical content or declared dependency digest changes.

- Verification mode: `automated`
- Validator: `docs.source_digest`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0020.json`

<a id="AIXEM-REQ-ARCH-0021"></a>

### AIXEM-REQ-ARCH-0021 — Cache non-authority

**MUST.** A cache hit MUST NOT bypass canonical validation or change source authority.

- Verification mode: `automated`
- Validator: `docs.generated_freshness`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-ARCH-0021.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Deterministic Builds](../concepts/deterministic-builds.md) — `AIXEM-CONCEPT-DETERMINISM-001`
- [Bounded Retrieval](../agent/retrieval.md) — `AIXEM-AGENT-RETRIEVAL-001`
- [Build and Authoring Pipeline](pipeline.md) — `AIXEM-ARCH-PIPELINE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

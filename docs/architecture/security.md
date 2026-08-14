---
id: AIXEM-ARCH-SECURITY-001
title: Security and Trust Boundaries
status: normative
version: '1.0'
language: en
domain: architecture
kind: architecture
summary: Defines local-path safety, remote-asset denial, digest verification, untrusted Markdown handling, and release
  archive checks.
authority:
- security-boundaries
aliases:
- security
- trust boundaries
- safe paths
agent:
  priority: critical
  estimated_tokens: 977
  intents:
  - validate-project
  - publish-release
  - change-architecture
depends_on: []
related:
- AIXEM-SPEC-PROJECT-LOCK-001
- AIXEM-SPEC-RELEASE-001
navigation:
  group: architecture
  order: 60
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-SEC-0001
  title: Path containment
  level: MUST
  statement: Project-relative and documentation-relative paths MUST be resolved without escaping the declared repository
    or project root.
  validator: docs.path_safety
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-SEC-0001.json
- id: AIXEM-REQ-SEC-0002
  title: No required remote assets
  level: MUST
  statement: Reference release validation MUST reject required remote scripts, styles, fonts, images, and symbol
    assets.
  validator: schematic.remote_assets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-SEC-0002.json
- id: AIXEM-REQ-SEC-0003
  title: Archive traversal safety
  level: MUST
  statement: Archive verification MUST reject absolute paths and parent-directory traversal entries.
  validator: docs.archive_safety
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-SEC-0003.json
---

# Security and Trust Boundaries

Defines local-path safety, remote-asset denial, digest verification, untrusted Markdown handling, and release archive checks.

> **Document ID:** `AIXEM-ARCH-SECURITY-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The architecture separates authored authority, generated products, validation evidence, and static consumption surfaces.

The declared authority scopes are `security-boundaries`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Digests establish content identity.
- Static output reduces runtime attack surface.
- HTML generation escapes untrusted metadata.

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

<a id="AIXEM-REQ-SEC-0001"></a>

### AIXEM-REQ-SEC-0001 — Path containment

**MUST.** Project-relative and documentation-relative paths MUST be resolved without escaping the declared repository or project root.

- Verification mode: `automated`
- Validator: `docs.path_safety`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SEC-0001.json`

<a id="AIXEM-REQ-SEC-0002"></a>

### AIXEM-REQ-SEC-0002 — No required remote assets

**MUST.** Reference release validation MUST reject required remote scripts, styles, fonts, images, and symbol assets.

- Verification mode: `automated`
- Validator: `schematic.remote_assets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SEC-0002.json`

<a id="AIXEM-REQ-SEC-0003"></a>

### AIXEM-REQ-SEC-0003 — Archive traversal safety

**MUST.** Archive verification MUST reject absolute paths and parent-directory traversal entries.

- Verification mode: `automated`
- Validator: `docs.archive_safety`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-SEC-0003.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Project Lock Contract 1](../specifications/project/project-lock-contract.md) — `AIXEM-SPEC-PROJECT-LOCK-001`
- [Documentation Release Integrity 1](../specifications/documentation/release-integrity.md) — `AIXEM-SPEC-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

---
id: AIXEM-SPEC-PROJECT-LOCK-001
title: Project Lock Contract 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: specification
summary: Defines project identity, locked inputs, render policy, feature declarations, provenance, and expected
  outputs.
authority:
- project-lock-contract
aliases:
- project lock
- aixproj contract
- project manifest
agent:
  priority: critical
  estimated_tokens: 1064
  intents:
  - validate-project
  - publish-release
depends_on:
- AIXEM-CONCEPT-DETERMINISM-001
related:
- AIXEM-FORMAT-AIXPROJ-001
- AIXEM-CONF-RELEASE-001
navigation:
  group: specifications
  order: 90
artifacts:
  owns:
  - docs/specifications/schemas/component-graphics-1/aixem-project-manifest-1.schema.json
  consumes: []
requirements:
- id: AIXEM-REQ-PROJECT-0001
  title: Project schema
  level: MUST
  statement: Every project lock MUST validate against the declared project manifest schema.
  validator: schematic.project_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-PROJECT-0001.json
- id: AIXEM-REQ-PROJECT-0002
  title: Digest verification
  level: MUST
  statement: A renderer MUST verify every referenced input digest before resolving the project.
  validator: schematic.digest_lock
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-PROJECT-0002.json
- id: AIXEM-REQ-PROJECT-0003
  title: Remote asset policy
  level: MUST
  statement: The reference project profile MUST deny required remote assets.
  validator: schematic.remote_assets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-PROJECT-0003.json
- id: AIXEM-REQ-PROJECT-0004
  title: Declared output roles
  level: MUST
  statement: Expected project outputs MUST declare a path, media type, and role.
  validator: schematic.project_schema
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example
  evidence: validation/evidence/requirements/AIXEM-REQ-PROJECT-0004.json
---

# Project Lock Contract 1

Defines project identity, locked inputs, render policy, feature declarations, provenance, and expected outputs.

> **Document ID:** `AIXEM-SPEC-PROJECT-LOCK-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `project-lock-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The lock is the reproducible build boundary.
- Feature declarations make capability negotiation explicit.
- Output declarations enable release checks.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/specifications/schemas/component-graphics-1/aixem-project-manifest-1.schema.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-PROJECT-0001"></a>

### AIXEM-REQ-PROJECT-0001 — Project schema

**MUST.** Every project lock MUST validate against the declared project manifest schema.

- Verification mode: `automated`
- Validator: `schematic.project_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PROJECT-0001.json`

<a id="AIXEM-REQ-PROJECT-0002"></a>

### AIXEM-REQ-PROJECT-0002 — Digest verification

**MUST.** A renderer MUST verify every referenced input digest before resolving the project.

- Verification mode: `automated`
- Validator: `schematic.digest_lock`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PROJECT-0002.json`

<a id="AIXEM-REQ-PROJECT-0003"></a>

### AIXEM-REQ-PROJECT-0003 — Remote asset policy

**MUST.** The reference project profile MUST deny required remote assets.

- Verification mode: `automated`
- Validator: `schematic.remote_assets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PROJECT-0003.json`

<a id="AIXEM-REQ-PROJECT-0004"></a>

### AIXEM-REQ-PROJECT-0004 — Declared output roles

**MUST.** Expected project outputs MUST declare a path, media type, and role.

- Verification mode: `automated`
- Validator: `schematic.project_schema`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_schematic_example`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-PROJECT-0004.json`

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
- [.aixproj.json Project Lock](../../file-formats/aixproj.md) — `AIXEM-FORMAT-AIXPROJ-001`
- [Release Gates](../../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

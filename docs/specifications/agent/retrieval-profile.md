---
id: AIXEM-SPEC-AGENT-RETRIEVAL-001
title: Agent Retrieval Profile 1
status: normative
version: '1.0'
language: en
domain: specifications
kind: profile
summary: Defines route-first lookup, bounded context, exact section targeting, fallback search, and fail-closed
  resolution for AI agents.
authority:
- agent-retrieval-contract
aliases:
- retrieval profile
- agent navigation
- bounded context
agent:
  priority: critical
  estimated_tokens: 1465
  intents:
  - build-documentation
  - change-architecture
depends_on: []
related:
- AIXEM-ARCH-ADR-0002
- AIXEM-AGENT-RETRIEVAL-001
- AIXEM-AGENT-ROUTES-001
navigation:
  group: specifications
  order: 100
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-AGENT-0001
  title: Route-first lookup
  level: MUST
  statement: A known task intent MUST resolve through the authored route index before repository-wide search.
  validator: route.resolve
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0001.json
- id: AIXEM-REQ-AGENT-0002
  title: Default document budget
  level: MUST
  statement: A default route MUST load no more than seven canonical documents.
  validator: route.budget
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0002.json
- id: AIXEM-REQ-AGENT-0003
  title: Default byte budget
  level: MUST
  statement: A default route MUST declare a documentation budget no greater than 96 KiB.
  validator: route.budget
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0003.json
- id: AIXEM-REQ-AGENT-0004
  title: Default depth budget
  level: MUST
  statement: A default route MUST declare a dependency depth no greater than three.
  validator: route.budget
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0004.json
- id: AIXEM-REQ-AGENT-0005
  title: Unresolved target failure
  level: MUST
  statement: A missing route target or required section MUST fail the compiler and agent lookup.
  validator: route.targets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0005.json
---

# Agent Retrieval Profile 1

Defines route-first lookup, bounded context, exact section targeting, fallback search, and fail-closed resolution for AI agents.

> **Document ID:** `AIXEM-SPEC-AGENT-RETRIEVAL-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

Normative language on this page is release-gating and is linked to validators, tests, and evidence.

The declared authority scopes are `agent-retrieval-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Intent aliases normalize user language.
- Routes order only the required documents.
- The inverted index is a fallback rather than the default.

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

<a id="AIXEM-REQ-AGENT-0001"></a>

### AIXEM-REQ-AGENT-0001 — Route-first lookup

**MUST.** A known task intent MUST resolve through the authored route index before repository-wide search.

- Verification mode: `automated`
- Validator: `route.resolve`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0001.json`

<a id="AIXEM-REQ-AGENT-0002"></a>

### AIXEM-REQ-AGENT-0002 — Default document budget

**MUST.** A default route MUST load no more than seven canonical documents.

- Verification mode: `automated`
- Validator: `route.budget`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0002.json`

<a id="AIXEM-REQ-AGENT-0003"></a>

### AIXEM-REQ-AGENT-0003 — Default byte budget

**MUST.** A default route MUST declare a documentation budget no greater than 96 KiB.

- Verification mode: `automated`
- Validator: `route.budget`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0003.json`

<a id="AIXEM-REQ-AGENT-0004"></a>

### AIXEM-REQ-AGENT-0004 — Default depth budget

**MUST.** A default route MUST declare a dependency depth no greater than three.

- Verification mode: `automated`
- Validator: `route.budget`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0004.json`

<a id="AIXEM-REQ-AGENT-0005"></a>

### AIXEM-REQ-AGENT-0005 — Unresolved target failure

**MUST.** A missing route target or required section MUST fail the compiler and agent lookup.

- Verification mode: `automated`
- Validator: `route.targets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0005.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Bounded Retrieval](../../agent/retrieval.md) — `AIXEM-AGENT-RETRIEVAL-001`
- [Task Routes](../../agent/task-routing.md) — `AIXEM-AGENT-ROUTES-001`
- [ADR-0002: Route-First Agent Retrieval](../../architecture/adr/0002-route-first-retrieval.md) — `AIXEM-ARCH-ADR-0002`
## Diagnostic-Driven Narrow Retrieval

Agent Diagnostic Contract 1 permits a blocking code to select a known remediation route and its generated task packet directly. Retrieval should use `code -> remediationRoute -> exact route sections`, then open the affected artifact location. This is a bounded alternative to repository-wide discovery, not permission to skip the owning specification.

The execution packet also carries the task-packet digest, allowed write scope, validators, and stage exits, so a cold-start agent can act without inspecting renderer implementation. Unknown diagnostic codes, missing route mappings, or contradictory ownership fail closed.
<a id="0-5-6-cold-start-reference-packs"></a>
## Cold-start reference packs

A cold-start reference pack is compiled from the already resolved canonical route and general AIXEM execution dependencies. It may contain schemas, profiles, task packets, authoring tools, and general examples, but must exclude the case evaluator, completed target, prior attempts, validation results, and completed target renders. Retrieval-discipline claims are valid only for event classes declared complete by the executor adapter.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

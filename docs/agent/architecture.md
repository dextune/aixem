---
id: AIXEM-AGENT-ARCH-001
title: Agent Architecture
status: normative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Defines the planner, bounded retriever, authority resolver, authoring tools, validators, evidence store,
  and release gate used by an AIXEM agent.
authority:
- agent-system-architecture
aliases:
- agent architecture
- AI workflow architecture
- agent components
agent:
  priority: critical
  estimated_tokens: 897
  intents:
  - change-architecture
  - build-documentation
depends_on:
- AIXEM-CONCEPT-AUTHORITY-001
- AIXEM-SPEC-AGENT-RETRIEVAL-001
related:
- AIXEM-ARCH-SYSTEM-001
- AIXEM-AGENT-VALIDATION-001
navigation:
  group: agent
  order: 20
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-AGENT-0010
  title: Authority-aware planning
  level: MUST
  statement: An AIXEM agent MUST identify the owning authority layer before modifying an artifact.
  validator: agent.authority_plan
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0010.json
- id: AIXEM-REQ-AGENT-0011
  title: Evidence-producing completion
  level: MUST
  statement: An agent MUST retain the validation commands and evidence required by the scope before reporting completion.
  validator: agent.evidence
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0011.json
---

# Agent Architecture

Defines the planner, bounded retriever, authority resolver, authoring tools, validators, evidence store, and release gate used by an AIXEM agent.

> **Document ID:** `AIXEM-AGENT-ARCH-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-system-architecture`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- The retriever minimizes context.
- The authoring adapter operates on canonical sources.
- Validators are independent from generated presentation.

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

<a id="AIXEM-REQ-AGENT-0010"></a>

### AIXEM-REQ-AGENT-0010 — Authority-aware planning

**MUST.** An AIXEM agent MUST identify the owning authority layer before modifying an artifact.

- Verification mode: `automated`
- Validator: `agent.authority_plan`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0010.json`

<a id="AIXEM-REQ-AGENT-0011"></a>

### AIXEM-REQ-AGENT-0011 — Evidence-producing completion

**MUST.** An agent MUST retain the validation commands and evidence required by the scope before reporting completion.

- Verification mode: `automated`
- Validator: `agent.evidence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0011.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Authority Model](../concepts/authority-model.md) — `AIXEM-CONCEPT-AUTHORITY-001`
- [Agent Retrieval Profile 1](../specifications/agent/retrieval-profile.md) — `AIXEM-SPEC-AGENT-RETRIEVAL-001`
- [System Overview](../architecture/system-overview.md) — `AIXEM-ARCH-SYSTEM-001`
- [Three-Stage Validation Loop](validation-loop.md) — `AIXEM-AGENT-VALIDATION-001`

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

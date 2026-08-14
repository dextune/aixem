---
id: AIXEM-AGENT-ROUTES-001
title: Task Routes
status: normative
version: '1.0'
language: en
domain: agent
kind: reference
summary: Defines authored route YAML, aliases, ordered document targets, section anchors, budgets, conditions, and
  completion criteria.
authority:
- agent-route-contract
aliases:
- task routes
- route index
- intent routing
agent:
  priority: critical
  estimated_tokens: 1197
  intents:
  - build-documentation
  - publish-release
depends_on:
- AIXEM-AGENT-RETRIEVAL-001
related:
- AIXEM-SPEC-METADATA-001
- AIXEM-ARCH-ADR-0002
navigation:
  group: agent
  order: 40
artifacts:
  owns:
  - docs/_meta/routes/*.yaml
  - docs/_meta/generated/route-index.json
  consumes: []
requirements:
- id: AIXEM-REQ-AGENT-0012
  title: Unique route aliases
  level: MUST
  statement: Normalized route IDs and aliases MUST resolve to at most one active route.
  validator: route.aliases
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0012.json
- id: AIXEM-REQ-AGENT-0013
  title: Ordered targets
  level: MUST
  statement: A route MUST preserve an explicit ordered list of canonical document and optional section targets.
  validator: route.targets
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0013.json
- id: AIXEM-REQ-AGENT-0014
  title: Completion conditions
  level: MUST
  statement: A route MUST declare objective completion conditions appropriate to its task.
  validator: route.completion
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0014.json
---

# Task Routes

Defines authored route YAML, aliases, ordered document targets, section anchors, budgets, conditions, and completion criteria.

> **Document ID:** `AIXEM-AGENT-ROUTES-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-route-contract`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Routes are authored YAML.
- Compiled JSON includes resolved paths and size estimates.
- Aliases are normalized consistently.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Resolve this document by its stable ID rather than relying only on its path.
2. Apply the rules at the authority layer declared in the metadata.
3. Regenerate every downstream artifact affected by the change.
4. Run the mapped validators and retain release-specific evidence.

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Declared owned artifacts:

- `docs/_meta/routes/*.yaml`
- `docs/_meta/generated/route-index.json`

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-AGENT-0012"></a>

### AIXEM-REQ-AGENT-0012 — Unique route aliases

**MUST.** Normalized route IDs and aliases MUST resolve to at most one active route.

- Verification mode: `automated`
- Validator: `route.aliases`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0012.json`

<a id="AIXEM-REQ-AGENT-0013"></a>

### AIXEM-REQ-AGENT-0013 — Ordered targets

**MUST.** A route MUST preserve an explicit ordered list of canonical document and optional section targets.

- Verification mode: `automated`
- Validator: `route.targets`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0013.json`

<a id="AIXEM-REQ-AGENT-0014"></a>

### AIXEM-REQ-AGENT-0014 — Completion conditions

**MUST.** A route MUST declare objective completion conditions appropriate to its task.

- Verification mode: `automated`
- Validator: `route.completion`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_route_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0014.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Bounded Retrieval](retrieval.md) — `AIXEM-AGENT-RETRIEVAL-001`
- [Documentation Metadata Contract 1](../specifications/documentation/metadata-contract.md) — `AIXEM-SPEC-METADATA-001`
- [ADR-0002: Route-First Agent Retrieval](../architecture/adr/0002-route-first-retrieval.md) — `AIXEM-ARCH-ADR-0002`
## Diagnostic-Driven Remediation Routing

Canonical task packets now expose `writes` and `remediation` metadata. Initial intent selects the entry route; a blocking diagnostic then selects the narrow repair route through its stable `remediationRoute`. A composite packet exposes child-stage metadata but does not grant the union of child write scopes.

Use the active task packet as the execution boundary. Search beyond route-selected documents only when the registered owner cannot explain a concrete discrepancy. After repair, return to the interrupted stage and satisfy its exit conditions before advancing.
<a id="0-5-6-live-agent-maintenance-route"></a>
## Live-agent maintenance route

`validate-live-agent-authoring` is the single maintenance/evaluation route for stage, executor, observation, scorer, evidence, and claim operations. L001-L012 do not receive dedicated routes. Each case exercises the same normal create/route/compose/validate routes used outside evaluation.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

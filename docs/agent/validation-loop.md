---
id: AIXEM-AGENT-VALIDATION-001
title: Three-Stage Validation Loop
status: normative
version: '1.0'
language: en
domain: agent
kind: guide
summary: Defines structural, semantic, and human-facing review stages for agent-produced changes.
authority:
- agent-validation-workflow
aliases:
- validation loop
- agent self check
- three pass validation
agent:
  priority: critical
  estimated_tokens: 1203
  intents:
  - validate-project
  - publish-release
  - build-documentation
depends_on:
- AIXEM-CONF-VALIDATION-001
related:
- AIXEM-CONF-TESTS-001
- AIXEM-CONF-RELEASE-001
navigation:
  group: agent
  order: 80
artifacts:
  owns: []
  consumes: []
requirements:
- id: AIXEM-REQ-AGENT-0020
  title: Narrow-first validation
  level: MUST
  statement: An agent MUST run the narrow validator for the changed authority before release-level validation.
  validator: agent.evidence
  verification_mode: automated
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0020.json
- id: AIXEM-REQ-AGENT-0021
  title: Rendered review
  level: MUST
  statement: A schematic or documentation presentation change MUST include inspection of generated output at relevant
    viewport sizes.
  validator: docs.visual_review
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0021.json
- id: AIXEM-REQ-AGENT-0022
  title: No unexecuted claims
  level: MUST
  statement: An agent completion report MUST NOT claim a validation command that was not executed.
  validator: agent.evidence
  verification_mode: review
  test: tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-0022.json
---

# Three-Stage Validation Loop

Defines structural, semantic, and human-facing review stages for agent-produced changes.

> **Document ID:** `AIXEM-AGENT-VALIDATION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Overview

The procedure is designed to minimize context while preserving authority, traceability, and fail-closed behavior.

The declared authority scopes are `agent-validation-workflow`. Changes must be made in the source that owns those scopes and then propagated through generation and validation.

### Scope

This document covers:

- Agent validation workflow.

It does not allow presentation geometry, generated output, or examples to silently redefine a higher-authority contract.

## Authoritative Workflow

1. Stage 1: validate structure and schemas
2. Stage 2: validate cross-artifact semantics and deterministic generation
3. Stage 3: inspect human-facing output and run the release gate

### Inputs and outputs

Inputs are the canonical documents and artifacts named by the dependency graph and the selected task route.

Outputs remain in the authority layer described by the metadata; derived representations are regenerated rather than edited as an independent source.

## Operational Rules

The following requirements are normative for this release.

<a id="AIXEM-REQ-AGENT-0020"></a>

### AIXEM-REQ-AGENT-0020 — Narrow-first validation

**MUST.** An agent MUST run the narrow validator for the changed authority before release-level validation.

- Verification mode: `automated`
- Validator: `agent.evidence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0020.json`

<a id="AIXEM-REQ-AGENT-0021"></a>

### AIXEM-REQ-AGENT-0021 — Rendered review

**MUST.** A schematic or documentation presentation change MUST include inspection of generated output at relevant viewport sizes.

- Verification mode: `review`
- Validator: `docs.visual_review`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_documentation_integrity`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0021.json`

<a id="AIXEM-REQ-AGENT-0022"></a>

### AIXEM-REQ-AGENT-0022 — No unexecuted claims

**MUST.** An agent completion report MUST NOT claim a validation command that was not executed.

- Verification mode: `review`
- Validator: `agent.evidence`
- Test reference: `tests/docs/test_repository.py::RepositoryConformanceTests.test_agent_policy`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-0022.json`

## Validation and Evidence

Validation is complete only when every requirement above has a current evidence record and the release traceability index resolves the document, validator, test, and evidence path.

Minimum review sequence:

1. Validate metadata, IDs, links, dependencies, and artifact ownership.
2. Run the narrow validator for the affected authority layer.
3. Rebuild generated indexes or render output.
4. Run release-level integrity checks when the change is intended for publication.
5. Inspect the generated static page and confirm that agent routes resolve within their budgets.

## Related Documents

- [Validation Architecture](../conformance/validation.md) — `AIXEM-CONF-VALIDATION-001`
- [Test Suite](../conformance/test-suite.md) — `AIXEM-CONF-TESTS-001`
- [Release Gates](../conformance/release-gates.md) — `AIXEM-CONF-RELEASE-001`
## Structured Authoring Feedback Loop

For authoring tasks, each validation stage emits Agent Diagnostic Contract 1 records. The agent groups blocking records by authority, chooses the smallest registered remediation route, edits only that route's declared files, computes Authoring Change-Set 1, and reruns route-local validators before full rendering. Message prose is explanatory; branching keys are the stable code, authority, structured location, and remediation route.

Final validation additionally requires a schema-valid Authoring Run Record 1, deterministic three-run render evidence, no generated-output edits, and no stalled or oscillating loop. This execution evidence extends the three-stage review model without changing semantic, layout, project, renderer, or Viewer authority.
<a id="0-5-6-live-cold-start-wrapper"></a>
## Live cold-start wrapper

The live wrapper does not replace the normal validation loop. It stages an incomplete workspace, invokes the external agent, then validates the agent's actual result through the existing `check` and `close` authority before evaluator-only semantic invariants are scored and Live Run Evidence 1 is retained.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

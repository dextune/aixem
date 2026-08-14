---
status: normative
version: '1.0'
language: en
domain: conformance
agent:
  priority: critical
  estimated_tokens: 543
  intents:
  - validate-project
  - publish-release
navigation:
  group: conformance
  order: 95
artifacts:
  owns: []
  consumes: []
id: AIXEM-CONF-AGENT-DIAGNOSTICS-001
title: Agent Diagnostic Registry and Conformance
kind: conformance
summary: Defines the P0 diagnostic registry, controlled ownership vocabulary, remediation-route coverage,
  and structural negative conformance for agent authoring feedback.
authority:
- agent-diagnostic-conformance
aliases:
- diagnostic registry
- agent diagnostic codes
depends_on:
- AIXEM-SPEC-AGENT-DIAGNOSTIC-001
related:
- AIXEM-CONF-AGENT-AUTHORING-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0017
  title: P0 registry coverage
  level: MUST
  statement: The release diagnostic registry MUST contain and route every P0 code declared by the 0.5.5
    authoring plan, with no unknown authority or repair class.
  validator: agent.diagnostics
  verification_mode: automated
  test: tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_registry_contains_complete_p0_set_and_valid_metadata
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0017.json
---

# Agent Diagnostic Registry and Conformance

Defines the P0 diagnostic registry, controlled ownership vocabulary, remediation-route coverage, and structural negative conformance for agent authoring feedback.

> **Document ID:** `AIXEM-CONF-AGENT-DIAGNOSTICS-001`  
> **Status:** Normative  
> **Version:** 1.0

## Registry Policy

The P0 registry normalizes schema, semantic endpoint, net closure, component binding, symbol design, placement, local routing, project composition, project routing, determinism, unsupported capability, and execution-scope failures.

## Required Mapping

Every code has one authority owner, one repair class, one requirement owner, and one existing remediation route. Messages may become clearer without changing the code semantics.

## Structural Negative Cases

Conformance rejects unknown codes, missing owner or route, contradictory rich diagnostic metadata, unsafe repair artifacts, and raw validator failures that cannot be normalized.

## Registry Source

`implementation/agent/diagnostics.py` is the executable registry. This document and generated evidence present the registry; they do not override its tested contract.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0017"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0017 — P0 registry coverage

**MUST.** The release diagnostic registry MUST contain and route every P0 code declared by the 0.5.5 authoring plan, with no unknown authority or repair class.

- Verification mode: `automated`
- Validator: `agent.diagnostics`
- Test reference: `tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_registry_contains_complete_p0_set_and_valid_metadata`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0017.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

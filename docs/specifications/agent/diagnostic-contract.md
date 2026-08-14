---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 980
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 180
artifacts:
  owns: []
  consumes: []
id: AIXEM-SPEC-AGENT-DIAGNOSTIC-001
title: Agent Diagnostic Contract 1
kind: contract
summary: Defines stable machine-readable authoring diagnostics with authority ownership, structured location,
  remediation routing, and fail-closed repair targets.
authority:
- agent-diagnostic-contract
aliases:
- agent diagnostics
- diagnostic contract
- machine repair feedback
depends_on:
- AIXEM-SPEC-AGENT-RETRIEVAL-001
- AIXEM-CONF-VALIDATION-001
related:
- AIXEM-CONF-AGENT-DIAGNOSTICS-001
- AIXEM-SPEC-AGENT-EXECUTION-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0001
  title: Stable diagnostic envelope
  level: MUST
  statement: Every P0 blocking authoring failure MUST be emitted with a stable diagnostic code and schema-valid
    machine-readable envelope.
  validator: agent.diagnostics
  verification_mode: automated
  test: tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_diagnostic_serialization_is_schema_valid_and_stable
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0001.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0002
  title: Authority-aware remediation
  level: MUST
  statement: Every P0 diagnostic MUST identify the authoritative owner and an existing narrow remediation
    route without requiring prose parsing.
  validator: agent.diagnostics
  verification_mode: automated
  test: tests/agent/test_route_execution_metadata.py::RouteExecutionMetadataTests.test_all_recommended_diagnostics_are_accepted_by_an_existing_route
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0002.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0003
  title: Generated output is not a repair owner
  level: MUST
  statement: A diagnostic MUST NOT identify generated SVG, resolved evidence, Viewer Model, Viewer HTML,
    or Workbench HTML as the authoritative final repair target.
  validator: agent.diagnostics
  verification_mode: automated
  test: tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_registry_contains_complete_p0_set_and_valid_metadata
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0003.json
---

# Agent Diagnostic Contract 1

Defines stable machine-readable authoring diagnostics with authority ownership, structured location, remediation routing, and fail-closed repair targets.

> **Document ID:** `AIXEM-SPEC-AGENT-DIAGNOSTIC-001`  
> **Status:** Normative  
> **Version:** 1.0

## Purpose

Agent Diagnostic Contract 1 adapts existing schema, semantic, symbol, binding, layout, project, renderer, and execution failures into a deterministic envelope. The envelope is derived evidence only and never creates circuit meaning.

## Required Record

A record contains `id`, `code`, `severity`, `authority`, `artifact`, `location`, `requirement`, `remediationRoute`, `repairClass`, `message`, and `evidence`. Agents branch on stable fields rather than English prose.

## Authority Vocabulary

`semantic`, `component-library`, `symbol`, `layout`, `project`, `project-routing`, `renderer`, `viewer`, `workbench`, `documentation`, and `agent-execution` are controlled values.

## Repair Boundary

Diagnostics point to the smallest owning authority and route. They never authorize patching `render/`, evidence JSON, SVG, Viewer Model, `viewer.html`, or `workbench.html`. A visible failure in those artifacts is routed upstream to authoritative source or implementation ownership.

## Structured Location

Where available, location uses a JSON Pointer plus an object kind and object identifier. Schema failures also retain the schema pointer in evidence. Missing fine-grained location uses the owning artifact with the root pointer.

## Deterministic Identity

Diagnostic IDs are assigned after stable sorting and deduplication. The blocking diagnostic state digest excludes presentation-only IDs so equivalent failure states compare identically across runs.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0001"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0001 — Stable diagnostic envelope

**MUST.** Every P0 blocking authoring failure MUST be emitted with a stable diagnostic code and schema-valid machine-readable envelope.

- Verification mode: `automated`
- Validator: `agent.diagnostics`
- Test reference: `tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_diagnostic_serialization_is_schema_valid_and_stable`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0001.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0002"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0002 — Authority-aware remediation

**MUST.** Every P0 diagnostic MUST identify the authoritative owner and an existing narrow remediation route without requiring prose parsing.

- Verification mode: `automated`
- Validator: `agent.diagnostics`
- Test reference: `tests/agent/test_route_execution_metadata.py::RouteExecutionMetadataTests.test_all_recommended_diagnostics_are_accepted_by_an_existing_route`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0002.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0003"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0003 — Generated output is not a repair owner

**MUST.** A diagnostic MUST NOT identify generated SVG, resolved evidence, Viewer Model, Viewer HTML, or Workbench HTML as the authoritative final repair target.

- Verification mode: `automated`
- Validator: `agent.diagnostics`
- Test reference: `tests/agent/test_diagnostics.py::AgentDiagnosticContractTests.test_registry_contains_complete_p0_set_and_valid_metadata`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0003.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

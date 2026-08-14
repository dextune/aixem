---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1046
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 180
artifacts:
  owns: []
  consumes: []
id: AIXEM-SPEC-AGENT-CHANGESET-001
title: Authoring Change-Set Contract 1
kind: contract
summary: Defines deterministic before-and-after file evidence, route write scopes, authority constraints,
  and generated-output edit detection for each agent iteration.
authority:
- agent-change-set-contract
aliases:
- authoring change set
- write scope
- scope evidence
depends_on:
- AIXEM-SPEC-AGENT-DIAGNOSTIC-001
- AIXEM-CONCEPT-AUTHORITY-001
related:
- AIXEM-SPEC-AGENT-EXECUTION-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0004
  title: Objective change derivation
  level: MUST
  statement: Each iteration change set MUST be computed from deterministic before-and-after snapshots
    rather than accepted from an agent declaration.
  validator: agent.change_scope
  verification_mode: automated
  test: tests/agent/test_change_scope.py::AgentChangeScopeTests.test_allowed_layout_and_digest_only_project_change
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0004.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0005
  title: Route authority enforcement
  level: MUST
  statement: Every authoritative file change MUST match both the active route authority set and its declared
    artifact patterns and constraints.
  validator: agent.change_scope
  verification_mode: automated
  test: tests/agent/test_change_scope.py::AgentChangeScopeTests.test_wrong_authority_and_non_digest_project_change_fail
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0005.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0006
  title: Generated-output edit detection
  level: MUST
  statement: A hand edit to generated render or evidence output MUST be reported as a blocking scope violation.
  validator: agent.change_scope
  verification_mode: automated
  test: tests/agent/test_change_scope.py::AgentChangeScopeTests.test_generated_output_edit_is_detected_and_schema_valid
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0006.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0007
  title: Active child-stage scope
  level: MUST
  statement: A composite authoring route MUST apply only the current child route write scope and MUST
    NOT grant a broad union scope.
  validator: route.write_scope
  verification_mode: automated
  test: tests/agent/test_route_execution_metadata.py::RouteExecutionMetadataTests.test_task_packets_expose_active_child_scope
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0007.json
---

# Authoring Change-Set Contract 1

Defines deterministic before-and-after file evidence, route write scopes, authority constraints, and generated-output edit detection for each agent iteration.

> **Document ID:** `AIXEM-SPEC-AGENT-CHANGESET-001`  
> **Status:** Normative  
> **Version:** 1.0

## Purpose

The change set proves what changed, which authority owns each artifact, whether that change was allowed, and which validators must run. It is generated from snapshots; an agent cannot self-certify scope compliance.

## Snapshot Policy

The harness hashes every regular file inside the staged workspace without following symlinks. Authoritative digests are calculated separately from derived and support files. JSON authoritative artifacts retain parsed values only for local pointer-level comparison.

## Route Write Scope

Canonical authoring routes declare allowed authority values, artifact patterns, derived output patterns, prohibited generated outputs, and optional constraints. Project manifests may be updated under a `digest-only` constraint when a child source, layout, symbol, or library digest changes.

## Composite Routes

`author-component-circuit` is orchestration only. Its active child stage—such as `create-symbol`, `create-schematic`, or `route-nets`—owns the current write boundary.

## Generated Artifacts

A valid authoritative edit may be followed by regeneration. A pre-render hand edit to SVG, resolved scenes, Viewer Model, Viewer HTML, Workbench HTML, render manifests, or validation evidence is always reported and prevents closure.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0004"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0004 — Objective change derivation

**MUST.** Each iteration change set MUST be computed from deterministic before-and-after snapshots rather than accepted from an agent declaration.

- Verification mode: `automated`
- Validator: `agent.change_scope`
- Test reference: `tests/agent/test_change_scope.py::AgentChangeScopeTests.test_allowed_layout_and_digest_only_project_change`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0004.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0005"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0005 — Route authority enforcement

**MUST.** Every authoritative file change MUST match both the active route authority set and its declared artifact patterns and constraints.

- Verification mode: `automated`
- Validator: `agent.change_scope`
- Test reference: `tests/agent/test_change_scope.py::AgentChangeScopeTests.test_wrong_authority_and_non_digest_project_change_fail`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0005.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0006"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0006 — Generated-output edit detection

**MUST.** A hand edit to generated render or evidence output MUST be reported as a blocking scope violation.

- Verification mode: `automated`
- Validator: `agent.change_scope`
- Test reference: `tests/agent/test_change_scope.py::AgentChangeScopeTests.test_generated_output_edit_is_detected_and_schema_valid`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0006.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0007"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0007 — Active child-stage scope

**MUST.** A composite authoring route MUST apply only the current child route write scope and MUST NOT grant a broad union scope.

- Verification mode: `automated`
- Validator: `route.write_scope`
- Test reference: `tests/agent/test_route_execution_metadata.py::RouteExecutionMetadataTests.test_task_packets_expose_active_child_scope`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0007.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

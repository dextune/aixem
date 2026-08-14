---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 878
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 180
artifacts:
  owns: []
  consumes: []
id: AIXEM-SPEC-AGENT-RUN-001
title: Authoring Run Record 1
kind: contract
summary: Defines deterministic end-to-end evidence for one route-bounded authoring or repair task from
  baseline through closure.
authority:
- agent-authoring-run-record
aliases:
- authoring run record
- execution evidence
- closure record
depends_on:
- AIXEM-SPEC-AGENT-EXECUTION-001
- AIXEM-SPEC-AGENT-CHANGESET-001
related:
- AIXEM-CONF-AGENT-AUTHORING-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0011
  title: Complete iteration evidence
  level: MUST
  statement: A run record MUST retain the route chain, baseline and final authoritative digests, every
    iteration diagnostic state, change-set digest, executed validators, and final render evidence.
  validator: agent.run_record
  verification_mode: automated
  test: tests/agent/test_run_record.py::AgentRunRecordTests.test_closed_record_is_schema_valid_and_deterministic
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0011.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0012
  title: Deterministic serialization
  level: MUST
  statement: Equivalent recorded artifacts, validator results, and execution metadata MUST produce a byte-stable
    run record and record digest.
  validator: agent.run_record
  verification_mode: automated
  test: tests/agent/test_run_record.py::AgentRunRecordTests.test_closed_record_is_schema_valid_and_deterministic
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0012.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0013
  title: Fail-closed closure
  level: MUST
  statement: A run MUST NOT close while blocking diagnostics, scope violations, generated-output edits,
    loop stalls, oscillation, or renderer nondeterminism remain.
  validator: agent.run_record
  verification_mode: automated
  test: tests/agent/test_run_record.py::AgentRunRecordTests.test_blocking_diagnostic_prevents_closure
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0013.json
---

# Authoring Run Record 1

Defines deterministic end-to-end evidence for one route-bounded authoring or repair task from baseline through closure.

> **Document ID:** `AIXEM-SPEC-AGENT-RUN-001`  
> **Status:** Normative  
> **Version:** 1.0

## Purpose

Authoring Run Record 1 is reproducible execution evidence, not reasoning text and not circuit authority. It proves how a task moved from a locked baseline to a validated and rendered final state.

## Top-Level Data

The record contains run and task IDs, route chain, task packet digest, execution mode, baseline authoritative digests, iteration records, loop state, final authoritative and render digests, final diagnostics, and conformance status.

## Iteration Data

Each iteration stores diagnostics before and after the edit, diagnostic state digests, the complete Change Set 1 object and digest, authoritative digests before and after, validator IDs, rendered evidence when present, and an improvement flag.

## Execution Truth

`execution.mode` distinguishes deterministic harness/replay from live external agent execution. Provider and model metadata are optional evaluation metadata and never affect circuit conformance.

## Closure

`CLOSED` requires zero blocking diagnostics, zero scope violations, zero generated-output edits, deterministic render evidence, and no stalled or oscillating loop. Otherwise status is `BLOCKED`.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0011"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0011 — Complete iteration evidence

**MUST.** A run record MUST retain the route chain, baseline and final authoritative digests, every iteration diagnostic state, change-set digest, executed validators, and final render evidence.

- Verification mode: `automated`
- Validator: `agent.run_record`
- Test reference: `tests/agent/test_run_record.py::AgentRunRecordTests.test_closed_record_is_schema_valid_and_deterministic`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0011.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0012"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0012 — Deterministic serialization

**MUST.** Equivalent recorded artifacts, validator results, and execution metadata MUST produce a byte-stable run record and record digest.

- Verification mode: `automated`
- Validator: `agent.run_record`
- Test reference: `tests/agent/test_run_record.py::AgentRunRecordTests.test_closed_record_is_schema_valid_and_deterministic`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0012.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0013"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0013 — Fail-closed closure

**MUST.** A run MUST NOT close while blocking diagnostics, scope violations, generated-output edits, loop stalls, oscillation, or renderer nondeterminism remain.

- Verification mode: `automated`
- Validator: `agent.run_record`
- Test reference: `tests/agent/test_run_record.py::AgentRunRecordTests.test_blocking_diagnostic_prevents_closure`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0013.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

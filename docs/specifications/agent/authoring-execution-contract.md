---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1065
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 180
artifacts:
  owns: []
  consumes: []
id: AIXEM-SPEC-AGENT-EXECUTION-001
title: Authoring Execution Contract 1
kind: contract
summary: Defines the PREPARED-to-CLOSED authoring state machine, prepare/check/close harness, narrow validation,
  authority-local repair, and loop-stall handling.
authority:
- agent-authoring-execution-contract
aliases:
- authoring execution
- closed loop
- prepare check close
depends_on:
- AIXEM-SPEC-AGENT-DIAGNOSTIC-001
- AIXEM-SPEC-AGENT-CHANGESET-001
- AIXEM-SPEC-AGENT-RETRIEVAL-001
related:
- AIXEM-SPEC-AGENT-RUN-001
- AIXEM-CONF-AGENT-AUTHORING-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0008
  title: Deterministic preflight
  level: MUST
  statement: Prepare MUST resolve the entry route, active child route, write scope, validators, task packet
    digest, baseline digests, and initial diagnostics before an edit begins.
  validator: agent.authoring_closed_loop
  verification_mode: automated
  test: tests/agent/test_authoring_harness.py::AuthoringHarnessTests.test_prepare_check_close_valid_project
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0008.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0009
  title: Authority-local repair loop
  level: MUST
  statement: A failed iteration MUST normalize diagnostics, select the smallest owning remediation route,
    enforce its scope, rerun narrow validators, and defer rendering until structural validity.
  validator: agent.authoring_closed_loop
  verification_mode: automated
  test: tests/agent/test_authoring_harness.py::AuthoringHarnessTests.test_wrong_authority_edit_blocks_route
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0009.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0010
  title: Non-improving loop detection
  level: MUST
  statement: The execution harness MUST expose an unchanged blocking state and an A-to-B-to-A state oscillation
    instead of silently repeating repair.
  validator: agent.run_record
  verification_mode: automated
  test: tests/agent/test_run_record.py::AgentRunRecordTests.test_stalled_and_oscillating_state_detection
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0010.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0016
  title: Workspace path safety
  level: MUST
  statement: Workspace snapshot and execution paths MUST remain inside the staged root and MUST fail closed
    on symlinks or traversal.
  validator: agent.change_scope
  verification_mode: automated
  test: tests/agent/test_change_scope.py::AgentChangeScopeTests.test_symlink_fails_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0016.json
---

# Authoring Execution Contract 1

Defines the PREPARED-to-CLOSED authoring state machine, prepare/check/close harness, narrow validation, authority-local repair, and loop-stall handling.

> **Document ID:** `AIXEM-SPEC-AGENT-EXECUTION-001`  
> **Status:** Normative  
> **Version:** 1.0

## Canonical State Machine

```text
PREPARED
  -> EDITED
  -> VALIDATED
     -> PASS -> RENDERED -> CLOSED
     -> FAIL -> DIAGNOSED -> REPAIR -> VALIDATED
```

## Prepare

`tools/agent_authoring.py prepare` resolves the route and current composite child stage, snapshots the staged workspace, runs narrow preflight validation, and emits a deterministic execution packet.

## Check

`check` computes the file change set, detects scope and generated-output violations, runs route-local validators, normalizes diagnostics, returns remediation routes, and appends one iteration record. The harness never edits authoritative source on behalf of the agent.

## Close

`close` refuses blocking or unsafe state, runs full validation, executes the production renderer three times, validates Viewer Model output, compares artifact digests, and emits Authoring Run Record 1.

## Repair Selection

Blocking diagnostics are grouped by authority. The smallest owning route is re-entered. Presentation defects are not repaired by changing semantics unless semantic data is the actual owner.

## Stalled State

The harness detects unchanged blocking diagnostic state and A-to-B-to-A oscillation. P0 reports the state and requires manual or agent strategy change; it does not introduce an autonomous source patcher.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0008"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0008 — Deterministic preflight

**MUST.** Prepare MUST resolve the entry route, active child route, write scope, validators, task packet digest, baseline digests, and initial diagnostics before an edit begins.

- Verification mode: `automated`
- Validator: `agent.authoring_closed_loop`
- Test reference: `tests/agent/test_authoring_harness.py::AuthoringHarnessTests.test_prepare_check_close_valid_project`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0008.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0009"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0009 — Authority-local repair loop

**MUST.** A failed iteration MUST normalize diagnostics, select the smallest owning remediation route, enforce its scope, rerun narrow validators, and defer rendering until structural validity.

- Verification mode: `automated`
- Validator: `agent.authoring_closed_loop`
- Test reference: `tests/agent/test_authoring_harness.py::AuthoringHarnessTests.test_wrong_authority_edit_blocks_route`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0009.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0010"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0010 — Non-improving loop detection

**MUST.** The execution harness MUST expose an unchanged blocking state and an A-to-B-to-A state oscillation instead of silently repeating repair.

- Verification mode: `automated`
- Validator: `agent.run_record`
- Test reference: `tests/agent/test_run_record.py::AgentRunRecordTests.test_stalled_and_oscillating_state_detection`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0010.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0016"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0016 — Workspace path safety

**MUST.** Workspace snapshot and execution paths MUST remain inside the staged root and MUST fail closed on symlinks or traversal.

- Verification mode: `automated`
- Validator: `agent.change_scope`
- Test reference: `tests/agent/test_change_scope.py::AgentChangeScopeTests.test_symlink_fails_closed`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0016.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

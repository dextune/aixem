---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 950
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 190
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-task-1.schema.json
  consumes:
  - docs/_meta/generated/task-packets/*.json
id: AIXEM-SPEC-AGENT-TASK-001
title: Agent Task Contract 1
kind: contract
summary: Defines the non-authoritative machine envelope for one cold-start authoring request and resolves it against route-owned write scope.
authority:
- agent-task-envelope
aliases:
- agent task contract
- cold-start task
- task request envelope
depends_on:
- AIXEM-SPEC-AGENT-RETRIEVAL-001
- AIXEM-SPEC-AGENT-EXECUTION-001
related:
- AIXEM-SPEC-AGENT-STAGE-001
- AIXEM-CONF-AGENT-LIVE-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0001
  title: Task request is not authority
  level: MUST
  statement: An Agent Task Contract 1 document MUST be treated as a request envelope and MUST NOT grant an authority or artifact write that the selected task route does not own.
  validator: agent.task_contract
  verification_mode: automated
  test: tests/agent/test_task_contract.py::AgentTaskContractTests.test_task_cannot_widen_route_authority
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0001.json
- id: AIXEM-REQ-AGENT-LIVE-0002
  title: Effective scope only narrows
  level: MUST
  statement: Task write constraints MUST resolve as an equal or narrower subset of the active route authority, artifact patterns, prohibitions, constraints, and validators.
  validator: agent.task_contract
  verification_mode: automated
  test: tests/agent/test_task_contract.py::AgentTaskContractTests.test_valid_task_resolves_route_bounded_write_scope
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0002.json
- id: AIXEM-REQ-AGENT-LIVE-0003
  title: Executable route is fixed before staging
  level: MUST
  statement: A live attempt MUST resolve one executable active route before stage materialization; a simple route cannot select an unrelated route and a composite route must select one declared child stage.
  validator: agent.task_contract
  verification_mode: automated
  test: tests/agent/test_task_contract.py::AgentTaskContractTests.test_simple_route_cannot_select_an_unrelated_active_route
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0003.json
---

# Agent Task Contract 1

Agent Task Contract 1 is the stable, non-authoritative input envelope for a cold-start authoring attempt. It captures user intent, supplied facts, the route chosen by the orchestrator, expected artifacts, and completion criteria without becoming circuit, layout, symbol, project, or presentation authority.

> **Document ID:** `AIXEM-SPEC-AGENT-TASK-001`  
> **Schema:** `docs/specifications/schemas/agent/aixem-agent-task-1.schema.json`  
> **Implementation:** `implementation/agent/task_contract.py`

## Authority Rule

```text
user request / task facts
        ↓ may narrow
compiled active route write contract
        ↓ determines
actual writable authorities and artifact paths
```

A task cannot make a forbidden write legal by naming it. It cannot add `semantic` authority to `create-symbol`, cannot hand-edit `render/**`, and cannot escape the staged workspace.

## Required Resolution

The resolver validates the task schema, loads the compiled entry task packet, resolves the active child for a composite route, compares requested authorities and paths against route scope, unions route prohibitions with task-specific prohibitions, and records all digests in a derived route-resolution result.

`routingMode: fixed` means the stage already contains a resolved route. Future `agent-resolve` requests may be accepted by an upstream orchestrator, but a materialized attempt still requires one active route before execution.

## Machine Fields

The task envelope includes:

- stable task ID, title, operation, prompt, and structured facts;
- `entryRoute` and executable `activeRoute`;
- optional project path relative to the staged workspace;
- writable authority/path constraints that only narrow route scope;
- required validators, prohibited paths, completion criteria, and expected artifacts.

The task carries no secret values, hidden evaluator predicates, completed target artifact, or private reasoning transcript.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0001"></a>

### AIXEM-REQ-AGENT-LIVE-0001 — Task request is not authority

**MUST.** An Agent Task Contract 1 document MUST be treated as a request envelope and MUST NOT grant an authority or artifact write that the selected task route does not own.

- Validator: `agent.task_contract`
- Test: `tests/agent/test_task_contract.py::AgentTaskContractTests.test_task_cannot_widen_route_authority`

<a id="AIXEM-REQ-AGENT-LIVE-0002"></a>

### AIXEM-REQ-AGENT-LIVE-0002 — Effective scope only narrows

**MUST.** Task write constraints MUST resolve as an equal or narrower subset of the active route authority, artifact patterns, prohibitions, constraints, and validators.

- Validator: `agent.task_contract`
- Test: `tests/agent/test_task_contract.py::AgentTaskContractTests.test_valid_task_resolves_route_bounded_write_scope`

<a id="AIXEM-REQ-AGENT-LIVE-0003"></a>

### AIXEM-REQ-AGENT-LIVE-0003 — Executable route is fixed before staging

**MUST.** A live attempt MUST resolve one executable active route before stage materialization; a simple route cannot select an unrelated route and a composite route must select one declared child stage.

- Validator: `agent.task_contract`
- Test: `tests/agent/test_task_contract.py::AgentTaskContractTests.test_simple_route_cannot_select_an_unrelated_active_route`

## Validation

```bash
python tools/live_agent_authoring.py build-stage \
  --case validation/agent-evals-3/cases/L008 \
  --attempt-id L008-example-01 \
  --output /tmp/aixem-L008
```

A task-resolution failure is terminal for that attempt. The runner does not silently widen scope or substitute another route.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

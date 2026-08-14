---
status: normative
version: '1.0'
language: en
domain: conformance
agent:
  priority: critical
  estimated_tokens: 824
  intents:
  - validate-project
  - publish-release
navigation:
  group: conformance
  order: 95
artifacts:
  owns: []
  consumes: []
id: AIXEM-CONF-AGENT-AUTHORING-001
title: Agent Authoring Closed-Loop Conformance
kind: conformance
summary: Defines Tier A deterministic harness proof, optional Tier B live-agent evidence, A001-A012 corpus
  outcomes, scope discipline, closure, and claim truthfulness.
authority:
- agent-authoring-conformance
aliases:
- agent authoring conformance
- closed-loop conformance
- Agent Evaluation 2
depends_on:
- AIXEM-SPEC-AGENT-EXECUTION-001
- AIXEM-SPEC-AGENT-RUN-001
- AIXEM-CONF-AGENT-DIAGNOSTICS-001
related:
- AIXEM-CONF-RELEASE-001
requirements:
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0014
  title: Tier separation
  level: MUST
  statement: Conformance evidence MUST distinguish deterministic Tier A harness/replay from Tier B live
    external agent execution.
  validator: agent.evaluation_tier_truth
  verification_mode: automated
  test: tests/agent/test_agent_evals_2.py::AgentEvaluation2Tests.test_tier_status_never_conflates_replay_and_live_execution
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0014.json
- id: AIXEM-REQ-AGENT-CLOSED-LOOP-0015
  title: Truthful live-agent claim
  level: MUST
  statement: A release MUST NOT claim live-agent success unless retained evidence records an actually
    executed external agent and its executor configuration.
  validator: agent.evaluation_tier_truth
  verification_mode: automated
  test: tests/agent/test_agent_evals_2.py::AgentEvaluation2Tests.test_tier_status_never_conflates_replay_and_live_execution
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0015.json
---

# Agent Authoring Closed-Loop Conformance

Defines Tier A deterministic harness proof, optional Tier B live-agent evidence, A001-A012 corpus outcomes, scope discipline, closure, and claim truthfulness.

> **Document ID:** `AIXEM-CONF-AGENT-AUTHORING-001`  
> **Status:** Normative  
> **Version:** 1.0

## Evaluation Tiers

Tier A is deterministic and mandatory in CI. It validates schemas, diagnostic routing, write scope, generated-output detection, known repair replay, render closure, and run-record determinism. Tier B is optional and executes a real external agent in an isolated cold-start stage.

## Corpus

Agent Evaluation 2 contains A001-A012: two-pin passive, connector, controller, parameter/variant, three-terminal junction, two-sheet hierarchy, same-name local nets, lead/port repair, wrong semantic net, non-orthogonal route, duplicate project-net member, and field/body overlap.

## Outcome Scoring

Evaluation scores final schema and semantic closure, authority ownership, route compliance, allowed write scope, generated-output discipline, repair convergence, render success, Viewer Model success, and deterministic rerender. Exact source bytes are required only for locked determinism.

## Live-Agent Evidence

Tier B stages must hide completed target fixtures. Results record documents opened, searches, renderer-source inspection, changed files, diagnostics, iterations, executor metadata, and final conformance. `liveExternalAgentExecuted=false` is the only valid value when no external executor was run.

## Public Claims

Tier A supports a claim about route-bounded machine-readable authoring closure. A generic autonomous-design claim or live-agent success claim is prohibited without corresponding Tier B evidence.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0014"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0014 — Tier separation

**MUST.** Conformance evidence MUST distinguish deterministic Tier A harness/replay from Tier B live external agent execution.

- Verification mode: `automated`
- Validator: `agent.evaluation_tier_truth`
- Test reference: `tests/agent/test_agent_evals_2.py::AgentEvaluation2Tests.test_tier_status_never_conflates_replay_and_live_execution`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0014.json`

<a id="AIXEM-REQ-AGENT-CLOSED-LOOP-0015"></a>

### AIXEM-REQ-AGENT-CLOSED-LOOP-0015 — Truthful live-agent claim

**MUST.** A release MUST NOT claim live-agent success unless retained evidence records an actually executed external agent and its executor configuration.

- Verification mode: `automated`
- Validator: `agent.evaluation_tier_truth`
- Test reference: `tests/agent/test_agent_evals_2.py::AgentEvaluation2Tests.test_tier_status_never_conflates_replay_and_live_execution`
- Release evidence: `validation/evidence/requirements/AIXEM-REQ-AGENT-CLOSED-LOOP-0015.json`

## Validation and Evidence

Conformance requires current machine-readable evidence for every requirement, successful execution of the mapped tests, and release traceability that resolves this document, its validator, and its evidence artifact.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

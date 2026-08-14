---
status: normative
version: '1.0'
language: en
domain: conformance
agent:
  priority: critical
  estimated_tokens: 1573
  intents:
  - validate-project
navigation:
  group: conformance
  order: 180
artifacts:
  owns:
  - validation/agent-evals-3/**
  consumes:
  - validation/agent-evals-2/**
id: AIXEM-CONF-AGENT-LIVE-001
title: Live-Agent Cold-Start Conformance
kind: conformance
summary: Defines Agent Evaluation 3 L001-L012, deterministic Tier A protocol conformance, actual Tier B external execution, retention, scoring, and truthful capability claims.
authority:
- live-agent-conformance
aliases:
- agent evaluation 3
- live agent tier b
- cold-start corpus
depends_on:
- AIXEM-SPEC-AGENT-TASK-001
- AIXEM-SPEC-AGENT-STAGE-001
- AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
- AIXEM-SPEC-AGENT-OBSERVATION-001
- AIXEM-SPEC-AGENT-EVAL-INVARIANT-001
- AIXEM-SPEC-AGENT-LIVE-RUN-001
related:
- AIXEM-CONF-AGENT-AUTHORING-001
- AIXEM-RELEASE-056-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0018
  title: Complete cold-start corpus
  level: MUST
  statement: Agent Evaluation 3 MUST contain exactly L001-L012 with seven creation and five repair tasks, incomplete staged starts, task/evaluator separation, declared initial diagnostics, and no bundled completed target.
  validator: agent.evaluation_3
  verification_mode: automated
  test: tests/agent/test_agent_evals_3.py::AgentEvaluation3CorpusTests.test_manifest_contains_exact_l001_l012_creation_and_repair_inventory
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0018.json
- id: AIXEM-REQ-AGENT-LIVE-0019
  title: Tier A and Tier B are never conflated
  level: MUST
  statement: Deterministic protocol fixtures MUST remain Tier A only, and Tier B or a public live-agent claim MUST remain false until an actual external-AI executor produces retained execution evidence.
  validator: agent.evaluation_3
  verification_mode: automated
  test: tests/agent/test_agent_evals_3.py::AgentEvaluation3CorpusTests.test_tier_b_status_never_claims_an_execution_that_did_not_happen
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0019.json
- id: AIXEM-REQ-AGENT-LIVE-0025
  title: Deterministic pre-live success and fault closure
  level: MUST
  statement: Before Tier B, non-AI test fixtures MUST prove complete PASS flows for symbol, semantic, layout, and project authorities and retain the declared executor error, failure, timeout, tamper, scope, generated-output, invariant, close, malformed-observation, and secret-leak fault paths without setting any live-agent flag.
  validator: agent.pre_live_readiness
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_generated_readiness_report_closes_all_pre_live_gates
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0025.json
- id: AIXEM-REQ-AGENT-LIVE-0027
  title: Reference-pack and authoring-route readiness
  level: MUST
  statement: Representative readiness fixtures MUST execute prepare, check, and close from the staged reference pack without source-repository PYTHONPATH fallback, and every existing authoring route MUST have exactly one explicit pre-live readiness classification without adding a readiness-only route.
  validator: agent.pre_live_readiness
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_generated_readiness_report_closes_all_pre_live_gates
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0027.json
---

# Live-Agent Cold-Start Conformance

Agent Evaluation 3 tests the operational claim that an external AI agent can start from AIXEM's normal route entry point, edit incomplete authoritative artifacts, use the 0.5.5 closed loop, and leave evidence that can be scored without exposing a completed answer.

## Corpus Inventory

| ID | Class | Primary capability |
|---|---|---|
| L001 | creation | novel two-pin passive symbol and binding |
| L002 | creation | six-pin connector symbol and binding |
| L003 | creation | twelve-pin controller symbol and binding |
| L004 | creation | parameterized variant selection and placement |
| L005 | creation | three-terminal semantic net and junction closure |
| L006 | creation | two-sheet project-net composition |
| L007 | creation | same-name local net isolation plus explicit project binding |
| L008 | repair | visible lead/port coincidence |
| L009 | repair | semantic net closure behind plausible geometry |
| L010 | repair | off-grid non-orthogonal route |
| L011 | repair | duplicate project-net member |
| L012 | repair | field/body overlap |

L001-L007 are creation tasks; L008-L012 are repair tasks. Case values, IDs, and net names are deliberately changed from ordinary examples where practical. Each start state excludes `render/`, `evidence/`, evaluator data, and completed targets.

## Tier A — Deterministic Protocol Conformance

Tier A validates:

- all task and machine schemas;
- route-bounded scope resolution;
- two independent builds of every stage with equal digests;
- zero target leakage;
- initial diagnostic declarations;
- a real subprocess launch using a non-AI observable fixture;
- observation validation and no-CoT rejection;
- actual final-workspace scoring;
- retained FAIL evidence for the fixture;
- false `liveExternalAgentExecuted` and false claim eligibility.

Tier A is a release dependency. Tier A is not evidence that an AI solved the task.

## Tier B — Actual External Agent

Tier B requires an explicit descriptor with `agentClass: external-ai`. Prefer three fresh attempts per case for one named executor profile. All 36 expected attempt IDs must be retained when three attempts are declared. No result may be removed because it failed, timed out, or encountered an executor error.

A Tier B attempt is scored only after the external process exits or times out. The evaluator never edits the workspace. A passing invariant set without a conformant Authoring Run Record remains `FAIL`.

## Current Release Evidence State

`validation/agent-evals-3/results/tier-a-results.json` is the deterministic protocol result. `tier-b-status.json` is the live execution gate. In a build environment without a supplied external executor, the correct state is:

```text
Tier A protocol conformance: PASS
Tier B actual execution: NOT EXECUTED
Live external-agent claim: NOT AUTHORIZED
```

This is a truthful environmental blocker, not a protocol failure and not a fabricated pass.

## Public Claim Rule

After retained Tier B evidence exists, an allowed claim is limited to the exact executor profile, cases, attempts, and numerator/denominator. The release must not claim arbitrary circuit design autonomy or universal LLM compatibility.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0018"></a>

### AIXEM-REQ-AGENT-LIVE-0018 — Complete cold-start corpus

**MUST.** Agent Evaluation 3 MUST contain exactly L001-L012 with seven creation and five repair tasks, incomplete staged starts, task/evaluator separation, declared initial diagnostics, and no bundled completed target.

<a id="AIXEM-REQ-AGENT-LIVE-0019"></a>

### AIXEM-REQ-AGENT-LIVE-0019 — Tier A and Tier B are never conflated

**MUST.** Deterministic protocol fixtures MUST remain Tier A only, and Tier B or a public live-agent claim MUST remain false until an actual external-AI executor produces retained execution evidence.

## Commands

```bash
python tools/build_agent_evals_3.py
python tools/run_agent_evals_3.py --tier-a-only
python tools/run_agent_evals_3.py --external-executor /secure/executor.json --attempts-per-case 3
```


## Pre-Live Readiness Gate

Before any external AI executor is connected, AIXEM runs four authority-representative non-AI subprocess fixtures:

| Fixture | Route | Authority boundary |
|---|---|---|
| R001 | `create-symbol` | symbol, component library, project locks |
| R002 | `create-schematic` | semantic source and project locks |
| R003 | `route-nets` | layout and project locks |
| R004 | `compose-project` | project composition |

Each fixture must complete `fresh stage → subprocess → prepare → authority-local edit → check → close → run record → invariant scoring → retained PASS evidence`. All fixtures remain `agentClass=test-fixture`, `liveExternalAgentExecuted=false`, and `claimEligible=false`.

The integrated fault matrix retains missing executable, non-zero exit, timeout with mutation, immutable task tamper, wrong-authority edit, generated-output edit, zero exit with invariant failure, close failure, malformed observation, and observation secret cases. The generated readiness report also audits all L001-L012 invariant bases, staged-reference closure, all eight authoring routes, and platform-only timing/size metrics.

<a id="AIXEM-REQ-AGENT-LIVE-0025"></a>

### AIXEM-REQ-AGENT-LIVE-0025 — Deterministic pre-live success and fault closure

**MUST.** Before Tier B, non-AI test fixtures MUST prove complete PASS flows for symbol, semantic, layout, and project authorities and retain the declared executor error, failure, timeout, tamper, scope, generated-output, invariant, close, malformed-observation, and secret-leak fault paths without setting any live-agent flag.

<a id="AIXEM-REQ-AGENT-LIVE-0027"></a>

### AIXEM-REQ-AGENT-LIVE-0027 — Reference-pack and authoring-route readiness

**MUST.** Representative readiness fixtures MUST execute `prepare`, `check`, and `close` from the staged reference pack without source-repository `PYTHONPATH` fallback, and every existing authoring route MUST have exactly one explicit pre-live readiness classification without adding a readiness-only route.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.

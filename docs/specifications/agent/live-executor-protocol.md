---
status: normative
version: '1.0'
language: en
domain: specifications
agent:
  priority: critical
  estimated_tokens: 1209
  intents:
  - author-component-circuit
  - validate-project
navigation:
  group: specifications
  order: 192
artifacts:
  owns:
  - docs/specifications/schemas/agent/aixem-agent-executor-1.schema.json
  consumes:
  - docs/specifications/schemas/agent/aixem-agent-observation-event-1.schema.json
id: AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001
title: Live Executor Protocol 1
kind: contract
summary: Defines a provider-neutral, bounded external subprocess boundary with explicit execution proof, observation capability, network policy, and secret handling.
authority:
- live-executor-protocol
aliases:
- live executor
- external agent subprocess
- provider-neutral agent adapter
depends_on:
- AIXEM-SPEC-AGENT-STAGE-001
- AIXEM-SPEC-AGENT-OBSERVATION-001
related:
- AIXEM-SPEC-AGENT-LIVE-RUN-001
requirements:
- id: AIXEM-REQ-AGENT-LIVE-0007
  title: Provider-neutral subprocess boundary
  level: MUST
  statement: AIXEM core MUST launch external agents through a generic argv-based subprocess descriptor and MUST NOT require a provider SDK in the authoring-conformance core.
  validator: agent.live_executor
  verification_mode: automated
  test: tests/agent/test_live_executor.py::LiveExecutorProtocolTests.test_missing_executable_is_retained_as_executor_error
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0007.json
- id: AIXEM-REQ-AGENT-LIVE-0008
  title: Bounded execution and proof
  level: MUST
  statement: The executor MUST enforce wall-time, output-byte, and observation-event bounds and MUST distinguish unavailable, started, failed, timed-out, and completed processes with observable execution proof.
  validator: agent.live_executor
  verification_mode: automated
  test: tests/agent/test_live_executor.py::LiveExecutorProtocolTests.test_wall_time_and_output_limits_fail_closed
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0008.json
- id: AIXEM-REQ-AGENT-LIVE-0009
  title: Secret values are never serialized
  level: MUST
  statement: Credential values MUST NOT appear in executor descriptors or retained output; explicitly inherited secret-bearing environment values MUST be redacted while inherited variable names may be recorded.
  validator: agent.live_executor
  verification_mode: automated
  test: tests/agent/test_live_executor.py::LiveExecutorProtocolTests.test_inherited_secret_value_is_redacted_without_serializing_it
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0009.json
- id: AIXEM-REQ-AGENT-LIVE-0021
  title: Complete process-tree timeout cleanup
  level: MUST
  statement: On supported POSIX systems the executor MUST launch each attempt in a dedicated process group and terminate the complete group with bounded terminate-to-kill escalation when wall time expires.
  validator: agent.live_executor
  verification_mode: automated
  test: tests/agent/test_pre_live_readiness.py::PreLiveReadinessHardeningTests.test_timeout_terminates_spawned_child_process_group
  evidence: validation/evidence/requirements/AIXEM-REQ-AGENT-LIVE-0021.json
---

# Live Executor Protocol 1

Live Executor Protocol 1 is a minimal adapter contract between the AIXEM cold-start harness and any external command-line AI agent. AIXEM passes paths and limits; the adapter remains responsible for provider-specific authentication, model invocation, tool integration, and event emission.

> **Document ID:** `AIXEM-SPEC-AGENT-EXECUTOR-LIVE-001`  
> **Schema:** `docs/specifications/schemas/agent/aixem-agent-executor-1.schema.json`  
> **Implementation:** `implementation/agent/live_executor.py`

## Descriptor

The descriptor declares:

- stable adapter ID and version;
- `agentClass`: `external-ai` or `test-fixture`;
- argv command template without shell interpolation;
- working-directory and task-input modes;
- observable event coverage;
- network policy and enforcement owner;
- wall-time, output-byte, and event-count bounds;
- redacted executor identity and configuration digest;
- optional literal non-secret environment values;
- optional `inheritEnvironment` names whose values are injected only at launch.

Supported command placeholders are `{stage}`, `{task}`, `{taskMarkdown}`, `{workspace}`, `{reference}`, `{state}`, and `{observationLog}`.

## Execution Proof

`processStarted` proves only that the operating system started a process. `liveExternalAgentExecuted` additionally requires:

1. `agentClass: external-ai` in the retained descriptor;
2. a started process;
3. a valid observation log;
4. an observed `task-open` event;
5. at least one route, command, validator, file-write, or completion action.

The exact executable digest, descriptor digest, sanitized command shape, return code, timeout state, output digests, observation digest, and duration are retained. A test fixture can prove protocol mechanics but can never become live external-AI evidence because its descriptor class is `test-fixture`.

## Secret Boundary

Descriptors reject credential-like literal environment keys and known credential-value patterns. `inheritEnvironment` records variable names only. Values are drawn from the launch environment, never copied into the stage or descriptor, and are included in the redaction set for stdout/stderr. Host-home or OAuth configuration access must be explicit through the adapter and external sandbox policy; it is not silently granted by core.

## Failure States

- missing executable or launch error → `EXECUTOR_ERROR`;
- wall-time exceeded → `TIMEOUT`;
- non-zero return code → `FAILED`;
- zero return code → `COMPLETED`.

These are executor states, not task-evaluation results. A completed process can still produce a retained task `FAIL`.

## Normative Requirements

<a id="AIXEM-REQ-AGENT-LIVE-0007"></a>

### AIXEM-REQ-AGENT-LIVE-0007 — Provider-neutral subprocess boundary

**MUST.** AIXEM core MUST launch external agents through a generic argv-based subprocess descriptor and MUST NOT require a provider SDK in the authoring-conformance core.

<a id="AIXEM-REQ-AGENT-LIVE-0008"></a>

### AIXEM-REQ-AGENT-LIVE-0008 — Bounded execution and proof

**MUST.** The executor MUST enforce wall-time, output-byte, and observation-event bounds and MUST distinguish unavailable, started, failed, timed-out, and completed processes with observable execution proof.

<a id="AIXEM-REQ-AGENT-LIVE-0009"></a>

### AIXEM-REQ-AGENT-LIVE-0009 — Secret values are never serialized

**MUST.** Credential values MUST NOT appear in executor descriptors or retained output; explicitly inherited secret-bearing environment values MUST be redacted while inherited variable names may be recorded.

## Reference Template

`validation/agent-evals-3/executors/external-ai-template.json` is a non-executable template. Supplying it unchanged does not constitute Tier B execution.


## Process Lifecycle and Output Semantics

On POSIX, each executor starts in a dedicated session. A timeout first terminates the complete process group, waits for a bounded grace interval, and then kills the group if necessary. Unsupported platforms use a conservative parent-process fallback and report the enforcement mode. This prevents helper shells, validators, renderers, and model-client children from continuing against the stage after the parent times out.

`outputBytes` bounds retained bytes per captured stdout/stderr stream. It does not claim to meter arbitrary files written by the child process.

<a id="AIXEM-REQ-AGENT-LIVE-0021"></a>

### AIXEM-REQ-AGENT-LIVE-0021 — Complete process-tree timeout cleanup

**MUST.** On supported POSIX systems the executor MUST launch each attempt in a dedicated process group and terminate the complete group with bounded terminate-to-kill escalation when wall time expires.

---

This file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content.
